import subprocess
from dataclasses import dataclass


@dataclass
class SandboxExecutionResult:
    stdout: str
    stderr: str
    exit_code: int
    timed_out: bool = False

    def is_success(self) -> bool:
        return self.exit_code == 0 and not self.timed_out

    def get_combined_output(self) -> str:
        parts = []
        if self.stdout.strip():
            parts.append(self.stdout)
        if self.stderr.strip():
            parts.append(f"STDERR: {self.stderr}")
        return "\n".join(parts)


class SandboxSettings:
    image = "python:3.12-slim"
    work_dir = "/workspace"
    memory_limit = "512m"
    cpu_limit = "1.0"
    timeout = 300
    network_enabled = False


class DockerSandbox:
    def __init__(self):
        self.container_id: str | None = None

    def _run_docker(self, args: list[str], *, timeout: int, check: bool = False) -> subprocess.CompletedProcess[str]:
        try:
            result = subprocess.run(
                ["docker", *args],
                capture_output=True,
                text=True,
                timeout=timeout,
                check=check,
            )
        except FileNotFoundError as exc:
            raise RuntimeError("Docker CLI is not installed or not available on PATH") from exc
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(f"Docker command timed out: docker {' '.join(args)}") from exc
        except subprocess.CalledProcessError as exc:
            output = (exc.stdout or "") + (exc.stderr or "")
            raise RuntimeError(output.strip() or f"Docker command failed: docker {' '.join(args)}") from exc
        return result

    def start(self) -> None:
        if self.is_running():
            return
        network = "bridge" if SandboxSettings.network_enabled else "none"
        command = [
            "docker",
            "run",
            "-d",
            "--rm",
            "--network",
            network,
            "--memory",
            SandboxSettings.memory_limit,
            "--cpus",
            SandboxSettings.cpu_limit,
            "-w",
            SandboxSettings.work_dir,
            SandboxSettings.image,
            "sleep",
            "infinity",
        ]
        result = self._run_docker(command[1:], timeout=120)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "docker run failed")
        self.container_id = result.stdout.strip()

    def execute_command(self, command: str) -> SandboxExecutionResult:
        if not self.is_running():
            raise RuntimeError("Sandbox is not running")
        try:
            result = self._run_docker(["exec", self.container_id, "/bin/sh", "-c", command], timeout=SandboxSettings.timeout)
            return SandboxExecutionResult(result.stdout, result.stderr, result.returncode)
        except RuntimeError as exc:
            if "timed out" in str(exc):
                return SandboxExecutionResult("", str(exc), 124, True)
            raise

    def copy_file_to_sandbox(self, local_path: str, container_path: str) -> None:
        if not self.is_running():
            raise RuntimeError("Sandbox is not running")
        self._run_docker(["cp", local_path, f"{self.container_id}:{container_path}"], timeout=60, check=True)

    def copy_file_from_sandbox(self, container_path: str, local_path: str) -> None:
        if not self.is_running():
            raise RuntimeError("Sandbox is not running")
        self._run_docker(["cp", f"{self.container_id}:{container_path}", local_path], timeout=60, check=True)

    def stop(self) -> None:
        if self.container_id:
            self._run_docker(["stop", self.container_id], timeout=60)
        self.container_id = None

    def is_running(self) -> bool:
        if not self.container_id:
            return False
        try:
            result = self._run_docker(["inspect", "-f", "{{.State.Running}}", self.container_id], timeout=30)
            return result.returncode == 0 and result.stdout.strip().lower() == "true"
        except RuntimeError:
            return False

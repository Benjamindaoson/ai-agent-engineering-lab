from __future__ import annotations

import os
import shutil
import subprocess
import sys


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def run_short(command: list[str]) -> tuple[bool, str]:
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=10, check=False)
    except FileNotFoundError:
        return False, "not found"
    except subprocess.TimeoutExpired:
        return False, "timeout"
    output = (result.stdout + result.stderr).strip().splitlines()
    return result.returncode == 0, output[0] if output else f"exit {result.returncode}"


def print_check(name: str, ok: bool, detail: str = "") -> None:
    status = "PASS" if ok else "MISSING"
    suffix = f" - {detail}" if detail else ""
    print(f"{name}: {status}{suffix}")


def main() -> int:
    print("Production platform environment check")
    print()

    python_ok = sys.version_info >= (3, 10)
    print_check("Python >= 3.10", python_ok, sys.version.split()[0])

    git_ok, git_detail = run_short(["git", "--version"])
    print_check("Git CLI", git_ok, git_detail)

    docker_cli = command_exists("docker")
    print_check("Docker CLI", docker_cli)
    if docker_cli:
        docker_ok, docker_detail = run_short(["docker", "version", "--format", "{{.Server.Version}}"])
        print_check("Docker daemon", docker_ok, docker_detail)

    playwright_import = subprocess.run(
        [sys.executable, "-c", "import importlib.util; raise SystemExit(0 if importlib.util.find_spec('playwright') else 1)"],
        check=False,
    )
    print_check("Playwright package", playwright_import.returncode == 0)

    print_check("DASHSCOPE_API_KEY", bool(os.getenv("DASHSCOPE_API_KEY")))
    print_check("DEEPSEEK_API_KEY", bool(os.getenv("DEEPSEEK_API_KEY")))

    print()
    print("This script only checks local readiness. It does not call live models or start browser automation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

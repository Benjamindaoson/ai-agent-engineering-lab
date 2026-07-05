import time
from typing import Any

from python_ai_manus.tools.base_tool import BaseTool
from python_ai_manus.tools.tool_result import ToolResult

from .docker_sandbox import DockerSandbox


class SandboxTool(BaseTool):
    def __init__(self):
        super().__init__("sandbox", "Execute commands safely in a Docker container sandbox")
        self.sandbox: DockerSandbox | None = None

    def get_parameters_schema(self) -> dict[str, Any]:
        return self.build_schema(
            {
                "action": self.enum_param("Sandbox action", ["start", "stop", "execute", "status"]),
                "command": self.string_param("Command to execute in sandbox"),
                "language": self.enum_param("Programming language for code execution", ["python", "bash", "node", "java"]),
                "code": self.string_param("Code to execute"),
                "working_dir": self.string_param("Working directory in container"),
            },
            ["action"],
        )

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        action = self.get_string(parameters, "action")
        if not action:
            return ToolResult.failure("action is required")
        try:
            if action.lower() == "start":
                return self._handle_start()
            if action.lower() == "stop":
                return self._handle_stop()
            if action.lower() == "execute":
                return self._handle_execute(parameters)
            if action.lower() == "status":
                return self._handle_status()
            return ToolResult.failure(f"Unknown action: {action}")
        except Exception as exc:
            # ponytail: sandbox is an external tool boundary; keep failures inside ToolResult.
            return ToolResult.failure(f"Sandbox operation failed: {exc}")

    def _handle_start(self) -> ToolResult:
        if self.sandbox is None:
            self.sandbox = DockerSandbox()
        if self.sandbox.is_running():
            return ToolResult.success("Sandbox is already running")
        self.sandbox.start()
        return ToolResult.success("Sandbox started successfully")

    def _handle_stop(self) -> ToolResult:
        if self.sandbox is None or not self.sandbox.is_running():
            return ToolResult.success("Sandbox is not running")
        self.sandbox.stop()
        return ToolResult.success("Sandbox stopped successfully")

    def _handle_execute(self, parameters: dict[str, Any]) -> ToolResult:
        if self.sandbox is None:
            self.sandbox = DockerSandbox()
        if not self.sandbox.is_running():
            self.sandbox.start()

        command = self.get_string(parameters, "command")
        code = self.get_string(parameters, "code")
        language = self.get_string(parameters, "language")
        working_dir = self.get_string(parameters, "working_dir")
        if command is None:
            if code is None or language is None:
                return ToolResult.failure("Either command or both code and language must be provided")
            command = self.build_code_execution_command(code, language)
        if working_dir:
            command = f"cd {working_dir} && {command}"

        result = self.sandbox.execute_command(command)
        if result.is_success():
            return ToolResult.success(result.get_combined_output())
        if result.timed_out:
            return ToolResult.failure("Command timed out")
        return ToolResult.failure(f"Command failed with exit code {result.exit_code}:\n{result.get_combined_output()}")

    def _handle_status(self) -> ToolResult:
        if self.sandbox is None:
            return ToolResult.success("Sandbox not initialized")
        return ToolResult.success(f"Sandbox status: {'running' if self.sandbox.is_running() else 'stopped'}")

    @staticmethod
    def escape_for_python_command(python_code: str) -> str:
        return "'" + python_code.replace("'", "'\"'\"'").replace('"', '\\"').replace("\n", "\\n") + "'"

    def build_code_execution_command(self, code: str, language: str) -> str:
        language = language.lower()
        if language == "python":
            return self._build_heredoc_command(code, "python3")
        if language == "bash":
            return code
        if language == "node":
            return self._build_heredoc_command(code, "node")
        if language == "java":
            return self._build_heredoc_to_file(code, "/tmp/Main.java") + " && cd /tmp && javac Main.java && java Main"
        raise ValueError(f"Unsupported language: {language}")

    def _build_heredoc_command(self, code: str, interpreter: str) -> str:
        delimiter = self._generate_heredoc_delimiter()
        return f"{interpreter} << '{delimiter}'\n{code}\n{delimiter}"

    def _build_heredoc_to_file(self, code: str, file_path: str) -> str:
        delimiter = self._generate_heredoc_delimiter()
        return f"cat > {file_path} << '{delimiter}'\n{code}\n{delimiter}"

    def _generate_heredoc_delimiter(self) -> str:
        return f"OPENMANUS_CODE_EOF_{int(time.time() * 1000)}"

    def cleanup(self) -> None:
        if self.sandbox is not None and self.sandbox.is_running():
            self.sandbox.stop()

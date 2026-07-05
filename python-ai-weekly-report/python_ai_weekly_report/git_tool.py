import subprocess
from datetime import date, timedelta


class GitTool:
    def get_commit_log(self, project_path: str) -> str:
        return self.fetch_weekly_git_log(project_path)

    def fetch_weekly_git_log(self, project_path: str) -> str:
        since_date = (date.today() - timedelta(weeks=1)).isoformat()
        author_name = self.get_local_git_user(project_path)
        result = self._run_git(
            project_path,
            [
                "log",
                f"--since={since_date}",
                f"--author={author_name}",
                "--pretty=format:%ad | %an | %s",
                "--date=short",
            ],
        )
        return result.stdout.strip()

    def get_local_git_user(self, project_path: str) -> str:
        result = self._run_git(project_path, ["config", "user.name"])
        user_name = result.stdout.strip()
        if not user_name:
            raise RuntimeError(f"无法获取本地 Git 用户名 (git config user.name)：{project_path}")
        return user_name

    def _run_git(self, project_path: str, args: list[str]) -> subprocess.CompletedProcess[str]:
        try:
            result = subprocess.run(
                ["git", *args],
                cwd=project_path,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30,
            )
        except FileNotFoundError as exc:
            raise RuntimeError("Git is not installed or not available on PATH") from exc
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(f"Git command timed out: git {' '.join(args)}") from exc
        if result.returncode != 0:
            output = (result.stdout + result.stderr).strip()
            raise RuntimeError(f"Git command failed with exit code {result.returncode}. Output: {output}")
        return result

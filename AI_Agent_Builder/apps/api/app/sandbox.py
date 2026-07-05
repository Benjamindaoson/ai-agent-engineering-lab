from __future__ import annotations

import shutil
import sqlite3
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

from .config import settings
from .db import DbConnection
from .utils import new_id, now_iso


def run_submission_sandbox(
    conn: DbConnection,
    review_job_id: str,
    submission_id: str,
) -> dict[str, Any]:
    submission = conn.execute("SELECT * FROM submissions WHERE id = ?", (submission_id,)).fetchone()
    if submission is None:
        raise ValueError("Submission not found")

    now = now_iso()
    sandbox_run_id = new_id()
    started = time.perf_counter()
    command = submission["sandbox_command"] or settings.sandbox_default_command
    status = "failed"
    stdout = ""
    stderr = ""
    exit_code: int | None = None
    image = f"{settings.sandbox_backend}:local"

    try:
        with tempfile.TemporaryDirectory(prefix="agentlab-sandbox-") as temp_dir:
            repo_dir = Path(temp_dir) / "repo"
            _materialize_submission_repo(submission, repo_dir)
            completed = subprocess.run(
                command,
                cwd=repo_dir,
                shell=True,
                text=True,
                capture_output=True,
                timeout=settings.sandbox_timeout_seconds,
            )
            stdout = completed.stdout[-12000:]
            stderr = completed.stderr[-12000:]
            exit_code = completed.returncode
            status = "succeeded" if completed.returncode == 0 else "failed"
    except subprocess.TimeoutExpired as exc:
        status = "timed_out"
        exit_code = 124
        stdout = (exc.stdout or "")[-12000:] if isinstance(exc.stdout, str) else ""
        stderr = ((exc.stderr or "") if isinstance(exc.stderr, str) else "")[-12000:]
        stderr = (stderr + f"\nSandbox command timed out after {settings.sandbox_timeout_seconds}s.").strip()
    except Exception as exc:
        status = "failed"
        exit_code = 1
        stderr = str(exc)

    finished = now_iso()
    duration_ms = int((time.perf_counter() - started) * 1000)
    conn.execute(
        """
        INSERT INTO sandbox_runs (
          id, review_job_id, submission_id, status, image, command,
          stdout_ref, stderr_ref, exit_code, duration_ms, created_at, finished_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            sandbox_run_id,
            review_job_id,
            submission_id,
            status,
            image,
            command,
            stdout,
            stderr,
            exit_code,
            duration_ms,
            now,
            finished,
        ),
    )
    return {
        "sandbox_run_id": sandbox_run_id,
        "status": status,
        "image": image,
        "command": command,
        "stdout": stdout,
        "stderr": stderr,
        "exit_code": exit_code,
        "duration_ms": duration_ms,
    }


def _materialize_submission_repo(submission: sqlite3.Row | dict[str, Any], repo_dir: Path) -> None:
    source_repo_path = submission["source_repo_path"]
    github_repo_url = submission["github_repo_url"]
    if source_repo_path:
        source = Path(source_repo_path).resolve()
        allowed_root = settings.sandbox_allowed_root
        if not source.exists() or not source.is_dir():
            raise ValueError(f"source_repo_path does not exist or is not a directory: {source}")
        if not _is_relative_to(source, allowed_root):
            raise ValueError(f"source_repo_path must be under SANDBOX_ALLOWED_ROOT: {allowed_root}")
        ignore = shutil.ignore_patterns(".git", ".venv", "node_modules", ".next", "__pycache__", ".pytest_cache")
        shutil.copytree(source, repo_dir, ignore=ignore)
        return
    if github_repo_url:
        completed = subprocess.run(
            ["git", "clone", "--depth", "1", str(github_repo_url), str(repo_dir)],
            text=True,
            capture_output=True,
            timeout=settings.sandbox_timeout_seconds,
        )
        if completed.returncode != 0:
            raise ValueError(f"git clone failed: {completed.stderr[-4000:]}")
        return
    raise ValueError("Submission must include source_repo_path or github_repo_url for sandbox execution.")


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False

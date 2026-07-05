from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from .config import settings


class PostgresConnection:
    def __init__(self) -> None:
        try:
            import psycopg
            from psycopg.rows import dict_row
        except ImportError as exc:
            raise RuntimeError("Install psycopg[binary] to use DATABASE_URL=postgresql://...") from exc
        self._conn = psycopg.connect(settings.database_url, row_factory=dict_row)

    def execute(self, sql: str, params: tuple[Any, ...] | list[Any] = ()) -> Any:
        return self._conn.execute(sql.replace("?", "%s"), params)

    def executescript(self, sql: str) -> None:
        for statement in [part.strip() for part in sql.split(";") if part.strip()]:
            self.execute(statement)

    def commit(self) -> None:
        self._conn.commit()

    def rollback(self) -> None:
        self._conn.rollback()

    def close(self) -> None:
        self._conn.close()


DbConnection = sqlite3.Connection | PostgresConnection


def connect() -> DbConnection:
    if settings.database_driver == "postgres":
        return PostgresConnection()
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(settings.database_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_conn() -> Iterator[DbConnection]:
    conn = connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    schema_path = Path(__file__).with_name("schema.sql")
    with get_conn() as conn:
        conn.executescript(schema_path.read_text(encoding="utf-8"))
        ensure_schema_compat(conn)


def ensure_schema_compat(conn: DbConnection) -> None:
    ensure_table(
        conn,
        "planning_sessions",
        """
        CREATE TABLE IF NOT EXISTS planning_sessions (
          id TEXT PRIMARY KEY,
          learner_id TEXT NOT NULL,
          status TEXT NOT NULL,
          intent_json TEXT NOT NULL,
          context_json TEXT NOT NULL,
          plan_preview_json TEXT,
          missing_slot TEXT,
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL,
          confirmed_at TEXT,
          FOREIGN KEY (learner_id) REFERENCES users(id)
        )
        """,
    )
    ensure_table(
        conn,
        "planning_messages",
        """
        CREATE TABLE IF NOT EXISTS planning_messages (
          id TEXT PRIMARY KEY,
          session_id TEXT NOT NULL,
          role TEXT NOT NULL,
          content TEXT NOT NULL,
          payload_json TEXT,
          created_at TEXT NOT NULL,
          FOREIGN KEY (session_id) REFERENCES planning_sessions(id)
        )
        """,
    )
    ensure_table(
        conn,
        "planning_agent_runs",
        """
        CREATE TABLE IF NOT EXISTS planning_agent_runs (
          id TEXT PRIMARY KEY,
          session_id TEXT NOT NULL,
          agent_name TEXT NOT NULL,
          input_json TEXT NOT NULL,
          output_json TEXT NOT NULL,
          status TEXT NOT NULL,
          created_at TEXT NOT NULL,
          FOREIGN KEY (session_id) REFERENCES planning_sessions(id)
        )
        """,
    )
    ensure_table(
        conn,
        "agent_traces",
        """
        CREATE TABLE IF NOT EXISTS agent_traces (
          id TEXT PRIMARY KEY,
          agent_run_id TEXT,
          learner_id TEXT NOT NULL,
          agent_name TEXT NOT NULL,
          runtime TEXT NOT NULL,
          provider TEXT NOT NULL,
          model TEXT,
          tool_names_json TEXT NOT NULL DEFAULT '[]',
          input_json TEXT NOT NULL,
          output_json TEXT NOT NULL,
          status TEXT NOT NULL,
          latency_ms INTEGER,
          parent_type TEXT,
          parent_id TEXT,
          created_at TEXT NOT NULL,
          FOREIGN KEY (agent_run_id) REFERENCES agent_runs(id),
          FOREIGN KEY (learner_id) REFERENCES users(id)
        )
        """,
    )
    ensure_table(
        conn,
        "agent_runs",
        """
        CREATE TABLE IF NOT EXISTS agent_runs (
          id TEXT PRIMARY KEY,
          review_job_id TEXT,
          learner_id TEXT,
          agent_name TEXT,
          runtime TEXT,
          provider TEXT NOT NULL,
          model TEXT,
          mode TEXT NOT NULL,
          prompt_version TEXT,
          parent_type TEXT,
          parent_id TEXT,
          tool_names_json TEXT NOT NULL DEFAULT '[]',
          input_json TEXT,
          output_json TEXT,
          input_ref TEXT,
          output_ref TEXT,
          token_usage TEXT,
          cost_usd REAL,
          latency_ms INTEGER,
          status TEXT NOT NULL,
          error TEXT,
          created_at TEXT NOT NULL,
          finished_at TEXT,
          FOREIGN KEY (review_job_id) REFERENCES review_jobs(id),
          FOREIGN KEY (learner_id) REFERENCES users(id)
        )
        """,
    )
    ensure_table(
        conn,
        "course_lessons",
        """
        CREATE TABLE IF NOT EXISTS course_lessons (
          id TEXT PRIMARY KEY,
          course_module_id TEXT NOT NULL,
          title TEXT NOT NULL,
          content_type TEXT NOT NULL,
          content_ref TEXT,
          body TEXT NOT NULL,
          sort_order INTEGER NOT NULL DEFAULT 100,
          created_at TEXT NOT NULL,
          FOREIGN KEY (course_module_id) REFERENCES course_modules(id)
        )
        """,
    )
    ensure_table(
        conn,
        "course_exercises",
        """
        CREATE TABLE IF NOT EXISTS course_exercises (
          id TEXT PRIMARY KEY,
          course_module_id TEXT NOT NULL,
          prompt TEXT NOT NULL,
          expected_keywords TEXT NOT NULL DEFAULT '[]',
          rubric_json TEXT NOT NULL DEFAULT '{}',
          created_at TEXT NOT NULL,
          FOREIGN KEY (course_module_id) REFERENCES course_modules(id)
        )
        """,
    )
    ensure_table(
        conn,
        "course_exercise_attempts",
        """
        CREATE TABLE IF NOT EXISTS course_exercise_attempts (
          id TEXT PRIMARY KEY,
          learner_id TEXT NOT NULL,
          course_exercise_id TEXT NOT NULL,
          answer TEXT NOT NULL,
          score INTEGER NOT NULL,
          feedback TEXT NOT NULL,
          next_action TEXT NOT NULL,
          status TEXT NOT NULL,
          created_at TEXT NOT NULL,
          FOREIGN KEY (learner_id) REFERENCES users(id),
          FOREIGN KEY (course_exercise_id) REFERENCES course_exercises(id)
        )
        """,
    )
    ensure_table(
        conn,
        "tutor_sessions",
        """
        CREATE TABLE IF NOT EXISTS tutor_sessions (
          id TEXT PRIMARY KEY,
          learner_id TEXT NOT NULL,
          learner_project_id TEXT NOT NULL,
          task_id TEXT,
          status TEXT NOT NULL,
          ai_dependency_score INTEGER NOT NULL DEFAULT 0,
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL,
          FOREIGN KEY (learner_id) REFERENCES users(id),
          FOREIGN KEY (learner_project_id) REFERENCES learner_projects(id),
          FOREIGN KEY (task_id) REFERENCES tasks(id)
        )
        """,
    )
    ensure_table(
        conn,
        "tutor_messages",
        """
        CREATE TABLE IF NOT EXISTS tutor_messages (
          id TEXT PRIMARY KEY,
          tutor_session_id TEXT NOT NULL,
          role TEXT NOT NULL,
          content TEXT NOT NULL,
          hint_level INTEGER,
          learning_signal TEXT,
          created_at TEXT NOT NULL,
          FOREIGN KEY (tutor_session_id) REFERENCES tutor_sessions(id)
        )
        """,
    )
    ensure_table(
        conn,
        "tutor_agent_runs",
        """
        CREATE TABLE IF NOT EXISTS tutor_agent_runs (
          id TEXT PRIMARY KEY,
          tutor_session_id TEXT NOT NULL,
          agent_name TEXT NOT NULL,
          input_json TEXT NOT NULL,
          output_json TEXT NOT NULL,
          status TEXT NOT NULL,
          created_at TEXT NOT NULL,
          FOREIGN KEY (tutor_session_id) REFERENCES tutor_sessions(id)
        )
        """,
    )
    ensure_table(
        conn,
        "coach_tasks",
        """
        CREATE TABLE IF NOT EXISTS coach_tasks (
          id TEXT PRIMARY KEY,
          learner_id TEXT NOT NULL,
          learner_project_id TEXT,
          review_id TEXT,
          source_type TEXT NOT NULL,
          title TEXT NOT NULL,
          reason TEXT NOT NULL,
          action_json TEXT NOT NULL,
          status TEXT NOT NULL,
          priority INTEGER NOT NULL DEFAULT 100,
          created_at TEXT NOT NULL,
          completed_at TEXT,
          FOREIGN KEY (learner_id) REFERENCES users(id),
          FOREIGN KEY (learner_project_id) REFERENCES learner_projects(id),
          FOREIGN KEY (review_id) REFERENCES reviews(id)
        )
        """,
    )
    ensure_column(conn, "submissions", "source_repo_path", "TEXT")
    ensure_column(conn, "submissions", "sandbox_command", "TEXT")
    ensure_column(conn, "agent_runs", "learner_id", "TEXT")
    ensure_column(conn, "agent_runs", "agent_name", "TEXT")
    ensure_column(conn, "agent_runs", "runtime", "TEXT")
    ensure_column(conn, "agent_runs", "parent_type", "TEXT")
    ensure_column(conn, "agent_runs", "parent_id", "TEXT")
    ensure_column(conn, "agent_runs", "tool_names_json", "TEXT NOT NULL DEFAULT '[]'")
    ensure_column(conn, "agent_runs", "input_json", "TEXT")
    ensure_column(conn, "agent_runs", "output_json", "TEXT")
    ensure_column(conn, "agent_traces", "agent_run_id", "TEXT")


def ensure_table(conn: DbConnection, table: str, create_sql: str) -> None:
    if table_exists(conn, table):
        return
    conn.execute(create_sql)


def table_exists(conn: DbConnection, table: str) -> bool:
    if settings.database_driver == "postgres":
        row = conn.execute(
            """
            SELECT 1
            FROM information_schema.tables
            WHERE table_name = ?
            """,
            (table,),
        ).fetchone()
        return row is not None
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table,),
    ).fetchone()
    return row is not None


def ensure_column(conn: DbConnection, table: str, column: str, definition: str) -> None:
    if column_exists(conn, table, column):
        return
    conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def column_exists(conn: DbConnection, table: str, column: str) -> bool:
    if settings.database_driver == "postgres":
        row = conn.execute(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = ? AND column_name = ?
            """,
            (table, column),
        ).fetchone()
        return row is not None
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(row["name"] == column for row in rows)

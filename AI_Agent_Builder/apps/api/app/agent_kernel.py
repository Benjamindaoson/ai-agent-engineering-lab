from __future__ import annotations

import json
from typing import Any

from .db import DbConnection
from .utils import new_id, now_iso


def record_agent_run(
    conn: DbConnection,
    *,
    learner_id: str,
    agent_name: str,
    runtime: str,
    provider: str,
    model: str | None,
    input_data: dict[str, Any],
    output_data: dict[str, Any] | str,
    status: str,
    latency_ms: int | None,
    parent_type: str | None,
    parent_id: str | None,
    tool_names: list[str] | None = None,
    review_job_id: str | None = None,
    mode: str | None = None,
    prompt_version: str | None = None,
    token_usage: dict[str, Any] | None = None,
    error: str | None = None,
    created_at: str | None = None,
    finished_at: str | None = None,
) -> str:
    run_id = new_id()
    now = created_at or now_iso()
    output_text = output_data if isinstance(output_data, str) else json.dumps(output_data, ensure_ascii=False)
    conn.execute(
        """
        INSERT INTO agent_runs (
          id, review_job_id, learner_id, agent_name, runtime, provider, model, mode,
          prompt_version, parent_type, parent_id, tool_names_json, input_json,
          output_json, input_ref, output_ref, token_usage, latency_ms, status,
          error, created_at, finished_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            run_id,
            review_job_id,
            learner_id,
            agent_name,
            runtime,
            provider,
            model,
            mode or runtime,
            prompt_version,
            parent_type,
            parent_id,
            json.dumps(tool_names or []),
            json.dumps(input_data, ensure_ascii=False),
            output_text,
            json.dumps(input_data, ensure_ascii=False),
            output_text[-12000:],
            json.dumps(token_usage) if token_usage else None,
            latency_ms,
            status,
            error,
            now,
            finished_at,
        ),
    )
    return run_id

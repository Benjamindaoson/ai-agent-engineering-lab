from __future__ import annotations

import asyncio
import json
import re
import time
from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from .config import settings
from .mock_review import run_mock_review
from .review_schema import ReviewResult


class AgentRuntimeUnavailable(ValueError):
    pass


@dataclass(frozen=True)
class ReviewRun:
    result: ReviewResult
    provider: str
    model: str | None
    mode: str
    reviewer_type: str
    raw_output: str
    token_usage: dict[str, Any] | None
    latency_ms: int


@dataclass(frozen=True)
class ClaudeAgentRun:
    raw_output: str
    token_usage: dict[str, Any] | None
    latency_ms: int
    model: str | None


def run_review(mode: str, context: dict[str, Any]) -> ReviewRun:
    started = time.perf_counter()
    if mode == "mock":
        result = run_mock_review()
        return ReviewRun(
            result=result,
            provider="mock",
            model=None,
            mode="mock",
            reviewer_type="mock_agent",
            raw_output=result.model_dump_json(),
            token_usage=None,
            latency_ms=_elapsed_ms(started),
        )
    if mode == "claude":
        return asyncio.run(_run_claude_review(context, started))
    raise AgentRuntimeUnavailable(f"Unknown agent mode: {mode}")


async def _run_claude_review(context: dict[str, Any], started: float) -> ReviewRun:
    schema = ReviewResult.model_json_schema()
    system_prompt = (
        "You are AgentLab's hiring-focused AI Agent project reviewer. "
        "Evaluate submitted AI Agent/RAG projects for job readiness. "
        "Return only JSON that conforms to the provided schema. "
        "Do not invent evidence that is not present in the submission or sandbox logs."
    )
    prompt = build_review_prompt(context, schema)
    agent_run = await run_claude_agent_json(
        prompt=prompt,
        system_prompt=system_prompt,
        output_schema=schema,
        max_turns=settings.claude_review_max_turns,
        started=started,
    )

    raw_output = agent_run.raw_output
    try:
        result = ReviewResult.model_validate_json(raw_output)
    except ValidationError:
        result = ReviewResult.model_validate_json(_extract_json_object(raw_output))
    return ReviewRun(
        result=result,
        provider="anthropic",
        model=agent_run.model,
        mode="claude",
        reviewer_type="claude_agent",
        raw_output=raw_output,
        token_usage=agent_run.token_usage,
        latency_ms=agent_run.latency_ms,
    )


async def run_claude_agent_json(
    *,
    prompt: str,
    system_prompt: str,
    output_schema: dict[str, Any],
    max_turns: int,
    started: float | None = None,
) -> ClaudeAgentRun:
    try:
        from claude_agent_sdk import ClaudeAgentOptions, query
    except ImportError as exc:
        raise AgentRuntimeUnavailable("claude-agent-sdk is not installed.") from exc

    run_started = started if started is not None else time.perf_counter()
    raw_parts: list[str] = []
    token_usage: dict[str, Any] | None = None
    options = ClaudeAgentOptions(
        system_prompt=system_prompt,
        max_turns=max_turns,
        model=settings.claude_model,
        cwd=str(settings.root_dir),
        output_format={"type": "json_schema", "schema": output_schema},
    )
    try:
        async for message in query(prompt=prompt, options=options):
            text = _message_text(message)
            if text:
                raw_parts.append(text)
            usage = _message_usage(message)
            if usage:
                token_usage = usage
    except Exception as exc:
        raise AgentRuntimeUnavailable(f"Claude Agent SDK review failed: {exc}") from exc

    raw_output = "\n".join(raw_parts).strip()
    if not raw_output:
        raise AgentRuntimeUnavailable("Claude Agent SDK returned no output.")
    return ClaudeAgentRun(
        raw_output=raw_output,
        token_usage=token_usage,
        latency_ms=_elapsed_ms(run_started),
        model=settings.claude_model,
    )


def build_review_prompt(context: dict[str, Any], schema: dict[str, Any]) -> str:
    return json.dumps(
        {
            "task": "Review this learner submission and produce hiring-readiness evidence.",
            "review_schema": schema,
            "rubric": {
                "project_delivery": "Can the learner deliver a working, documented project?",
                "rag_quality": "Does retrieval, grounding, evaluation, and citation strategy look credible?",
                "engineering_quality": "Are error handling, logs, tests, deployment notes, and maintainability present?",
                "job_readiness": "Would this evidence help the learner pass a practical hiring screen?",
            },
            "context": context,
            "output_rules": [
                "Return valid JSON only.",
                "Use skill_slug values that exist in the supplied skill_nodes list.",
                "If sandbox failed, reflect that in risk_flags and engineering scores.",
                "Set passport_eligible only for evidence backed by submission fields or sandbox logs.",
            ],
        },
        ensure_ascii=True,
    )


def _message_text(message: Any) -> str:
    if isinstance(message, dict):
        return _content_to_text(message.get("content")) or str(message.get("text") or "")
    content = getattr(message, "content", None)
    text = _content_to_text(content)
    if text:
        return text
    if hasattr(message, "text"):
        return str(getattr(message, "text"))
    return ""


def _content_to_text(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                value = item.get("text") or item.get("content")
            else:
                value = getattr(item, "text", None)
            if value:
                parts.append(str(value))
        return "\n".join(parts)
    return ""


def _message_usage(message: Any) -> dict[str, Any] | None:
    usage = getattr(message, "usage", None)
    if usage is None and isinstance(message, dict):
        usage = message.get("usage")
    if usage is None:
        return None
    if isinstance(usage, dict):
        return usage
    if hasattr(usage, "model_dump"):
        return usage.model_dump()
    return {"raw": str(usage)}


def _extract_json_object(text: str) -> str:
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced:
        return fenced.group(1)
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        return text[start : end + 1]
    raise AgentRuntimeUnavailable("Claude review output did not contain a JSON object.")


def _elapsed_ms(started: float) -> int:
    return int((time.perf_counter() - started) * 1000)

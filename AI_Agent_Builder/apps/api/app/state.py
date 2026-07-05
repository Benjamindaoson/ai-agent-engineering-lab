from __future__ import annotations


class StateTransitionError(ValueError):
    pass


REVIEW_JOB_TRANSITIONS: dict[str, set[str]] = {
    "queued": {"running", "cancelled", "failed"},
    "running": {"succeeded", "failed", "cancelled"},
    "succeeded": set(),
    "failed": {"queued"},
    "cancelled": set(),
}


SUBMISSION_TRANSITIONS: dict[str, set[str]] = {
    "draft": {"submitted"},
    "submitted": {"review_queued"},
    "review_queued": {"ai_reviewing", "needs_revision"},
    "ai_reviewing": {"review_completed", "needs_revision", "passed"},
    "review_completed": {"needs_revision", "passed", "verified"},
    "needs_revision": {"submitted", "review_queued"},
    "passed": {"verified"},
    "verified": set(),
}


def ensure_transition(entity: str, current: str, next_state: str) -> None:
    if current == next_state:
        return
    transitions = REVIEW_JOB_TRANSITIONS if entity == "review_job" else SUBMISSION_TRANSITIONS
    allowed = transitions.get(current)
    if allowed is None:
        raise StateTransitionError(f"Unknown {entity} state: {current}")
    if next_state not in allowed:
        raise StateTransitionError(f"Invalid {entity} transition: {current} -> {next_state}")

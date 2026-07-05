from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def new_id() -> str:
    return str(uuid4())


def slugify(value: str) -> str:
    return (
        value.lower()
        .replace(" / ", "-")
        .replace("/", "-")
        .replace(" ", "-")
        .replace("_", "-")
    )

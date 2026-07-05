import json
from typing import Any


def event(event_type: str, **data: Any) -> dict[str, Any]:
    return {"type": event_type, **data}


def to_sse(events: list[dict[str, Any]]) -> bytes:
    return "".join(f"data: {json.dumps(item, ensure_ascii=False)}\n\n" for item in events).encode("utf-8")


def parse_sse_events(text: str) -> list[dict[str, Any]]:
    parsed: list[dict[str, Any]] = []
    for chunk in text.replace("\r\n", "\n").split("\n\n"):
        for line in chunk.splitlines():
            if line.startswith("data:"):
                parsed.append(json.loads(line[5:].strip()))
    return parsed

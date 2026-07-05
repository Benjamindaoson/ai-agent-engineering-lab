from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

API_PATH = Path(__file__).resolve().parents[2] / "api"
sys.path.insert(0, str(API_PATH))

from app.agent_runtime import run_review  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="AgentLab Agent Runner")
    parser.add_argument("--mode", default="mock", choices=["mock", "claude"])
    parser.add_argument("--context", default="-")
    parser.add_argument("--output", default="-")
    args = parser.parse_args()

    context = {}
    if args.context != "-":
        context = json.loads(Path(args.context).read_text(encoding="utf-8"))
    review_run = run_review(args.mode, context)
    payload = {
        "agent_run": {
            "provider": review_run.provider,
            "model": review_run.model,
            "mode": review_run.mode,
            "status": "succeeded",
            "latency_ms": review_run.latency_ms,
        },
        "review_result": review_run.result.model_dump(mode="json"),
        "artifacts": [],
    }
    text = json.dumps(payload, indent=2)
    if args.output == "-":
        print(text)
    else:
        Path(args.output).write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()

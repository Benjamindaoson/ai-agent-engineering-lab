from __future__ import annotations

import sys
from pathlib import Path

API_PATH = Path(__file__).resolve().parents[2] / "api"
sys.path.insert(0, str(API_PATH))

from app.db import get_conn, init_db  # noqa: E402
from app.services import process_next_review_job  # noqa: E402


def run_once() -> None:
    init_db()
    with get_conn() as conn:
        result = process_next_review_job(conn)
    if result:
        print(f"Processed review job: {result}")
    else:
        print("No queued review jobs.")


if __name__ == "__main__":
    run_once()


from __future__ import annotations

import argparse
import json
from pathlib import Path

from marketing_posts.main import run
from run_eval import CASES, case_output_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="为每个评测案例生成独立输出")
    parser.add_argument("--output-root", type=Path, default=Path("output/cases"))
    args = parser.parse_args()
    cases = json.loads(CASES.read_text(encoding="utf-8"))
    args.output_root.mkdir(parents=True, exist_ok=True)
    for index, case in enumerate(cases):
        output_dir = case_output_dir(args.output_root, index)
        print(f"GENERATE: {case['name']} -> {output_dir}")
        run(
            inputs={**case, "case_name": case["name"]},
            output_dir=output_dir,
        )


if __name__ == "__main__":
    main()

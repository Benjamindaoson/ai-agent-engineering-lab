from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from marketing_posts.crew import MarketingPostsCrew
from marketing_posts.runtime import (
    load_inputs,
    parse_args,
    prepare_output_dir,
    validate_outputs,
    write_manifest,
)


def run(
    inputs: Mapping[str, Any] | None = None,
    *,
    output_dir: Path | None = None,
    argv: Sequence[str] | None = None,
) -> None:
    if inputs is None:
        args = parse_args(argv)
        resolved_inputs = load_inputs(args.input)
        resolved_output_dir = output_dir or args.output_dir
    else:
        resolved_inputs = load_inputs(overrides=inputs)
        resolved_output_dir = output_dir or Path("output")

    resolved_output_dir = prepare_output_dir(Path(resolved_output_dir))
    write_manifest(resolved_output_dir, resolved_inputs)

    try:
        MarketingPostsCrew(output_dir=resolved_output_dir).crew().kickoff(
            inputs=resolved_inputs
        )
        validate_outputs(resolved_output_dir)
        print(f"Marketing strategy plan generated: {resolved_output_dir}")
    except Exception as exc:
        raise RuntimeError(f"营销策略项目运行失败: {exc}") from exc


if __name__ == "__main__":
    run()

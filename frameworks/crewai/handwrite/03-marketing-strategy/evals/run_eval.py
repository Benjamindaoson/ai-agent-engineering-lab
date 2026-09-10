from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CASES = Path(__file__).resolve().parent / "cases.json"
REQUIRED_FILENAMES = (
    "research_report.md",
    "marketing_strategy.json",
    "campaign_plan.json",
    "marketing_copies.json",
    "final_marketing_plan.md",
)
BAD_PHRASES = ["保证就业", "保证涨薪", "百分之百有效", "绝对领先", "行业第一"]


def case_output_dir(root: Path, index: int) -> Path:
    return root / f"case-{index + 1:02d}"


def manifest_matches_case(output_dir: Path, case: dict[str, Any]) -> bool:
    path = output_dir / "run_manifest.json"
    if not path.exists():
        return False
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return all(manifest.get(key) == case.get(key) for key in ("brand_name", "product_name"))


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _fail(failures: list[str], message: str) -> None:
    failures.append(message)


def check_case(case: dict[str, Any], output_dir: Path) -> list[str]:
    failures: list[str] = []
    missing = [name for name in REQUIRED_FILENAMES if not (output_dir / name).is_file()]
    if missing:
        _fail(failures, f"missing output files: {', '.join(missing)}")
    if not manifest_matches_case(output_dir, case):
        _fail(failures, "run_manifest.json does not match this case")
    if failures:
        return failures

    try:
        strategy = _read_json(output_dir / "marketing_strategy.json")
        campaign = _read_json(output_dir / "campaign_plan.json")
        copies = _read_json(output_dir / "marketing_copies.json")
    except Exception as exc:
        _fail(failures, f"JSON parse failed: {exc}")
        return failures

    report_text = (output_dir / "research_report.md").read_text(encoding="utf-8")
    final_text = (output_dir / "final_marketing_plan.md").read_text(encoding="utf-8")
    combined_text = "\n".join(
        [
            report_text,
            final_text,
            json.dumps(strategy, ensure_ascii=False),
            json.dumps(campaign, ensure_ascii=False),
            json.dumps(copies, ensure_ascii=False),
        ]
    )

    if "tatics" in combined_text:
        _fail(failures, "found typo: tatics")
    if re.search(r"(?:当前年份|当前年度|今年|本年度|current year).{0,20}2024", combined_text, re.IGNORECASE):
        _fail(failures, "2024 used as current year")
    if "http://" not in report_text and "https://" not in report_text:
        _fail(failures, "research report has no source URL")
    for phrase in BAD_PHRASES:
        bad_lines = [line for line in combined_text.splitlines() if phrase in line]
        if any(
            not re.search(r"避免|禁止|不得|不使用|不应|不能|严禁", line)
            for line in bad_lines
        ):
            _fail(failures, f"found exaggerated promise: {phrase}")
            break

    if not isinstance(strategy, dict):
        _fail(failures, "marketing_strategy.json is not an object")
    else:
        required_keys = {
            "name",
            "positioning",
            "target_audience",
            "value_proposition",
            "tactics",
            "channels",
            "kpis",
            "budget_suggestion",
        }
        missing_keys = required_keys - set(strategy)
        if missing_keys:
            _fail(failures, f"strategy missing fields: {sorted(missing_keys)}")
        if not isinstance(strategy.get("tactics"), list) or not strategy["tactics"]:
            _fail(failures, "strategy tactics are invalid")

    ideas = campaign.get("ideas", []) if isinstance(campaign, dict) else []
    if len(ideas) != 5:
        _fail(failures, f"campaign count is {len(ideas)}, expected 5")
    else:
        descriptions = set()
        channels = set()
        for idea in ideas:
            required = {"name", "description", "target_audience", "channel", "core_message"}
            if not required.issubset(idea):
                _fail(failures, "campaign idea missing required fields")
                break
            descriptions.add(idea.get("description", ""))
            channels.add(idea.get("channel", ""))
        if len(descriptions) < 5:
            _fail(failures, "campaign descriptions are duplicated")
        if len(channels) < 2:
            _fail(failures, "campaign channels are too narrow")

    copies_list = copies.get("copies", []) if isinstance(copies, dict) else []
    if not copies_list:
        _fail(failures, "no platform copy generated")
    else:
        platforms = set()
        for copy in copies_list:
            required = {"campaign_name", "platform", "title", "body", "call_to_action"}
            if not required.issubset(copy):
                _fail(failures, "copy missing required fields")
                break
            if not str(copy.get("call_to_action", "")).strip():
                _fail(failures, "copy missing call to action")
                break
            platforms.add(copy.get("platform", ""))
        if len(platforms) < 2:
            _fail(failures, "platform copy diversity is too narrow")

    if "KPI" not in final_text and "kpi" not in final_text.lower():
        _fail(failures, "final plan missing KPI")
    if "预算" not in final_text:
        _fail(failures, "final plan missing budget")
    if not any(p in final_text for p in ["咨询", "报名", "私信", "联系", "领取"]):
        _fail(failures, "final plan missing clear call to action")
    return failures


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="评测独立营销案例输出")
    parser.add_argument("--output-root", type=Path, default=ROOT / "output" / "cases")
    args = parser.parse_args(argv)
    cases = _read_json(CASES)
    overall_failures = 0
    for index, case in enumerate(cases):
        output_dir = case_output_dir(args.output_root, index)
        print(f"CASE: {case['name']} -> {output_dir}")
        failures = check_case(case, output_dir)
        if failures:
            overall_failures += 1
            print("FAIL")
            for failure in failures:
                print(f"- {failure}")
        else:
            print("PASS")
    if overall_failures:
        raise SystemExit(overall_failures)


if __name__ == "__main__":
    main()

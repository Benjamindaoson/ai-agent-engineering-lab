from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT_DIR = Path(__file__).resolve().parents[2]
KNOWN_OUTPUT_FILES = (
    "research_report.md",
    "project_understanding.md",
    "marketing_strategy.json",
    "campaign_plan.json",
    "marketing_copies.json",
    "final_marketing_plan.md",
    "run_manifest.json",
)
REQUIRED_GENERATED_FILES = KNOWN_OUTPUT_FILES[:6]
REQUIRED_INPUTS = (
    "brand_name",
    "product_name",
    "customer_domain",
    "project_description",
    "target_customer",
    "target_market",
    "competitors",
    "marketing_goal",
    "budget",
    "platforms",
    "brand_tone",
    "current_year",
)

DEFAULT_INPUTS: dict[str, Any] = {
    "brand_name": "道生AI",
    "product_name": "AI Agent 实战训练营",
    "customer_domain": "暂无官方网站",
    "project_description": (
        "一套面向开发者和职业转型者的 AI Agent 项目实战课程，强调从零手写、"
        "代码调试、Agent 工作流设计和工程化交付，而不是只演示 API 调用。"
    ),
    "target_customer": "希望转型成为 AI Agent 开发工程师的后端、前端和全栈开发者。",
    "target_market": "中国大陆中文市场",
    "competitors": "主流大模型培训课程、Agent 编程课程和 AI 编程训练营",
    "marketing_goal": "获取首期课程的有效咨询和付费报名用户",
    "budget": "人民币 2 万元以内",
    "platforms": "微信公众号、小红书、朋友圈、视频号",
    "brand_tone": "专业、可信、通俗、务实，不夸大就业和收入效果",
    "current_year": datetime.now().year,
}


def load_inputs(
    path: Path | None = None,
    *,
    overrides: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    values = dict(DEFAULT_INPUTS)
    if path is not None:
        try:
            payload = json.loads(path.read_text(encoding="utf-8-sig"))
        except FileNotFoundError as exc:
            raise ValueError(f"输入文件不存在: {path}") from exc
        except json.JSONDecodeError as exc:
            raise ValueError(f"输入文件不是有效 JSON: {path}") from exc
        if not isinstance(payload, dict):
            raise ValueError("输入文件必须是 JSON 对象")
        values.update(payload)
    if overrides:
        values.update(overrides)

    try:
        values["current_year"] = int(values["current_year"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("current_year 必须是整数") from exc

    missing = [
        name
        for name in REQUIRED_INPUTS
        if name != "current_year" and not str(values.get(name, "")).strip()
    ]
    if missing:
        raise ValueError(f"缺少必填输入: {', '.join(missing)}")
    return values


def prepare_output_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    for filename in KNOWN_OUTPUT_FILES:
        target = path / filename
        if target.is_file():
            target.unlink()
    return path


def write_manifest(output_dir: Path, inputs: Mapping[str, Any]) -> Path:
    path = output_dir / "run_manifest.json"
    path.write_text(
        json.dumps(dict(inputs), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def validate_outputs(output_dir: Path) -> None:
    missing = [
        name for name in REQUIRED_GENERATED_FILES if not (output_dir / name).is_file()
    ]
    if missing:
        raise ValueError(f"missing generated output: {', '.join(missing)}")
    report = (output_dir / "research_report.md").read_text(encoding="utf-8")
    if "http://" not in report and "https://" not in report:
        raise ValueError("research report has no source URL")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成营销策略与平台文案")
    parser.add_argument("--input", type=Path, help="JSON 输入文件")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT_DIR / "output",
        help="本次运行的输出目录",
    )
    return parser.parse_args(argv)

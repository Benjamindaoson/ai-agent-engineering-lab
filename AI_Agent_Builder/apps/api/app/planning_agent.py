from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


REQUIRED_SLOTS = ["primary_goal", "target_role", "weekly_hours", "background", "project_domain"]


@dataclass(frozen=True)
class PlanningDecision:
    intent: dict[str, Any]
    context: dict[str, Any]
    status: str
    missing_slot: str | None
    assistant_message: str
    quick_options: list[str]


def run_planning_agent(message: str, context: dict[str, Any] | None = None) -> PlanningDecision:
    next_context = dict(context or {})
    extracted = extract_context(message)
    for key, value in extracted.items():
        if value not in (None, ""):
            next_context[key] = value

    intent = recognize_intent(next_context, message)
    next_context["primary_goal"] = next_context.get("primary_goal") or intent["primary_goal"]
    missing_slot = first_missing_slot(next_context)

    if missing_slot:
        return PlanningDecision(
            intent=intent,
            context=next_context,
            status="clarifying",
            missing_slot=missing_slot,
            assistant_message=clarification_message(missing_slot, next_context),
            quick_options=quick_options_for_slot(missing_slot),
        )

    return PlanningDecision(
        intent=intent,
        context=next_context,
        status="ready_to_confirm",
        missing_slot=None,
        assistant_message=ready_message(next_context),
        quick_options=["确认生成路线", "修改目标岗位", "修改每周时间"],
    )


def extract_context(message: str) -> dict[str, Any]:
    text = normalize(message)
    result: dict[str, Any] = {}

    if any(word in text for word in ["求职", "转行", "找工作", "面试", "简历"]):
        result["primary_goal"] = "求职转行"
    elif any(word in text for word in ["接单", "自由职业", "变现"]):
        result["primary_goal"] = "接单变现"
    elif any(word in text for word in ["企业", "内训", "员工", "团队"]):
        result["primary_goal"] = "企业内训"
    elif any(word in text for word in ["创业", "产品", "saas"]):
        result["primary_goal"] = "创业产品"
    elif any(word in text for word in ["学习", "提升", "补齐"]):
        result["primary_goal"] = "能力提升"

    if "rag" in text or "知识库" in text or "检索" in text:
        result["target_role"] = "RAG Builder"
        result["project_domain"] = result.get("project_domain") or "企业知识库 / 文档问答"
    if "workflow" in text or "工作流" in text:
        result["target_role"] = "Workflow Builder"
        result["project_domain"] = result.get("project_domain") or "业务流程自动化"
    if "自动化" in text or "工具调用" in text or "tool" in text:
        result["target_role"] = "AI Agent Builder"
        result["project_domain"] = result.get("project_domain") or "业务自动化 Agent"
    if "架构" in text:
        result["target_role"] = "AI Agent 架构师方向"

    weekly_hours = extract_number_before_unit(text, ["小时", "h"])
    if weekly_hours is not None:
        result["weekly_hours"] = max(4, min(30, weekly_hours))

    timeline_weeks = extract_timeline_weeks(text)
    if timeline_weeks is not None:
        result["timeline_weeks"] = timeline_weeks

    if any(word in text for word in ["零基础", "不会编程", "没写过代码"]):
        result["background"] = "零基础或编程基础较弱"
    elif any(word in text for word in ["会python", "会 python", "python/api", "api 基础", "写过代码", "有编程", "程序员"]):
        result["background"] = "有编程基础"
    elif any(word in text for word in ["产品经理", "运营", "业务", "非技术"]):
        result["background"] = "非技术背景，有业务理解"

    if any(word in text for word in ["时间少", "工作忙", "晚上", "周末"]):
        result["constraints"] = "学习时间有限，需要压缩路径和提高项目密度"
    if any(word in text for word in ["英文弱", "英语弱"]):
        result["constraints"] = merge_constraints(result.get("constraints"), "英文资料阅读压力较大")

    if any(word in text for word in ["求职", "简历", "岗位"]):
        result["project_domain"] = result.get("project_domain") or "AI 求职 / 岗位分析 Agent"
    if any(word in text for word in ["客服", "售后"]):
        result["project_domain"] = "客服知识库 Agent"
    if any(word in text for word in ["财务", "票据", "报销"]):
        result["project_domain"] = "财务票据分析 Agent"
    if any(word in text for word in ["邮件", "销售"]):
        result["project_domain"] = "邮件处理 / 销售自动化 Agent"

    return result


def recognize_intent(context: dict[str, Any], message: str) -> dict[str, Any]:
    primary_goal = context.get("primary_goal") or "能力提升"
    confidence = 0.55
    if primary_goal != "能力提升":
        confidence = 0.82
    if context.get("target_role"):
        confidence += 0.08
    if context.get("project_domain"):
        confidence += 0.05
    return {
        "primary_goal": primary_goal,
        "confidence": min(confidence, 0.95),
        "signals": extract_signals(message),
    }


def first_missing_slot(context: dict[str, Any]) -> str | None:
    for slot in REQUIRED_SLOTS:
        if not context.get(slot):
            return slot
    return None


def clarification_message(slot: str, context: dict[str, Any]) -> str:
    if slot == "primary_goal":
        return "我先确认你的核心目标：你学习 AI Agent 主要是为了求职转行、接单变现、企业内训、创业产品，还是单纯提升能力？"
    if slot == "target_role":
        return "你的目标角色更接近哪一种：AI Agent Builder、RAG Builder、Workflow Builder，还是 AI Agent 架构师方向？"
    if slot == "weekly_hours":
        return "你每周能稳定投入多少小时？这个会决定路线是 8 周冲刺、10 周稳态，还是更长周期。"
    if slot == "background":
        return "你当前基础是什么？比如零基础、会一点 Python、做过 Web/API、产品/运营背景，或者已经是工程师。"
    if slot == "project_domain":
        goal = context.get("primary_goal", "目标")
        return f"为了让路线服务于{goal}，你最想做哪类作品项目？例如知识库问答、业务自动化、求职分析、客服 Agent、财务票据或邮件处理。"
    return "我还需要一个关键信息，才能生成可靠的学习路线。"


def quick_options_for_slot(slot: str) -> list[str]:
    return {
        "primary_goal": ["求职转行", "接单变现", "企业内训", "创业产品"],
        "target_role": ["AI Agent Builder", "RAG Builder", "Workflow Builder", "AI Agent 架构师方向"],
        "weekly_hours": ["每周 6 小时", "每周 8 小时", "每周 12 小时", "每周 16 小时"],
        "background": ["零基础或编程较弱", "会一点 Python/API", "有工程经验", "产品/运营业务背景"],
        "project_domain": ["企业知识库 / 文档问答", "业务自动化 Agent", "AI 求职 / 岗位分析 Agent", "客服知识库 Agent"],
    }.get(slot, [])


def ready_message(context: dict[str, Any]) -> str:
    return (
        "信息已经足够生成第一版学习路线。"
        f"我识别到你的目标是{context['primary_goal']}，目标角色是{context['target_role']}，"
        f"每周投入约 {context['weekly_hours']} 小时，项目方向是{context['project_domain']}。"
        "你可以确认生成路线，也可以继续修改目标。"
    )


def intake_from_planning_context(context: dict[str, Any], existing: dict[str, Any] | None = None) -> dict[str, Any]:
    base = dict(existing or {})
    background = str(context.get("background", ""))
    primary_goal = str(context.get("primary_goal", "能力提升"))
    target_role = str(context.get("target_role", base.get("target_role", "AI Agent Builder")))
    weekly_hours = int(context.get("weekly_hours") or base.get("weekly_hours") or 8)

    programming_level = int(base.get("programming_level") or 2)
    if "零基础" in background or "较弱" in background:
        programming_level = 1
    elif "工程" in background or "Python" in background or "API" in background:
        programming_level = 3

    rag_level = int(base.get("rag_level") or 1)
    tool_use_level = int(base.get("tool_use_level") or 1)
    deployment_level = int(base.get("deployment_level") or 1)
    if target_role == "RAG Builder":
        rag_level = max(rag_level, 2)
    if target_role in {"AI Agent Builder", "Workflow Builder"}:
        tool_use_level = max(tool_use_level, 2)
    if primary_goal in {"求职转行", "接单变现"}:
        deployment_level = max(deployment_level, 2)

    return {
        "target_role": target_role,
        "weekly_hours": weekly_hours,
        "programming_level": programming_level,
        "prompt_level": int(base.get("prompt_level") or 3),
        "rag_level": rag_level,
        "tool_use_level": tool_use_level,
        "deployment_level": deployment_level,
        "career_goal": f"{primary_goal}：完成 {context.get('project_domain', 'AI Agent')} 方向的可展示项目，并生成 Skill Passport。",
        "constraints": str(context.get("constraints") or base.get("constraints") or ""),
    }


def normalize(message: str) -> str:
    return message.strip().lower()


def extract_number_before_unit(text: str, units: list[str]) -> int | None:
    for unit in units:
        match = re.search(rf"(\d+)\s*{re.escape(unit)}", text)
        if match:
            return int(match.group(1))
    return None


def extract_timeline_weeks(text: str) -> int | None:
    week_match = re.search(r"(\d+)\s*周", text)
    if week_match:
        return int(week_match.group(1))
    month_match = re.search(r"(\d+)\s*个?月", text)
    if month_match:
        return int(month_match.group(1)) * 4
    return None


def extract_signals(message: str) -> list[str]:
    signals = []
    for keyword in ["求职", "转行", "接单", "企业", "创业", "RAG", "知识库", "自动化", "部署", "简历"]:
        if keyword.lower() in message.lower():
            signals.append(keyword)
    return signals


def merge_constraints(current: str | None, extra: str) -> str:
    if not current:
        return extra
    if extra in current:
        return current
    return f"{current}；{extra}"

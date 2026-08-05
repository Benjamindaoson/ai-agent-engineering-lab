from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TutorDecision:
    content: str
    hint_level: int
    learning_signal: str
    ai_dependency_delta: int
    guardrail_triggered: bool
    next_checkpoint: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "content": self.content,
            "hint_level": self.hint_level,
            "learning_signal": self.learning_signal,
            "ai_dependency_delta": self.ai_dependency_delta,
            "guardrail_triggered": self.guardrail_triggered,
            "next_checkpoint": self.next_checkpoint,
        }


def run_tutor_agent(message: str, context: dict[str, Any]) -> TutorDecision:
    normalized = message.strip().lower()
    project_title = context.get("project_title") or "当前项目"
    task_title = context.get("task_title") or "当前任务"
    active_tasks = context.get("active_coach_tasks") or []
    latest_submission = context.get("latest_submission") or {}

    if _looks_like_answer_request(normalized):
        return TutorDecision(
            content=(
                "我不能替你完成可直接提交的成品。\n\n"
                f"下一步：先写《{project_title} / {task_title}》的方案草稿。\n"
                "为什么：招聘方要看你能不能自己拆问题，而不是复制答案。\n"
                "要提交：方案假设、输入/处理/输出三步、验证方法。\n"
                "风险：如果只交成品、没有过程证据，会被判断为 AI 代做风险。"
            ),
            hint_level=4,
            learning_signal="answer_request",
            ai_dependency_delta=28,
            guardrail_triggered=True,
            next_checkpoint="提交自己的方案草稿，而不是请求可复制答案。",
        )

    if active_tasks or latest_submission.get("latest_review"):
        task_text = active_tasks[0]["title"] if active_tasks else "最近一次 Review 暴露的薄弱项"
        latest_review = latest_submission.get("latest_review") or {}
        risk_count = len(latest_review.get("risk_flags") or [])
        return TutorDecision(
            content=(
                f"我已经读取了你最近的提交和检查结果。当前最该处理的是：{task_text}。\n\n"
                "下一步：先补一份可验证的修复材料。\n"
                f"为什么：这来自项目检查中的 {risk_count} 个风险提示，不是泛泛建议。\n"
                "要提交：一个失败样例、一个修复动作、一个重新运行的验证命令。\n"
                "风险：继续加功能会掩盖基础问题，求职报告里的可信度不会提高。"
            ),
            hint_level=2,
            learning_signal="review_remediation",
            ai_dependency_delta=5,
            guardrail_triggered=False,
            next_checkpoint="提交失败样例、修复动作和验证命令三项草稿。",
        )
    if _looks_like_debug_request(normalized):
        return TutorDecision(
            content=(
                "下一步：先做最小复现，不要改大段代码。\n"
                "为什么：没有复现就没有可靠修复，只是在猜。\n"
                "要提交：最小报错日志、触发输入、一个复现测试、重跑结果。\n"
                "风险：如果是 RAG 不稳定，优先查 chunk 边界、top_k、引用来源和空检索分支。"
            ),
            hint_level=2,
            learning_signal="debugging_need",
            ai_dependency_delta=8,
            guardrail_triggered=False,
            next_checkpoint="贴出最小复现、日志和你已经排除的原因。",
        )

    if _looks_like_planning_request(normalized):
        return TutorDecision(
            content=(
                f"下一步：把《{project_title}》拆成数据准备、核心链路、质量评测、交付说明四步。\n"
                "为什么：项目不是功能清单，而是一组可验证证据。\n"
                "要提交：样例输入输出、失败样例、评测指标和 README 说明。\n"
                "风险：没有评测指标的项目，招聘方很难相信它能在真实场景工作。"
            ),
            hint_level=2,
            learning_signal="implementation_planning",
            ai_dependency_delta=6,
            guardrail_triggered=False,
            next_checkpoint="补一版指标清单和对应测试样例。",
        )

    return TutorDecision(
        content=(
            "下一步：先说清楚你卡在哪里。\n"
            "为什么：概念不清、实现报错、评测不会做、交付材料不会写，对应的训练动作不同。\n"
            "要提交：选择一个卡点，并说明你已经尝试过什么。\n"
            "风险：如果问题太泛，AI 只能给泛泛建议，不能帮你推进项目。"
        ),
        hint_level=1,
        learning_signal="conceptual_gap",
        ai_dependency_delta=4,
        guardrail_triggered=False,
        next_checkpoint="明确一个卡点和一次已尝试动作。",
    )


def _looks_like_answer_request(text: str) -> bool:
    direct_answer_terms = [
        "直接",
        "完整代码",
        "帮我写完",
        "复制提交",
        "代做",
        "给我答案",
        "full code",
        "complete code",
    ]
    return any(term in text for term in direct_answer_terms)


def _looks_like_debug_request(text: str) -> bool:
    debug_terms = ["报错", "error", "exception", "traceback", "失败", "跑不通", "bug", "debug"]
    return any(term in text for term in debug_terms)


def _looks_like_planning_request(text: str) -> bool:
    planning_terms = ["怎么设计", "拆解", "思路", "评测", "架构", "下一步", "计划", "design", "plan", "eval"]
    return any(term in text for term in planning_terms)


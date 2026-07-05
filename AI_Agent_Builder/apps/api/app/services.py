from __future__ import annotations

import asyncio
import json
import time
from typing import Any

from .agent_kernel import record_agent_run
from .agent_runtime import AgentRuntimeUnavailable, ReviewRun, run_claude_agent_json, run_review
from .config import settings
from .db import DbConnection
from .planning_agent import PlanningDecision, intake_from_planning_context, run_planning_agent
from .review_schema import ReviewResult
from .sandbox import run_submission_sandbox
from .state import ensure_transition
from .tutor_agent import TutorDecision, run_tutor_agent
from .utils import new_id, now_iso


DEMO_USER_ID = settings.demo_learner_id


def row_to_dict(row: Any | None) -> dict[str, Any] | None:
    return dict(row) if row is not None else None


def elapsed_ms(started: float) -> int:
    return int((time.perf_counter() - started) * 1000)


def get_user(conn: DbConnection, learner_id: str) -> Any:
    row = conn.execute("SELECT * FROM users WHERE id = ?", (learner_id,)).fetchone()
    if row is None:
        raise ValueError("Learner missing.")
    return row


def list_jobs(conn: DbConnection) -> list[dict[str, Any]]:
    rows = conn.execute(
        "SELECT id, slug, title, description FROM target_jobs WHERE is_active = 1 ORDER BY title"
    ).fetchall()
    return [dict(row) for row in rows]


def select_job(conn: DbConnection, target_job_id: str, learner_id: str) -> dict[str, Any]:
    target_job = conn.execute("SELECT id FROM target_jobs WHERE id = ? AND is_active = 1", (target_job_id,)).fetchone()
    if target_job is None:
        raise ValueError("Target job not found")
    now = now_iso()
    conn.execute(
        "UPDATE users SET selected_target_job_id = ?, updated_at = ? WHERE id = ?",
        (target_job_id, now, learner_id),
    )
    ensure_learning_plan(conn, learner_id)
    return {"learner_id": learner_id, "target_job_id": target_job_id, "selected_at": now}


def normalize_agent_runtime(value: str) -> str:
    return "claude_agent_sdk" if value in {"claude", "claude_agent_sdk", "anthropic"} else "rule"


def get_agent_runtime_status() -> dict[str, Any]:
    reviewer_runtime = "claude_agent_sdk" if settings.agent_mode in {"claude", "claude_agent_sdk", "anthropic"} else "mock"
    return {
        "planner": {
            "active_runtime": normalize_agent_runtime(settings.planner_runtime),
            "available_runtimes": ["rule", "claude_agent_sdk"],
            "tool_runtime": "intent_parser, slot_clarifier, learning_plan_builder",
        },
        "tutor": {
            "active_runtime": normalize_agent_runtime(settings.tutor_runtime),
            "available_runtimes": ["rule", "claude_agent_sdk"],
            "tool_runtime": "hint_ladder, dependency_meter, project_context_reader",
        },
        "reviewer": {
            "active_runtime": reviewer_runtime,
            "available_runtimes": ["mock", "claude_agent_sdk"],
            "tool_runtime": "sandbox_logs, rubric_scorer, evidence_extractor",
        },
    }


def execute_planning_agent(message: str, context: dict[str, Any]) -> tuple[PlanningDecision, dict[str, Any]]:
    started = time.perf_counter()
    if normalize_agent_runtime(settings.planner_runtime) == "claude_agent_sdk":
        try:
            schema = {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "intent": {"type": "object"},
                    "context": {"type": "object"},
                    "status": {"type": "string", "enum": ["clarifying", "ready_to_confirm"]},
                    "missing_slot": {"type": ["string", "null"]},
                    "assistant_message": {"type": "string"},
                    "quick_options": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["intent", "context", "status", "missing_slot", "assistant_message", "quick_options"],
            }
            prompt = json.dumps(
                {
                    "task": "Act as AgentLab LearningPlannerAgent. Clarify learner intent and return a planning decision.",
                    "required_slots": ["primary_goal", "target_role", "weekly_hours", "background", "project_domain"],
                    "user_message": message,
                    "current_context": context,
                    "rules": [
                        "Ask for exactly one missing slot at a time.",
                        "Return ready_to_confirm only when all required slots are present.",
                        "Keep assistant_message concise and in Chinese.",
                        "Do not generate a full plan here; only produce the planning decision.",
                    ],
                },
                ensure_ascii=False,
            )
            run = asyncio.run(
                run_claude_agent_json(
                    prompt=prompt,
                    system_prompt="You are AgentLab's planning agent. Return JSON only.",
                    output_schema=schema,
                    max_turns=2,
                    started=started,
                )
            )
            data = json.loads(run.raw_output)
            return (
                PlanningDecision(
                    intent=dict(data["intent"]),
                    context=dict(data["context"]),
                    status=str(data["status"]),
                    missing_slot=data.get("missing_slot"),
                    assistant_message=str(data["assistant_message"]),
                    quick_options=list(data.get("quick_options") or []),
                ),
                {
                    "runtime": "claude_agent_sdk",
                    "provider": "anthropic",
                    "model": run.model,
                    "latency_ms": run.latency_ms,
                    "fallback_reason": None,
                },
            )
        except (AgentRuntimeUnavailable, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            decision = run_planning_agent(message, context)
            return (
                decision,
                {
                    "runtime": "rule",
                    "provider": "agentlab",
                    "model": None,
                    "latency_ms": elapsed_ms(started),
                    "fallback_reason": str(exc),
                },
            )

    decision = run_planning_agent(message, context)
    return (
        decision,
        {
            "runtime": "rule",
            "provider": "agentlab",
            "model": None,
            "latency_ms": elapsed_ms(started),
            "fallback_reason": None,
        },
    )


def execute_tutor_agent(message: str, context: dict[str, Any]) -> tuple[TutorDecision, dict[str, Any]]:
    started = time.perf_counter()
    if normalize_agent_runtime(settings.tutor_runtime) == "claude_agent_sdk":
        try:
            schema = {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "content": {"type": "string"},
                    "hint_level": {"type": "integer", "minimum": 1, "maximum": 4},
                    "learning_signal": {"type": "string"},
                    "ai_dependency_delta": {"type": "integer", "minimum": 0, "maximum": 40},
                    "guardrail_triggered": {"type": "boolean"},
                    "next_checkpoint": {"type": "string"},
                },
                "required": [
                    "content",
                    "hint_level",
                    "learning_signal",
                    "ai_dependency_delta",
                    "guardrail_triggered",
                    "next_checkpoint",
                ],
            }
            prompt = json.dumps(
                {
                    "task": "Act as AgentLab ProjectTutorAgent.",
                    "user_message": message,
                    "project_context": context,
                    "rules": [
                        "Coach in Chinese.",
                        "Do not write a full directly submittable solution for the learner.",
                        "Use a hint ladder: ask, hint, explain, local example, never default to full answer.",
                        "Increase ai_dependency_delta when the learner asks for direct answers or full code.",
                    ],
                },
                ensure_ascii=False,
            )
            run = asyncio.run(
                run_claude_agent_json(
                    prompt=prompt,
                    system_prompt="You are AgentLab's project tutor. Return JSON only.",
                    output_schema=schema,
                    max_turns=2,
                    started=started,
                )
            )
            data = json.loads(run.raw_output)
            return (
                TutorDecision(
                    content=str(data["content"]),
                    hint_level=int(data["hint_level"]),
                    learning_signal=str(data["learning_signal"]),
                    ai_dependency_delta=int(data["ai_dependency_delta"]),
                    guardrail_triggered=bool(data["guardrail_triggered"]),
                    next_checkpoint=str(data["next_checkpoint"]),
                ),
                {
                    "runtime": "claude_agent_sdk",
                    "provider": "anthropic",
                    "model": run.model,
                    "latency_ms": run.latency_ms,
                    "fallback_reason": None,
                },
            )
        except (AgentRuntimeUnavailable, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            decision = run_tutor_agent(message, context)
            return (
                decision,
                {
                    "runtime": "rule",
                    "provider": "agentlab",
                    "model": None,
                    "latency_ms": elapsed_ms(started),
                    "fallback_reason": str(exc),
                },
            )

    decision = run_tutor_agent(message, context)
    return (
        decision,
        {
            "runtime": "rule",
            "provider": "agentlab",
            "model": None,
            "latency_ms": elapsed_ms(started),
            "fallback_reason": None,
        },
    )


def build_next_best_action(
    conn: DbConnection,
    learner_id: str,
    projects: list[dict[str, Any]],
    learning_plan: dict[str, Any],
    evidence_count: int,
) -> dict[str, Any]:
    planning = conn.execute(
        """
        SELECT status
        FROM planning_sessions
        WHERE learner_id = ?
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (learner_id,),
    ).fetchone()
    if planning is None or planning["status"] != "confirmed":
        return {
            "type": "planning",
            "title": "先完成个性化学习路线规划",
            "reason": "系统还没有确认你的目标角色、时间约束和项目路径，后续课程与项目都应该由规划结果驱动。",
            "estimated_minutes": 8,
            "primary_cta": {"label": "启动规划 Agent", "href": "/intake"},
            "secondary_cta": {"label": "查看课程库", "href": "/courses"},
            "evidence_outcome": "产出目标角色、每周计划、推荐项目路径和能力短板。",
        }

    next_project = next((project for project in projects if project["status"] != "passed"), None)
    if next_project:
        return {
            "type": "project_lab",
            "title": f"进入 Project Lab：{next_project['title']}",
            "reason": "课程、Tutor、提交和质量门都围绕当前项目任务展开，这是最能产生招聘证据的下一步。",
            "estimated_minutes": 45,
            "primary_cta": {"label": "进入 Project Lab", "href": f"/lab/{next_project['learner_project_id']}"},
            "secondary_cta": {"label": "查看学习路线", "href": "/learning-plan"},
            "evidence_outcome": "产出 GitHub、Demo、架构图、评测报告与 Review 证据。",
        }

    if evidence_count == 0:
        return {
            "type": "quality_gate",
            "title": "补齐至少一个可验证项目证据",
            "reason": "招聘方不会只看完成状态，需要可追溯的提交物、评审报告和能力证据。",
            "estimated_minutes": 30,
            "primary_cta": {"label": "查看项目实战", "href": "/projects"},
            "secondary_cta": {"label": "查看 Agent Trace", "href": "/agent-traces"},
            "evidence_outcome": "让 Skill Passport 从学习记录变成招聘方可验证报告。",
        }

    return {
        "type": "passport",
        "title": "生成招聘方 Skill Passport",
        "reason": "你的项目路径已经形成，可以把项目、能力图谱、Review 和 AI Dependency 汇总成招聘报告。",
        "estimated_minutes": 10,
        "primary_cta": {"label": "生成 Skill Passport", "href": "/passport"},
        "secondary_cta": {"label": "查看能力图谱", "href": "/skill-map"},
        "evidence_outcome": "生成面向招聘方的能力证据档案。",
    }


def get_open_coach_tasks(conn: DbConnection, learner_id: str, limit: int = 3) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT *
        FROM coach_tasks
        WHERE learner_id = ? AND status = 'open'
        ORDER BY priority, created_at DESC
        LIMIT ?
        """,
        (learner_id, limit),
    ).fetchall()
    return [{**dict(row), "actions": json.loads(row["action_json"])} for row in rows]


def get_latest_planning_signal(conn: DbConnection, learner_id: str) -> dict[str, Any]:
    row = conn.execute(
        """
        SELECT status, missing_slot
        FROM planning_sessions
        WHERE learner_id = ?
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (learner_id,),
    ).fetchone()
    return dict(row) if row else {"status": "missing", "missing_slot": "primary_goal"}


def build_agent_decision(
    *,
    planning: dict[str, Any],
    next_best_action: dict[str, Any],
    learning_plan: dict[str, Any],
    skill_gaps: list[dict[str, Any]],
    evidence_count: int,
    open_coach_tasks: list[dict[str, Any]],
) -> dict[str, Any]:
    missing_inputs = []
    if planning.get("status") != "confirmed":
        missing_inputs.append(str(planning.get("missing_slot") or "confirmed_learning_goal"))
    if next_best_action["type"] == "project_lab" and not evidence_count:
        missing_inputs.append("first_verified_project_evidence")

    top_gap = skill_gaps[0] if skill_gaps else None
    reasoning = [
        {
            "title": "路线状态",
            "detail": "学习路线已确认，可以进入项目交付。" if planning.get("status") == "confirmed" else "目标、时间或项目方向还未确认，先完成规划。",
        },
        {
            "title": "能力缺口",
            "detail": f"{top_gap['name']} 距离目标还差 {top_gap['gap']} 分。" if top_gap else "暂未发现明显能力缺口，继续积累项目证据。",
        },
        {
            "title": "证据状态",
            "detail": f"Evidence Store 已有 {evidence_count} 条证据。" if evidence_count else "还没有可验证项目证据，招聘可信度不足。",
        },
    ]
    if open_coach_tasks:
        reasoning.insert(
            0,
            {
                "title": "Review 后任务",
                "detail": f"还有 {len(open_coach_tasks)} 个 Review Agent 生成的修复任务未完成。",
            },
        )

    return {
        "agent_name": "AICoachAgent",
        "status": "ready" if not missing_inputs else "needs_input",
        "primary_action": {
            "type": next_best_action["type"],
            "label": next_best_action["primary_cta"]["label"],
            "href": next_best_action["primary_cta"]["href"],
        },
        "reasoning": reasoning,
        "missing_inputs": missing_inputs,
        "evidence_outcome": next_best_action.get("evidence_outcome"),
        "target_role": learning_plan["target_role"],
    }


def build_workspace_state(
    conn: DbConnection,
    learner_id: str,
    *,
    projects: list[dict[str, Any]],
    learning_plan: dict[str, Any],
    adaptive_courses: list[dict[str, Any]],
    skill_gaps: list[dict[str, Any]],
    next_best_action: dict[str, Any],
    next_project: dict[str, Any] | None,
    evidence_count: int,
) -> dict[str, Any]:
    planning = get_latest_planning_signal(conn, learner_id)
    open_coach_tasks = get_open_coach_tasks(conn, learner_id)
    latest_evidence = list_evidence(conn, learner_id)[:3]

    if planning.get("status") != "confirmed":
        learner_stage = "planning"
    elif open_coach_tasks:
        learner_stage = "review_repair"
    elif next_project:
        learner_stage = "project_delivery"
    elif evidence_count:
        learner_stage = "passport_ready"
    else:
        learner_stage = "evidence_building"

    return {
        "learner_stage": learner_stage,
        "next_best_action": next_best_action,
        "active_project": next_project,
        "recommended_course": adaptive_courses[0] if adaptive_courses else None,
        "open_coach_tasks": open_coach_tasks,
        "latest_evidence": latest_evidence,
        "agent_decision": build_agent_decision(
            planning=planning,
            next_best_action=next_best_action,
            learning_plan=learning_plan,
            skill_gaps=skill_gaps,
            evidence_count=evidence_count,
            open_coach_tasks=open_coach_tasks,
        ),
    }


def get_dashboard(conn: DbConnection, learner_id: str) -> dict[str, Any]:
    ensure_learning_plan(conn, learner_id)
    projects = list_projects(conn, learner_id)
    learning_plan = get_learning_plan(conn, learner_id)
    skill_map = get_skill_map(conn, learner_id)
    adaptive_courses = get_adaptive_courses(conn, learner_id)
    evidence_count = conn.execute(
        "SELECT COUNT(*) AS count FROM evidence_items WHERE learner_id = ?",
        (learner_id,),
    ).fetchone()["count"]
    next_project = next((project for project in projects if project["status"] != "passed"), projects[0] if projects else None)
    skill_gaps = sorted(
        [
            {
                "slug": skill["slug"],
                "name": skill["name"],
                "gap": max(0, int(skill["required_level"]) - int(skill["current_score"])),
                "current_score": skill["current_score"],
                "required_level": skill["required_level"],
            }
            for skill in skill_map["skills"]
        ],
        key=lambda item: item["gap"],
        reverse=True,
    )[:4]
    next_best_action = build_next_best_action(conn, learner_id, projects, learning_plan, evidence_count)
    workspace_state = build_workspace_state(
        conn,
        learner_id,
        projects=projects,
        learning_plan=learning_plan,
        adaptive_courses=adaptive_courses["courses"][:5],
        skill_gaps=skill_gaps,
        next_best_action=next_best_action,
        next_project=next_project,
        evidence_count=evidence_count,
    )
    return {
        "learner": row_to_dict(get_user(conn, learner_id)),
        "learning_plan": learning_plan,
        "next_best_action": next_best_action,
        "workspace_state": workspace_state,
        "next_project": next_project,
        "projects": projects,
        "skill_gaps": skill_gaps,
        "adaptive_courses": adaptive_courses["courses"][:5],
        "evidence_count": evidence_count,
        "agent_runtimes": get_agent_runtime_status(),
    }


def get_agent_command_center(
    conn: DbConnection,
    learner_id: str,
    learner_project_id: str | None = None,
) -> dict[str, Any]:
    dashboard = get_dashboard(conn, learner_id)
    workspace = dashboard["workspace_state"]
    decision = workspace["agent_decision"]
    learning_plan = dashboard["learning_plan"]
    runtimes = dashboard["agent_runtimes"]
    project_summary = dashboard["next_project"]
    if learner_project_id:
        project_summary = next(
            (project for project in dashboard["projects"] if project["learner_project_id"] == learner_project_id),
            None,
        )
        if project_summary is None:
            raise ValueError("Project not found")
    active_project = build_command_center_project(conn, learner_id, project_summary)
    course_items = build_command_center_courses(dashboard["adaptive_courses"][:5])
    quality_gate = build_command_center_quality_gate(active_project)
    workflow = build_command_center_workflow(workspace["learner_stage"], active_project, quality_gate)
    handoffs = build_command_center_handoffs(active_project, course_items, quality_gate)
    agent_queue = build_agent_command_queue(
        conn,
        learner_id,
        active_project=active_project,
        course_items=course_items,
        quality_gate=quality_gate,
        fallback_action=decision["primary_action"],
        allow_global_fallback=learner_project_id is None,
    )
    next_action_href = active_project["workspace_href"] if learner_project_id and active_project else decision["primary_action"]["href"]

    return {
        "contract_version": "agent_command_center.v1",
        "learner": {
            "id": dashboard["learner"]["id"],
            "display_name": dashboard["learner"]["display_name"],
            "email": dashboard["learner"]["email"],
            "target_role": learning_plan["target_role"],
            "weekly_hours": learning_plan.get("weekly_hours", 0),
        },
        "agent": {
            "name": "AICoachAgent",
            "mode": runtimes["planner"]["active_runtime"],
            "status": decision["status"],
            "stage": workspace["learner_stage"],
            "tools": [
                "IntentClarificationAgent",
                "LearningPathPlanner",
                "CourseRecommender",
                "ProjectTutorAgent",
                "ReviewQualityGate",
                "EvidenceStoreWriter",
            ],
            "reasoning": decision["reasoning"],
            "missing_inputs": decision["missing_inputs"],
            "runtime_status": runtimes,
        },
        "mission": {
            "title": dashboard["next_best_action"]["title"],
            "reason": dashboard["next_best_action"]["reason"],
            "estimated_minutes": dashboard["next_best_action"]["estimated_minutes"],
            "success_evidence": dashboard["next_best_action"]["evidence_outcome"],
            "next_best_action": {
                "type": decision["primary_action"]["type"],
                "label": decision["primary_action"]["label"],
                "href": canonical_agent_href(next_action_href),
            },
            "secondary_action": dashboard["next_best_action"]["secondary_cta"],
        },
        "workflow": workflow,
        "active_project": active_project,
        "course_queue": {
            "strategy": "任务驱动的最小课程补给",
            "storage": {
                "module_table": "course_modules",
                "lesson_table": "course_lessons",
                "binding_table": "task_course_modules",
                "progress_table": "course_progress",
            },
            "items": course_items,
        },
        "quality_gate": quality_gate,
        "agent_queue": agent_queue,
        "tutor": {
            "name": "ProjectTutorAgent",
            "policy": "先追问，再提示，再解释，再给局部示例；不直接代写完整提交物。",
            "entry_href": handoffs["project_lab"]["href"],
            "ai_dependency_guardrail": "记录提示层级和 AI Dependency Score，防止学员只复制答案。",
        },
        "evidence": {
            "store": "evidence_items",
            "count": dashboard["evidence_count"],
            "latest_items": workspace["latest_evidence"],
            "top_skill_gaps": dashboard["skill_gaps"],
            "passport_href": "/passport",
        },
        "data_sources": {
            "learning_plan": "learning_plans.plan_json",
            "planning": "planning_sessions + planning_messages + planning_agent_runs",
            "projects": "learner_projects + project_templates + tasks",
            "courses": "course_modules + task_course_modules + course_progress",
            "tutor": "tutor_sessions + tutor_messages + agent_traces",
            "review": "submissions + review_jobs + reviews + sandbox_runs",
            "agent_queue": "planning + course_progress + submissions + reviews + coach_tasks + evidence_items",
            "evidence": "evidence_items + learner_skill_scores",
        },
        "handoffs": handoffs,
    }


def canonical_agent_href(href: str) -> str:
    if href.startswith("/projects/"):
        return href.replace("/projects/", "/lab/")
    if href.startswith("/courses/"):
        return href.replace("/courses/", "/learn/")
    return href


def build_command_center_project(
    conn: DbConnection,
    learner_id: str,
    project_summary: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if project_summary is None:
        return None
    project = get_project(conn, project_summary["learner_project_id"], learner_id)
    tasks = []
    for task in project["tasks"]:
        tasks.append(
            {
                "id": task["id"],
                "slug": task["slug"],
                "title": task["title"],
                "description": task["description"],
                "required_submission_types": task["required_submission_types"],
                "courses": [
                    {
                        "id": course["id"],
                        "title": course["title"],
                        "category": course["category"],
                        "estimated_minutes": course["estimated_minutes"],
                        "href": f"/learn/{course['id']}",
                        "reason": course.get("reason") or course.get("recommendation_reason"),
                    }
                    for course in task["recommended_courses"]
                ],
            }
        )
    return {
        "id": project["id"],
        "slug": project["project_template_slug"],
        "title": project["title"],
        "description": project["description"],
        "status": project["status"],
        "workspace_href": f"/lab/{project['id']}",
        "tasks": tasks,
        "coach_tasks": project["coach_tasks"],
        "latest_submission": project["latest_submission"],
    }


def build_command_center_courses(courses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "id": course["id"],
            "slug": course["slug"],
            "title": course["title"],
            "description": course["description"],
            "category": course["category"],
            "difficulty": course["difficulty"],
            "estimated_minutes": course["estimated_minutes"],
            "status": course["status"],
            "priority_score": course.get("priority_score", 0),
            "reason": course.get("recommendation_reason") or course.get("reason") or "匹配当前项目任务。",
            "href": f"/learn/{course['id']}",
        }
        for course in courses
    ]


def build_command_center_quality_gate(active_project: dict[str, Any] | None) -> dict[str, Any]:
    latest_submission = active_project.get("latest_submission") if active_project else None
    if latest_submission is None:
        status = "not_started"
        href = "/projects"
        review_id = None
        submission_id = None
    else:
        submission_id = latest_submission["id"]
        review_id = latest_submission.get("latest_review_id")
        if latest_submission["status"] in {"passed", "review_completed"}:
            status = "passed"
        elif latest_submission["status"] == "needs_revision":
            status = "needs_revision"
        else:
            status = "queued"
        href = f"/report/{review_id}" if review_id else "/projects"

    return {
        "status": status,
        "href": href,
        "submission_id": submission_id,
        "review_id": review_id,
        "required_checks": ["sandbox", "agent_review", "rubric", "evidence_write"],
        "acceptance": [
            "提交物能真实运行并产生日志",
            "Agent Review 输出结构化 Rubric",
            "关键能力证据写入 Evidence Store",
            "风险和下一轮任务可追踪",
        ],
    }


def build_command_center_workflow(
    learner_stage: str,
    active_project: dict[str, Any] | None,
    quality_gate: dict[str, Any],
) -> dict[str, Any]:
    current_step_id = {
        "planning": "plan",
        "project_delivery": "build",
        "review_repair": "review",
        "evidence_building": "review",
        "passport_ready": "passport",
    }.get(learner_stage, "plan")
    course_count = sum(len(task["courses"]) for task in active_project["tasks"]) if active_project else 0
    steps = [
        {
            "id": "plan",
            "label": "规划",
            "status": "active" if current_step_id == "plan" else "done",
            "agent": "LearningPathPlanner",
            "output": "目标、基础、时间约束、项目路径",
        },
        {
            "id": "learn",
            "label": "课程",
            "status": "active" if current_step_id == "learn" else ("done" if course_count else "waiting"),
            "agent": "CourseRecommender",
            "output": f"{course_count} 个与任务绑定的微课程",
        },
        {
            "id": "build",
            "label": "项目",
            "status": "active" if current_step_id == "build" else ("waiting" if not active_project else "ready"),
            "agent": "ProjectTutorAgent",
            "output": active_project["title"] if active_project else "等待项目路径",
        },
        {
            "id": "review",
            "label": "质量门",
            "status": "active" if current_step_id == "review" else quality_gate["status"],
            "agent": "ReviewAgent",
            "output": "Sandbox、Rubric、风险、证据",
        },
        {
            "id": "passport",
            "label": "Skill Passport",
            "status": "active" if current_step_id == "passport" else "waiting",
            "agent": "EvidenceStoreWriter",
            "output": "招聘方能力证据报告",
        },
    ]
    return {"current_step_id": current_step_id, "steps": steps}


def build_command_center_handoffs(
    active_project: dict[str, Any] | None,
    course_items: list[dict[str, Any]],
    quality_gate: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    project_href = active_project["workspace_href"] if active_project else "/projects"
    first_course_href = course_items[0]["href"] if course_items else "/courses"
    return {
        "planning": {"label": "更新学习路线", "href": "/intake"},
        "project_lab": {"label": "进入 Project Lab", "href": project_href},
        "courses": {"label": "打开推荐微课程", "href": first_course_href},
        "review": {"label": "进入质量门", "href": quality_gate["href"]},
        "passport": {"label": "生成 Skill Passport", "href": "/passport"},
    }


def build_agent_command_queue(
    conn: DbConnection,
    learner_id: str,
    *,
    active_project: dict[str, Any] | None,
    course_items: list[dict[str, Any]],
    quality_gate: dict[str, Any],
    fallback_action: dict[str, Any] | None = None,
    allow_global_fallback: bool = False,
) -> dict[str, Any]:
    project_href = active_project["workspace_href"] if active_project else "/projects"
    project_id = active_project["id"] if active_project else None
    course_handoff = (
        {"label": course_items[0]["title"], "href": course_items[0]["href"]}
        if course_items
        else {"label": "查看自适应课程队列", "href": "/courses"}
    )
    coach_tasks = active_project.get("coach_tasks", []) if active_project else []
    if not coach_tasks and allow_global_fallback:
        coach_tasks = list_active_coach_tasks(conn, learner_id)
    commands = [
        build_command_from_coach_task(
            conn,
            task,
            project_href=project_href,
            course_handoff=course_handoff,
            quality_gate=quality_gate,
        )
        for task in coach_tasks
    ]

    if not commands and fallback_action:
        commands.append(
            {
                "id": f"fallback:{fallback_action['type']}",
                "source_type": "agent_decision",
                "source_id": fallback_action["type"],
                "agent": "AICoachAgent",
                "status": "open",
                "priority": 90,
                "title": fallback_action["label"],
                "reason": "当前没有 Review 生成的修复任务，系统使用 Agent 决策作为下一步动作。",
                "actions": [
                    {
                        "type": fallback_action["type"],
                        "label": fallback_action["label"],
                        "instruction": "按 Agent 指挥中心给出的下一步动作推进。",
                        "deliverable": "产出下一条可验证学习或项目证据。",
                    }
                ],
                "primary_handoff": {"label": fallback_action["label"], "href": canonical_agent_href(fallback_action["href"])},
                "course_handoff": course_handoff,
                "quality_gate": quality_gate,
                "evidence_outcome": "产出下一条可验证学习或项目证据。",
                "project_id": project_id,
                "created_at": None,
            }
        )

    return {
        "contract_version": "agent_command_queue.v1",
        "source": "planning + course_progress + submissions + reviews + coach_tasks + evidence_items",
        "policy": "所有页面只读取同一组 Agent commands：先处理 Review 风险，再补课程缺口，最后回到 Project Lab 重新提交质量门。",
        "commands": sorted(commands, key=lambda item: (item["priority"], item["created_at"] or "")),
    }


def build_command_from_coach_task(
    conn: DbConnection,
    task: dict[str, Any],
    *,
    project_href: str,
    course_handoff: dict[str, Any],
    quality_gate: dict[str, Any],
) -> dict[str, Any]:
    actions = task.get("actions") or []
    primary_action = actions[0] if actions else {
        "type": "coach_task",
        "label": task["title"],
        "instruction": task["reason"],
        "deliverable": "补充项目证据并重新提交质量门。",
    }
    review_id = task.get("review_id")
    review_job_id = None
    if review_id:
        row = conn.execute("SELECT review_job_id FROM reviews WHERE id = ?", (review_id,)).fetchone()
        review_job_id = row["review_job_id"] if row else None
    gate_href = f"/gate/{review_job_id}" if review_job_id else quality_gate["href"]
    task_project_href = f"/lab/{task['learner_project_id']}" if task.get("learner_project_id") else project_href

    return {
        "id": task["id"],
        "source_type": task["source_type"],
        "source_id": review_id or task["id"],
        "agent": "AICoachAgent",
        "status": task["status"],
        "priority": task["priority"],
        "title": task["title"],
        "reason": task["reason"],
        "actions": actions,
        "primary_handoff": {"label": "进入 Project Lab 执行", "href": task_project_href},
        "course_handoff": course_handoff,
        "quality_gate": {
            **quality_gate,
            "href": gate_href,
        },
        "evidence_outcome": primary_action.get("deliverable") or "补充项目证据并重新提交质量门。",
        "project_id": task.get("learner_project_id"),
        "created_at": task["created_at"],
    }


def get_demo_mode(conn: DbConnection, learner_id: str) -> dict[str, Any]:
    dashboard = get_dashboard(conn, learner_id)
    next_project_href = (
        f"/projects/{dashboard['next_project']['learner_project_id']}"
        if dashboard["next_project"]
        else "/projects"
    )
    steps = [
        {
            "name": "目标识别",
            "promise": "识别学员是为了求职、转行、企业内训、接单还是创业。",
            "screen": "规划 Agent",
            "proof": "intent + context 被记录到 planning_sessions 与 Agent Trace。",
            "status": "ready",
            "href": "/intake",
        },
        {
            "name": "个性化路线",
            "promise": "把目标、基础、时间约束转成每周计划、项目路径和能力短板。",
            "screen": "学习路线",
            "proof": "learning_plans.plan_json 是后续推荐和项目分配的依据。",
            "status": "ready",
            "href": "/learning-plan",
        },
        {
            "name": "Project Lab",
            "promise": "学员在一个核心工作台完成任务、课程补给、提交和 Tutor 互动。",
            "screen": "项目实战",
            "proof": "每个任务绑定课程、提交要求和评审入口。",
            "status": "ready",
            "href": next_project_href,
        },
        {
            "name": "Tutor 辅导",
            "promise": "右侧常驻教练只给分层提示，并记录 AI Dependency。",
            "screen": "项目内导师",
            "proof": "tutor_messages、tutor_agent_runs 和 agent_traces 持续沉淀。",
            "status": "ready",
            "href": next_project_href,
        },
        {
            "name": "质量门评审",
            "promise": "提交物必须经过 Sandbox、Agent Review、Rubric 与风险标记。",
            "screen": "Review Gate",
            "proof": "review_jobs、sandbox_runs、agent_runs、reviews 形成可追溯链路。",
            "status": "ready",
            "href": "/projects",
        },
        {
            "name": "能力证据",
            "promise": "每次评审把项目表现写入 Evidence Store 并更新能力图谱。",
            "screen": "能力图谱",
            "proof": "evidence_items 与 learner_skill_scores 是系统数据资产。",
            "status": "ready",
            "href": "/skill-map",
        },
        {
            "name": "Skill Passport",
            "promise": "生成包含项目、Demo、GitHub、Review、能力图谱和 AI Dependency 的档案。",
            "screen": "招聘方报告",
            "proof": "passport_snapshots 固化每个版本，可用于对外展示。",
            "status": "ready",
            "href": "/passport",
        },
        {
            "name": "招聘方验证",
            "promise": "用证据链回答招聘方最关心的问题：是否能独立交付，是否可信。",
            "screen": "Investor Demo",
            "proof": "Demo Mode 串起完整商业闭环。",
            "status": "ready",
            "href": "/demo",
        },
    ]
    return {
        "headline": "TIAI 第一版 Investor Demo Mode",
        "positioning": "AI Agent 工程师训练、评测与招聘证据系统。",
        "next_best_action": dashboard["next_best_action"],
        "steps": steps,
        "metrics": {
            "projects": len(dashboard["projects"]),
            "evidence_count": dashboard["evidence_count"],
            "adaptive_courses": len(dashboard["adaptive_courses"]),
            "agent_runtimes": dashboard["agent_runtimes"],
        },
    }


def get_intake_assessment(conn: DbConnection, learner_id: str) -> dict[str, Any]:
    ensure_learning_plan(conn, learner_id)
    row = conn.execute("SELECT * FROM intake_assessments WHERE learner_id = ?", (learner_id,)).fetchone()
    if row is None:
        raise ValueError("Intake assessment not found")
    return dict(row)


def save_intake_assessment(conn: DbConnection, learner_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    now = now_iso()
    existing = conn.execute("SELECT id FROM intake_assessments WHERE learner_id = ?", (learner_id,)).fetchone()
    values = (
        payload["target_role"],
        int(payload["weekly_hours"]),
        int(payload["programming_level"]),
        int(payload["prompt_level"]),
        int(payload["rag_level"]),
        int(payload["tool_use_level"]),
        int(payload["deployment_level"]),
        payload["career_goal"],
        payload.get("constraints"),
        now,
    )
    if existing:
        conn.execute(
            """
            UPDATE intake_assessments
            SET target_role = ?, weekly_hours = ?, programming_level = ?, prompt_level = ?,
                rag_level = ?, tool_use_level = ?, deployment_level = ?, career_goal = ?,
                constraints = ?, updated_at = ?
            WHERE learner_id = ?
            """,
            (*values, learner_id),
        )
    else:
        conn.execute(
            """
            INSERT INTO intake_assessments (
              id, learner_id, target_role, weekly_hours, programming_level, prompt_level,
              rag_level, tool_use_level, deployment_level, career_goal, constraints,
              created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(learner_id) DO NOTHING
            """,
            (new_id(), learner_id, *values[:-1], now, now),
        )
    regenerate_learning_plan(conn, learner_id)
    return get_learning_plan(conn, learner_id)


def get_current_planning_session(conn: DbConnection, learner_id: str) -> dict[str, Any]:
    ensure_learning_plan(conn, learner_id)
    row = conn.execute(
        """
        SELECT *
        FROM planning_sessions
        WHERE learner_id = ?
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (learner_id,),
    ).fetchone()
    if row is None:
        return {
            "session": None,
            "messages": [],
            "learning_plan": get_learning_plan(conn, learner_id),
            "intake": get_intake_assessment(conn, learner_id),
        }
    return serialize_planning_session(conn, row, learner_id)


def create_planning_session(conn: DbConnection, learner_id: str, message: str) -> dict[str, Any]:
    get_user(conn, learner_id)
    now = now_iso()
    session_id = new_id()
    conn.execute(
        """
        INSERT INTO planning_sessions (
          id, learner_id, status, intent_json, context_json, plan_preview_json,
          missing_slot, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (session_id, learner_id, "started", "{}", "{}", None, None, now, now),
    )
    add_planning_message(conn, session_id, "user", message)
    return advance_planning_session(conn, session_id, learner_id, message)


def add_planning_user_message(conn: DbConnection, session_id: str, learner_id: str, message: str) -> dict[str, Any]:
    session = require_planning_session(conn, session_id, learner_id)
    if session["status"] == "confirmed":
        raise ValueError("Planning session already confirmed")
    add_planning_message(conn, session_id, "user", message)
    return advance_planning_session(conn, session_id, learner_id, message)


def confirm_planning_session(conn: DbConnection, session_id: str, learner_id: str) -> dict[str, Any]:
    session = require_planning_session(conn, session_id, learner_id)
    context = json.loads(session["context_json"])
    decision, trace_meta = execute_planning_agent("确认生成路线", context)
    if decision.status != "ready_to_confirm":
        raise ValueError("Planning session still needs clarification")

    existing_intake = row_to_dict(
        conn.execute("SELECT * FROM intake_assessments WHERE learner_id = ?", (learner_id,)).fetchone()
    )
    intake_payload = intake_from_planning_context(decision.context, existing_intake)
    plan = save_intake_assessment(conn, learner_id, intake_payload)
    now = now_iso()
    conn.execute(
        """
        UPDATE planning_sessions
        SET status = ?, intent_json = ?, context_json = ?, plan_preview_json = ?,
            missing_slot = ?, updated_at = ?, confirmed_at = ?
        WHERE id = ?
        """,
        (
            "confirmed",
            json.dumps(decision.intent),
            json.dumps(decision.context),
            json.dumps(plan),
            None,
            now,
            now,
            session_id,
        ),
    )
    add_planning_message(conn, session_id, "assistant", "已确认并生成新的个性化学习路线。")
    record_planning_agent_run(conn, session_id, "LearningPlannerAgent", {"context": decision.context}, plan, trace_meta)
    return {**serialize_planning_session(conn, require_planning_session(conn, session_id, learner_id), learner_id), "learning_plan": plan}


def advance_planning_session(conn: DbConnection, session_id: str, learner_id: str, message: str) -> dict[str, Any]:
    session = require_planning_session(conn, session_id, learner_id)
    context = json.loads(session["context_json"])
    decision, trace_meta = execute_planning_agent(message, context)
    plan_preview = None
    if decision.status == "ready_to_confirm":
        existing_intake = row_to_dict(
            conn.execute("SELECT * FROM intake_assessments WHERE learner_id = ?", (learner_id,)).fetchone()
        )
        intake_payload = intake_from_planning_context(decision.context, existing_intake)
        plan_preview = build_learning_plan(intake_payload)

    now = now_iso()
    conn.execute(
        """
        UPDATE planning_sessions
        SET status = ?, intent_json = ?, context_json = ?, plan_preview_json = ?,
            missing_slot = ?, updated_at = ?
        WHERE id = ?
        """,
        (
            decision.status,
            json.dumps(decision.intent),
            json.dumps(decision.context),
            json.dumps(plan_preview) if plan_preview else None,
            decision.missing_slot,
            now,
            session_id,
        ),
    )
    add_planning_message(
        conn,
        session_id,
        "assistant",
        decision.assistant_message,
        {"quick_options": decision.quick_options, "missing_slot": decision.missing_slot},
    )
    record_planning_agent_run(
        conn,
        session_id,
        "IntentClarificationAgent",
        {"message": message, "previous_context": context},
        {
            "intent": decision.intent,
            "context": decision.context,
            "status": decision.status,
            "missing_slot": decision.missing_slot,
            "quick_options": decision.quick_options,
        },
        trace_meta,
    )
    record_planning_agent_run(
        conn,
        session_id,
        "LearningPlannerAgent",
        {"message": message, "context": decision.context},
        {
            "status": decision.status,
            "missing_slot": decision.missing_slot,
            "plan_preview": plan_preview,
            "next_step": "confirm_plan" if plan_preview else "continue_clarifying",
        },
        trace_meta,
    )
    return serialize_planning_session(conn, require_planning_session(conn, session_id, learner_id), learner_id)


def require_planning_session(conn: DbConnection, session_id: str, learner_id: str) -> Any:
    row = conn.execute(
        "SELECT * FROM planning_sessions WHERE id = ? AND learner_id = ?",
        (session_id, learner_id),
    ).fetchone()
    if row is None:
        raise ValueError("Planning session not found")
    return row


def add_planning_message(
    conn: DbConnection,
    session_id: str,
    role: str,
    content: str,
    payload: dict[str, Any] | None = None,
) -> None:
    conn.execute(
        """
        INSERT INTO planning_messages (id, session_id, role, content, payload_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (new_id(), session_id, role, content, json.dumps(payload) if payload else None, now_iso()),
    )


def record_planning_agent_run(
    conn: DbConnection,
    session_id: str,
    agent_name: str,
    input_data: dict[str, Any],
    output_data: dict[str, Any],
    trace_meta: dict[str, Any] | None = None,
) -> None:
    session = conn.execute("SELECT learner_id FROM planning_sessions WHERE id = ?", (session_id,)).fetchone()
    conn.execute(
        """
        INSERT INTO planning_agent_runs (
          id, session_id, agent_name, input_json, output_json, status, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (new_id(), session_id, agent_name, json.dumps(input_data), json.dumps(output_data), "succeeded", now_iso()),
    )
    if session:
        meta = trace_meta or {
            "runtime": "rule",
            "provider": "agentlab",
            "model": None,
            "latency_ms": None,
            "fallback_reason": None,
        }
        trace_output = dict(output_data)
        if meta.get("fallback_reason"):
            trace_output["fallback_reason"] = meta["fallback_reason"]
        agent_run_id = record_agent_run(
            conn,
            learner_id=session["learner_id"],
            agent_name=agent_name,
            runtime=meta["runtime"],
            provider=meta["provider"],
            model=meta["model"],
            input_data=input_data,
            output_data=trace_output,
            status="succeeded",
            latency_ms=meta["latency_ms"],
            parent_type="planning_session",
            parent_id=session_id,
            tool_names=["intent_parser", "slot_clarifier", "learning_plan_builder"],
            mode=meta["runtime"],
            prompt_version="planner-v1",
        )
        record_agent_trace(
            conn,
            agent_run_id=agent_run_id,
            learner_id=session["learner_id"],
            agent_name=agent_name,
            runtime=meta["runtime"],
            provider=meta["provider"],
            model=meta["model"],
            input_data=input_data,
            output_data=trace_output,
            status="succeeded",
            latency_ms=meta["latency_ms"],
            parent_type="planning_session",
            parent_id=session_id,
            tool_names=["intent_parser", "slot_clarifier", "learning_plan_builder"],
        )


def record_agent_trace(
    conn: DbConnection,
    *,
    agent_run_id: str | None = None,
    learner_id: str,
    agent_name: str,
    runtime: str,
    provider: str,
    model: str | None,
    input_data: dict[str, Any],
    output_data: dict[str, Any],
    status: str,
    latency_ms: int | None,
    parent_type: str | None,
    parent_id: str | None,
    tool_names: list[str] | None = None,
) -> None:
    conn.execute(
        """
        INSERT INTO agent_traces (
          id, agent_run_id, learner_id, agent_name, runtime, provider, model, tool_names_json,
          input_json, output_json, status, latency_ms, parent_type, parent_id, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            new_id(),
            agent_run_id,
            learner_id,
            agent_name,
            runtime,
            provider,
            model,
            json.dumps(tool_names or []),
            json.dumps(input_data),
            json.dumps(output_data),
            status,
            latency_ms,
            parent_type,
            parent_id,
            now_iso(),
        ),
    )


def serialize_planning_session(conn: DbConnection, session: Any, learner_id: str) -> dict[str, Any]:
    messages = conn.execute(
        """
        SELECT id, role, content, payload_json, created_at
        FROM planning_messages
        WHERE session_id = ?
        ORDER BY created_at
        """,
        (session["id"],),
    ).fetchall()
    agent_runs = conn.execute(
        """
        SELECT id, agent_name, status, created_at
        FROM planning_agent_runs
        WHERE session_id = ?
        ORDER BY created_at DESC
        """,
        (session["id"],),
    ).fetchall()
    return {
        "session": {
            "id": session["id"],
            "status": session["status"],
            "intent": json.loads(session["intent_json"]),
            "context": json.loads(session["context_json"]),
            "plan_preview": json.loads(session["plan_preview_json"]) if session["plan_preview_json"] else None,
            "missing_slot": session["missing_slot"],
            "created_at": session["created_at"],
            "updated_at": session["updated_at"],
            "confirmed_at": session["confirmed_at"],
        },
        "messages": [
            {
                **dict(message),
                "payload": json.loads(message["payload_json"]) if message["payload_json"] else None,
            }
            for message in messages
        ],
        "agent_runs": [dict(run) for run in agent_runs],
        "learning_plan": get_learning_plan(conn, learner_id),
        "intake": get_intake_assessment(conn, learner_id),
    }


def ensure_learning_plan(conn: DbConnection, learner_id: str) -> None:
    get_user(conn, learner_id)
    assessment = conn.execute("SELECT * FROM intake_assessments WHERE learner_id = ?", (learner_id,)).fetchone()
    now = now_iso()
    if assessment is None:
        conn.execute(
            """
            INSERT INTO intake_assessments (
              id, learner_id, target_role, weekly_hours, programming_level, prompt_level,
              rag_level, tool_use_level, deployment_level, career_goal, constraints,
              created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(learner_id) DO NOTHING
            """,
            (
                new_id(),
                learner_id,
                "AI Agent Builder",
                8,
                2,
                3,
                1,
                1,
                1,
                "完成可用于求职和接单展示的 AI Agent 项目作品集。",
                "需要从 AI 使用者过渡到能独立交付项目的 Builder。",
                now,
                now,
            ),
        )
    plan = conn.execute("SELECT id FROM learning_plans WHERE learner_id = ?", (learner_id,)).fetchone()
    if plan is None:
        regenerate_learning_plan(conn, learner_id)


def regenerate_learning_plan(conn: DbConnection, learner_id: str) -> None:
    assessment = conn.execute("SELECT * FROM intake_assessments WHERE learner_id = ?", (learner_id,)).fetchone()
    if assessment is None:
        raise ValueError("Intake assessment not found")
    plan = build_learning_plan(dict(assessment))
    now = now_iso()
    existing = conn.execute("SELECT id FROM learning_plans WHERE learner_id = ?", (learner_id,)).fetchone()
    if existing:
        conn.execute(
            """
            UPDATE learning_plans
            SET target_role = ?, current_level = ?, estimated_weeks = ?, summary = ?,
                plan_json = ?, updated_at = ?
            WHERE learner_id = ?
            """,
            (
                plan["target_role"],
                plan["current_level"],
                plan["estimated_weeks"],
                plan["summary"],
                json.dumps(plan),
                now,
                learner_id,
            ),
        )
    else:
        conn.execute(
            """
            INSERT INTO learning_plans (
              id, learner_id, target_role, current_level, estimated_weeks,
              summary, plan_json, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(learner_id) DO UPDATE SET
              target_role = excluded.target_role,
              current_level = excluded.current_level,
              estimated_weeks = excluded.estimated_weeks,
              summary = excluded.summary,
              plan_json = excluded.plan_json,
              updated_at = excluded.updated_at
            """,
            (
                new_id(),
                learner_id,
                plan["target_role"],
                plan["current_level"],
                plan["estimated_weeks"],
                plan["summary"],
                json.dumps(plan),
                now,
                now,
            ),
        )


def get_learning_plan(conn: DbConnection, learner_id: str) -> dict[str, Any]:
    ensure_learning_plan(conn, learner_id)
    row = conn.execute("SELECT * FROM learning_plans WHERE learner_id = ?", (learner_id,)).fetchone()
    if row is None:
        raise ValueError("Learning plan not found")
    data = json.loads(row["plan_json"])
    data.update(
        {
            "id": row["id"],
            "target_role": row["target_role"],
            "current_level": row["current_level"],
            "estimated_weeks": row["estimated_weeks"],
            "summary": row["summary"],
            "updated_at": row["updated_at"],
        }
    )
    return data


def build_learning_plan(assessment: dict[str, Any]) -> dict[str, Any]:
    foundation = min(
        int(assessment["programming_level"]),
        int(assessment["prompt_level"]),
        int(assessment["rag_level"]),
        int(assessment["tool_use_level"]),
        int(assessment["deployment_level"]),
    )
    current_level = "入门起步" if foundation <= 1 else "训练中 Builder" if foundation <= 3 else "项目就绪"
    weekly_hours = max(4, int(assessment["weekly_hours"]))
    estimated_weeks = 8 if weekly_hours >= 8 else 10
    blockers = []
    if int(assessment["programming_level"]) <= 2:
        blockers.append("Python / API / GitHub 基础")
    if int(assessment["rag_level"]) <= 2:
        blockers.append("RAG 检索与评测")
    if int(assessment["tool_use_level"]) <= 2:
        blockers.append("工具调用与工作流自动化")
    if int(assessment["deployment_level"]) <= 2:
        blockers.append("部署与生产交付")
    weeks = [
        {
            "week": 1,
            "focus": "Builder 基础与结构化 Prompt",
            "outcome": "提交 Prompt + Workflow Agent 初版，能稳定输出结构化结果。",
            "courses": ["prompt_structured_output", "python_api_github_foundation"],
        },
        {
            "week": 2,
            "focus": "Workflow 设计与基础评测",
            "outcome": "补齐确定性步骤、测试样例和评测记录。",
            "courses": ["workflow_design", "basic_eval_trace"],
        },
        {
            "week": 3,
            "focus": "RAG 基础",
            "outcome": "完成文档解析、切分、Embedding 和检索基线。",
            "courses": ["rag_fundamentals", "chunking_embedding_vector_db"],
        },
        {
            "week": 4,
            "focus": "RAG 质量与证据",
            "outcome": "提升检索质量、引用可信度，并提交 RAG 评测报告。",
            "courses": ["retrieval_eval", "rag_prompt_grounding"],
        },
        {
            "week": 5,
            "focus": "Tool Use 与业务自动化",
            "outcome": "构建一个带审批和重试逻辑的工具调用 Agent。",
            "courses": ["function_calling_tool_use", "error_handling_hitl"],
        },
        {
            "week": 6,
            "focus": "部署与可观测性",
            "outcome": "部署一个项目，并补齐日志、环境变量和交付 README。",
            "courses": ["deployment_basics", "trace_logging_cost_control"],
        },
        {
            "week": 7,
            "focus": "作品集强化",
            "outcome": "准备 Demo、架构图、评测报告和面试讲解稿。",
            "courses": ["technical_writing_for_ai_projects", "portfolio_interview_story"],
        },
        {
            "week": 8,
            "focus": "最终评审与 Skill Passport",
            "outcome": "通过项目评审，生成 Skill Passport，并关闭关键能力短板。",
            "courses": ["skill_passport_readiness"],
        },
    ]
    return {
        "target_role": assessment["target_role"],
        "current_level": current_level,
        "estimated_weeks": estimated_weeks,
        "summary": f"{assessment['target_role']} 路线重点补齐：{', '.join(blockers[:3]) if blockers else '作品集交付能力'}。",
        "blockers": blockers,
        "weekly_hours": weekly_hours,
        "weeks": weeks[:estimated_weeks],
    }


def get_skill_map(conn: DbConnection, learner_id: str) -> dict[str, Any]:
    user = get_user(conn, learner_id)
    target_job = None
    if user["selected_target_job_id"]:
        target_job = conn.execute(
            "SELECT slug, title FROM target_jobs WHERE id = ?", (user["selected_target_job_id"],)
        ).fetchone()

    rows = conn.execute(
        """
        SELECT
          sn.id,
          sn.slug,
          sn.name,
          COALESCE(jsr.required_level, 70) AS required_level,
          COALESCE(lss.score, 0) AS current_score,
          COALESCE(lss.confidence, 0) AS confidence,
          COALESCE(lss.evidence_count, 0) AS evidence_count
        FROM skill_nodes sn
        LEFT JOIN job_skill_requirements jsr
          ON jsr.skill_node_id = sn.id
          AND jsr.target_job_id = ?
        LEFT JOIN learner_skill_scores lss
          ON lss.skill_node_id = sn.id
          AND lss.learner_id = ?
        ORDER BY sn.name
        """,
        (user["selected_target_job_id"], learner_id),
    ).fetchall()
    return {
        "target_job": dict(target_job) if target_job else None,
        "skills": [dict(row) for row in rows],
    }


def list_projects(conn: DbConnection, learner_id: str) -> list[dict[str, Any]]:
    ensure_learner_projects(conn, learner_id)
    rows = conn.execute(
        """
        SELECT
          lp.id AS learner_project_id,
          pt.slug AS project_template_slug,
          pt.title,
          pt.description,
          pt.level,
          lp.status
        FROM learner_projects lp
        JOIN project_templates pt ON pt.id = lp.project_template_id
        WHERE lp.learner_id = ?
        ORDER BY pt.level, lp.created_at
        """,
        (learner_id,),
    ).fetchall()
    return [dict(row) for row in rows]


def ensure_learner_projects(conn: DbConnection, learner_id: str) -> None:
    projects = conn.execute(
        """
        SELECT id FROM project_templates
        WHERE is_active = 1
        ORDER BY level, created_at
        """
    ).fetchall()
    now = now_iso()
    for project in projects:
        exists = conn.execute(
            "SELECT id FROM learner_projects WHERE learner_id = ? AND project_template_id = ?",
            (learner_id, project["id"]),
        ).fetchone()
        if exists:
            continue
        conn.execute(
            """
            INSERT INTO learner_projects (id, learner_id, project_template_id, status, started_at, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (new_id(), learner_id, project["id"], "in_progress", now, now),
        )


def get_project(conn: DbConnection, learner_project_id: str, learner_id: str) -> dict[str, Any]:
    project = conn.execute(
        """
        SELECT
          lp.id,
          lp.status,
          pt.slug AS project_template_slug,
          pt.title,
          pt.description
        FROM learner_projects lp
        JOIN project_templates pt ON pt.id = lp.project_template_id
        WHERE lp.id = ? AND lp.learner_id = ?
        """,
        (learner_project_id, learner_id),
    ).fetchone()
    if project is None:
        raise ValueError("Project not found")
    tasks = conn.execute(
        """
        SELECT t.id, t.slug, t.title, t.description, t.required_submission_types
        FROM tasks t
        JOIN learner_projects lp ON lp.project_template_id = t.project_template_id
        WHERE lp.id = ?
        ORDER BY t.sort_order
        """,
        (learner_project_id,),
    ).fetchall()
    task_items = []
    for row in tasks:
        courses = get_task_courses(conn, row["id"], learner_id)
        task_items.append(
            {
                **dict(row),
                "required_submission_types": json.loads(row["required_submission_types"]),
                "recommended_courses": courses,
            }
        )
    project_data = {
        **dict(project),
        "tasks": task_items,
        "coach_tasks": list_active_coach_tasks(conn, learner_id, learner_project_id),
        "latest_submission": get_latest_project_submission(conn, learner_id, learner_project_id),
    }
    active_project = {
        "id": project_data["id"],
        "slug": project_data["project_template_slug"],
        "title": project_data["title"],
        "description": project_data["description"],
        "status": project_data["status"],
        "workspace_href": f"/lab/{project_data['id']}",
        "tasks": [
            {
                "id": task["id"],
                "slug": task["slug"],
                "title": task["title"],
                "description": task["description"],
                "required_submission_types": task["required_submission_types"],
                "courses": [
                    {
                        "id": course["id"],
                        "title": course["title"],
                        "category": course["category"],
                        "estimated_minutes": course["estimated_minutes"],
                        "href": f"/learn/{course['id']}",
                        "reason": course.get("reason") or course.get("recommendation_reason"),
                    }
                    for course in task["recommended_courses"]
                ],
            }
            for task in task_items
        ],
        "coach_tasks": project_data["coach_tasks"],
        "latest_submission": project_data["latest_submission"],
    }
    course_items = [
        course
        for task in active_project["tasks"]
        for course in task["courses"]
    ]
    quality_gate = build_command_center_quality_gate(active_project)
    project_data["agent_queue"] = build_agent_command_queue(
        conn,
        learner_id,
        active_project=active_project,
        course_items=course_items,
        quality_gate=quality_gate,
        fallback_action={"type": "project_lab", "label": "继续项目任务", "href": active_project["workspace_href"]},
    )
    return project_data


def list_active_coach_tasks(
    conn: DbConnection,
    learner_id: str,
    learner_project_id: str | None = None,
) -> list[dict[str, Any]]:
    if learner_project_id:
        rows = conn.execute(
            """
            SELECT *
            FROM coach_tasks
            WHERE learner_id = ? AND learner_project_id = ? AND status = 'open'
            ORDER BY priority, created_at DESC
            LIMIT 5
            """,
            (learner_id, learner_project_id),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT *
            FROM coach_tasks
            WHERE learner_id = ? AND status = 'open'
            ORDER BY priority, created_at DESC
            LIMIT 5
            """,
            (learner_id,),
        ).fetchall()
    return [
        {
            **dict(row),
            "actions": json.loads(row["action_json"]),
        }
        for row in rows
    ]


def get_latest_project_submission(
    conn: DbConnection,
    learner_id: str,
    learner_project_id: str,
) -> dict[str, Any] | None:
    row = conn.execute(
        """
        SELECT id, status, github_repo_url, demo_url, readme_url, evaluation_report_url,
               reflection_text, latest_review_id, created_at, updated_at
        FROM submissions
        WHERE learner_id = ? AND learner_project_id = ?
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (learner_id, learner_project_id),
    ).fetchone()
    if row is None:
        return None
    data = dict(row)
    if data.get("latest_review_id"):
        data["latest_review"] = get_review(conn, data["latest_review_id"], learner_id)
    else:
        data["latest_review"] = None
    return data


def get_project_tutor(conn: DbConnection, learner_project_id: str, learner_id: str) -> dict[str, Any]:
    project = get_project(conn, learner_project_id, learner_id)
    task_id = project["tasks"][0]["id"] if project["tasks"] else None
    session = ensure_tutor_session(conn, learner_project_id, learner_id, task_id)
    return serialize_tutor_session(conn, session)


def send_tutor_message(
    conn: DbConnection,
    learner_project_id: str,
    learner_id: str,
    message: str,
) -> dict[str, Any]:
    clean_message = message.strip()
    if not clean_message:
        raise ValueError("Tutor message cannot be empty")

    project = get_project(conn, learner_project_id, learner_id)
    task = project["tasks"][0] if project["tasks"] else None
    session = ensure_tutor_session(conn, learner_project_id, learner_id, task["id"] if task else None)
    now = now_iso()
    conn.execute(
        """
        INSERT INTO tutor_messages (
          id, tutor_session_id, role, content, hint_level, learning_signal, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (new_id(), session["id"], "learner", clean_message, None, None, now),
    )

    context = {
        "project_title": project["title"],
        "project_slug": project["project_template_slug"],
        "task_title": task["title"] if task else None,
        "current_ai_dependency_score": session["ai_dependency_score"],
        "latest_submission": project.get("latest_submission"),
        "active_coach_tasks": project.get("coach_tasks", []),
    }
    decision, trace_meta = execute_tutor_agent(clean_message, context)
    next_score = min(100, int(session["ai_dependency_score"]) + decision.ai_dependency_delta)
    conn.execute(
        """
        INSERT INTO tutor_messages (
          id, tutor_session_id, role, content, hint_level, learning_signal, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            new_id(),
            session["id"],
            "tutor",
            decision.content,
            decision.hint_level,
            decision.learning_signal,
            now_iso(),
        ),
    )
    conn.execute(
        """
        UPDATE tutor_sessions
        SET ai_dependency_score = ?, updated_at = ?
        WHERE id = ?
        """,
        (next_score, now_iso(), session["id"]),
    )
    conn.execute(
        """
        INSERT INTO tutor_agent_runs (
          id, tutor_session_id, agent_name, input_json, output_json, status, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            new_id(),
            session["id"],
            "ProjectTutorAgent",
            json.dumps({"message": clean_message, "context": context}),
            json.dumps(
                {
                    **decision.as_dict(),
                    **({"fallback_reason": trace_meta["fallback_reason"]} if trace_meta.get("fallback_reason") else {}),
                }
            ),
            "succeeded",
            now_iso(),
        ),
    )
    trace_output = decision.as_dict()
    if trace_meta.get("fallback_reason"):
        trace_output["fallback_reason"] = trace_meta["fallback_reason"]
    tutor_agent_run_id = record_agent_run(
        conn,
        learner_id=learner_id,
        agent_name="ProjectTutorAgent",
        runtime=trace_meta["runtime"],
        provider=trace_meta["provider"],
        model=trace_meta["model"],
        input_data={"message": clean_message, "context": context},
        output_data=trace_output,
        status="succeeded",
        latency_ms=trace_meta["latency_ms"],
        parent_type="tutor_session",
        parent_id=session["id"],
        tool_names=["guardrail", "hint_policy", "ai_dependency_scorer"],
        mode=trace_meta["runtime"],
        prompt_version="tutor-v1",
    )
    record_agent_trace(
        conn,
        agent_run_id=tutor_agent_run_id,
        learner_id=learner_id,
        agent_name="ProjectTutorAgent",
        runtime=trace_meta["runtime"],
        provider=trace_meta["provider"],
        model=trace_meta["model"],
        input_data={"message": clean_message, "context": context},
        output_data=trace_output,
        status="succeeded",
        latency_ms=trace_meta["latency_ms"],
        parent_type="tutor_session",
        parent_id=session["id"],
        tool_names=["guardrail", "hint_policy", "ai_dependency_scorer"],
    )
    return serialize_tutor_session(conn, require_tutor_session(conn, session["id"], learner_id))


def ensure_tutor_session(
    conn: DbConnection,
    learner_project_id: str,
    learner_id: str,
    task_id: str | None,
) -> Any:
    row = conn.execute(
        """
        SELECT *
        FROM tutor_sessions
        WHERE learner_project_id = ? AND learner_id = ?
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (learner_project_id, learner_id),
    ).fetchone()
    if row is not None:
        return row

    now = now_iso()
    session_id = new_id()
    conn.execute(
        """
        INSERT INTO tutor_sessions (
          id, learner_id, learner_project_id, task_id, status, ai_dependency_score,
          created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (session_id, learner_id, learner_project_id, task_id, "active", 0, now, now),
    )
    conn.execute(
        """
        INSERT INTO tutor_messages (
          id, tutor_session_id, role, content, hint_level, learning_signal, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            new_id(),
            session_id,
            "tutor",
            "我是项目内 Agent Tutor。我的目标是帮你拆解、提示、定位问题和检查方案，但不会替你完成可直接提交的成品。",
            1,
            "orientation",
            now,
        ),
    )
    return require_tutor_session(conn, session_id, learner_id)


def require_tutor_session(conn: DbConnection, session_id: str, learner_id: str) -> Any:
    row = conn.execute(
        "SELECT * FROM tutor_sessions WHERE id = ? AND learner_id = ?",
        (session_id, learner_id),
    ).fetchone()
    if row is None:
        raise ValueError("Tutor session not found")
    return row


def serialize_tutor_session(conn: DbConnection, session: Any) -> dict[str, Any]:
    messages = conn.execute(
        """
        SELECT id, role, content, hint_level, learning_signal, created_at
        FROM tutor_messages
        WHERE tutor_session_id = ?
        ORDER BY created_at
        """,
        (session["id"],),
    ).fetchall()
    runs = conn.execute(
        """
        SELECT id, agent_name, status, created_at
        FROM tutor_agent_runs
        WHERE tutor_session_id = ?
        ORDER BY created_at DESC
        """,
        (session["id"],),
    ).fetchall()
    score = int(session["ai_dependency_score"])
    if score >= 70:
        rating = "high"
    elif score >= 35:
        rating = "medium"
    else:
        rating = "low"
    return {
        "session": {
            "id": session["id"],
            "learner_project_id": session["learner_project_id"],
            "task_id": session["task_id"],
            "status": session["status"],
            "ai_dependency_score": score,
            "ai_dependency_rating": rating,
            "created_at": session["created_at"],
            "updated_at": session["updated_at"],
        },
        "messages": [dict(message) for message in messages],
        "agent_runs": [dict(run) for run in runs],
    }


def get_ai_dependency_summary(conn: DbConnection, learner_id: str) -> dict[str, Any]:
    rows = conn.execute(
        """
        SELECT ai_dependency_score
        FROM tutor_sessions
        WHERE learner_id = ?
        """,
        (learner_id,),
    ).fetchall()
    if not rows:
        return {"average_score": 0, "max_score": 0, "session_count": 0, "rating": "low"}
    scores = [int(row["ai_dependency_score"]) for row in rows]
    average = round(sum(scores) / len(scores))
    max_score = max(scores)
    rating = "high" if average >= 70 or max_score >= 85 else "medium" if average >= 35 else "low"
    return {
        "average_score": average,
        "max_score": max_score,
        "session_count": len(scores),
        "rating": rating,
    }


def get_task_courses(conn: DbConnection, task_id: str, learner_id: str) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT
          cm.id,
          cm.slug,
          cm.title,
          cm.description,
          cm.category,
          cm.difficulty,
          cm.estimated_minutes,
          (
            SELECT COUNT(*) FROM course_lessons cl WHERE cl.course_module_id = cm.id
          ) AS lesson_count,
          tcm.reason,
          COALESCE(cp.status, 'not_started') AS status
        FROM task_course_modules tcm
        JOIN course_modules cm ON cm.id = tcm.course_module_id
        LEFT JOIN course_progress cp
          ON cp.course_module_id = cm.id
          AND cp.learner_id = ?
        WHERE tcm.task_id = ?
        ORDER BY tcm.sort_order, cm.sort_order
        """,
        (learner_id, task_id),
    ).fetchall()
    return [dict(row) for row in rows]


def get_adaptive_courses(conn: DbConnection, learner_id: str) -> dict[str, Any]:
    ensure_learner_projects(conn, learner_id)
    skill_map = get_skill_map(conn, learner_id)
    gaps_by_slug = {
        skill["slug"]: max(0, int(skill["required_level"]) - int(skill["current_score"]))
        for skill in skill_map["skills"]
    }
    rows = conn.execute(
        """
        SELECT
          cm.id,
          cm.slug,
          cm.title,
          cm.description,
          cm.category,
          cm.difficulty,
          cm.estimated_minutes,
          (
            SELECT COUNT(*) FROM course_lessons cl WHERE cl.course_module_id = cm.id
          ) AS lesson_count,
          sn.slug AS skill_slug,
          sn.name AS skill_name,
          COALESCE(cp.status, 'not_started') AS status,
          MIN(tcm.reason) AS project_reason
        FROM course_modules cm
        LEFT JOIN skill_nodes sn ON sn.id = cm.skill_node_id
        LEFT JOIN course_progress cp
          ON cp.course_module_id = cm.id
          AND cp.learner_id = ?
        LEFT JOIN task_course_modules tcm ON tcm.course_module_id = cm.id
        GROUP BY
          cm.id, cm.slug, cm.title, cm.description, cm.category, cm.difficulty,
          cm.estimated_minutes, sn.slug, sn.name, cp.status
        ORDER BY cm.sort_order
        """,
        (learner_id,),
    ).fetchall()
    courses = []
    for row in rows:
        item = dict(row)
        skill_slug = item.get("skill_slug")
        gap = gaps_by_slug.get(skill_slug, 0) if skill_slug else 0
        item["priority_score"] = gap + (20 if item["status"] == "not_started" else 0)
        item["recommendation_reason"] = (
            f"能力差距：{item['skill_name']} 距离目标还差 {gap} 分。"
            if gap > 0 and item.get("skill_name")
            else item.get("project_reason") or "适合当前项目路径。"
        )
        courses.append(item)
    courses.sort(key=lambda item: (-int(item["priority_score"]), item["category"], item["title"]))
    return {"courses": courses}


def list_course_library(conn: DbConnection, learner_id: str) -> dict[str, Any]:
    data = get_adaptive_courses(conn, learner_id)
    return {
        "storage": {
            "module_table": "course_modules",
            "lesson_table": "course_lessons",
            "binding_table": "task_course_modules",
            "progress_table": "course_progress",
        },
        "courses": data["courses"],
    }


def get_course_detail(conn: DbConnection, course_id: str, learner_id: str) -> dict[str, Any]:
    course = conn.execute(
        """
        SELECT
          cm.*,
          sn.slug AS skill_slug,
          sn.name AS skill_name,
          COALESCE(cp.status, 'not_started') AS status
        FROM course_modules cm
        LEFT JOIN skill_nodes sn ON sn.id = cm.skill_node_id
        LEFT JOIN course_progress cp
          ON cp.course_module_id = cm.id
          AND cp.learner_id = ?
        WHERE cm.id = ?
        """,
        (learner_id, course_id),
    ).fetchone()
    if course is None:
        raise ValueError("课程不存在")
    lessons = conn.execute(
        """
        SELECT id, title, content_type, content_ref, body, sort_order
        FROM course_lessons
        WHERE course_module_id = ?
        ORDER BY sort_order
        """,
        (course_id,),
    ).fetchall()
    bindings = conn.execute(
        """
        SELECT
          t.title AS task_title,
          pt.title AS project_title,
          tcm.reason
        FROM task_course_modules tcm
        JOIN tasks t ON t.id = tcm.task_id
        JOIN project_templates pt ON pt.id = t.project_template_id
        WHERE tcm.course_module_id = ?
        ORDER BY pt.level, tcm.sort_order
        """,
        (course_id,),
    ).fetchall()
    exercise = ensure_course_exercise(conn, course_id)
    attempts = conn.execute(
        """
        SELECT id, answer, score, feedback, next_action, status, created_at
        FROM course_exercise_attempts
        WHERE learner_id = ? AND course_exercise_id = ?
        ORDER BY created_at DESC
        LIMIT 3
        """,
        (learner_id, exercise["id"]),
    ).fetchall()
    return {
        **dict(course),
        "lessons": [dict(row) for row in lessons],
        "project_bindings": [dict(row) for row in bindings],
        "exercise": exercise,
        "exercise_attempts": [dict(row) for row in attempts],
        "storage": {
            "module_ref": f"db://course_modules/{course_id}",
            "lesson_refs": [row["content_ref"] for row in lessons],
        },
    }


def get_course_workbench(conn: DbConnection, course_id: str, learner_id: str) -> dict[str, Any]:
    course = get_course_detail(conn, course_id, learner_id)
    binding = get_primary_course_binding(conn, course_id, learner_id)
    command_center = get_agent_command_center(
        conn,
        learner_id,
        binding["learner_project_id"] if binding else None,
    )
    project_context = build_course_project_context(binding, command_center)
    latest_attempt = course["exercise_attempts"][0] if course["exercise_attempts"] else None
    project_href = project_context["project"]["workspace_href"] if project_context["project"] else command_center["handoffs"]["project_lab"]["href"]

    return {
        "contract_version": "course_workbench.v1",
        "agent": {
            "name": "MicroExerciseCoach",
            "mode": "rule",
            "status": "ready",
            "policy": "课程不是内容消费，而是项目任务的最小技能补给。MicroExerciseCoach 会检查学员是否能把知识转成提交物动作。",
            "tools": ["keyword_checker", "rubric_feedback", "progress_updater", "project_context_linker"],
        },
        "course": {
            "id": course["id"],
            "slug": course["slug"],
            "title": course["title"],
            "description": course["description"],
            "category": course["category"],
            "difficulty": course["difficulty"],
            "estimated_minutes": course["estimated_minutes"],
            "status": course["status"],
            "skill_name": course.get("skill_name"),
        },
        "mission": {
            "title": f"把《{course['title']}》应用到当前项目任务",
            "reason": binding["reason"] if binding else "这门课匹配当前能力差距，需要通过微练习证明你能应用。",
            "success_evidence": "微练习通过后，课程进度写入 course_progress，并在 Agent Trace 中留下 MicroExerciseCoach 评估记录。",
            "next_best_action": {
                "label": "完成交互式微练习",
                "href": f"/learn/{course_id}#micro-exercise",
            },
        },
        "project_context": project_context,
        "lessons": course["lessons"],
        "exercise": {
            **course["exercise"],
            "pass_standard": {
                "minimum_score": 70,
                "required_keywords": course["exercise"]["expected_keywords"],
                "outcome": "把答案写入项目 README、评测报告或架构说明，再回到 Project Lab 提交质量门。",
            },
        },
        "latest_attempt": latest_attempt,
        "agent_queue": command_center["agent_queue"],
        "storage": course["storage"],
        "handoffs": {
            "command_center": {"label": "回到 Agent 指挥中心", "href": "/coach"},
            "project_lab": {"label": "回到 Project Lab", "href": project_href},
            "quality_gate": command_center["handoffs"]["review"],
            "next_course": get_next_course_handoff(command_center, course_id),
        },
        "data_sources": {
            "course": "course_modules + course_lessons",
            "binding": "task_course_modules + tasks + learner_projects",
            "exercise": "course_exercises + course_exercise_attempts",
            "progress": "course_progress",
            "agent_trace": "agent_traces",
        },
    }


def get_primary_course_binding(conn: DbConnection, course_id: str, learner_id: str) -> dict[str, Any] | None:
    row = conn.execute(
        """
        SELECT
          lp.id AS learner_project_id,
          lp.status AS learner_project_status,
          pt.slug AS project_slug,
          pt.title AS project_title,
          pt.description AS project_description,
          t.id AS task_id,
          t.slug AS task_slug,
          t.title AS task_title,
          t.description AS task_description,
          t.required_submission_types,
          tcm.reason
        FROM task_course_modules tcm
        JOIN tasks t ON t.id = tcm.task_id
        JOIN project_templates pt ON pt.id = t.project_template_id
        JOIN learner_projects lp
          ON lp.project_template_id = pt.id
          AND lp.learner_id = ?
        WHERE tcm.course_module_id = ?
        ORDER BY pt.level, tcm.sort_order
        LIMIT 1
        """,
        (learner_id, course_id),
    ).fetchone()
    if row is None:
        return None
    data = dict(row)
    data["required_submission_types"] = json.loads(data["required_submission_types"])
    return data


def build_course_project_context(
    binding: dict[str, Any] | None,
    command_center: dict[str, Any],
) -> dict[str, Any]:
    if binding is None:
        return {
            "project": command_center["active_project"],
            "task": command_center["active_project"]["tasks"][0] if command_center["active_project"] else None,
            "why_now": "当前课程来自自适应课程队列，用来补齐能力差距。",
        }
    return {
        "project": {
            "id": binding["learner_project_id"],
            "slug": binding["project_slug"],
            "title": binding["project_title"],
            "description": binding["project_description"],
            "status": binding["learner_project_status"],
            "workspace_href": f"/lab/{binding['learner_project_id']}",
        },
        "task": {
            "id": binding["task_id"],
            "slug": binding["task_slug"],
            "title": binding["task_title"],
            "description": binding["task_description"],
            "required_submission_types": binding["required_submission_types"],
        },
        "why_now": binding["reason"],
    }


def get_next_course_handoff(command_center: dict[str, Any], current_course_id: str) -> dict[str, Any]:
    next_course = next(
        (course for course in command_center["course_queue"]["items"] if course["id"] != current_course_id),
        None,
    )
    if next_course:
        return {"label": next_course["title"], "href": next_course["href"]}
    return {"label": "查看全部课程", "href": "/courses"}


def ensure_course_exercise(conn: DbConnection, course_id: str) -> dict[str, Any]:
    row = conn.execute(
        "SELECT * FROM course_exercises WHERE course_module_id = ? ORDER BY created_at LIMIT 1",
        (course_id,),
    ).fetchone()
    if row:
        return {**dict(row), "expected_keywords": json.loads(row["expected_keywords"]), "rubric": json.loads(row["rubric_json"])}
    course = conn.execute("SELECT title FROM course_modules WHERE id = ?", (course_id,)).fetchone()
    if course is None:
        raise ValueError("Course module not found")
    exercise_id = new_id()
    now = now_iso()
    conn.execute(
        """
        INSERT INTO course_exercises (id, course_module_id, prompt, expected_keywords, rubric_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            exercise_id,
            course_id,
            f"请说明你会如何把《{course['title']}》应用到当前项目，并写出验证方法。",
            json.dumps(["实现", "验证", "失败", "调整"]),
            json.dumps({"implementation": 35, "validation": 35, "debug_strategy": 30}),
            now,
        ),
    )
    return {
        "id": exercise_id,
        "course_module_id": course_id,
        "prompt": f"请说明你会如何把《{course['title']}》应用到当前项目，并写出验证方法。",
        "expected_keywords": ["实现", "验证", "失败", "调整"],
        "rubric": {"implementation": 35, "validation": 35, "debug_strategy": 30},
        "created_at": now,
    }


def submit_course_exercise(
    conn: DbConnection,
    learner_id: str,
    course_module_id: str,
    answer: str,
) -> dict[str, Any]:
    clean_answer = answer.strip()
    if len(clean_answer) < 20:
        raise ValueError("练习答案太短，至少说明一个动作和一个验证方法")
    exercise = ensure_course_exercise(conn, course_module_id)
    keywords = exercise["expected_keywords"]
    hit_count = sum(1 for keyword in keywords if keyword.lower() in clean_answer.lower())
    length_bonus = 20 if len(clean_answer) >= 80 else 10
    score = min(100, hit_count * 20 + length_bonus)
    passed = score >= 70
    feedback = (
        "你的答案已经包含实现动作、验证方法和失败调整思路，可以进入项目提交物。"
        if passed
        else "答案还不够可执行。请补充：具体实现动作、如何验证、失败后如何调整。"
    )
    next_action = "把这段内容写入项目 README 或 evaluation report。" if passed else "重写练习答案后再提交。"
    now = now_iso()
    attempt_id = new_id()
    conn.execute(
        """
        INSERT INTO course_exercise_attempts (
          id, learner_id, course_exercise_id, answer, score, feedback, next_action, status, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            attempt_id,
            learner_id,
            exercise["id"],
            clean_answer,
            score,
            feedback,
            next_action,
            "passed" if passed else "needs_revision",
            now,
        ),
    )
    update_course_progress(conn, learner_id, course_module_id, "completed" if passed else "in_progress")
    record_agent_trace(
        conn,
        agent_run_id=record_agent_run(
            conn,
            learner_id=learner_id,
            agent_name="MicroExerciseCoach",
            runtime="rule",
            provider="agentlab",
            model=None,
            input_data={"course_module_id": course_module_id, "answer": clean_answer},
            output_data={"score": score, "feedback": feedback, "next_action": next_action, "status": "passed" if passed else "needs_revision"},
            status="succeeded",
            latency_ms=None,
            parent_type="course_exercise",
            parent_id=exercise["id"],
            tool_names=["keyword_checker", "rubric_feedback", "progress_updater"],
            mode="rule",
            prompt_version="micro-exercise-v1",
        ),
        learner_id=learner_id,
        agent_name="MicroExerciseCoach",
        runtime="rule",
        provider="agentlab",
        model=None,
        input_data={"course_module_id": course_module_id, "answer": clean_answer},
        output_data={"score": score, "feedback": feedback, "next_action": next_action, "status": "passed" if passed else "needs_revision"},
        status="succeeded",
        latency_ms=None,
        parent_type="course_exercise",
        parent_id=exercise["id"],
        tool_names=["keyword_checker", "rubric_feedback", "progress_updater"],
    )
    return {
        "id": attempt_id,
        "course_module_id": course_module_id,
        "course_exercise_id": exercise["id"],
        "score": score,
        "feedback": feedback,
        "next_action": next_action,
        "status": "passed" if passed else "needs_revision",
        "created_at": now,
    }


def update_course_progress(
    conn: DbConnection,
    learner_id: str,
    course_module_id: str,
    status: str,
) -> dict[str, Any]:
    if status not in {"not_started", "in_progress", "completed"}:
        raise ValueError("status must be not_started, in_progress, or completed")
    course = conn.execute("SELECT id FROM course_modules WHERE id = ?", (course_module_id,)).fetchone()
    if course is None:
        raise ValueError("Course module not found")
    now = now_iso()
    completed_at = now if status == "completed" else None
    existing = conn.execute(
        "SELECT id FROM course_progress WHERE learner_id = ? AND course_module_id = ?",
        (learner_id, course_module_id),
    ).fetchone()
    if existing:
        conn.execute(
            """
            UPDATE course_progress
            SET status = ?, completed_at = ?, updated_at = ?
            WHERE id = ?
            """,
            (status, completed_at, now, existing["id"]),
        )
    else:
        conn.execute(
            """
            INSERT INTO course_progress (id, learner_id, course_module_id, status, completed_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (new_id(), learner_id, course_module_id, status, completed_at, now),
        )
    return {"course_module_id": course_module_id, "status": status, "updated_at": now}


def create_submission(conn: DbConnection, payload: dict[str, Any], learner_id: str) -> dict[str, Any]:
    user = get_user(conn, learner_id)
    learner_project = conn.execute(
        "SELECT * FROM learner_projects WHERE id = ? AND learner_id = ?",
        (payload["learner_project_id"], user["id"]),
    ).fetchone()
    if learner_project is None:
        raise ValueError("Learner project not found")
    now = now_iso()
    submission_id = new_id()
    conn.execute(
        """
        INSERT INTO submissions (
          id, learner_id, learner_project_id, task_id, status, github_repo_url,
          demo_url, readme_url, architecture_doc_url, evaluation_report_url,
          source_repo_path, sandbox_command, reflection_text, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            submission_id,
            user["id"],
            payload["learner_project_id"],
            payload["task_id"],
            "submitted",
            payload.get("github_repo_url"),
            payload.get("demo_url"),
            payload.get("readme_url"),
            payload.get("architecture_doc_url"),
            payload.get("evaluation_report_url"),
            payload.get("source_repo_path"),
            payload.get("sandbox_command"),
            payload.get("reflection_text"),
            now,
            now,
        ),
    )
    conn.execute("UPDATE learner_projects SET status = ? WHERE id = ?", ("submitted", payload["learner_project_id"]))
    review_job_id = None
    status = "submitted"
    if payload.get("queue_review", True):
        review_job_id = create_review_job(conn, submission_id, payload.get("mode", settings.agent_mode), learner_id)["review_job_id"]
        status = "review_queued"
        conn.execute("UPDATE submissions SET status = ?, updated_at = ? WHERE id = ?", (status, now, submission_id))
    return {"submission_id": submission_id, "status": status, "review_job_id": review_job_id}


def create_review_job(
    conn: DbConnection,
    submission_id: str,
    mode: str = "mock",
    learner_id: str | None = None,
) -> dict[str, Any]:
    if mode not in {"mock", "claude"}:
        raise ValueError("mode must be mock or claude")
    if learner_id:
        submission = conn.execute(
            "SELECT id FROM submissions WHERE id = ? AND learner_id = ?",
            (submission_id, learner_id),
        ).fetchone()
    else:
        submission = conn.execute("SELECT id FROM submissions WHERE id = ?", (submission_id,)).fetchone()
    if submission is None:
        raise ValueError("Submission not found")
    now = now_iso()
    review_job_id = new_id()
    conn.execute(
        """
        INSERT INTO review_jobs (id, submission_id, status, mode, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (review_job_id, submission_id, "queued", mode, now),
    )
    transition_submission(conn, submission_id, "review_queued")
    return {"review_job_id": review_job_id, "status": "queued"}


def get_review_job(conn: DbConnection, review_job_id: str, learner_id: str | None = None) -> dict[str, Any]:
    row = conn.execute("SELECT * FROM review_jobs WHERE id = ?", (review_job_id,)).fetchone()
    if row is None:
        raise ValueError("Review job not found")
    if learner_id:
        get_submission(conn, row["submission_id"], learner_id)
    sandbox_runs = conn.execute(
        "SELECT * FROM sandbox_runs WHERE review_job_id = ? ORDER BY created_at DESC",
        (review_job_id,),
    ).fetchall()
    agent_runs = conn.execute(
        """
        SELECT id, learner_id, agent_name, runtime, provider, model, mode, status,
               latency_ms, cost_usd, parent_type, parent_id, created_at, finished_at
        FROM agent_runs
        WHERE review_job_id = ?
        ORDER BY created_at DESC
        """,
        (review_job_id,),
    ).fetchall()
    return {
        **dict(row),
        "sandbox_runs": [dict(item) for item in sandbox_runs],
        "agent_runs": [dict(item) for item in agent_runs],
    }


def get_review_gate_workbench(conn: DbConnection, review_job_id: str, learner_id: str) -> dict[str, Any]:
    job = get_review_job(conn, review_job_id, learner_id)
    context = get_review_gate_context(conn, review_job_id, learner_id)
    review = get_review(conn, job["review_id"], learner_id) if job.get("review_id") else None
    evidence_items = list_review_gate_evidence(conn, context["submission"]["id"], job.get("review_id"))
    coach_tasks = review["coach_tasks"] if review else []
    sandbox_latest = job["sandbox_runs"][0] if job["sandbox_runs"] else None
    workflow = build_review_gate_workflow(
        job_status=job["status"],
        sandbox_latest=sandbox_latest,
        agent_runs=job["agent_runs"],
        evidence_items=evidence_items,
        coach_tasks=coach_tasks,
    )
    project_href = f"/lab/{context['project']['id']}"
    report_href = f"/report/{job['review_id']}" if job.get("review_id") else f"/gate/{review_job_id}"

    return {
        "contract_version": "review_gate_workbench.v1",
        "agent": {
            "name": "ReviewAgent",
            "mode": job["mode"],
            "status": job["status"],
            "policy": "ReviewAgent 必须先读取 Sandbox 运行结果，再按 Rubric 评审提交物，最后把证据写入 Evidence Store 并生成下一轮修复任务。",
            "tools": ["sandbox_logs", "rubric_scorer", "evidence_extractor", "coach_task_generator"],
        },
        "job": {
            "id": job["id"],
            "status": job["status"],
            "mode": job["mode"],
            "submission_id": job["submission_id"],
            "review_id": job.get("review_id"),
            "attempt_count": job["attempt_count"],
            "last_error": job["last_error"],
            "created_at": job["created_at"],
            "started_at": job["started_at"],
            "finished_at": job["finished_at"],
        },
        "submission": context["submission"],
        "project_context": {
            "project": {
                **context["project"],
                "workspace_href": project_href,
            },
            "task": context["task"],
        },
        "workflow": workflow,
        "sandbox": {
            "status": sandbox_latest["status"] if sandbox_latest else "not_started",
            "latest": sandbox_latest,
            "runs": job["sandbox_runs"],
        },
        "review": review,
        "agent_runs": job["agent_runs"],
        "evidence": {
            "store": "evidence_items",
            "items": evidence_items,
            "count": len(evidence_items),
            "passport_eligible_count": sum(1 for item in evidence_items if item["is_passport_eligible"]),
        },
        "coach_tasks": coach_tasks,
        "handoffs": {
            "command_center": {"label": "回到 Agent 指挥中心", "href": "/coach"},
            "project_lab": {"label": "回到 Project Lab", "href": project_href},
            "report": {"label": "查看质量门报告", "href": report_href},
            "passport": {"label": "生成 Skill Passport", "href": "/passport"},
        },
        "data_sources": {
            "job": "review_jobs",
            "submission": "submissions",
            "sandbox": "sandbox_runs",
            "agent_runs": "agent_runs",
            "review": "reviews + review_scores + review_risk_flags",
            "evidence": "evidence_items + skill_nodes",
            "coach_tasks": "coach_tasks",
        },
    }


def get_review_gate_context(conn: DbConnection, review_job_id: str, learner_id: str) -> dict[str, Any]:
    row = conn.execute(
        """
        SELECT
          rj.id AS review_job_id,
          s.id AS submission_id,
          s.status AS submission_status,
          s.learner_project_id,
          s.task_id,
          s.github_repo_url,
          s.demo_url,
          s.readme_url,
          s.architecture_doc_url,
          s.evaluation_report_url,
          s.source_repo_path,
          s.sandbox_command,
          s.reflection_text,
          s.created_at AS submission_created_at,
          s.updated_at AS submission_updated_at,
          lp.id AS project_id,
          lp.status AS project_status,
          pt.slug AS project_slug,
          pt.title AS project_title,
          pt.description AS project_description,
          t.id AS task_id,
          t.slug AS task_slug,
          t.title AS task_title,
          t.description AS task_description,
          t.required_submission_types
        FROM review_jobs rj
        JOIN submissions s ON s.id = rj.submission_id
        JOIN learner_projects lp ON lp.id = s.learner_project_id
        JOIN project_templates pt ON pt.id = lp.project_template_id
        JOIN tasks t ON t.id = s.task_id
        WHERE rj.id = ? AND s.learner_id = ?
        """,
        (review_job_id, learner_id),
    ).fetchone()
    if row is None:
        raise ValueError("Review job not found")
    return {
        "submission": {
            "id": row["submission_id"],
            "status": row["submission_status"],
            "learner_project_id": row["learner_project_id"],
            "task_id": row["task_id"],
            "github_repo_url": row["github_repo_url"],
            "demo_url": row["demo_url"],
            "readme_url": row["readme_url"],
            "architecture_doc_url": row["architecture_doc_url"],
            "evaluation_report_url": row["evaluation_report_url"],
            "source_repo_path": row["source_repo_path"],
            "sandbox_command": row["sandbox_command"],
            "reflection_text": row["reflection_text"],
            "created_at": row["submission_created_at"],
            "updated_at": row["submission_updated_at"],
        },
        "project": {
            "id": row["project_id"],
            "slug": row["project_slug"],
            "title": row["project_title"],
            "description": row["project_description"],
            "status": row["project_status"],
        },
        "task": {
            "id": row["task_id"],
            "slug": row["task_slug"],
            "title": row["task_title"],
            "description": row["task_description"],
            "required_submission_types": json.loads(row["required_submission_types"]),
        },
    }


def list_review_gate_evidence(conn: DbConnection, submission_id: str, review_id: str | None) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT ei.*, sn.name AS skill, sn.slug AS skill_slug
        FROM evidence_items ei
        JOIN skill_nodes sn ON sn.id = ei.skill_node_id
        WHERE ei.submission_id = ? OR ei.review_id = ?
        ORDER BY ei.created_at DESC
        """,
        (submission_id, review_id),
    ).fetchall()
    return [dict(row) for row in rows]


def build_review_gate_workflow(
    *,
    job_status: str,
    sandbox_latest: dict[str, Any] | None,
    agent_runs: list[dict[str, Any]],
    evidence_items: list[dict[str, Any]],
    coach_tasks: list[dict[str, Any]],
) -> dict[str, Any]:
    sandbox_status = sandbox_latest["status"] if sandbox_latest else "not_started"
    sandbox_done = sandbox_status == "succeeded"
    sandbox_failed = sandbox_status == "failed" or job_status == "failed"
    agent_done = len(agent_runs) > 0
    evidence_done = len(evidence_items) > 0
    next_task_done = len(coach_tasks) > 0

    if job_status == "queued":
        current_step_id = "sandbox"
    elif job_status == "running" and not sandbox_done:
        current_step_id = "sandbox"
    elif job_status == "running" and not agent_done:
        current_step_id = "agent_review"
    elif job_status == "failed":
        current_step_id = "sandbox" if sandbox_failed else "agent_review"
    elif job_status == "succeeded":
        current_step_id = "next_task"
    else:
        current_step_id = "agent_review"

    steps = [
        {
            "id": "sandbox",
            "label": "Sandbox",
            "status": "failed" if sandbox_failed else "done" if sandbox_done else "active",
            "agent": "SandboxRunner",
            "output": "运行提交代码、测试命令并采集 stdout / stderr / exit_code。",
        },
        {
            "id": "agent_review",
            "label": "Agent Review",
            "status": "done" if agent_done else "active" if sandbox_done and job_status != "failed" else "waiting",
            "agent": "ReviewAgent",
            "output": "读取 Sandbox 日志、Rubric、提交物链接，生成评审结论。",
        },
        {
            "id": "evidence",
            "label": "Evidence Store",
            "status": "done" if evidence_done else "active" if agent_done else "waiting",
            "agent": "EvidenceExtractor",
            "output": "把通过评审的能力证据写入 evidence_items 并更新能力图谱。",
        },
        {
            "id": "next_task",
            "label": "下一轮任务",
            "status": "done" if next_task_done else "active" if evidence_done else "waiting",
            "agent": "CoachTaskAgent",
            "output": "根据风险项和低分 Rubric 自动生成下一轮修复任务。",
        },
    ]
    return {"current_step_id": current_step_id, "steps": steps}


def process_next_review_job(conn: DbConnection) -> dict[str, Any] | None:
    job = conn.execute(
        "SELECT * FROM review_jobs WHERE status = 'queued' ORDER BY priority, created_at LIMIT 1"
    ).fetchone()
    if job is None:
        return None
    return process_review_job(conn, job["id"])


def process_review_job(conn: DbConnection, review_job_id: str) -> dict[str, Any]:
    job = conn.execute("SELECT * FROM review_jobs WHERE id = ?", (review_job_id,)).fetchone()
    if job is None:
        raise ValueError("Review job not found")
    now = now_iso()
    try:
        transition_review_job(conn, review_job_id, "running", started_at=now)
        transition_submission(conn, job["submission_id"], "ai_reviewing")
        sandbox_result = run_submission_sandbox(conn, review_job_id, job["submission_id"])
        context = build_review_context(conn, job["submission_id"], sandbox_result)
        review_run = run_review(job["mode"], context)
        result = review_run.result
        finished_at = now_iso()
        submission = conn.execute("SELECT learner_id FROM submissions WHERE id = ?", (job["submission_id"],)).fetchone()
        if submission:
            review_agent_run_id = record_agent_run(
                conn,
                review_job_id=review_job_id,
                learner_id=submission["learner_id"],
                agent_name="ReviewAgent",
                runtime="claude_agent_sdk" if review_run.provider == "anthropic" else "mock",
                provider=review_run.provider,
                model=review_run.model,
                input_data=context,
                output_data=result.model_dump(mode="json"),
                status="succeeded",
                latency_ms=review_run.latency_ms,
                parent_type="review_job",
                parent_id=review_job_id,
                tool_names=["sandbox_logs", "rubric_scorer", "evidence_extractor"],
                mode=review_run.mode,
                prompt_version="review-v1",
                token_usage=review_run.token_usage,
                created_at=now,
                finished_at=finished_at,
            )
            record_agent_trace(
                conn,
                agent_run_id=review_agent_run_id,
                learner_id=submission["learner_id"],
                agent_name="ReviewAgent",
                runtime="claude_agent_sdk" if review_run.provider == "anthropic" else "mock",
                provider=review_run.provider,
                model=review_run.model,
                input_data=context,
                output_data=result.model_dump(mode="json"),
                status="succeeded",
                latency_ms=review_run.latency_ms,
                parent_type="review_job",
                parent_id=review_job_id,
                tool_names=["sandbox_logs", "rubric_scorer", "evidence_extractor"],
            )
        review_id = persist_review_result(conn, review_job_id, job["submission_id"], result, review_run)
        transition_review_job(conn, review_job_id, "succeeded", finished_at=finished_at, review_id=review_id)
        conn.execute(
            "UPDATE submissions SET status = ?, latest_review_id = ?, updated_at = ? WHERE id = ?",
            ("review_completed", review_id, finished_at, job["submission_id"]),
        )
        submission_status = "needs_revision" if result.next_action == "revise" else "passed"
        transition_submission(conn, job["submission_id"], submission_status)
        return {"review_job_id": review_job_id, "review_id": review_id, "status": "succeeded"}
    except Exception as exc:
        fail_review_job(conn, review_job_id, str(exc))
        raise


def transition_review_job(
    conn: DbConnection,
    review_job_id: str,
    next_state: str,
    *,
    started_at: str | None = None,
    finished_at: str | None = None,
    review_id: str | None = None,
) -> None:
    job = conn.execute("SELECT * FROM review_jobs WHERE id = ?", (review_job_id,)).fetchone()
    if job is None:
        raise ValueError("Review job not found")
    ensure_transition("review_job", job["status"], next_state)
    conn.execute(
        """
        UPDATE review_jobs
        SET status = ?,
            started_at = COALESCE(?, started_at),
            finished_at = COALESCE(?, finished_at),
            review_id = COALESCE(?, review_id),
            attempt_count = attempt_count + CASE WHEN ? = 'running' THEN 1 ELSE 0 END
        WHERE id = ?
        """,
        (next_state, started_at, finished_at, review_id, next_state, review_job_id),
    )


def fail_review_job(conn: DbConnection, review_job_id: str, error: str) -> None:
    now = now_iso()
    job = conn.execute("SELECT * FROM review_jobs WHERE id = ?", (review_job_id,)).fetchone()
    if job and job["status"] not in {"succeeded", "failed", "cancelled"}:
        conn.execute(
            "UPDATE review_jobs SET status = ?, last_error = ?, finished_at = ? WHERE id = ?",
            ("failed", error, now, review_job_id),
        )
        conn.execute(
            "UPDATE submissions SET status = ?, updated_at = ? WHERE id = ?",
            ("needs_revision", now, job["submission_id"]),
        )


def build_review_context(conn: DbConnection, submission_id: str, sandbox_result: dict[str, Any]) -> dict[str, Any]:
    submission = conn.execute(
        """
        SELECT
          s.*,
          t.slug AS task_slug,
          t.title AS task_title,
          t.description AS task_description,
          pt.slug AS project_slug,
          pt.title AS project_title,
          pt.description AS project_description
        FROM submissions s
        JOIN tasks t ON t.id = s.task_id
        JOIN learner_projects lp ON lp.id = s.learner_project_id
        JOIN project_templates pt ON pt.id = lp.project_template_id
        WHERE s.id = ?
        """,
        (submission_id,),
    ).fetchone()
    if submission is None:
        raise ValueError("Submission not found")
    skill_rows = conn.execute("SELECT slug, name, description FROM skill_nodes ORDER BY name").fetchall()
    return {
        "submission": {
            "id": submission["id"],
            "github_repo_url": submission["github_repo_url"],
            "demo_url": submission["demo_url"],
            "readme_url": submission["readme_url"],
            "architecture_doc_url": submission["architecture_doc_url"],
            "evaluation_report_url": submission["evaluation_report_url"],
            "source_repo_path": submission["source_repo_path"],
            "reflection_text": submission["reflection_text"],
        },
        "project": {
            "slug": submission["project_slug"],
            "title": submission["project_title"],
            "description": submission["project_description"],
        },
        "task": {
            "slug": submission["task_slug"],
            "title": submission["task_title"],
            "description": submission["task_description"],
        },
        "sandbox": sandbox_result,
        "skill_nodes": [dict(row) for row in skill_rows],
    }


def transition_submission(conn: DbConnection, submission_id: str, next_state: str) -> None:
    submission = conn.execute("SELECT * FROM submissions WHERE id = ?", (submission_id,)).fetchone()
    if submission is None:
        raise ValueError("Submission not found")
    ensure_transition("submission", submission["status"], next_state)
    conn.execute(
        "UPDATE submissions SET status = ?, updated_at = ? WHERE id = ?",
        (next_state, now_iso(), submission_id),
    )


def persist_review_result(
    conn: DbConnection,
    review_job_id: str,
    submission_id: str,
    result: ReviewResult,
    review_run: ReviewRun,
) -> str:
    now = now_iso()
    review_id = new_id()
    conn.execute(
        """
        INSERT INTO reviews (
          id, review_job_id, submission_id, reviewer_type, overall_score,
          hiring_readiness, confidence, summary, next_action, raw_json, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            review_id,
            review_job_id,
            submission_id,
            review_run.reviewer_type,
            result.overall_score,
            result.hiring_readiness,
            result.confidence,
            result.summary,
            result.next_action,
            result.model_dump_json(),
            now,
        ),
    )
    for score in result.rubric_scores:
        conn.execute(
            """
            INSERT INTO review_scores (id, review_id, rubric_item_key, score, max_score, reason, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (new_id(), review_id, score.rubric_item_key, score.score, score.max_score, score.reason, now),
        )
    for flag in result.risk_flags:
        conn.execute(
            """
            INSERT INTO review_risk_flags (id, review_id, type, severity, description, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (new_id(), review_id, flag.type, flag.severity, flag.description, now),
        )
    generate_evidence_from_review(conn, review_id, result)
    generate_coach_tasks_from_review(conn, review_id, result)
    return review_id


def generate_coach_tasks_from_review(conn: DbConnection, review_id: str, result: ReviewResult) -> None:
    review = conn.execute("SELECT * FROM reviews WHERE id = ?", (review_id,)).fetchone()
    submission = conn.execute("SELECT * FROM submissions WHERE id = ?", (review["submission_id"],)).fetchone()
    low_scores = sorted(result.rubric_scores, key=lambda item: item.score)[:2]
    risk_flags = result.risk_flags[:2]
    actions: list[dict[str, Any]] = []

    for score in low_scores:
        actions.append(
            {
                "type": "rubric_fix",
                "label": f"修复 {score.rubric_item_key}",
                "instruction": score.reason or "补充能证明该项能力的项目证据。",
                "deliverable": "写入 README / evaluation report，并重新提交质量门。",
            }
        )
    for flag in risk_flags:
        actions.append(
            {
                "type": "risk_fix",
                "label": f"处理 {flag.type}",
                "instruction": flag.description or "解释风险来源并给出修复证据。",
                "deliverable": "补充失败样例、修复动作和复测结果。",
            }
        )

    if not actions:
        actions.append(
            {
                "type": "passport_polish",
                "label": "强化招聘方说明",
                "instruction": "把项目结果整理成招聘方能理解的技术故事。",
                "deliverable": "补充 README 项目亮点、架构图和面试讲解稿。",
            }
        )

    first_action = actions[0]
    conn.execute(
        """
        INSERT INTO coach_tasks (
          id, learner_id, learner_project_id, review_id, source_type, title,
          reason, action_json, status, priority, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            new_id(),
            submission["learner_id"],
            submission["learner_project_id"],
            review_id,
            "review",
            first_action["label"],
            "Review Agent 已完成质量门分析，系统自动生成下一轮训练任务。",
            json.dumps(actions),
            "open",
            10 if result.next_action == "revise" else 40,
            now_iso(),
        ),
    )
    coach_agent_run_id = record_agent_run(
        conn,
        learner_id=submission["learner_id"],
        agent_name="CoachTaskAgent",
        runtime="rule",
        provider="agentlab",
        model=None,
        input_data={"review_id": review_id, "overall_score": result.overall_score, "next_action": result.next_action},
        output_data={"actions": actions},
        status="succeeded",
        latency_ms=None,
        parent_type="review",
        parent_id=review_id,
        tool_names=["rubric_gap_reader", "risk_flag_reader", "next_task_generator"],
        mode="rule",
        prompt_version="coach-task-v1",
    )
    record_agent_trace(
        conn,
        agent_run_id=coach_agent_run_id,
        learner_id=submission["learner_id"],
        agent_name="CoachTaskAgent",
        runtime="rule",
        provider="agentlab",
        model=None,
        input_data={"review_id": review_id, "overall_score": result.overall_score, "next_action": result.next_action},
        output_data={"actions": actions},
        status="succeeded",
        latency_ms=None,
        parent_type="review",
        parent_id=review_id,
        tool_names=["rubric_gap_reader", "risk_flag_reader", "next_task_generator"],
    )


def generate_evidence_from_review(conn: DbConnection, review_id: str, result: ReviewResult) -> None:
    review = conn.execute("SELECT * FROM reviews WHERE id = ?", (review_id,)).fetchone()
    submission = conn.execute("SELECT * FROM submissions WHERE id = ?", (review["submission_id"],)).fetchone()
    learner_project = conn.execute("SELECT * FROM learner_projects WHERE id = ?", (submission["learner_project_id"],)).fetchone()
    for candidate in result.evidence_items:
        skill = conn.execute("SELECT * FROM skill_nodes WHERE slug = ?", (candidate.skill_slug,)).fetchone()
        if skill is None:
            continue
        evidence_id = new_id()
        source_url = submission["github_repo_url"] if candidate.source_ref in {"github_repo_url", "mock_review"} else None
        conn.execute(
            """
            INSERT INTO evidence_items (
              id, learner_id, project_template_id, task_id, submission_id, review_id,
              skill_node_id, source_type, source_url, score, confidence, evidence_text,
              risk_flags, reviewer_type, is_verified, is_passport_eligible, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                evidence_id,
                submission["learner_id"],
                learner_project["project_template_id"],
                submission["task_id"],
                submission["id"],
                review_id,
                skill["id"],
                candidate.source_type,
                source_url,
                candidate.score,
                candidate.confidence,
                candidate.evidence_text,
                json.dumps([flag.model_dump() for flag in result.risk_flags]),
                review["reviewer_type"],
                0,
                1 if candidate.passport_eligible else 0,
                now_iso(),
            ),
        )
        update_skill_score(conn, submission["learner_id"], skill["id"], evidence_id, candidate.score, candidate.confidence)


def update_skill_score(
    conn: DbConnection,
    learner_id: str,
    skill_node_id: str,
    evidence_id: str,
    evidence_score: int,
    evidence_confidence: float,
) -> None:
    now = now_iso()
    existing = conn.execute(
        "SELECT * FROM learner_skill_scores WHERE learner_id = ? AND skill_node_id = ?",
        (learner_id, skill_node_id),
    ).fetchone()
    if existing:
        previous_score = int(existing["score"])
        evidence_count = int(existing["evidence_count"]) + 1
        new_score = round((previous_score * existing["evidence_count"] + evidence_score) / evidence_count)
        new_confidence = min(1.0, float(existing["confidence"]) + evidence_confidence * 0.15)
        conn.execute(
            """
            UPDATE learner_skill_scores
            SET score = ?, confidence = ?, evidence_count = ?, updated_at = ?
            WHERE id = ?
            """,
            (new_score, new_confidence, evidence_count, now, existing["id"]),
        )
    else:
        previous_score = None
        new_score = evidence_score
        conn.execute(
            """
            INSERT INTO learner_skill_scores (id, learner_id, skill_node_id, score, confidence, evidence_count, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (new_id(), learner_id, skill_node_id, new_score, evidence_confidence, 1, now),
        )
    conn.execute(
        """
        INSERT INTO skill_score_history (
          id, learner_id, skill_node_id, evidence_item_id, previous_score,
          new_score, score_delta, reason, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            new_id(),
            learner_id,
            skill_node_id,
            evidence_id,
            previous_score,
            new_score,
            new_score - (previous_score or 0),
            "Updated from review evidence.",
            now,
        ),
    )


def get_review(conn: DbConnection, review_id: str, learner_id: str | None = None) -> dict[str, Any]:
    if learner_id:
        review = conn.execute(
            """
            SELECT r.*
            FROM reviews r
            JOIN submissions s ON s.id = r.submission_id
            WHERE r.id = ? AND s.learner_id = ?
            """,
            (review_id, learner_id),
        ).fetchone()
    else:
        review = conn.execute("SELECT * FROM reviews WHERE id = ?", (review_id,)).fetchone()
    if review is None:
        raise ValueError("Review not found")
    scores = conn.execute("SELECT * FROM review_scores WHERE review_id = ?", (review_id,)).fetchall()
    flags = conn.execute("SELECT * FROM review_risk_flags WHERE review_id = ?", (review_id,)).fetchall()
    coach_rows = conn.execute(
        "SELECT * FROM coach_tasks WHERE review_id = ? ORDER BY priority, created_at DESC",
        (review_id,),
    ).fetchall()
    return {
        **dict(review),
        "rubric_scores": [dict(row) for row in scores],
        "risk_flags": [dict(row) for row in flags],
        "coach_tasks": [{**dict(row), "actions": json.loads(row["action_json"])} for row in coach_rows],
    }


def get_submission(conn: DbConnection, submission_id: str, learner_id: str | None = None) -> dict[str, Any]:
    if learner_id:
        row = conn.execute("SELECT * FROM submissions WHERE id = ? AND learner_id = ?", (submission_id, learner_id)).fetchone()
    else:
        row = conn.execute("SELECT * FROM submissions WHERE id = ?", (submission_id,)).fetchone()
    if row is None:
        raise ValueError("Submission not found")
    return dict(row)


def list_evidence(conn: DbConnection, learner_id: str) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT ei.*, sn.name AS skill, sn.slug AS skill_slug
        FROM evidence_items ei
        JOIN skill_nodes sn ON sn.id = ei.skill_node_id
        WHERE ei.learner_id = ?
        ORDER BY ei.created_at DESC
        """,
        (learner_id,),
    ).fetchall()
    return [dict(row) for row in rows]


def list_agent_traces(conn: DbConnection, learner_id: str) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT
          id, agent_name, runtime, provider, model, tool_names_json,
          status, latency_ms, parent_type, parent_id, created_at
        FROM agent_traces
        WHERE learner_id = ?
        ORDER BY created_at DESC
        """,
        (learner_id,),
    ).fetchall()
    return [
        {
            **dict(row),
            "tool_names": json.loads(row["tool_names_json"]) if row["tool_names_json"] else [],
        }
        for row in rows
    ]


def generate_passport(conn: DbConnection, learner_id: str) -> dict[str, Any]:
    user = conn.execute("SELECT * FROM users WHERE id = ?", (learner_id,)).fetchone()
    if user is None:
        raise ValueError("Learner not found")
    now = now_iso()
    passport = conn.execute("SELECT * FROM hiring_passports WHERE learner_id = ?", (learner_id,)).fetchone()
    if passport is None:
        passport_id = new_id()
        slug = user["email"].split("@")[0].replace(".", "-") + "-agentlab"
        conn.execute(
            """
            INSERT INTO hiring_passports (id, learner_id, slug, visibility, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (passport_id, learner_id, slug, "unlisted", now, now),
        )
    else:
        passport_id = passport["id"]
        slug = passport["slug"]

    latest_version = conn.execute(
        "SELECT COALESCE(MAX(version), 0) AS version FROM passport_snapshots WHERE hiring_passport_id = ?",
        (passport_id,),
    ).fetchone()["version"]
    version = int(latest_version) + 1
    skill_map = get_skill_map(conn, learner_id)
    evidence = list_evidence(conn, learner_id)
    projects = list_projects(conn, learner_id)
    ai_dependency = get_ai_dependency_summary(conn, learner_id)
    snapshot = {
        "version": version,
        "learner": {"display_name": user["display_name"], "email": user["email"]},
        "target_job": skill_map["target_job"],
        "skill_summary": skill_map["skills"],
        "projects": projects,
        "evidence": evidence,
        "ai_dependency": ai_dependency,
    }
    snapshot_id = new_id()
    conn.execute(
        """
        INSERT INTO passport_snapshots (id, hiring_passport_id, version, status, snapshot_json, created_at, published_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (snapshot_id, passport_id, version, "published", json.dumps(snapshot), now, now),
    )
    conn.execute("UPDATE hiring_passports SET updated_at = ? WHERE id = ?", (now, passport_id))
    return {"passport_id": passport_id, "snapshot_id": snapshot_id, "version": version, "status": "published", "slug": slug}


def get_passport(conn: DbConnection, slug: str) -> dict[str, Any]:
    passport = conn.execute("SELECT * FROM hiring_passports WHERE slug = ?", (slug,)).fetchone()
    if passport is None:
        raise ValueError("Passport not found")
    snapshot = conn.execute(
        """
        SELECT * FROM passport_snapshots
        WHERE hiring_passport_id = ?
        ORDER BY version DESC
        LIMIT 1
        """,
        (passport["id"],),
    ).fetchone()
    return {
        "slug": passport["slug"],
        "visibility": passport["visibility"],
        "latest_snapshot": json.loads(snapshot["snapshot_json"]) if snapshot else None,
    }


def export_portfolio(
    conn: DbConnection,
    submission_id: str,
    export_types: list[str],
    learner_id: str,
) -> list[dict[str, Any]]:
    submission = conn.execute(
        "SELECT * FROM submissions WHERE id = ? AND learner_id = ?",
        (submission_id, learner_id),
    ).fetchone()
    if submission is None:
        raise ValueError("Submission not found")
    now = now_iso()
    exports = []
    for export_type in export_types:
        content = build_export_content(export_type, submission)
        export_id = new_id()
        conn.execute(
            """
            INSERT INTO portfolio_exports (id, learner_id, submission_id, export_type, content, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (export_id, submission["learner_id"], submission_id, export_type, content, now),
        )
        exports.append({"id": export_id, "export_type": export_type, "content": content})
    return exports


def build_export_content(export_type: str, submission: Any) -> str:
    if export_type == "resume_bullets":
        return "构建了一个 RAG 知识库 Agent，包含可追溯检索、项目文档和结构化工程评审证据。"
    if export_type == "interview_script":
        return "我构建这个 RAG 项目是为了让系统能基于自定义文档回答问题。核心取舍是检索质量、引用可信度和实现复杂度之间的平衡。"
    if export_type == "readme":
        return "# RAG 知识库 Agent\n\n本项目展示文档检索、基于上下文的回答生成、引用溯源和评测计划。"
    return "根据 AgentLab 能力证据生成的作品集材料。"

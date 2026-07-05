from __future__ import annotations

import json

from .db import get_conn, init_db
from .services import DEMO_USER_ID
from .utils import now_iso


def upsert(conn, table: str, row: dict) -> None:
    keys = list(row.keys())
    placeholders = ", ".join(["?"] * len(keys))
    columns = ", ".join(keys)
    updates = ", ".join([f"{key}=excluded.{key}" for key in keys if key != "id"])
    conn.execute(
        f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) ON CONFLICT(id) DO UPDATE SET {updates}",
        tuple(row[key] for key in keys),
    )


def reset_demo_runtime_state(conn) -> None:
    learner_id = DEMO_USER_ID
    conn.execute("DELETE FROM agent_traces WHERE learner_id = ?", (learner_id,))
    conn.execute("DELETE FROM agent_runs WHERE learner_id = ?", (learner_id,))
    for row in conn.execute("SELECT id FROM planning_sessions WHERE learner_id = ?", (learner_id,)).fetchall():
        conn.execute("DELETE FROM planning_agent_runs WHERE session_id = ?", (row["id"],))
        conn.execute("DELETE FROM planning_messages WHERE session_id = ?", (row["id"],))
    conn.execute("DELETE FROM planning_sessions WHERE learner_id = ?", (learner_id,))
    for row in conn.execute("SELECT id FROM tutor_sessions WHERE learner_id = ?", (learner_id,)).fetchall():
        conn.execute("DELETE FROM tutor_agent_runs WHERE tutor_session_id = ?", (row["id"],))
        conn.execute("DELETE FROM tutor_messages WHERE tutor_session_id = ?", (row["id"],))
    conn.execute("DELETE FROM tutor_sessions WHERE learner_id = ?", (learner_id,))
    for row in conn.execute("SELECT id FROM hiring_passports WHERE learner_id = ?", (learner_id,)).fetchall():
        conn.execute("DELETE FROM passport_snapshots WHERE hiring_passport_id = ?", (row["id"],))
    conn.execute("DELETE FROM hiring_passports WHERE learner_id = ?", (learner_id,))
    conn.execute("DELETE FROM portfolio_exports WHERE learner_id = ?", (learner_id,))
    conn.execute("DELETE FROM skill_score_history WHERE learner_id = ?", (learner_id,))
    conn.execute("DELETE FROM evidence_items WHERE learner_id = ?", (learner_id,))
    conn.execute("DELETE FROM learner_skill_scores WHERE learner_id = ?", (learner_id,))
    conn.execute("DELETE FROM coach_tasks WHERE learner_id = ?", (learner_id,))
    conn.execute("DELETE FROM course_exercise_attempts WHERE learner_id = ?", (learner_id,))
    for sub in conn.execute("SELECT id FROM submissions WHERE learner_id = ?", (learner_id,)).fetchall():
        for job in conn.execute("SELECT id, review_id FROM review_jobs WHERE submission_id = ?", (sub["id"],)).fetchall():
            if job["review_id"]:
                conn.execute("DELETE FROM review_scores WHERE review_id = ?", (job["review_id"],))
                conn.execute("DELETE FROM review_risk_flags WHERE review_id = ?", (job["review_id"],))
                conn.execute("DELETE FROM reviews WHERE id = ?", (job["review_id"],))
            conn.execute("DELETE FROM sandbox_runs WHERE review_job_id = ?", (job["id"],))
            conn.execute("DELETE FROM agent_runs WHERE review_job_id = ?", (job["id"],))
            conn.execute("DELETE FROM review_jobs WHERE id = ?", (job["id"],))
    conn.execute("DELETE FROM submissions WHERE learner_id = ?", (learner_id,))
    conn.execute("DELETE FROM learner_projects WHERE learner_id = ?", (learner_id,))
    conn.execute("DELETE FROM course_progress WHERE learner_id = ?", (learner_id,))
    conn.execute("DELETE FROM learning_plans WHERE learner_id = ?", (learner_id,))
    conn.execute("DELETE FROM intake_assessments WHERE learner_id = ?", (learner_id,))


def lesson_body(title: str, description: str) -> str:
    return "\n\n".join(
        [
            f"这节小课只服务当前项目任务：{title}。",
            f"1. 核心概念：{description}",
            "2. 项目例子：把这个方法直接用到 README、代码实现、测试样例或评估报告里。",
            "3. 常见错误：只写概念、不写验证；只跑通一次、不记录失败样例；让 AI 生成答案但不说明自己的取舍。",
            "4. 小任务：写出一个具体实现动作、一个验证方法、一个失败后的调整策略。",
            "5. 留下证据：把应用结果写进 README 或 evaluation report，作为求职能力报告里的项目证据。",
        ]
    )


def seed() -> None:
    init_db()
    now = now_iso()
    with get_conn() as conn:
        reset_demo_runtime_state(conn)

        jobs = [
            ("job-ai-app", "ai_agent_builder", "AI Agent Builder", "Build, evaluate, and ship AI Agent applications."),
            ("job-rag", "rag_builder", "RAG Builder", "Build reliable knowledge-base agents with retrieval evaluation."),
            ("job-agent-auto", "ai_agent_automation_engineer", "AI Agent Automation Engineer", "Build tool-using agents for business workflows."),
        ]
        for job_id, slug, title, description in jobs:
            upsert(conn, "target_jobs", {"id": job_id, "slug": slug, "title": title, "description": description, "is_active": 1, "created_at": now})

        upsert(
            conn,
            "users",
            {
                "id": DEMO_USER_ID,
                "email": "learner@example.com",
                "display_name": "Demo Learner",
                "role": "learner",
                "selected_target_job_id": "job-ai-app",
                "created_at": now,
                "updated_at": now,
            },
        )

        skills = [
            ("skill-prompt", "prompt_engineering", "Prompt Engineering"),
            ("skill-structured", "structured_output", "Structured Output"),
            ("skill-rag", "rag", "RAG"),
            ("skill-vector", "vector_search", "Vector Search"),
            ("skill-eval", "evaluation_trace", "Evaluation"),
            ("skill-debug", "debug", "Debug"),
            ("skill-deploy", "deployment", "Deployment"),
            ("skill-docs", "documentation", "Documentation"),
            ("skill-delivery", "project_delivery", "Project Delivery"),
            ("skill-comm", "technical_communication", "Technical Communication"),
        ]
        for skill_id, slug, name in skills:
            upsert(conn, "skill_nodes", {"id": skill_id, "slug": slug, "name": name, "description": name, "category": "builder", "created_at": now})
            upsert(
                conn,
                "job_skill_requirements",
                {
                    "id": f"req-job-ai-app-{skill_id}",
                    "target_job_id": "job-ai-app",
                    "skill_node_id": skill_id,
                    "required_level": 75 if skill_id in {"skill-rag", "skill-docs", "skill-delivery"} else 65,
                    "weight": 1,
                    "evidence_expectation": "Evidence from project review and submitted artifacts.",
                    "created_at": now,
                },
            )

        projects = [
            ("project-workflow", "prompt_workflow_agent", "Prompt + Workflow Agent", "Build a structured-output business assistant with workflow steps and basic evaluation.", "01"),
            ("project-rag", "rag_knowledge_agent", "RAG Knowledge Agent", "Build a knowledge-base Q&A agent with citations and retrieval evaluation.", "02"),
            ("project-tool-use", "business_automation_agent", "Tool Use / Business Automation Agent", "Build an agent that calls tools, handles failures, and documents delivery.", "03"),
        ]
        for project_id, slug, title, description, level in projects:
            upsert(
                conn,
                "project_templates",
                {"id": project_id, "slug": slug, "title": title, "description": description, "target_job_id": "job-ai-app", "level": level, "is_active": 1, "created_at": now},
            )
            upsert(
                conn,
                "learner_projects",
                {"id": f"learner-{project_id}", "learner_id": DEMO_USER_ID, "project_template_id": project_id, "status": "not_started", "started_at": None, "completed_at": None, "created_at": now},
            )

        tasks = [
            ("task-workflow-final", "project-workflow", "workflow_submission", "Structured Workflow Agent submission", "Submit prompt, workflow steps, sample inputs, output schema, and basic evaluation.", ["github_repo_url", "readme_url", "reflection_text"]),
            ("task-rag-final", "project-rag", "final_submission", "RAG final submission", "Submit repo, demo, README, retrieval evaluation report, and reflection.", ["github_repo_url", "readme_url", "evaluation_report_url", "reflection_text"]),
            ("task-tool-use-final", "project-tool-use", "automation_submission", "Business automation Agent submission", "Submit tool definitions, error handling, approval flow, deployment notes, and reflection.", ["github_repo_url", "readme_url", "architecture_doc_url", "reflection_text"]),
        ]
        for index, (task_id, project_id, slug, title, description, required) in enumerate(tasks, start=1):
            upsert(
                conn,
                "tasks",
                {"id": task_id, "project_template_id": project_id, "slug": slug, "title": title, "description": description, "sort_order": index, "required_submission_types": json.dumps(required), "created_at": now},
            )

        courses = [
            ("course-python-api", "python_api_github_foundation", "Python / API / GitHub Foundation", "Build a reproducible AI project: API call, repo structure, dependencies, and run command.", "Foundation", "skill-debug", "beginner", 90, 10),
            ("course-prompt-structured", "prompt_structured_output", "Structured Prompt and Output", "Design prompts that return stable structured outputs with constraints and failure cases.", "Prompt", "skill-structured", "beginner", 60, 20),
            ("course-workflow", "workflow_design", "Workflow Agent Design", "Break a business process into steps, state, validation, and controlled output.", "Workflow", "skill-prompt", "beginner", 75, 30),
            ("course-basic-eval", "basic_eval_trace", "Basic Evaluation", "Create sample tests, failure records, and trace logs before the project gets complex.", "Evaluation", "skill-eval", "beginner", 60, 40),
            ("course-rag-fundamentals", "rag_fundamentals", "RAG Fundamentals", "Understand loading, chunking, embeddings, retrieval, and context-grounded answers.", "RAG", "skill-rag", "intermediate", 90, 50),
            ("course-vector", "chunking_embedding_vector_db", "Chunking / Embedding / Vector DB", "Build retrieval with chunk size, metadata, and vector search tradeoffs.", "RAG", "skill-vector", "intermediate", 100, 60),
            ("course-retrieval-eval", "retrieval_eval", "Retrieval Evaluation", "Measure hit rate, citation quality, hallucination risk, and retrieval degradation.", "Evaluation", "skill-eval", "intermediate", 80, 70),
            ("course-rag-grounding", "rag_prompt_grounding", "RAG Prompt Grounding", "Write prompts that cite context, refuse unsupported answers, and expose uncertainty.", "RAG", "skill-rag", "intermediate", 60, 80),
            ("course-tool-use", "function_calling_tool_use", "Function Calling and Tool Use", "Define tools, validate parameters, execute calls, and return structured tool results.", "Agent", "skill-prompt", "advanced", 90, 90),
            ("course-error-hitl", "error_handling_hitl", "Error Handling and Human Approval", "Add retries, fallback behavior, human approval nodes, and auditable logs.", "Agent", "skill-debug", "advanced", 80, 100),
            ("course-deploy", "deployment_basics", "Deployment Basics", "Ship a small AI app with environment variables, docs, and reproducible run command.", "Deployment", "skill-deploy", "advanced", 90, 110),
            ("course-writing", "technical_writing_for_ai_projects", "AI Project Technical Writing", "Write README, architecture notes, limitations, and evaluation reports recruiters can trust.", "Portfolio", "skill-docs", "intermediate", 70, 120),
        ]
        for course_id, slug, title, description, category, skill_id, difficulty, minutes, order in courses:
            upsert(
                conn,
                "course_modules",
                {"id": course_id, "slug": slug, "title": title, "description": description, "category": category, "skill_node_id": skill_id, "difficulty": difficulty, "estimated_minutes": minutes, "sort_order": order, "created_at": now},
            )
            upsert(
                conn,
                "course_lessons",
                {"id": f"lesson-{course_id}-overview", "course_module_id": course_id, "title": f"{title}: project application", "content_type": "text", "content_ref": f"db://course_lessons/lesson-{course_id}-overview", "body": lesson_body(title, description), "sort_order": 10, "created_at": now},
            )
            upsert(
                conn,
                "course_exercises",
                {
                    "id": f"exercise-{course_id}-apply",
                    "course_module_id": course_id,
                    "prompt": f"Use 3-5 sentences to explain how you will apply {title} to the current project. Include one implementation action, one validation method, and one adjustment strategy after failure.",
                    "expected_keywords": json.dumps(["实现", "验证", "失败", "调整"]),
                    "rubric_json": json.dumps({"implementation": 35, "validation": 35, "debug_strategy": 30}),
                    "created_at": now,
                },
            )

        task_courses = [
            ("task-course-workflow-1", "task-workflow-final", "course-prompt-structured", "Used to produce stable structured outputs.", 10),
            ("task-course-workflow-2", "task-workflow-final", "course-workflow", "Used to model a business assistant as a controlled workflow.", 20),
            ("task-course-workflow-3", "task-workflow-final", "course-basic-eval", "Used to prove the workflow passes sample tasks.", 30),
            ("task-course-rag-1", "task-rag-final", "course-rag-fundamentals", "Used to build the RAG baseline.", 10),
            ("task-course-rag-2", "task-rag-final", "course-vector", "Used to complete chunking, embeddings, and retrieval strategy.", 20),
            ("task-course-rag-3", "task-rag-final", "course-retrieval-eval", "Used to complete the retrieval evaluation report.", 30),
            ("task-course-rag-4", "task-rag-final", "course-rag-grounding", "Used to reduce hallucination and improve citation credibility.", 40),
            ("task-course-tool-1", "task-tool-use-final", "course-tool-use", "Used to implement tool calls correctly.", 10),
            ("task-course-tool-2", "task-tool-use-final", "course-error-hitl", "Used to handle failures, retries, and human approval.", 20),
            ("task-course-tool-3", "task-tool-use-final", "course-deploy", "Used to package and deploy the automation agent.", 30),
            ("task-course-tool-4", "task-tool-use-final", "course-writing", "Used to improve portfolio and delivery documentation.", 40),
        ]
        for link_id, task_id, course_id, reason, order in task_courses:
            upsert(conn, "task_course_modules", {"id": link_id, "task_id": task_id, "course_module_id": course_id, "reason": reason, "sort_order": order, "created_at": now})


if __name__ == "__main__":
    seed()

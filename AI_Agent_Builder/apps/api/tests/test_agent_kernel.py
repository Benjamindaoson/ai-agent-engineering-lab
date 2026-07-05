from pathlib import Path

from fastapi.testclient import TestClient

from app.db import get_conn
from app.main import app
from app.seed import seed


def test_planner_and_tutor_write_canonical_agent_runs():
    seed()
    client = TestClient(app)

    planning = client.post(
        "/api/planning/sessions",
        json={"message": "我想转行做 AI Agent 工程师，每周 8 小时，想做企业知识库项目。"},
    ).json()
    session_id = planning["session"]["id"]

    projects = client.get("/api/projects").json()["projects"]
    project_id = next(project["learner_project_id"] for project in projects if project["project_template_slug"] == "rag_knowledge_agent")
    client.post(
        f"/api/projects/{project_id}/tutor/messages",
        json={"message": "我需要你帮我拆解 RAG 评测应该怎么做，不要直接给完整答案。"},
    )

    with get_conn() as conn:
        planner_run = conn.execute(
            """
            SELECT *
            FROM agent_runs
            WHERE agent_name = ? AND parent_type = ? AND parent_id = ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            ("LearningPlannerAgent", "planning_session", session_id),
        ).fetchone()
        tutor_run = conn.execute(
            """
            SELECT *
            FROM agent_runs
            WHERE agent_name = ? AND parent_type = ? AND learner_id = ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            ("ProjectTutorAgent", "tutor_session", "learner-demo"),
        ).fetchone()
        planner_trace = conn.execute(
            "SELECT * FROM agent_traces WHERE agent_run_id = ?",
            (planner_run["id"] if planner_run else "",),
        ).fetchone()

    assert planner_run is not None
    assert planner_run["learner_id"] == "learner-demo"
    assert planner_run["runtime"] in {"rule", "claude_agent_sdk"}
    assert planner_run["status"] == "succeeded"
    assert planner_run["tool_names_json"]
    assert tutor_run is not None
    assert tutor_run["runtime"] in {"rule", "claude_agent_sdk"}
    assert tutor_run["status"] == "succeeded"
    assert planner_trace is not None


def test_review_chain_writes_review_and_next_task_agent_runs():
    seed()
    client = TestClient(app)
    sample_repo = Path(__file__).resolve().parents[3] / "samples" / "rag-agent"

    projects = client.get("/api/projects").json()["projects"]
    project_id = next(project["learner_project_id"] for project in projects if project["project_template_slug"] == "rag_knowledge_agent")
    project = client.get(f"/api/projects/{project_id}").json()
    task_id = project["tasks"][0]["id"]

    submission = client.post(
        "/api/submissions",
        json={
            "learner_project_id": project_id,
            "task_id": task_id,
            "github_repo_url": "https://github.com/example/rag-agent",
            "source_repo_path": str(sample_repo),
            "sandbox_command": "python -m unittest discover -s tests -q",
            "reflection_text": "Agent kernel test submission.",
            "queue_review": True,
        },
    ).json()
    review_job_id = submission["review_job_id"]

    result = client.post(f"/api/reviews/jobs/{review_job_id}/run").json()

    with get_conn() as conn:
        review_run = conn.execute(
            """
            SELECT *
            FROM agent_runs
            WHERE agent_name = ? AND parent_type = ? AND parent_id = ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            ("ReviewAgent", "review_job", review_job_id),
        ).fetchone()
        next_task_run = conn.execute(
            """
            SELECT *
            FROM agent_runs
            WHERE agent_name = ? AND parent_type = ? AND parent_id = ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            ("CoachTaskAgent", "review", result["review_id"]),
        ).fetchone()
        open_task = conn.execute(
            "SELECT * FROM coach_tasks WHERE review_id = ? AND status = ?",
            (result["review_id"], "open"),
        ).fetchone()
        sandbox = conn.execute(
            "SELECT * FROM sandbox_runs WHERE review_job_id = ?",
            (review_job_id,),
        ).fetchone()

    assert result["status"] == "succeeded"
    assert sandbox is not None
    assert sandbox["status"] == "succeeded"
    assert review_run is not None
    assert review_run["learner_id"] == "learner-demo"
    assert review_run["runtime"] == "mock"
    assert review_run["provider"] == "mock"
    assert next_task_run is not None
    assert next_task_run["runtime"] == "rule"
    assert open_task is not None

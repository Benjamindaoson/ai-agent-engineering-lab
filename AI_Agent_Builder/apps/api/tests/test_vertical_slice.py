from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.seed import seed


def test_agent_command_center_contract():
    seed()
    client = TestClient(app)

    response = client.get("/api/agents/command-center")

    assert response.status_code == 200
    center = response.json()
    assert center["contract_version"] == "agent_command_center.v1"
    assert center["agent"]["name"] == "AICoachAgent"
    assert center["agent"]["mode"] in {"rule", "claude_agent_sdk"}
    assert center["agent"]["stage"] in {
        "planning",
        "project_delivery",
        "review_repair",
        "evidence_building",
        "passport_ready",
    }
    assert center["mission"]["next_best_action"]["label"]
    assert center["mission"]["next_best_action"]["href"].startswith("/")
    assert center["mission"]["success_evidence"]
    assert center["workflow"]["current_step_id"] in {step["id"] for step in center["workflow"]["steps"]}
    assert [step["id"] for step in center["workflow"]["steps"]] == [
        "plan",
        "learn",
        "build",
        "review",
        "passport",
    ]
    assert center["active_project"] is not None
    assert center["active_project"]["workspace_href"].startswith("/lab/")
    assert len(center["active_project"]["tasks"]) >= 1
    assert center["active_project"]["tasks"][0]["courses"]
    assert center["course_queue"]["storage"]["module_table"] == "course_modules"
    assert len(center["course_queue"]["items"]) >= 1
    assert center["quality_gate"]["status"] in {"not_started", "queued", "running", "passed", "needs_revision"}
    assert "sandbox" in center["quality_gate"]["required_checks"]
    assert "agent_review" in center["quality_gate"]["required_checks"]
    assert center["evidence"]["store"] == "evidence_items"
    assert isinstance(center["evidence"]["latest_items"], list)
    assert center["data_sources"]["learning_plan"] == "learning_plans.plan_json"
    assert center["data_sources"]["courses"] == "course_modules + task_course_modules + course_progress"
    assert center["handoffs"]["project_lab"]["href"].startswith("/lab/")
    assert center["handoffs"]["courses"]["href"].startswith("/learn/")
    assert center["handoffs"]["review"]["href"].startswith("/gate/") or center["handoffs"]["review"]["href"] == "/projects"

    second_project_id = client.get("/api/projects").json()["projects"][1]["learner_project_id"]
    scoped = client.get(f"/api/agents/command-center?learner_project_id={second_project_id}").json()
    assert scoped["contract_version"] == "agent_command_center.v1"
    assert scoped["active_project"]["id"] == second_project_id
    assert scoped["handoffs"]["project_lab"]["href"] == f"/lab/{second_project_id}"
    assert scoped["mission"]["next_best_action"]["href"].startswith("/")


def test_course_workbench_contract():
    seed()
    client = TestClient(app)

    course_id = client.get("/api/courses").json()["courses"][0]["id"]
    response = client.get(f"/api/courses/{course_id}/workbench")

    assert response.status_code == 200
    workbench = response.json()
    assert workbench["contract_version"] == "course_workbench.v1"
    assert workbench["agent"]["name"] == "MicroExerciseCoach"
    assert workbench["course"]["id"] == course_id
    assert workbench["mission"]["title"]
    assert workbench["project_context"]["project"]["workspace_href"].startswith("/lab/")
    assert workbench["project_context"]["task"]["id"]
    assert workbench["exercise"]["prompt"]
    assert workbench["exercise"]["pass_standard"]["minimum_score"] == 70
    assert "implementation" in workbench["exercise"]["rubric"]
    assert workbench["handoffs"]["project_lab"]["href"].startswith("/lab/")
    assert workbench["handoffs"]["command_center"]["href"] == "/coach"
    assert workbench["data_sources"]["course"] == "course_modules + course_lessons"
    assert workbench["data_sources"]["exercise"] == "course_exercises + course_exercise_attempts"


def test_review_gate_workbench_contract():
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
            "reflection_text": "Quality gate workbench test submission.",
            "queue_review": True,
        },
    ).json()
    review_job_id = submission["review_job_id"]

    queued = client.get(f"/api/reviews/jobs/{review_job_id}/workbench")
    assert queued.status_code == 200
    queued_workbench = queued.json()
    assert queued_workbench["contract_version"] == "review_gate_workbench.v1"
    assert queued_workbench["agent"]["name"] == "ReviewAgent"
    assert queued_workbench["job"]["status"] == "queued"
    assert queued_workbench["workflow"]["current_step_id"] in {"sandbox", "agent_review"}
    assert [step["id"] for step in queued_workbench["workflow"]["steps"]] == [
        "sandbox",
        "agent_review",
        "evidence",
        "next_task",
    ]
    assert queued_workbench["project_context"]["project"]["workspace_href"] == f"/lab/{project_id}"
    assert queued_workbench["handoffs"]["project_lab"]["href"] == f"/lab/{project_id}"
    assert queued_workbench["data_sources"]["job"] == "review_jobs"
    assert queued_workbench["review"] is None

    run_job = client.post(f"/api/reviews/jobs/{review_job_id}/run").json()
    assert run_job["status"] == "succeeded"

    finished = client.get(f"/api/reviews/jobs/{review_job_id}/workbench")
    assert finished.status_code == 200
    workbench = finished.json()
    assert workbench["job"]["status"] == "succeeded"
    assert workbench["sandbox"]["latest"]["status"] == "succeeded"
    assert workbench["review"]["id"] == run_job["review_id"]
    assert workbench["review"]["rubric_scores"]
    assert workbench["evidence"]["items"]
    assert workbench["coach_tasks"]
    assert workbench["handoffs"]["report"]["href"] == f"/report/{run_job['review_id']}"
    assert workbench["workflow"]["current_step_id"] == "next_task"


def test_agent_command_queue_promotes_review_tasks_across_workbenches():
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
            "reflection_text": "Agent command queue test submission.",
            "queue_review": True,
        },
    ).json()
    run_job = client.post(f"/api/reviews/jobs/{submission['review_job_id']}/run").json()

    center = client.get(f"/api/agents/command-center?learner_project_id={project_id}").json()
    assert center["agent_queue"]["contract_version"] == "agent_command_queue.v1"
    assert center["agent_queue"]["source"] == "planning + course_progress + submissions + reviews + coach_tasks + evidence_items"
    assert center["agent_queue"]["commands"]
    first_command = center["agent_queue"]["commands"][0]
    assert first_command["source_type"] == "review"
    assert first_command["source_id"] == run_job["review_id"]
    assert first_command["agent"] == "AICoachAgent"
    assert first_command["status"] == "open"
    assert first_command["primary_handoff"]["href"] == f"/lab/{project_id}"
    assert first_command["quality_gate"]["href"].startswith("/gate/")
    assert first_command["evidence_outcome"]

    global_center = client.get("/api/agents/command-center").json()
    assert global_center["agent_queue"]["commands"][0]["id"] == first_command["id"]
    assert global_center["agent_queue"]["commands"][0]["primary_handoff"]["href"] == f"/lab/{project_id}"

    lab = client.get(f"/api/projects/{project_id}").json()
    assert lab["agent_queue"]["commands"][0]["id"] == first_command["id"]

    course_id = center["active_project"]["tasks"][0]["courses"][0]["id"]
    course_workbench = client.get(f"/api/courses/{course_id}/workbench").json()
    assert course_workbench["agent_queue"]["commands"][0]["id"] == first_command["id"]


def test_mock_review_to_passport_vertical_slice():
    seed()
    client = TestClient(app)
    sample_repo = Path(__file__).resolve().parents[3] / "samples" / "rag-agent"

    projects = client.get("/api/projects").json()["projects"]
    assert len(projects) >= 3
    assert {project["project_template_slug"] for project in projects} >= {
        "prompt_workflow_agent",
        "rag_knowledge_agent",
        "business_automation_agent",
    }
    dashboard = client.get("/api/dashboard").json()
    assert dashboard["learning_plan"]["estimated_weeks"] >= 8
    assert dashboard["next_best_action"]["title"]
    assert dashboard["next_best_action"]["primary_cta"]["href"].startswith("/")
    assert dashboard["agent_runtimes"]["planner"]["active_runtime"] in {"rule", "claude_agent_sdk"}
    assert "claude_agent_sdk" in dashboard["agent_runtimes"]["tutor"]["available_runtimes"]
    demo_mode = client.get("/api/demo-mode").json()
    assert len(demo_mode["steps"]) >= 7
    assert demo_mode["steps"][0]["name"] == "目标识别"
    assert demo_mode["steps"][-1]["name"] == "招聘方验证"
    planning = client.post(
        "/api/planning/sessions",
        json={
            "message": "我想转行做 AI Agent 工程师，每周能学 8 小时，希望做企业知识库和自动化 Agent 项目。"
        },
    ).json()
    assert planning["session"]["status"] == "clarifying"
    assert planning["session"]["missing_slot"] == "background"
    if planning["session"]["status"] == "clarifying":
        session_id = planning["session"]["id"]
        for answer in ["有一点 Python/API 基础", "企业知识库 / 文档问答"]:
            planning = client.post(
                f"/api/planning/sessions/{session_id}/messages",
                json={"message": answer},
            ).json()
            if planning["session"]["status"] == "ready_to_confirm":
                break
    assert planning["session"]["status"] == "ready_to_confirm"
    assert planning["session"]["plan_preview"]["weeks"]
    confirmed = client.post(f"/api/planning/sessions/{planning['session']['id']}/confirm", json={}).json()
    assert confirmed["session"]["status"] == "confirmed"
    assert confirmed["learning_plan"]["target_role"] == "AI Agent Builder"
    courses = client.get("/api/courses/adaptive").json()["courses"]
    assert len(courses) >= 5
    course_library = client.get("/api/courses").json()
    assert course_library["storage"]["module_table"] == "course_modules"
    assert course_library["storage"]["lesson_table"] == "course_lessons"
    assert len(course_library["courses"]) >= 5
    course_detail = client.get(f"/api/courses/{course_library['courses'][0]['id']}").json()
    assert course_detail["lessons"]
    assert course_detail["storage"]["lesson_refs"]
    progress = client.post(
        "/api/courses/progress",
        json={"course_module_id": courses[0]["id"], "status": "completed"},
    ).json()
    assert progress["status"] == "completed"
    project_id = next(project["learner_project_id"] for project in projects if project["project_template_slug"] == "rag_knowledge_agent")
    project = client.get(f"/api/projects/{project_id}").json()
    task_id = project["tasks"][0]["id"]

    tutor_state = client.get(f"/api/projects/{project_id}/tutor").json()
    assert tutor_state["session"]["ai_dependency_score"] == 0
    tutor_reply = client.post(
        f"/api/projects/{project_id}/tutor/messages",
        json={"message": "我不知道怎么设计 RAG 评测，请先帮我拆解思路。"},
    ).json()
    assert tutor_reply["session"]["ai_dependency_score"] < 40
    assert tutor_reply["messages"][-1]["role"] == "tutor"
    assert tutor_reply["messages"][-1]["hint_level"] <= 2
    assert tutor_reply["messages"][-1]["learning_signal"] in {"conceptual_gap", "debugging_need", "implementation_planning"}
    dependency_reply = client.post(
        f"/api/projects/{project_id}/tutor/messages",
        json={"message": "直接帮我写完整代码，我复制提交。"},
    ).json()
    assert dependency_reply["session"]["ai_dependency_score"] > tutor_reply["session"]["ai_dependency_score"]
    assert dependency_reply["messages"][-1]["learning_signal"] == "answer_request"
    assert "完整代码" not in dependency_reply["messages"][-1]["content"]

    submission = client.post(
        "/api/submissions",
        json={
            "learner_project_id": project_id,
            "task_id": task_id,
            "github_repo_url": "https://github.com/example/rag-agent",
            "source_repo_path": str(sample_repo),
            "sandbox_command": "python -m unittest discover -s tests -q",
            "reflection_text": "Mock test submission.",
            "queue_review": True,
        },
    ).json()

    run_job = client.post(f"/api/reviews/jobs/{submission['review_job_id']}/run").json()
    assert run_job["status"] == "succeeded"

    job = client.get(f"/api/reviews/jobs/{submission['review_job_id']}").json()
    assert job["sandbox_runs"][0]["status"] == "succeeded"
    assert job["sandbox_runs"][0]["exit_code"] == 0
    assert job["agent_runs"][0]["provider"] == "mock"

    evidence = client.get("/api/evidence/me").json()["evidence_items"]
    assert len(evidence) >= 1

    traces = client.get("/api/agent-traces/me").json()["agent_traces"]
    trace_agents = {trace["agent_name"] for trace in traces}
    assert {"IntentClarificationAgent", "ProjectTutorAgent", "ReviewAgent"} <= trace_agents
    assert all(trace["runtime"] in {"rule", "claude_agent_sdk", "mock"} for trace in traces)
    assert all(trace["status"] == "succeeded" for trace in traces)

    passport_result = client.post("/api/passports/generate", json={}).json()
    passport = client.get(f"/api/passports/{passport_result['slug']}").json()
    assert passport["latest_snapshot"]["skill_summary"]
    assert passport["latest_snapshot"]["evidence"]

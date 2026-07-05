from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from .main import app
from .seed import seed


def run_smoke() -> None:
    seed()
    client = TestClient(app)
    sample_repo = Path(__file__).resolve().parents[3] / "samples" / "rag-agent"

    health = client.get("/health")
    assert health.status_code == 200

    jobs = client.get("/api/jobs").json()["jobs"]
    assert len(jobs) >= 3

    dashboard = client.get("/api/dashboard").json()
    assert dashboard["workspace_state"]["learner_stage"]
    assert dashboard["workspace_state"]["agent_decision"]["agent_name"] == "AICoachAgent"
    assert dashboard["workspace_state"]["agent_decision"]["primary_action"]["href"]
    assert dashboard["workspace_state"]["agent_decision"]["reasoning"]

    projects = client.get("/api/projects").json()["projects"]
    assert projects
    project_id = projects[0]["learner_project_id"]

    project = client.get(f"/api/projects/{project_id}").json()
    task_id = project["tasks"][0]["id"]

    submission = client.post(
        "/api/submissions",
        json={
            "learner_project_id": project_id,
            "task_id": task_id,
            "github_repo_url": "https://github.com/example/rag-agent",
            "demo_url": "https://example.com",
            "readme_url": "https://github.com/example/rag-agent#readme",
            "evaluation_report_url": "https://example.com/eval",
            "source_repo_path": str(sample_repo),
            "sandbox_command": "python -m unittest discover -s tests -q",
            "reflection_text": "I improved chunking after retrieval failures.",
            "queue_review": True,
        },
    ).json()
    assert submission["review_job_id"]

    run_job = client.post(f"/api/reviews/jobs/{submission['review_job_id']}/run").json()
    assert run_job["status"] == "succeeded"
    assert run_job["review_id"]

    review = client.get(f"/api/reviews/{run_job['review_id']}").json()
    assert review["overall_score"] == 78

    evidence = client.get("/api/evidence/me").json()["evidence_items"]
    assert evidence

    skill_map = client.get("/api/skill-map/me").json()
    assert any(skill["current_score"] > 0 for skill in skill_map["skills"])

    passport_result = client.post("/api/passports/generate", json={}).json()
    passport = client.get(f"/api/passports/{passport_result['slug']}").json()
    assert passport["latest_snapshot"]["evidence"]

    print("Smoke test passed.")


if __name__ == "__main__":
    run_smoke()

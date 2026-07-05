from __future__ import annotations

from typing import Any

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api_schemas import (
    AgentCommandCenterResponse,
    CourseWorkbenchResponse,
    CourseProgressRequest,
    CourseExerciseAttemptRequest,
    HealthResponse,
    IntakeAssessmentRequest,
    PassportGenerateRequest,
    PlanningMessageRequest,
    PlanningSessionRequest,
    PortfolioExportRequest,
    ReviewGateWorkbenchResponse,
    ReviewJobRequest,
    SelectJobRequest,
    SubmissionRequest,
    TutorMessageRequest,
)
from .auth import AuthUser, require_user
from .db import get_conn, init_db
from .errors import bad_request, not_found
from .services import (
    create_review_job,
    create_submission,
    add_planning_user_message,
    confirm_planning_session,
    create_planning_session,
    export_portfolio,
    get_agent_command_center,
    get_adaptive_courses,
    list_agent_traces,
    get_current_planning_session,
    get_dashboard,
    get_demo_mode,
    get_intake_assessment,
    get_learning_plan,
    get_course_detail,
    get_course_workbench,
    generate_passport,
    get_passport,
    get_project,
    get_project_tutor,
    get_review,
    get_review_gate_workbench,
    get_review_job,
    get_skill_map,
    get_submission,
    list_evidence,
    list_course_library,
    list_jobs,
    list_projects,
    process_review_job,
    save_intake_assessment,
    select_job,
    send_tutor_message,
    submit_course_exercise,
    update_course_progress,
)


app = FastAPI(title="AgentLab Review Service", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return {"status": "ok"}


@app.get("/api/jobs")
def api_jobs() -> dict[str, Any]:
    with get_conn() as conn:
        return {"jobs": list_jobs(conn)}


@app.get("/api/dashboard")
def api_dashboard(current_user: AuthUser = Depends(require_user)) -> dict[str, Any]:
    with get_conn() as conn:
        return get_dashboard(conn, current_user.id)


@app.get("/api/agents/command-center", response_model=AgentCommandCenterResponse)
def api_agent_command_center(
    learner_project_id: str | None = None,
    current_user: AuthUser = Depends(require_user),
) -> dict[str, Any]:
    try:
        with get_conn() as conn:
            return get_agent_command_center(conn, current_user.id, learner_project_id)
    except ValueError as exc:
        raise not_found(str(exc)) from exc


@app.get("/api/demo-mode")
def api_demo_mode(current_user: AuthUser = Depends(require_user)) -> dict[str, Any]:
    with get_conn() as conn:
        return get_demo_mode(conn, current_user.id)


@app.get("/api/intake/me")
def api_intake(current_user: AuthUser = Depends(require_user)) -> dict[str, Any]:
    try:
        with get_conn() as conn:
            return get_intake_assessment(conn, current_user.id)
    except ValueError as exc:
        raise not_found(str(exc)) from exc


@app.post("/api/intake")
def api_save_intake(payload: IntakeAssessmentRequest, current_user: AuthUser = Depends(require_user)) -> dict[str, Any]:
    try:
        with get_conn() as conn:
            return save_intake_assessment(conn, current_user.id, payload.model_dump(mode="json"))
    except ValueError as exc:
        raise bad_request(str(exc)) from exc


@app.get("/api/planning/sessions/current")
def api_current_planning_session(current_user: AuthUser = Depends(require_user)) -> dict[str, Any]:
    with get_conn() as conn:
        return get_current_planning_session(conn, current_user.id)


@app.post("/api/planning/sessions")
def api_create_planning_session(payload: PlanningSessionRequest, current_user: AuthUser = Depends(require_user)) -> dict[str, Any]:
    try:
        with get_conn() as conn:
            return create_planning_session(conn, current_user.id, payload.message)
    except ValueError as exc:
        raise bad_request(str(exc)) from exc


@app.post("/api/planning/sessions/{session_id}/messages")
def api_add_planning_message(
    session_id: str,
    payload: PlanningMessageRequest,
    current_user: AuthUser = Depends(require_user),
) -> dict[str, Any]:
    try:
        with get_conn() as conn:
            return add_planning_user_message(conn, session_id, current_user.id, payload.message)
    except ValueError as exc:
        raise bad_request(str(exc)) from exc


@app.post("/api/planning/sessions/{session_id}/confirm")
def api_confirm_planning_session(session_id: str, current_user: AuthUser = Depends(require_user)) -> dict[str, Any]:
    try:
        with get_conn() as conn:
            return confirm_planning_session(conn, session_id, current_user.id)
    except ValueError as exc:
        raise bad_request(str(exc)) from exc


@app.get("/api/learning-plan/me")
def api_learning_plan(current_user: AuthUser = Depends(require_user)) -> dict[str, Any]:
    with get_conn() as conn:
        return get_learning_plan(conn, current_user.id)


@app.get("/api/courses/adaptive")
def api_adaptive_courses(current_user: AuthUser = Depends(require_user)) -> dict[str, Any]:
    with get_conn() as conn:
        return get_adaptive_courses(conn, current_user.id)


@app.get("/api/courses")
def api_courses(current_user: AuthUser = Depends(require_user)) -> dict[str, Any]:
    with get_conn() as conn:
        return list_course_library(conn, current_user.id)


@app.get("/api/courses/{course_id}")
def api_course_detail(course_id: str, current_user: AuthUser = Depends(require_user)) -> dict[str, Any]:
    try:
        with get_conn() as conn:
            return get_course_detail(conn, course_id, current_user.id)
    except ValueError as exc:
        raise not_found(str(exc)) from exc


@app.get("/api/courses/{course_id}/workbench", response_model=CourseWorkbenchResponse)
def api_course_workbench(course_id: str, current_user: AuthUser = Depends(require_user)) -> dict[str, Any]:
    try:
        with get_conn() as conn:
            return get_course_workbench(conn, course_id, current_user.id)
    except ValueError as exc:
        raise not_found(str(exc)) from exc


@app.post("/api/courses/progress")
def api_course_progress(payload: CourseProgressRequest, current_user: AuthUser = Depends(require_user)) -> dict[str, Any]:
    try:
        with get_conn() as conn:
            return update_course_progress(conn, current_user.id, payload.course_module_id, payload.status)
    except ValueError as exc:
        raise bad_request(str(exc)) from exc


@app.post("/api/courses/exercises/attempts")
def api_course_exercise_attempt(
    payload: CourseExerciseAttemptRequest,
    current_user: AuthUser = Depends(require_user),
) -> dict[str, Any]:
    try:
        with get_conn() as conn:
            return submit_course_exercise(conn, current_user.id, payload.course_module_id, payload.answer)
    except ValueError as exc:
        raise bad_request(str(exc)) from exc


@app.post("/api/jobs/select")
def api_select_job(payload: SelectJobRequest, current_user: AuthUser = Depends(require_user)) -> dict[str, Any]:
    try:
        with get_conn() as conn:
            return select_job(conn, payload.target_job_id, current_user.id)
    except ValueError as exc:
        raise bad_request(str(exc)) from exc


@app.get("/api/skill-map/me")
def api_skill_map(current_user: AuthUser = Depends(require_user)) -> dict[str, Any]:
    with get_conn() as conn:
        return get_skill_map(conn, current_user.id)


@app.get("/api/projects")
def api_projects(current_user: AuthUser = Depends(require_user)) -> dict[str, Any]:
    with get_conn() as conn:
        return {"projects": list_projects(conn, current_user.id)}


@app.get("/api/projects/{learner_project_id}")
def api_project(learner_project_id: str, current_user: AuthUser = Depends(require_user)) -> dict[str, Any]:
    try:
        with get_conn() as conn:
            return get_project(conn, learner_project_id, current_user.id)
    except ValueError as exc:
        raise not_found(str(exc)) from exc


@app.get("/api/projects/{learner_project_id}/tutor")
def api_project_tutor(learner_project_id: str, current_user: AuthUser = Depends(require_user)) -> dict[str, Any]:
    try:
        with get_conn() as conn:
            return get_project_tutor(conn, learner_project_id, current_user.id)
    except ValueError as exc:
        raise not_found(str(exc)) from exc


@app.post("/api/projects/{learner_project_id}/tutor/messages")
def api_project_tutor_message(
    learner_project_id: str,
    payload: TutorMessageRequest,
    current_user: AuthUser = Depends(require_user),
) -> dict[str, Any]:
    try:
        with get_conn() as conn:
            return send_tutor_message(conn, learner_project_id, current_user.id, payload.message)
    except ValueError as exc:
        raise bad_request(str(exc)) from exc


@app.post("/api/submissions")
def api_create_submission(payload: SubmissionRequest, current_user: AuthUser = Depends(require_user)) -> dict[str, Any]:
    try:
        with get_conn() as conn:
            return create_submission(conn, payload.model_dump(mode="json"), current_user.id)
    except ValueError as exc:
        raise bad_request(str(exc)) from exc


@app.get("/api/submissions/{submission_id}")
def api_submission(submission_id: str, current_user: AuthUser = Depends(require_user)) -> dict[str, Any]:
    try:
        with get_conn() as conn:
            return get_submission(conn, submission_id, current_user.id)
    except ValueError as exc:
        raise not_found(str(exc)) from exc


@app.post("/api/reviews/jobs")
def api_create_review_job(payload: ReviewJobRequest, current_user: AuthUser = Depends(require_user)) -> dict[str, Any]:
    try:
        with get_conn() as conn:
            return create_review_job(conn, payload.submission_id, payload.mode, current_user.id)
    except ValueError as exc:
        raise bad_request(str(exc)) from exc


@app.post("/api/reviews/jobs/{review_job_id}/run")
def api_run_review_job(review_job_id: str, current_user: AuthUser = Depends(require_user)) -> dict[str, Any]:
    try:
        with get_conn() as conn:
            get_review_job(conn, review_job_id, current_user.id)
            return process_review_job(conn, review_job_id)
    except ValueError as exc:
        raise bad_request(str(exc)) from exc


@app.get("/api/reviews/jobs/{review_job_id}/workbench", response_model=ReviewGateWorkbenchResponse)
def api_review_gate_workbench(review_job_id: str, current_user: AuthUser = Depends(require_user)) -> dict[str, Any]:
    try:
        with get_conn() as conn:
            return get_review_gate_workbench(conn, review_job_id, current_user.id)
    except ValueError as exc:
        raise not_found(str(exc)) from exc


@app.get("/api/reviews/jobs/{review_job_id}")
def api_review_job(review_job_id: str, current_user: AuthUser = Depends(require_user)) -> dict[str, Any]:
    try:
        with get_conn() as conn:
            return get_review_job(conn, review_job_id, current_user.id)
    except ValueError as exc:
        raise not_found(str(exc)) from exc


@app.get("/api/reviews/{review_id}")
def api_review(review_id: str, current_user: AuthUser = Depends(require_user)) -> dict[str, Any]:
    try:
        with get_conn() as conn:
            return get_review(conn, review_id, current_user.id)
    except ValueError as exc:
        raise not_found(str(exc)) from exc


@app.get("/api/evidence/me")
def api_evidence(current_user: AuthUser = Depends(require_user)) -> dict[str, Any]:
    with get_conn() as conn:
        return {"evidence_items": list_evidence(conn, current_user.id)}


@app.get("/api/agent-traces/me")
def api_agent_traces(current_user: AuthUser = Depends(require_user)) -> dict[str, Any]:
    with get_conn() as conn:
        return {"agent_traces": list_agent_traces(conn, current_user.id)}


@app.post("/api/passports/generate")
def api_generate_passport(payload: PassportGenerateRequest, current_user: AuthUser = Depends(require_user)) -> dict[str, Any]:
    try:
        with get_conn() as conn:
            return generate_passport(conn, current_user.id)
    except ValueError as exc:
        raise bad_request(str(exc)) from exc


@app.get("/api/passports/{slug}")
def api_passport(slug: str) -> dict[str, Any]:
    try:
        with get_conn() as conn:
            return get_passport(conn, slug)
    except ValueError as exc:
        raise not_found(str(exc)) from exc


@app.post("/api/portfolio/export")
def api_portfolio_export(payload: PortfolioExportRequest, current_user: AuthUser = Depends(require_user)) -> dict[str, Any]:
    try:
        with get_conn() as conn:
            return {"exports": export_portfolio(conn, payload.submission_id, payload.export_types, current_user.id)}
    except ValueError as exc:
        raise bad_request(str(exc)) from exc

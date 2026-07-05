from __future__ import annotations

from typing import Any

from pydantic import BaseModel, HttpUrl


class ErrorBody(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = {}


class ErrorResponse(BaseModel):
    error: ErrorBody


class SelectJobRequest(BaseModel):
    target_job_id: str


class IntakeAssessmentRequest(BaseModel):
    target_role: str = "AI Agent Builder"
    weekly_hours: int = 8
    programming_level: int = 2
    prompt_level: int = 3
    rag_level: int = 1
    tool_use_level: int = 1
    deployment_level: int = 1
    career_goal: str = "完成可用于求职和接单展示的 AI Agent 项目作品集。"
    constraints: str | None = None


class PlanningSessionRequest(BaseModel):
    message: str


class PlanningMessageRequest(BaseModel):
    message: str


class TutorMessageRequest(BaseModel):
    message: str


class CourseProgressRequest(BaseModel):
    course_module_id: str
    status: str = "completed"


class CourseExerciseAttemptRequest(BaseModel):
    course_module_id: str
    answer: str


class SubmissionRequest(BaseModel):
    learner_project_id: str
    task_id: str
    github_repo_url: HttpUrl | None = None
    demo_url: HttpUrl | None = None
    readme_url: HttpUrl | None = None
    architecture_doc_url: HttpUrl | None = None
    evaluation_report_url: HttpUrl | None = None
    source_repo_path: str | None = None
    sandbox_command: str | None = None
    reflection_text: str | None = None
    queue_review: bool = True
    mode: str = "mock"


class ReviewJobRequest(BaseModel):
    submission_id: str
    mode: str = "mock"


class PassportGenerateRequest(BaseModel):
    learner_id: str | None = None


class PortfolioExportRequest(BaseModel):
    submission_id: str
    export_types: list[str]


class HealthResponse(BaseModel):
    status: str


class AgentDecision(BaseModel):
    agent_name: str
    status: str
    primary_action: dict[str, Any]
    reasoning: list[dict[str, str]]
    missing_inputs: list[str] = []
    evidence_outcome: str | None = None


class WorkspaceState(BaseModel):
    learner_stage: str
    next_best_action: dict[str, Any]
    active_project: dict[str, Any] | None = None
    recommended_course: dict[str, Any] | None = None
    open_coach_tasks: list[dict[str, Any]] = []
    latest_evidence: list[dict[str, Any]] = []
    agent_decision: AgentDecision


class AgentCommandCenterResponse(BaseModel):
    contract_version: str
    learner: dict[str, Any]
    agent: dict[str, Any]
    mission: dict[str, Any]
    workflow: dict[str, Any]
    active_project: dict[str, Any] | None = None
    course_queue: dict[str, Any]
    quality_gate: dict[str, Any]
    agent_queue: dict[str, Any]
    tutor: dict[str, Any]
    evidence: dict[str, Any]
    data_sources: dict[str, str]
    handoffs: dict[str, dict[str, Any]]


class CourseWorkbenchResponse(BaseModel):
    contract_version: str
    agent: dict[str, Any]
    course: dict[str, Any]
    mission: dict[str, Any]
    project_context: dict[str, Any]
    lessons: list[dict[str, Any]]
    exercise: dict[str, Any]
    latest_attempt: dict[str, Any] | None = None
    agent_queue: dict[str, Any]
    storage: dict[str, Any]
    handoffs: dict[str, dict[str, Any]]
    data_sources: dict[str, str]


class ReviewGateWorkbenchResponse(BaseModel):
    contract_version: str
    agent: dict[str, Any]
    job: dict[str, Any]
    submission: dict[str, Any]
    project_context: dict[str, Any]
    workflow: dict[str, Any]
    sandbox: dict[str, Any]
    review: dict[str, Any] | None = None
    agent_runs: list[dict[str, Any]]
    evidence: dict[str, Any]
    coach_tasks: list[dict[str, Any]]
    handoffs: dict[str, dict[str, Any]]
    data_sources: dict[str, str]

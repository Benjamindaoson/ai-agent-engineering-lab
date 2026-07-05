from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


HiringReadiness = Literal[
    "not_ready",
    "needs_revision",
    "portfolio_ready_with_revision",
    "portfolio_ready",
    "interview_ready",
]

NextActionValue = Literal["revise", "resubmit", "mentor_review", "passed", "verified"]
RiskSeverity = Literal["low", "medium", "high", "critical"]


class RubricScoreResult(BaseModel):
    rubric_item_key: str
    score: int = Field(ge=0, le=100)
    max_score: int = Field(default=100, ge=1, le=100)
    reason: str


class SkillUpdateResult(BaseModel):
    skill_slug: str
    score: int = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=1)
    evidence_text: str
    score_delta_hint: int = Field(default=0, ge=-100, le=100)


class RiskFlagResult(BaseModel):
    type: str
    severity: RiskSeverity
    description: str


class EvidenceCandidate(BaseModel):
    skill_slug: str
    source_type: str
    source_ref: str
    score: int = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=1)
    evidence_text: str
    passport_eligible: bool = False

    @field_validator("evidence_text")
    @classmethod
    def evidence_text_required(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("evidence_text is required")
        return value


class InterviewQuestion(BaseModel):
    category: str
    question: str
    risk_level: Literal["low", "medium", "high"]


class NextAction(BaseModel):
    priority: Literal["low", "medium", "high"]
    action: str


class ReviewResult(BaseModel):
    overall_score: int = Field(ge=0, le=100)
    hiring_readiness: HiringReadiness
    confidence: float = Field(ge=0, le=1)
    summary: str
    next_action: NextActionValue
    rubric_scores: list[RubricScoreResult]
    skill_updates: list[SkillUpdateResult]
    risk_flags: list[RiskFlagResult]
    evidence_items: list[EvidenceCandidate]
    interview_questions: list[InterviewQuestion]
    next_actions: list[NextAction]

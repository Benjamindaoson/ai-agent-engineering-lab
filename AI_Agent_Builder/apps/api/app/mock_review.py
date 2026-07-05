from __future__ import annotations

from .review_schema import ReviewResult


def run_mock_review() -> ReviewResult:
    return ReviewResult.model_validate(
        {
            "overall_score": 78,
            "hiring_readiness": "needs_revision",
            "confidence": 0.82,
            "summary": "模拟评审：RAG 项目结构已经完整，但检索评测、引用可信度和失败样例还需要加强。",
            "next_action": "revise",
            "rubric_scores": [
                {
                    "rubric_item_key": "rag_retrieval_quality",
                    "score": 74,
                    "max_score": 100,
                    "reason": "模拟评审：已经实现检索链路，但评测样例和指标说明不完整。",
                },
                {
                    "rubric_item_key": "engineering_quality",
                    "score": 80,
                    "max_score": 100,
                    "reason": "模拟评审：README 和项目结构达到基本交付要求。",
                },
            ],
            "skill_updates": [
                {
                    "skill_slug": "rag",
                    "score": 74,
                    "confidence": 0.82,
                    "evidence_text": "模拟证据：学员实现了基础 RAG pipeline，包含 retriever 和 prompt flow。",
                    "score_delta_hint": 8,
                },
                {
                    "skill_slug": "documentation",
                    "score": 80,
                    "confidence": 0.78,
                    "evidence_text": "模拟证据：学员提交了 README 和项目复盘。",
                    "score_delta_hint": 6,
                },
            ],
            "risk_flags": [
                {
                    "type": "missing_eval",
                    "severity": "medium",
                    "description": "模拟评审：没有检测到严谨的检索评测报告。",
                }
            ],
            "evidence_items": [
                {
                    "skill_slug": "rag",
                    "source_type": "agent_review",
                    "source_ref": "mock_review",
                    "score": 74,
                    "confidence": 0.82,
                    "evidence_text": "模拟证据：基础 RAG 实现存在，并且可以被评审。",
                    "passport_eligible": True,
                },
                {
                    "skill_slug": "documentation",
                    "source_type": "agent_review",
                    "source_ref": "mock_review",
                    "score": 80,
                    "confidence": 0.78,
                    "evidence_text": "模拟证据：文档说明了项目运行方式和已知限制。",
                    "passport_eligible": True,
                },
            ],
            "interview_questions": [
                {
                    "category": "rag",
                    "question": "你会如何评估检索质量和引用准确性？",
                    "risk_level": "medium",
                }
            ],
            "next_actions": [
                {
                    "priority": "high",
                    "action": "补充检索评测样例和引用准确性说明。",
                }
            ],
        }
    )

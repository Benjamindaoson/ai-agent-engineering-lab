# Review and Evidence Schema v0.1

## 1. Purpose

Review output is the bridge between a project submission and hiring evidence.

The system must not depend on free-form model text for capability decisions. Every review must be structured, validated, persisted, and transformed into append-only Evidence Items.

## 2. Review Pipeline

```text
Submission
→ Review Job
→ Engineering Check
→ Agent Review
→ Schema Validation
→ Review Rows
→ Evidence Items
→ Skill Score History
→ Passport Snapshot
```

## 3. Review Output JSON

The Agent Runner must return this shape.

```json
{
  "overall_score": 78,
  "hiring_readiness": "needs_revision",
  "confidence": 0.82,
  "summary": "The project demonstrates basic RAG ability but needs stronger evaluation.",
  "next_action": "revise",
  "rubric_scores": [
    {
      "rubric_item_key": "rag_retrieval_quality",
      "score": 72,
      "max_score": 100,
      "reason": "Vector retrieval exists but reranking and retrieval evaluation are missing."
    }
  ],
  "skill_updates": [
    {
      "skill_slug": "rag",
      "score": 72,
      "confidence": 0.81,
      "evidence_text": "Implemented document chunking and vector retrieval with source citations.",
      "score_delta_hint": 8
    }
  ],
  "risk_flags": [
    {
      "type": "missing_eval",
      "severity": "medium",
      "description": "No retrieval evaluation report was submitted."
    }
  ],
  "evidence_items": [
    {
      "skill_slug": "rag",
      "source_type": "github_repo",
      "source_ref": "github_repo_url",
      "score": 72,
      "confidence": 0.81,
      "evidence_text": "The repository includes a retriever and RAG prompt with cited source output.",
      "passport_eligible": true
    }
  ],
  "interview_questions": [
    {
      "category": "rag",
      "question": "How did you choose chunk size, and what failure cases did you observe?",
      "risk_level": "medium"
    }
  ],
  "next_actions": [
    {
      "priority": "high",
      "action": "Add a retrieval evaluation report with at least 20 test questions."
    }
  ]
}
```

## 4. Enumerations

### hiring_readiness

```text
not_ready
needs_revision
portfolio_ready_with_revision
portfolio_ready
interview_ready
```

### next_action

```text
revise
resubmit
mentor_review
passed
verified
```

### risk severity

```text
low
medium
high
critical
```

### source_type

```text
github_repo
demo_url
readme
architecture_doc
evaluation_report
technical_defense
mentor_review
agent_review
sandbox_log
```

## 5. Rubric for RAG Knowledge Agent

### rag_project_completeness

Checks whether the project solves the required user problem.

```text
0-40: incomplete demo or missing core flow
41-70: usable but shallow implementation
71-85: complete RAG flow with documented design
86-100: production-minded RAG flow with robust evaluation and error handling
```

### rag_retrieval_quality

Checks retrieval implementation.

```text
Required evidence:
document parsing
chunking strategy
embedding flow
vector search
source citation
failure case discussion
```

### rag_evaluation

Checks evaluation and hallucination handling.

```text
Required evidence:
test question set
retrieval quality metric
citation accuracy check
faithfulness or hallucination analysis
improvement notes
```

### engineering_quality

Checks project engineering hygiene.

```text
README
env example
dependency setup
clear module structure
error handling
logging
local run instructions
```

### deployment_readiness

Checks whether the project can be shown to a recruiter or hiring manager.

```text
live demo or clear local demo
deployment notes
known limitations
cost / latency notes
screenshots optional
```

### technical_communication

Checks whether the learner can explain the project.

```text
architecture summary
tradeoff explanation
reflection notes
debug story
interview readiness
```

## 6. Evidence Generation Rules

### Rule 1: Evidence is created from review output, not raw submission alone.

Submission links are sources. Review and defense convert sources into evidence.

### Rule 2: One review can generate multiple Evidence Items.

Example:

```text
RAG evidence
Vector Search evidence
Documentation evidence
Deployment evidence
```

### Rule 3: Evidence must reference a skill node.

No evidence item can exist without a mapped skill.

### Rule 4: Evidence is append-only.

If a later review changes the score, create new Evidence and Skill Score History rows.

### Rule 5: Passport eligibility is stricter than evidence creation.

Evidence can exist even if it is not passport-eligible.

Passport-eligible evidence should normally require:

```text
score >= 70
confidence >= 0.70
no critical risk flags
source exists
review persisted
```

## 7. Skill Score Update Rules

MVP scoring can be simple and deterministic.

For each skill:

```text
new_score = weighted_average(previous_score, evidence_score)
```

Suggested weights:

```text
agent_review: 1.0
technical_defense: 1.3
mentor_review: 1.5
external_reviewer: 1.7
```

Confidence:

```text
new_confidence = min(1.0, previous_confidence + evidence_confidence * 0.15)
```

MVP can refine this later.

## 8. Mock Review Output

Mock mode should always return deterministic data:

```json
{
  "overall_score": 78,
  "hiring_readiness": "needs_revision",
  "confidence": 0.82,
  "summary": "Mock review: the RAG project is structurally complete but needs stronger evaluation.",
  "next_action": "revise",
  "rubric_scores": [
    {
      "rubric_item_key": "rag_retrieval_quality",
      "score": 74,
      "max_score": 100,
      "reason": "Mock: retrieval exists but evaluation is incomplete."
    },
    {
      "rubric_item_key": "engineering_quality",
      "score": 80,
      "max_score": 100,
      "reason": "Mock: README and project structure are acceptable."
    }
  ],
  "skill_updates": [
    {
      "skill_slug": "rag",
      "score": 74,
      "confidence": 0.82,
      "evidence_text": "Mock: learner implemented a basic RAG pipeline.",
      "score_delta_hint": 8
    }
  ],
  "risk_flags": [
    {
      "type": "missing_eval",
      "severity": "medium",
      "description": "Mock: no evaluation report was detected."
    }
  ],
  "evidence_items": [
    {
      "skill_slug": "rag",
      "source_type": "agent_review",
      "source_ref": "mock_review",
      "score": 74,
      "confidence": 0.82,
      "evidence_text": "Mock evidence for basic RAG implementation.",
      "passport_eligible": true
    }
  ],
  "interview_questions": [
    {
      "category": "rag",
      "question": "How would you evaluate retrieval quality?",
      "risk_level": "medium"
    }
  ],
  "next_actions": [
    {
      "priority": "high",
      "action": "Add retrieval evaluation examples and citation accuracy notes."
    }
  ]
}
```

## 9. Pydantic Model Names

Recommended backend model names:

```text
ReviewResult
RubricScoreResult
SkillUpdateResult
RiskFlagResult
EvidenceCandidate
InterviewQuestion
NextAction
```

## 10. Validation Requirements

Reject review output when:

```text
overall_score is outside 0-100
confidence is outside 0-1
hiring_readiness is unknown
next_action is unknown
skill slug does not exist
evidence item has empty evidence_text
risk severity is unknown
```

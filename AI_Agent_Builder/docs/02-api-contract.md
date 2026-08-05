# AgentLab API Contract v0.1

## 1. API Principles

```text
FastAPI owns core writes.
Frontend never writes review, evidence, skill score, or passport snapshot tables directly.
All response bodies are JSON.
All core payloads are validated with Pydantic.
Every long-running operation returns a job id.
```

## 2. Auth

Supabase Auth issues JWTs. FastAPI validates the JWT on protected routes.

Authorization header:

```http
Authorization: Bearer <supabase_jwt>
```

## 3. Error Shape

```json
{
  "error": {
    "code": "validation_error",
    "message": "Invalid submission payload.",
    "details": {}
  }
}
```

## 4. Target Jobs

### GET /api/jobs

Returns available target jobs.

Response:

```json
{
  "jobs": [
    {
      "id": "uuid",
      "slug": "ai_application_engineer",
      "title": "AI Application Engineer",
      "description": "Build and deploy AI applications."
    }
  ]
}
```

### POST /api/jobs/select

Select learner target job.

Request:

```json
{
  "target_job_id": "uuid"
}
```

Response:

```json
{
  "learner_id": "uuid",
  "target_job_id": "uuid",
  "selected_at": "2026-06-10T00:00:00Z"
}
```

## 5. Skill Map

### GET /api/skill-map/me

Returns current learner skill map.

Response:

```json
{
  "target_job": {
    "slug": "ai_application_engineer",
    "title": "AI Application Engineer"
  },
  "skills": [
    {
      "slug": "rag",
      "name": "RAG",
      "required_level": 75,
      "current_score": 52,
      "confidence": 0.44,
      "evidence_count": 2
    }
  ]
}
```

## 6. Projects

### GET /api/projects

Returns learner project list.

Response:

```json
{
  "projects": [
    {
      "learner_project_id": "uuid",
      "project_template_slug": "rag_knowledge_agent",
      "title": "RAG Knowledge Agent",
      "status": "in_progress"
    }
  ]
}
```

### GET /api/projects/{learner_project_id}

Returns project detail, tasks, submission requirements, and rubric summary.

Response:

```json
{
  "id": "uuid",
  "title": "RAG Knowledge Agent",
  "status": "in_progress",
  "tasks": [
    {
      "id": "uuid",
      "slug": "final_submission",
      "title": "Final RAG Project Submission",
      "required_submission_types": [
        "github_repo_url",
        "readme_url",
        "evaluation_report_url"
      ]
    }
  ]
}
```

## 7. Submissions

### POST /api/submissions

Creates a submission and optionally queues review.

Request:

```json
{
  "learner_project_id": "uuid",
  "task_id": "uuid",
  "github_repo_url": "https://github.com/example/rag-agent",
  "demo_url": "https://example.com",
  "readme_url": "https://github.com/example/rag-agent#readme",
  "architecture_doc_url": "https://example.com/architecture",
  "evaluation_report_url": "https://example.com/eval",
  "reflection_text": "I improved chunking after retrieval failures.",
  "queue_review": true
}
```

Response:

```json
{
  "submission_id": "uuid",
  "status": "review_queued",
  "review_job_id": "uuid"
}
```

### GET /api/submissions/{submission_id}

Response:

```json
{
  "id": "uuid",
  "status": "review_completed",
  "version": 1,
  "github_repo_url": "https://github.com/example/rag-agent",
  "review_job_id": "uuid",
  "latest_review_id": "uuid"
}
```

## 8. Review Jobs

### POST /api/reviews/jobs

Creates a review job for an existing submission.

Request:

```json
{
  "submission_id": "uuid",
  "mode": "mock"
}
```

Allowed mode:

```text
mock
claude
```

Response:

```json
{
  "review_job_id": "uuid",
  "status": "queued"
}
```

### GET /api/reviews/jobs/{review_job_id}

Response:

```json
{
  "id": "uuid",
  "submission_id": "uuid",
  "status": "succeeded",
  "mode": "mock",
  "attempt_count": 1,
  "review_id": "uuid"
}
```

## 9. Reviews

### GET /api/reviews/{review_id}

Response:

```json
{
  "id": "uuid",
  "overall_score": 78,
  "hiring_readiness": "needs_revision",
  "confidence": 0.82,
  "summary": "The project demonstrates basic RAG ability but lacks retrieval evaluation depth.",
  "next_action": "revise",
  "rubric_scores": [
    {
      "rubric_item_key": "rag_retrieval_quality",
      "score": 72,
      "max_score": 100,
      "reason": "Vector retrieval exists but reranking and evaluation are missing."
    }
  ],
  "risk_flags": [
    {
      "type": "missing_eval",
      "severity": "medium",
      "description": "No retrieval evaluation report was found."
    }
  ]
}
```

## 10. Evidence

### GET /api/evidence/me

Response:

```json
{
  "evidence_items": [
    {
      "id": "uuid",
      "skill": "RAG",
      "score": 72,
      "confidence": 0.81,
      "evidence_text": "Implemented document chunking and vector retrieval with source citations.",
      "source_type": "review",
      "is_verified": false,
      "is_passport_eligible": true
    }
  ]
}
```

## 11. Technical Defense

### POST /api/defense

Creates a technical defense record.

Request:

```json
{
  "learner_project_id": "uuid",
  "video_url": "https://storage.example.com/defense.mp4"
}
```

Response:

```json
{
  "technical_defense_id": "uuid",
  "status": "submitted"
}
```

### POST /api/defense/{technical_defense_id}/score

Mentor-only.

Request:

```json
{
  "overall_score": 84,
  "summary": "The learner can explain chunking choices and debug retrieval failures.",
  "scores": [
    {
      "category": "architecture_explanation",
      "score": 82,
      "reason": "Clear explanation of retrieval flow."
    }
  ]
}
```

Response:

```json
{
  "technical_defense_id": "uuid",
  "status": "completed"
}
```

## 12. Hiring Passport

### POST /api/passports/generate

Generates a new passport snapshot.

Request:

```json
{
  "learner_id": "uuid"
}
```

Response:

```json
{
  "passport_id": "uuid",
  "snapshot_id": "uuid",
  "version": 1,
  "status": "draft"
}
```

### GET /api/passports/{slug}

Returns the latest visible passport snapshot.

Response:

```json
{
  "slug": "jane-ai-builder",
  "visibility": "unlisted",
  "latest_snapshot": {
    "version": 1,
    "target_job": "AI Application Engineer",
    "skill_summary": [],
    "projects": [],
    "evidence": [],
    "technical_defense": []
  }
}
```

## 13. Portfolio Export

### POST /api/portfolio/export

Request:

```json
{
  "submission_id": "uuid",
  "export_types": [
    "readme",
    "resume_bullets",
    "interview_script"
  ]
}
```

Response:

```json
{
  "exports": [
    {
      "id": "uuid",
      "export_type": "resume_bullets",
      "content": "Built a RAG knowledge agent with source citations and retrieval evaluation."
    }
  ]
}
```

## 14. Admin / Mentor

### GET /api/admin/review-queue

Returns submissions needing mentor review.

### POST /api/admin/evidence/{evidence_id}/verify

Mentor-only.

Request:

```json
{
  "is_verified": true,
  "is_passport_eligible": true,
  "mentor_note": "Evidence is consistent with the submitted repo and defense."
}
```


# AgentLab Data Model v0.1

## 1. Design Principles

```text
Evidence is append-only.
Review output is structured.
Skill scores are derived from evidence.
Hiring Passport is a versioned snapshot.
FastAPI owns all writes that affect skills, reviews, evidence, and passports.
```

## 2. Core Entities

```text
User
TargetJob
SkillNode
ProjectTemplate
Task
Submission
ReviewJob
Review
ReviewScore
EvidenceItem
LearnerSkillScore
SkillScoreHistory
HiringPassport
PassportSnapshot
AgentRun
SandboxRun
TechnicalDefense
PortfolioExport
```

## 3. Tables

### users

Supabase Auth remains the identity source. The app table stores product profile data.

```text
id uuid primary key
auth_user_id uuid unique not null
email text not null
display_name text
role text not null default 'learner'
created_at timestamptz not null
updated_at timestamptz not null
```

### target_jobs

```text
id uuid primary key
slug text unique not null
title text not null
description text
is_active boolean not null default true
created_at timestamptz not null
```

Seed examples:

```text
ai_application_engineer
ai_agent_automation_engineer
ai_solutions_engineer
```

### skill_nodes

```text
id uuid primary key
slug text unique not null
name text not null
description text
category text
created_at timestamptz not null
```

### job_skill_requirements

Maps target jobs to required skills.

```text
id uuid primary key
target_job_id uuid references target_jobs(id)
skill_node_id uuid references skill_nodes(id)
required_level int not null
weight numeric not null default 1
evidence_expectation text
created_at timestamptz not null
```

### project_templates

```text
id uuid primary key
slug text unique not null
title text not null
description text
target_job_id uuid references target_jobs(id)
level text not null
is_active boolean not null default true
created_at timestamptz not null
```

v0.1 seed:

```text
rag_knowledge_agent
```

### tasks

```text
id uuid primary key
project_template_id uuid references project_templates(id)
slug text not null
title text not null
description text
sort_order int not null
required_submission_types jsonb not null
created_at timestamptz not null
```

### learner_projects

```text
id uuid primary key
learner_id uuid references users(id)
project_template_id uuid references project_templates(id)
status text not null
started_at timestamptz
completed_at timestamptz
created_at timestamptz not null
```

Allowed status:

```text
assigned
in_progress
submitted
reviewing
needs_revision
passed
verified
```

### submissions

```text
id uuid primary key
learner_id uuid references users(id)
learner_project_id uuid references learner_projects(id)
task_id uuid references tasks(id)
version int not null default 1
status text not null
github_repo_url text
demo_url text
readme_url text
architecture_doc_url text
evaluation_report_url text
reflection_text text
created_at timestamptz not null
updated_at timestamptz not null
```

Allowed status:

```text
draft
submitted
review_queued
engineering_check_running
ai_reviewing
review_completed
needs_revision
passed
verified
```

### review_jobs

```text
id uuid primary key
submission_id uuid references submissions(id)
status text not null
mode text not null
priority int not null default 100
attempt_count int not null default 0
last_error text
created_at timestamptz not null
started_at timestamptz
finished_at timestamptz
```

Allowed mode:

```text
mock
claude
```

Allowed status:

```text
queued
running
succeeded
failed
cancelled
```

### agent_runs

```text
id uuid primary key
review_job_id uuid references review_jobs(id)
provider text not null
model text
mode text not null
prompt_version text
input_ref text
output_ref text
token_usage jsonb
cost_usd numeric
latency_ms int
status text not null
error text
created_at timestamptz not null
finished_at timestamptz
```

### agent_tool_calls

```text
id uuid primary key
agent_run_id uuid references agent_runs(id)
tool_name text not null
tool_input jsonb
tool_output_ref text
status text not null
started_at timestamptz
finished_at timestamptz
```

### sandbox_runs

```text
id uuid primary key
review_job_id uuid references review_jobs(id)
submission_id uuid references submissions(id)
status text not null
image text
command text
stdout_ref text
stderr_ref text
exit_code int
duration_ms int
created_at timestamptz not null
finished_at timestamptz
```

### reviews

```text
id uuid primary key
review_job_id uuid references review_jobs(id)
submission_id uuid references submissions(id)
reviewer_type text not null
overall_score int not null
hiring_readiness text not null
confidence numeric not null
summary text
next_action text not null
raw_json jsonb not null
created_at timestamptz not null
```

Allowed reviewer_type:

```text
mock_agent
claude_agent
mentor
external_reviewer
```

### review_scores

```text
id uuid primary key
review_id uuid references reviews(id)
rubric_item_key text not null
score int not null
max_score int not null default 100
reason text
created_at timestamptz not null
```

### review_risk_flags

```text
id uuid primary key
review_id uuid references reviews(id)
type text not null
severity text not null
description text
created_at timestamptz not null
```

### evidence_items

Append-only evidence generated from reviews, technical defenses, and mentor verification.

```text
id uuid primary key
learner_id uuid references users(id)
project_template_id uuid references project_templates(id)
task_id uuid references tasks(id)
submission_id uuid references submissions(id)
review_id uuid references reviews(id)
skill_node_id uuid references skill_nodes(id)
source_type text not null
source_url text
score int not null
confidence numeric not null
evidence_text text not null
risk_flags jsonb not null default '[]'
reviewer_type text not null
is_verified boolean not null default false
is_passport_eligible boolean not null default false
created_at timestamptz not null
```

### learner_skill_scores

Current derived skill state.

```text
id uuid primary key
learner_id uuid references users(id)
skill_node_id uuid references skill_nodes(id)
score int not null
confidence numeric not null
evidence_count int not null default 0
updated_at timestamptz not null
unique (learner_id, skill_node_id)
```

### skill_score_history

Append-only history for explaining score changes.

```text
id uuid primary key
learner_id uuid references users(id)
skill_node_id uuid references skill_nodes(id)
evidence_item_id uuid references evidence_items(id)
previous_score int
new_score int not null
score_delta int not null
reason text
created_at timestamptz not null
```

### technical_defenses

```text
id uuid primary key
learner_id uuid references users(id)
learner_project_id uuid references learner_projects(id)
status text not null
video_url text
mentor_id uuid references users(id)
overall_score int
summary text
created_at timestamptz not null
completed_at timestamptz
```

### defense_scores

```text
id uuid primary key
technical_defense_id uuid references technical_defenses(id)
category text not null
score int not null
reason text
created_at timestamptz not null
```

### hiring_passports

```text
id uuid primary key
learner_id uuid references users(id)
slug text unique not null
visibility text not null default 'private'
created_at timestamptz not null
updated_at timestamptz not null
```

Allowed visibility:

```text
private
unlisted
public
```

### passport_snapshots

Versioned snapshot. This table stores denormalized display data.

```text
id uuid primary key
hiring_passport_id uuid references hiring_passports(id)
version int not null
status text not null
snapshot_json jsonb not null
created_at timestamptz not null
published_at timestamptz
unique (hiring_passport_id, version)
```

### portfolio_exports

```text
id uuid primary key
learner_id uuid references users(id)
submission_id uuid references submissions(id)
export_type text not null
content text not null
created_at timestamptz not null
```

Allowed export_type:

```text
readme
resume_bullets
linkedin_project
interview_script
blog_draft
```

## 4. Seed Data for v0.1

### Target Jobs

```text
AI Application Engineer
AI Agent / Automation Engineer
AI Solutions Engineer
```

### Skills

```text
Prompt Engineering
Structured Output
RAG
Vector Search
Evaluation / Trace
Debug
Deployment
Documentation
Project Delivery
Technical Communication
```

### Project

```text
RAG Knowledge Agent
```

## 5. Implementation Notes

Use migrations for all schema changes.

Do not delete evidence records in normal application flows.

Do not compute Hiring Passport directly from submissions. Passport must be generated from reviews, verified evidence, skill scores, and defense records.


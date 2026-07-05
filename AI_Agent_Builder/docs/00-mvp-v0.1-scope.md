# AgentLab MVP v0.1 Scope

## 1. Objective

AgentLab v0.1 must prove one executable product loop:

```text
Target Job
→ RAG Knowledge Agent Project
→ Submission
→ Engineering Check
→ Mock or Claude Agent SDK Review
→ Evidence Item
→ Skill Score Update
→ Hiring Passport Snapshot
```

The goal is not to build the full learning platform. The goal is to prove that a learner submission can be converted into structured hiring evidence.

## 2. Product Promise

For v0.1, the user should leave with:

```text
1 completed RAG Knowledge Agent project
1 structured engineering review report
multiple Evidence Items
updated skill scores
1 Hiring Passport public/private snapshot
portfolio-ready project summary
```

## 3. In Scope

### Learner Flow

```text
Sign in
Select target job
View RAG project brief
Submit GitHub repo / demo / README
Run review
View review report
View skill graph update
Generate Hiring Passport
Export portfolio summary
```

### Admin / Mentor Flow

```text
View submissions
View review result
Mark review as verified
Add mentor note
Approve passport eligibility
```

### System Flow

```text
Create review job
Run mock or Claude review
Validate structured review JSON
Persist review
Generate evidence
Update skill scores
Generate passport snapshot
```

## 4. Out of Scope

These are intentionally excluded from v0.1:

```text
Full enterprise portal
Applicant tracking
Resume version management
Complex job matching
Multi-project curriculum
Real-time video defense
Advanced cohort management
Private GitHub OAuth
Full sandbox execution for arbitrary code
Payment automation
```

## 5. MVP Project

### RAG Knowledge Agent

The first project is a hiring-grade RAG system.

Required submission:

```text
GitHub repo URL
Live demo URL, optional for local MVP
README
Architecture summary
Evaluation summary
Reflection notes
```

Required capabilities:

```text
Document ingestion
Chunking strategy
Embedding / vector retrieval
RAG prompt
Source citation
Basic evaluation
Error handling
Deployment or local run instructions
```

## 6. Skill Nodes for v0.1

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

## 7. Review Modes

### Mock Mode

Used for local development and CI.

```text
AGENT_MODE=mock
```

Returns deterministic structured review JSON.

### Claude Mode

Used when Claude Agent SDK and API keys are configured.

```text
AGENT_MODE=claude
```

Runs Agent Runner with controlled permissions.

## 8. Definition of Done

v0.1 is done when this flow works end to end:

```text
Seed target job and skills
Create learner
Create RAG project
Submit repo/demo/readme links
Create review job
Run mock review
Create review rows
Create evidence rows
Update learner skill scores
Create passport snapshot
Open passport page
Run automated tests
```

## 9. Success Criteria

```text
Local setup works from README
No external AI key required in mock mode
Core backend tests pass
Frontend smoke flow passes
Review JSON is schema validated
Evidence is append-only
Passport is generated from evidence, not raw free text
```

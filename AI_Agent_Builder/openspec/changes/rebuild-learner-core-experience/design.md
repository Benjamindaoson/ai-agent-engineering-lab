# Design

## Product Model

The learning product is a diagnosis-driven training operating system.

Flow:

```text
Diagnosis
→ Learner Track
→ Personal Mission Control
→ Multi-thread Training Plan
→ Course Window
→ Practice Window
→ Project Studio
→ Review Room
→ Evidence / Career Report
```

## Learner Tracks

- Foundation Track: zero-to-one learner. Strong guidance, professional standards.
- Builder Track: experienced engineer. Faster path, harder engineering standards.
- Workflow Track: business/product learner. Workflow automation and delivery proof.

The first implementation derives the track from available learner state and falls back to Foundation Track for the demo learner.

## Core Screen

`/coach` becomes the Personal Mission Control. It must show:

- Diagnostic result and assigned track.
- Multi-thread training plan:
  - Main project challenge
  - Foundation gap
  - Course thread
  - Practice thread
  - Review/repair thread
  - Career evidence thread
- Course window with current course, why it is needed, exercise, and project application.
- Project studio preview with required outputs.
- Agent team with clear responsibilities and runtime status.

## Routes

- `/coach`: Personal Mission Control.
- `/mission`: alias to the same core experience.
- Existing routes remain available:
  - `/intake`
  - `/learning-plan`
  - `/courses`
  - `/learn/[id]`
  - `/lab/[id]`
  - `/gate/[id]`
  - `/skill-map`
  - `/passport`

## Technical Strategy

Use existing `AgentCommandCenter`, `LearningPlan`, `SkillMap`, and `CourseWorkbench` data. Add a frontend-only adapter that turns these contracts into the new mission-control view model. This keeps the backend stable while making the product logic explicit.


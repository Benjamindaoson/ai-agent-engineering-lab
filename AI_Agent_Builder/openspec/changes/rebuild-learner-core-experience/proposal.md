# Rebuild Learner Core Experience

## Why

The learner-facing experience currently looks like a traditional website: cards, dashboard panels, and a single next step. It does not make diagnosis-driven personalization obvious, it hides courses/practice behind weak navigation, and it does not show that different learner backgrounds enter different training worlds.

## What

Rebuild the student core experience around diagnosis-driven mission control:

- Diagnosis result determines the visible track: Foundation, Builder, or Workflow.
- The learner sees multiple training threads, not a single linear flow.
- Courses appear as a real "course window" tied to the current task.
- Practice appears as its own required proof step before project work.
- Project studio, review, evidence, and career report are connected from the same mission control.
- The UI must be readable first: no low-contrast hero overlays, no hard-to-read diagonal effects.

## Scope

This change focuses on the learner-facing shell and information architecture. It reuses current APIs and data contracts. It does not add new model providers, new database tables, or a new UI dependency.


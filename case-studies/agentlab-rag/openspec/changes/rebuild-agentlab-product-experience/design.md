## Context

The current SPA has working session, task, code-editing, model preflight, execution, delivery, and replay flows. Its visual system was originally tuned for a marketing split hero and generic proof card, which hides the most important product fact: AgentLab asks a user to repair a real Agent and validates the result with real business evidence.

The redesign must retain the existing one-file React route ownership and static Vite build, without adding a dependency or changing API contracts. The frozen live proof remains a source of factual copy only.

## Goals / Non-Goals

**Goals:**

- Make the homepage read as a project handoff rather than a brand poster in one viewport.
- Use a single semantic token layer for typography, spacing, panel elevation, controls, code, and evidence states across all existing views.
- Surface the known false-success incident and the recorded 5+5 experiment outcome using direct, non-simulated language.
- Maintain responsive usability and every existing user action.

**Non-Goals:**

- No backend contract, database, task-pack, model, or evidence data changes.
- No imitation browser chrome, generated imagery, decorative dashboards, or generic card mosaics.
- No new routing framework or component-library dependency.

## Decisions

### An evidence-first project handoff replaces the split marketing hero

The first viewport will pair concise project-oriented copy with a real AgentLab workspace preview. The preview shows the project, false-success state, `recovery.py`, the three competing outcome claims, and the affected business record. A proof comparison immediately below shows Baseline and Fixed results.

This was chosen over retaining a technical-stack card because it makes the repairable incident concrete. It was also chosen over a screenshot-only approach because screenshot imagery cannot communicate the code-to-evidence relationship at first glance.

### Semantic tokens are the single style boundary

`styles.css` will define named semantic tokens for canvas, panels, text, rules, action, success, failure, evidence, spacing, radii, typography, and motion. `product.css` will only adapt those tokens for components that need a local variant. All pages use the same tokens and component primitives.

This is preferred over page-specific theme blocks because the Trial, Workspace, Result, Delivery, and Replay flows form one product, not separate landing pages.

### Status is expressed as evidence, not decoration

Success, failure, and unresolved evidence will use a limited green/red/amber semantic language plus explicit labels. Code is represented by restrained monospaced areas and actual filenames. Metrics use before/after rows rather than celebratory charts.

This avoids a dashboard aesthetic while preserving immediate scanability.

## Risks / Trade-offs

- [The homepage can become dense] → Use a two-column work-preview at wide widths and a deliberate single-column order on narrow viewports.
- [Static proof may be confused for a live run] → Label the proof with its runtime stack and state that it is a recorded real result, not an animation.
- [Global CSS changes can affect functional views] → Preserve existing class names and run source-level, build, browser-flow, and viewport checks.
- [Old styling has duplicate overrides] → Consolidate visual values into tokens and remove obsolete hero overrides rather than layering another cosmetic patch.

## Migration Plan

1. Add UI source contracts for the new information architecture.
2. Replace homepage markup and consolidate shared CSS tokens while keeping event handlers unchanged.
3. Build the static frontend and inspect Home plus the primary project-entry flow in a local browser.
4. Validate desktop viewports, then polish twice based on screenshots.
5. Rollback is a file-level revert of the frontend and OpenSpec change; backend data and evidence are untouched.

## Open Questions

None. The requested first-project and real-run entry points map to existing actions.

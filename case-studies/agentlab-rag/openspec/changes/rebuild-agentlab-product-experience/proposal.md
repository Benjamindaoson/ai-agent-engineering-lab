## Why

AgentLab already provides real code, Browser Agent execution, and evidence-based business verification, but its current presentation reads as a concept landing page. New users cannot immediately see the repairable engineering problem, the working environment, or the difference between an agent's claim and an actual business result.

## What Changes

- Replace the homepage's marketing-led hero with a compact, evidence-first project handoff and workspace preview.
- Make the false-success incident, relevant source file, business-state checks, and real DeepSeek experiment proof visible before a user enters a project.
- Establish shared design tokens and component treatments for navigation, actions, forms, panels, code areas, status signals, and evidence across Home, Trial, Workspace, Run Result, Delivery, and Replay.
- Preserve all existing session, task, editing, connector preflight, run, delivery, and replay behavior.

## Capabilities

### New Capabilities

- `agent-engineering-product-experience`: Evidence-first navigation and page presentation that helps users understand and enter a real Agent repair project.
- `evidence-led-workspace-preview`: A homepage workspace preview and before/after run proof that distinguish reported success from verified business success.

### Modified Capabilities

- `evidence-workbench-presentation`: Apply the shared evidence-focused visual language consistently to the existing workbench, run result, delivery, and replay views.
- `hallmark-agentlab-design-system`: Refine the locked design system from a Tally-derived landing treatment into a restrained Agent engineering product system.

## Impact

- Affects `agentlab_web/src/App.tsx`, shared frontend CSS, source-level UI contracts, and the project design system.
- Does not change backend APIs, model connector security behavior, project-pack semantics, or the frozen proof evidence.

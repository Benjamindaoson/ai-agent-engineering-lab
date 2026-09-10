# Design — AgentLab

A locked design system for the AgentLab product SPA. Its visual language is an evidence-first Agent engineering product: users see the project, code, runtime claim, business state, and proof before they see product promotion.

## Genre

Modern-minimal engineering product.

## Macrostructure family

- Marketing: project handoff, incident workspace preview, and recorded before/after proof.
- App: three-zone workbench with a task rail, code work surface, and evidence sidebar.
- Content: restrained evidence documents for delivery and replay.

## Theme

- Canvas and panels: `--surface-canvas`, `--surface-panel`, `--surface-subtle`
- Text and rules: `--text-strong`, `--text-body`, `--text-muted`, `--border-subtle`, `--border-strong`
- Actions: `--action-primary`, `--action-hover`
- Evidence states: `--status-success`, `--status-failure`, `--status-evidence` and their corresponding `-bg` tokens
- Code: `--surface-code`

## Typography

- Display and body: Geist, with system-safe fallbacks.
- Labels and metrics: Geist Mono, with system-safe fallbacks.
- Display headings are upright, never italic.

## Spacing and interaction

- Use named spacing tokens (`--space-1` through `--space-8`) and 8/14/18px component radii.
- Primary actions are compact dark-ink controls; secondary actions are white panels with a firm border. Pills are reserved for compact status only.
- Motion is short opacity/translate feedback only, with reduced-motion fallback.
- App views use no decorative illustrations or fake browser/IDE chrome. Workspace previews show product-specific code, business state, and run evidence instead.

## Component language

- **Panels** use one pixel structural borders and shallow shadows only at workspace boundaries.
- **Code areas** use the dark code surface with an explicit filename and context label.
- **Status** always pairs a semantic color with an explicit factual label; green confirms business success, red shows a disproven claim, and blue marks evidence or active engineering work.
- **Proof** is a before/after metric row, not an animated chart or generic analytics card.

## Source and boundaries

- No external page styles are loaded at runtime.
- Do not add fabricated usage metrics, customer logos, prices, imagery, or marketing copy. Product claims must be traceable to a task pack, run evidence, or actual UI behavior.

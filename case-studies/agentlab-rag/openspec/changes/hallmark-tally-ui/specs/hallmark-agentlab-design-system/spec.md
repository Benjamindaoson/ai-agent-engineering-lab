## ADDED Requirements

### Requirement: Provide one responsive design system
The product SHALL use named CSS tokens for paper, ink, accent, focus, type, spacing, borders, radii, and motion across all six AgentLab views. It SHALL use a Tally-derived light indigo workbench language and SHALL not load external example styles at runtime.

#### Scenario: User visits any product view
- **WHEN** the application renders home, trial, workspace, result, delivery, or replay
- **THEN** the view SHALL consume the same named design tokens and expose a visible keyboard focus treatment

### Requirement: Remain usable on narrow screens
The frontend SHALL avoid horizontal page scrolling at 320, 375, 414, and 768 pixel widths. Interactive labels SHALL remain readable and the workspace SHALL collapse its three columns into a vertical flow.

#### Scenario: User opens the workbench on a phone
- **WHEN** the viewport is 375 pixels wide
- **THEN** the task rail, editor, and run sidebar SHALL stack without clipping a control or overflowing the page

### Requirement: Use authentic run presentation
The UI SHALL show a real Browser Agent screenshot only when the backend reports it available; otherwise it SHALL show the actual current action or terminal run status. It SHALL not draw fake browser chrome.

#### Scenario: Completed run lacks a screenshot
- **WHEN** a run result has no screenshot evidence
- **THEN** the workspace SHALL show its real status text and SHALL not display decorative browser dots or a fabricated image frame

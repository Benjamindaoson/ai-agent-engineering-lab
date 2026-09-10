# Hallmark Tally UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild AgentLab's SPA as an evidence-first, responsive engineering workbench using the Hallmark Tally example as the direct visual basis.

**Architecture:** Keep the existing React state machine and FastAPI contracts untouched. Replace the view markup class structure and CSS with a tokenized design system described by `design.md`; use only actual API-derived task and run values.

**Tech Stack:** React 19, TypeScript, Vite, Monaco, FastAPI test suite, CSS custom properties.

## Global Constraints

- Preserve every current API endpoint and user action.
- No new runtime dependencies, invented metrics, Hallmark brand copy, or fake browser chrome.
- Use named CSS tokens and support 320/375/414/768px widths.

---

### Task 1: UI contract test and locked design system

**Files:**
- Create: `tests/test_agentlab_ui.py`
- Create: `design.md`

- [ ] **Step 1: Write a failing presentation contract test**

```python
def test_workbench_uses_authentic_evidence_presentation():
    source = APP.read_text(encoding='utf-8')
    assert 'evidence-status' in source
    assert 'className="dots"' not in source
```

- [ ] **Step 2: Run the test and observe failure**

Run: `uv run pytest -q tests/test_agentlab_ui.py`

- [ ] **Step 3: Add the testable workbench classes and root design system**

```tsx
<section className="evidence-status">{run?.current_action}</section>
```

- [ ] **Step 4: Run the test and observe success**

Run: `uv run pytest -q tests/test_agentlab_ui.py`

### Task 2: Tally-derived product shell and six views

**Files:**
- Modify: `agentlab_web/src/App.tsx`
- Modify: `agentlab_web/src/styles.css`
- Modify: `agentlab_web/src/product.css`

- [ ] **Step 1: Rebuild navigation, home, and trial as evidence-first surfaces**
- [ ] **Step 2: Rebuild workspace, result, delivery, and replay with semantic workbench classes**
- [ ] **Step 3: Implement responsive tokens, focus states, and reduced-motion support**
- [ ] **Step 4: Run `npm --prefix agentlab_web run typecheck` and `npm --prefix agentlab_web run build`**

### Task 3: Verification

**Files:**
- Modify: `openspec/changes/hallmark-tally-ui/tasks.md`

- [ ] **Step 1: Run full backend tests and strict OpenSpec validation**
- [ ] **Step 2: Start the local product and smoke-test desktop plus narrow viewport rendering**
- [ ] **Step 3: Mark verified OpenSpec tasks complete and review the diff**

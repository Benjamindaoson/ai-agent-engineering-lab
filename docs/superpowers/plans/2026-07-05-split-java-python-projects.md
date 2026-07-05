# Java/Python Project Split Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reorganize the repository into `handwritten-ai-agent-java/` and `handwritten-ai-agent-python/` as its only visible top-level projects.

**Architecture:** Flatten the current `java-projects/` and `python-projects/` module containers into named project roots. Put shared course/platform material in the Python project because its executable tooling and platform backend are Python, then update only paths broken by the move.

**Tech Stack:** Git, PowerShell, Maven/Spring Boot, Python 3/unittest, Next.js/npm

## Global Constraints

- Preserve root `.git/` as the only non-project top-level entry.
- Do not delete, restore, or overwrite existing user changes.
- Stop on target-name collisions.
- Do not refactor teaching-project business logic.
- Keep all moves inside `C:\Users\Admin（无密码）\Music\备课配套项目\shouxieagent`.

---

### Task 1: Record and validate the migration map

**Files:**
- Create: `openspec/changes/split-java-python-projects/`
- Read: repository root entries and Git status

- [ ] Confirm both destination directories do not already exist.
- [ ] Record every current top-level entry and classify it as Java, Python, or root Git metadata.
- [ ] Create the OpenSpec proposal, design, specs, and tasks for this exact migration.
- [ ] Verify the OpenSpec change is apply-ready.

### Task 2: Create the two project roots and move content

**Files:**
- Create: `handwritten-ai-agent-java/`
- Create: `handwritten-ai-agent-python/`
- Move: `java-projects/*` to `handwritten-ai-agent-java/`
- Move: `python-projects/*` to `handwritten-ai-agent-python/`
- Move: root Maven files to `handwritten-ai-agent-java/`
- Move: all remaining project content to `handwritten-ai-agent-python/`

- [ ] Resolve and validate both destination paths under the repository root.
- [ ] Move Java modules and Maven aggregation without overwriting.
- [ ] Move Python modules, AgentLab, course tooling, docs, specs, and project metadata without overwriting.
- [ ] Copy the repository license into both projects.
- [ ] Remove only source directories proven empty after successful moves.

### Task 3: Repair Java project paths

**Files:**
- Modify: `handwritten-ai-agent-java/pom.xml`
- Create: `handwritten-ai-agent-java/README.md`
- Create: `handwritten-ai-agent-java/.gitignore`

- [ ] Remove the `java-projects/` prefix from all 20 Maven module declarations.
- [ ] Document Java prerequisites and Maven build/run commands.
- [ ] Verify every declared module contains a `pom.xml`.
- [ ] Run `mvn help:effective-pom -DskipTests` or report the exact environment blocker.

### Task 4: Repair Python project paths

**Files:**
- Modify: `handwritten-ai-agent-python/course.py`
- Modify: `handwritten-ai-agent-python/scripts/python_quality_gate.py`
- Modify: `handwritten-ai-agent-python/tests/test_course.py`
- Modify: Python README and course documents containing old root paths

- [ ] Change course discovery from `ROOT / "python-projects"` to `ROOT`.
- [ ] Change quality-gate discovery to the new Python project root.
- [ ] Update tests and documentation so commands run from `handwritten-ai-agent-python/`.
- [ ] Search maintained source/docs for stale `java-projects/` and `python-projects/` references and classify intentional historical references separately.

### Task 5: Verify the final repository

**Files:**
- Test: `handwritten-ai-agent-python/tests/test_course.py`
- Test: `handwritten-ai-agent-python/tests/test_python_quality_gate.py`
- Test: all Python teaching-project tests through the quality gate

- [ ] Verify root entries are only `.git/`, `handwritten-ai-agent-java/`, and `handwritten-ai-agent-python/`.
- [ ] Verify Java has 20 module directories and Python has 19 teaching-project directories.
- [ ] Run Python root tests without writing course progress.
- [ ] Run the Python quality gate and report its exact pass/fail counts.
- [ ] Run Java Maven model/build validation and report its exact result.
- [ ] Inspect `git status` and confirm no source content was lost by comparing pre/post migration inventories.

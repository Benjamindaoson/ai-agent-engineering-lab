# Add Course Runner

## Why

Teachers and students need one root command to follow the 19 Python projects in order. The course should behave like sequential levels: finish the current level before the next level unlocks.

## What Changes

- Add root `course.py`.
- Track local progress in `.course_progress.json`.
- Run only the current level's `self_check`, `offline_demo`, or `tests`.
- Unlock the next level only when the selected run succeeds.

## Out of Scope

- Web UI.
- Accounts, cloud sync, leaderboard, scoring, or role permissions.
- A full platform merge of the 19 projects.

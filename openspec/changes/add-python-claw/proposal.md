## Why

`java-claw` is the platform-style course capstone: workspace templates, skills, daily notes, long-term memory, two agent sessions, web chat protocol, and Feishu message routing.

## What Changes

- Add `python-claw/` without modifying `java-claw/`.
- Mirror the Java package shape with Python modules for properties, memory, session startup, skill loading, agent orchestration, Feishu tools, Feishu receiver, WebSocket handler, and update-memory tool.
- Copy the JavaClaw templates and static page as Python resources for classroom side-by-side comparison.
- Keep the implementation offline-first with stdlib storage and fake agent responses.

## Impact

- New Python module under `python-claw/`.
- New OpenSpec change under `openspec/changes/add-python-claw/`.

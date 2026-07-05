# Split Java and Python Projects

## Why

The repository currently mixes Java modules, Python ports, course tooling, and AgentLab at one level. Users cannot tell which runtime owns shared files or where each project starts.

## What Changes

- Create `handwritten-ai-agent-java/` for the Maven build and all Java modules.
- Create `handwritten-ai-agent-python/` for Python teaching modules, course tooling, AgentLab, specifications, and platform material.
- Repair relative paths and project documentation broken by the move.
- Leave only those two visible projects and root Git metadata.

## Out of Scope

- Refactoring Agent implementations.
- Merging teaching modules.
- Creating a third top-level AgentLab project.

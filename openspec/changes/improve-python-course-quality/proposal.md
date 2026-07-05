# Improve Python Course Quality

## Why

The 19 Python course projects need repeatable quality checks and clearer failure behavior before they can be treated as a complete classroom engineering track.

## What Changes

- Add a root quality gate that runs every Python project's `self_check`, tests, and `offline_demo`.
- Improve external command failure messages for Git and Docker boundaries.
- Standardize README run paths for root-directory classroom use.
- Add tests for the new quality gate and external dependency errors.

## Out of Scope

- Production authentication, deployment, telemetry, or account systems.
- Real external-service smoke tests for Tavily, Docker Desktop, Playwright, browser automation, or online LLM APIs.

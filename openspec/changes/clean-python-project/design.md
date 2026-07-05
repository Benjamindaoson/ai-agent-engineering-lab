# Design

Use an explicit deletion allowlist and constrain all recursive removal to the resolved Python project root. `run-local.ps1` checks prerequisites, recreates the virtual environment and npm dependencies when absent, seeds SQLite, and starts both local services without a new dependency.

Verification starts from a clean dependency-free tree, restores the environment, runs course and AgentLab checks, performs HTTP smoke checks, then removes regenerated local artifacts again.

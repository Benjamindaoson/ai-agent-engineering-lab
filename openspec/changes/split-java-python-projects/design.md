# Design

## Layout

The Java directory is a self-contained Maven multi-module project. The Python directory is a self-contained course and platform workspace containing the 19 Python modules and AgentLab's Python-led full-stack application.

## Migration

Move files without overwriting, flatten the existing language container directories, then update only path-dependent configuration, tests, and documentation. Preserve `.git/` at the repository root and preserve all existing working-tree changes.

## Validation

Check the root inventory, declared module existence, Python course discovery, Python tests, the quality gate, Maven project loading, and stale path references.

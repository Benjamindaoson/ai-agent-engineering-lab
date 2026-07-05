## Design

`python-ai-data` mirrors the Java module:

- `dto/`: `ColumnInfo`, `TableInfo`, `Plan`, `Step`, `StepResultDto`
- `node/`: `KeywordsExtractNode`, `TableInfoRecallNode`, `PlannerNode`, `PlanExecuteNode`, `SqlExecuteNode`, `ReportGeneratorNode`
- `util/prompt_util.py`
- `data_application.py`, `data_controller.py`, `init_controller.py`

The Python workflow keeps the Java state keys: `input`, `keywordsExtractResult`, `tableInfoRecallResult`, `plannerResult`, `currentStepNum`, `planExecuteResult`, `planExecuteNextNode`, and `reportGeneratorResult`.

SQLite is used for offline execution. This keeps the course runnable without MySQL. The SQL repair loop stays the same: failed step result -> ask model/client for fixed SQL -> update current step -> retry.

## Verification

Tests use fake clients and an in-memory SQLite database. They cover DTO parsing, keyword extraction, schema recall, planner output parsing, SQL success/failure, SQL repair, full workflow, and controller continuation.

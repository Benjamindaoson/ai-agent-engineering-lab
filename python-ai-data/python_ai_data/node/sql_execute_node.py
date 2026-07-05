import json
import sqlite3

from python_ai_data.dto import StepResultDto


class SqlExecuteNode:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def apply(self, state: dict) -> dict:
        plan = state["plannerResult"]
        current_step_num = state.get("currentStepNum", 0)
        step = plan.steps[current_step_num]
        result = dict(state.get("planExecuteResult", {}))
        try:
            rows = self._query(step.sql)
            result[current_step_num] = StepResultDto(step, True, json.dumps(rows, ensure_ascii=False))
        except (sqlite3.Error, ValueError) as exc:
            result[current_step_num] = StepResultDto(step, False, f"SQL execution failed: {exc}")
        return {"planExecuteResult": result}

    def _query(self, sql: str) -> list[dict]:
        statement = sql.strip().lower()
        if not (statement.startswith("select") or statement.startswith("with")):
            raise ValueError("Only SELECT queries are allowed")
        cursor = self.connection.execute(sql)
        columns = [description[0] for description in cursor.description or []]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

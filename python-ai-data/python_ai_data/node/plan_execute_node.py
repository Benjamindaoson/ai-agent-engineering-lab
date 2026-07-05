class PlanExecuteNode:
    def __init__(self, chat_client):
        self.chat_client = chat_client

    def apply(self, state: dict) -> dict:
        plan = state["plannerResult"]
        current_step_num = state.get("currentStepNum", 0)
        plan_execute_result = state.get("planExecuteResult", {})
        step_result = plan_execute_result.get(current_step_num)

        if step_result is None:
            return {"planExecuteNextNode": "sql", "currentStepNum": current_step_num}

        if step_result.success:
            current_step_num += 1
            return {
                "planExecuteNextNode": "report" if current_step_num >= len(plan.steps) else "sql",
                "currentStepNum": current_step_num,
            }

        prompt = (
            "The following SQL failed. Return only the fixed SQL.\n\n"
            f"Original SQL:\n{step_result.step.sql}\n\nError:\n{step_result.data}\n"
        )
        plan.steps[current_step_num].sql = self.chat_client.complete("", prompt).strip()
        return {"planExecuteNextNode": "sql", "currentStepNum": current_step_num, "plannerResult": plan}

from .data_application import DataWorkflow
from .dto import Plan


class DataController:
    def __init__(self, workflow: DataWorkflow):
        self.workflow = workflow

    def stream(self, input_text: str) -> str:
        state = self.workflow.prepare_plan(input_text)
        return "Plan generated, please confirm! " + state["plannerResult"].to_json()

    def stream_continue(self, input_text: str) -> str:
        current_plan = self.workflow.state["plannerResult"]
        raw_plan = self.workflow.chat_client.complete(
            "Revise the current plan according to user feedback. Current plan: " + current_plan.to_json(),
            "User feedback: " + input_text,
        )
        self.workflow.state["plannerResult"] = Plan.from_json(raw_plan)
        self.workflow.state["currentStepNum"] = 0
        self.workflow.state["planExecuteResult"] = {}
        return self.workflow.run_from_plan()

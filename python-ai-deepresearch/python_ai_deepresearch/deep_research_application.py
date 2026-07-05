from concurrent.futures import ThreadPoolExecutor, as_completed

from .chat_client import ChatClient
from .dto import Plan
from .model_config import ModelConfig
from .node import CoordinatorNode, PlannerNode, ReporterNode, ResearcherNode


class DeepResearchWorkflow:
    def __init__(self, chat_client=None, max_steps: int = 3, parallel: bool = True):
        self.chat_client = chat_client or ChatClient(ModelConfig.from_env())
        self.max_steps = max_steps
        self.parallel = parallel
        self.state: dict = {}

    def run(self, user_input: str) -> str:
        self.state = {"input": user_input}
        self.state.update(CoordinatorNode(self.chat_client).apply(self.state))
        if self.state["coordinatorResult"] != "NEED_PLAN":
            return self.state["coordinatorResult"]

        self.state.update(PlannerNode(self.chat_client, self.max_steps).apply(self.state))
        plan = Plan.from_json(self.state["plannerResult"])
        self._run_researchers(len(plan.steps))
        self.state.update(ReporterNode(self.chat_client).apply(self.state))
        return self.state["reporterResult"]

    def _run_researchers(self, step_count: int) -> None:
        if not self.parallel:
            for index in range(step_count):
                self.state.update(ResearcherNode(self.chat_client, index).apply(self.state))
            return
        with ThreadPoolExecutor(max_workers=max(1, step_count)) as executor:
            futures = [executor.submit(ResearcherNode(self.chat_client, index).apply, dict(self.state)) for index in range(step_count)]
            for future in as_completed(futures):
                self.state.update(future.result())


def main() -> None:
    workflow = DeepResearchWorkflow()
    print(workflow.run("Research the current state of AI agents."))


if __name__ == "__main__":
    main()

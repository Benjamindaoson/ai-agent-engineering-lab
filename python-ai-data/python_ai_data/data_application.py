from .chat_client import ChatClient
from .init_controller import InitController, create_demo_connection
from .model_config import ModelConfig
from .node import (
    KeywordsExtractNode,
    PlanExecuteNode,
    PlannerNode,
    ReportGeneratorNode,
    SqlExecuteNode,
    TableInfoRecallNode,
)


class DataWorkflow:
    def __init__(self, chat_client=None, connection=None, table_infos=None):
        self.chat_client = chat_client or ChatClient(ModelConfig.from_env())
        self.connection = connection or create_demo_connection()
        self.table_infos = table_infos or InitController(self.connection).init()
        self.state: dict = {}

    def prepare_plan(self, user_input: str) -> dict:
        self.state = {"input": user_input}
        for node in (
            KeywordsExtractNode(self.chat_client),
            TableInfoRecallNode(self.table_infos),
            PlannerNode(self.chat_client),
        ):
            self.state.update(node.apply(self.state))
        return self.state

    def run(self, user_input: str) -> str:
        self.prepare_plan(user_input)
        return self.run_from_plan()

    def run_from_plan(self) -> str:
        plan_execute = PlanExecuteNode(self.chat_client)
        sql_execute = SqlExecuteNode(self.connection)
        while True:
            self.state.update(plan_execute.apply(self.state))
            next_node = self.state["planExecuteNextNode"]
            if next_node == "report":
                self.state.update(ReportGeneratorNode(self.chat_client).apply(self.state))
                return self.state["reportGeneratorResult"]
            self.state.update(sql_execute.apply(self.state))


def main() -> None:
    workflow = DataWorkflow()
    print(workflow.run("How many orders are there?"))


if __name__ == "__main__":
    main()

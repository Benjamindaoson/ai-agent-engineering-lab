import json

from .data_application import DataWorkflow
from .init_controller import create_demo_connection


class FakeDataClient:
    def __init__(self):
        self.calls = 0

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        self.calls += 1
        if "Extract keywords" in system_prompt:
            return '{"keywords":["orders","total_amount"]}'
        if "data analysis planner" in system_prompt:
            return json.dumps(
                {
                    "steps": [
                        {
                            "stepNum": 1,
                            "description": "Count orders and sum amount",
                            "sql": "select count(*) as order_count, sum(total_amount) as total from orders",
                        }
                    ]
                },
                ensure_ascii=False,
            )
        return (
            "<html><body><h1>Order Analysis</h1>"
            "<p>The demo query counted orders and summed order amount.</p>"
            "<footer>Created by Autobots</footer></body></html>"
        )


def main() -> None:
    workflow = DataWorkflow(FakeDataClient(), create_demo_connection())
    print(workflow.run("How many orders and total amount?"))


if __name__ == "__main__":
    main()

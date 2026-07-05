from dataclasses import dataclass


@dataclass
class SubTask:
    name: str
    state: str = "TODO"


class PlanNotebook:
    def __init__(self, max_subtasks: int = 10) -> None:
        self.max_subtasks = max_subtasks
        self.subtasks: list[SubTask] = []

    def create_snake_game_plan(self) -> None:
        names = ["创建 snake.html", "创建 snake.css", "创建 snake.js", "检查运行说明"]
        self.subtasks = [SubTask(name) for name in names[: self.max_subtasks]]

    def run_all(self) -> list[SubTask]:
        for subtask in self.subtasks:
            subtask.state = "DONE"
        return self.subtasks


def run_plan_demo() -> str:
    notebook = PlanNotebook(max_subtasks=10)
    notebook.create_snake_game_plan()
    notebook.run_all()
    return "\n".join(f"{item.name} - {item.state}" for item in notebook.subtasks)


def main() -> None:
    print(run_plan_demo())


if __name__ == "__main__":
    main()

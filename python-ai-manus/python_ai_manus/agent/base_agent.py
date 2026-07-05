from abc import ABC, abstractmethod
from dataclasses import dataclass

from python_ai_manus.model import Memory, Message


@dataclass
class StepResult:
    output: str
    should_continue: bool


class BaseAgent(ABC):
    def __init__(self, system_prompt: str | None):
        self.memory = Memory()
        self.max_step = 10
        self.system_prompt = system_prompt or ""

    def run(self, prompt: str) -> str:
        self.memory.add_message(Message.system_message(self.system_prompt))
        self.memory.add_message(Message.user_message(prompt))

        current_step = 0
        all_step_result: list[str] = []
        while current_step < self.max_step:
            step_result = self.step(prompt)
            all_step_result.append(step_result.output)
            if not step_result.should_continue:
                break
            current_step += 1
        return "\n".join(all_step_result)

    @abstractmethod
    def step(self, current_query: str) -> StepResult:
        raise NotImplementedError

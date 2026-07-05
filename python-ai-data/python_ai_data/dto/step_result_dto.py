from dataclasses import dataclass

from .step import Step


@dataclass
class StepResultDto:
    step: Step
    success: bool
    data: str

    def to_dict(self) -> dict:
        return {"step": self.step.to_dict(), "success": self.success, "data": self.data}

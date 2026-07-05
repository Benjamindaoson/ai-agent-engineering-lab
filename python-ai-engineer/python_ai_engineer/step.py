from dataclasses import dataclass


@dataclass
class Step:
    step_num: str
    agent_name: str
    prompt: str

    @classmethod
    def from_dict(cls, data: dict) -> "Step":
        return cls(
            step_num=str(data.get("stepNum") or data.get("step_num") or ""),
            agent_name=str(data.get("agentName") or data.get("agent_name") or ""),
            prompt=str(data.get("prompt") or ""),
        )

    def to_dict(self) -> dict:
        return {"stepNum": self.step_num, "agentName": self.agent_name, "prompt": self.prompt}

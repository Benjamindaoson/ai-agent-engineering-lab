from dataclasses import dataclass


@dataclass
class Step:
    step_num: int
    description: str
    sql: str

    @classmethod
    def from_dict(cls, data: dict) -> "Step":
        return cls(
            int(data.get("stepNum") or data.get("step_num") or 0),
            str(data.get("description") or ""),
            str(data.get("sql") or ""),
        )

    def to_dict(self) -> dict:
        return {"stepNum": self.step_num, "description": self.description, "sql": self.sql}

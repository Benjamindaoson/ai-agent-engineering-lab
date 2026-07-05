from dataclasses import dataclass


@dataclass
class AlarmRequest:
    time: str
    address: str | None = None

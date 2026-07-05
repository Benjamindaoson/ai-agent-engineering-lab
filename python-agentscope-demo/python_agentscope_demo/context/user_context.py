from dataclasses import dataclass


@dataclass(frozen=True)
class UserContext:
    user_id: str

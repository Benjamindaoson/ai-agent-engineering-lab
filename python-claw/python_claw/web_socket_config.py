from dataclasses import dataclass


@dataclass(frozen=True)
class WebSocketConfig:
    endpoint: str = "/ws/chat"

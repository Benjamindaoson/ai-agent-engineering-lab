from __future__ import annotations

from .feishu_message_receiver import FeishuMessageReceiver


class FeishuDemo:
    def __init__(self, receiver: FeishuMessageReceiver) -> None:
        self.receiver = receiver

    def process_and_reply_message(self, event: dict[str, str]) -> dict[str, str]:
        return self.receiver.process_and_reply_message(event)

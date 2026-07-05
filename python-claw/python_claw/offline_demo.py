from __future__ import annotations

import json

from .feishu_message_receiver import FeishuMessageReceiver
from .feishu_tools import FeishuTools
from .claw_application import create_application
from .web_socket_handler import WebSocketHandler


def main() -> None:
    app = create_application()
    ws = WebSocketHandler(app.claw_agent)
    receiver = FeishuMessageReceiver(app.claw_agent)
    tools = FeishuTools(random_func=lambda low, high: low)

    print("== workspace ==")
    print(app.properties.workspace_dir)
    print(app.skill_loader.load_all_skills())
    print("== web chat ==")
    print(ws.on_message(json.dumps({"message": "你好"}, ensure_ascii=False)))
    print("== feishu ==")
    print(receiver.handle_event({
        "event_id": "demo-1",
        "message_id": "msg-1",
        "chat_type": "p2p",
        "content": json.dumps({"text": "你好"}, ensure_ascii=False),
        "sender_open_id": "ou_demo",
    }))
    print("== tools ==")
    print(tools.get_weather("北京"))
    print(tools.calculate("3+4"))


if __name__ == "__main__":
    main()

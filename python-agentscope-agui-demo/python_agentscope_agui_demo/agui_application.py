import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from .agui_protocol import event, to_sse


STATIC_ROOT = Path(__file__).resolve().parent / "static"


class AguiApplication:
    def __init__(self) -> None:
        self.memory: dict[str, list[dict[str, str]]] = {}

    def handle_run(self, payload: dict[str, Any]) -> tuple[bytes, dict[str, str]]:
        thread_id = str(payload.get("threadId") or "default")
        run_id = str(payload.get("runId") or "run-1")
        messages = payload.get("messages") or []
        user_messages = [msg for msg in messages if msg.get("role") == "user"]
        self.memory.setdefault(thread_id, []).extend({"role": "user", "content": str(msg.get("content", ""))} for msg in user_messages)

        last_text = self.memory[thread_id][-1]["content"] if self.memory[thread_id] else ""
        message_id = f"{run_id}-assistant"
        response = f"Assistant: 已收到 {last_text}。当前线程已有 {len(self.memory[thread_id])} 条用户消息。"
        events = [
            event("RUN_STARTED", threadId=thread_id, runId=run_id),
            event("TEXT_MESSAGE_START", messageId=message_id, role="assistant"),
            event("TEXT_MESSAGE_CONTENT", messageId=message_id, delta=response),
            event("TEXT_MESSAGE_END", messageId=message_id),
            event("RUN_FINISHED", threadId=thread_id, runId=run_id),
        ]
        return to_sse(events), {"Content-Type": "text/event-stream; charset=utf-8", "Cache-Control": "no-cache"}

    def static_response(self, path: str) -> tuple[bytes, dict[str, str]]:
        if path in ("", "/"):
            target = STATIC_ROOT / "index.html"
            content_type = "text/html; charset=utf-8"
        elif path == "/js/agui-client.js":
            target = STATIC_ROOT / "js" / "agui-client.js"
            content_type = "application/javascript; charset=utf-8"
        else:
            return b"Not Found", {"Content-Type": "text/plain; charset=utf-8", "Status": "404"}
        return target.read_bytes(), {"Content-Type": content_type}


def create_application() -> AguiApplication:
    return AguiApplication()


def make_handler(app: AguiApplication):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            body, headers = app.static_response(self.path)
            status = int(headers.pop("Status", "200"))
            self.send_response(status)
            for key, value in headers.items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self) -> None:
            if self.path != "/agui/run":
                self.send_response(404)
                self.end_headers()
                return
            length = int(self.headers.get("Content-Length", "0"))
            try:
                payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
            except json.JSONDecodeError:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"invalid json")
                return
            body, headers = app.handle_run(payload)
            self.send_response(200)
            for key, value in headers.items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: Any) -> None:
            return

    return Handler


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), make_handler(create_application()))
    print(f"AG-UI demo server: http://{host}:{port}")
    server.serve_forever()

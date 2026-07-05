from .agui_application import create_application
from .agui_protocol import parse_sse_events


def main() -> None:
    app = create_application()
    body, _ = app.handle_run({"threadId": "check", "runId": "run-1", "messages": [{"role": "user", "content": "你好"}]})
    events = parse_sse_events(body.decode("utf-8"))
    assert events[0]["type"] == "RUN_STARTED"
    assert events[-1]["type"] == "RUN_FINISHED"
    print("self_check: ok")


if __name__ == "__main__":
    main()

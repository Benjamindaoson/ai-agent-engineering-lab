from .agui_application import create_application


def main() -> None:
    app = create_application()
    body, headers = app.handle_run(
        {"threadId": "thread-demo", "runId": "run-demo", "messages": [{"role": "user", "content": "课堂演示"}]}
    )
    print(headers["Content-Type"])
    print(body.decode("utf-8"))
    print("浏览器演示：python -m python_agentscope_agui_demo --port 8000")


if __name__ == "__main__":
    main()

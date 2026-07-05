from __future__ import annotations

from .graph_application import create_application


def main() -> None:
    app = create_application()
    print("== simple ==")
    print(app.controller.simple("AI Agent"))
    print("== stream ==")
    print(app.controller.stream("AI Agent"))
    print("== conditional ==")
    print(app.controller.conditional("写Python代码"))
    print("== memory ==")
    print(app.controller.memory_saver_endpoint("demo", "你好"))
    print("== interrupt before ==")
    print(app.controller.interrupt_before_state_graph("before-demo"))
    print(app.controller.continue_before_state_graph("before-demo", "next"))
    print("== sub graph ==")
    print(app.controller.sub_graph())


if __name__ == "__main__":
    main()

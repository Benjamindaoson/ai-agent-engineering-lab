from __future__ import annotations

from .graph_application import create_application


def main() -> None:
    app = create_application()
    assert "content" in app.controller.simple("AI Agent")
    assert app.controller.conditional("写Python代码")["intentionResult"] == "2"
    assert "周瑜" in app.controller.thread("check", "你好")
    assert len(app.memory_saver.list("check")) == 1
    assert "中断了，请提供用户的年龄" in app.controller.interrupt_before_state_graph("check-before")
    assert "我是节点3" in "".join(app.controller.continue_before_state_graph("check-before", "next"))
    assert app.controller.parallel()["next_node"] == "__END__"
    assert app.controller.sub_graph()["ids"]["b2"] == "B2"
    print("python-ai-alibaba-graph-demo self check passed")


if __name__ == "__main__":
    main()

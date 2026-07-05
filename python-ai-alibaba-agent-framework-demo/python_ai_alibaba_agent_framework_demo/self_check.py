from __future__ import annotations

from .agent_application import create_application


def main() -> None:
    app = create_application()
    assert "helloAgent" in app.controller.hello("杭州天气")
    assert len(app.controller.stream("杭州天气")) > 0
    app.controller.memory("记住我叫周瑜", "check")
    assert "history=2" in app.controller.memory("我叫什么", "check")
    assert "请确认是否执行工具" in app.controller.human_hook("查询天气", "check-thread")
    assert "APPROVED" in app.controller.human_agent_feedback("check-thread")
    assert "api_key" in app.controller.multi_agent("api_key 怎么查")["rag"]
    print("python-ai-alibaba-agent-framework-demo self check passed")


if __name__ == "__main__":
    main()

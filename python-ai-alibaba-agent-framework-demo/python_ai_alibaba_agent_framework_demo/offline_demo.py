from __future__ import annotations

from .agent_application import create_application


def main() -> None:
    app = create_application()
    print("== hello ==")
    print(app.controller.hello("杭州天气"))
    print("== memory ==")
    print(app.controller.memory("记住我叫周瑜", "demo"))
    print(app.controller.memory("我叫什么", "demo"))
    print("== hook ==")
    print(app.controller.hook("普通问题"))
    print("== human approval ==")
    print(app.controller.human_hook("查询天气", "thread"))
    print(app.controller.human_agent_feedback("thread"))
    print("== multi agent ==")
    print(app.sequential_agent.invoke("写计划"))
    print(app.parallel_agent.invoke("写代码"))
    print(app.controller.multi_agent("api_key 怎么查"))


if __name__ == "__main__":
    main()

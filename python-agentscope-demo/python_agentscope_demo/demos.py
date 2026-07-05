import base64
from pathlib import Path

from python_agentscope_demo.core import (
    ConfirmationHook,
    FakeChatModel,
    InMemoryMemory,
    Msg,
    MsgHub,
    ReActAgent,
    Toolkit,
    fanout,
    sequential,
)
from python_agentscope_demo.context.user_context import UserContext
from python_agentscope_demo.product.product_info import ProductInfo
from python_agentscope_demo.tools.email_service import EmailService
from python_agentscope_demo.tools.weather_service import WeatherService


RESOURCE_ROOT = Path(__file__).resolve().parents[1] / "resources"


def make_model() -> FakeChatModel:
    return FakeChatModel()


def make_basic_agent(toolkit: Toolkit | None = None, memory: InMemoryMemory | None = None, hooks: list | None = None) -> ReActAgent:
    return ReActAgent("Assistant", "你是一个有帮助的 AI 助手。", make_model(), toolkit=toolkit, memory=memory, hooks=hooks)


def run_hello_world_demo() -> str:
    return make_basic_agent().call(Msg.text("你好！")).text


def run_tool_demo() -> str:
    toolkit = Toolkit()
    toolkit.register_tool(WeatherService())
    return make_basic_agent(toolkit).call(Msg.text("长沙什么天气")).text


def run_tool_preset_demo() -> str:
    toolkit = Toolkit()
    toolkit.register_tool(EmailService(), preset_parameters={"send": {"apiKey": "123123"}})
    return make_basic_agent(toolkit).call(Msg.text("发邮件给zhouyu,主题为Python")).text


def run_tool_context_demo() -> str:
    toolkit = Toolkit()
    toolkit.register_tool(WeatherService())
    toolkit.register_context("user", UserContext("user-123"))
    return make_basic_agent(toolkit).call(Msg.text("查询最近一个月的订单数据")).text


def run_tool_group_demo() -> list[str]:
    toolkit = Toolkit()
    toolkit.create_tool_group("basic", "基础工具")
    toolkit.register_tool(WeatherService(), group="basic")
    agent = make_basic_agent(toolkit)
    first = agent.call(Msg.text("上海什么天气")).text
    toolkit.update_tool_groups(["basic"], False)
    second = agent.call(Msg.text("上海什么天气")).text
    return [first, second]


def run_tool_emitter_demo(count: int = 3) -> list[str]:
    toolkit = Toolkit()
    toolkit.register_tool(WeatherService())
    chunks: list[str] = []
    toolkit.set_chunk_callback(lambda use, result: chunks.append(result))
    make_basic_agent(toolkit).call(Msg.text(f"生成{count}个数据"))
    return chunks


def run_hook_demo() -> list[str]:
    hook = ConfirmationHook()
    toolkit = Toolkit()
    toolkit.register_tool(WeatherService())
    response = make_basic_agent(toolkit, hooks=[hook]).call(Msg.text("生成10个数据"))
    return [tool["name"] for tool in response.pending_tools]


def run_human_in_the_loop_demo(confirm: bool = False) -> str:
    toolkit = Toolkit()
    toolkit.register_tool(WeatherService())
    agent = make_basic_agent(toolkit, hooks=[ConfirmationHook()])
    pending = agent.call(Msg.text("生成2个数据"))
    if not pending.pending_tools:
        return pending.text
    if not confirm:
        return "操作已取消"
    return toolkit.generate(pending.pending_tools[0]["input"]["count"])[0]


def run_short_memory_demo(session_root: Path) -> int:
    memory = InMemoryMemory()
    memory.add(Msg.text("我是周瑜", name="user"))
    memory.save_to(session_root, "session1")
    restored = InMemoryMemory()
    restored.load_from(session_root, "session1")
    return len(restored.messages)


def run_long_memory_demo() -> str:
    return "长记忆演示：真实 Mem0 入口保留为外部服务，离线课堂用摘要记忆替代。"


def run_msg_hub_demo() -> list[str]:
    alice = ReActAgent("Alice", "你是 Alice，一位友好的老师。", make_model(), memory=InMemoryMemory())
    bob = ReActAgent("Bob", "你是 Bob，一位好奇的学生。", make_model(), memory=InMemoryMemory())
    jams = ReActAgent("Jams", "你是 Jams，一位深思熟虑的观察者。", make_model(), memory=InMemoryMemory())
    with MsgHub([alice, bob, jams], announcement=Msg.text("欢迎来到讨论！", name="system")) as hub:
        hub.enter()
    return [alice.call().text, bob.call().text, jams.call().text]


def run_multi_agent_debate_demo(rounds: int = 2) -> str:
    topic = "程序员是以技术为主，还是以业务为主"
    alice = ReActAgent("Alice", f"简短回答，你是辩论者 Alice。主题：{topic}", make_model())
    bob = ReActAgent("Bob", f"简短回答，你是辩论者 Bob。主题：{topic}", make_model())
    moderator = ReActAgent("Moderator", f"你是主持人，评估关于以下主题的辩论：{topic}", make_model())
    for _ in range(rounds):
        alice.call(Msg.text("发表你的观点。"))
        bob.call(Msg.text("回应 Alice 并发表你的观点。"))
    return moderator.call(Msg.text("评估辩论。是否有正确答案？")).text


def run_sequential_pipeline_demo() -> str:
    return sequential(
        [
            ReActAgent("Researcher", "你是一名研究员。分析主题并提供关键发现。", make_model()),
            ReActAgent("Writer", "你是一名作家。根据研究发现撰写简洁的摘要。", make_model()),
            ReActAgent("Editor", "你是一名编辑。润色并定稿摘要。", make_model()),
        ],
        Msg.text("人工智能在医疗领域的应用"),
    ).text


def run_fanout_pipeline_demo() -> list[str]:
    return [
        msg.text
        for msg in fanout(
            [
                ReActAgent("Optimist", "你是一个乐观主义者。分析主题的积极方面。", make_model()),
                ReActAgent("Pessimist", "你是一个悲观主义者。分析潜在的风险和挑战。", make_model()),
                ReActAgent("Realist", "你是一个现实主义者。提供平衡的分析。", make_model()),
            ],
            Msg.text("如何提高自己的技能？"),
        )
    ]


def run_structured_output_demo() -> ProductInfo:
    return make_basic_agent().call(Msg.text("模拟生成1个产品"), ProductInfo).structured_data


def run_rag_demo(question: str) -> str:
    qa_path = RESOURCE_ROOT / "qa.txt"
    content = qa_path.read_text(encoding="utf-8")
    if "apikey" in question.lower() or "api-key" in question.lower():
        return "API-KEY 是 DashScope 灵积模型服务用于鉴权和计量计费的凭证。"
    return content.splitlines()[0]


def run_mcp_demo(question: str) -> str:
    return f"MCP 离线演示：remote-mcp 可注册为工具来源，收到问题：{question}"


def run_vision_demo() -> str:
    encoded = base64.b64encode(b"offline image placeholder").decode("ascii")
    return f"视觉离线演示：已构造 base64 图片输入，长度 {len(encoded)}"


def run_image_generate_demo() -> str:
    return "图片生成离线演示：当前保留入口并说明需要图像模型。"


def run_studio_demo(inputs: list[str] | None = None) -> str:
    inputs = inputs or ["你好", "exit"]
    transcript = []
    for index, text in enumerate(inputs, start=1):
        if text.lower() == "exit":
            transcript.append("Studio conversation ended")
            break
        transcript.append(f"Studio Turn {index}: User={text}; Agent=已收到")
    return "\n".join(transcript)

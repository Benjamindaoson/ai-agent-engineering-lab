from .alarm_request import AlarmRequest
from .zhouyu_tools import ZhouyuTools


class ToolController:
    def __init__(self, chat_client, zhouyu_tools: ZhouyuTools):
        self.chat_client = chat_client
        self.zhouyu_tools = zhouyu_tools

    def tool(self, question: str) -> str:
        tool_context = self._tool_context(question)
        return self.chat_client.complete(f"{question}\n\n工具结果：{tool_context}")

    def user_controlled_tool(self, question: str) -> str:
        tool_context = self._tool_context(question)
        return self.chat_client.complete(f"{question}\n\n用户控制工具执行结果：{tool_context}")

    def stream_tool(self, question: str):
        return self.chat_client.stream(self.tool(question))

    def _tool_context(self, question: str) -> str:
        if "时间" in question or "几点" in question:
            return str(self.zhouyu_tools.get_current_date_time())
        if "保存" in question:
            return self.zhouyu_tools.save_code(question)
        if "闹钟" in question:
            return self.zhouyu_tools.set_alarm(AlarmRequest(time=question))
        return "没有工具需要执行"

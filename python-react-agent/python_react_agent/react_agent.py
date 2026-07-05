import re
from dataclasses import dataclass
from typing import Callable

from .agent_tools import AgentTools
from .model_config import ModelConfig
from .tool_util import ToolUtil


REACT_PROMPT_TEMPLATE = """
## 角色定义
你是一个强大的 AI 助手，通过思考和使用工具来解决用户的问题。

## 任务
你的任务是尽你所能回答以下问题。你可以使用以下工具：
{tools}

## 规则
- Action 中只需要返回工具的名字，比如 write_file，不要返回 toolName=write_file。
- 每次只做一次 Reason/Action/ActionInput 或 FinalAnswer 的输出过程。
- 每次返回的过程中不要自己生成 Observation 的内容。

## 输出过程参考
Reason: 你的思考过程
Action: 你的下一步动作，必须是可用工具中的一个
ActionInput: 你要调用的工具输入参数

最后一轮：
FinalAnswer: 最终答案

## 用户需求
Question: {input}

## 历史聊天记录
{history}
"""


@dataclass(frozen=True)
class ParsedOutput:
    type: str
    answer: str | None = None
    reason: str | None = None
    action: str | None = None
    action_input_str: str | None = None
    message: str | None = None


class ReActAgent:
    def __init__(
        self,
        api_client=None,
        config: ModelConfig | None = None,
        model_output_label: str = "Model output",
        tool_result_label: str = "Tool result",
    ):
        self.config = config or ModelConfig.from_env()
        self.api_client = api_client or self._create_client(self.config)
        self.model_output_label = model_output_label
        self.tool_result_label = tool_result_label
        self.tools: dict[str, Callable[[str], str]] = {
            "write_file": AgentTools().write_file,
        }

    @staticmethod
    def _create_client(config: ModelConfig):
        from openai import OpenAI

        return OpenAI(api_key=config.api_key, base_url=config.base_url)

    def run(self, input_text: str, max_iterations: int = 10) -> str:
        history = []

        for _ in range(max_iterations):
            prompt = self.build_prompt(input_text, "".join(history))
            raw_output = self.call_model(prompt)
            print(f"{self.model_output_label}: {raw_output}")

            parsed = self.parse_llm_output(raw_output)
            if parsed.type == "final_answer":
                return parsed.answer or ""
            if parsed.type != "action":
                return parsed.message or "解析 LLM 输出失败"

            observation = self.execute_tool(parsed)
            print(f"{self.tool_result_label}: {observation}")
            history.append(
                f"Reason: {parsed.reason}\n"
                f"Action: {parsed.action}\n"
                f"ActionInput: {parsed.action_input_str}\n"
                f"Observation: {observation}\n"
            )

        return "达到了循环最大次数"

    def call_model(self, prompt: str) -> str:
        response = self.api_client.chat.completions.create(
            model=self.config.llm_name,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content or ""

    def execute_tool(self, parsed_output: ParsedOutput) -> str:
        tool_method = self.tools.get(parsed_output.action or "")
        if not tool_method:
            return f"未知工具: {parsed_output.action}"
        return str(tool_method(parsed_output.action_input_str or ""))

    def build_prompt(self, input_text: str, history: str) -> str:
        return (
            REACT_PROMPT_TEMPLATE.replace("{tools}", ToolUtil.get_tool_description(AgentTools))
            .replace("{input}", input_text)
            .replace("{history}", history)
        )

    @staticmethod
    def parse_llm_output(llm_output: str) -> ParsedOutput:
        if "FinalAnswer:" in llm_output:
            return ParsedOutput("final_answer", answer=llm_output.split("FinalAnswer:", 1)[1].strip())

        match = re.search(r"Reason:(.*?)Action:(.*?)ActionInput:(.*)", llm_output, re.DOTALL)
        if not match:
            return ParsedOutput("error", message=f"解析 LLM 输出失败: '{llm_output}'")

        action_input = match.group(3).strip()
        if action_input.startswith("```json"):
            action_input = action_input[7:]
        if action_input.endswith("```"):
            action_input = action_input[:-3]

        return ParsedOutput(
            "action",
            reason=match.group(1).strip(),
            action=match.group(2).strip(),
            action_input_str=action_input.strip(),
        )

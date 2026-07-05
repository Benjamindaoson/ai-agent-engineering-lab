import json
import uuid
from typing import Any

from python_ai_manus.model import Function, Message, OpenAIClient, ToolCall
from python_ai_manus.tools import ToolCollection, ToolResult

from .base_agent import BaseAgent, StepResult


class ToolCallAgent(BaseAgent):
    def __init__(self, openai_client: OpenAIClient, tool_collection: ToolCollection | None, system_prompt: str | None):
        super().__init__(system_prompt)
        self.openai_client = openai_client
        self.tool_collection = tool_collection or ToolCollection()

    def step(self, current_query: str) -> StepResult:
        context_messages = self.memory.get_messages(current_query)
        tool_definitions = self.tool_collection.get_relevant_tool_definitions(current_query)
        model_response = self.openai_client.chat(context_messages, tool_definitions)

        if model_response.has_tool_calls():
            assistant_message = Message.assistant_message(model_response.content)
            assistant_message.tool_calls = self._convert_to_tool_calls(model_response.tool_calls)
            self.memory.add_message(assistant_message)
            return self._handle_tool_calls(model_response.tool_calls)

        if model_response.content:
            self.memory.add_message(Message.assistant_message(model_response.content))

        if model_response.finish_reason == "stop":
            return StepResult("The model believes the task is complete.", False)
        return StepResult(model_response.content or "", True)

    def _convert_to_tool_calls(self, tool_call_objects: list[Any]) -> list[ToolCall]:
        return [self._convert_one_tool_call(item) for item in tool_call_objects]

    def _convert_one_tool_call(self, item: Any) -> ToolCall:
        node = self._as_dict(item)
        function = node.get("function") or {}
        return ToolCall(
            id=str(node.get("id") or uuid.uuid4()),
            type=str(node.get("type") or "function"),
            function=Function(
                name=str(function.get("name") or ""),
                arguments=function.get("arguments") or "{}",
            ),
        )

    def _handle_tool_calls(self, tool_calls: list[Any]) -> StepResult:
        all_results = []
        for tool_call_obj in tool_calls:
            try:
                node = self._as_dict(tool_call_obj)
                tool_call_id = str(node.get("id") or uuid.uuid4())
                function = node.get("function") or {}
                tool_name = str(function.get("name") or "")
                arguments_json = function.get("arguments") or "{}"
                arguments = json.loads(arguments_json) if isinstance(arguments_json, str) else dict(arguments_json)
                result = self.tool_collection.execute_tool(tool_name, arguments)
                result_content = self._result_content(result)
                self.memory.add_message(Message.tool_message(result_content, tool_name, tool_call_id, result.base64_image))
                all_results.append(f"{tool_name}: {result_content}")
            except Exception as exc:
                # ponytail: tool boundary; individual tools convert expected failures first.
                error_msg = f"Tool execution failed: {exc}"
                self.memory.add_message(Message.tool_message(error_msg, "unknown", str(uuid.uuid4())))
                all_results.append(error_msg)
        return StepResult("\n".join(all_results), True)

    def _result_content(self, result: ToolResult) -> str:
        if result.has_error():
            return f"Error: {result.error}"
        return str(result.output) if result.output is not None else "Success"

    def _as_dict(self, item: Any) -> dict[str, Any]:
        if isinstance(item, dict):
            return item
        if hasattr(item, "model_dump"):
            return item.model_dump()
        if hasattr(item, "to_dict"):
            return item.to_dict()
        raise TypeError(f"Unsupported tool call object: {type(item)!r}")

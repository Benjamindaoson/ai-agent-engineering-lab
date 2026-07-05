from .agent_tools import AgentTools
from .model_config import ModelConfig
from .react_agent import ReActAgent
from .tool_util import ToolUtil


def main() -> None:
    config = ModelConfig.from_env({"PROVIDER": "deepseek", "DEEPSEEK_API_KEY": "sk-test"})
    assert config.base_url == "https://api.deepseek.com"

    description = ToolUtil.get_tool_description(AgentTools)
    assert "toolName=write_file" in description

    parsed = ReActAgent.parse_llm_output(
        'Reason: test\nAction: write_file\nActionInput: ```json\n{"file_path":"a.txt","content":"hi"}\n```'
    )
    assert parsed.type == "action"
    assert parsed.action_input_str == '{"file_path":"a.txt","content":"hi"}'

    final = ReActAgent.parse_llm_output("FinalAnswer: done")
    assert final.answer == "done"

    print("self_check passed")


if __name__ == "__main__":
    main()

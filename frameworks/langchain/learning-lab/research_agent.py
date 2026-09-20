import urllib.error
import urllib.request

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver


SYSTEM_PROMPT = """You are a literary data assistant.

## Capabilities

- `fetch_text_from_url`: loads document text from a URL into the conversation.
Do not guess line counts or positions—ground them in tool results from the saved file.
"""


@tool
def fetch_text_from_url(url: str) -> str:
    """Fetch the document from a URL."""

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; quickstart-research/1.0)"
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read()

    except urllib.error.URLError as e:
        return f"Fetch failed: {e}"

    text = raw.decode("utf-8", errors="replace")
    return text


model = init_chat_model(
    "deepseek-v4-flash",
    model_provider="deepseek",
    temperature=0.2,
    timeout=300,
    max_tokens=4096,
    max_retries=2,
    extra_body={
        "thinking": {
            "type": "disabled"
        }
    },
)

checkpointer = InMemorySaver()


agent = create_agent(
    model=model,
    tools=[fetch_text_from_url],
    system_prompt=SYSTEM_PROMPT,
    checkpointer=checkpointer,
)
content = """Project Gutenberg hosts a full plain-text copy of F. Scott Fitzgerald's The Great Gatsby.
URL: https://www.gutenberg.org/files/64317/64317-0.txt

Answer as much as you can:

1) How many lines in the complete Gutenberg file contain the substring `Gatsby`
   (count lines, not occurrences within a line, each line ends with a line break).

2) The 1-based line number of the first line in the file that contains `Daisy`.

3) A two-sentence neutral synopsis.

Do your best on (1) and (2).

If at any point you realize you cannot verify an exact answer with your available
tools and reasoning, do not fabricate numbers: use `null` for that field and spell
out the limitation in `how_you_computed_counts`.

If you encounter any errors, report what the error was and what the error message was.
"""


agent_result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": content,
            }
        ]
    },
    config={
        "configurable": {
            "thread_id": "great-gatsby-lc"
        }
    },
)


print("\n=== LangChain Agent 完整消息链 ===")

for index, message in enumerate(agent_result["messages"], start=1):
    print(f"\n--- 消息 {index} ---")
    print("类型：", type(message).__name__)

    content = message.content

    # ToolMessage 可能包含整本小说，避免整个终端被刷爆
    if type(message).__name__ == "ToolMessage":
        print("内容长度：", len(str(content)))
        print("内容前 300 字符：")
        print(str(content)[:300])
    else:
        print("内容：", repr(content))


if getattr(message, "response_metadata", None):
    print("finish_reason：", message.response_metadata.get("finish_reason"))

if getattr(message, "usage_metadata", None):
    print("usage_metadata：", message.usage_metadata)

if getattr(message, "additional_kwargs", None):
    reasoning = message.additional_kwargs.get("reasoning_content")
    if reasoning:
        print("reasoning_content 长度：", len(reasoning))
        print("reasoning_content 前 300 字符：")
        print(reasoning[:300])
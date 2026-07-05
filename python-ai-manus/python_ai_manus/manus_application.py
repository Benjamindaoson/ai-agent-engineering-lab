from python_ai_manus.agent import ManusAgent
from python_ai_manus.model import LLMRelevanceFilter, ModelConfig, OpenAIClient


def main() -> None:
    openai_client = OpenAIClient(ModelConfig.from_env())
    manus_agent = ManusAgent(openai_client)
    manus_agent.set_relevance_filter(LLMRelevanceFilter(openai_client))

    prompt = """
1. Create an HTML file named test_page.html and add content.
2. Open the local file in the browser using file://.
3. Take a screenshot of the opened page.
4. Tell me what is in the screenshot.
"""
    print(manus_agent.run(prompt))


if __name__ == "__main__":
    main()

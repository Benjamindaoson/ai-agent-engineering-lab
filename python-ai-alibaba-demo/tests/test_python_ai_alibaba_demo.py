import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from python_ai_alibaba_demo.alibaba_application import create_chat_memory
from python_ai_alibaba_demo.baidu_test import build_baidu_search_request
from python_ai_alibaba_demo.chat_client import FakeChatClient
from python_ai_alibaba_demo.chat_controller import ChatController
from python_ai_alibaba_demo.markdown_test import MarkdownDocumentParserConfig, parse_markdown
from python_ai_alibaba_demo.model_config import ModelConfig
from python_ai_alibaba_demo.pdf_test import parse_pdf_pages
from python_ai_alibaba_demo.simple_ai import Document, SimpleVectorStore


RESOURCE_DIR = PROJECT_ROOT / "resources"


class AlibabaDemoTests(unittest.TestCase):
    def test_model_config_reads_deepseek_provider(self):
        env = {
            "PROVIDER": "deepseek",
            "DEEPSEEK_API_KEY": "sk-test",
            "LLM_NAME": "deepseek-chat",
        }

        config = ModelConfig.from_env(env)

        self.assertEqual(config.provider, "deepseek")
        self.assertEqual(config.api_key, "sk-test")
        self.assertEqual(config.model, "deepseek-chat")
        self.assertEqual(config.base_url, "https://api.deepseek.com")

    def test_markdown_parser_keeps_code_and_blockquote_and_splits_on_rule(self):
        markdown = RESOURCE_DIR / "markdown-test.md"
        config = MarkdownDocumentParserConfig(
            additional_metadata={"title": "zhouyu_title"},
            include_code_block=True,
            include_blockquote=True,
            horizontal_rule_create_document=True,
        )

        documents = parse_markdown(markdown, config)

        self.assertEqual(len(documents), 2)
        self.assertEqual(documents[0].metadata["title"], "zhouyu_title")
        self.assertIn("class Test:", documents[0].content)
        self.assertIn("> 111", documents[0].content)
        self.assertIn("222", documents[1].content)

    def test_pdf_parser_reports_each_pdf_as_document_without_external_parser(self):
        pdf = RESOURCE_DIR / "pdf-test.pdf"

        documents = parse_pdf_pages(pdf)

        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0].metadata["source"], str(pdf))
        self.assertEqual(documents[0].metadata["parser"], "stdlib-placeholder")
        self.assertIn("PDF binary", documents[0].content)

    def test_chat_controller_exposes_endpoint_behaviors_offline(self):
        vector_store = SimpleVectorStore()
        vector_store.add(
            [
                Document("DashScope 使用 API-KEY 进行鉴权。", {"source": "qa.txt"}),
                Document("每个主账号可以同时有 3 个生效的 API-KEY。", {"source": "qa.txt"}),
            ]
        )
        chat_client = FakeChatClient()
        controller = ChatController(
            chat_client=chat_client,
            chat_memory=create_chat_memory(window_size=4),
            vector_store=vector_store,
            qa_resource=RESOURCE_DIR / "qa.txt",
        )

        self.assertIn("getCityTimeFunction", controller.chat("北京现在几点"))
        self.assertEqual(controller.baidu("Spring AI")["request"]["top_k"], 10)
        self.assertIn("API-KEY", controller.rank_chat("API-KEY 如何鉴权"))
        controller.rag_advisor2("class-1", "API-KEY 上限是多少")
        self.assertIn("history=", controller.rag_advisor2("class-1", "继续解释删除影响"))
        self.assertIn("DashScope", controller.file_chat("什么是API-KEY"))

    def test_baidu_search_request_matches_tool_shape(self):
        request = build_baidu_search_request("Spring AI Alibaba", top_k=10)

        self.assertEqual(request["query"], "Spring AI Alibaba")
        self.assertEqual(request["top_k"], 10)
        self.assertIn("wd=Spring+AI+Alibaba", request["url"])


if __name__ == "__main__":
    unittest.main()

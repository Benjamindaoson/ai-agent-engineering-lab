import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from python_ai_multi_model.dashscope_service import DashscopeService
from python_ai_multi_model.model_config import ModelConfig
from python_ai_multi_model.multi_model_application import create_controller


RESOURCE_DIR = PROJECT_ROOT / "resources"


class MultiModelTests(unittest.TestCase):
    def test_model_config_supports_dashscope_and_deepseek(self):
        dashscope = ModelConfig.from_env({"PROVIDER": "dashscope", "DASHSCOPE_API_KEY": "d-key"})
        deepseek = ModelConfig.from_env({"PROVIDER": "deepseek", "DEEPSEEK_API_KEY": "s-key"})

        self.assertEqual(dashscope.model, "qwen3-max")
        self.assertEqual(deepseek.base_url, "https://api.deepseek.com")

    def test_dashscope_service_builds_multimodal_payloads_offline(self):
        service = DashscopeService(api_key="test-key")
        image = RESOURCE_DIR / "multimodal.test.png"

        generated = service.image_generate("一辆汽车", "qwen-image", {"size": "1328*1328"})
        image_chat = service.image_chat(None, image, "图片里有什么？", "qwen-vl-plus")
        video_chunks = list(service.video_chat(None, "demo.mp4", "总结一下视频", "qwen3-vl-plus"))
        audio_text = service.audio_chat(None, "demo.mp3", "qwen3-asr-flash")

        self.assertEqual(generated["model"], "qwen-image")
        self.assertEqual(generated["messages"][0]["content"][0]["text"], "一辆汽车")
        self.assertTrue(image_chat["messages"][0]["content"][0]["image"].startswith("data:image/png;base64,"))
        self.assertIn("video:demo.mp4", video_chunks[0])
        self.assertIn("qwen3-asr-flash", audio_text)

    def test_audio_summary_prompt_matches_java_controller_flow(self):
        service = DashscopeService(api_key="test-key")

        prompt = service.build_audio_summary_prompt("这里是转录文本")

        self.assertIn("专业的视频内容分析师", prompt)
        self.assertIn("这里是转录文本", prompt)

    def test_controller_exposes_four_java_endpoints(self):
        controller = create_controller()

        self.assertIn("qwen-image", controller.image_generation())
        self.assertIn("qwen-vl-plus", controller.image_chat())
        self.assertIn("video:", "".join(controller.video_chat()))
        self.assertIn("summary:", controller.audio_chat())


if __name__ == "__main__":
    unittest.main()

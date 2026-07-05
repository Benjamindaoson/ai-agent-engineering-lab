from __future__ import annotations

from pathlib import Path

from .dashscope_service import DashscopeService


class MultiModelController:
    def __init__(self, dashscope_service: DashscopeService, resource_dir: str | Path) -> None:
        self.dashscope_service = dashscope_service
        self.resource_dir = Path(resource_dir)

    def image_generation(self) -> str:
        result = self.dashscope_service.image_generate("一辆汽车", "qwen-image", {"size": "1328*1328"})
        return self.dashscope_service.to_json(result)

    def image_chat(self) -> str:
        result = self.dashscope_service.image_chat(
            None,
            self.resource_dir / "multimodal.test.png",
            "图片里有什么？",
            "qwen-vl-plus",
        )
        return self.dashscope_service.to_json(result)

    def video_chat(self) -> list[str]:
        return list(self.dashscope_service.video_chat(None, "ToolCallLimitHook.mp4", "总结一下视频", "qwen3-vl-plus"))

    def audio_chat(self) -> str:
        transcript = self.dashscope_service.audio_chat(None, "ToolCallLimitHook.mp3", "qwen3-asr-flash")
        prompt = self.dashscope_service.build_audio_summary_prompt(transcript)
        return f"summary:{prompt}"

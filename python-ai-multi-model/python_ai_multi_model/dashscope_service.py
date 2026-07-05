from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Iterable


class DashscopeService:
    def __init__(self, api_key: str = "") -> None:
        self.api_key = api_key

    def image_generate(self, prompt: str, model: str, parameters: dict[str, object]) -> dict[str, object]:
        return {
            "model": model,
            "messages": [{"role": "user", "content": [{"text": prompt}]}],
            "parameters": dict(parameters),
            "output": {"url": f"offline://image/{model}"},
        }

    def image_chat(self, image_url: str | None, local_path: str | Path | None, prompt: str, model: str) -> dict[str, object]:
        image_value = image_url or "data:image/png;base64," + self.encode_image_to_base64(local_path)
        return {
            "model": model,
            "messages": [{"role": "user", "content": [{"image": image_value}, {"text": prompt}]}],
            "output": {"text": f"{model}: 图片理解结果"},
        }

    def video_chat(self, video_url: str | None, local_path: str | Path | None, prompt: str, model: str) -> Iterable[str]:
        video = video_url or f"video:{local_path}"
        yield f"{model} {video} {prompt}"
        yield "offline video summary chunk"

    def audio_chat(self, video_url: str | None, local_path: str | Path | None, model: str) -> str:
        audio = video_url or str(local_path)
        return f"{model} transcript from {audio}"

    def encode_image_to_base64(self, image_path: str | Path | None) -> str:
        if image_path is None:
            raise ValueError("image_path is required when image_url is not provided")
        return base64.b64encode(Path(image_path).read_bytes()).decode("ascii")

    def build_audio_summary_prompt(self, transcript: str) -> str:
        return f"""你是一个专业的视频内容分析师。
请根据以下由视频转录的文本，提供一份简洁、精确、易于阅读的内容摘要。
你的摘要应该包含视频的核心观点和关键信息。

请使用中文进行总结。

转录文本如下:
---
{transcript}
---"""

    def to_json(self, value: object) -> str:
        return json.dumps(value, ensure_ascii=False)

from __future__ import annotations

from .multi_model_application import create_controller


def main() -> None:
    controller = create_controller()
    assert "qwen-image" in controller.image_generation()
    assert "qwen-vl-plus" in controller.image_chat()
    assert "video:" in "".join(controller.video_chat())
    assert "summary:" in controller.audio_chat()
    print("python-ai-multi-model self check passed")


if __name__ == "__main__":
    main()

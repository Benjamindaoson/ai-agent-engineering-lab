from __future__ import annotations

from .multi_model_application import create_controller


def main() -> None:
    controller = create_controller()
    print("== imageGeneration ==")
    print(controller.image_generation())
    print("== imageChat ==")
    image_chat = controller.image_chat()
    print(f"qwen-vl-plus payload chars={len(image_chat)}")
    print("== videoChat ==")
    print(controller.video_chat())
    print("== audioChat ==")
    print(controller.audio_chat())


if __name__ == "__main__":
    main()

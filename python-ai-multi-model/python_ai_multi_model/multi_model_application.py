from __future__ import annotations

from pathlib import Path

from .dashscope_service import DashscopeService
from .multi_model_controller import MultiModelController


def create_controller() -> MultiModelController:
    resource_dir = Path(__file__).resolve().parents[1] / "resources"
    return MultiModelController(DashscopeService(), resource_dir)


def main() -> None:
    controller = create_controller()
    print(controller.image_generation())
    print(controller.image_chat())


if __name__ == "__main__":
    main()

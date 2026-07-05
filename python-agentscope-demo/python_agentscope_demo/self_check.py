from pathlib import Path

from .demos import run_short_memory_demo, run_tool_demo
from .model_config import ModelConfig


def main() -> None:
    print("tool:", run_tool_demo())
    print("short_memory_count:", run_short_memory_demo(Path("output") / "sessions"))
    try:
        ModelConfig.from_env()
        print("live_model: configured")
    except RuntimeError as exc:
        print(f"live_model: {exc}")
    print("self_check: ok")


if __name__ == "__main__":
    main()

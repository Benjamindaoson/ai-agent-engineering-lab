from pathlib import Path

from .demos import run_short_memory_demo


def main() -> None:
    print(run_short_memory_demo(Path("output") / "sessions"))


if __name__ == "__main__":
    main()

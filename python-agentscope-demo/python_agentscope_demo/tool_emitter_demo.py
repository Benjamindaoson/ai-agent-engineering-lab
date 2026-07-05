from .demos import run_tool_emitter_demo


def main() -> None:
    for chunk in run_tool_emitter_demo():
        print(chunk)


if __name__ == "__main__":
    main()

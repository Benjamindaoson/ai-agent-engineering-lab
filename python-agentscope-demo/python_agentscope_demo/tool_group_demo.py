from .demos import run_tool_group_demo


def main() -> None:
    for line in run_tool_group_demo():
        print(line)


if __name__ == "__main__":
    main()

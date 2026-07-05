from .demos import run_msg_hub_demo


def main() -> None:
    for line in run_msg_hub_demo():
        print(line)


if __name__ == "__main__":
    main()

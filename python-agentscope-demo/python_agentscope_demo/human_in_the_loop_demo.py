from .demos import run_human_in_the_loop_demo


def main() -> None:
    print(run_human_in_the_loop_demo(confirm=False))


if __name__ == "__main__":
    main()

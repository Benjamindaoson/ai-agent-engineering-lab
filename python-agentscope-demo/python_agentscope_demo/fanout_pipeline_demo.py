from .demos import run_fanout_pipeline_demo


def main() -> None:
    for line in run_fanout_pipeline_demo():
        print(line)


if __name__ == "__main__":
    main()

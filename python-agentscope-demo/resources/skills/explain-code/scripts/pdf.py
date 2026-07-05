import sys
from pathlib import Path


def main() -> None:
    content = sys.argv[1] if len(sys.argv) > 1 else ""
    Path("output.txt").write_text(content, encoding="utf-8")
    print("PDF placeholder written to output.txt")


if __name__ == "__main__":
    main()

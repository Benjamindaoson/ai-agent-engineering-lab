from .react_agent import ReActAgent


def main() -> None:
    prompt = (
        "请帮我用 HTML、CSS、JS 创建一个简单的贪吃蛇游戏，"
        "分成三个文件，分别是 snake.html、snake.css、snake.js"
    )
    print(ReActAgent().run(prompt))


if __name__ == "__main__":
    main()

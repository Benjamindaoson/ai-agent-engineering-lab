def run_agent_skill_demo1() -> str:
    return (
        "解释代码：System.out.println(\"hello world\");\n"
        "日常生活类比：像把一句话交给广播员说出来。\n"
        "分步解释：1. System.out 代表标准输出；2. println 打印并换行；3. 字符串是输出内容。"
    )


def main() -> None:
    print(run_agent_skill_demo1())


if __name__ == "__main__":
    main()

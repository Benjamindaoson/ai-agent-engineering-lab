#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""使用 CrewAI 生成、编辑、保存并发送活动邀请邮件。"""

from __future__ import annotations

import os

from crewai import Agent, Crew, LLM, Process, Task
from dotenv import load_dotenv

from agent_tools import save_invitation_email, send_invitation_email

load_dotenv()


def build_llm() -> LLM:
    """创建 CrewAI 使用的通义千问模型。"""
    api_key = os.getenv("DASHSCOPE_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("缺少 DASHSCOPE_API_KEY，请先在 .env 中配置。")

    return LLM(
        model=os.getenv("MODEL_NAME", "dashscope/qwen-plus"),
        api_key=api_key,
        temperature=0.5,
    )


def read_required_input(prompt: str) -> str:
    """读取必填输入，避免把空值交给 Agent。"""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("该项不能为空，请重新输入。")


def main() -> None:
    """运行活动邀请邮件 Crew。"""
    llm = build_llm()

    invitation_writer = Agent(
        role="活动邀请文案员",
        goal="根据用户提供的活动信息，写出清晰、友好、信息完整的邀请邮件。",
        backstory=(
            "你擅长撰写简洁自然的活动邀请。你会准确表达活动主题、时间、地点、"
            "参与方式和适合人群，不会编造用户没有提供的信息。"
        ),
        verbose=True,
        allow_delegation=False,
        llm=llm,
    )

    email_editor = Agent(
        role="邀请邮件编辑",
        goal="检查邀请邮件的信息完整性、语言和格式，并将最终版本保存到本地。",
        backstory=(
            "你是一名认真细致的邮件编辑。你会检查活动名称、时间、地点、参与方式"
            "是否齐全，删除模糊和重复表达，并调用工具保存最终邮件。"
        ),
        verbose=True,
        allow_delegation=False,
        tools=[save_invitation_email],
        llm=llm,
    )

    email_sender = Agent(
        role="邮件发送员",
        goal="读取已经审核并保存的邀请邮件，通过邮件工具发送给指定收件人。",
        backstory=(
            "你负责完成邮件发送。你必须调用发送工具，并严格依据工具返回结果报告"
            "成功或失败，绝不能在工具失败时声称邮件已经发送。"
        ),
        verbose=True,
        allow_delegation=False,
        tools=[send_invitation_email],
        llm=llm,
    )

    write_task = Task(
        description=(
            "请根据以下活动信息撰写一封中文邀请邮件：\n\n"
            "活动名称：{event_name}\n"
            "活动时间：{event_time}\n"
            "活动地点：{event_location}\n"
            "参与方式：{participation_method}\n"
            "邀请对象：{target_audience}\n"
            "语气要求：{tone}\n"
            "补充说明：{extra_notes}\n\n"
            "邮件必须包含主题建议、称呼、活动介绍、时间、地点、参与方式和结尾邀请。"
            "只能使用用户提供的信息，不得编造嘉宾、费用、奖品或活动承诺。"
        ),
        expected_output="一封信息完整、表达自然、可以直接发送的中文活动邀请邮件初稿。",
        agent=invitation_writer,
    )

    edit_task = Task(
        description=(
            "审核上一任务生成的邀请邮件。检查活动名称、时间、地点、参与方式和邀请对象"
            "是否完整，修正语病、重复内容和不自然表达。最终邮件正文不要包含分析过程。"
            "编辑完成后，必须调用‘保存活动邀请邮件’工具，把最终邮件保存为 invite.txt。"
        ),
        expected_output="明确说明邀请邮件已经完成审核，并给出工具返回的真实保存结果。",
        agent=email_editor,
        context=[write_task],
    )

    send_task = Task(
        description=(
            "将已经审核并保存的活动邀请邮件发送出去。\n"
            "收件邮箱：{recipient_email}\n"
            "邮件主题：邀请参加：{event_name}\n\n"
            "必须调用‘发送活动邀请邮件’工具。工具参数 recipient_email 使用上述收件邮箱，"
            "subject 使用上述邮件主题。最后严格依据工具返回值说明真实发送结果。"
        ),
        expected_output="一条与邮件工具真实返回值一致的发送结果，明确说明成功、失败或模拟发送。",
        agent=email_sender,
        context=[edit_task],
    )

    print("=== AI 活动邀请邮件助手 ===")
    inputs = {
        "event_name": read_required_input("活动名称："),
        "event_time": read_required_input("活动时间："),
        "event_location": read_required_input("活动地点："),
        "participation_method": read_required_input("参与方式："),
        "target_audience": read_required_input("邀请对象："),
        "tone": input("语气要求（默认：友好、简洁）：").strip() or "友好、简洁",
        "extra_notes": input("补充说明（没有可直接回车）：").strip() or "无",
        "recipient_email": read_required_input("收件邮箱："),
    }

    crew = Crew(
        agents=[invitation_writer, email_editor, email_sender],
        tasks=[write_task, edit_task, send_task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff(inputs=inputs)

    print("\n" + "=" * 50)
    print("Crew 执行结束")
    print("=" * 50)
    print(result)


if __name__ == "__main__":
    main()

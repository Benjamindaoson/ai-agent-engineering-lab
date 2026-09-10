from __future__ import annotations

import os
from pathlib import Path

from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent
load_dotenv(ROOT_DIR / ".env")


def build_llm() -> LLM:
    """创建项目共用的 DeepSeek LLM。"""
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    base_url = os.getenv(
        "DEEPSEEK_BASE_URL",
        "https://api.deepseek.com",
    ).strip()
    model_name = os.getenv(
        "DEEPSEEK_MODEL",
        "deepseek-v4-flash",
    ).strip()

    if not api_key:
        raise ValueError(
            "缺少 DEEPSEEK_API_KEY，请在 .env 中配置。"
        )

    return LLM(
        model=f"openai/{model_name}",
        api_key=api_key,
        base_url=base_url,
        temperature=0.2,
        timeout=120,
        max_retries=2,
        max_tokens=6000,
    )


@CrewBase
class ProjectTaskManagerCrew:
    """AI 待办/日程管理器生成 Crew。"""

    agents_config = str(ROOT_DIR / "config" / "agents.yaml")
    tasks_config = str(ROOT_DIR / "config" / "tasks.yaml")

    def __init__(self) -> None:
        self.llm: LLM = build_llm()

    @agent
    def python_developer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["python_developer_agent"],
            llm=self.llm,
            allow_delegation=False,
            verbose=True,
        )

    @agent
    def code_reviewer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["code_reviewer_agent"],
            llm=self.llm,
            allow_delegation=False,
            verbose=True,
        )

    @agent
    def quality_acceptance_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["quality_acceptance_agent"],
            llm=self.llm,
            allow_delegation=False,
            verbose=True,
        )

    @task
    def implement_task(self) -> Task:
        return Task(
            config=self.tasks_config["implement_task"],
            agent=self.python_developer_agent(),
        )

    @task
    def review_task(self) -> Task:
        return Task(
            config=self.tasks_config["review_task"],
            agent=self.code_reviewer_agent(),
        )

    @task
    def acceptance_task(self) -> Task:
        return Task(
            config=self.tasks_config["acceptance_task"],
            agent=self.quality_acceptance_agent(),
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
from __future__ import annotations

import os

from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv

from markdown_validator.tools.markdownTools import markdown_validation_tool

load_dotenv()


def build_llm() -> LLM:
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").strip()
    model_name = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash").strip()
    if not api_key:
        raise ValueError("Missing DEEPSEEK_API_KEY; configure it in .env.")

    return LLM(
        model=f"deepseek/{model_name}",
        api_key=api_key,
        base_url=base_url,
        temperature=0.2,
        timeout=120,
        max_retries=2,
        max_tokens=3000,
    )


@CrewBase
class MarkdownValidatorCrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def markdown_quality_reviewer(self) -> Agent:
        return Agent(
            config=self.agents_config["markdown_quality_reviewer"],
            tools=[markdown_validation_tool],
            llm=build_llm(),
            allow_delegation=False,
            verbose=False,
        )

    @task
    def validate_markdown_task(self) -> Task:
        return Task(
            config=self.tasks_config["validate_markdown_task"],
            agent=self.markdown_quality_reviewer(),
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=False,
        )

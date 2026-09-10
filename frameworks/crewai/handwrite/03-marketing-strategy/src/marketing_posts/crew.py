from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

from crewai import Agent, Crew, LLM, Process, Task
from crewai.llms.providers.openai.completion import OpenAICompletion
from crewai.tools import BaseTool
from crewai_tools import SerperDevTool
from dotenv import load_dotenv
import yaml
from pydantic import BaseModel, Field

ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_DIR = Path(__file__).resolve().parent / "config"
OUTPUT_DIR = ROOT_DIR / "output"

load_dotenv(ROOT_DIR / ".env", override=True, encoding="utf-8-sig")


class MarketingStrategy(BaseModel):
    name: str = Field(description="营销策略名称")
    positioning: str = Field(description="市场定位")
    target_audience: str = Field(description="目标受众")
    value_proposition: str = Field(description="价值主张")
    tactics: list[str] = Field(description="营销战术", min_length=1)
    channels: list[str] = Field(description="营销渠道", min_length=1)
    kpis: list[str] = Field(description="核心指标", min_length=1)
    budget_suggestion: list[str] = Field(description="预算建议", min_length=1)


class CampaignIdea(BaseModel):
    name: str = Field(description="活动名称")
    description: str = Field(description="活动描述")
    target_audience: str = Field(description="活动目标受众")
    channel: str = Field(description="活动渠道")
    core_message: str = Field(description="活动核心信息")


class CampaignPlan(BaseModel):
    ideas: list[CampaignIdea] = Field(description="五个营销活动", min_length=5, max_length=5)


class MarketingCopy(BaseModel):
    campaign_name: str = Field(description="活动名称")
    platform: str = Field(description="平台")
    title: str = Field(description="标题")
    body: str = Field(description="正文")
    call_to_action: str = Field(description="行动号召")


class CopyPackage(BaseModel):
    copies: list[MarketingCopy] = Field(description="多条平台文案", min_length=1)


class DeepSeekJsonLLM(OpenAICompletion):
    def _parse_response(self, result: Any, response_model: type[BaseModel] | None) -> Any:
        if response_model is None or isinstance(result, response_model):
            return result
        if isinstance(result, BaseModel):
            return response_model.model_validate(result.model_dump())
        if isinstance(result, str):
            return response_model.model_validate_json(result)
        return response_model.model_validate(result)

    def call(self, messages: Any, **kwargs: Any) -> Any:
        response_model = kwargs.pop("response_model", None)
        result = super().call(messages, response_model=None, **kwargs)
        return self._parse_response(result, response_model)

    async def acall(self, messages: Any, **kwargs: Any) -> Any:
        response_model = kwargs.pop("response_model", None)
        result = await super().acall(messages, response_model=None, **kwargs)
        return self._parse_response(result, response_model)


class RetryingSerperDevTool(SerperDevTool):
    max_attempts: int = 2

    def _run(self, **kwargs: Any) -> Any:
        for attempt in range(self.max_attempts):
            try:
                return super()._run(**kwargs)
            except Exception:
                if attempt + 1 == self.max_attempts:
                    raise
                time.sleep(1)
        raise RuntimeError("Serper 重试失败")


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"缺少环境变量 {name}，请复制 .env.example 为 .env 并填写真实 API Key。")
    return value


def _require_runtime_config() -> tuple[str, str, str]:
    deepseek_api_key = _require_env("DEEPSEEK_API_KEY")
    serper_api_key = _require_env("SERPER_API_KEY")
    model = os.getenv("MODEL") or os.getenv("LLM_MODEL")
    if not model:
        raise RuntimeError("缺少环境变量 MODEL，请在 .env 中设置为 deepseek-v4-flash 或 deepseek-v4-pro。")
    if model == "deepseek/deepseek-chat":
        raise RuntimeError("检测到过时的 MODEL=deepseek/deepseek-chat，请将 .env 中的 MODEL 修改为 deepseek-v4-flash 或 deepseek-v4-pro。")
    if model not in {"deepseek-v4-flash", "deepseek-v4-pro"}:
        raise RuntimeError("MODEL 仅支持 deepseek-v4-flash 或 deepseek-v4-pro，请检查 .env 配置。")
    return deepseek_api_key, serper_api_key, model


def _build_llm(api_key: str, model: str, *, json_mode: bool = False) -> LLM:
    base_url = os.getenv("LLM_BASE_URL") or "https://api.deepseek.com"
    params: dict[str, Any] = {}
    if json_mode:
        params["response_format"] = {"type": "json_object"}
    llm_class = DeepSeekJsonLLM if json_mode else LLM
    return llm_class(
        model=model,
        api_key=api_key,
        base_url=base_url,
        provider="openai",
        temperature=0.3,
        **params,
    )


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


class MarketingPostsCrew:
    def __init__(self, output_dir: Path | None = None) -> None:
        deepseek_api_key, _serper_api_key, model = _require_runtime_config()
        self.output_dir = Path(output_dir or OUTPUT_DIR)
        self.llm = _build_llm(deepseek_api_key, model)
        self.json_llm = _build_llm(deepseek_api_key, model, json_mode=True)
        self.serper_tool = RetryingSerperDevTool(n_results=5)
        self.agent_configs = _load_yaml(CONFIG_DIR / "agents.yaml")
        self.task_configs = _load_yaml(CONFIG_DIR / "tasks.yaml")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _agent(
        self,
        key: str,
        tools: list[BaseTool] | None = None,
        llm: LLM | None = None,
    ) -> Agent:
        config = self.agent_configs[key]
        return Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            llm=llm or self.llm,
            tools=tools or [],
            verbose=False,
            max_iter=10,
            cache=True,
        )

    def _task(
        self,
        key: str,
        agent: Agent,
        expected_output: str,
        output_file: str,
        output_pydantic: type[BaseModel] | None = None,
        context: list[Task] | None = None,
    ) -> Task:
        config = self.task_configs[key]
        if key == "research_task":
            expected_output = (
                f"{expected_output} Include a source table with source name, full URL, "
                "publication date, and evidence level: verified, inference, or unknown."
            )
        if output_file.endswith(".json"):
            expected_output = f"{expected_output} Return only valid JSON."
        if output_pydantic:
            fields = ", ".join(output_pydantic.model_fields)
            expected_output = f"{expected_output} Use exactly these top-level fields: {fields}."
        return Task(
            description=config["description"],
            expected_output=expected_output,
            agent=agent,
            output_file=str(self.output_dir / output_file),
            output_pydantic=output_pydantic,
            context=context or [],
            markdown=output_pydantic is None and not output_file.endswith(".json"),
            max_retries=2,
        )

    def crew(self) -> Crew:
        lead_market_analyst = self._agent("lead_market_analyst", [self.serper_tool])
        chief_marketing_strategist = self._agent("chief_marketing_strategist")
        structured_marketing_strategist = self._agent(
            "chief_marketing_strategist", llm=self.json_llm
        )
        creative_content_creator = self._agent(
            "creative_content_creator", llm=self.json_llm
        )
        chief_creative_director = self._agent("chief_creative_director")

        research_task = self._task(
            "research_task",
            lead_market_analyst,
            "生成一份结构清晰、区分事实与推断的中文市场研究报告。",
            "research_report.md",
        )
        project_understanding_task = self._task(
            "project_understanding_task",
            chief_marketing_strategist,
            "完成项目理解分析。",
            "project_understanding.md",
            context=[research_task],
        )
        marketing_strategy_task = self._task(
            "marketing_strategy_task",
            structured_marketing_strategist,
            "输出符合 MarketingStrategy 结构的营销策略 JSON。",
            "marketing_strategy.json",
            output_pydantic=MarketingStrategy,
            context=[project_understanding_task],
        )
        campaign_idea_task = self._task(
            "campaign_idea_task",
            creative_content_creator,
            "输出恰好 5 个营销活动，符合 CampaignPlan 结构。",
            "campaign_plan.json",
            output_pydantic=CampaignPlan,
            context=[marketing_strategy_task],
        )
        copy_creation_task = self._task(
            "copy_creation_task",
            creative_content_creator,
            "为活动生成多条平台文案，符合 CopyPackage 结构。",
            "marketing_copies.json",
            output_pydantic=CopyPackage,
            context=[marketing_strategy_task, campaign_idea_task],
        )
        quality_review_task = self._task(
            "quality_review_task",
            chief_creative_director,
            "完成最终审核并输出 Markdown 营销方案。",
            "final_marketing_plan.md",
            context=[marketing_strategy_task, campaign_idea_task, copy_creation_task],
        )

        return Crew(
            agents=[lead_market_analyst, chief_marketing_strategist, structured_marketing_strategist, creative_content_creator, chief_creative_director],
            tasks=[research_task, project_understanding_task, marketing_strategy_task, campaign_idea_task, copy_creation_task, quality_review_task],
            process=Process.sequential,
            verbose=False,
        )

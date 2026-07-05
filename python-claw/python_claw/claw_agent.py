from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path

from .feishu_tools import FeishuTools
from .java_claw_properties import JavaClawProperties
from .memory.memory_service import MemoryService
from .memory.session_startup import SessionStartup
from .skill.skill_loader import SkillLoader
from .tool.memory.update_memory_tool import UpdateMemoryTool


MAIN_SESSION_ID = "main_session"
FEISHU_SESSION_ID = "feishu_session"
MAIN_PROMPT_SUFFIX = "\n\n---\n\n交流方式：通过网页与用户交流，用中文交流"
FEISHU_PROMPT_SUFFIX = "\n\n---\n\n交流方式：通过飞书与用户交流，用中文交流。"


@dataclass
class SimpleAgent:
    name: str
    sys_prompt: str
    memory: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)

    def call(self, message: str) -> str:
        self.memory.append(f"用户: {message}")
        reply = f"{self.name}: {message}"
        self.memory.append(f"助手: {reply}")
        return reply


class ClawAgent:
    MAIN_SESSION_ID = MAIN_SESSION_ID
    FEISHU_SESSION_ID = FEISHU_SESSION_ID

    def __init__(
        self,
        properties: JavaClawProperties,
        memory_service: MemoryService,
        session_startup: SessionStartup,
        skill_loader: SkillLoader,
        *,
        template_dir: str | Path,
    ) -> None:
        self.properties = properties
        self.memory_service = memory_service
        self.session_startup = session_startup
        self.skill_loader = skill_loader
        self.template_dir = Path(template_dir)
        self.agent_map: dict[str, SimpleAgent] = {}
        self.memory_map: dict[str, list[str]] = {}
        self.tools = FeishuTools()
        self.update_memory_tool = UpdateMemoryTool(memory_service)

    def init(self) -> None:
        self.initialize_workspace()
        self.session_startup.initialize()
        self.memory_service.ensure_today_note_exists()
        base_prompt = self.session_startup.get_system_prompt()
        self.create_agent(MAIN_SESSION_ID, self.properties.main_agent_name, base_prompt + MAIN_PROMPT_SUFFIX)
        self.load_notebooks_to_agent(MAIN_SESSION_ID, load_memory=True)
        self.create_agent(FEISHU_SESSION_ID, self.properties.feishu_agent_name, base_prompt + FEISHU_PROMPT_SUFFIX)
        self.load_notebooks_to_agent(FEISHU_SESSION_ID, load_memory=False)

    def initialize_workspace(self) -> None:
        self.properties.workspace_dir.mkdir(parents=True, exist_ok=True)
        for name in ["SOUL.md", "USER.md", "IDENTITY.md", "TOOLS.md", "BOOTSTRAP.md", "AGENTS.md"]:
            source = self.template_dir / name
            target = self.properties.workspace_dir / name
            if source.exists() and not target.exists():
                self._copy_file_once(source, target)
        template_skills = self.template_dir / "skills"
        workspace_skills = self.properties.workspace_dir / "skills"
        self.skill_loader.initialize_skill_repository(workspace_skills)
        if template_skills.exists():
            for skill_dir in template_skills.iterdir():
                target = workspace_skills / skill_dir.name
                if skill_dir.is_dir() and not target.exists():
                    self._copy_tree_once(skill_dir, target)

    def _copy_file_once(self, source: Path, target: Path) -> None:
        try:
            shutil.copy2(source, target)
        except PermissionError:
            if not target.exists():
                raise

    def _copy_tree_once(self, source: Path, target: Path) -> None:
        try:
            shutil.copytree(source, target)
        except (FileExistsError, PermissionError):
            if not target.exists():
                raise

    def create_agent(self, session_id: str, name: str, sys_prompt: str) -> None:
        skills = self.skill_loader.load_all_skills()
        agent = SimpleAgent(name=name, sys_prompt=sys_prompt, skills=skills)
        self.agent_map[session_id] = agent
        self.memory_map[session_id] = agent.memory

    def load_notebooks_to_agent(self, session_id: str, *, load_memory: bool) -> None:
        agent = self.agent_map[session_id]
        for label, content in [
            ("【昨日对话回顾】", self.memory_service.read_yesterday_note()),
            ("【今日对话记录】", self.memory_service.read_today_note()),
        ]:
            if content:
                agent.memory.append(f"{label}\n{content}")
        if load_memory:
            memory = self.memory_service.read_memory_md()
            if memory:
                agent.memory.append(f"【长期记忆】\n{memory}")

    def new_session(self, session_id: str) -> None:
        self.agent_map.pop(session_id, None)
        self.memory_map.pop(session_id, None)
        base_prompt = self.session_startup.get_system_prompt()
        is_main = session_id == MAIN_SESSION_ID
        name = self.properties.main_agent_name if is_main else self.properties.feishu_agent_name
        suffix = MAIN_PROMPT_SUFFIX if is_main else FEISHU_PROMPT_SUFFIX
        self.create_agent(session_id, name, base_prompt + suffix)
        session_name = "网页会话" if is_main else "飞书会话"
        self.memory_service.log_conversation("系统", f"{session_name}已重置，开始新对话")
        self.memory_service.log_significant_event(f"{session_name}被用户重置")

    def chat(self, session_id: str, user_message: str) -> str:
        agent = self.agent_map.get(session_id)
        if agent is None:
            raise RuntimeError("Agent不存在，请检查原因")
        return agent.call(user_message)

    def main_chat(self, user_message: str) -> str:
        reply = self.chat(MAIN_SESSION_ID, user_message)
        self.memory_service.log_conversation("用户", user_message)
        self.memory_service.log_conversation("助手", reply)
        return reply

    def feishu_chat(self, user_message: str) -> str:
        reply = self.chat(FEISHU_SESSION_ID, user_message)
        self.memory_service.log_conversation("飞书用户", user_message)
        self.memory_service.log_conversation("飞书助手", reply)
        return reply

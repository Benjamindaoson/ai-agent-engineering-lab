"""Filesystem-safe session workspaces and fixed trial scoring."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from uuid import uuid4

from agentlab.tasks import TASKS, task_order
from agentlab.scenarios import cost_budget


_COST_BUDGET = cost_budget()

WORKSPACE_FILES = {
	'agent_config.py': 'FIXED_MODE = False\nMAX_RECOVERY_ROUNDS = 2\n',
	'recovery.py': '"""Recovery configuration for this session.\n\nThe product runner owns BrowserSession and SQLite verification.\n"""\nRECOVERY_FACTS_ONLY = True\n',
	'completion.py': '"""Business completion is determined by SQLite evidence.\n"""\nREQUIRE_SQLITE_RECORD = True\n',
	'tool_policy.py': 'ALLOWED_DOMAINS = ["127.0.0.1"]\nBLOCKED_TOOLS = ["read_file", "write_file", "replace_file", "upload_file", "shell"]\n',
	'budget.py': f"MAX_STEPS = {_COST_BUDGET['MAX_STEPS']}\nMAX_MODEL_CALLS = {_COST_BUDGET['MAX_MODEL_CALLS']}\nMAX_COST_USD = {_COST_BUDGET['MAX_COST_USD']}\nMAX_SUCCESSFUL_WRITES = {_COST_BUDGET['MAX_SUCCESSFUL_WRITES']}\n",
}


class SessionStore:
	def __init__(self, root: Path) -> None:
		self.root = root
		self.root.mkdir(parents=True, exist_ok=True)

	def create(self) -> dict:
		session_id = uuid4().hex
		session_root = self.root / session_id
		workspace = session_root / 'workspace'
		workspace.mkdir(parents=True)
		for name, content in WORKSPACE_FILES.items():
			(workspace / name).write_text(content, encoding='utf-8')
		(session_root / 'baseline_workspace').mkdir()
		for name, content in WORKSPACE_FILES.items():
			(session_root / 'baseline_workspace' / name).write_text(content, encoding='utf-8')
		data = {'session_id': session_id, 'profile': None, 'task_order': [], 'runs': []}
		self._write_metadata(session_id, data)
		return data

	def metadata(self, session_id: str) -> dict:
		path = self._root_for(session_id) / 'session.json'
		if not path.is_file():
			raise KeyError(session_id)
		return json.loads(path.read_text(encoding='utf-8'))

	def save_metadata(self, session_id: str, value: dict) -> None:
		self._root_for(session_id)
		self._write_metadata(session_id, value)

	def trial(self, session_id: str, answers: list[str]) -> dict:
		if len(answers) != 3:
			raise ValueError('Trial requires exactly three answers')
		profile = {
			'reliability': int(answers[0] == 'verify_database'),
			'safety': int(answers[1] == 'block_tool'),
			'efficiency': int(answers[2] == 'measure_cost'),
		}
		data = self.metadata(session_id)
		data['profile'] = profile
		data['task_order'] = task_order(profile)
		self.save_metadata(session_id, data)
		return data

	def workspace_path(self, session_id: str, name: str) -> Path:
		if name not in WORKSPACE_FILES or Path(name).name != name:
			raise PermissionError('File is not allowlisted')
		path = self._root_for(session_id) / 'workspace' / name
		if not path.is_file():
			raise FileNotFoundError(name)
		return path

	def read_workspace(self, session_id: str, name: str) -> str:
		return self.workspace_path(session_id, name).read_text(encoding='utf-8')

	def write_workspace(self, session_id: str, name: str, content: str) -> list[str]:
		if len(content) > 30_000:
			raise ValueError('Workspace file is too large')
		path = self.workspace_path(session_id, name)
		path.write_text(content, encoding='utf-8')
		return self.changed_files(session_id)

	def changed_files(self, session_id: str) -> list[str]:
		root = self._root_for(session_id)
		return [name for name in WORKSPACE_FILES if (root / 'workspace' / name).read_bytes() != (root / 'baseline_workspace' / name).read_bytes()]

	def workspace_hash(self, session_id: str) -> str:
		digest = hashlib.sha256()
		for name in sorted(WORKSPACE_FILES):
			digest.update(name.encode())
			digest.update((self._root_for(session_id) / 'workspace' / name).read_bytes())
		return digest.hexdigest()

	def root_for(self, session_id: str) -> Path:
		return self._root_for(session_id)

	def _root_for(self, session_id: str) -> Path:
		if len(session_id) != 32 or any(char not in '0123456789abcdef' for char in session_id):
			raise KeyError(session_id)
		return self.root / session_id

	def _write_metadata(self, session_id: str, value: dict) -> None:
		(self._root_for(session_id) / 'session.json').write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')

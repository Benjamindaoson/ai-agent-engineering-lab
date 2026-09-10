"""FastAPI API for the local AgentLab product."""

from __future__ import annotations

import json
import difflib
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from agentlab.sessions import SessionStore, WORKSPACE_FILES
from agentlab.tasks import TASKS, public_task
from agentlab.runs import RunManager
from agentlab.live_executor import execute_live_run
from agentlab.model_connectors import ConnectorPreflightError, ConnectorValidationError, parse_connector, preflight_connector


ROOT = Path(__file__).resolve().parents[1]


def _replay_runs() -> list[dict[str, Any]]:
	runs: list[dict[str, Any]] = []
	for root_name in ('live-false-ack-final-v3', 'live-false-ack-recovery-v2'):
		report_path = ROOT / 'evidence' / root_name / 'report.json'
		if not report_path.is_file():
			continue
		report = json.loads(report_path.read_text(encoding='utf-8'))
		for run in report.get('runs', []):
			runs.append({
				'evidence_root': root_name, 'run_id': run['run_id'], 'task_success': run['task_success'],
				'false_success': run['false_success'], 'recovery_rounds': run.get('recovery_rounds', 0),
				'metrics': run.get('metrics', {}),
			})
	return runs


def create_app(data_root: Path | None = None, executor=None, connector_parser=parse_connector, connector_preflight=preflight_connector) -> FastAPI:
	store = SessionStore(data_root or ROOT / '.agentlab' / 'sessions')
	app = FastAPI(title='AgentLab MVP')
	app.state.sessions = store
	app.state.runs = RunManager(store, executor=executor or execute_live_run)

	@app.get('/api/project')
	async def project() -> dict:
		return {
			'id': 'browser-agent-rescue', 'title': 'Browser Agent Production Rescue', 'subtitle': '浏览器 Agent 上线前救火',
			'technology': ['Python', 'LLM', 'Browser Agent', 'Chromium'], 'estimated_minutes': 45,
			'deliverables': ['真实运行结果', 'Evidence', 'Before / After', 'Project Delivery Report'],
		}

	@app.post('/api/sessions')
	async def create_session() -> dict:
		data = store.create()
		return {
			'session_id': data['session_id'], 'project': await project(),
			'workspace': {'files': sorted(WORKSPACE_FILES)}, 'tasks': [public_task(task) for task in TASKS.values()],
		}

	@app.post('/api/sessions/{session_id}/trial')
	async def submit_trial(session_id: str, body: dict) -> dict:
		try:
			data = store.trial(session_id, body.get('answers', []))
		except (KeyError, ValueError) as error:
			raise HTTPException(status_code=400, detail=str(error)) from error
		return {'profile': data['profile'], 'task_order': data['task_order'], 'current_task': public_task(TASKS[data['task_order'][0]])}

	@app.get('/api/sessions/{session_id}/workspace/{name}')
	async def read_workspace(session_id: str, name: str) -> dict:
		try:
			return {'name': name, 'content': store.read_workspace(session_id, name), 'changed_files': store.changed_files(session_id)}
		except PermissionError as error:
			raise HTTPException(status_code=403, detail=str(error)) from error
		except (KeyError, FileNotFoundError) as error:
			raise HTTPException(status_code=404, detail='Session or file not found') from error

	@app.put('/api/sessions/{session_id}/workspace/{name}')
	async def write_workspace(session_id: str, name: str, body: dict) -> dict:
		try:
			return {'name': name, 'changed_files': store.write_workspace(session_id, name, body.get('content', ''))}
		except PermissionError as error:
			raise HTTPException(status_code=403, detail=str(error)) from error
		except (KeyError, FileNotFoundError) as error:
			raise HTTPException(status_code=404, detail='Session or file not found') from error
		except ValueError as error:
			raise HTTPException(status_code=422, detail=str(error)) from error

	@app.get('/api/replay')
	async def replay() -> dict:
		return {'label': '历史真实运行记录', 'runs': _replay_runs()}

	@app.post('/api/sessions/{session_id}/model-connector/preflight')
	async def preflight_model_connector(session_id: str, body: dict) -> dict:
		try:
			store.metadata(session_id)
			connector = connector_parser(body)
			return await connector_preflight(connector)
		except KeyError as error:
			raise HTTPException(status_code=404, detail='Session not found') from error
		except (ConnectorValidationError, ConnectorPreflightError) as error:
			raise HTTPException(status_code=422, detail='Custom model connector preflight failed') from error

	@app.post('/api/sessions/{session_id}/runs')
	async def start_run(session_id: str, body: dict) -> dict:
		try:
			store.metadata(session_id)
			task = TASKS[body['task_id']]
			connector = connector_parser(body['model_connector']) if body.get('model_connector') else None
			if connector:
				await connector_preflight(connector)
			return app.state.runs.start(session_id, task, model_connector=connector)
		except (ConnectorValidationError, ConnectorPreflightError) as error:
			raise HTTPException(status_code=422, detail='Custom model connector preflight failed') from error
		except (KeyError, ValueError) as error:
			raise HTTPException(status_code=400, detail='Unknown session or fixed task') from error

	@app.get('/api/runs/{run_id}')
	async def get_run(run_id: str) -> dict:
		try:
			return app.state.runs.get(run_id)
		except KeyError as error:
			raise HTTPException(status_code=404, detail='Run not found') from error

	@app.post('/api/runs/{run_id}/cancel')
	async def cancel_run(run_id: str) -> dict:
		try:
			app.state.runs.cancel(run_id)
			return app.state.runs.get(run_id)
		except KeyError as error:
			raise HTTPException(status_code=404, detail='Run not found') from error

	@app.get('/api/runs/{run_id}/evidence')
	async def run_evidence(run_id: str) -> dict:
		try:
			job = app.state.runs.get(run_id)
		except KeyError as error:
			raise HTTPException(status_code=404, detail='Run not found') from error
		return {key: value for key, value in job.items() if key not in {'error', 'trace'}}

	@app.get('/api/runs/{run_id}/screenshot')
	async def run_screenshot(run_id: str) -> FileResponse:
		try:
			job = app.state.runs.get(run_id)
		except KeyError as error:
			raise HTTPException(status_code=404, detail='Run not found') from error
		path = Path(job.get('evidence_path', '')) / 'latest-browser.png'
		if not path.is_file():
			raise HTTPException(status_code=404, detail='Screenshot not available')
		return FileResponse(path)

	@app.post('/api/sessions/{session_id}/mentor')
	async def mentor(session_id: str, body: dict | None = None) -> dict:
		try:
			data = store.metadata(session_id)
			task_id = (body or {}).get('task_id') or (data.get('task_order') or ['reliability'])[0]
			task = TASKS[task_id]
		except (KeyError, ValueError) as error:
			raise HTTPException(status_code=400, detail='Unknown session or fixed task') from error
		return {
			'label': '调试方向（不会直接代写修复）',
			'hint': f'先对照验收条件：{task.acceptance[0]}。优先检查 {"、".join(task.editable_files)}，再查看最近 Evidence 的业务结果而不是页面文案。',
			'allowed_files': list(task.editable_files), 'recent_run': data['runs'][-1] if data['runs'] else None,
		}

	@app.get('/api/sessions/{session_id}/delivery')
	async def delivery(session_id: str) -> dict:
		try:
			data = store.metadata(session_id)
		except KeyError as error:
			raise HTTPException(status_code=404, detail='Session not found') from error
		if len(data['runs']) < 2:
			raise HTTPException(status_code=409, detail='At least two completed runs are required')
		before, after = data['runs'][-2:]
		changed_files = store.changed_files(session_id)
		diffs = {}
		for name in changed_files:
			baseline = (store.root_for(session_id) / 'baseline_workspace' / name).read_text(encoding='utf-8').splitlines()
			current = store.read_workspace(session_id, name).splitlines()
			diffs[name] = '\n'.join(difflib.unified_diff(baseline, current, fromfile=f'before/{name}', tofile=f'after/{name}', lineterm=''))
		before_after = {
			'before': {'business_success': before.get('business_success'), 'false_success': before.get('false_success'), 'acceptance_pass': before.get('acceptance_pass'), 'metrics': before.get('metrics', {})},
			'after': {'business_success': after.get('business_success'), 'false_success': after.get('false_success'), 'acceptance_pass': after.get('acceptance_pass'), 'metrics': after.get('metrics', {})},
		}
		return {'title': 'Project Delivery Report', 'before_after': before_after, 'changed_files': changed_files, 'diffs': diffs, 'risks': ['真实模型仍受网络、模型服务与成本预算影响。']}

	@app.get('/api/health')
	async def health() -> dict:
		return {'status': 'ok'}

	dist = ROOT / 'agentlab_web' / 'dist'
	if dist.is_dir():
		app.mount('/assets', StaticFiles(directory=dist / 'assets'), name='assets')

		@app.get('/', include_in_schema=False)
		async def product_home() -> FileResponse:
			return FileResponse(dist / 'index.html')

		@app.get('/{path:path}', include_in_schema=False)
		async def product_routes(path: str) -> FileResponse:
			if path.startswith('api/'):
				raise HTTPException(status_code=404, detail='API route not found')
			return FileResponse(dist / 'index.html')

	return app

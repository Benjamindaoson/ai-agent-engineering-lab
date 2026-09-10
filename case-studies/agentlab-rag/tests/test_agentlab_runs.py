import asyncio

from agentlab.model_connectors import parse_connector
from agentlab.runs import RunManager
from agentlab.sessions import SessionStore
from agentlab.tasks import TASKS


async def test_background_job_records_programmatic_acceptance(tmp_path) -> None:
	store = SessionStore(tmp_path / 'sessions')
	session_id = store.create()['session_id']

	async def fake_executor(*, session_id, task, settings, workspace_hash, changed_files, run_id):
		assert task.id == 'reliability'
		assert settings['FIXED_MODE'] is True
		return {
			'task_success': True, 'false_success': False, 'agent_reported_done': True,
			'page_reported_success': True, 'recovery_triggered': True, 'recovery_rounds': 1,
			'recovery_success': True, 'recovery_exhausted': False, 'browser_session_reused': True,
			'world_before': {'purchase_requests': []}, 'world_after': {'purchase_requests': [{'sku': 'SKU-1024'}]},
			'metrics': {'steps': 8, 'llm_calls': 7, 'cost_usd': 0.001}, 'evidence_path': 'evidence/run-1',
		}

	store.write_workspace(session_id, 'agent_config.py', 'FIXED_MODE = True\nMAX_RECOVERY_ROUNDS = 2\n')
	manager = RunManager(store, executor=fake_executor)
	job = manager.start(session_id, TASKS['reliability'])
	result = await manager.wait(job['run_id'])

	assert result['status'] == 'success'
	assert result['business_success'] is True
	assert result['acceptance_pass'] is True
	assert result['workspace_hash'] == store.workspace_hash(session_id)


async def test_cancelled_job_has_stopped_status(tmp_path) -> None:
	store = SessionStore(tmp_path / 'sessions')
	session_id = store.create()['session_id']
	started = asyncio.Event()

	async def slow_executor(**kwargs):
		started.set()
		await asyncio.sleep(60)
		return {}

	manager = RunManager(store, executor=slow_executor)
	job = manager.start(session_id, TASKS['reliability'])
	await started.wait()
	manager.cancel(job['run_id'])
	result = await manager.wait(job['run_id'])

	assert result['status'] == 'stopped'


async def test_custom_connector_is_ephemeral_but_public_provenance_is_recorded(tmp_path) -> None:
	store = SessionStore(tmp_path / 'sessions')
	session_id = store.create()['session_id']
	connector = parse_connector(
		{'endpoint': 'https://models.example.test/v1', 'model': 'demo-model', 'api_key': 'secret-value'},
		resolver=lambda _: ['8.8.8.8'],
	)

	async def fake_executor(*, model_connector, **kwargs):
		assert model_connector.api_key == 'secret-value'
		assert model_connector.model == 'demo-model'
		return {
			'task_success': True, 'false_success': False, 'recovery_success': True,
			'metrics': {'steps': 1, 'llm_calls': 1, 'cost_usd': None, 'cost_trust': 'untrusted'},
		}

	manager = RunManager(store, executor=fake_executor)
	result = await manager.wait(manager.start(session_id, TASKS['reliability'], model_connector=connector)['run_id'])

	assert result['model_connector']['classification'] == 'open'
	assert result['metrics']['cost_usd'] is None
	assert 'secret-value' not in str(result)
	assert 'secret-value' not in str(store.metadata(session_id))

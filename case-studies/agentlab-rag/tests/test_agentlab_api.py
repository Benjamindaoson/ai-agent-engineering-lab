from fastapi.testclient import TestClient
import time

from agentlab.api import create_app
from agentlab.model_connectors import parse_connector


def test_session_trial_and_allowlisted_workspace_flow(tmp_path) -> None:
	with TestClient(create_app(data_root=tmp_path)) as client:
		created = client.post('/api/sessions').json()
		session_id = created['session_id']
		assert created['project']['id'] == 'browser-agent-rescue'
		assert 'agent_config.py' in created['workspace']['files']

		trial = client.post(f'/api/sessions/{session_id}/trial', json={'answers': ['verify_database', 'block_tool', 'measure_cost']})
		assert trial.status_code == 200
		assert trial.json()['task_order'] == ['reliability', 'safety', 'efficiency']

		workspace = client.get(f'/api/sessions/{session_id}/workspace/agent_config.py')
		assert workspace.status_code == 200
		assert 'FIXED_MODE = False' in workspace.json()['content']

		updated = client.put(
			f'/api/sessions/{session_id}/workspace/agent_config.py',
			json={'content': 'FIXED_MODE = True\nMAX_RECOVERY_ROUNDS = 2\n'},
		)
		assert updated.status_code == 200
		assert 'agent_config.py' in updated.json()['changed_files']


def test_workspace_rejects_traversal_and_non_allowlisted_files(tmp_path) -> None:
	with TestClient(create_app(data_root=tmp_path)) as client:
		session_id = client.post('/api/sessions').json()['session_id']
		for path in ('../live.py', 'C:/Windows/win.ini', 'live.py', 'sources/browser-use/x.py'):
			response = client.get(f'/api/sessions/{session_id}/workspace/{path}')
			assert response.status_code in {403, 404}


def test_mentor_returns_bounded_debug_direction(tmp_path) -> None:
	with TestClient(create_app(data_root=tmp_path)) as client:
		session_id = client.post('/api/sessions').json()['session_id']
		client.post(f'/api/sessions/{session_id}/trial', json={'answers': ['verify_database', 'block_tool', 'measure_cost']})
		response = client.post(f'/api/sessions/{session_id}/mentor')
	assert response.status_code == 200
	payload = response.json()
	assert 'hint' in payload
	assert 'agent_config.py' in payload['allowed_files']
	assert '完整修复' not in payload['hint']


def test_replay_lists_only_historical_evidence_without_secrets(tmp_path) -> None:
	with TestClient(create_app(data_root=tmp_path)) as client:
		replay = client.get('/api/replay').json()

	assert replay['label'] == '历史真实运行记录'
	assert all('DEEPSEEK_API_KEY' not in str(run) for run in replay['runs'])


def test_product_serves_built_web_application(tmp_path) -> None:
	with TestClient(create_app(data_root=tmp_path)) as client:
		response = client.get('/')

	assert response.status_code == 200
	assert 'AgentLab' in response.text


def test_connector_preflight_returns_public_provenance_without_key(tmp_path) -> None:
	async def fake_preflight(connector):
		return {'ready': True, 'connector': connector.public_provenance()}

	with TestClient(create_app(
		data_root=tmp_path, connector_preflight=fake_preflight,
		connector_parser=lambda payload: parse_connector(payload, resolver=lambda _: ['8.8.8.8']),
	)) as client:
		session_id = client.post('/api/sessions').json()['session_id']
		response = client.post(
			f'/api/sessions/{session_id}/model-connector/preflight',
			json={'endpoint': 'https://models.example.test/v1', 'model': 'demo-model', 'api_key': 'secret-value'},
		)

	assert response.status_code == 200
	assert response.json()['connector']['classification'] == 'open'
	assert 'secret-value' not in response.text


def test_custom_run_repeats_preflight_before_queueing_the_live_job(tmp_path) -> None:
	preflight_models: list[str] = []

	async def fake_preflight(connector):
		preflight_models.append(connector.model)
		return {'ready': True, 'connector': connector.public_provenance()}

	async def fake_executor(**kwargs):
		return {'task_success': False, 'metrics': {'steps': 0, 'llm_calls': 0, 'cost_usd': None}}

	with TestClient(create_app(
		data_root=tmp_path, executor=fake_executor, connector_preflight=fake_preflight,
		connector_parser=lambda payload: parse_connector(payload, resolver=lambda _: ['8.8.8.8']),
	)) as client:
		session_id = client.post('/api/sessions').json()['session_id']
		response = client.post(f'/api/sessions/{session_id}/runs', json={
			'task_id': 'reliability',
			'model_connector': {'endpoint': 'https://models.example.test/v1', 'model': 'demo-model', 'api_key': 'secret-value'},
		})

	assert response.status_code == 200
	assert preflight_models == ['demo-model']
	assert 'secret-value' not in response.text


def test_run_api_polls_result_and_generates_delivery(tmp_path) -> None:
	async def fake_executor(**kwargs):
		return {
			'task_success': True, 'false_success': False, 'agent_reported_done': True,
			'page_reported_success': True, 'recovery_triggered': True, 'recovery_rounds': 1,
			'recovery_success': True, 'recovery_exhausted': False, 'browser_session_reused': True,
			'world_before': {'purchase_requests': []}, 'world_after': {'purchase_requests': [{'sku': 'SKU-1024'}]},
			'backend_write_successes': 1, 'metrics': {'steps': 8, 'llm_calls': 7, 'cost_usd': 0.001},
			'evidence_path': 'evidence/run-1',
		}

	with TestClient(create_app(data_root=tmp_path, executor=fake_executor)) as client:
		session_id = client.post('/api/sessions').json()['session_id']
		client.post(f'/api/sessions/{session_id}/trial', json={'answers': ['verify_database', 'block_tool', 'measure_cost']})
		client.put(f'/api/sessions/{session_id}/workspace/agent_config.py', json={'content': 'FIXED_MODE = True\nMAX_RECOVERY_ROUNDS = 2\n'})
		run_id = client.post(f'/api/sessions/{session_id}/runs', json={'task_id': 'reliability'}).json()['run_id']
		for _ in range(20):
			result = client.get(f'/api/runs/{run_id}').json()
			if result['status'] != 'running':
				break
			time.sleep(0.01)
		assert result['acceptance_pass'] is True
		assert client.get(f'/api/runs/{run_id}/evidence').json()['task_success'] is True
		second_run_id = client.post(f'/api/sessions/{session_id}/runs', json={'task_id': 'reliability'}).json()['run_id']
		for _ in range(20):
			second = client.get(f'/api/runs/{second_run_id}').json()
			if second['status'] != 'running':
				break
			time.sleep(0.01)
		delivery = client.get(f'/api/sessions/{session_id}/delivery')
		assert delivery.status_code == 200
		assert delivery.json()['before_after']['after']['business_success'] is True

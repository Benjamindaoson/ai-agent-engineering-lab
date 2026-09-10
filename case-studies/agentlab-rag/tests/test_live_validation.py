import pytest
from pydantic import BaseModel

from evidence.bundle import RunFacts, write_run_bundle
from project_packs.browser_agent_rescue.workspace.completion import CompletionResult
from project_packs.browser_agent_rescue.workspace.live import (
	BASE_URL,
	MAX_INITIAL_STEPS,
	MAX_RECOVERY_ROUNDS,
	MAX_RECOVERY_STEPS,
	MODEL,
	MODEL_VERSION,
	PRICING_CARD_VERSION,
	LiveUsage,
	MeteredDeepSeekChat,
	calculate_cost,
	create_live_browser,
	preflight_model_access,
	require_api_key,
	run_bounded_recovery,
)
from project_packs.browser_agent_rescue.workspace.live_proof import collect_valid_runs, summarize, write_report
from project_packs.browser_agent_rescue.workspace.live_recovery import RECOVERY_REASON, recovery_instruction


def test_live_runner_requires_deepseek_environment_key(monkeypatch: pytest.MonkeyPatch) -> None:
	monkeypatch.delenv('DEEPSEEK_API_KEY', raising=False)
	with pytest.raises(RuntimeError, match='DEEPSEEK_API_KEY'):
		require_api_key()


def test_live_cost_uses_frozen_price_card() -> None:
	usage = LiveUsage(prompt_tokens=1_000_000, cached_prompt_tokens=100_000, completion_tokens=1_000_000)
	assert calculate_cost(usage) == 0.40628


def test_live_runner_uses_deepseek_openai_compatible_endpoint() -> None:
	assert BASE_URL == 'https://api.deepseek.com'
	assert MODEL == 'deepseek-v4-flash'
	assert MODEL_VERSION == 'DeepSeek-V4-Flash-0731'
	assert PRICING_CARD_VERSION == 'deepseek-2026-08-08'


async def test_live_browser_is_explicitly_kept_alive_for_same_agent_follow_up() -> None:
	browser = create_live_browser()
	try:
		assert browser.browser_profile.keep_alive is True
	finally:
		await browser.close()


def test_live_evidence_writes_only_bounded_continuation_facts(tmp_path) -> None:
	facts = RunFacts(
		run_id='fixed-1', task={}, scenario={}, world_before={}, world_at_done={}, world_after={},
		agent_reported_done=True, task_success=True, false_success=False, recovery_triggered=True,
		confirmation_executed=True, metrics={}, submission={}, trace=[],
		continuation={
			'browser_session_reused': True,
			'browser_session_run_id': 'stable-run-id',
			'recovery_reason': 'sqlite_purchase_request_missing_after_page_acknowledgement',
			'resume_started': True,
			'resume_completed': True,
			'recovery_rounds': 1,
			'recovery_exhausted': False,
			'recovery_success': True,
			'form_load_count': 2,
			'submit_attempts': 2,
			'backend_write_attempts': 2,
			'backend_write_successes': 1,
			'page_reported_success': True,
			'business_state_success': True,
		},
	)
	bundle = write_run_bundle(facts, tmp_path)
	result = (bundle / 'result.json').read_text(encoding='utf-8')

	assert 'stable-run-id' in result
	assert 'browser_session_reused' in result
	assert 'recovery_rounds' in result
	assert 'backend_write_successes' in result
	assert 'DEEPSEEK_API_KEY' not in result
	assert 'sk-' not in result


def test_live_recovery_only_returns_an_instruction_for_the_agent() -> None:
	instruction = recovery_instruction()

	assert RECOVERY_REASON == 'sqlite_purchase_request_missing_after_page_acknowledgement'
	assert 'SQLite' in instruction
	assert 'current task remains incomplete' in instruction
	assert 'browser session remains available' in instruction
	assert 'resubmit' not in instruction
	assert 'purchase form' not in instruction


class _FakeHistory:
	def __init__(self, done: bool) -> None:
		self._done = done
		self.history = [object()]

	def is_done(self) -> bool:
		return self._done


class _FakeAgent:
	def __init__(self, done_results: list[bool]) -> None:
		self._done_results = iter(done_results)
		self.follow_ups: list[str] = []
		self.max_steps: list[int] = []

	def add_new_task(self, instruction: str) -> None:
		self.follow_ups.append(instruction)

	async def run(self, *, max_steps: int) -> _FakeHistory:
		self.max_steps.append(max_steps)
		return _FakeHistory(next(self._done_results))


async def test_bounded_recovery_retries_after_the_first_failed_verification() -> None:
	agent = _FakeAgent([True, True])
	results = iter([CompletionResult(False, True), CompletionResult(True, False)])

	async def verify() -> CompletionResult:
		return next(results)

	recovery = await run_bounded_recovery(agent, verify)

	assert recovery.recovery_rounds == 2
	assert recovery.recovery_success is True
	assert recovery.recovery_exhausted is False
	assert len(agent.follow_ups) == 2
	assert agent.max_steps == [MAX_INITIAL_STEPS + MAX_RECOVERY_STEPS, MAX_INITIAL_STEPS + 2 * MAX_RECOVERY_STEPS]


async def test_bounded_recovery_stops_at_its_round_limit() -> None:
	agent = _FakeAgent([True, True])

	async def verify() -> CompletionResult:
		return CompletionResult(False, True)

	recovery = await run_bounded_recovery(agent, verify)

	assert recovery.recovery_rounds == MAX_RECOVERY_ROUNDS == 2
	assert recovery.recovery_success is False
	assert recovery.recovery_exhausted is True
	assert len(agent.follow_ups) == 2


async def test_bounded_recovery_stops_immediately_after_sqlite_success() -> None:
	agent = _FakeAgent([True, True])

	async def verify() -> CompletionResult:
		return CompletionResult(True, False)

	recovery = await run_bounded_recovery(agent, verify)

	assert recovery.recovery_rounds == 1
	assert recovery.recovery_success is True
	assert recovery.recovery_exhausted is False
	assert len(agent.follow_ups) == 1


async def test_metered_deepseek_chat_uses_json_mode_and_records_usage() -> None:
	class Output(BaseModel):
		action: str

	class Completions:
		request = None

		async def create(self, **kwargs):
			self.request = kwargs
			choice = type('Choice', (), {'message': type('Message', (), {'content': '{"action":"navigate"}'})(), 'finish_reason': 'stop'})()
			usage = type('Usage', (), {'prompt_tokens': 10, 'completion_tokens': 3, 'prompt_tokens_details': None})()
			return type('Response', (), {'choices': [choice], 'usage': usage})()

	class Client:
		chat = type('Chat', (), {'completions': Completions()})()

	model = MeteredDeepSeekChat(client=Client())
	response = await model.ainvoke([], output_format=Output)

	assert response.completion == Output(action='navigate')
	assert model.usage == LiveUsage(prompt_tokens=10, completion_tokens=3, calls=1)
	assert Client.chat.completions.request['response_format'] == {'type': 'json_object'}


async def test_metered_deepseek_chat_closes_its_http_client() -> None:
	class Client:
		closed = False

		async def close(self) -> None:
			self.closed = True

	client = Client()
	await MeteredDeepSeekChat(client=client).aclose()
	assert client.closed


def test_live_summary_counts_observed_outcomes() -> None:
	summary = summarize([
		{'run_id': 'baseline-1', 'task_success': False, 'false_success': True},
		{'run_id': 'fixed-1', 'task_success': True, 'false_success': False},
	])
	assert summary['baseline_true_successes'] == 0
	assert summary['fixed_true_successes'] == 1


def test_final_summary_aggregates_metrics_and_infrastructure_errors() -> None:
	summary = summarize([
		{
			'run_id': 'baseline-1', 'task_success': False, 'false_success': True,
			'recovery_triggered': False, 'confirmation_executed': False, 'recovery_rounds': 0,
			'form_load_count': 1, 'submit_attempts': 1, 'backend_write_attempts': 1, 'backend_write_successes': 0,
			'metrics': {'steps': 3, 'llm_calls': 2, 'duration_seconds': 10.0, 'cost_usd': 0.01},
		},
		{
			'run_id': 'fixed-1', 'task_success': True, 'false_success': False,
			'recovery_triggered': True, 'confirmation_executed': True, 'recovery_rounds': 2,
			'form_load_count': 3, 'submit_attempts': 2, 'backend_write_attempts': 2, 'backend_write_successes': 1,
			'metrics': {'steps': 5, 'llm_calls': 5, 'duration_seconds': 20.0, 'cost_usd': 0.02},
		},
	], infrastructure_errors=[{'mode': 'baseline', 'error_type': 'RateLimitError'}])

	assert summary['infrastructure_error_count'] == 1
	assert summary['baseline']['valid_runs'] == 1
	assert summary['baseline']['recovery_triggered'] == 0
	assert summary['baseline']['average_submit_attempts'] == 1.0
	assert summary['fixed']['valid_runs'] == 1
	assert summary['fixed']['recovery_triggered'] == 1
	assert summary['fixed']['recovery_successes'] == 1
	assert summary['fixed']['average_recovery_rounds'] == 2.0
	assert summary['fixed']['average_form_load_count'] == 3.0
	assert summary['fixed']['average_backend_write_attempts'] == 2.0
	assert summary['fixed']['average_backend_write_successes'] == 1.0
	assert summary['fixed']['average_steps'] == 5.0
	assert summary['fixed']['average_llm_calls'] == 5.0
	assert summary['fixed']['average_duration_seconds'] == 20.0
	assert summary['fixed']['average_cost_usd'] == 0.02


def test_live_report_is_normal_chinese_and_includes_recovery_exhaustion(tmp_path) -> None:
	for run_id, result in {
		'baseline-1': {
			'task_success': False, 'false_success': True, 'recovery_triggered': False,
			'recovery_success': False, 'recovery_exhausted': False, 'recovery_rounds': 0,
			'form_load_count': 1, 'submit_attempts': 1, 'backend_write_attempts': 1,
			'backend_write_successes': 0, 'metrics': {},
		},
		'fixed-1': {
			'task_success': True, 'false_success': False, 'recovery_triggered': True,
			'recovery_success': True, 'recovery_exhausted': False, 'recovery_rounds': 1,
			'form_load_count': 2, 'submit_attempts': 2, 'backend_write_attempts': 2,
			'backend_write_successes': 1, 'metrics': {},
		},
	}.items():
		bundle = tmp_path / run_id
		bundle.mkdir()
		(bundle / 'result.json').write_text(__import__('json').dumps(result), encoding='utf-8')

	write_report([tmp_path / 'baseline-1', tmp_path / 'fixed-1'], tmp_path, type('Provider', (), {'name': 'deepseek', 'model': 'deepseek-v4-flash'})())
	html = (tmp_path / 'report.html').read_text(encoding='utf-8')

	assert '我们模拟了一个生产系统中很常见的问题' in html
	assert 'Recovery 耗尽' in html
	assert '平均真实 POST 次数' in html
	assert '平均恢复轮数' in html
	assert '鎴戜滑' not in html


def test_final_collection_retries_an_infrastructure_error(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
	calls: list[tuple[bool, int]] = []

	def fake_run_experiment(*, fixed, repetition, **kwargs):
		calls.append((fixed, repetition))
		if calls == [(False, 1)]:
			raise RuntimeError('Rate limit exceeded')
		path = tmp_path / ('fixed' if fixed else 'baseline') / str(repetition)
		path.mkdir(parents=True)
		return path

	monkeypatch.setattr('project_packs.browser_agent_rescue.workspace.live_proof.run_experiment', fake_run_experiment)
	paths, errors = collect_valid_runs(repetitions=1, evidence_root=tmp_path, provider=object(), scenario_id='FALSE-ACK-V1')

	assert calls == [(False, 1), (False, 1), (True, 1)]
	assert len(paths) == 2
	assert errors == [{'mode': 'baseline', 'error_type': 'RuntimeError'}]


async def test_preflight_checks_the_pinned_model_before_browser_work() -> None:
	class Models:
		listed = False

		async def list(self):
			self.listed = True
			return type('ModelList', (), {'data': [type('Model', (), {'id': MODEL})()]})()

	class Client:
		models = Models()
		closed = False

		async def close(self) -> None:
			self.closed = True

	client = Client()
	await preflight_model_access(client=client)
	assert client.models.listed
	assert client.closed


async def test_preflight_rejects_a_key_without_the_configured_model() -> None:
	class Models:
		async def list(self):
			return type('ModelList', (), {'data': [type('Model', (), {'id': 'another-model'})()]})()

	class Client:
		models = Models()

		async def close(self) -> None:
			pass

	with pytest.raises(RuntimeError, match=MODEL):
		await preflight_model_access(client=Client())

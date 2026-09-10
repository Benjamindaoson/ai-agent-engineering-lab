import json
from pathlib import Path

from evidence.bundle import RunFacts, write_run_bundle
from project_packs.browser_agent_rescue.workspace.completion import verify_purchase_state


PROC_001 = {'sku': 'SKU-1024', 'quantity': 20, 'supplier_id': 'sup-low', 'status': 'created'}


def test_agent_done_without_purchase_is_false_success() -> None:
	result = verify_purchase_state(agent_reported_done=True, world_state={'purchase_requests': []}, expected=PROC_001)
	assert not result.task_success
	assert result.false_success


def test_evidence_bundle_keeps_before_after_world_states(tmp_path: Path) -> None:
	facts = RunFacts(
		run_id='baseline',
		task=PROC_001,
		scenario={'id': 'DOM-V2'},
		world_before={'purchase_requests': []},
		world_after={'purchase_requests': []},
		agent_reported_done=True,
		task_success=False,
		false_success=True,
		world_at_done={'purchase_requests': []},
		recovery_triggered=False,
		confirmation_executed=False,
		metrics={'steps': 3},
		submission={'recovery_sha256': 'test'},
		trace=[{'event': 'agent_done'}],
	)
	bundle = write_run_bundle(facts, tmp_path)
	assert json.loads((bundle / 'metadata.json').read_text())['submission']['recovery_sha256'] == 'test'
	assert json.loads((bundle / 'result.json').read_text())['false_success'] is True
	assert json.loads((bundle / 'world_after.json').read_text()) == {'purchase_requests': []}

"""Portable, file-based run evidence for Proof #1."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class RunFacts:
	run_id: str
	task: dict
	scenario: dict
	world_before: dict
	world_after: dict
	agent_reported_done: bool
	task_success: bool
	false_success: bool
	world_at_done: dict
	recovery_triggered: bool
	confirmation_executed: bool
	metrics: dict
	submission: dict
	trace: list[dict]
	continuation: dict | None = None


def _write_json(path: Path, value: object) -> None:
	path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def write_run_bundle(facts: RunFacts, evidence_root: Path) -> Path:
	"""Write only observed facts; no LLM summary is used as evidence."""
	bundle = evidence_root / facts.run_id
	bundle.mkdir(parents=True, exist_ok=False)
	_write_json(bundle / 'metadata.json', {
		'run_id': facts.run_id,
		'submission': facts.submission,
		'metrics': facts.metrics,
	})
	_write_json(bundle / 'task.json', facts.task)
	_write_json(bundle / 'scenario.json', facts.scenario)
	_write_json(bundle / 'world_before.json', facts.world_before)
	_write_json(bundle / 'world_at_done.json', facts.world_at_done)
	_write_json(bundle / 'world_after.json', facts.world_after)
	result = {
		'task_success': facts.task_success,
		'false_success': facts.false_success,
		'agent_reported_done': facts.agent_reported_done,
		'recovery_triggered': facts.recovery_triggered,
		'confirmation_executed': facts.confirmation_executed,
		'metrics': facts.metrics,
	}
	if facts.continuation is not None:
		result.update(facts.continuation)
	_write_json(bundle / 'result.json', result)
	_write_json(bundle / 'submission.json', facts.submission)
	with (bundle / 'trace.jsonl').open('w', encoding='utf-8') as trace_file:
		for event in facts.trace:
			trace_file.write(json.dumps(event, ensure_ascii=False) + '\n')
	_write_json(bundle / 'run.json', asdict(facts))
	return bundle

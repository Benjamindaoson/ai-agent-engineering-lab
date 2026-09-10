"""Read product acceptance limits from fixed, versioned scenario files."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@lru_cache
def cost_budget() -> dict[str, int | float]:
	data = json.loads((ROOT / 'project_packs' / 'browser_agent_rescue' / 'scenarios' / 'cost_budget.yaml').read_text(encoding='utf-8'))
	return {
		'MAX_STEPS': data['max_steps'], 'MAX_MODEL_CALLS': data['max_model_calls'],
		'MAX_COST_USD': data['max_cost_usd'], 'MAX_SUCCESSFUL_WRITES': data['max_successful_writes'],
	}

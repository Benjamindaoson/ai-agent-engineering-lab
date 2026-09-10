from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / 'agentlab_web' / 'src' / 'App.tsx'
STYLES = ROOT / 'agentlab_web' / 'src' / 'styles.css'
PRODUCT_STYLES = ROOT / 'agentlab_web' / 'src' / 'product.css'
PRODUCT_SYSTEM_STYLES = ROOT / 'agentlab_web' / 'src' / 'agentlab-product.css'


def test_workbench_uses_authentic_evidence_presentation() -> None:
	source = APP.read_text(encoding='utf-8')
	styles = PRODUCT_SYSTEM_STYLES.read_text(encoding='utf-8')

	assert 'evidence-status' in source
	assert 'className="dots"' not in source
	assert '.evidence-status' in styles
	assert (ROOT / 'design.md').is_file()


def test_redesign_keeps_the_existing_primary_product_actions() -> None:
	source = APP.read_text(encoding='utf-8')

	for action in ('begin', 'submitTrial', 'startRun', 'openDelivery', 'openReplay', 'askMentor'):
		assert action in source


def test_workbench_exposes_ephemeral_custom_model_preflight() -> None:
	source = APP.read_text(encoding='utf-8')

	assert 'model-connector/preflight' in source
	assert 'preflightConnector' in source
	assert 'modelConnector.api_key' in source
	assert 'localStorage' not in source


def test_home_hands_off_a_real_agent_incident_with_recorded_proof() -> None:
	source = APP.read_text(encoding='utf-8')
	styles = PRODUCT_SYSTEM_STYLES.read_text(encoding='utf-8')

	for marker in (
		'workspace-preview',
		'incident-panel',
		'Browser Agent Production Rescue',
		'Agent reported done',
		'Business state success',
		'FALSE SUCCESS',
		'recovery.py',
		'proof-comparison',
		'Baseline',
		'Fixed',
		'0/5',
		'5/5',
		'不是模拟动画',
	):
		assert marker in source

	for selector in ('.workspace-preview', '.incident-panel', '.proof-comparison', '.proof-run'):
		assert selector in styles


def test_shared_product_tokens_cover_operational_statuses() -> None:
	styles = PRODUCT_SYSTEM_STYLES.read_text(encoding='utf-8')

	for token in ('--surface-canvas', '--surface-panel', '--status-success', '--status-failure', '--status-evidence', '--radius-panel'):
		assert token in styles

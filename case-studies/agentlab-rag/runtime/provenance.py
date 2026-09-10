"""Pinned third-party runtime checks."""

from __future__ import annotations

import subprocess
from pathlib import Path

AUDITED_BROWSER_USE_COMMIT = '32601887cfbc9f4f1e3cad3e2b678e56aeaeaae4'


def assert_browser_use_commit(repo_root: Path) -> str:
	"""Return the audited Browser Use commit or fail before a pack run."""
	source_dir = repo_root / 'sources' / 'browser-use'
	try:
		result = subprocess.run(
			['git', '-C', str(source_dir), 'rev-parse', 'HEAD'],
			check=True,
			capture_output=True,
			text=True,
		)
	except subprocess.CalledProcessError as error:
		raise RuntimeError('Browser Use provenance mismatch: source checkout is unavailable') from error

	commit = result.stdout.strip()
	if commit != AUDITED_BROWSER_USE_COMMIT:
		raise RuntimeError(
			f'Browser Use provenance mismatch: expected {AUDITED_BROWSER_USE_COMMIT}, found {commit}'
		)
	return commit


if __name__ == '__main__':
	print(assert_browser_use_commit(Path(__file__).resolve().parents[1]))

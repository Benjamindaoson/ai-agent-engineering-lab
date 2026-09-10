from pathlib import Path

import pytest

from runtime.provenance import AUDITED_BROWSER_USE_COMMIT, assert_browser_use_commit


def test_audited_browser_use_commit_is_accepted() -> None:
	repo_root = Path(__file__).resolve().parents[1]
	assert assert_browser_use_commit(repo_root) == AUDITED_BROWSER_USE_COMMIT


def test_changed_browser_use_commit_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match='Browser Use provenance mismatch'):
        assert_browser_use_commit(tmp_path)

"""Facts and follow-up instruction for live recovery; it never operates the world."""

from __future__ import annotations


RECOVERY_REASON = 'sqlite_purchase_request_missing_after_page_acknowledgement'


def recovery_instruction() -> str:
	return (
		'Business-state verification found no target purchase request in SQLite. '
		'The current task remains incomplete. The existing browser session remains available. '
		'Continue handling the original task and do not report completion until it is truly complete.'
	)

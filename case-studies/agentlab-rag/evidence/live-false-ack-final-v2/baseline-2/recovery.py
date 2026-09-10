"""Facts and follow-up instruction for live recovery; it never operates the world."""

from __future__ import annotations


RECOVERY_REASON = 'sqlite_purchase_request_missing_after_page_acknowledgement'


def recovery_instruction() -> str:
	return (
		'Business-state verification found no purchase request in SQLite even though the page reported success. '
		'Inspect the current state, return to the purchase form if necessary, resubmit the original request, '
		'and do not report done until the purchase request exists.'
	)

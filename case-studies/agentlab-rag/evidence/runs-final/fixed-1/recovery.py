"""The only learner-editable repair in Proof #1."""

from __future__ import annotations


def recovery_actions(base_url: str) -> list[dict]:
	"""Continue the existing browser task by completing the pending confirmation."""
	return [
		{'navigate': {'url': f'{base_url}/purchase/confirm', 'new_tab': False}},
		{
			'evaluate': {
				'code': "(function(){const form=document.querySelector('form[action=\\\"/purchase/confirm\\\"]');if(!form)return 'confirmation missing';form.submit();return 'confirmation submitted';})()"
			}
		},
		{'done': {'text': 'Purchase confirmation completed', 'success': True}},
	]

from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest

from agentlab.model_connectors import (
	ConnectorPreflightError,
	ConnectorValidationError,
	parse_connector,
	preflight_connector,
)
from project_packs.browser_agent_rescue.workspace.live import ProviderConfig


def public_resolver(_: str) -> list[str]:
	return ['8.8.8.8']


def test_parse_connector_rejects_a_local_literal_ip_endpoint() -> None:
	with pytest.raises(ConnectorValidationError):
		parse_connector({'endpoint': 'http://127.0.0.1:8000/v1', 'model': 'demo', 'api_key': 'secret'}, resolver=public_resolver)
	with pytest.raises(ConnectorValidationError):
		parse_connector({'endpoint': 'https://10.0.0.8/v1', 'model': 'demo', 'api_key': 'secret'}, resolver=public_resolver)


def test_parse_connector_accepts_a_public_hostname_behind_a_local_proxy_mapping() -> None:
	connector = parse_connector(
		{'endpoint': 'https://api.deepseek.com', 'model': 'deepseek-v4-flash', 'api_key': 'secret'},
		resolver=lambda _: ['198.18.0.94'],
	)

	assert connector.hostname == 'api.deepseek.com'


def test_parse_connector_returns_only_non_secret_public_provenance() -> None:
	connector = parse_connector(
		{'endpoint': 'https://models.example.test/v1/', 'model': 'demo-model', 'api_key': 'secret-value'},
		resolver=public_resolver,
	)

	assert connector.endpoint == 'https://models.example.test/v1'
	assert connector.public_provenance() == {
		'classification': 'open', 'protocol': 'openai-chat-completions',
		'endpoint_hostname': 'models.example.test', 'model': 'demo-model',
		'fingerprint': connector.fingerprint,
	}
	assert 'secret-value' not in str(connector.public_provenance())


class CompatibleClient:
	def __init__(self, **_: str) -> None:
		self.models = SimpleNamespace(list=self.list_models)
		self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create_completion))

	async def list_models(self):
		return SimpleNamespace(data=[SimpleNamespace(id='demo-model')])

	async def create_completion(self, **_: object):
		return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='OK'))])

	async def close(self) -> None:
		return None


def test_preflight_verifies_model_and_chat_completion_shape() -> None:
	connector = parse_connector(
		{'endpoint': 'https://models.example.test/v1', 'model': 'demo-model', 'api_key': 'secret-value'},
		resolver=public_resolver,
	)

	result = asyncio.run(preflight_connector(connector, client_factory=CompatibleClient))

	assert result['ready'] is True
	assert result['connector']['model'] == 'demo-model'
	assert 'secret-value' not in str(result)


def test_preflight_rejects_missing_model() -> None:
	class MissingModelClient(CompatibleClient):
		async def list_models(self):
			return SimpleNamespace(data=[])

	connector = parse_connector(
		{'endpoint': 'https://models.example.test/v1', 'model': 'demo-model', 'api_key': 'secret-value'},
		resolver=public_resolver,
	)

	with pytest.raises(ConnectorPreflightError, match='cannot access configured model'):
		asyncio.run(preflight_connector(connector, client_factory=MissingModelClient))


def test_provider_configuration_repr_never_includes_an_ephemeral_key() -> None:
	provider = ProviderConfig('custom', 'CUSTOM_MODEL_API_KEY', 'https://models.example.test/v1', 'demo', 'demo', 'untrusted', 0, 0, 0, 'json_object', api_key='secret-value')

	assert 'secret-value' not in repr(provider)

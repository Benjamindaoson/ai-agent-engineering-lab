"""Safe, ephemeral configuration for user-supplied OpenAI-compatible models."""

from __future__ import annotations

import hashlib
import ipaddress
import socket
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlparse, urlunparse

from openai import AsyncOpenAI


class ConnectorValidationError(ValueError):
	"""A connector is not eligible for AgentLab's public-endpoint boundary."""


class ConnectorPreflightError(RuntimeError):
	"""A syntactically safe connector failed a bounded compatibility check."""


def _system_resolver(hostname: str) -> list[str]:
	return sorted({entry[4][0] for entry in socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)})


def _require_safe_endpoint_host(hostname: str, resolver: Callable[[str], Sequence[str]]) -> None:
	try:
		literal_ip = ipaddress.ip_address(hostname)
	except ValueError:
		literal_ip = None
	if literal_ip is not None:
		if not literal_ip.is_global:
			raise ConnectorValidationError('Endpoint must not use a private or reserved literal IP address')
		return
	try:
		addresses = resolver(hostname)
	except OSError as error:
		raise ConnectorValidationError('Endpoint hostname could not be resolved') from error
	if not addresses:
		raise ConnectorValidationError('Endpoint hostname did not resolve to an address')
	for address in addresses:
		try:
			ip = ipaddress.ip_address(address)
		except ValueError as error:
			raise ConnectorValidationError('Endpoint hostname resolved to an invalid address') from error


@dataclass(frozen=True)
class CustomModelConnector:
	endpoint: str
	model: str
	api_key: str = field(repr=False, compare=False)

	@property
	def hostname(self) -> str:
		return urlparse(self.endpoint).hostname or ''

	@property
	def fingerprint(self) -> str:
		return hashlib.sha256(f'{self.endpoint}\0{self.model}'.encode('utf-8')).hexdigest()[:16]

	def public_provenance(self) -> dict[str, str]:
		return {
			'classification': 'open', 'protocol': 'openai-chat-completions',
			'endpoint_hostname': self.hostname, 'model': self.model, 'fingerprint': self.fingerprint,
		}


def parse_connector(payload: Any, *, resolver: Callable[[str], Sequence[str]] | None = None) -> CustomModelConnector:
	"""Validate untrusted request data without ever making the key serializable."""
	if not isinstance(payload, dict):
		raise ConnectorValidationError('Connector must be an object')
	endpoint = payload.get('endpoint')
	model = payload.get('model')
	api_key = payload.get('api_key')
	if not all(isinstance(value, str) and value.strip() for value in (endpoint, model, api_key)):
		raise ConnectorValidationError('Endpoint, model, and API key are required')
	if len(endpoint) > 2_048 or len(model) > 256 or len(api_key) > 4_096:
		raise ConnectorValidationError('Connector field exceeds the permitted length')
	parsed = urlparse(endpoint.strip())
	if parsed.scheme != 'https' or not parsed.netloc:
		raise ConnectorValidationError('Endpoint must be a public HTTPS URL')
	if parsed.username or parsed.password or parsed.query or parsed.fragment:
		raise ConnectorValidationError('Endpoint must not contain credentials, query, or fragment data')
	hostname = parsed.hostname
	if not hostname or hostname.lower() == 'localhost' or hostname.lower().endswith('.localhost'):
		raise ConnectorValidationError('Endpoint must not target localhost')
	_require_safe_endpoint_host(hostname, resolver or _system_resolver)
	normalized = urlunparse(('https', parsed.netloc, parsed.path.rstrip('/'), '', '', ''))
	return CustomModelConnector(endpoint=normalized, model=model.strip(), api_key=api_key.strip())


async def preflight_connector(
	connector: CustomModelConnector,
	*,
	client_factory: Callable[..., Any] = AsyncOpenAI,
) -> dict[str, Any]:
	"""Check model availability and minimal response shape before a Browser Use run."""
	client = client_factory(api_key=connector.api_key, base_url=connector.endpoint)
	try:
		models = await client.models.list()
		if connector.model not in {item.id for item in models.data}:
			raise ConnectorPreflightError(f'Custom endpoint cannot access configured model {connector.model}')
		response = await client.chat.completions.create(
			model=connector.model,
			messages=[{'role': 'user', 'content': 'Reply with OK.'}],
			max_tokens=1,
		)
		if not getattr(response, 'choices', None) or not hasattr(response.choices[0], 'message'):
			raise ConnectorPreflightError('Custom endpoint returned an invalid Chat Completions response')
		return {'ready': True, 'connector': connector.public_provenance()}
	except ConnectorPreflightError:
		raise
	except Exception as error:
		raise ConnectorPreflightError('Custom endpoint preflight failed') from error
	finally:
		await client.close()

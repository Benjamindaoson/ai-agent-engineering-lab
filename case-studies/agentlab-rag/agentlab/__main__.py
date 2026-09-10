"""One-command local AgentLab server."""

import uvicorn


if __name__ == '__main__':
	uvicorn.run('agentlab.api:create_app', host='127.0.0.1', port=8000, factory=True)

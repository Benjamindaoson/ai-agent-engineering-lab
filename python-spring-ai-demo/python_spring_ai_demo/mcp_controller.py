class McpController:
    def __init__(self, chat_client, tool_callbacks=None, mcp_sync_clients=None):
        self.chat_client = chat_client
        self.tool_callbacks = list(tool_callbacks or [])
        self.mcp_sync_clients = list(mcp_sync_clients or [])

    def mcp(self, message: str) -> str:
        callback_results = [callback(message) for callback in self.tool_callbacks]
        return self.chat_client.complete(f"{message}\n\nMCP工具结果：{callback_results}")

    def mcp_prompt(self, question: str) -> str:
        client = self._first_client()
        return str(client.list_prompts()[0])

    def mcp_resource(self, question: str) -> str:
        client = self._first_client()
        return str(client.read_resource("config://username"))

    def _first_client(self):
        if not self.mcp_sync_clients:
            raise RuntimeError("No MCP client configured")
        return self.mcp_sync_clients[0]

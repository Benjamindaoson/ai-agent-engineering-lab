import json
from dataclasses import asdict, is_dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

from .weather_service import WeatherService


class McpServerApplication:
    def __init__(self, weather_service: WeatherService | None = None, name: str = "streamable-mcp-server-demo", version: str = "1.0.0"):
        self.weather_service = weather_service or WeatherService()
        self.name = name
        self.version = version

    def list_tools(self) -> list[dict]:
        return [{"name": "getWeather", "description": "获取指定城市的天气", "inputSchema": {"cityName": "string"}}]

    def call_tool(self, name: str, arguments: dict) -> str:
        if name != "getWeather":
            raise ValueError(f"Unknown tool: {name}")
        return self.weather_service.get_weather(arguments.get("cityName", ""))

    def list_prompts(self) -> list[dict]:
        return [{"name": "greeting", "description": "欢迎语", "arguments": [{"name": "name", "required": True}]}]

    def get_prompt(self, name: str, arguments: dict):
        if name != "greeting":
            raise ValueError(f"Unknown prompt: {name}")
        return self.weather_service.greeting(arguments.get("name", ""))

    def list_resources(self) -> list[dict]:
        return [{"uri": "config://{key}", "name": "configuration"}]

    def read_resource(self, uri: str) -> str:
        prefix = "config://"
        if not uri.startswith(prefix):
            raise ValueError(f"Unknown resource: {uri}")
        return self.weather_service.get_config(uri[len(prefix) :])

    def handle_json(self, payload: str) -> str:
        request = json.loads(payload)
        method = request.get("method")
        params = request.get("params", {})
        if method == "tools/list":
            result = self.list_tools()
        elif method == "tools/call":
            result = self.call_tool(params.get("name", ""), params.get("arguments", {}))
        elif method == "prompts/list":
            result = self.list_prompts()
        elif method == "prompts/get":
            result = self.get_prompt(params.get("name", ""), params.get("arguments", {}))
        elif method == "resources/list":
            result = self.list_resources()
        elif method == "resources/read":
            result = self.read_resource(params.get("uri", ""))
        else:
            raise ValueError(f"Unsupported MCP method: {method}")
        return json.dumps({"result": self._jsonable(result)}, ensure_ascii=False)

    def serve(self, host: str = "127.0.0.1", port: int = 8082) -> HTTPServer:
        app = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                length = int(self.headers.get("Content-Length", "0"))
                response = app.handle_json(self.rfile.read(length).decode("utf-8"))
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(response.encode("utf-8"))

            def do_GET(self):
                path = urlparse(self.path).path
                if path == "/health":
                    body = json.dumps({"name": app.name, "version": app.version}, ensure_ascii=False)
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(body.encode("utf-8"))
                    return
                self.send_response(404)
                self.end_headers()

            def log_message(self, format, *args):
                return

        return HTTPServer((host, port), Handler)

    def _jsonable(self, value):
        if is_dataclass(value):
            return asdict(value)
        if isinstance(value, list):
            return [self._jsonable(item) for item in value]
        if isinstance(value, dict):
            return {key: self._jsonable(item) for key, item in value.items()}
        return value


def main() -> None:
    server = McpServerApplication().serve()
    print("python-ai-mcp-server-demo listening on http://127.0.0.1:8082")
    server.serve_forever()


if __name__ == "__main__":
    main()

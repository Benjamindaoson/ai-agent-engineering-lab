class ZhouyuToolInterceptor:
    def get_name(self) -> str:
        return "zhouyuToolInterceptor"

    def intercept(self, tool_name: str, handler) -> str:
        try:
            return handler()
        except Exception:
            # ponytail: interceptor is the user-facing tool boundary.
            return "工具执行遇到问题，请稍后重试"

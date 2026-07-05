class ZhouyuModelInterceptor:
    def get_name(self) -> str:
        return "zhouyuModelInterceptor"

    def intercept(self, messages: list[str], handler) -> str:
        if any("死亡" in message for message in messages):
            return "输入有不适当的内容"
        response = handler()
        if "死亡" in response:
            return "输出有不适当的内容"
        return response

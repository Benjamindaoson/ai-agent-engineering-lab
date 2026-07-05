import inspect


class ToolUtil:
    @staticmethod
    def get_tool_description(clazz: type) -> str:
        formatted_tools = []
        for name, method in inspect.getmembers(clazz, predicate=inspect.isfunction):
            description = getattr(method, "_tool_description", None)
            if not description:
                continue

            params = getattr(method, "_tool_params", {})
            param_description = next(iter(params.values()), "")
            formatted_tools.append(
                f"- toolName={name}, toolDescription={description}, paramDescription={param_description}"
            )

        return "\n\n".join(formatted_tools)

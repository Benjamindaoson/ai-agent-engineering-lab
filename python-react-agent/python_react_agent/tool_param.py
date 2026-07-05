def tool_param(name: str, description: str):
    def decorate(func):
        params = getattr(func, "_tool_params", {}).copy()
        params[name] = description
        func._tool_params = params
        return func

    return decorate

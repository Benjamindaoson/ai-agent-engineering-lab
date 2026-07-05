def tool(description: str):
    def decorate(func):
        func._tool_description = description
        return func

    return decorate

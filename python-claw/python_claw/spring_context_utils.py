class SpringContextUtils:
    def __init__(self) -> None:
        self._beans: dict[type, object] = {}

    def register(self, bean: object) -> None:
        self._beans[type(bean)] = bean

    def get_bean(self, bean_type: type) -> object:
        return self._beans[bean_type]

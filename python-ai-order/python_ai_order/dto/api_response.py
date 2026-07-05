import time
from dataclasses import dataclass, field
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class ApiResponse(Generic[T]):
    code: int
    message: str
    data: T | None = None
    timestamp: int = field(default_factory=lambda: int(time.time() * 1000))

    @classmethod
    def success(cls, data=None, message: str = "操作成功") -> "ApiResponse":
        return cls(200, message, data)

    @classmethod
    def error(cls, message: str, code: int = 500) -> "ApiResponse":
        return cls(code, message)

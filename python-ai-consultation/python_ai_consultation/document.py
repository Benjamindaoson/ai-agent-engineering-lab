from dataclasses import dataclass, field


@dataclass
class Document:
    text: str
    metadata: dict = field(default_factory=dict)

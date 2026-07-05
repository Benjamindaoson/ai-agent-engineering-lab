from dataclasses import dataclass, field


@dataclass
class ProductInfo:
    name: str
    price: float
    features: list[str] = field(default_factory=list)

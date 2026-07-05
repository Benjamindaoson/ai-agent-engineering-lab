from dataclasses import dataclass

from ..entity.order import Order


@dataclass
class PaymentResponse:
    success: bool
    message: str
    order: Order | None = None

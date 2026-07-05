from dataclasses import dataclass
from decimal import Decimal


@dataclass
class OrderItem:
    item_id: int | None = None
    order_id: int | None = None
    product_id: int | None = None
    product_name: str = ""
    product_price: Decimal = Decimal("0")
    quantity: int = 0
    subtotal: Decimal = Decimal("0")
    product_image: str | None = None
    product_specs: str | None = None

    def set_quantity(self, quantity: int) -> None:
        self.quantity = quantity
        self.subtotal = self.product_price * Decimal(quantity)

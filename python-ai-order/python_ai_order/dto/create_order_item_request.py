from dataclasses import dataclass


@dataclass
class CreateOrderItemRequest:
    product_id: int
    quantity: int

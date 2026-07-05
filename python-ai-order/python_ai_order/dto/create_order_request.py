from dataclasses import dataclass, field

from .create_order_item_request import CreateOrderItemRequest


@dataclass
class CreateOrderRequest:
    user_id: str
    items: list[CreateOrderItemRequest] = field(default_factory=list)
    remark: str = ""
    delivery_address: str = ""
    receiver_name: str = ""
    receiver_phone: str = ""

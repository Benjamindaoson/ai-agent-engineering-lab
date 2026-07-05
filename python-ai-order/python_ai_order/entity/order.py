from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from ..enums.order_status import OrderStatus
from .order_item import OrderItem


@dataclass
class Order:
    order_id: int | None = None
    user_id: str = ""
    order_no: str = ""
    total_amount: Decimal = Decimal("0")
    status: OrderStatus = OrderStatus.PENDING
    remark: str = ""
    delivery_address: str = ""
    receiver_name: str = ""
    receiver_phone: str = ""
    create_time: datetime = field(default_factory=datetime.now)
    update_time: datetime = field(default_factory=datetime.now)
    pay_time: datetime | None = None
    ship_time: datetime | None = None
    deliver_time: datetime | None = None
    order_items: list[OrderItem] = field(default_factory=list)

    def set_status(self, status: OrderStatus) -> None:
        self.status = status
        self.update_time = datetime.now()

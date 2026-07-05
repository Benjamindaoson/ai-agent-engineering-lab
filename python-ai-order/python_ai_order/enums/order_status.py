from enum import Enum


class OrderStatus(Enum):
    PENDING = "待付款"
    PAID = "已付款"
    SHIPPED = "已发货"
    DELIVERED = "已送达"
    COMPLETED = "已完成"
    CANCELLED = "已取消"
    REFUNDED = "已退款"

    @property
    def description(self) -> str:
        return self.value

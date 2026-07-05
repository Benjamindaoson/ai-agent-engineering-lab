from enum import Enum


class SessionStatus(Enum):
    CONFIRMING_ORDER = "确认订单信息"
    ORDER_CREATED = "订单已创建"
    CONFIRMING_PAYMENT = "确认支付信息"
    PAYMENT_COMPLETED = "支付已完成"
    ORDER_REFUND = "订单已退款"
    CONVERSATION_ENDED = "对话结束"

    @property
    def description(self) -> str:
        return self.value

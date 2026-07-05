from ..dto.create_order_request import CreateOrderRequest
from ..dto.payment_response import PaymentResponse
from ..entity.order import Order
from ..entity.product import Product
from ..enums.session_status import SessionStatus
from ..parser.order_document_parser import Document
from ..service.order_service import OrderService, OrderServiceError


class OrderTool:
    def __init__(self, order_service: OrderService):
        self.order_service = order_service
        self.session_context: dict[str, SessionStatus] = {}

    def search_products(self, question: str, keyword: str) -> list[Product]:
        return self.order_service.search_products(question, keyword)

    def create_order(self, create_order_request: CreateOrderRequest) -> Order:
        return self.order_service.create_order(create_order_request)

    def pay_order(self, order_no: str, tool_context: dict | None = None) -> PaymentResponse:
        try:
            chat_id = (tool_context or {}).get("chatId")
            if self.session_context.get(chat_id) != SessionStatus.CONFIRMING_PAYMENT:
                return PaymentResponse(False, "请先确认是否支付")
            order = self.order_service.pay_order(order_no)
            self.session_context[chat_id] = SessionStatus.PAYMENT_COMPLETED
            return PaymentResponse(True, "支付成功", order)
        except OrderServiceError as exc:
            return PaymentResponse(False, f"支付失败: {exc}")

    def refund_order(self, order_no: str, reason: str) -> PaymentResponse:
        try:
            order = self.order_service.refund_order(order_no, reason)
            return PaymentResponse(True, "订单退款成功", order)
        except OrderServiceError as exc:
            return PaymentResponse(False, f"订单退款失败: {exc}")

    def customer_info_search(self, question: str) -> list[Document]:
        return self.order_service.search_customer_vector(question)

    def get_session_context(self) -> dict[str, SessionStatus]:
        return self.session_context

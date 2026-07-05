from ..dto.api_response import ApiResponse
from ..dto.create_order_request import CreateOrderRequest
from ..service.order_service import OrderService, OrderServiceError


class OrderController:
    def __init__(self, order_service: OrderService):
        self.order_service = order_service

    def create_order(self, request: CreateOrderRequest) -> ApiResponse:
        try:
            return ApiResponse.success(self.order_service.create_order(request), "订单创建成功")
        except OrderServiceError as exc:
            return ApiResponse.error(f"订单创建失败: {exc}")

    def get_order_by_order_no(self, order_no: str) -> ApiResponse:
        try:
            return ApiResponse.success(self.order_service.get_order_by_order_no(order_no))
        except OrderServiceError as exc:
            return ApiResponse.error(f"订单查询失败: {exc}")

    def get_user_orders(self, user_id: str) -> ApiResponse:
        try:
            return ApiResponse.success(self.order_service.get_user_orders(user_id))
        except OrderServiceError as exc:
            return ApiResponse.error(f"用户订单查询失败: {exc}")

    def pay_order(self, order_no: str) -> ApiResponse:
        try:
            return ApiResponse.success(self.order_service.pay_order(order_no), "订单支付成功")
        except OrderServiceError as exc:
            return ApiResponse.error(f"订单支付失败: {exc}")

    def refund_order(self, order_no: str, reason: str | None = None) -> ApiResponse:
        try:
            return ApiResponse.success(self.order_service.refund_order(order_no, reason or "用户申请退款"), "订单退款成功")
        except OrderServiceError as exc:
            return ApiResponse.error(f"订单退款失败: {exc}")

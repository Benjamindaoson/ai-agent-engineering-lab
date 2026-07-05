from .dto.create_order_item_request import CreateOrderItemRequest
from .dto.create_order_request import CreateOrderRequest
from .enums.session_status import SessionStatus
from .service.order_service import OrderService
from .tool.order_tool import OrderTool


def main() -> None:
    service = OrderService()
    tool = OrderTool(service)
    products = tool.search_products("想买降噪耳机", "耳机")
    assert products[0].name == "AirPods Pro"
    order = tool.create_order(
        CreateOrderRequest(
            user_id="1010",
            items=[CreateOrderItemRequest(6, 1)],
            remark="self check",
            delivery_address="长沙市",
            receiver_name="周瑜",
            receiver_phone="13800000000",
        )
    )
    assert not tool.pay_order(order.order_no, {"chatId": "check"}).success
    tool.session_context["check"] = SessionStatus.CONFIRMING_PAYMENT
    assert tool.pay_order(order.order_no, {"chatId": "check"}).success
    assert tool.refund_order(order.order_no, "课堂自检").success
    assert tool.customer_info_search("退款到账时间")
    print("python-ai-order self check passed")


if __name__ == "__main__":
    main()

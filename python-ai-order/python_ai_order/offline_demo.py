from .dto.create_order_item_request import CreateOrderItemRequest
from .dto.create_order_request import CreateOrderRequest
from .enums.session_status import SessionStatus
from .service.order_service import OrderService
from .tool.order_tool import OrderTool


def main() -> None:
    service = OrderService()
    tool = OrderTool(service)
    chat_id = "demo"

    print("1. 推荐商品")
    for product in tool.search_products("我想买一台 iPhone", "iPhone")[:3]:
        print(f"- {product.id}: {product.name} {product.price} - {product.description}")

    print("\n2. 创建订单")
    order = tool.create_order(
        CreateOrderRequest(
            user_id="1010",
            items=[CreateOrderItemRequest(product_id=6, quantity=1)],
            remark="离线演示订单",
            delivery_address="长沙市岳麓区",
            receiver_name="周瑜",
            receiver_phone="13800000000",
        )
    )
    print(f"订单号: {order.order_no}, 金额: {order.total_amount}, 状态: {order.status.description}")

    print("\n3. 未确认直接支付")
    print(tool.pay_order(order.order_no, {"chatId": chat_id}).message)

    print("\n4. 确认后支付")
    tool.session_context[chat_id] = SessionStatus.CONFIRMING_PAYMENT
    paid = tool.pay_order(order.order_no, {"chatId": chat_id})
    print(f"{paid.message}: {paid.order.status.description}")

    print("\n5. 退款并查询售后知识")
    refunded = tool.refund_order(order.order_no, "课堂演示退款")
    print(f"{refunded.message}: {refunded.order.status.description}")
    for doc in tool.customer_info_search("退款到账时间")[:1]:
        print(doc.text)


if __name__ == "__main__":
    main()

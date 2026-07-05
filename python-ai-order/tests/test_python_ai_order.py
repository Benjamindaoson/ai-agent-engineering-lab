import pathlib
import sys
import unittest
from decimal import Decimal

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from python_ai_order.controller.ai_order_controller import AIOrderController
from python_ai_order.controller.order_controller import OrderController
from python_ai_order.dto.create_order_item_request import CreateOrderItemRequest
from python_ai_order.dto.create_order_request import CreateOrderRequest
from python_ai_order.enums.order_status import OrderStatus
from python_ai_order.enums.session_status import SessionStatus
from python_ai_order.parser.order_document_parser import OrderDocumentParser
from python_ai_order.service.order_service import OrderService, OrderServiceError
from python_ai_order.tool.order_tool import OrderTool


class FakeChatClient:
    def __init__(self, text="好的，已为你处理。"):
        self.text = text
        self.calls = []

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        self.calls.append((system_prompt, user_prompt))
        return self.text


class PythonAiOrderTests(unittest.TestCase):
    def make_order_request(self):
        return CreateOrderRequest(
            user_id="1010",
            items=[CreateOrderItemRequest(product_id=1, quantity=2)],
            remark="课堂演示",
            delivery_address="长沙市",
            receiver_name="周瑜",
            receiver_phone="13800000000",
        )

    def test_search_products_matches_keyword_without_elasticsearch(self):
        service = OrderService()

        products = service.search_products("想买降噪耳机", "耳机")

        self.assertEqual("AirPods Pro", products[0].name)
        self.assertGreaterEqual(len(products), 3)

    def test_create_order_calculates_items_and_total_amount(self):
        service = OrderService()

        order = service.create_order(self.make_order_request())

        self.assertEqual(OrderStatus.PENDING, order.status)
        self.assertEqual(Decimal("15998.00"), order.total_amount)
        self.assertEqual("iPhone 15 Pro", order.order_items[0].product_name)

    def test_order_tool_requires_confirm_pay_before_payment(self):
        service = OrderService()
        order = service.create_order(self.make_order_request())
        tool = OrderTool(service)

        blocked = tool.pay_order(order.order_no, {"chatId": "c1"})
        tool.session_context["c1"] = SessionStatus.CONFIRMING_PAYMENT
        paid = tool.pay_order(order.order_no, {"chatId": "c1"})

        self.assertFalse(blocked.success)
        self.assertIn("请先确认", blocked.message)
        self.assertTrue(paid.success)
        self.assertEqual(OrderStatus.PAID, paid.order.status)

    def test_refund_only_allows_paid_or_later_orders(self):
        service = OrderService()
        order = service.create_order(self.make_order_request())

        with self.assertRaises(OrderServiceError):
            service.refund_order(order.order_no, "不想买了")

        service.pay_order(order.order_no)
        refunded = service.refund_order(order.order_no, "不想买了")

        self.assertEqual(OrderStatus.REFUNDED, refunded.status)
        self.assertIn("退款原因", refunded.remark)

    def test_parser_splits_customer_markdown_by_third_level_headings(self):
        parser = OrderDocumentParser("### 退款到账时间\n3-5个工作日\n\n### 配送费用\n满299免运费")

        documents = parser.parse()

        self.assertEqual(["退款到账时间", "配送费用"], [doc.metadata["title"] for doc in documents])
        self.assertIn("3-5个工作日", documents[0].text)

    def test_controllers_wrap_service_and_stream_agent_response(self):
        service = OrderService()
        order_controller = OrderController(service)
        ai_controller = AIOrderController(FakeChatClient("推荐 iPhone 15 Pro"), OrderTool(service), service)

        response = order_controller.create_order(self.make_order_request())
        stream_text = "".join(chunk["content"] for chunk in ai_controller.sse("chat-1", "推荐手机"))

        self.assertEqual(200, response.code)
        self.assertIn("推荐 iPhone 15 Pro", stream_text)


if __name__ == "__main__":
    unittest.main()

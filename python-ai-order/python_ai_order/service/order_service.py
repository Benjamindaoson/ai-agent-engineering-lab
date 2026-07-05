from datetime import datetime
from decimal import Decimal

from ..dto.create_order_request import CreateOrderRequest
from ..entity.order import Order
from ..entity.order_item import OrderItem
from ..entity.product import Product
from ..enums.order_status import OrderStatus
from ..parser.order_document_parser import Document, OrderDocumentParser


class OrderServiceError(RuntimeError):
    pass


class OrderService:
    def __init__(self, order_document_parser: OrderDocumentParser | None = None):
        self.order_storage: dict[int, Order] = {}
        self.order_id_generator = 1
        self.item_id_generator = 1
        self.product_storage = self._init_mock_products()
        self.customer_documents = (order_document_parser or OrderDocumentParser()).parse()

    def create_order(self, request: CreateOrderRequest) -> Order:
        order = Order(
            order_id=self.order_id_generator,
            order_no=self.generate_order_no(),
            user_id=request.user_id,
            remark=request.remark,
            delivery_address=request.delivery_address,
            receiver_name=request.receiver_name,
            receiver_phone=request.receiver_phone,
        )
        self.order_id_generator += 1
        total_amount = Decimal("0")
        for item_request in request.items:
            product = self.product_storage.get(item_request.product_id)
            if product is None:
                raise OrderServiceError(f"商品不存在: {item_request.product_id}")
            item = OrderItem(
                item_id=self.item_id_generator,
                order_id=order.order_id,
                product_id=product.id,
                product_name=product.name,
                product_price=product.price,
                quantity=item_request.quantity,
                subtotal=product.price * Decimal(item_request.quantity),
            )
            self.item_id_generator += 1
            order.order_items.append(item)
            total_amount += item.subtotal
        order.total_amount = total_amount
        self.order_storage[order.order_id] = order
        return order

    def get_order_by_order_no(self, order_no: str) -> Order:
        for order in self.order_storage.values():
            if order.order_no == order_no:
                return order
        raise OrderServiceError(f"订单不存在: {order_no}")

    def pay_order(self, order_no: str) -> Order:
        order = self.get_order_by_order_no(order_no)
        if order.status != OrderStatus.PENDING:
            raise OrderServiceError(f"订单状态不允许支付: {order.status.description}")
        order.set_status(OrderStatus.PAID)
        order.pay_time = datetime.now()
        return order

    def refund_order(self, order_no: str, reason: str) -> Order:
        order = self.get_order_by_order_no(order_no)
        if order.status in (OrderStatus.PENDING, OrderStatus.CANCELLED):
            raise OrderServiceError(f"订单状态不允许退款: {order.status.description}")
        order.set_status(OrderStatus.REFUNDED)
        order.remark = f"{order.remark} [退款原因: {reason}]"
        return order

    def get_user_orders(self, user_id: str) -> list[Order]:
        return sorted(
            [order for order in self.order_storage.values() if order.user_id == user_id],
            key=lambda order: order.create_time,
            reverse=True,
        )

    def init_product_vector(self) -> str:
        return "success"

    def init_customer_vector(self) -> str:
        return "success"

    def search_products(self, question: str, keyword: str) -> list[Product]:
        terms = [term.lower() for term in (question + " " + keyword).split() if term.strip()]
        if keyword:
            terms.append(keyword.lower())
        scored: list[tuple[int, Product]] = []
        for product in self.product_storage.values():
            haystack = f"{product.name} {product.description}".lower()
            score = sum(1 for term in terms if term and term in haystack)
            if score:
                scored.append((score, product))
        scored.sort(key=lambda pair: (-pair[0], pair[1].id))
        result = [product for _, product in scored]
        for product in self.product_storage.values():
            if len(result) >= 3:
                break
            if product not in result:
                result.append(product)
        return result or list(self.product_storage.values())[:5]

    def search_customer_vector(self, question: str) -> list[Document]:
        lower_question = question.lower()
        matched = [doc for doc in self.customer_documents if any(token and token in doc.text.lower() for token in lower_question.split())]
        if matched:
            return matched[:5]
        return self.customer_documents[:5]

    def generate_order_no(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"ORD{timestamp}{self.order_id_generator % 1000:03d}"

    def _init_mock_products(self) -> dict[int, Product]:
        return {
            1: Product(1, "iPhone 15 Pro", Decimal("7999.00"), "最新款iPhone，支持5G，A17 Pro芯片"),
            2: Product(2, "iPhone 14", Decimal("4999.00"), "iPhone 14，A15仿生芯片"),
            3: Product(3, "iPhone 15", Decimal("5999.00"), "iPhone 15标准版，A16仿生芯片"),
            4: Product(4, "MacBook Pro 14", Decimal("15999.00"), "专业笔记本电脑，M3 Pro芯片"),
            5: Product(5, "MacBook Air", Decimal("8999.00"), "轻薄笔记本电脑，M2芯片"),
            6: Product(6, "AirPods Pro", Decimal("1999.00"), "无线蓝牙耳机，主动降噪"),
            7: Product(7, "iPad Air", Decimal("4599.00"), "轻薄平板电脑，M1芯片"),
            8: Product(8, "iPad Pro", Decimal("6799.00"), "专业平板电脑，M2芯片"),
            9: Product(9, "Apple Watch Series 9", Decimal("2999.00"), "最新款智能手表"),
            10: Product(10, "Apple Watch SE", Decimal("1999.00"), "性价比智能手表"),
        }

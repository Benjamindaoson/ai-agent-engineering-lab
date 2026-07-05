from ..enums.session_status import SessionStatus
from ..service.order_service import OrderService
from ..tool.order_tool import OrderTool


SYSTEM_PROMPT = """
你是一个专业的智能订单助手，帮助客户自动创建订单、支付订单、退款等操作。

# 职责
- 先理解客户需求
- 根据客户需求从商品库中查找并推荐合适商品
- 客户确定了购买的商品后帮助客户创建订单
- 订单创建好了之后就进行订单支付

# 支付订单注意事项
- 支付订单前一定要让客户先确认是否自动扣款

# 其他注意事项
- 不要编造其他商品，只能基于商品库中的商品信息回答问题或创建订单
- 用户ID: 1010
- 用户名: 周瑜
"""


class AIOrderController:
    def __init__(self, chat_client, order_tool: OrderTool, order_service: OrderService):
        self.chat_client = chat_client
        self.order_tool = order_tool
        self.order_service = order_service
        self.memory: dict[str, list[str]] = {}

    def sse(self, chat_id: str, question: str):
        self.memory.setdefault(chat_id, []).append(question)
        answer = self.chat_client.complete(SYSTEM_PROMPT, question)
        self.memory[chat_id].append(answer)
        yield from self._stream(answer)

    def init_product(self) -> str:
        return self.order_service.init_product_vector()

    def init_customer(self) -> str:
        return self.order_service.init_customer_vector()

    def confirm_pay(self, chat_id: str) -> str:
        self.order_tool.session_context[chat_id] = SessionStatus.CONFIRMING_PAYMENT
        return "success"

    def _stream(self, text: str, chunk_size: int = 24):
        for index in range(0, len(text), chunk_size):
            yield {"content": text[index : index + chunk_size]}

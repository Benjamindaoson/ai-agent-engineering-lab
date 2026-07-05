from .chat_client import ChatClient
from .controller.ai_order_controller import AIOrderController
from .controller.order_controller import OrderController
from .model_config import ModelConfig
from .service.order_service import OrderService
from .tool.order_tool import OrderTool


def create_app():
    service = OrderService()
    tool = OrderTool(service)
    ai_controller = AIOrderController(ChatClient(ModelConfig.from_env()), tool, service)
    order_controller = OrderController(service)
    return ai_controller, order_controller


def main() -> None:
    ai_controller, _ = create_app()
    chat_id = "cli"
    question = input("请输入订单问题: ").strip()
    for chunk in ai_controller.sse(chat_id, question):
        print(chunk["content"], end="", flush=True)
    print()


if __name__ == "__main__":
    main()

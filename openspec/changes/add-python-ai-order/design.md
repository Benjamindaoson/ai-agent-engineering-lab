## Design

`python-ai-order` mirrors the Java module:

- `dto/`: `ApiResponse`, `CreateOrderItemRequest`, `CreateOrderRequest`, `PaymentResponse`
- `entity/`: `Product`, `OrderItem`, `Order`
- `enums/`: `OrderStatus`, `SessionStatus`
- `parser/order_document_parser.py`: splits customer-service Markdown by `###` headings.
- `service/order_service.py`: in-memory products and orders, order creation, payment, refund, product/customer search.
- `tool/order_tool.py`: tool-facing wrapper and per-chat payment confirmation state.
- `controller/`: API-style order controller and SSE-style AI order controller.

The Python port keeps the core Java behavior but avoids Elasticsearch by using simple keyword scoring over products and parsed customer documents.

## Verification

Tests cover product search, order total calculation, payment confirmation gating, refund state rules, customer document parsing, and controller wrapping/streaming.

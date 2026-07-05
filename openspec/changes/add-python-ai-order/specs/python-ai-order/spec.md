## ADDED Requirements

### Requirement: Python module mirrors Java ai-order structure
The system SHALL add `python-ai-order/` with Python counterparts for Java DTOs, entities, enums, parser, service, tool, controllers, and application wiring.

#### Scenario: Source files are comparable
- **WHEN** a learner opens `python-ai-order/python_ai_order/`
- **THEN** they can find Python files corresponding to the Java source groups in `ai-order/src/main/java/com/zhouyu/`.

### Requirement: Order business flow preserves Java behavior
The workflow SHALL support product search, order creation, order lookup, user order listing, payment, refund, and customer-service knowledge search.

#### Scenario: Order is created
- **WHEN** a create-order request contains valid product ids and quantities
- **THEN** the service creates an order with pending status, order items, and total amount.

#### Scenario: Payment requires confirmation through the tool
- **WHEN** the payment tool is called before the chat session confirms payment
- **THEN** payment is rejected with a clear confirmation message.

#### Scenario: Refund follows status rules
- **WHEN** a pending or cancelled order is refunded
- **THEN** the service rejects the refund.

### Requirement: Offline verification works without Elasticsearch or model credentials
The module SHALL include tests, a self-check, and an offline demo that run with stdlib data structures.

#### Scenario: Offline demo runs
- **WHEN** the user runs `python -m python_ai_order.offline_demo`
- **THEN** product recommendation, order creation, confirmation-gated payment, and refund are demonstrated.

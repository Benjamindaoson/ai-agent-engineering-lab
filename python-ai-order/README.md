# python-ai-order

Python counterpart of the Java `ai-order` module.

## Run order for class

```powershell
cd python-ai-order
python -m unittest discover -s tests -v
python -m python_ai_order.self_check
python -m python_ai_order.offline_demo
python -m python_ai_order
```

The first three commands are offline. Product/customer vector search is represented by in-memory keyword search so the demo does not require Elasticsearch.

## Provider config

```powershell
$env:PROVIDER="deepseek"
$env:DEEPSEEK_API_KEY="your-key"
$env:LLM_NAME="deepseek-chat"
```

## Class storyline

1. Recommend products from the product store.
2. Create an order with real item totals.
3. Block payment until the chat session confirms payment.
4. Pay the order after confirmation.
5. Refund paid orders and search customer-service knowledge.

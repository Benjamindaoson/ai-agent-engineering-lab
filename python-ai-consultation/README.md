# python-ai-consultation

Python counterpart of the Java `ai-consultation` module.

## Run order for class

```powershell
cd python-ai-consultation
python -m unittest discover -s tests -v
python -m python_ai_consultation.self_check
python -m python_ai_consultation.offline_demo
python -m python_ai_consultation
```

The first three commands are offline. Department retrieval uses an in-memory keyword store instead of Elasticsearch. Chat memory uses an in-process dictionary instead of JDBC/MySQL.

## Provider config

```powershell
$env:PROVIDER="deepseek"
$env:DEEPSEEK_API_KEY="your-key"
$env:LLM_NAME="deepseek-chat"
```

## Class storyline

1. Load department summary documents.
2. Expand retrieval queries from previous user messages.
3. Retrieve top department context.
4. Ask the assistant to route departments without diagnosis or treatment advice.
5. Register only after user confirmation.

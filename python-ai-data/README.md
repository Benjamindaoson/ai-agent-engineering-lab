# python-ai-data

A Python teaching project for data analysis agents: Text-to-SQL, SQLite querying, plan execution, and result explanation.

## Run order for class

```powershell
cd python-ai-data
python -m unittest discover -s tests -v
python -m python_ai_data.self_check
python -m python_ai_data.offline_demo
python -m python_ai_data
```

The first three commands are offline and use SQLite. The last command calls the configured model.

## Provider config

```powershell
$env:PROVIDER="deepseek"
$env:DEEPSEEK_API_KEY="your-key"
$env:LLM_NAME="deepseek-chat"
```

# python-ai-engineer

Python counterpart of the Java `ai-engineer` module.

## Run order for class

```powershell
cd python-ai-engineer
python -m unittest discover -s tests -v
python -m python_ai_engineer.self_check
python -m python_ai_engineer.offline_demo
python -m python_ai_engineer
```

The first three commands are offline. The last command calls the configured model.

## Provider config

```powershell
$env:PROVIDER="deepseek"
$env:DEEPSEEK_API_KEY="your-key"
$env:LLM_NAME="deepseek-chat"
```

or:

```powershell
$env:PROVIDER="dashscope"
$env:DASHSCOPE_API_KEY="your-key"
$env:LLM_NAME="qwen-plus"
```

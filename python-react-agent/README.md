# Python ReAct Agent

Python counterpart of `java-react-agent`. The Java module is unchanged.

## Setup

```powershell
cd python-react-agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Provider Config

DashScope:

```powershell
$env:PROVIDER = "dashscope"
$env:DASHSCOPE_API_KEY = "your-key"
$env:LLM_NAME = "qwen3-max"
```

DeepSeek:

```powershell
$env:PROVIDER = "deepseek"
$env:DEEPSEEK_API_KEY = "your-key"
$env:LLM_NAME = "deepseek-v4-flash"
```

`LLM_NAME` is optional.

## Run

This calls the configured real provider:

```powershell
python -m python_react_agent
```

## Offline Full Demo

This runs the full ReAct flow with fake model responses, so it does not need an API key:

```powershell
python -m python_react_agent.offline_demo
```

Use this only to explain the loop. It is not a real DeepSeek call.

## Offline Check

```powershell
python -m unittest discover -s tests -v
python -m python_react_agent.self_check
```

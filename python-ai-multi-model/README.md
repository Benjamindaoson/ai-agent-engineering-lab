# python-ai-multi-model

Python counterpart of the Java `ai-multi-model` module.

## Run order for class

```powershell
cd python-ai-multi-model
python -m unittest discover -s tests -v
python -m python_ai_multi_model.self_check
python -m python_ai_multi_model.offline_demo
python -m python_ai_multi_model
```

The first three commands are offline. DashScope SDK, Spring Boot, ffmpeg, and the large video asset are not required.

## Provider config

```powershell
$env:PROVIDER="deepseek"
$env:DEEPSEEK_API_KEY="your-key"
$env:LLM_NAME="deepseek-chat"
```

For DashScope-compatible config:

```powershell
$env:PROVIDER="dashscope"
$env:DASHSCOPE_API_KEY="your-key"
$env:LLM_NAME="qwen3-max"
```

## Java to Python map

- `MultiModelApplication.java` -> `multi_model_application.py`
- `MultiModelController.java` -> `multi_model_controller.py`
- `DashscopeService.java` -> `dashscope_service.py`

## Class storyline

1. Image generation payload.
2. Image chat with local PNG converted to base64.
3. Video chat as stream chunks.
4. Audio transcription text rendered into a summary prompt.

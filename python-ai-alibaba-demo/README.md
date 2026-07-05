# python-ai-alibaba-demo

Python counterpart of the Java `spring-ai-alibaba-demo` module.

## Run order for class

```powershell
cd python-ai-alibaba-demo
python -m unittest discover -s tests -v
python -m python_ai_alibaba_demo.self_check
python -m python_ai_alibaba_demo.offline_demo
python -m python_ai_alibaba_demo
```

The first three commands are offline. DashScope, Baidu, Elasticsearch, Spring AI advisors, and PDFBox are represented by fake clients, request builders, and in-memory retrieval so the classroom flow is stable.

## Provider config

```powershell
$env:PROVIDER="deepseek"
$env:DEEPSEEK_API_KEY="your-key"
$env:LLM_NAME="deepseek-chat"
```

For DashScope-compatible runs:

```powershell
$env:PROVIDER="dashscope"
$env:DASHSCOPE_API_KEY="your-key"
$env:LLM_NAME="qwen-long"
```

## Java to Python map

- `AlibabaApplication.java` -> `python_ai_alibaba_demo/alibaba_application.py`
- `ChatController.java` -> `python_ai_alibaba_demo/chat_controller.py`
- `BaiduTest.java` -> `python_ai_alibaba_demo/baidu_test.py`
- `MarkdownTest.java` -> `python_ai_alibaba_demo/markdown_test.py`
- `PdfTest.java` -> `python_ai_alibaba_demo/pdf_test.py`

## Class storyline

1. Alibaba/DashScope provider configuration.
2. Local tool calling with city-time style tool names.
3. Baidu search tool request shape.
4. Markdown and PDF document parser demos.
5. Vector retrieval, reranking, memory RAG, and file question answering.

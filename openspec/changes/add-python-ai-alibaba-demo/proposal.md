## Why

`spring-ai-alibaba-demo` is the course step where the Java project moves from generic Spring AI into Spring AI Alibaba integrations: DashScope chat, Baidu search tool calling, document parsing, file question answering, and RAG with reranking.

## What Changes

- Add `python-ai-alibaba-demo/` without modifying `spring-ai-alibaba-demo/`.
- Mirror the Java entry points: `AlibabaApplication`, `ChatController`, `BaiduTest`, `MarkdownTest`, and `PdfTest`.
- Keep live model configuration OpenAI-compatible with `PROVIDER=dashscope|deepseek`, while making tests and classroom demos run offline.
- Replace Elasticsearch, Spring AI advisors, DashScope document analysis, and PDFBox with stdlib/in-memory equivalents that preserve the teaching shape.

## Impact

- New Python module under `python-ai-alibaba-demo/`.
- New OpenSpec change under `openspec/changes/add-python-ai-alibaba-demo/`.

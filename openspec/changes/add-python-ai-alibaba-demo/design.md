## Design

`python-ai-alibaba-demo` mirrors the Java module with Python-native files:

- `alibaba_application.py`: application wiring and in-memory chat memory.
- `chat_controller.py`: Python methods corresponding to `/chat`, `/baidu`, `/rankChat`, `/ragAdvisor2`, and `/fileChat`.
- `baidu_test.py`: Baidu search request helper matching the Java tool-call shape.
- `markdown_test.py`: stdlib Markdown parser configured like the Java `MarkdownDocumentParserConfig`.
- `pdf_test.py`: stdlib PDF placeholder parser with clear metadata, because real PDF text extraction would require an extra dependency.
- `simple_ai.py`: document, vector store, retrieval, rerank, and chat memory primitives.
- `chat_client.py` and `model_config.py`: fake offline client plus OpenAI-compatible live-provider config.

External integrations are injectable. Offline tests and demos use fake chat clients and in-memory retrieval.

## Verification

Tests cover provider config, Markdown parsing, PDF fallback parsing, Baidu request construction, and the controller methods that correspond to Java endpoints.

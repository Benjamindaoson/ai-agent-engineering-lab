## Design

`python-ai-consultation` mirrors the Java module:

- `consultation_controller.py`: SSE-style generator with system prompt, chat memory, query expansion, retrieval context, and tool wiring.
- `consultation_tools.py`: `register(department_name)` tool.
- `consultation_query_expander.py`: expands retrieval queries from user messages in chat history.
- `department_summary_vector_store_job.py`: loads department summary files into document objects with `departmentName` metadata.
- `department_summary_job.py`: summarizes raw department files into summary files using a chat client.
- `department_scraper.py`: stdlib scraper shell for fetching department pages when HTML is available.
- `vector_store.py`: small in-memory keyword retriever replacing Elasticsearch for offline use.

The Python port keeps the Java safety prompt: no diagnosis, no treatment advice, ask only for department routing, and register only after user confirmation.

## Verification

Tests cover document loading, query expansion, retrieval ranking, controller RAG context streaming, registration tool state, and summary generation.

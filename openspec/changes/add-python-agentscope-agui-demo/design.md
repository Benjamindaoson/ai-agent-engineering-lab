## Design

Use the standard library instead of a web framework:

- `agui_protocol.py` serializes and parses AG-UI server-sent events.
- `agui_application.py` contains the application behavior, memory map, static file serving, and `http.server` handler.
- Static files mirror the Java demo entrypoints: `/` and `/js/agui-client.js`.

The offline response is deterministic. Live model configuration is present in `model_config.py`, but tests and demos do not require credentials.

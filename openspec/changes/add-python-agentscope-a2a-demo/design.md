## Design

Keep the A2A teaching surface small:

- `nacos_registry.py` is the offline replacement for Nacos agent-card discovery.
- `a2a_server_spring_boot_application.py` builds and registers `my-assistant`.
- `a2a_client_application.py` resolves an agent card and streams task/message events.
- `weather_service.py` mirrors the Java tool methods.

No A2A SDK or web framework is required for the classroom path.

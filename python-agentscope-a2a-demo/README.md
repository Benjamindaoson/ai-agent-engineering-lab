# python-agentscope-a2a-demo

Python counterpart of the Java `agentscope-a2a-demo` module.

## Run order for class

```powershell
cd python-agentscope-a2a-demo
python -m unittest discover -s tests -v
python -m python_agentscope_a2a_demo.self_check
python -m python_agentscope_a2a_demo.offline_demo
python -m python_agentscope_a2a_demo
```

All commands are offline. Nacos, AgentScope A2A starter, Spring Boot, and DashScope are represented by a stdlib in-memory registry and deterministic stream events.

## Java to Python map

- `A2AServerSpringBootApplication.java` -> `a2a_server_spring_boot_application.py`
- `A2AClientApplication.java` -> `a2a_client_application.py`
- `WeatherService.java` -> `weather_service.py`
- `application.yml` -> agent-card skills in `create_server_application()`

## Class storyline

1. Server creates `my-assistant`.
2. Server publishes an agent card with `getWeather` and `generate`.
3. Client resolves the card through a Nacos-like registry.
4. Client streams task events from the remote agent.

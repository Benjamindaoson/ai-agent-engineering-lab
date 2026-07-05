## Design

`python-ai-multi-model` mirrors the Java module:

- `multi_model_application.py`: application wiring.
- `multi_model_controller.py`: methods corresponding to `/imageGeneration`, `/imageChat`, `/videoChat`, and `/audioChat`.
- `dashscope_service.py`: payload builders for image generation, image chat, video chat streaming, audio chat, image base64 encoding, and audio-summary prompt rendering.
- `model_config.py`: `PROVIDER=dashscope|deepseek` config.

The Python port does not copy the large video asset. Offline video/audio methods accept placeholder paths and return deterministic outputs. Live multimedia transport can be added later behind the same service methods.

## Verification

Unit tests cover provider config, multimodal payload shapes, image base64 encoding, video stream shape, audio summary prompt, and controller endpoint equivalents.

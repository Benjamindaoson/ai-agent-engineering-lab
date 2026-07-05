## Why

`ai-multi-model` demonstrates DashScope multimodal calls: image generation, image understanding, video understanding stream, and audio transcription followed by summary.

## What Changes

- Add `python-ai-multi-model/` without modifying `ai-multi-model/`.
- Mirror Java `MultiModelApplication`, `MultiModelController`, and `DashscopeService`.
- Keep offline tests and demos deterministic with stdlib payload builders.
- Keep OpenAI-compatible provider configuration for DashScope and DeepSeek.

## Impact

- New Python module under `python-ai-multi-model/`.
- New OpenSpec change under `openspec/changes/add-python-ai-multi-model/`.

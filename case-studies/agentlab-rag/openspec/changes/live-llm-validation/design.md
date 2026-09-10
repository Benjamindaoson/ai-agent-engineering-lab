## Context

`proof-1-passed` is immutable deterministic evidence. This change runs the same DOM-V2 procurement world with a real provider-selected model, so the model chooses browser actions while the scorer still uses database state. The default and actual experiment provider is DeepSeek; OpenAI remains selectable for compatibility.

## Goals / Non-Goals

**Goals:**

- Use a centrally declared OpenAI-compatible provider configuration; run this validation with DeepSeek `deepseek-v4-flash` using `DEEPSEEK_API_KEY` and `https://api.deepseek.com`.
- Run five fresh baseline worlds and five fresh fixed worlds.
- Record raw API usage, calculated cost, latency, action trace, recovery behavior, and business-state result.
- Enforce an explicit step and completion-token ceiling per run.

**Non-Goals:**

- Change the frozen deterministic Proof #1, `PROC-001`, DOM-V2 page, purchase scorer, or recovery implementation.
- Claim deterministic or causal LLM improvement from ten stochastic samples.
- Store an API key, send data beyond the local synthetic procurement world, or add a UI.

## Decisions

### Use a provider configuration and OpenAI-compatible transport

The live runner selects either `deepseek` or `openai` from one configuration mapping. The provider name, base URL, requested model, key environment variable, structured-output mode, and frozen price card live together. DeepSeek uses its documented JSON-object mode; OpenAI preserves JSON-schema structured output.

### Keep baseline and fixed as separate live Agent phases

Both execute the same initial task. The fixed condition checks database state after the first Agent says done; only if no request exists does it start a second live Browser Use session at the pending-confirmation page. This matches the frozen recovery mechanism while accommodating Browser Use closing a completed session.

### Bound cost in code and record observed usage

Each run is capped by a fixed action limit and `max_completion_tokens`. A metering wrapper records prompt, cached-prompt, and completion tokens from the OpenAI responses and calculates USD cost using the declared price card. The environment key is never persisted.

### Preserve live evidence separately

Live evidence is written under an explicit user-selected directory and labels itself as stochastic validation, never as deterministic Proof #1.

## Risks / Trade-offs

- [The API key lacks model access or quota] → fail before any evidence claim; preserve no partial success as a result.
- [LLM behavior varies] → run five fresh worlds per condition, record all runs, and report counts rather than a fabricated pass rate.
- [A model call becomes unexpectedly long] → enforce steps and completion-token limits; actual cost is recorded per run.
- [Browser Use's adapter sends unsupported parameters] → configure the live model with reasoning settings and no temperature/frequency penalties.

## Context

AgentLab is a local FastAPI product that launches Browser Use against a controlled SQLite world. Its pinned runner supports a `ProviderConfig`, but the product execution path currently always selects the DeepSeek default and reads only `DEEPSEEK_API_KEY` from the process environment. The approved v1 product boundary is any public HTTPS endpoint that implements OpenAI Chat Completions; arbitrary provider protocols and private-network endpoints are excluded.

## Goals / Non-Goals

**Goals:**
- Let a learner configure a model endpoint, model identifier, and key for one session run.
- Reject malformed, non-HTTPS, credential-bearing, localhost, and private/reserved literal-IP endpoints before network access.
- Preflight a custom connector with a minimal Models and Chat Completions request.
- Use the approved configuration in the real Browser Use run and record non-secret provenance.
- Keep keys ephemeral: do not save them in session metadata, job data, Evidence, traces, API responses, or frontend persistence.

**Non-Goals:**
- Supporting arbitrary non-OpenAI protocols, private endpoints, OAuth, provider billing reconciliation, teams, or a production credential vault.
- Treating custom-endpoint USD cost as an official or trusted ranking metric.
- Changing the frozen default DeepSeek proof path or historical evidence.

## Decisions

1. Add a small `agentlab.model_connectors` boundary rather than parsing endpoint input in API routes. It owns normalization, public-network checks, non-secret provenance, and preflight. This keeps URL/secret policy testable and prevents a route-specific bypass.
2. Treat endpoint addresses as open but protocol as constrained. A base URL MUST be public HTTPS and the endpoint MUST answer the OpenAI-compatible Models and Chat Completions APIs. The local single-user MVP rejects literal local/private addresses but accepts a hostname that resolves through a local transparent proxy, because provider DNS mappings such as DeepSeek's cannot reliably be classified by Python's IP flags. Supporting a provider-specific adapter now would make preflight, metering, and Browser Use output contracts ambiguous.
3. Reuse the existing `ProviderConfig`-based Browser Use adapter with an explicit API-key override. The official default remains environment-backed; a custom connector creates an in-memory provider configuration only for the async job that received it.
4. The preflight API returns only connector metadata: endpoint hostname, SHA-256 endpoint/model fingerprint, model id, and `open` classification. The run start API revalidates the submitted connector and captures the key only in the spawned job closure; its serializable job and session metadata contain the public representation only.
5. Custom-run usage tokens remain observable when the provider returns them, but USD cost is `null` and marked untrusted because arbitrary compatible endpoints cannot provide a trustworthy pricing card. The existing fixed official provider continues to calculate cost normally.

## Risks / Trade-offs

- [DNS rebinding and SSRF] → Reject local hostnames and non-public literal IPs, validate hostname resolution before each preflight/run, reject URL credentials, and keep v1 to public HTTPS only. A production multi-tenant deployment MUST add an egress proxy that validates the connected address; the local MVP does not treat DNS classification as authoritative.
- [Endpoint receives task content] → Show the endpoint hostname and an explicit external-model disclosure before preflight/run; only users who supply the key can initiate the call.
- [Provider incompatibility] → Preflight checks both API families, and failure is returned as a clear connector error before Chromium starts.
- [Unknown pricing] → Mark custom runs as open and cost-untrusted; do not synthesize a USD value.
- [Key retention through exceptions] → Never include connector objects in persisted jobs or exception text; expose only generic infrastructure errors.

## Migration Plan

1. Preserve runs with no connector payload as official DeepSeek runs.
2. Add connector APIs and UI controls behind the existing local session flow.
3. Run API and UI verification with fake connectors; execute one optional live DeepSeek regression only with the existing environment key.
4. Roll back by omitting connector payloads; the default provider code path remains unchanged.

## Open Questions

- The present local MVP has no leaderboard. Future competition work will need a separate verified-provider policy before custom endpoint runs can influence a shared ranking.

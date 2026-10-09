# AI-to-AI Orchestration V1

Z1 remains the system of record. The orchestration layer is a controlled execution boundary between Zoë and external AI providers.

## Flow

Zoë / Z1 -> TaskEnvelope -> Provider Registry -> Provider Adapter -> model -> TaskResult -> Z1 audit sink

Every task receives a stable task_id and carries agent_id, model_id, provider_id, conversation_id, parent_task_id, and tenant_id.

## Providers

- openai: OpenAI Responses API adapter. Enabled only when OPENAI_API_KEY and OPENAI_MODEL are configured.
- gemini: Gemini generateContent adapter. Enabled only when GEMINI_API_KEY and GEMINI_MODEL are configured.
- copilot: explicit HTTP adapter, enabled only when COPILOT_ENDPOINT, COPILOT_API_KEY, and COPILOT_MODEL are configured. It does not assume that GitHub Copilot exposes a generic public inference endpoint.

## Routing

POST /v1/orchestrate requires Authorization: Bearer $Z1_ORCHESTRATOR_TOKEN.

Selection order:
1. explicit provider_id;
2. first configured provider from metadata.preferred_providers;
3. provider matching model_id;
4. OpenAI, then Gemini, then the first configured provider.

Provider credentials are never stored in Z1 memory or source code. They must be supplied as deployment secrets/environment variables.

## Audit

Set Z1_AUDIT_URL and Z1_AUDIT_TOKEN to forward task.started, task.completed, and task.failed events to the Z1 audit endpoint. Without those variables the forwarding sink is disabled; the execution path remains functional.

## Verification

The repository CI runs the orchestration unit test and Python compilation check. Live provider calls require real provider credentials and are intentionally not performed in CI.
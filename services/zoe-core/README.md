# zoe-core – ZOE BRAIN

The reasoning, planning, context, intent, response, and orchestration layer of the Zoë AI Platform.

## Modules

| Module | Description |
|---|---|
| `reasoning/` | LLM call wrappers, chain-of-thought, inference |
| `planning/` | Task decomposition, goal planning, step sequencing |
| `context/` | Context window management, retrieval-augmented generation |
| `intent/` | Intent classification and entity extraction |
| `response/` | Response formatting, streaming, validation |
| `orchestration/` | Agent orchestration, tool dispatching, flow control |

## Request lifecycle

```
User Request → intent/ → context/ → planning/ → reasoning/ → orchestration/ → response/ → User
```

See: [Architecture Blueprint](../../docs/architecture/ZOE-BLUEPRINT-V1.0.md#2-zoe-brain-zoe-core)

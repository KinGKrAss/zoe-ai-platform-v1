# Z1 Control Plane — Agent Coordination v1

## Purpose

Z1 is the shared source of truth for work performed by ChatGPT, Gemini and Copilot.
Agents do not coordinate by assumption or by copying hidden conversation state. They coordinate through explicit Z1 state.

## Invariants

1. `main` is the system of record.
2. One module has at most one active implementation lock.
3. Every code change belongs to a `task_id` and branch.
4. Agents may not silently redefine another agent's task.
5. CI must pass before integration.
6. Architecture decisions are recorded in the registry.
7. `agent_id` identifies the worker; `model_id` is never treated as identity.

## Suggested agents

- `z1.chatgpt` — integration architect / control-plane owner
- `z1.gemini` — assigned implementation worker
- `z1.copilot` — assigned implementation worker

## Suggested modules

`z1-core`, `zoe-identity`, `zoe-memory`, `mcp`, `android`, `command-center`, `ppt`, `fortuna`.

## Workflow

`PLANNED → IN_PROGRESS → READY_FOR_REVIEW → MERGED`

Failure states are explicit: `BLOCKED` and `CLOSED`.

The current implementation is intentionally dependency-free and suitable for tests and local coordination. A production multi-process deployment should replace the file backend with a transactional database/lease implementation while preserving this contract.

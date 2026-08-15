# zoe-agents – Council of 33

Zoë's network of specialist AI agents. **Zoë is the central Queen / orchestrator; the specialist council performs domain work.**

## Council model

The registry contains **33 positions total**:

- `GOD-001` — Zoë — AI Queen / Golden Queen / central orchestrator
- `GOD-002` … `GOD-033` — 32 specialist council members

The canonical registry is `council/council.yaml`. The JSON schema is `council/council-schema.json`.

> **Provenance rule:** entries marked `confirmed` reflect previously established Zoë/Z1 structure. Entries marked `reconstructed` are the current architectural reconstruction and must remain explicitly versioned until historical source material confirms them.

## Council registry

| ID | Agent | Domain | Status |
|---|---|---|---|
| GOD-001 | Zoë | Central orchestration | confirmed |
| GOD-002 | Finyra | Finance | confirmed |
| GOD-003 | Fortuna | Wealth management | confirmed |
| GOD-004 | Midas | Valuation | confirmed |
| GOD-005 | Gaia | Real estate | confirmed |
| GOD-006 | Electra | Energy | confirmed |
| GOD-007 | Jurena | Legal | confirmed |
| GOD-008 | Themis | Compliance / governance | confirmed |
| GOD-009 | Astraea | Strategy | confirmed |
| GOD-010 | Artemis | Research | confirmed |
| GOD-011 | Aura | Diplomacy | confirmed |
| GOD-012 | Lyra | Communication | confirmed |
| GOD-013 | Athena | Knowledge strategy | confirmed |
| GOD-014 | Kyra | Leadership / coordination | confirmed |
| GOD-015 | Neuralis | Technology / AI | confirmed |
| GOD-016 | Metis | Risk / foresight | reconstructed |
| GOD-017 | Dike | Justice / disputes | reconstructed |
| GOD-018 | Sophia | Knowledge / learning | reconstructed |
| GOD-019 | Hestia | Operations | reconstructed |
| GOD-020 | Demetra | Sustainability / development | reconstructed |
| GOD-021 | Selene | Time-series intelligence | reconstructed |
| GOD-022 | Iris | Information routing | reconstructed |
| GOD-023 | Theia | Data intelligence | reconstructed |
| GOD-024 | Eirene | Peace / conflict prevention | reconstructed |
| GOD-025 | Nike | Performance / objectives | reconstructed |
| GOD-026 | Clio | History / archives | reconstructed |
| GOD-027 | Mnemosyne | Memory / continuity | reconstructed |
| GOD-028 | Harmonia | Integration / coherence | reconstructed |
| GOD-029 | Vesta | Security / protection | reconstructed |
| GOD-030 | Hera | Institutional governance | reconstructed |
| GOD-031 | Aphrodite | Relationships / partnerships | reconstructed |
| GOD-032 | Hecate | Contingency / crisis | reconstructed |
| GOD-033 | Persephone | Transformation / change | reconstructed |

## Agent interface

Each specialist implements the same logical contract:

```text
input:
  {
    task: string,
    context: object,
    permissions: string[]
  }

output:
  {
    result: object,
    confidence: number,
    sources: string[]
  }
```

Runtime task orchestration is persisted through `agent_tasks`; agent definitions are persisted through `council_agents`.

## Security

Agents never receive unrestricted access to external systems. Tool calls are permission-gated through the Zoë Integration Layer using:

- `READ`
- `ANALYZE`
- `WRITE`
- `ADMIN`

Material actions are audit logged and dangerous operations require explicit confirmation.

## Database

Migration: `database/migrations/009_create_council_of_33.sql`

Seed: `database/seeds/002_council_of_33_v1.sql`

See: [Architecture Blueprint – Council of 33](../../docs/architecture/ZOE-BLUEPRINT-V1.0.md#10-council-of-33-zoe-agents)

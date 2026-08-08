# zoe-agents – Council of 33

Zoë's network of specialist AI agents. Zoë orchestrates these agents; she does not replace them.

## Agents

| Agent | Domain |
|---|---|
| `finance/` | Financial analysis, cashflow, valuation |
| `legal/` | Legal review, contracts, compliance |
| `realestate/` | Property intelligence, market analysis |
| `energy/` | Energy efficiency, sustainability |
| `strategy/` | Strategic planning, scenario analysis |
| `research/` | Data retrieval, market research |
| `diplomacy/` | Communication, negotiation, stakeholder management |
| `technology/` | Technical and IT analysis |
| `compliance/` | Regulatory compliance, reporting obligations |
| `risk/` | Risk assessment and mitigation |
| `communication/` | Reporting and communication output |

## Agent interface

Each agent implements a standard interface:

```
input:  { task: string, context: object, permissions: string[] }
output: { result: object, confidence: number, sources: string[] }
```

See: [Architecture Blueprint – Council of 33](../../docs/architecture/ZOE-BLUEPRINT-V1.0.md#10-council-of-33-zoe-agents)

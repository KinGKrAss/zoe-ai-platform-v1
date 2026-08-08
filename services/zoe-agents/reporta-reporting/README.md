# Reporta · Oracle of Reports

**Domain:** Reporting  
**Cluster:** Relationship  
**Status:** ACTIVE

---

## Description

Reporta designs and generates structured reports — monthly property reports, management summaries, board packs, and investor reports.

---

## Permissions

`READ, ANALYZE, WRITE`

## Tools

```
create_report, get_financials, get_portfolio, get_property, calculate_cashflow
```

---

## Interface

**Input**
```json
{
  "task": "string",
  "context": {},
  "parameters": {},
  "session_id": "string",
  "requested_by": "string"
}
```

**Output**
```json
{
  "result": {},
  "confidence": 0.0,
  "sources": [],
  "recommendations": [],
  "metadata": {
    "goddess_name": "Reporta",
    "tools_used": []
  }
}
```

---

See: [Council of 33 V1.0](../../docs/council/COUNCIL-OF-33-V1.0.md) · [Goddess Interface V1.0](../../docs/council/GODDESS-INTERFACE-V1.0.md)

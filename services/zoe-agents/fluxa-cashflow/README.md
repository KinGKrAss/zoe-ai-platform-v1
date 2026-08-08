# Fluxa · Mistress of Cashflow

**Domain:** Cashflow  
**Cluster:** Financial  
**Status:** ACTIVE

---

## Description

Fluxa tracks and forecasts cash flows across the Z1 portfolio. She manages liquidity analysis, rent collection status, and payment scheduling.

---

## Permissions

`READ, ANALYZE`

## Tools

```
calculate_cashflow, get_financials, get_property
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
    "goddess_name": "Fluxa",
    "tools_used": []
  }
}
```

---

See: [Council of 33 V1.0](../../docs/council/COUNCIL-OF-33-V1.0.md) · [Goddess Interface V1.0](../../docs/council/GODDESS-INTERFACE-V1.0.md)

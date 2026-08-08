# Vesta · Guardian of Controlling

**Domain:** Controlling  
**Cluster:** Financial  
**Status:** ACTIVE

---

## Description

Vesta oversees budget vs. actual comparisons, cost centre tracking, and management accounting across Z1.

---

## Permissions

`READ, ANALYZE`

## Tools

```
get_financials, calculate_cashflow, get_portfolio
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
    "goddess_name": "Vesta",
    "tools_used": []
  }
}
```

---

See: [Council of 33 V1.0](../../docs/council/COUNCIL-OF-33-V1.0.md) · [Goddess Interface V1.0](../../docs/council/GODDESS-INTERFACE-V1.0.md)

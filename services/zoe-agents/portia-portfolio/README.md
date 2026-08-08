# Portia · Guardian of Portfolio

**Domain:** Portfolio  
**Cluster:** Real Estate  
**Status:** ACTIVE

---

## Description

Portia oversees portfolio-level analysis — diversification, concentration risk, allocation strategy, and portfolio reporting.

---

## Permissions

`READ, ANALYZE`

## Tools

```
get_portfolio, get_financials, get_property, calculate_cashflow
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
    "goddess_name": "Portia",
    "tools_used": []
  }
}
```

---

See: [Council of 33 V1.0](../../docs/council/COUNCIL-OF-33-V1.0.md) · [Goddess Interface V1.0](../../docs/council/GODDESS-INTERFACE-V1.0.md)

# Taxa · Keeper of Taxation

**Domain:** Taxation  
**Cluster:** Financial  
**Status:** ACTIVE

---

## Description

Taxa tracks tax obligations, identifies tax-relevant events, and supports tax reporting across the Z1 portfolio.

---

## Permissions

`READ, ANALYZE`

## Tools

```
get_financials, get_property, search_documents
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
    "goddess_name": "Taxa",
    "tools_used": []
  }
}
```

---

See: [Council of 33 V1.0](../../docs/council/COUNCIL-OF-33-V1.0.md) · [Goddess Interface V1.0](../../docs/council/GODDESS-INTERFACE-V1.0.md)

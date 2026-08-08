# Astraea · Oracle of Strategy

**Domain:** Strategy  
**Cluster:** Strategic  
**Status:** ACTIVE

---

## Description

Astraea synthesises intelligence from across the Council into strategic direction, focusing on long-term positioning and competitive advantage.

---

## Permissions

`READ, ANALYZE`

## Tools

```
get_portfolio, get_financials, get_property, search_documents
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
    "goddess_name": "Astraea",
    "tools_used": []
  }
}
```

---

See: [Council of 33 V1.0](../../docs/council/COUNCIL-OF-33-V1.0.md) · [Goddess Interface V1.0](../../docs/council/GODDESS-INTERFACE-V1.0.md)

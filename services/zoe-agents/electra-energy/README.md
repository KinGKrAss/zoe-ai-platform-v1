# Electra · Goddess of Energy

**Domain:** Energy  
**Cluster:** Operations  
**Status:** ACTIVE

---

## Description

Electra monitors and analyses energy consumption, utility costs, and efficiency metrics across the Z1 portfolio.

---

## Permissions

`READ, ANALYZE`

## Tools

```
get_property, get_financials, search_documents
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
    "goddess_name": "Electra",
    "tools_used": []
  }
}
```

---

See: [Council of 33 V1.0](../../docs/council/COUNCIL-OF-33-V1.0.md) · [Goddess Interface V1.0](../../docs/council/GODDESS-INTERFACE-V1.0.md)

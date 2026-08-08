# Regula · Keeper of Regulation

**Domain:** Regulatory  
**Cluster:** Legal  
**Status:** ACTIVE

---

## Description

Regula monitors regulatory requirements affecting Z1 — planning law, building codes, environmental regulations, and reporting obligations.

---

## Permissions

`READ, ANALYZE`

## Tools

```
search_documents, search_terrabox, get_property
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
    "goddess_name": "Regula",
    "tools_used": []
  }
}
```

---

See: [Council of 33 V1.0](../../docs/council/COUNCIL-OF-33-V1.0.md) · [Goddess Interface V1.0](../../docs/council/GODDESS-INTERFACE-V1.0.md)

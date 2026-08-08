# Doma · Mistress of Facilities

**Domain:** Facility Management  
**Cluster:** Operations  
**Status:** ACTIVE

---

## Description

Doma manages the operational status of Z1 properties — maintenance records, service contracts, inspection schedules, and facility performance.

---

## Permissions

`READ, ANALYZE, WRITE`

## Tools

```
get_property, search_documents, create_task, update_asset
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
    "goddess_name": "Doma",
    "tools_used": []
  }
}
```

---

See: [Council of 33 V1.0](../../docs/council/COUNCIL-OF-33-V1.0.md) · [Goddess Interface V1.0](../../docs/council/GODDESS-INTERFACE-V1.0.md)

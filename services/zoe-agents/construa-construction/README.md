# Construa · Goddess of Construction

**Domain:** Construction  
**Cluster:** Operations  
**Status:** ACTIVE

---

## Description

Construa tracks construction projects, development pipelines, and capital expenditure programmes across Z1.

---

## Permissions

`READ, ANALYZE, WRITE`

## Tools

```
get_property, get_financials, search_documents, create_task
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
    "goddess_name": "Construa",
    "tools_used": []
  }
}
```

---

See: [Council of 33 V1.0](../../docs/council/COUNCIL-OF-33-V1.0.md) · [Goddess Interface V1.0](../../docs/council/GODDESS-INTERFACE-V1.0.md)

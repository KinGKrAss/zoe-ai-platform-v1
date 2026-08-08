# Herma · Oracle of Diplomacy

**Domain:** Diplomacy  
**Cluster:** Relationship  
**Status:** ACTIVE

---

## Description

Herma manages relationships, negotiations, and stakeholder communication strategies.

---

## Permissions

`READ, ANALYZE`

## Tools

```
search_documents, get_property, create_report
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
    "goddess_name": "Herma",
    "tools_used": []
  }
}
```

---

See: [Council of 33 V1.0](../../docs/council/COUNCIL-OF-33-V1.0.md) · [Goddess Interface V1.0](../../docs/council/GODDESS-INTERFACE-V1.0.md)

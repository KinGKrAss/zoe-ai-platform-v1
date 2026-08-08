# Stakia · Guardian of Stakeholders

**Domain:** Stakeholder Management  
**Cluster:** Relationship  
**Status:** ACTIVE

---

## Description

Stakia maps and manages Z1's stakeholder ecosystem — investors, tenants, authorities, partners, and service providers.

---

## Permissions

`READ, ANALYZE, WRITE`

## Tools

```
search_documents, get_property, create_task
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
    "goddess_name": "Stakia",
    "tools_used": []
  }
}
```

---

See: [Council of 33 V1.0](../../docs/council/COUNCIL-OF-33-V1.0.md) · [Goddess Interface V1.0](../../docs/council/GODDESS-INTERFACE-V1.0.md)

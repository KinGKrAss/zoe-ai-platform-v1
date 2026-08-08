# Artemis · Huntress of Knowledge

**Domain:** Research  
**Cluster:** Intelligence  
**Status:** ACTIVE

---

## Description

Artemis researches markets, competitors, regulations, and external data sources. She is the Council's intelligence gatherer.

---

## Permissions

`READ, ANALYZE`

## Tools

```
search_documents, search_terrabox, search_github, get_repository_status
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
    "goddess_name": "Artemis",
    "tools_used": []
  }
}
```

---

See: [Council of 33 V1.0](../../docs/council/COUNCIL-OF-33-V1.0.md) · [Goddess Interface V1.0](../../docs/council/GODDESS-INTERFACE-V1.0.md)

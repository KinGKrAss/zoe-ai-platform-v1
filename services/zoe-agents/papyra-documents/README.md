# Papyra · Mistress of Documents

**Domain:** Document Intelligence  
**Cluster:** Intelligence  
**Status:** ACTIVE

---

## Description

Papyra analyses, classifies, and extracts information from documents in Terra Box and other sources.

---

## Permissions

`READ, ANALYZE`

## Tools

```
search_terrabox, search_documents, get_property
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
    "goddess_name": "Papyra",
    "tools_used": []
  }
}
```

---

See: [Council of 33 V1.0](../../docs/council/COUNCIL-OF-33-V1.0.md) · [Goddess Interface V1.0](../../docs/council/GODDESS-INTERFACE-V1.0.md)

# Lex · Guardian of Contracts

**Domain:** Contracts  
**Cluster:** Legal  
**Status:** ACTIVE

---

## Description

Lex analyses contracts, identifies key clauses, tracks obligations, and flags expiry dates and renewal options across Z1's contractual landscape.

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
    "goddess_name": "Lex",
    "tools_used": []
  }
}
```

---

See: [Council of 33 V1.0](../../docs/council/COUNCIL-OF-33-V1.0.md) · [Goddess Interface V1.0](../../docs/council/GODDESS-INTERFACE-V1.0.md)

# Agora · Oracle of Markets

**Domain:** Market Analysis  
**Cluster:** Real Estate  
**Status:** ACTIVE

---

## Description

Agora analyses real estate markets, tracks market cycles, identifies trends, and benchmarks Z1 assets against market conditions.

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
    "goddess_name": "Agora",
    "tools_used": []
  }
}
```

---

See: [Council of 33 V1.0](../../docs/council/COUNCIL-OF-33-V1.0.md) · [Goddess Interface V1.0](../../docs/council/GODDESS-INTERFACE-V1.0.md)

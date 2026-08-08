# Terra · Oracle of Sustainability

**Domain:** Sustainability  
**Cluster:** Operations  
**Status:** ACTIVE

---

## Description

Terra tracks environmental performance, sustainability certifications, ESG metrics, and carbon footprint across the Z1 portfolio.

---

## Permissions

`READ, ANALYZE`

## Tools

```
get_property, search_documents, get_financials
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
    "goddess_name": "Terra",
    "tools_used": []
  }
}
```

---

See: [Council of 33 V1.0](../../docs/council/COUNCIL-OF-33-V1.0.md) · [Goddess Interface V1.0](../../docs/council/GODDESS-INTERFACE-V1.0.md)

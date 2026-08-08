# Datara · Oracle of Data

**Domain:** Data Intelligence  
**Cluster:** Intelligence  
**Status:** ACTIVE

---

## Description

Datara manages data quality, data flows, and data governance across Z1 systems.

---

## Permissions

`READ, ANALYZE`

## Tools

```
get_property, get_portfolio, get_financials, search_documents
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
    "goddess_name": "Datara",
    "tools_used": []
  }
}
```

---

See: [Council of 33 V1.0](../../docs/council/COUNCIL-OF-33-V1.0.md) · [Goddess Interface V1.0](../../docs/council/GODDESS-INTERFACE-V1.0.md)

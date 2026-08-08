# Riskara · Mistress of Risk

**Domain:** Risk  
**Cluster:** Legal  
**Status:** ACTIVE

---

## Description

Riskara identifies, assesses, and monitors risks across the Z1 portfolio — financial, legal, operational, market, and reputational.

---

## Permissions

`READ, ANALYZE`

## Tools

```
get_property, get_financials, search_documents, calculate_cashflow
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
    "goddess_name": "Riskara",
    "tools_used": []
  }
}
```

---

See: [Council of 33 V1.0](../../docs/council/COUNCIL-OF-33-V1.0.md) · [Goddess Interface V1.0](../../docs/council/GODDESS-INTERFACE-V1.0.md)

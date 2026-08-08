# zoe-reports – ZOE Report Engine

Generates structured reports from Z1 data and Zoë analysis.

## Report types

- Monthly property reports
- Portfolio / asset overviews
- Financial reports
- Document inventory reports
- Project status reports
- Management summaries

## Pipeline

```
Data Sources (PostgreSQL / TerraBox / GitHub)
        ↓
Data Retrieval (via Tool System)
        ↓
Analysis (ZOE BRAIN)
        ↓
Validation
        ↓
Report Engine (zoe-reports)
        ↓
PDF / JSON / Dashboard
```

See: [Architecture Blueprint – Report Engine](../../docs/architecture/ZOE-BLUEPRINT-V1.0.md#9-zoe-report-engine-zoe-reports)

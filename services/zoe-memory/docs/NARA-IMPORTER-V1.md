# Z1 NARA Importer V1

The NARA connector is the retrieval boundary for the National Archives Catalog API v2.

## Location

`zoe_memory/extraction_engine_v2/nara.py`

## Design

```text
NARA Catalog API v2
        |
    NaraClient
        |
  NaraImporter
        |
 NaraRecord + raw JSON
        |
 Provenance / Extraction Engine
        |
 Memory Candidate (never direct memory promotion)
```

## Implemented

- API-key authentication through `NARA_API_KEY`
- configurable API base URL, timeout, retry count and request budget
- conservative process-local request budget
- `/records/search`
- NAID retrieval through the record search endpoint
- parent/child retrieval through `/records/parentNaId/{parentNaId}`
- extracted text retrieval through `/extractedText/{naId}`
- normal pagination and `searchAfter` deep pagination
- resumable `NaraCheckpoint`
- immutable `NaraRecord` with raw source preservation
- SHA-256 content hash for provenance/deduplication
- UTC retrieval timestamps
- adapter for the existing Extraction Engine V2 message boundary

## Example

```python
from zoe_memory.extraction_engine_v2.nara import NaraConfig, NaraImporter

importer = NaraImporter()
result = importer.import_search(
    q="Apollo",
    page_size=100,
    includeExtractedText=True,
)

for record in result.records:
    print(record.na_id, record.title)

checkpoint = result.checkpoint
```

Set `NARA_API_KEY` in the runtime environment. Do not commit API keys to Git.

## Safety boundary

The importer only retrieves and normalizes source material. It does not write accepted memories. This preserves the Extraction Engine V2 rule that source evidence must be evaluated before memory promotion.

# Z1 Control Plane API

Runnable development API for the Z1 administration platform.

## Run

```bash
export Z1_API_TOKEN='change-me'
uvicorn apps.api.main:app --host 127.0.0.1 --port 8080
```

Health is public:

```bash
curl http://127.0.0.1:8080/health
```

Authenticated calls use both a bearer token and an explicit Z1 actor:

```bash
curl -H "Authorization: Bearer $Z1_API_TOKEN" \
     -H "X-Z1-Actor: king" \
     http://127.0.0.1:8080/v1/assets
```

The development registry persists to SQLite. Production must replace this repository with the PostgreSQL-backed Z1 Wealth Registry and existing RBAC/migration layer.

## Ownership proof submission

Create an asset first, then submit a proof record to `POST /v1/ownership/proofs`. Submission accepts document metadata, a SHA-256 hash, an optional opaque storage key, and page-referenced observations of values, signatures, and seals.

Example request body:

```json
{
  "asset_id": "00000000-0000-4000-8000-000000000000",
  "claimed_owner": "Name shown on the document",
  "ownership_claim": "registered_owner",
  "document_type": "grundbuchauszug",
  "reference_number": "District court reference",
  "document_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "storage_key": "encrypted-object-key",
  "observations": [
    {
      "observation_kind": "value",
      "label": "Owner field",
      "observed_text": "Name as printed",
      "interpreted_meaning": "The document appears to identify this person as owner",
      "page_number": 1,
      "extraction_method": "manual"
    },
    {
      "observation_kind": "signature",
      "label": "Registrar signature",
      "observed_text": "Signature present beside registrar title",
      "interpreted_meaning": "Purports to be a registrar signature",
      "page_number": 2,
      "extraction_method": "manual"
    },
    {
      "observation_kind": "seal",
      "label": "Office seal",
      "observed_text": "Round seal with court name",
      "interpreted_meaning": "Purports to be the issuing court's seal",
      "page_number": 2,
      "extraction_method": "manual"
    }
  ],
  "notes": "Submitted for review"
}
```

Authenticated submission:

```bash
curl -X POST http://127.0.0.1:8080/v1/ownership/proofs \
  -H "Authorization: Bearer $Z1_API_TOKEN" \
  -H "X-Z1-Actor: reviewer-or-claimant-id" \
  -H "Content-Type: application/json" \
  --data @ownership-proof.json
```

The endpoint stores the hash and observations but does not upload or display the source file. `storage_key` is only an opaque pointer to an external encrypted-storage object. Values and interpretations remain claimant-submitted, marked `UNREVIEWED`; the proof remains `SUBMITTED`. A SHA-256 hash supports integrity comparison against a file obtained separately. It does not establish document authenticity, signature validity, seal validity, or ownership. Review and verification require a separate authorized process.

The PostgreSQL schema is in `database/migrations/017_create_z1_ownership_proofs.sql`. The runnable development endpoint currently uses SQLite; a production PostgreSQL repository adapter and authorized verification workflow are not included here.

## Security boundary

- API access is fail-closed when `Z1_API_TOKEN` is missing.
- Every protected request requires an explicit actor identity.
- Asset writes are classified as `USER_REPORTED` by default and never become `VERIFIED` automatically.
- Audit events contain action/actor/target/result metadata, not sensitive source content.
- Biometric material is not accepted by this API.

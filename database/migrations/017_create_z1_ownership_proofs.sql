-- Migration: 017_create_z1_ownership_proofs.sql
-- FORTUNA ownership claims linked to the existing asset and evidence registries.
-- Submission records a claim; verification is a separate, reviewed operation.

CREATE TABLE IF NOT EXISTS z1_ownership_proofs (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  asset_id              UUID NOT NULL REFERENCES z1_wealth_assets(id) ON DELETE CASCADE,
  evidence_id           UUID NOT NULL UNIQUE REFERENCES z1_wealth_evidence(id) ON DELETE CASCADE,
  claimant_id           VARCHAR(200) NOT NULL,
  claimed_owner         VARCHAR(300) NOT NULL,
  ownership_claim       VARCHAR(100) NOT NULL,
  document_type         VARCHAR(100) NOT NULL,
  reference_number      VARCHAR(255),
  storage_key           VARCHAR(128),
  verification_status   VARCHAR(30) NOT NULL DEFAULT 'SUBMITTED',
  verification_notes    TEXT,
  verified_by           VARCHAR(200),
  verified_at           TIMESTAMPTZ,
  created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT z1_ownership_proofs_status_check CHECK (
    verification_status IN ('SUBMITTED','INCOMPLETE','UNDER_REVIEW','VERIFIED','REJECTED','CONFLICT')
  ),
  CONSTRAINT z1_ownership_proofs_document_type_check CHECK (
    document_type IN ('grundbuchauszug','handelsregister','kaufvertrag','fahrzeugbrief','erc721','kontoauszug','sonstiger_nachweis')
  ),
  CONSTRAINT z1_ownership_proofs_storage_key_check CHECK (
    storage_key IS NULL OR storage_key ~ '^[A-Za-z0-9_-]{1,128}$'
  ),
  CONSTRAINT z1_ownership_proofs_verified_metadata_check CHECK (
    verification_status <> 'VERIFIED' OR (verified_by IS NOT NULL AND verified_at IS NOT NULL)
  )
);

CREATE TABLE IF NOT EXISTS z1_ownership_proof_observations (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  proof_id              UUID NOT NULL REFERENCES z1_ownership_proofs(id) ON DELETE CASCADE,
  observation_kind      VARCHAR(20) NOT NULL,
  label                 VARCHAR(200) NOT NULL,
  observed_text         TEXT NOT NULL,
  interpreted_meaning   TEXT,
  normalized_value      TEXT,
  page_number           INTEGER,
  extraction_method     VARCHAR(20) NOT NULL DEFAULT 'manual',
  review_status         VARCHAR(20) NOT NULL DEFAULT 'UNREVIEWED',
  reviewed_by           VARCHAR(200),
  reviewed_at           TIMESTAMPTZ,
  review_notes          TEXT,
  created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT z1_ownership_observation_kind_check CHECK (
    observation_kind IN ('value','signature','seal')
  ),
  CONSTRAINT z1_ownership_observation_page_check CHECK (
    page_number IS NULL OR page_number > 0
  ),
  CONSTRAINT z1_ownership_observation_method_check CHECK (
    extraction_method IN ('manual','ocr','metadata')
  ),
  CONSTRAINT z1_ownership_observation_review_check CHECK (
    review_status IN ('UNREVIEWED','CONFIRMED','DISPUTED','REJECTED')
  )
);

CREATE INDEX IF NOT EXISTS idx_z1_ownership_proofs_asset
  ON z1_ownership_proofs(asset_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_z1_ownership_proofs_status
  ON z1_ownership_proofs(verification_status);
CREATE INDEX IF NOT EXISTS idx_z1_ownership_observations_proof
  ON z1_ownership_proof_observations(proof_id, page_number);
CREATE INDEX IF NOT EXISTS idx_z1_ownership_observations_kind
  ON z1_ownership_proof_observations(observation_kind, review_status);

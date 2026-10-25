-- Migration: 018_create_z1_fortuna_international_registers.sql
-- International property and PPT/MIDAS records with explicit source and review state.
-- Submitted values are claims; this migration does not independently verify ownership or balances.

CREATE TABLE IF NOT EXISTS z1_fortuna_international_properties (
  id                       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  property_name            VARCHAR(255) NOT NULL,
  country_code             CHAR(2) NOT NULL,
  legal_entity             VARCHAR(255) NOT NULL,
  local_tax_id             VARCHAR(100),
  valuation_local_currency NUMERIC(28, 8) NOT NULL CHECK (valuation_local_currency >= 0),
  currency_code            CHAR(3) NOT NULL,
  valuation_eur            NUMERIC(28, 8),
  fx_rate_to_eur           NUMERIC(28, 12),
  fx_source                VARCHAR(255),
  ownership_share_percent  NUMERIC(7, 4) NOT NULL DEFAULT 100.0000,
  reporting_date           DATE NOT NULL,
  evidence_reference       TEXT,
  document_hash            CHAR(64),
  storage_key              VARCHAR(128),
  record_status            VARCHAR(24) NOT NULL DEFAULT 'SUBMITTED',
  created_by               VARCHAR(200) NOT NULL,
  verified_by              VARCHAR(200),
  verified_at              TIMESTAMPTZ,
  created_at               TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT z1_fortuna_int_property_country_check
    CHECK (country_code ~ '^[A-Z]{2}$'),
  CONSTRAINT z1_fortuna_int_property_currency_check
    CHECK (currency_code ~ '^[A-Z]{3}$'),
  CONSTRAINT z1_fortuna_int_property_ownership_check
    CHECK (ownership_share_percent >= 0 AND ownership_share_percent <= 100),
  CONSTRAINT z1_fortuna_int_property_document_hash_check
    CHECK (document_hash IS NULL OR document_hash ~ '^[a-f0-9]{64}$'),
  CONSTRAINT z1_fortuna_int_property_storage_key_check
    CHECK (storage_key IS NULL OR storage_key ~ '^[A-Za-z0-9_-]{1,128}$'),
  CONSTRAINT z1_fortuna_int_property_fx_check
    CHECK (
      (valuation_eur IS NULL AND fx_rate_to_eur IS NULL AND fx_source IS NULL)
      OR (valuation_eur IS NOT NULL AND fx_rate_to_eur > 0 AND fx_source IS NOT NULL)
    ),
  CONSTRAINT z1_fortuna_int_property_status_check
    CHECK (record_status IN ('SUBMITTED','INCOMPLETE','UNDER_REVIEW','VERIFIED','REJECTED','CONFLICT')),
  CONSTRAINT z1_fortuna_int_property_verified_metadata_check
    CHECK (record_status <> 'VERIFIED' OR (verified_by IS NOT NULL AND verified_at IS NOT NULL))
);

CREATE TABLE IF NOT EXISTS z1_fortuna_ppt_midas_entries (
  id                       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  custody_type             VARCHAR(24) NOT NULL,
  custody_reference        VARCHAR(255) NOT NULL,
  asset_class              VARCHAR(40) NOT NULL,
  asset_symbol             VARCHAR(100) NOT NULL,
  quantity_nominal         NUMERIC(32, 12) CHECK (quantity_nominal IS NULL OR quantity_nominal >= 0),
  chain_id                 VARCHAR(120),
  public_wallet_address    VARCHAR(255),
  reporting_date           DATE NOT NULL,
  balance_nominal          NUMERIC(32, 12) NOT NULL CHECK (balance_nominal >= 0),
  currency_code            CHAR(3) NOT NULL,
  valuation_eur            NUMERIC(32, 12),
  fx_rate_to_eur           NUMERIC(28, 12),
  fx_source                VARCHAR(255),
  q1_return_nominal        NUMERIC(32, 12),
  q1_period_start          DATE,
  q1_period_end            DATE,
  evidence_reference       TEXT,
  document_hash            CHAR(64),
  storage_key              VARCHAR(128),
  transaction_reference    VARCHAR(255),
  verification_status      VARCHAR(24) NOT NULL DEFAULT 'SUBMITTED',
  audit_notes              TEXT,
  created_by               VARCHAR(200) NOT NULL,
  verified_by              VARCHAR(200),
  verified_at              TIMESTAMPTZ,
  created_at               TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT z1_fortuna_ppt_custody_type_check
    CHECK (custody_type IN ('bank','custodian','onchain_wallet','other')),
  CONSTRAINT z1_fortuna_ppt_onchain_reference_check
    CHECK (custody_type <> 'onchain_wallet' OR (chain_id IS NOT NULL AND public_wallet_address IS NOT NULL)),
  CONSTRAINT z1_fortuna_ppt_asset_class_check
    CHECK (asset_class IN ('fiat_pool','crypto_asset','token','yield_accrual','other')),
  CONSTRAINT z1_fortuna_ppt_token_quantity_check
    CHECK (asset_class NOT IN ('crypto_asset','token') OR quantity_nominal IS NOT NULL),
  CONSTRAINT z1_fortuna_ppt_currency_check
    CHECK (currency_code ~ '^[A-Z]{3}$'),
  CONSTRAINT z1_fortuna_ppt_fx_check
    CHECK (
      (valuation_eur IS NULL AND fx_rate_to_eur IS NULL AND fx_source IS NULL)
      OR (valuation_eur IS NOT NULL AND fx_rate_to_eur > 0 AND fx_source IS NOT NULL)
    ),
  CONSTRAINT z1_fortuna_ppt_document_hash_check
    CHECK (document_hash IS NULL OR document_hash ~ '^[a-f0-9]{64}$'),
  CONSTRAINT z1_fortuna_ppt_storage_key_check
    CHECK (storage_key IS NULL OR storage_key ~ '^[A-Za-z0-9_-]{1,128}$'),
  CONSTRAINT z1_fortuna_ppt_q1_dates_check
    CHECK (
      (q1_return_nominal IS NULL AND q1_period_start IS NULL AND q1_period_end IS NULL)
      OR (q1_return_nominal IS NOT NULL AND q1_period_start IS NOT NULL
          AND q1_period_end IS NOT NULL AND q1_period_end >= q1_period_start)
    ),
  CONSTRAINT z1_fortuna_ppt_status_check
    CHECK (verification_status IN ('SUBMITTED','INCOMPLETE','UNDER_REVIEW','VERIFIED','REJECTED','CONFLICT')),
  CONSTRAINT z1_fortuna_ppt_verified_metadata_check
    CHECK (verification_status <> 'VERIFIED' OR (verified_by IS NOT NULL AND verified_at IS NOT NULL))
);

CREATE INDEX IF NOT EXISTS idx_z1_fortuna_int_property_country_date
  ON z1_fortuna_international_properties(country_code, reporting_date DESC);
CREATE INDEX IF NOT EXISTS idx_z1_fortuna_int_property_entity
  ON z1_fortuna_international_properties(legal_entity);
CREATE INDEX IF NOT EXISTS idx_z1_fortuna_int_property_status
  ON z1_fortuna_international_properties(record_status);
CREATE INDEX IF NOT EXISTS idx_z1_fortuna_ppt_custody_date
  ON z1_fortuna_ppt_midas_entries(custody_reference, reporting_date DESC);
CREATE INDEX IF NOT EXISTS idx_z1_fortuna_ppt_status
  ON z1_fortuna_ppt_midas_entries(verification_status);

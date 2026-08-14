-- Migration: 015_create_zoe_z1_wealth_registry.sql
-- Zoë/Z1 Master Wealth Registry: auditable assets, valuations, evidence and consolidation.
-- Design rule: evidence-backed values are distinct from user-reported and derived values.

CREATE TABLE IF NOT EXISTS z1_wealth_assets (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  asset_key           VARCHAR(200) NOT NULL UNIQUE,
  asset_name          VARCHAR(300) NOT NULL,
  asset_type          VARCHAR(80) NOT NULL,
  module              VARCHAR(40) NOT NULL DEFAULT 'FORTUNA',
  legal_owner         VARCHAR(300),
  jurisdiction        VARCHAR(120),
  status              VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
  description         TEXT,
  metadata            JSONB NOT NULL DEFAULT '{}',
  created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT z1_wealth_assets_status_check
    CHECK (status IN ('ACTIVE','PENDING_VERIFICATION','DISPOSED','ARCHIVED'))
);

CREATE TABLE IF NOT EXISTS z1_wealth_valuations (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  asset_id            UUID NOT NULL REFERENCES z1_wealth_assets(id) ON DELETE CASCADE,
  valuation_date      DATE NOT NULL,
  value_amount       NUMERIC(24,4) NOT NULL,
  currency            CHAR(3) NOT NULL,
  valuation_method    VARCHAR(80),
  evidence_status     VARCHAR(30) NOT NULL DEFAULT 'UNVERIFIED',
  source_id           VARCHAR(200),
  source_location     TEXT,
  confidence          NUMERIC(5,2),
  notes               TEXT,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT z1_wealth_valuations_evidence_check
    CHECK (evidence_status IN ('VERIFIED','USER_REPORTED','DERIVED','UNVERIFIED','CONFLICT')),
  CONSTRAINT z1_wealth_valuations_confidence_check
    CHECK (confidence IS NULL OR (confidence >= 0 AND confidence <= 100))
);

CREATE TABLE IF NOT EXISTS z1_wealth_evidence (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  asset_id            UUID REFERENCES z1_wealth_assets(id) ON DELETE CASCADE,
  valuation_id        UUID REFERENCES z1_wealth_valuations(id) ON DELETE CASCADE,
  evidence_type       VARCHAR(60) NOT NULL,
  source_name         VARCHAR(300) NOT NULL,
  source_reference    TEXT,
  document_hash       VARCHAR(128),
  evidence_date       DATE,
  retrieved_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  status              VARCHAR(30) NOT NULL DEFAULT 'PENDING',
  notes               TEXT,
  metadata            JSONB NOT NULL DEFAULT '{}',
  CONSTRAINT z1_wealth_evidence_status_check
    CHECK (status IN ('VERIFIED','PENDING','REJECTED','SUPERSEDED')),
  CONSTRAINT z1_wealth_evidence_link_check
    CHECK (asset_id IS NOT NULL OR valuation_id IS NOT NULL)
);

CREATE TABLE IF NOT EXISTS z1_wealth_relationships (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  parent_asset_id     UUID NOT NULL REFERENCES z1_wealth_assets(id) ON DELETE CASCADE,
  child_asset_id      UUID NOT NULL REFERENCES z1_wealth_assets(id) ON DELETE CASCADE,
  relationship_type   VARCHAR(50) NOT NULL,
  ownership_pct       NUMERIC(7,4),
  notes               TEXT,
  CONSTRAINT z1_wealth_relationships_no_self CHECK (parent_asset_id <> child_asset_id),
  CONSTRAINT z1_wealth_relationships_pct_check
    CHECK (ownership_pct IS NULL OR (ownership_pct >= 0 AND ownership_pct <= 100)),
  UNIQUE (parent_asset_id, child_asset_id, relationship_type)
);

CREATE TABLE IF NOT EXISTS z1_wealth_consolidation_snapshots (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  snapshot_date       DATE NOT NULL,
  base_currency       CHAR(3) NOT NULL DEFAULT 'EUR',
  verified_total      NUMERIC(28,4) NOT NULL DEFAULT 0,
  reported_total      NUMERIC(28,4) NOT NULL DEFAULT 0,
  derived_total       NUMERIC(28,4) NOT NULL DEFAULT 0,
  excluded_total      NUMERIC(28,4) NOT NULL DEFAULT 0,
  fx_source            VARCHAR(200),
  methodology         TEXT,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (snapshot_date, base_currency)
);

CREATE INDEX IF NOT EXISTS idx_z1_wealth_assets_type ON z1_wealth_assets(asset_type);
CREATE INDEX IF NOT EXISTS idx_z1_wealth_assets_module ON z1_wealth_assets(module);
CREATE INDEX IF NOT EXISTS idx_z1_wealth_valuations_asset_date ON z1_wealth_valuations(asset_id, valuation_date DESC);
CREATE INDEX IF NOT EXISTS idx_z1_wealth_valuations_status ON z1_wealth_valuations(evidence_status);
CREATE INDEX IF NOT EXISTS idx_z1_wealth_evidence_asset ON z1_wealth_evidence(asset_id);
CREATE INDEX IF NOT EXISTS idx_z1_wealth_evidence_valuation ON z1_wealth_evidence(valuation_id);
CREATE INDEX IF NOT EXISTS idx_z1_wealth_relationships_parent ON z1_wealth_relationships(parent_asset_id);
CREATE INDEX IF NOT EXISTS idx_z1_wealth_relationships_child ON z1_wealth_relationships(child_asset_id);

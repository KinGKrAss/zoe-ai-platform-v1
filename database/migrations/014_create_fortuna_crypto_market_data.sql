-- Migration: 014_create_fortuna_crypto_market_data.sql
-- FORTUNA CryptoMarketData schema.

CREATE TABLE IF NOT EXISTS fortuna_crypto_assets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  cmc_id BIGINT NOT NULL UNIQUE,
  symbol VARCHAR(32) NOT NULL,
  name VARCHAR(200) NOT NULL,
  slug VARCHAR(220),
  rank INTEGER,
  platform JSONB,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  first_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS fortuna_crypto_quotes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  asset_id UUID NOT NULL REFERENCES fortuna_crypto_assets(id) ON DELETE CASCADE,
  currency VARCHAR(16) NOT NULL,
  price NUMERIC(38,18),
  market_cap NUMERIC(38,18),
  volume_24h NUMERIC(38,18),
  percent_change_1h NUMERIC(18,8),
  percent_change_24h NUMERIC(18,8),
  percent_change_7d NUMERIC(18,8),
  circulating_supply NUMERIC(38,18),
  total_supply NUMERIC(38,18),
  max_supply NUMERIC(38,18),
  source_updated_at TIMESTAMPTZ,
  fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_fortuna_crypto_quotes_asset_time ON fortuna_crypto_quotes(asset_id, fetched_at DESC);
CREATE INDEX IF NOT EXISTS idx_fortuna_crypto_assets_symbol ON fortuna_crypto_assets(symbol);

CREATE TABLE IF NOT EXISTS fortuna_crypto_api_usage (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  provider VARCHAR(64) NOT NULL DEFAULT 'coinmarketcap',
  endpoint VARCHAR(255) NOT NULL,
  request_count INTEGER NOT NULL DEFAULT 1,
  credit_count NUMERIC(18,4) NOT NULL DEFAULT 0,
  status_code INTEGER,
  requested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_fortuna_crypto_usage_time ON fortuna_crypto_api_usage(requested_at DESC);

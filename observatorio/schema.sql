-- Esquema Relacional del Observatorio de Precios de TallerLab
-- Compatible tanto con SQLite como con PostgreSQL

CREATE TABLE IF NOT EXISTS catalog_products (
    id VARCHAR(64) PRIMARY KEY,
    category VARCHAR(32) NOT NULL,
    brand VARCHAR(64) NOT NULL,
    model_name VARCHAR(128) NOT NULL,
    mpn VARCHAR(64),
    gtin_ean VARCHAR(32),
    voltage VARCHAR(32),
    specs_json TEXT,
    kit_content VARCHAR(255) NOT NULL,
    item_condition VARCHAR(16) NOT NULL DEFAULT 'nuevo',
    guide_url VARCHAR(255),
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sources (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    domain VARCHAR(128) NOT NULL,
    access_method VARCHAR(64) NOT NULL,
    terms_reference TEXT NOT NULL,
    status VARCHAR(32) NOT NULL,
    conservation_restrictions TEXT,
    max_requests_per_minute INTEGER DEFAULT 20,
    terms_verified_date TEXT,
    redistribution_allowed INTEGER NOT NULL DEFAULT 0,
    capture_allowed INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS offers (
    id VARCHAR(64) PRIMARY KEY,
    product_id VARCHAR(64) NOT NULL REFERENCES catalog_products(id),
    source_id VARCHAR(64) NOT NULL REFERENCES sources(id),
    seller_name VARCHAR(128) NOT NULL,
    direct_url TEXT NOT NULL,
    affiliate_url TEXT,
    external_sku VARCHAR(128),
    extraction_method VARCHAR(64) NOT NULL,
    enabled INTEGER NOT NULL DEFAULT 1,
    last_checked_at TEXT,
    next_attempt_at TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS collector_runs (
    id VARCHAR(64) PRIMARY KEY,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    status VARCHAR(32) NOT NULL,
    total_offers INTEGER DEFAULT 0,
    successful_offers INTEGER DEFAULT 0,
    failed_offers INTEGER DEFAULT 0,
    anomalies_detected INTEGER DEFAULT 0,
    error_summary TEXT
);

CREATE TABLE IF NOT EXISTS observations (
    id VARCHAR(64) PRIMARY KEY,
    run_id VARCHAR(64) REFERENCES collector_runs(id),
    offer_id VARCHAR(64) NOT NULL REFERENCES offers(id),
    product_id VARCHAR(64) NOT NULL REFERENCES catalog_products(id),
    observed_at TEXT NOT NULL,
    price_single_payment NUMERIC(14, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'ARS',
    price_transfer NUMERIC(14, 2),
    price_reference_shown NUMERIC(14, 2),
    availability VARCHAR(32) NOT NULL,
    shipping_cost NUMERIC(14, 2),
    shipping_note VARCHAR(255),
    validation_status VARCHAR(32) NOT NULL,
    is_published INTEGER NOT NULL DEFAULT 0,
    extractor_version VARCHAR(32) NOT NULL,
    raw_evidence_hash VARCHAR(64),
    raw_evidence_snippet TEXT,
    is_synthetic INTEGER NOT NULL DEFAULT 0,
    capture_key TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS incidents (
    id VARCHAR(64) PRIMARY KEY,
    offer_id VARCHAR(64) REFERENCES offers(id),
    run_id VARCHAR(64) REFERENCES collector_runs(id),
    incident_type VARCHAR(64) NOT NULL,
    severity VARCHAR(16) NOT NULL,
    details TEXT NOT NULL,
    resolved INTEGER NOT NULL DEFAULT 0,
    resolution_note TEXT,
    created_at TEXT NOT NULL,
    resolved_at TEXT
);

CREATE TABLE IF NOT EXISTS data_versions (
    version_id VARCHAR(32) PRIMARY KEY,
    applied_at TEXT NOT NULL,
    description TEXT NOT NULL,
    methodology_version VARCHAR(32) NOT NULL
);

-- Índices de consulta rápida
CREATE INDEX IF NOT EXISTS idx_obs_product_pub ON observations (product_id, is_published, observed_at);
CREATE INDEX IF NOT EXISTS idx_obs_offer_time ON observations (offer_id, observed_at);
CREATE INDEX IF NOT EXISTS idx_offers_product_enabled ON offers (product_id, enabled);
CREATE INDEX IF NOT EXISTS idx_incidents_active ON incidents (resolved, created_at);
CREATE INDEX IF NOT EXISTS idx_catalog_category_active ON catalog_products (category, is_active);
CREATE INDEX IF NOT EXISTS idx_obs_synthetic ON observations (is_synthetic, is_published);
CREATE UNIQUE INDEX IF NOT EXISTS idx_obs_capture_key ON observations (capture_key);

CREATE TABLE IF NOT EXISTS collector_attempts (
    id TEXT PRIMARY KEY,
    run_id VARCHAR(64) REFERENCES collector_runs(id),
    offer_id VARCHAR(64) REFERENCES offers(id),
    observed_at TEXT NOT NULL,
    status TEXT NOT NULL,
    is_synthetic INTEGER NOT NULL DEFAULT 0,
    details TEXT
);
CREATE INDEX IF NOT EXISTS idx_attempt_offer ON collector_attempts(offer_id, observed_at);
CREATE TABLE IF NOT EXISTS collector_lease (
    id INTEGER PRIMARY KEY,
    owner TEXT,
    expires_at TEXT NOT NULL
);

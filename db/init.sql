-- Run once against the Postgres instance the consumer writes to.
-- Stage 2 note: embedding is a placeholder 3-dim vector built from the
-- numeric telemetry fields themselves, not a learned semantic embedding.
-- The agent in Stage 2 replaces it with real embeddings without changing
-- the table shape.

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS telemetry_events (
    id               BIGSERIAL PRIMARY KEY,
    device_id        TEXT        NOT NULL,
    sector_id        TEXT        NOT NULL,
    event_time       TIMESTAMPTZ NOT NULL,
    signal_strength_dbm REAL     NOT NULL,
    snr_db           REAL        NOT NULL,
    sector_load_pct  REAL        NOT NULL,
    link_state       TEXT        NOT NULL,
    is_anomaly       BOOLEAN     NOT NULL DEFAULT FALSE,
    anomaly_reason   TEXT,
    embedding        VECTOR(3),
    ingested_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_telemetry_events_event_time ON telemetry_events (event_time);
CREATE INDEX IF NOT EXISTS idx_telemetry_events_anomaly ON telemetry_events (is_anomaly) WHERE is_anomaly;

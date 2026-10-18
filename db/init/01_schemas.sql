-- Run once by the postgres container on first start (empty volume).
CREATE SCHEMA IF NOT EXISTS raw;      -- data as ingested
CREATE SCHEMA IF NOT EXISTS staging;  -- dbt: cleaned
CREATE SCHEMA IF NOT EXISTS marts;    -- dbt: analytics tables
CREATE SCHEMA IF NOT EXISTS ops;      -- prediction log

CREATE TABLE IF NOT EXISTS ops.predictions (
    id            BIGSERIAL PRIMARY KEY,
    ticket_text   TEXT        NOT NULL,
    model_name    TEXT        NOT NULL,
    predicted     TEXT        NOT NULL,
    confidence    REAL,
    latency_ms    INTEGER,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

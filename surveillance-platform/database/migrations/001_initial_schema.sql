-- Surveillance Platform: Initial Schema Migration
-- Creates all core tables: users, cameras, zones, rules, events, tracks

BEGIN;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ── Users ──
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(20) NOT NULL DEFAULT 'OPERATOR',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── Cameras ──
CREATE TABLE IF NOT EXISTS cameras (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    source_reference TEXT NOT NULL,
    location_label VARCHAR(255),
    enabled BOOLEAN DEFAULT TRUE,
    status VARCHAR(20) DEFAULT 'OFFLINE',
    owner_id UUID REFERENCES users(id) ON DELETE SET NULL,
    last_seen_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── Zones ──
CREATE TABLE IF NOT EXISTS zones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    camera_id UUID NOT NULL REFERENCES cameras(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    polygon JSONB NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── Rules ──
CREATE TABLE IF NOT EXISTS rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    camera_id UUID NOT NULL REFERENCES cameras(id) ON DELETE CASCADE,
    rule_type VARCHAR(50) NOT NULL,
    configuration JSONB NOT NULL DEFAULT '{}',
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── Events ──
CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    camera_id UUID NOT NULL REFERENCES cameras(id),
    event_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL DEFAULT 'INFO',
    confidence FLOAT NOT NULL DEFAULT 0.0,
    occurred_at TIMESTAMPTZ NOT NULL,
    track_id VARCHAR(50),
    evidence_uri TEXT,
    status VARCHAR(20) DEFAULT 'NEW',
    metadata JSONB
);

-- Performance indexes for events
CREATE INDEX ix_events_camera_occurred ON events (camera_id, occurred_at);
CREATE INDEX ix_events_type_occurred ON events (event_type, occurred_at);
CREATE INDEX ix_events_severity ON events (severity);
CREATE INDEX ix_events_status ON events (status);

-- ── Tracks ──
CREATE TABLE IF NOT EXISTS tracks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    camera_id UUID NOT NULL REFERENCES cameras(id),
    track_id VARCHAR(50) NOT NULL,
    object_class VARCHAR(50) NOT NULL,
    first_seen TIMESTAMPTZ NOT NULL,
    last_seen TIMESTAMPTZ NOT NULL,
    summary JSONB
);

CREATE INDEX ix_tracks_camera_track ON tracks (camera_id, track_id);

COMMIT;

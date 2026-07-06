-- Migration 004: Create frustration_logs, repetition_schedule, and weakness_history tables
-- These tables support direct queries made by memory_store.py
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ── 1. FRUSTRATION LOGS ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS frustration_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    topic TEXT NOT NULL,
    frustration_score NUMERIC DEFAULT 0.0,
    frustration_level TEXT DEFAULT 'low',
    frustration_triggers TEXT[] DEFAULT '{}',
    confusion_count INTEGER DEFAULT 0,
    mistake_count INTEGER DEFAULT 0,
    consecutive_failures INTEGER DEFAULT 0,
    difficulty_signals INTEGER DEFAULT 0,
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    first_detected TIMESTAMPTZ DEFAULT NOW(),
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMPTZ,
    CONSTRAINT unique_user_frustration_topic UNIQUE (user_id, topic)
);

-- ── 2. REPETITION SCHEDULE ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS repetition_schedule (
    schedule_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    topic TEXT NOT NULL,
    repetition_count INTEGER DEFAULT 0,
    ease_factor NUMERIC DEFAULT 2.5,
    review_interval INTEGER DEFAULT 1,
    next_review_date TIMESTAMPTZ DEFAULT NOW(),
    last_reviewed TIMESTAMPTZ,
    first_studied TIMESTAMPTZ DEFAULT NOW(),
    retention_score NUMERIC DEFAULT 0.0,
    review_priority NUMERIC DEFAULT 0.0,
    quality_history INTEGER[] DEFAULT '{}',
    total_reviews INTEGER DEFAULT 0,
    is_overdue BOOLEAN DEFAULT FALSE,
    is_due_today BOOLEAN DEFAULT FALSE,
    CONSTRAINT unique_user_repetition_topic UNIQUE (user_id, topic)
);

-- ── 3. WEAKNESS HISTORY ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS weakness_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    topic TEXT NOT NULL,
    previous_score NUMERIC NOT NULL,
    new_score NUMERIC NOT NULL,
    delta NUMERIC NOT NULL,
    reason TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- ── 4. INDEXES ───────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_frustration_logs_user ON frustration_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_repetition_schedule_user ON repetition_schedule(user_id);
CREATE INDEX IF NOT EXISTS idx_weakness_history_user ON weakness_history(user_id);

-- ── 5. ROW-LEVEL SECURITY (RLS) POLICIES ────────────────────────────────────
ALTER TABLE frustration_logs ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS frustration_logs_policy ON frustration_logs;
CREATE POLICY frustration_logs_policy ON frustration_logs
    FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

ALTER TABLE repetition_schedule ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS repetition_schedule_policy ON repetition_schedule;
CREATE POLICY repetition_schedule_policy ON repetition_schedule
    FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

ALTER TABLE weakness_history ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS weakness_history_policy ON weakness_history;
CREATE POLICY weakness_history_policy ON weakness_history
    FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

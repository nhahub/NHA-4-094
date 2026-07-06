-- Migration: Initialize memory and personalization tables
-- This migration script sets up user profiles, memory items, conversation summaries,
-- chat sessions, messages, progress/mastery, and planner context tables.

-- Enable extensions (pgcrypto and vector)
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS vector;

-- ── 1. CHAT SESSIONS ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── 2. MESSAGES ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    topic TEXT,
    retrieved_chunks UUID[] DEFAULT '{}',
    source_chunk_id UUID REFERENCES document_chunks(id) ON DELETE SET NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    token_usage JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── 3. USER LEARNING PROFILES ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS user_learning_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE,
    academic_level TEXT DEFAULT 'beginner',
    learning_level TEXT DEFAULT 'beginner', -- Alias/synonym kept for safety
    learning_goals JSONB DEFAULT '[]'::jsonb,
    preferred_language TEXT DEFAULT 'auto',
    preferred_style TEXT DEFAULT 'balanced',
    explanation_style TEXT DEFAULT 'simple', -- Alias/synonym kept for safety
    explanation_depth TEXT DEFAULT 'medium',
    default_difficulty TEXT DEFAULT 'auto',
    strengths JSONB DEFAULT '[]'::jsonb,
    weaknesses JSONB DEFAULT '[]'::jsonb,
    accessibility_prefs JSONB DEFAULT '{}'::jsonb,
    confidence_score NUMERIC DEFAULT 0.5,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── 4. MEMORY ITEMS (LONG-TERM SEMANTIC MEMORY) ──────────────────────────────
CREATE TABLE IF NOT EXISTS memory_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    source_id UUID,
    source_type TEXT CHECK (source_type IN ('document', 'page', 'global')),
    session_id UUID REFERENCES chat_sessions(id) ON DELETE SET NULL,
    memory_type TEXT CHECK (memory_type IN ('preference', 'learning_goal', 'weakness', 'strength', 'misconception', 'session_summary', 'study_progress', 'accessibility')),
    content TEXT NOT NULL,
    summary TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    embedding vector(1024),
    importance NUMERIC DEFAULT 0.5,
    confidence NUMERIC DEFAULT 0.5,
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── 5. CONVERSATION SUMMARIES ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS conversation_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    source_id UUID,
    source_type TEXT DEFAULT 'document',
    summary_text TEXT NOT NULL,
    structured_summary JSONB DEFAULT '{}'::jsonb,
    last_message_id UUID REFERENCES messages(id) ON DELETE SET NULL,
    token_count INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── 6. LEARNING EVENTS ───────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS learning_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    source_id UUID,
    session_id UUID REFERENCES chat_sessions(id) ON DELETE SET NULL,
    event_type TEXT NOT NULL,
    topic TEXT,
    score NUMERIC,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── 7. TOPIC MASTERY ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS topic_mastery (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    source_id UUID,
    topic TEXT NOT NULL,
    subject TEXT,
    mastery_score NUMERIC DEFAULT 0,
    times_studied INTEGER DEFAULT 0,
    avg_quiz_score NUMERIC DEFAULT 0,
    latest_score NUMERIC DEFAULT 0,
    mastery_level TEXT DEFAULT 'learning',
    is_weak BOOLEAN DEFAULT FALSE,
    last_studied TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_user_topic UNIQUE (user_id, topic)
);

-- ── 8. WEAK TOPICS ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS weak_topics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    source_id UUID,
    topic TEXT NOT NULL,
    weakness_score NUMERIC DEFAULT 0,
    failed_count INTEGER DEFAULT 0,
    quiz_score NUMERIC DEFAULT 0,
    resolved BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_user_weak_topic UNIQUE (user_id, topic)
);

-- ── 9. MISTAKE PATTERNS ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS mistake_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    source_id UUID,
    topic TEXT NOT NULL,
    mistake_type TEXT,
    mistake_text TEXT NOT NULL,
    correct_answer TEXT,
    frequency INTEGER DEFAULT 1,
    severity TEXT DEFAULT 'medium',
    resolved BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── 10. PLANNER CONTEXT ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS planner_context (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE,
    last_intent TEXT DEFAULT '',
    last_task TEXT DEFAULT '',
    last_topic TEXT DEFAULT '',
    last_subject TEXT DEFAULT '',
    last_session_id TEXT DEFAULT '',
    last_response_type TEXT DEFAULT '',
    last_doc_name TEXT DEFAULT '',
    last_question TEXT DEFAULT '',
    unfinished_goals JSONB DEFAULT '[]'::jsonb,
    pending_topics JSONB DEFAULT '[]'::jsonb,
    previous_session_summary TEXT DEFAULT '',
    previous_session_id TEXT DEFAULT '',
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── 11. INDEXES ─────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user ON chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id);
CREATE INDEX IF NOT EXISTS idx_messages_user ON messages(user_id);
CREATE INDEX IF NOT EXISTS idx_memory_items_user ON memory_items(user_id);
CREATE INDEX IF NOT EXISTS idx_memory_items_session ON memory_items(session_id);
CREATE INDEX IF NOT EXISTS idx_memory_items_type ON memory_items(memory_type);
CREATE INDEX IF NOT EXISTS idx_conversation_summaries_session ON conversation_summaries(session_id);
CREATE INDEX IF NOT EXISTS idx_learning_events_user ON learning_events(user_id);
CREATE INDEX IF NOT EXISTS idx_topic_mastery_user ON topic_mastery(user_id);
CREATE INDEX IF NOT EXISTS idx_topic_mastery_topic ON topic_mastery(topic);
CREATE INDEX IF NOT EXISTS idx_weak_topics_user ON weak_topics(user_id);
CREATE INDEX IF NOT EXISTS idx_weak_topics_topic ON weak_topics(topic);
CREATE INDEX IF NOT EXISTS idx_mistake_patterns_user ON mistake_patterns(user_id);
CREATE INDEX IF NOT EXISTS idx_mistake_patterns_topic ON mistake_patterns(topic);

-- Create HNSW index for memory items semantic search using cosine distance
CREATE INDEX IF NOT EXISTS memory_items_embedding_idx
ON memory_items
USING hnsw (embedding vector_cosine_ops);

-- ── 12. ROW-LEVEL SECURITY (RLS) POLICIES ────────────────────────────────────
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS chat_sessions_policy ON chat_sessions;
CREATE POLICY chat_sessions_policy ON chat_sessions
    FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS messages_policy ON messages;
CREATE POLICY messages_policy ON messages
    FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

ALTER TABLE user_learning_profiles ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS user_learning_profiles_policy ON user_learning_profiles;
CREATE POLICY user_learning_profiles_policy ON user_learning_profiles
    FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

ALTER TABLE memory_items ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS memory_items_policy ON memory_items;
CREATE POLICY memory_items_policy ON memory_items
    FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

ALTER TABLE conversation_summaries ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS conversation_summaries_policy ON conversation_summaries;
CREATE POLICY conversation_summaries_policy ON conversation_summaries
    FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

ALTER TABLE learning_events ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS learning_events_policy ON learning_events;
CREATE POLICY learning_events_policy ON learning_events
    FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

ALTER TABLE topic_mastery ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS topic_mastery_policy ON topic_mastery;
CREATE POLICY topic_mastery_policy ON topic_mastery
    FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

ALTER TABLE weak_topics ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS weak_topics_policy ON weak_topics;
CREATE POLICY weak_topics_policy ON weak_topics
    FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

ALTER TABLE mistake_patterns ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS mistake_patterns_policy ON mistake_patterns;
CREATE POLICY mistake_patterns_policy ON mistake_patterns
    FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

ALTER TABLE planner_context ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS planner_context_policy ON planner_context;
CREATE POLICY planner_context_policy ON planner_context
    FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

-- ── 13. STORED PROCEDURE FOR SEMANTIC SEARCH ───────────────────────────────
CREATE OR REPLACE FUNCTION match_memory_items(
    query_embedding vector(1024),
    match_threshold float,
    match_count int,
    p_user_id uuid
)
RETURNS TABLE (
    id uuid,
    user_id uuid,
    source_id uuid,
    source_type text,
    session_id uuid,
    memory_type text,
    content text,
    summary text,
    metadata jsonb,
    importance numeric,
    confidence numeric,
    is_active boolean,
    expires_at timestamptz,
    created_at timestamptz,
    updated_at timestamptz,
    similarity numeric
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        m.id,
        m.user_id,
        m.source_id,
        m.source_type,
        m.session_id,
        m.memory_type,
        m.content,
        m.summary,
        m.metadata,
        m.importance,
        m.confidence,
        m.is_active,
        m.expires_at,
        m.created_at,
        m.updated_at,
        (1 - (m.embedding <=> query_embedding))::numeric AS similarity
    FROM memory_items m
    WHERE m.user_id = p_user_id
      AND m.is_active = true
      AND (1 - (m.embedding <=> query_embedding)) > match_threshold
    ORDER BY m.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

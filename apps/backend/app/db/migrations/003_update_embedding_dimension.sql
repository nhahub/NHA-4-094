-- Migration 003: Update embedding vector dimension to 1024
-- Required because we switched from 384/768 dim models to Cloudflare Workers AI BGE-M3 (1024 dimensions).
--
-- WARNING: This migration drops all existing vectors and re-creates the columns.
-- Existing documents and memories must be re-processed or updated to get 1024-dim embeddings.

-- ── 1. UPDATE DOCUMENT CHUNKS TABLE ──────────────────────────────────────────
-- Drop the existing HNSW index
DROP INDEX IF EXISTS document_chunks_embedding_idx;

-- Replace old embedding column with a new 1024-dim one
ALTER TABLE document_chunks DROP COLUMN IF EXISTS embedding;
ALTER TABLE document_chunks ADD COLUMN embedding vector(1024);

-- Re-create the HNSW index for the new 1024-dim column
CREATE INDEX IF NOT EXISTS document_chunks_embedding_idx
ON document_chunks
USING hnsw (embedding vector_cosine_ops);

-- ── 2. UPDATE MEMORY ITEMS TABLE ──────────────────────────────────────────────
-- Drop the existing HNSW index
DROP INDEX IF EXISTS memory_items_embedding_idx;

-- Replace old embedding column with a new 1024-dim one
ALTER TABLE memory_items DROP COLUMN IF EXISTS embedding;
ALTER TABLE memory_items ADD COLUMN embedding vector(1024);

-- Re-create the HNSW index for the new 1024-dim column
CREATE INDEX IF NOT EXISTS memory_items_embedding_idx
ON memory_items
USING hnsw (embedding vector_cosine_ops);

-- ── 3. UPDATE STORED PROCEDURE FOR SEMANTIC SEARCH ───────────────────────────
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

-- ── 4. MARK DOCUMENTS FOR RE-PROCESSING ──────────────────────────────────────
UPDATE documents
SET upload_status = 'uploaded', 
    error_message = 'Re-processing required: embedding dimension changed to 1024 for Cloudflare BGE-M3.'
WHERE upload_status = 'ready';

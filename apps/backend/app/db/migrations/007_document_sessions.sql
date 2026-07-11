-- Migration: Link chat sessions to document context
-- Add nullable document_id to chat_sessions table to isolate chat histories.

ALTER TABLE chat_sessions 
ADD COLUMN IF NOT EXISTS document_id UUID REFERENCES documents(id) ON DELETE CASCADE;

-- Create user_id + document_id search index
CREATE INDEX IF NOT EXISTS idx_chat_sessions_doc ON chat_sessions(user_id, document_id);

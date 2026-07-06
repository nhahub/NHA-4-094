from typing import List, Dict, Any, Optional
import logging
from app.db.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)
supabase = get_supabase_client()

async def create_chat_session(user_id: str, session_id: str) -> Dict[str, Any]:
    """Creates a new chat session in PostgreSQL."""
    logger.info(f"[DB] Creating chat session {session_id} for user {user_id}")
    
    # Check if session already exists
    existing = supabase.table("chat_sessions").select("*").eq("id", session_id).execute()
    if existing.data:
        return existing.data[0]
        
    response = supabase.table("chat_sessions").insert({
        "id": session_id,
        "user_id": user_id
    }).execute()
    return response.data[0] if response.data else {}

async def get_chat_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Gets a chat session by id."""
    response = supabase.table("chat_sessions").select("*").eq("id", session_id).execute()
    return response.data[0] if response.data else None

async def save_message(
    session_id: str,
    user_id: str,
    role: str,
    content: str,
    topic: Optional[str] = None,
    retrieved_chunks: List[str] = None,
    source_chunk_id: Optional[str] = None,
    metadata: Dict[str, Any] = None,
    token_usage: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Saves a message (user or assistant) in PostgreSQL."""
    logger.info(f"[DB] Saving {role} message to session {session_id}")
    
    # Ensure session exists first
    await create_chat_session(user_id, session_id)
    
    row = {
        "session_id": session_id,
        "user_id": user_id,
        "role": role,
        "content": content,
    }
    if topic:
        row["topic"] = topic
    if retrieved_chunks:
        row["retrieved_chunks"] = retrieved_chunks
    if source_chunk_id:
        row["source_chunk_id"] = source_chunk_id
    if metadata:
        row["metadata"] = metadata
    if token_usage:
        row["token_usage"] = token_usage
        
    response = supabase.table("messages").insert(row).execute()
    return response.data[0] if response.data else {}

async def get_session_messages(session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieves message history for a session ordered by created_at ascending."""
    response = (
        supabase.table("messages")
        .select("*")
        .eq("session_id", session_id)
        .order("created_at", desc=False)
        .limit(limit)
        .execute()
    )
    return response.data or []

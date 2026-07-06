from typing import List, Dict, Any, Optional
import logging
from app.db.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)
supabase = get_supabase_client()

async def get_latest_summary(user_id: str, session_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves the latest summary for a specific session."""
    response = (
        supabase.table("conversation_summaries")
        .select("*")
        .eq("user_id", user_id)
        .eq("session_id", session_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    return response.data[0] if response.data else None

async def upsert_summary(summary: Dict[str, Any]) -> Dict[str, Any]:
    """Upserts session summary."""
    data = dict(summary)
    session_id = data.get("session_id")
    user_id = data.get("user_id")
    
    # Check if a summary exists for this session
    existing = await get_latest_summary(user_id, session_id)
    if existing:
        record_id = existing["id"]
        data["updated_at"] = "now()"
        response = supabase.table("conversation_summaries").update(data).eq("id", record_id).execute()
    else:
        response = supabase.table("conversation_summaries").insert(data).execute()
        
    return response.data[0] if response.data else {}

async def get_session_summaries(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Gets summaries of all sessions for a user."""
    response = (
        supabase.table("conversation_summaries")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return response.data or []

async def update_last_message_id(summary_id: str, last_message_id: str) -> Dict[str, Any]:
    """Updates the reference to the last message processed by the summarizer."""
    response = (
        supabase.table("conversation_summaries")
        .update({
            "last_message_id": last_message_id,
            "updated_at": "now()"
        })
        .eq("id", summary_id)
        .execute()
    )
    return response.data[0] if response.data else {}

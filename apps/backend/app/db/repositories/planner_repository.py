from typing import Dict, Any, Optional
import logging
from app.db.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)
supabase = get_supabase_client()

async def get_planner_context(user_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves the planner context for a user."""
    response = supabase.table("planner_context").select("*").eq("user_id", user_id).execute()
    return response.data[0] if response.data else None

async def upsert_planner_context(context: Dict[str, Any]) -> Dict[str, Any]:
    """Upserts the planner context for a user."""
    data = dict(context)
    user_id = data.get("user_id")
    
    # Map context_id to id and remove it to prevent database schema errors
    if "context_id" in data:
        if "id" not in data:
            data["id"] = data["context_id"]
        data.pop("context_id")
        
    existing = await get_planner_context(user_id)
    if existing:
        record_id = existing["id"]
        data["updated_at"] = "now()"
        response = supabase.table("planner_context").update(data).eq("id", record_id).execute()
    else:
        response = supabase.table("planner_context").insert(data).execute()
        
    return response.data[0] if response.data else {}

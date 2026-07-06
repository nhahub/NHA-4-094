from typing import List, Dict, Any, Optional
import logging
from app.db.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)
supabase = get_supabase_client()

async def save_memory_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """Saves a long-term memory item to Supabase."""
    logger.info(f"[DB] Saving memory item for user {item.get('user_id')}")
    # Convert datetime to string if present
    data = dict(item)
    if data.get("expires_at") is not None:
        if hasattr(data["expires_at"], "isoformat"):
            data["expires_at"] = data["expires_at"].isoformat()
    
    response = supabase.table("memory_items").insert(data).execute()
    return response.data[0] if response.data else {}

async def update_memory_item(item_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """Updates an existing memory item."""
    logger.info(f"[DB] Updating memory item {item_id}")
    data = dict(updates)
    if "expires_at" in data and hasattr(data["expires_at"], "isoformat"):
        data["expires_at"] = data["expires_at"].isoformat()
    if "updated_at" in data and hasattr(data["updated_at"], "isoformat"):
        data["updated_at"] = data["updated_at"].isoformat()
        
    response = supabase.table("memory_items").update(data).eq("id", item_id).execute()
    return response.data[0] if response.data else {}

async def deactivate_memory_item(item_id: str) -> Dict[str, Any]:
    """Deactivates a memory item by setting is_active to False."""
    logger.info(f"[DB] Deactivating memory item {item_id}")
    response = supabase.table("memory_items").update({"is_active": False, "updated_at": "now()"}).eq("id", item_id).execute()
    return response.data[0] if response.data else {}

async def get_memory_items(
    user_id: str,
    memory_type: Optional[str] = None,
    source_id: Optional[str] = None,
    source_type: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """Retrieves active memory items for a user, filtered optionally by type/source."""
    query = supabase.table("memory_items").select("*").eq("user_id", user_id).eq("is_active", True)
    if memory_type:
        query = query.eq("memory_type", memory_type)
    if source_id:
        query = query.eq("source_id", source_id)
    if source_type:
        query = query.eq("source_type", source_type)
    
    response = query.order("created_at", desc=True).limit(limit).execute()
    return response.data or []

async def semantic_search_memory_items(
    user_id: str,
    query_embedding: List[float],
    threshold: float = 0.3,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """Performs a semantic search over memory items using stored procedure match_memory_items."""
    try:
        response = supabase.rpc("match_memory_items", {
            "query_embedding": query_embedding,
            "match_threshold": threshold,
            "match_count": limit,
            "p_user_id": user_id
        }).execute()
        return response.data or []
    except Exception as e:
        logger.error(f"[DB] Semantic search memory items failed: {str(e)}")
        # Fallback to metadata-based query if RPC is not loaded/fails during tests
        return await get_memory_items(user_id=user_id, limit=limit)

async def save_learning_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """Saves a learning event signal."""
    response = supabase.table("learning_events").insert(event).execute()
    return response.data[0] if response.data else {}

async def get_learning_events(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Gets learning events for a user."""
    response = supabase.table("learning_events").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
    return response.data or []

async def save_mistake_pattern(mistake: Dict[str, Any]) -> Dict[str, Any]:
    """Saves a mistake pattern record."""
    response = supabase.table("mistake_patterns").insert(mistake).execute()
    return response.data[0] if response.data else {}

async def get_mistake_patterns(
    user_id: str,
    topic: Optional[str] = None,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """Retrieves unresolved mistake patterns for a topic or user."""
    query = supabase.table("mistake_patterns").select("*").eq("user_id", user_id).eq("resolved", False)
    if topic:
        query = query.eq("topic", topic)
    response = query.order("frequency", desc=True).limit(limit).execute()
    return response.data or []

async def upsert_weak_topic(weak_topic: Dict[str, Any]) -> Dict[str, Any]:
    """Upserts a weak topic for a user."""
    data = dict(weak_topic)
    user_id = data.get("user_id")
    topic = data.get("topic")
    
    # Check if exists
    existing = (
        supabase.table("weak_topics")
        .select("*")
        .eq("user_id", user_id)
        .eq("topic", topic)
        .execute()
    )
    if existing.data:
        record_id = existing.data[0]["id"]
        data["updated_at"] = "now()"
        response = supabase.table("weak_topics").update(data).eq("id", record_id).execute()
    else:
        response = supabase.table("weak_topics").insert(data).execute()
        
    return response.data[0] if response.data else {}

async def get_weak_topics(
    user_id: str,
    resolved: bool = False,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """Retrieves unresolved weak topics ordered by weakness_score descending."""
    response = (
        supabase.table("weak_topics")
        .select("*")
        .eq("user_id", user_id)
        .eq("resolved", resolved)
        .order("weakness_score", desc=True)
        .limit(limit)
        .execute()
    )
    return response.data or []

async def upsert_topic_mastery(topic_mastery: Dict[str, Any]) -> Dict[str, Any]:
    """Upserts topic mastery record."""
    data = dict(topic_mastery)
    user_id = data.get("user_id")
    topic = data.get("topic")
    
    # Check if exists
    existing = (
        supabase.table("topic_mastery")
        .select("*")
        .eq("user_id", user_id)
        .eq("topic", topic)
        .execute()
    )
    if existing.data:
        record_id = existing.data[0]["id"]
        data["updated_at"] = "now()"
        response = supabase.table("topic_mastery").update(data).eq("id", record_id).execute()
    else:
        response = supabase.table("topic_mastery").insert(data).execute()
        
    return response.data[0] if response.data else {}

async def get_topic_mastery(
    user_id: str,
    topic: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Retrieves topic mastery records for a user."""
    query = supabase.table("topic_mastery").select("*").eq("user_id", user_id)
    if topic:
        query = query.eq("topic", topic)
    response = query.execute()
    return response.data or []

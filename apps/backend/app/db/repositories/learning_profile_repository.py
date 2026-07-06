from typing import Dict, Any, Optional
import logging
from app.db.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)
supabase = get_supabase_client()

async def get_profile(user_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves the personalization profile for a user."""
    response = supabase.table("user_learning_profiles").select("*").eq("user_id", user_id).execute()
    return response.data[0] if response.data else None

async def upsert_profile(profile: Dict[str, Any]) -> Dict[str, Any]:
    """Upserts the learning profile for a user."""
    data = dict(profile)
    user_id = data.get("user_id")
    
    existing = await get_profile(user_id)
    if existing:
        data["updated_at"] = "now()"
        response = supabase.table("user_learning_profiles").update(data).eq("user_id", user_id).execute()
    else:
        response = supabase.table("user_learning_profiles").insert(data).execute()
        
    return response.data[0] if response.data else {}

async def update_preferences(
    user_id: str,
    preferred_language: str,
    preferred_style: str,
    explanation_depth: str
) -> Dict[str, Any]:
    """Updates core style preferences for a user."""
    response = (
        supabase.table("user_learning_profiles")
        .update({
            "preferred_language": preferred_language,
            "preferred_style": preferred_style,
            "explanation_style": preferred_style, # keep alias in sync
            "explanation_depth": explanation_depth,
            "updated_at": "now()"
        })
        .eq("user_id", user_id)
        .execute()
    )
    return response.data[0] if response.data else {}

async def update_accessibility_prefs(user_id: str, accessibility_prefs: Dict[str, Any]) -> Dict[str, Any]:
    """Updates accessibility settings for a user."""
    response = (
        supabase.table("user_learning_profiles")
        .update({
            "accessibility_prefs": accessibility_prefs,
            "accessibility": accessibility_prefs, # keep alias in sync
            "updated_at": "now()"
        })
        .eq("user_id", user_id)
        .execute()
    )
    return response.data[0] if response.data else {}

async def update_learning_level(user_id: str, learning_level: str) -> Dict[str, Any]:
    """Updates academic/learning level for a user."""
    response = (
        supabase.table("user_learning_profiles")
        .update({
            "academic_level": learning_level,
            "learning_level": learning_level, # keep alias in sync
            "updated_at": "now()"
        })
        .eq("user_id", user_id)
        .execute()
    )
    return response.data[0] if response.data else {}

async def update_strengths_weaknesses(
    user_id: str,
    strengths: list,
    weaknesses: list
) -> Dict[str, Any]:
    """Updates identified student strengths and weaknesses."""
    response = (
        supabase.table("user_learning_profiles")
        .update({
            "strengths": strengths,
            "strong_subjects": strengths, # keep alias in sync
            "weaknesses": weaknesses,
            "weak_subjects": weaknesses, # keep alias in sync
            "updated_at": "now()"
        })
        .eq("user_id", user_id)
        .execute()
    )
    return response.data[0] if response.data else {}

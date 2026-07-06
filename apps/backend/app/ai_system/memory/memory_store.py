import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import json

from app.db.supabase_client import get_supabase_client
from app.db.repositories import (
    memory_repository,
    learning_profile_repository,
    conversation_summary_repository,
    chat_repository,
    planner_repository
)
from app.schemas.personalization_schema import UserProfile, AccessibilityPreferences
from app.schemas.memory_schema import (
    MemoryItem, WeakTopic, MistakePattern, TopicMastery,
    ConversationSummary, LearningEvent
)
from app.ai_system.memory.memory_types import ChatMessage
from app.ai_system.providers.embedding_client import embed_texts
from app.ai_system.memory import memory_config

logger = logging.getLogger(__name__)

class MemoryStore:
    """
    Production-grade Service layer wrapping repository calls for memory persistence.
    Operates completely in async mode using Supabase PostgreSQL.
    """
    def __init__(self) -> None:
        self.supabase = get_supabase_client()

    def get_embedding(self, text: str) -> List[float]:
        """Generates embedding for a single text using production model."""
        try:
            vectors = embed_texts([text])
            return vectors[0] if vectors else [0.0] * memory_config.EMBEDDING_DIM
        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            return [0.0] * memory_config.EMBEDDING_DIM

    # ── User Profile CRUD ────────────────────────────────────────────────────
    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        profile_dict = await learning_profile_repository.get_profile(user_id)
        if not profile_dict:
            return None
        return UserProfile.model_validate(profile_dict)

    async def upsert_user_profile(self, profile: UserProfile) -> UserProfile:
        dump = profile.model_dump()
        # Convert datetimes to strings
        if dump.get("created_at") and hasattr(dump["created_at"], "isoformat"):
            dump["created_at"] = dump["created_at"].isoformat()
        if dump.get("updated_at") and hasattr(dump["updated_at"], "isoformat"):
            dump["updated_at"] = dump["updated_at"].isoformat()
        # Serialize accessibility preferences sub-model
        if isinstance(dump.get("accessibility_prefs"), dict):
            pass # already dict
        elif hasattr(dump.get("accessibility_prefs"), "model_dump"):
            dump["accessibility_prefs"] = dump["accessibility_prefs"].model_dump()
        if isinstance(dump.get("accessibility"), dict):
            pass
        elif hasattr(dump.get("accessibility"), "model_dump"):
            dump["accessibility"] = dump["accessibility"].model_dump()
            
        res = await learning_profile_repository.upsert_profile(dump)
        return UserProfile.model_validate(res)

    # ── Chat Messages CRUD ───────────────────────────────────────────────────
    async def save_message(self, message: ChatMessage) -> Dict[str, Any]:
        """Saves user/assistant chat history message."""
        return await chat_repository.save_message(
            session_id=message.session_id,
            user_id=message.user_id,
            role=message.role,
            content=message.content,
            topic=message.topic
        )

    async def get_all_session_messages(self, user_id: str, session_id: str) -> List[ChatMessage]:
        messages_list = await chat_repository.get_session_messages(session_id)
        # Filter by user_id for multi-user isolation
        messages_list = [m for m in messages_list if str(m.get("user_id")) == str(user_id)]
        
        chat_messages = []
        for m in messages_list:
            chat_messages.append(ChatMessage(
                id=str(m["id"]),
                session_id=str(m["session_id"]),
                user_id=str(m["user_id"]),
                role=m["role"],
                content=m["content"],
                topic=m.get("topic"),
                created_at=datetime.fromisoformat(m["created_at"].replace("Z", "+00:00")) if isinstance(m.get("created_at"), str) else m.get("created_at")
            ))
        return chat_messages

    async def count_session_messages(self, user_id: str, session_id: str) -> int:
        messages = await self.get_all_session_messages(user_id, session_id)
        return len(messages)

    # ── Memory Items CRUD (Long-term) ────────────────────────────────────────
    async def save_memory_item(self, item: MemoryItem) -> Dict[str, Any]:
        dump = item.model_dump()
        # Generate semantic embedding
        dump["embedding"] = self.get_embedding(item.content)
        return await memory_repository.save_memory_item(dump)

    async def get_memory_items(
        self, user_id: str, memory_type: Optional[str] = None,
        source_id: Optional[str] = None, source_type: Optional[str] = None
    ) -> List[MemoryItem]:
        items = await memory_repository.get_memory_items(
            user_id=user_id,
            memory_type=memory_type,
            source_id=source_id,
            source_type=source_type
        )
        return [MemoryItem.model_validate(item) for item in items]

    async def semantic_search_memories(
        self, user_id: str, query: str, threshold: float = 0.3, limit: int = 5
    ) -> List[MemoryItem]:
        embedding = self.get_embedding(query)
        items = await memory_repository.semantic_search_memory_items(
            user_id=user_id,
            query_embedding=embedding,
            threshold=threshold,
            limit=limit
        )
        return [MemoryItem.model_validate(item) for item in items]

    # ── Mistake Patterns ─────────────────────────────────────────────────────
    async def save_mistake(self, mistake: MistakePattern) -> Dict[str, Any]:
        return await memory_repository.save_mistake_pattern(mistake.model_dump())

    async def get_mistakes(self, user_id: str, topic: Optional[str] = None, limit: int = 5) -> List[MistakePattern]:
        items = await memory_repository.get_mistake_patterns(user_id=user_id, topic=topic, limit=limit)
        return [MistakePattern.model_validate(item) for item in items]

    # ── Weak Topics ──────────────────────────────────────────────────────────
    async def upsert_weak_topic(self, weak_topic: WeakTopic) -> Dict[str, Any]:
        return await memory_repository.upsert_weak_topic(weak_topic.model_dump())

    async def get_weak_topics(self, user_id: str, resolved: bool = False, limit: int = 5) -> List[WeakTopic]:
        items = await memory_repository.get_weak_topics(user_id=user_id, resolved=resolved, limit=limit)
        return [WeakTopic.model_validate(item) for item in items]

    # ── Topic Mastery / Topic Memory ─────────────────────────────────────────
    async def upsert_topic_mastery(self, topic_mastery: TopicMastery) -> Dict[str, Any]:
        return await memory_repository.upsert_topic_mastery(topic_mastery.model_dump())

    async def get_topic_memory(self, user_id: str, topic: Optional[str] = None) -> List[TopicMastery]:
        items = await memory_repository.get_topic_mastery(user_id=user_id, topic=topic)
        return [TopicMastery.model_validate(item) for item in items]

    # ── Planner Context ──────────────────────────────────────────────────────
    async def get_planner_context(self, user_id: str) -> Optional[Dict[str, Any]]:
        return await planner_repository.get_planner_context(user_id)

    async def upsert_planner_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return await planner_repository.upsert_planner_context(context)

    # ── Sessions summaries & other supporting tables ───────────────────────
    async def upsert_session(self, session: Any) -> Dict[str, Any]:
        """Saves chat session summary metadata to Supabase."""
        # Map SessionMemory to conversation_summaries
        dump = {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "summary_text": session.summary_text,
            "structured_summary": {
                "planner_summary": session.planner_summary,
                "topics_covered": session.topics_covered,
                "questions_asked": session.questions_asked,
                "concepts_learned": session.concepts_learned,
                "confusions": session.confusions,
                "message_count": session.message_count,
                "avg_score": session.avg_score
            }
        }
        return await conversation_summary_repository.upsert_summary(dump)

    async def get_latest_summary(self, user_id: str, session_id: str) -> Optional[Dict[str, Any]]:
        return await conversation_summary_repository.get_latest_summary(user_id, session_id)

    async def save_learning_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        return await memory_repository.save_learning_event(event)

    # ── Frustration Logs Direct SQL mappings ─────────────────────────────────
    async def get_frustration_logs(self, user_id: str, topic: Optional[str] = None, min_level: str = "low", limit: int = 10) -> List[Dict[str, Any]]:
        query = self.supabase.table("frustration_logs").select("*").eq("user_id", user_id)
        if topic:
            query = query.eq("topic", topic)
        res = query.order("last_updated", desc=True).limit(limit).execute()
        return res.data or []

    async def detect_and_log_frustration(
        self, user_id: str, topic: str, confusion_signals=0, mistake_signals=0, consecutive_failures=0, difficulty_signals=0
    ) -> Dict[str, Any]:
        existing = self.supabase.table("frustration_logs").select("*").eq("user_id", user_id).eq("topic", topic).execute()
        score = 0.1 * confusion_signals + 0.15 * mistake_signals + 0.2 * consecutive_failures + 0.15 * difficulty_signals
        
        row = {
            "user_id": user_id,
            "topic": topic,
            "confusion_count": confusion_signals,
            "mistake_count": mistake_signals,
            "consecutive_failures": consecutive_failures,
            "difficulty_signals": difficulty_signals,
            "frustration_score": min(score, 1.0),
            "frustration_level": "high" if score >= memory_config.FRUSTRATION_HIGH_LEVEL else ("medium" if score >= memory_config.FRUSTRATION_MEDIUM_LEVEL else "low"),
            "last_updated": datetime.utcnow().isoformat()
        }
        
        if existing.data:
            rec_id = existing.data[0]["id"]
            # Accumulate
            row["confusion_count"] += existing.data[0]["confusion_count"]
            row["mistake_count"] += existing.data[0]["mistake_count"]
            row["consecutive_failures"] += existing.data[0]["consecutive_failures"]
            row["difficulty_signals"] += existing.data[0]["difficulty_signals"]
            # Recompute score
            new_score = min(0.1 * row["confusion_count"] + 0.15 * row["mistake_count"] + 0.2 * row["consecutive_failures"] + 0.15 * row["difficulty_signals"], 1.0)
            row["frustration_score"] = new_score
            row["frustration_level"] = "high" if new_score >= memory_config.FRUSTRATION_HIGH_LEVEL else ("medium" if new_score >= memory_config.FRUSTRATION_MEDIUM_LEVEL else "low")
            
            res = self.supabase.table("frustration_logs").update(row).eq("id", rec_id).execute()
        else:
            row["first_detected"] = datetime.utcnow().isoformat()
            res = self.supabase.table("frustration_logs").insert(row).execute()
            
        return res.data[0] if res.data else {}

    # ── Spaced Repetition Schedules mappings ────────────────────────────────
    async def upsert_repetition_schedule(self, schedule: Dict[str, Any]) -> Dict[str, Any]:
        user_id = schedule.get("user_id")
        topic = schedule.get("topic")
        
        # Serialize fields if needed
        data = dict(schedule)
        if "next_review_date" in data and hasattr(data["next_review_date"], "isoformat"):
            data["next_review_date"] = data["next_review_date"].isoformat()
        if "last_reviewed" in data and hasattr(data["last_reviewed"], "isoformat"):
            data["last_reviewed"] = data["last_reviewed"].isoformat()
        if "first_studied" in data and hasattr(data["first_studied"], "isoformat"):
            data["first_studied"] = data["first_studied"].isoformat()
            
        existing = self.supabase.table("repetition_schedule").select("*").eq("user_id", user_id).eq("topic", topic).execute()
        if existing.data:
            rec_id = existing.data[0]["schedule_id"]
            res = self.supabase.table("repetition_schedule").update(data).eq("schedule_id", rec_id).execute()
        else:
            res = self.supabase.table("repetition_schedule").insert(data).execute()
            
        return res.data[0] if res.data else {}

    # ── History entries logging ──────────────────────────────────────────────
    async def add_weakness_history_entry(self, user_id: str, topic: str, previous_score: float, new_score: float, reason: str) -> Dict[str, Any]:
        row = {
            "user_id": user_id,
            "topic": topic,
            "previous_score": previous_score,
            "new_score": new_score,
            "delta": new_score - previous_score,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        }
        res = self.supabase.table("weakness_history").insert(row).execute()
        return res.data[0] if res.data else {}

    async def advance_session_in_planner(
        self, user_id: str, completed_session: Any
    ) -> None:
        """
        Moves the completed session's planner_summary into
        PlannerContext.previous_session_summary for continuation support.
        """
        existing = await self.get_planner_context(user_id)
        if existing:
            existing["previous_session_summary"] = completed_session.planner_summary
            existing["previous_session_id"]      = completed_session.session_id
            await self.upsert_planner_context(existing)
        else:
            ctx = {
                "user_id": user_id,
                "previous_session_summary": completed_session.planner_summary,
                "previous_session_id": completed_session.session_id,
            }
            await self.upsert_planner_context(ctx)


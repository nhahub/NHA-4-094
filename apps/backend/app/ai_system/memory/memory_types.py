from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from app.schemas.personalization_schema import UserProfile, AccessibilityPreferences
from app.schemas.memory_schema import MemoryItem, WeakTopic, MistakePattern, TopicMastery, ConversationSummary, LearningEvent

class ChatMessage(BaseModel):
    id: Optional[str] = None
    session_id: str
    user_id: str
    role: str
    content: str
    topic: Optional[str] = None
    created_at: Optional[datetime] = None

class SessionMemory(BaseModel):
    session_id: str
    user_id: str
    summary_text: str = ""
    planner_summary: str = ""
    topics_covered: List[str] = Field(default_factory=list)
    questions_asked: List[str] = Field(default_factory=list)
    concepts_learned: List[str] = Field(default_factory=list)
    confusions: List[str] = Field(default_factory=list)
    message_count: int = 0
    avg_score: float = 0.0
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    is_summarized: bool = False

class FrustrationLog(BaseModel):
    log_id: Optional[str] = None
    user_id: str
    topic: str
    frustration_score: float = 0.0
    frustration_level: str = "low"
    frustration_triggers: List[str] = Field(default_factory=list)
    confusion_count: int = 0
    mistake_count: int = 0
    consecutive_failures: int = 0
    difficulty_signals: int = 0
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    first_detected: datetime = Field(default_factory=datetime.utcnow)
    resolved: bool = False
    resolved_at: Optional[datetime] = None

class RepetitionSchedule(BaseModel):
    schedule_id: Optional[str] = None
    user_id: str
    topic: str
    repetition_count: int = 0
    ease_factor: float = 2.5
    review_interval: int = 1
    next_review_date: datetime = Field(default_factory=datetime.utcnow)
    last_reviewed: Optional[datetime] = None
    first_studied: datetime = Field(default_factory=datetime.utcnow)
    retention_score: float = 0.0
    review_priority: float = 0.0
    quality_history: List[int] = Field(default_factory=list)
    total_reviews: int = 0
    is_overdue: bool = False
    is_due_today: bool = False

class MemoryContext(BaseModel):
    user_profile: Optional[UserProfile] = None
    recent_messages: List[ChatMessage] = Field(default_factory=list)
    relevant_past: List[MemoryItem] = Field(default_factory=list)
    topic_memories: List[TopicMastery] = Field(default_factory=list)
    weak_topics: List[WeakTopic] = Field(default_factory=list)
    recent_mistakes: List[MistakePattern] = Field(default_factory=list)
    session_summary: Optional[str] = None
    structured_summary: Dict[str, Any] = Field(default_factory=dict)
    frustration_logs: List[FrustrationLog] = Field(default_factory=list)
    repetition_schedule: List[RepetitionSchedule] = Field(default_factory=list)

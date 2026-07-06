from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class MemoryItemBase(BaseModel):
    user_id: str
    source_id: Optional[str] = None
    source_type: Optional[str] = None # 'document', 'page', 'global'
    session_id: Optional[str] = None
    memory_type: str # 'preference', 'learning_goal', 'weakness', 'strength', etc.
    content: str
    summary: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    importance: float = 0.5
    confidence: float = 0.5
    is_active: bool = True
    expires_at: Optional[datetime] = None

class MemoryItemCreate(MemoryItemBase):
    embedding: Optional[List[float]] = None

class MemoryItem(MemoryItemBase):
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ConversationSummaryBase(BaseModel):
    session_id: str
    user_id: str
    source_id: Optional[str] = None
    source_type: str = "document"
    summary_text: str
    structured_summary: Dict[str, Any] = Field(default_factory=dict)
    last_message_id: Optional[str] = None
    token_count: Optional[int] = None

class ConversationSummaryCreate(ConversationSummaryBase):
    pass

class ConversationSummary(ConversationSummaryBase):
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class LearningEventBase(BaseModel):
    user_id: str
    source_id: Optional[str] = None
    session_id: Optional[str] = None
    event_type: str
    topic: Optional[str] = None
    score: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class LearningEventCreate(LearningEventBase):
    pass

class LearningEvent(LearningEventBase):
    id: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TopicMasteryBase(BaseModel):
    user_id: str
    source_id: Optional[str] = None
    topic: str
    subject: Optional[str] = None
    mastery_score: float = 0.0
    times_studied: int = 0
    avg_quiz_score: float = 0.0
    latest_score: float = 0.0
    mastery_level: str = "learning"
    is_weak: bool = False
    last_studied: Optional[datetime] = None

class TopicMasteryCreate(TopicMasteryBase):
    pass

class TopicMastery(TopicMasteryBase):
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class WeakTopicBase(BaseModel):
    user_id: str
    source_id: Optional[str] = None
    topic: str
    weakness_score: float = 0.0
    failed_count: int = 0
    quiz_score: float = 0.0
    resolved: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)

class WeakTopicCreate(WeakTopicBase):
    pass

class WeakTopic(WeakTopicBase):
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class MistakePatternBase(BaseModel):
    user_id: str
    source_id: Optional[str] = None
    topic: str
    mistake_type: Optional[str] = None
    mistake_text: str
    correct_answer: Optional[str] = None
    frequency: int = 1
    severity: str = "medium"
    resolved: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MistakePatternCreate(MistakePatternBase):
    pass

class MistakePattern(MistakePatternBase):
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

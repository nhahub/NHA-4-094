import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from app.ai_system.memory.memory_retriever import MemoryRetriever, detect_continuation
from app.ai_system.memory.memory_types import ChatMessage
from app.schemas.personalization_schema import UserProfile
from app.schemas.memory_schema import MemoryItem, WeakTopic, MistakePattern, TopicMastery

def test_detect_continuation():
    assert detect_continuation("continue") is True
    assert detect_continuation("tell me more") is True
    assert detect_continuation("what is mitosis?") is False
    assert detect_continuation("كيف يمكنني الاستمرار؟") is True

@pytest.mark.asyncio
@patch("app.ai_system.memory.memory_store.MemoryStore.get_all_session_messages")
@patch("app.ai_system.memory.memory_store.MemoryStore.get_latest_summary")
@patch("app.ai_system.memory.memory_store.MemoryStore.get_user_profile")
@patch("app.ai_system.memory.memory_store.MemoryStore.semantic_search_memories")
@patch("app.ai_system.memory.memory_retriever.MemoryRetriever.get_weak_topics")
@patch("app.ai_system.memory.memory_retriever.MemoryRetriever.get_recent_mistakes")
@patch("app.ai_system.memory.memory_retriever.MemoryRetriever.get_topic_memories")
async def test_get_memory_context_tenant_scoping(
    mock_mastery, mock_mistakes, mock_weak, mock_semantic, mock_profile, mock_summary, mock_chats
):
    retriever = MemoryRetriever()
    
    # Mock return values
    mock_profile.return_value = UserProfile(user_id="user-123", learning_level="beginner")
    mock_chats.return_value = [
        ChatMessage(session_id="sess-1", user_id="user-123", role="user", content="hello", created_at=datetime.utcnow())
    ]
    mock_summary.return_value = {"summary_text": "A brief history."}
    mock_semantic.return_value = [
        MemoryItem(user_id="user-123", memory_type="preference", content="likes math", id="mem-1", created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    ]
    
    # Mock methods under test filtering by source_id
    wt_1 = WeakTopic(id="wt-1", user_id="user-123", topic="biology", source_id="doc-correct", created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    wt_2 = WeakTopic(id="wt-2", user_id="user-123", topic="history", source_id="doc-wrong", created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    mock_weak.return_value = [wt_1, wt_2]
    
    m_1 = MistakePattern(id="m-1", user_id="user-123", topic="biology", mistake_text="wrong biology", source_id="doc-correct", created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    mock_mistakes.return_value = [m_1]
    
    tm_1 = TopicMastery(id="tm-1", user_id="user-123", topic="biology", source_id="doc-correct", created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    mock_mastery.return_value = [tm_1]

    # Call with source_id scope "doc-correct"
    context = await retriever.get_memory_context(
        user_id="user-123",
        session_id="sess-1",
        source_id="doc-correct",
        source_type="document",
        user_query="tell me about biology"
    )
    
    assert context.user_profile.user_id == "user-123"
    assert len(context.recent_messages) == 1
    
    # Assert proper scoping and filtering
    assert len(context.weak_topics) == 1
    assert context.weak_topics[0].source_id == "doc-correct"
    assert len(context.recent_mistakes) == 1
    assert context.recent_mistakes[0].source_id == "doc-correct"
    assert len(context.topic_memories) == 1
    assert context.topic_memories[0].source_id == "doc-correct"

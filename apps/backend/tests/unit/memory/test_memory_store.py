import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from app.ai_system.memory.memory_store import MemoryStore
from app.schemas.personalization_schema import UserProfile
from app.schemas.memory_schema import MemoryItem, WeakTopic, MistakePattern, TopicMastery
from app.ai_system.memory.memory_types import ChatMessage

@pytest.fixture
def mock_supabase():
    with patch("app.db.repositories.memory_repository.supabase") as mock_db:
        yield mock_db

@pytest.mark.asyncio
@patch("app.db.repositories.learning_profile_repository.upsert_profile")
@patch("app.db.repositories.learning_profile_repository.get_profile")
async def test_upsert_get_profile(mock_get, mock_upsert):
    store = MemoryStore()
    
    mock_profile_data = {
        "user_id": "user-123",
        "academic_level": "beginner",
        "learning_level": "beginner",
        "preferred_language": "english",
        "preferred_style": "simple",
        "explanation_style": "simple",
        "explanation_depth": "medium",
        "default_difficulty": "auto",
        "confidence_score": 0.5,
        "total_sessions": 1,
        "total_messages": 2,
        "avg_quiz_score": 0.0
    }
    mock_get.return_value = mock_profile_data
    mock_upsert.return_value = mock_profile_data
    
    # Test Get
    profile = await store.get_user_profile("user-123")
    assert profile is not None
    assert profile.user_id == "user-123"
    assert profile.learning_level == "beginner"
    
    # Test Upsert
    updated_profile = UserProfile(user_id="user-123", learning_level="intermediate")
    mock_upsert.return_value = {**mock_profile_data, "learning_level": "intermediate", "academic_level": "intermediate"}
    
    res = await store.upsert_user_profile(updated_profile)
    assert res.learning_level == "intermediate"
    assert res.academic_level == "intermediate"

@pytest.mark.asyncio
@patch("app.db.repositories.chat_repository.save_message")
async def test_save_message(mock_save_msg):
    store = MemoryStore()
    mock_save_msg.return_value = {"id": "msg-999"}
    
    msg = ChatMessage(session_id="sess-1", user_id="user-1", role="user", content="Hello")
    res = await store.save_message(msg)
    assert res["id"] == "msg-999"
    mock_save_msg.assert_called_once()

@pytest.mark.asyncio
@patch("app.db.repositories.memory_repository.save_memory_item")
async def test_save_memory_item(mock_save_item):
    store = MemoryStore()
    mock_save_item.return_value = {"id": "mem-1"}
    
    item = MemoryItem(
        user_id="user-1",
        memory_type="preference",
        content="Prefers visual explanations",
        importance=0.8
    )
    res = await store.save_memory_item(item)
    assert res["id"] == "mem-1"
    mock_save_item.assert_called_once()

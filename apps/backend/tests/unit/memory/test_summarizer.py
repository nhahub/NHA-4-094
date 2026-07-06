import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from app.ai_system.memory.summarizer import Summarizer, _extract_questions, _extract_concepts_learned, _extract_confusions
from app.ai_system.memory.memory_types import ChatMessage, SessionMemory

def test_extract_questions():
    messages = [
        ChatMessage(session_id="sess-1", user_id="user-1", role="user", content="what is photosynthesis?"),
        ChatMessage(session_id="sess-1", user_id="user-1", role="assistant", content="It's a process in plants."),
        ChatMessage(session_id="sess-1", user_id="user-1", role="user", content="does it require sunlight?")
    ]
    questions = _extract_questions(messages)
    assert len(questions) == 2
    assert "what is photosynthesis?" in questions
    assert "does it require sunlight?" in questions

def test_extract_concepts_learned():
    messages = [
        ChatMessage(session_id="sess-1", user_id="user-1", role="user", content="tell me about biology"),
        ChatMessage(session_id="sess-1", user_id="user-1", role="assistant", content="We study cells.", topic="cells"),
        ChatMessage(session_id="sess-1", user_id="user-1", role="user", content="ah, I see cells make sense")
    ]
    concepts = _extract_concepts_learned(messages)
    assert "cells" in concepts

def test_extract_confusions():
    messages = [
        ChatMessage(session_id="sess-1", user_id="user-1", role="user", content="I still don't get the cellular division concept"),
    ]
    confusions = _extract_confusions(messages)
    assert len(confusions) == 1
    assert "don't get" in confusions[0]

@pytest.mark.asyncio
@patch("app.ai_system.memory.memory_store.MemoryStore.save_memory_item")
@patch("app.ai_system.memory.memory_store.MemoryStore.upsert_session")
@patch("app.ai_system.memory.memory_store.MemoryStore.advance_session_in_planner")
@patch("app.ai_system.memory.memory_store.MemoryStore.get_all_session_messages")
@patch("app.ai_system.memory.memory_store.MemoryStore.count_session_messages")
async def test_summarize_session_threshold(mock_count, mock_get, mock_advance, mock_upsert, mock_save_mem):
    summarizer = Summarizer()
    
    mock_count.return_value = 10 # above threshold
    mock_get.return_value = [
        ChatMessage(session_id="sess-1", user_id="user-1", role="user", content="explain photosynthesis", topic="photosynthesis"),
        ChatMessage(session_id="sess-1", user_id="user-1", role="assistant", content="it converts light to sugar", topic="photosynthesis")
    ]
    mock_upsert.return_value = {}
    mock_advance.return_value = None
    mock_save_mem.return_value = {}
    
    summary = await summarizer.summarize_session(user_id="user-1", session_id="sess-1", force=False)
    assert summary is not None
    assert "Session" in summary
    mock_upsert.assert_called_once()
    mock_advance.assert_called_once()

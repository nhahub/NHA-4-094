import pytest

from app.ai_system.memory.personalization import PersonalizationEngine
from app.ai_system.memory.memory_types import MemoryContext
from app.schemas.personalization_schema import UserProfile, AccessibilityPreferences
from app.schemas.memory_schema import WeakTopic

def test_dyslexia_friendly_accommodation():
    engine = PersonalizationEngine()
    
    # 1. No dyslexia friendlier profile
    p1 = UserProfile(user_id="u1", learning_level="beginner")
    inst1 = engine.get_accessibility_instruction(p1)
    assert inst1 == ""
    
    # 2. Dyslexia friendly profile
    p2 = UserProfile(
        user_id="u2",
        learning_level="beginner",
        accessibility=AccessibilityPreferences(dyslexia_friendly=True)
    )
    inst2 = engine.get_accessibility_instruction(p2)
    assert "DYSLEXIA SUPPORT" in inst2
    assert "short sentences" in inst2

def test_screen_reader_accommodation():
    engine = PersonalizationEngine()
    p = UserProfile(
        user_id="u3",
        accessibility=AccessibilityPreferences(screen_reader=True)
    )
    inst = engine.get_accessibility_instruction(p)
    assert "SCREEN READER" in inst
    assert "plain text only" in inst

def test_difficulty_adaptation_on_weak_topic():
    engine = PersonalizationEngine()
    
    p = UserProfile(user_id="u1", learning_level="intermediate")
    
    # Topic is NOT weak
    weak_list = [WeakTopic(user_id="u1", topic="history", weakness_score=0.9, failed_count=2)]
    inst1 = engine.get_difficulty_instruction(p, topic="biology", weak_topics=weak_list)
    assert "DIFFICULTY: Intermediate" in inst1
    assert "Difficulty reduced" not in inst1
    
    # Topic IS weak
    inst2 = engine.get_difficulty_instruction(p, topic="history", weak_topics=weak_list)
    assert "DIFFICULTY: Beginner" in inst2 # downgraded from intermediate
    assert "Difficulty reduced" in inst2

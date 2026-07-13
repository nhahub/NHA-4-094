from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import List, Dict, Any, Optional
from datetime import datetime

class AccessibilityPreferences(BaseModel):
    dyslexia_friendly: bool = False
    screen_reader: bool = False
    large_text: bool = False
    high_contrast: bool = False
    extended_time: bool = False
    simplified_language: bool = False
    custom_notes: str = ""

class UserProfile(BaseModel):
    user_id: str
    academic_level: str = "beginner"
    learning_level: str = "beginner"
    learning_goals: List[str] = Field(default_factory=list)
    study_goals: List[str] = Field(default_factory=list)
    preferred_language: str = "english"
    preferred_style: str = "balanced"
    explanation_style: str = "simple"
    explanation_depth: str = "medium"
    default_difficulty: str = "auto"
    strengths: List[str] = Field(default_factory=list)
    strong_subjects: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    weak_subjects: List[str] = Field(default_factory=list)
    accessibility_prefs: AccessibilityPreferences = Field(default_factory=AccessibilityPreferences)
    accessibility: AccessibilityPreferences = Field(default_factory=AccessibilityPreferences)
    confidence_score: float = 0.5
    total_sessions: int = 0
    total_messages: int = 0
    avg_quiz_score: float = 0.0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @model_validator(mode='before')
    @classmethod
    def sync_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Sync learning_level <-> academic_level
            if "learning_level" in data and "academic_level" not in data:
                data["academic_level"] = data["learning_level"]
            elif "academic_level" in data and "learning_level" not in data:
                data["learning_level"] = data["academic_level"]
            
            # Sync study_goals <-> learning_goals
            if "study_goals" in data and "learning_goals" not in data:
                data["learning_goals"] = data["study_goals"]
            elif "learning_goals" in data and "study_goals" not in data:
                data["study_goals"] = data["learning_goals"]

            # Sync explanation_style <-> preferred_style
            if "explanation_style" in data and "preferred_style" not in data:
                data["preferred_style"] = data["explanation_style"]
            elif "preferred_style" in data and "explanation_style" not in data:
                data["explanation_style"] = data["preferred_style"]

            # Sync strengths <-> strong_subjects
            if "strong_subjects" in data and "strengths" not in data:
                data["strengths"] = data["strong_subjects"]
            elif "strengths" in data and "strong_subjects" not in data:
                data["strong_subjects"] = data["strengths"]

            # Sync weaknesses <-> weak_subjects
            if "weak_subjects" in data and "weaknesses" not in data:
                data["weaknesses"] = data["weak_subjects"]
            elif "weaknesses" in data and "weak_subjects" not in data:
                data["weak_subjects"] = data["weaknesses"]

            # Sync accessibility <-> accessibility_prefs
            if "accessibility" in data and "accessibility_prefs" not in data:
                data["accessibility_prefs"] = data["accessibility"]
            elif "accessibility_prefs" in data and "accessibility" not in data:
                data["accessibility"] = data["accessibility_prefs"]
        return data

    model_config = ConfigDict(from_attributes=True)

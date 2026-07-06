from typing import Dict, Tuple

# ── Embedding ────────────────────────────────────────────────────────────────
EMBEDDING_DIM: int = 1024
EMBEDDING_MODEL: str = "@cf/baai/bge-m3"

# ── Importance Scoring ───────────────────────────────────────────────────────
IMPORTANCE_AI_RESPONSE:   float = 0.7
IMPORTANCE_MISTAKE:       float = 0.9
IMPORTANCE_QUIZ_RESULT:   float = 0.85
IMPORTANCE_USER_QUESTION: float = 0.75
IMPORTANCE_DEFAULT:       float = 0.5

# ── Mastery Thresholds ───────────────────────────────────────────────────────
MASTERY_THRESHOLDS: Dict[str, Tuple[float, float]] = {
    "learning":   (0.0,  0.4),
    "practicing": (0.4,  0.7),
    "mastered":   (0.7,  1.01),
}

# ── Retrieval ────────────────────────────────────────────────────────────────
MAX_RECENT_MESSAGES:  int = 20
TOP_K_CHATS:          int = 5
SIMILARITY_THRESHOLD: float = 0.25

# ── Ranking Weights ──────────────────────────────────────────────────────────
WEIGHT_SIMILARITY: float = 0.40
WEIGHT_RECENCY:    float = 0.30
WEIGHT_IMPORTANCE: float = 0.30
RECENCY_DECAY_RATE: float = 0.1   # 1.0 at t=0, ~0.5 at 10 days

# ── Summarization ────────────────────────────────────────────────────────────
SUMMARIZE_AFTER_N_MESSAGES:   int = 6
SUMMARY_MAX_INPUT_CHARS:      int = 4000
SUMMARY_MAX_OUTPUT_SENTENCES: int = 5

# ── Token Budgets (approximate) ──────────────────────────────────────────────
TOKEN_BUDGET_TOTAL:         int = 2000
TOKEN_BUDGET_PROFILE:       int = 200
TOKEN_BUDGET_RECENT_CHAT:   int = 600
TOKEN_BUDGET_PAST_CONTEXT:  int = 300
TOKEN_BUDGET_MISTAKES:      int = 200
TOKEN_BUDGET_WEAK_TOPICS:   int = 200

# ── Difficulty Instructions ──────────────────────────────────────────────────
DIFFICULTY_INSTRUCTIONS: Dict[str, str] = {
    "beginner": (
        "DIFFICULTY: Beginner.\n"
        "• Use plain, short sentences.\n"
        "• Define every technical term on first use.\n"
        "• Use analogies from daily life.\n"
        "• 1 concept per explanation.\n"
        "• Check understanding with simple questions."
    ),
    "intermediate": (
        "DIFFICULTY: Intermediate.\n"
        "• Use standard technical vocabulary.\n"
        "• 2-3 concepts per explanation.\n"
        "• Provide examples from related domains.\n"
        "• Ask linking questions."
    ),
    "advanced": (
        "DIFFICULTY: Advanced.\n"
        "• Use full technical depth.\n"
        "• Cross-link multiple concepts.\n"
        "• Cite edge cases and exceptions.\n"
        "• Challenge with complex problem-solving."
    ),
}

# ── Style Instructions ───────────────────────────────────────────────────────
STYLE_INSTRUCTIONS: Dict[str, str] = {
    "simple":         "Use the simplest possible explanation. Short sentences. One idea at a time.",
    "detailed":       "Provide thorough, comprehensive explanations with full context.",
    "visual":         "Use ASCII diagrams, tables, and structured lists to explain concepts visually.",
    "example-based":  "Lead with examples. Explain concepts through concrete cases.",
    "socratic":       "Guide the student through questions. Do not give direct answers — help them discover.",
}

# ── Quiz Parameters ──────────────────────────────────────────────────────────
QUIZ_PARAMS: Dict[str, Dict] = {
    "beginner": {
        "num_questions":    5,
        "question_types":   ["multiple_choice", "true_false"],
        "hints":            True,
        "max_retries":      2,
    },
    "intermediate": {
        "num_questions":    8,
        "question_types":   ["multiple_choice", "fill_blank", "short_answer"],
        "hints":            True,
        "max_retries":      1,
    },
    "advanced": {
        "num_questions":    10,
        "question_types":   ["short_answer", "essay", "problem_solving"],
        "hints":            False,
        "max_retries":      0,
    },
}

# ── Spaced Repetition (SM-2 derived) ─────────────────────────────────────────
REPETITION_DEFAULT_INTERVAL_DAYS: int = 1
REPETITION_EASY_BONUS:            float = 1.5
REPETITION_HARD_PENALTY:          float = 0.5
REPETITION_MAX_INTERVAL_DAYS:     int = 365
REPETITION_MIN_INTERVAL_DAYS:     int = 1
REPETITION_QUALITY_PASS_THRESHOLD: int = 3  # 0-5 scale

# ── Frustration Detection ────────────────────────────────────────────────────
FRUSTRATION_CONFUSION_THRESHOLD:    int = 3   # same confusion >3x → frustration
FRUSTRATION_MISTAKE_THRESHOLD:      int = 5   # same mistake >5x → frustration
FRUSTRATION_DECAY_DAYS:             int = 14  # frustration resets after 14d no incidents
FRUSTRATION_HIGH_LEVEL:             float = 0.7
FRUSTRATION_MEDIUM_LEVEL:           float = 0.4

# ── Persona Evolution ────────────────────────────────────────────────────────
PERSONA_EVOLVE_MASTERY_THRESHOLD:  float = 0.75  # avg mastery to level up
PERSONA_EVOLVE_MIN_SESSIONS:       int = 5        # minimum sessions before evolution
PERSONA_EVOLVE_MAX_MISTAKE_RATE:   float = 0.2    # max mistake rate for level up
PERSONA_EVOLVE_CONSISTENCY_GAP:    int = 7        # max days between study sessions

# ── Memory Aging ─────────────────────────────────────────────────────────────
MEMORY_AGING_DAYS_THRESHOLD:       int = 14    # after this many days, importance decays
MEMORY_AGING_DECAY_FACTOR:         float = 0.85 # multiply importance by this
MEMORY_AGING_MIN_IMPORTANCE:       float = 0.15 # floor for decayed importance

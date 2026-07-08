from app.schemas.ai_schema import TaskType, ExecutionMode

# Task Types (string constants mapped to TaskType Enum values)
TASK_CHAT_ANSWER = TaskType.CHAT_ANSWER.value
TASK_EXPLAIN = TaskType.EXPLAIN.value
TASK_SUMMARY = TaskType.SUMMARY.value
TASK_QUIZ = TaskType.QUIZ.value
TASK_ANSWER_TABLE = TaskType.ANSWER_TABLE.value
TASK_KEY_POINTS = TaskType.KEY_POINTS.value
TASK_COMPARISON_TABLE = TaskType.COMPARISON_TABLE.value
TASK_FLASHCARDS = TaskType.FLASHCARDS.value
TASK_ANSWER_EVALUATION = TaskType.ANSWER_EVALUATION.value
TASK_CLARIFICATION = TaskType.CLARIFICATION.value
TASK_OUT_OF_SCOPE = TaskType.OUT_OF_SCOPE.value
TASK_UNKNOWN = TaskType.UNKNOWN.value

SUPPORTED_TASK_TYPES = {
    TASK_CHAT_ANSWER,
    TASK_EXPLAIN,
    TASK_SUMMARY,
    TASK_QUIZ,
    TASK_ANSWER_TABLE,
    TASK_KEY_POINTS,
    TASK_COMPARISON_TABLE,
    TASK_FLASHCARDS,
    TASK_ANSWER_EVALUATION,
    TASK_CLARIFICATION,
    TASK_OUT_OF_SCOPE,
    TASK_UNKNOWN
}

# Execution Modes (string constants mapped to ExecutionMode Enum values)
MODE_SINGLE = ExecutionMode.SINGLE.value
MODE_PARALLEL = ExecutionMode.PARALLEL.value
MODE_SEQUENTIAL = ExecutionMode.SEQUENTIAL.value
MODE_HYBRID = ExecutionMode.HYBRID.value

SUPPORTED_EXECUTION_MODES = {
    MODE_SINGLE,
    MODE_PARALLEL,
    MODE_SEQUENTIAL,
    MODE_HYBRID
}

# Golden Rule Default No Answer response
NO_ANSWER_FALLBACK = "لم أجد إجابة واضحة في الملف المرفوع."

# Clarification defaults
CLARIFICATION_QUESTION_AR = "كيف يمكنني مساعدتك في محتوى هذا الملف؟"
CLARIFICATION_QUESTION_EN = "How can I help you with this document's content?"

# Keyword map for intent classification
KEYWORDS = {
    "ar": {
        TASK_SUMMARY: ["لخص", "ملخص", "تلخيص", "اختصر", "اختصار", "موجز"],
        TASK_QUIZ: ["اختبار", "كويز", "امتحان", "اسئلة", "أسئلة", "كوز"],
        TASK_ANSWER_TABLE: ["جدول اجابات", "جدول إجابات", "جدول الاجابات", "جدول الإجابات", "اجوبة", "أجوبة"],
        TASK_EXPLAIN: ["اشرح", "شرح", "وضح", "توضيح", "فسر", "تفسير"],
        TASK_KEY_POINTS: ["النقاط الرئيسية", "نقاط رئيسية", "أهم النقاط", "اهم النقاط", "افكار رئيسية"],
        TASK_COMPARISON_TABLE: ["جدول مقارنة", "مقارنة", "قارن", "جدول مقارنه"],
        TASK_FLASHCARDS: ["بطاقات استذكار", "فلاش كارد", "فلاش كاردز", "بطاقات تعليمية"],
        TASK_ANSWER_EVALUATION: ["تقييم اجابة", "تقييم إجابة", "قيم اجابتي", "تصحيح اجابتي", "صحح لي"]
    },
    "en": {
        TASK_SUMMARY: ["summarize", "summary", "brief", "digest", "shorten"],
        TASK_QUIZ: ["quiz", "test", "exam", "question", "quizzes"],
        TASK_ANSWER_TABLE: ["answer table", "answers table", "solution table", "answer sheet"],
        TASK_EXPLAIN: ["explain", "explanation", "clarify", "describe"],
        TASK_KEY_POINTS: ["key points", "bullet points", "main ideas", "takeaways"],
        TASK_COMPARISON_TABLE: ["comparison table", "compare", "contrast"],
        TASK_FLASHCARDS: ["flashcard", "flashcards", "study cards"],
        TASK_ANSWER_EVALUATION: ["evaluate answer", "grade my answer", "check my answer", "correct my answer"]
    }
}

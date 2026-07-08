import re
import uuid
from typing import List, Dict, Any
from app.schemas.ai_schema import (
    PDFChatRequest,
    DAGPlan,
    Task,
    TaskType,
    ExecutionMode,
    ModelTier,
    RetrievalStrategy,
    OutputFormat,
    FallbackPolicy,
    VerificationPolicy
)
from app.ai_system.orchestrator.constants import (
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
    TASK_UNKNOWN,
    MODE_SINGLE,
    MODE_PARALLEL,
    MODE_SEQUENTIAL,
    MODE_HYBRID,
    KEYWORDS,
    CLARIFICATION_QUESTION_AR,
    CLARIFICATION_QUESTION_EN
)
from app.ai_system.orchestrator.errors import PlanningError, CircularDependencyError

class TaskPlanner:
    """
    Planner module that parses user inputs, detects intents in English and Arabic,
    resolves dependencies, validates DAG paths (preventing cycles), and outputs a DAGPlan.
    """

    def __init__(self) -> None:
        # Setup regex splitting for compound requests using connectors
        self.split_regex = re.compile(
            r'\s+(?:and|then|ثم)\s+|[\,،\+]\s*|(?:\s+و\s+)',
            re.IGNORECASE
        )
        
        # Simple greetings to trigger clarification for vague queries
        self.greetings = {
            "hi", "hello", "hey", "hola", "مرحبا", "اهلا", "أهلاً", "سلام", "صباح الخير", "مساء الخير"
        }

    def plan(self, request: Any) -> DAGPlan:
        """
        Generates a DAGPlan based on the request (PDFChatRequest, SummaryRequest, or QuizRequest).
        """
        plan_id = f"plan-{uuid.uuid4()}"
        fallback_policy = FallbackPolicy()
        verification_policy = VerificationPolicy()

        # Handle Shortcut Requests
        if hasattr(request, "summary_style"):  # SummaryRequest shortcut
            metadata = {}
            if getattr(request, "summary_style", None):
                metadata["summary_style"] = request.summary_style
            
            task = Task(
                task_id="task-1",
                type=TaskType.SUMMARY,
                query="Generate a summary of the document",
                retrieval_required=True,
                retrieval_strategy=RetrievalStrategy.HYBRID,
                output_format=OutputFormat.MARKDOWN,
                model_tier=ModelTier.LIGHTWEIGHT,
                verification_required=True,
                metadata=metadata
            )
            return DAGPlan(
                plan_id=plan_id,
                primary_intent=TaskType.SUMMARY,
                execution_mode=ExecutionMode.SINGLE,
                confidence=1.0,
                needs_clarification=False,
                tasks=[task],
                fallback_policy=fallback_policy,
                verification_policy=verification_policy
            )

        if hasattr(request, "difficulty"):  # QuizRequest shortcut
            metadata = {
                "difficulty": getattr(request, "difficulty", "medium"),
                "number_of_questions": getattr(request, "number_of_questions", 5),
                "question_type": getattr(request, "question_type", "multiple_choice")
            }
            task = Task(
                task_id="task-1",
                type=TaskType.QUIZ,
                query="Generate a quiz from the document",
                retrieval_required=True,
                retrieval_strategy=RetrievalStrategy.HYBRID,
                output_format=OutputFormat.QUIZ_JSON,
                model_tier=ModelTier.LIGHTWEIGHT,
                verification_required=True,
                metadata=metadata
            )
            return DAGPlan(
                plan_id=plan_id,
                primary_intent=TaskType.QUIZ,
                execution_mode=ExecutionMode.SINGLE,
                confidence=1.0,
                needs_clarification=False,
                tasks=[task],
                fallback_policy=fallback_policy,
                verification_policy=verification_policy
            )

        # Handle Chat Request
        if not isinstance(request, PDFChatRequest):
            raise PlanningError("Invalid request object type passed to TaskPlanner.")

        message = request.message.strip()
        lang = request.language if request.language in ["ar", "en"] else "ar"

        # Check for empty or vague requests / greetings
        cleaned_msg = re.sub(r'[^\w\s]', '', message).lower().strip()
        if len(message) < 3 or cleaned_msg in self.greetings:
            question = CLARIFICATION_QUESTION_AR if lang == "ar" else CLARIFICATION_QUESTION_EN
            return DAGPlan(
                plan_id=plan_id,
                primary_intent=TaskType.CLARIFICATION,
                execution_mode=ExecutionMode.SINGLE,
                confidence=0.5,
                needs_clarification=True,
                clarification_question=question,
                tasks=[],
                fallback_policy=fallback_policy,
                verification_policy=verification_policy
            )

        # Detect intents
        detected_intents = self._detect_intents(message)

        # If no explicit intent keywords are matched, default to standard chat grounding
        if not detected_intents:
            task = Task(
                task_id="task-1",
                type=TaskType.CHAT_ANSWER,
                query=message,
                retrieval_required=True,
                retrieval_strategy=RetrievalStrategy.HYBRID,
                output_format=OutputFormat.MARKDOWN,
                model_tier=ModelTier.LIGHTWEIGHT,
                verification_required=True,
                metadata={}
            )
            return DAGPlan(
                plan_id=plan_id,
                primary_intent=TaskType.CHAT_ANSWER,
                execution_mode=ExecutionMode.SINGLE,
                confidence=0.9,
                needs_clarification=False,
                tasks=[task],
                fallback_policy=fallback_policy,
                verification_policy=verification_policy
            )

        # Handle single intent
        if len(detected_intents) == 1:
            intent = list(detected_intents)[0]
            task_type_enum = TaskType(intent)
            task = Task(
                task_id="task-1",
                type=task_type_enum,
                query=message,
                retrieval_required=self._is_retrieval_required(task_type_enum),
                retrieval_strategy=RetrievalStrategy.HYBRID,
                output_format=self._get_default_output_format(task_type_enum),
                model_tier=self._get_default_model_tier(task_type_enum),
                verification_required=True,
                metadata={}
            )
            return DAGPlan(
                plan_id=plan_id,
                primary_intent=task_type_enum,
                execution_mode=ExecutionMode.SINGLE,
                confidence=0.95,
                needs_clarification=False,
                tasks=[task],
                fallback_policy=fallback_policy,
                verification_policy=verification_policy
            )

        # Handle compound intent (multiple intents detected)
        parts = [p.strip() for p in self.split_regex.split(message) if p.strip()]
        tasks: List[Task] = []
        task_id_counter = 1

        for intent in detected_intents:
            task_query = message  # Default fallback
            
            # Search split parts for the one containing the intent keywords
            for part in parts:
                part_intents = self._detect_intents(part)
                if intent in part_intents:
                    task_query = part
                    break
            
            task_type_enum = TaskType(intent)
            tasks.append(
                Task(
                    task_id=f"task-{task_id_counter}",
                    type=task_type_enum,
                    query=task_query,
                    retrieval_required=self._is_retrieval_required(task_type_enum),
                    retrieval_strategy=RetrievalStrategy.HYBRID,
                    output_format=self._get_default_output_format(task_type_enum),
                    model_tier=self._get_default_model_tier(task_type_enum),
                    verification_required=True,
                    metadata={}
                )
            )
            task_id_counter += 1

        # Resolve Dependencies automatically
        quiz_tasks = [t for t in tasks if t.type == TaskType.QUIZ]
        ans_table_tasks = [t for t in tasks if t.type == TaskType.ANSWER_TABLE]
        if ans_table_tasks and quiz_tasks:
            for at in ans_table_tasks:
                for qt in quiz_tasks:
                    if qt.task_id not in at.depends_on:
                        at.depends_on.append(qt.task_id)

        chat_answer_tasks = [t for t in tasks if t.type == TaskType.CHAT_ANSWER]
        eval_tasks = [t for t in tasks if t.type == TaskType.ANSWER_EVALUATION]
        if eval_tasks and chat_answer_tasks:
            for et in eval_tasks:
                for ct in chat_answer_tasks:
                    if ct.task_id not in et.depends_on:
                        et.depends_on.append(ct.task_id)

        # Topological Sort & Circle Detection
        try:
            tasks = self._topological_sort(tasks)
        except CircularDependencyError as cde:
            raise cde
        except Exception as e:
            raise PlanningError(f"Dependency resolution error: {str(e)}")

        # Determine execution mode based on dependencies
        has_dependencies = any(len(t.depends_on) > 0 for t in tasks)
        mode = ExecutionMode.HYBRID if has_dependencies else ExecutionMode.PARALLEL

        # Select primary intent from sorted tasks
        primary_intent = tasks[0].type if tasks else TaskType.UNKNOWN

        return DAGPlan(
            plan_id=plan_id,
            primary_intent=primary_intent,
            execution_mode=mode,
            confidence=0.8,
            needs_clarification=False,
            tasks=tasks,
            fallback_policy=fallback_policy,
            verification_policy=verification_policy
        )

    def _detect_intents(self, text: str) -> set:
        """Helper to scan a string and return all matching intent types."""
        detected = set()
        text_lower = text.lower()
        
        for lang in ["ar", "en"]:
            for intent, keywords in KEYWORDS[lang].items():
                for keyword in keywords:
                    if keyword.lower() in text_lower:
                        detected.add(intent)
                        break
        return detected

    def _is_retrieval_required(self, task_type: TaskType) -> bool:
        if task_type in [TaskType.CLARIFICATION, TaskType.OUT_OF_SCOPE, TaskType.UNKNOWN]:
            return False
        return True

    def _get_default_output_format(self, task_type: TaskType) -> OutputFormat:
        if task_type == TaskType.QUIZ:
            return OutputFormat.QUIZ_JSON
        elif task_type == TaskType.FLASHCARDS:
            return OutputFormat.FLASHCARDS_JSON
        elif task_type == TaskType.COMPARISON_TABLE:
            return OutputFormat.COMPARISON_TABLE_MARKDOWN
        elif task_type == TaskType.ANSWER_TABLE:
            return OutputFormat.ANSWER_TABLE_MARKDOWN
        elif task_type == TaskType.ANSWER_EVALUATION:
            return OutputFormat.ANSWER_EVALUATION_JSON
        return OutputFormat.MARKDOWN

    def _get_default_model_tier(self, task_type: TaskType) -> ModelTier:
        if task_type in [TaskType.EXPLAIN, TaskType.COMPARISON_TABLE, TaskType.ANSWER_EVALUATION]:
            return ModelTier.REASONING
        return ModelTier.LIGHTWEIGHT

    def _topological_sort(self, tasks: List[Task]) -> List[Task]:
        """Performs topological sorting and validates that no dependency cycles exist."""
        adj = {t.task_id: [] for t in tasks}
        task_map = {t.task_id: t for t in tasks}
        in_degree = {t.task_id: 0 for t in tasks}
        
        for t in tasks:
            for dep in t.depends_on:
                if dep in adj:
                    adj[dep].append(t.task_id)
                    in_degree[t.task_id] += 1
        
        from collections import deque
        queue = deque([tid for tid, deg in in_degree.items() if deg == 0])
        sorted_tids = []
        
        while queue:
            u = queue.popleft()
            sorted_tids.append(u)
            for v in adj[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)
                    
        if len(sorted_tids) != len(tasks):
            raise CircularDependencyError("Circular dependencies detected in the execution plan.")
            
        return [task_map[tid] for tid in sorted_tids]

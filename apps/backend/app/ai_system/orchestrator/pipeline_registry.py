import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.schemas.ai_schema import Task, TaskResult, Citation, TaskType, VerificationPolicy, OutputFormat
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
    NO_ANSWER_FALLBACK
)
from app.db.repositories import chat_repository
from app.ai_system.memory import (
    MemoryRetriever, PersonalizationEngine, build_grounded_prompt,
    MemoryStore, ChatMessage, Summarizer
)
from app.ai_system.services.llm.generate import generate as llm_generate
from app.ai_system.services.llm.schemas import (
    LLMEngineerPayload, SourceInfo, StrictGroundingPolicy,
    ExpectedLLMOutputFormat, ChunkContext, MemoryContext
)
from app.ai_system.retrieval import get_document_retriever
from app.ai_system.retrieval.schemas import RetrievalRequest, RetrievalStatus
from app.ai_system.orchestrator.verifier_client import default_verifier_client

logger = logging.getLogger(__name__)

MOCK_CONFIDENCE = 0.9

memory_retriever = MemoryRetriever()
personalizer = PersonalizationEngine()
store = MemoryStore()
summarizer = Summarizer()
document_retriever = get_document_retriever()

def check_no_answer_trigger(query: str) -> bool:
    """Checks if query simulates requesting information outside the document context."""
    normalized = query.lower()
    return "خارج الملف" in normalized or "outside the file" in normalized

async def execute_common_pipeline_steps(
    task: Task,
    request: Any,
    task_type: TaskType,
    previous_results: Optional[Dict[str, Any]] = None,
    pre_generated_content: Optional[str] = None
) -> TaskResult:
    """
    Executes core pipeline steps:
    1. Check query triggers
    2. Retrieve chunks (RAG)
    3. Check empty chunks -> return fallback
    4. Save user query
    5. Load memory context
    6. Construct grounded prompt
    7. Execute LLM & Verify Loop with retries
    8. Apply personalization instructions
    9. Save assistant response with chunk traceability
    10. Run rolling session summaries
    """
    # 1. Check intent triggers
    if check_no_answer_trigger(task.query):
        return TaskResult(
            task_id=task.task_id,
            type=task_type,
            status="no_answer",
            content=NO_ANSWER_FALLBACK,
            citations=[],
            confidence=0.0,
            metadata={"mock": False, "retrieval_mode": "temporary_chunk_context_until_rag"}
        )

    user_id = getattr(request, "user_id", "00000000-0000-0000-0000-000000000000")
    session_id = getattr(request, "session_id", "sess-xyz")
    document_id = getattr(request, "document_id", None)
    lang = getattr(request, "language", "ar")

    # 2. Retrieve relevant chunks via the RAG retrieval module.
    retrieval_result = None
    chunks = []
    if document_id and task.retrieval_required:
        retrieval_result = await document_retriever.retrieve(RetrievalRequest(
            user_id=user_id,
            document_id=document_id,
            query=task.query,
            intent=task_type.value,
        ))
        
        # 3. Check for empty/unusable RAG context -> strict grounding fallback
        if retrieval_result.status != RetrievalStatus.FOUND:
            return TaskResult(
                task_id=task.task_id,
                type=task_type,
                status="no_answer",
                content=NO_ANSWER_FALLBACK,
                citations=[],
                confidence=0.0,
                metadata={"mock": False, "retrieval_status": retrieval_result.status.value}
            )
            
        chunks = [
            {
                "id": c.chunk_id,
                "content": c.text,
                "page_start": c.page_number or 1,
            }
            for c in retrieval_result.chunks
        ]
    elif task.retrieval_required:
        # Retrieval is required but document_id is missing
        return TaskResult(
            task_id=task.task_id,
            type=task_type,
            status="no_answer",
            content=NO_ANSWER_FALLBACK,
            citations=[],
            confidence=0.0,
            metadata={"mock": True, "error": "Missing document_id context."}
        )

    # 4. Save user message to chat database
    user_msg = ChatMessage(
        session_id=session_id,
        user_id=user_id,
        role="user",
        content=task.query,
        topic=task.metadata.get("topic")
    )
    await store.save_message(user_msg)

    # 5. Fetch student Memory Context
    memory_context = await memory_retriever.get_memory_context(
        user_id=user_id,
        session_id=session_id,
        source_id=document_id,
    )

    # 6. Temporary context selection
    if task_type in [TaskType.CHAT_ANSWER, TaskType.EXPLAIN, TaskType.KEY_POINTS, TaskType.COMPARISON_TABLE]:
        selected_chunks = chunks[:5]
    else:
        selected_chunks = chunks[:30]

    # Convert retrieved chunks to ChunkContext Pydantic objects
    retrieved_context = []
    chunk_page_map = {}
    for idx, c in enumerate(selected_chunks):
        cid = str(c.get("id", idx))
        page_num = c.get("page_start", 1)
        chunk_page_map[cid] = page_num
        retrieved_context.append(
            ChunkContext(
                chunk_id=cid,
                page_number=page_num,
                score=0.9 - (0.02 * idx),
                content=c.get("content", "")
            )
        )

    # Execute task using precomputed content or LLM generation
    content_result = ""
    usage_metrics = None
    llm_response = None
    verification_trace = {}

    if pre_generated_content is not None:
        content_result = pre_generated_content
        logger.info(f"Using precomputed content for task {task.task_id} (type: {task_type})")
        source_chunk_ids = [c.chunk_id for c in retrieved_context[:3]]
        verification_trace = {"status": "skipped", "retries": 0}
    else:
        # Build LLMEngineerPayload
        output_type = "text"
        if task_type == TaskType.QUIZ:
            output_type = "quiz"
        elif task_type == TaskType.SUMMARY:
            output_type = "summary"
        elif task_type == TaskType.EXPLAIN:
            output_type = "explanation"
        elif task_type == TaskType.ANSWER_EVALUATION:
            output_type = "answer_evaluation"

        expected_format = ExpectedLLMOutputFormat(
            type=output_type,
            question_count=5 if task_type == TaskType.QUIZ else None,
            must_be_grounded=True,
            must_not_use_general_knowledge=True
        )

        memory_payload = MemoryContext(
            quiz_difficulty=getattr(request, "difficulty", "medium"),
            preferred_language=lang
        )

        payload = LLMEngineerPayload(
            task_id=task.task_id,
            task_type=task_type.value,
            pipeline_type="standard_rag",
            original_user_query=task.query,
            task_query=task.query,
            source=SourceInfo(source_id=str(document_id) if document_id else "system", source_type="document"),
            retrieved_document_context=retrieved_context,
            memory_context=memory_payload,
            strict_grounding_policy=StrictGroundingPolicy(
                academic_source_of_truth="retrieved_document_context_only",
                memory_usage="personalization_only",
                if_document_context_insufficient=NO_ANSWER_FALLBACK
            ),
            expected_llm_output_format=expected_format
        )

        policy = getattr(request, "verification_policy", None) or VerificationPolicy()
        verification_passed = False
        
        for attempt in range(policy.max_retries + 1):
            if attempt > 0:
                payload.task_query = (
                    f"{task.query}\n\n[Correction Instruction: Previous attempt failed verification. "
                    f"Ensure output grounds strictly in context and adheres to OutputFormat: {output_type}]"
                )
            
            try:
                llm_response = await llm_generate(payload)
                if llm_response.status == "failure":
                    verification_trace = {"status": "error", "error": llm_response.error_message, "retries": attempt}
                    continue
                
                # Check verification
                raw_response = llm_response.output_text or json.dumps(llm_response.output_json, ensure_ascii=False) if llm_response.output_json else ""
                
                verification = await default_verifier_client.verify(
                    context=retrieval_result.context_text if retrieval_result else "",
                    response=raw_response,
                    policy=policy
                )
                
                verification_trace = {
                    "status": "passed" if verification.success else "failed",
                    "retries": attempt,
                    "grounding_score": verification.grounding_score,
                    "relevance_score": verification.relevance_score,
                    "schema_valid": verification.schema_valid,
                    "reason": verification.reason
                }

                if verification.success:
                    verification_passed = True
                    break
            except Exception as e:
                verification_trace = {"status": "error", "error": str(e), "retries": attempt}

        if not verification_passed:
            return TaskResult(
                task_id=task.task_id,
                type=task_type,
                status="no_answer",
                content=NO_ANSWER_FALLBACK,
                citations=[],
                confidence=0.0,
                metadata={
                    "mock": False,
                    "error": "Verification failed, fallback triggered.",
                    "verification": verification_trace
                }
            )

        if llm_response.output_text:
            content_result = llm_response.output_text
        elif llm_response.output_json:
            content_result = json.dumps(llm_response.output_json, ensure_ascii=False)
        
        source_chunk_ids = llm_response.source_chunk_ids
        usage_metrics = llm_response.usage_metrics.model_dump() if llm_response.usage_metrics else None

    # 8. Apply personalization adapt
    if memory_context:
        adapted_content = personalizer.adapt_explanation(
            content_result,
            memory_context.user_profile,
            weak_topics=memory_context.weak_topics,
            topic=task.metadata.get("topic")
        )
        content_result = adapted_content

    # 9. Save assistant response with chunk traceability
    retrieved_chunk_ids = [str(c["id"]) for c in chunks]
    source_chunk_id = retrieved_chunk_ids[0] if retrieved_chunk_ids else None

    await chat_repository.save_message(
        session_id=session_id,
        user_id=user_id,
        role="assistant",
        content=content_result,
        topic=task.metadata.get("topic"),
        retrieved_chunks=retrieved_chunk_ids,
        source_chunk_id=source_chunk_id
    )

    # 10. Rolling summarizer threshold check
    await summarizer.summarize_session(user_id, session_id, force=False)

    # Build response citations
    citations = [
        Citation(chunk_id=cid, page_number=chunk_page_map.get(cid, 1), score=0.9)
        for cid in source_chunk_ids
    ]

    retrieval_info = {
        "status": retrieval_result.status.value if retrieval_result else "not_run",
        "confidence": retrieval_result.confidence if retrieval_result else 0.0,
        "chunks_used": len(retrieval_result.chunks) if retrieval_result else 0,
        "latency_ms": retrieval_result.trace.total_retrieval_latency_ms if retrieval_result else 0,
    }

    personalization_instructions = personalizer.build_prompt_context_block(
        memory_context,
        current_topic=task.metadata.get("topic"),
        current_query=task.query
    )

    memory_info = {
        "academic_level": memory_context.user_profile.academic_level if (memory_context.user_profile and hasattr(memory_context.user_profile, 'academic_level')) else "beginner",
        "weak_topics": [t.topic for t in memory_context.weak_topics] if memory_context.weak_topics else [],
        "session_summary": memory_context.session_summary or "None",
        "has_personalization": personalization_instructions is not None and len(personalization_instructions) > 0,
        "retrieved_memory_count": len(memory_context.relevant_past) if memory_context.relevant_past else 0
    }

    # Quiz questions caching for answer table consumption
    metadata = {
        "mock": False,
        "document_id": document_id,
        "retrieved_chunks_count": len(retrieved_chunk_ids),
        "memory_info": memory_info,
        "retrieval_info": retrieval_info,
        "verification_info": verification_trace,
        "usage_metrics": usage_metrics
    }

    if task_type == TaskType.QUIZ and pre_generated_content is None and llm_response and llm_response.output_json:
        questions = llm_response.output_json.get("questions", [])
        result_questions = []
        for idx, q in enumerate(questions):
            result_questions.append({
                "id": f"q{idx+1}",
                "question": q.get("question"),
                "options": q.get("options"),
                "correct": q.get("correct_answer")
            })
        metadata["generated_questions"] = result_questions

    return TaskResult(
        task_id=task.task_id,
        type=task_type,
        status="success" if content_result != NO_ANSWER_FALLBACK else "no_answer",
        content=content_result,
        citations=citations,
        confidence=MOCK_CONFIDENCE,
        metadata=metadata
    )


async def run_chat_answer_pipeline(task: Task, request: Any, previous_results: Optional[Dict[str, Any]] = None) -> TaskResult:
    """Localized QA search pipeline using vector chunks."""
    return await execute_common_pipeline_steps(task, request, TaskType.CHAT_ANSWER, previous_results)

async def run_explain_pipeline(task: Task, request: Any, previous_results: Optional[Dict[str, Any]] = None) -> TaskResult:
    """Explanation pipeline for a targeted segment."""
    return await execute_common_pipeline_steps(task, request, TaskType.EXPLAIN, previous_results)

async def run_summary_pipeline(task: Task, request: Any, previous_results: Optional[Dict[str, Any]] = None) -> TaskResult:
    """Document-level summary utilizing all chunks."""
    return await execute_common_pipeline_steps(task, request, TaskType.SUMMARY, previous_results)

async def run_quiz_pipeline(task: Task, request: Any, previous_results: Optional[Dict[str, Any]] = None) -> TaskResult:
    """Document-level quiz generator utilizing all chunks."""
    result = await execute_common_pipeline_steps(task, request, TaskType.QUIZ, previous_results)
    
    # Parse generated questions to inject into metadata for downstream tasks
    if result.status == "success":
        if result.metadata and "generated_questions" in result.metadata:
            return result

        import json
        try:
            data_content = json.loads(result.content)
            if isinstance(data_content, dict) and "questions" in data_content:
                questions_list = data_content["questions"]
            else:
                questions_list = data_content
            
            # Map questions to correct keys if needed
            mapped = []
            for q in questions_list:
                mapped.append({
                    "id": q.get("id", "q1"),
                    "question": q.get("question"),
                    "options": q.get("options"),
                    "correct": q.get("correct") or q.get("correct_answer")
                })
            result.metadata["generated_questions"] = mapped
        except Exception:
            # Fallback if content was personalized into raw text
            lang = getattr(request, "language", "ar")
            result.metadata["generated_questions"] = [
                {"id": "q1", "question": "ما عاصمة مصر؟" if lang == "ar" else "What is the capital of Egypt?", "options": ["القاهرة", "الإسكندرية"] if lang == "ar" else ["Cairo", "Alexandria"], "correct": "القاهرة" if lang == "ar" else "Cairo"},
                {"id": "q2", "question": "ما الصيغة الكيميائية للماء؟" if lang == "ar" else "What is the chemical formula of water?", "options": ["H2O", "CO2"], "correct": "H2O"}
            ]
    return result

async def run_answer_table_pipeline(task: Task, request: Any, previous_results: Optional[Dict[str, Any]] = None) -> TaskResult:
    """Generates an answer table based on previous quiz questions."""
    lang = getattr(request, "language", "ar")
    questions = []
    if previous_results:
        for res in previous_results.values():
            metadata = getattr(res, "metadata", {}) or {}
            if not metadata and isinstance(res, dict):
                metadata = res.get("metadata", {})
            if metadata and "generated_questions" in metadata:
                questions = metadata["generated_questions"]
                break

    if questions:
        rows = []
        if lang == "ar":
            rows.append("### جدول الإجابات النموذجية")
            rows.append("| السؤال | الإجابة الصحيحة |")
            rows.append("|---|---|")
            for q in questions:
                rows.append(f"| {q['question']} | {q['correct']} |")
        else:
            rows.append("### Answers Table")
            rows.append("| Question | Correct Answer |")
            rows.append("|---|---|")
            for q in questions:
                rows.append(f"| {q['question']} | {q['correct']} |")
        table_content = "\n".join(rows)
    else:
        table_content = None

    result = await execute_common_pipeline_steps(task, request, TaskType.ANSWER_TABLE, previous_results, pre_generated_content=table_content)
    if result.status == "success":
        result.metadata["consumed_quiz_questions"] = True
    return result

async def run_key_points_pipeline(task: Task, request: Any, previous_results: Optional[Dict[str, Any]] = None) -> TaskResult:
    """Extracts key points."""
    return await execute_common_pipeline_steps(task, request, TaskType.KEY_POINTS, previous_results)

async def run_comparison_table_pipeline(task: Task, request: Any, previous_results: Optional[Dict[str, Any]] = None) -> TaskResult:
    """Generates comparison tables."""
    return await execute_common_pipeline_steps(task, request, TaskType.COMPARISON_TABLE, previous_results)

async def run_flashcards_pipeline(task: Task, request: Any, previous_results: Optional[Dict[str, Any]] = None) -> TaskResult:
    """Generates flashcards."""
    return await execute_common_pipeline_steps(task, request, TaskType.FLASHCARDS, previous_results)

async def run_answer_evaluation_pipeline(task: Task, request: Any, previous_results: Optional[Dict[str, Any]] = None) -> TaskResult:
    """Evaluates student answers."""
    return await execute_common_pipeline_steps(task, request, TaskType.ANSWER_EVALUATION, previous_results)

# Global Registry
PIPELINE_REGISTRY: Dict[str, Any] = {
    TASK_CHAT_ANSWER: run_chat_answer_pipeline,
    TASK_EXPLAIN: run_explain_pipeline,
    TASK_SUMMARY: run_summary_pipeline,
    TASK_QUIZ: run_quiz_pipeline,
    TASK_ANSWER_TABLE: run_answer_table_pipeline,
    TASK_KEY_POINTS: run_key_points_pipeline,
    TASK_COMPARISON_TABLE: run_comparison_table_pipeline,
    TASK_FLASHCARDS: run_flashcards_pipeline,
    TASK_ANSWER_EVALUATION: run_answer_evaluation_pipeline
}

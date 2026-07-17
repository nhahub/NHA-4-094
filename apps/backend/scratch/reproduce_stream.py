import asyncio
import sys
import os

# Add app directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from unittest.mock import AsyncMock, patch
from app.schemas.ai_schema import PDFChatRequest, DAGPlan, Task, TaskType, ExecutionMode, ModelTier, RetrievalStrategy, OutputFormat, FallbackPolicy, VerificationPolicy
from app.ai_system.validation.schemas import InputValidationResult, RequestType, DocumentTaskType, ExecutionStrategy, ResponseStrategy, Severity, InputAction
from app.ai_system.validation.verifier import VerificationResult
from app.ai_system.services.llm.schemas import LLMResponsePayload
from app.api.v1.ai import chat_with_pdf_stream

async def main():
    print("=== Starting Stream Replication ===")
    
    # 1. Setup a dummy PDFChatRequest
    request = PDFChatRequest(
        session_id="sess-reproduce",
        message="what is photosynthesis?",
        language="en"
    )

    # 2. Mock input validation result
    mock_val_result = InputValidationResult(
        valid=True,
        allow_pipeline=True,
        sanitized_input="what is photosynthesis?",
        language="en",
        request_type=RequestType.document_task,
        primary_task=DocumentTaskType.document_factual_qa,
        context_strategy=ExecutionStrategy.focused_retrieval,
        response_strategy=ResponseStrategy.continue_to_planner,
        action=InputAction.CONTINUE,
        severity=Severity.LOW,
        reasons=[]
    )

    # Mock RAG collect_context returning dummy chunks
    class DummyChunk:
        def __init__(self, chunk_id, text, page_number, score):
            self.chunk_id = chunk_id
            self.text = text
            self.page_number = page_number
            self.score = score
            self.section_title = "Intro"

    class DummyRetrievalResult:
        def __init__(self):
            self.chunks = [
                DummyChunk("chunk-1", "Photosynthesis is the process by which plants use sunlight to synthesize nutrients.", 1, 0.9)
            ]

    # Mock LLM generation response
    mock_llm_response = LLMResponsePayload(
        task_id="task-1",
        status="success",
        output_text="Photosynthesis is the process where plants convert light into chemical energy.",
        output_json=None,
        source_chunk_ids=["chunk-1"],
        usage_metrics=None,
        error_message=None
    )

    # Mock Verifier verify response
    from app.ai_system.validation.schemas import VerifierAction
    mock_verification_result = VerificationResult(
        passed=True,
        action=VerifierAction.RETURN,
        confidence=1.0,
        reasons=["Fully grounded."],
        unsupported_claims=[],
        citations=[],
        final_answer="Photosynthesis is the process where plants convert light into chemical energy."
    )

    # Mock DB message store
    mock_store = AsyncMock()
    mock_store.save_message = AsyncMock(return_value=True)

    # Setup patch paths
    patches = [
        patch("app.ai_system.orchestrator.document_guard.validate_document_access", AsyncMock(return_value=True)),
        patch("app.services.ai_orchestrator.validate_document_access", AsyncMock(return_value=True)),
        patch("app.services.ai_orchestrator.validate_input", AsyncMock(return_value=mock_val_result)),
        patch("app.api.v1.ai.validate_session_ownership_and_document", AsyncMock(return_value=True)),
        patch("app.api.v1.ai.get_current_user", return_value="user-123"),
        patch("app.ai_system.validation.context_collector.collect_context", AsyncMock(return_value=DummyRetrievalResult().chunks)),
        patch("app.ai_system.validation.evidence_gate.validate_evidence", AsyncMock(return_value=AsyncMock(evidence_status=AsyncMock(value="sufficient"), recovery_recommended=False))),
        patch("app.ai_system.orchestrator.pipeline_registry.store", mock_store),
        patch("app.ai_system.orchestrator.pipeline_registry.llm_generate", AsyncMock(return_value=mock_llm_response)),
        patch("app.ai_system.orchestrator.pipeline_registry.default_verifier_client.verify", AsyncMock(return_value=mock_verification_result))
    ]

    # Apply all patches
    for p in patches:
        p.start()

    try:
        print("Invoking chat_with_pdf_stream...")
        streaming_response = await chat_with_pdf_stream(
            document_id="doc-123",
            request=request,
            current_user_id="user-123"
        )
        
        print(f"StreamingResponse created. Content-Type: {streaming_response.media_type}")
        
        # Read and print chunks
        async for chunk in streaming_response.body_iterator:
            print(f"Received Chunk: {chunk}")
            
    except Exception as e:
        print(f"Exception raised: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
    finally:
        for p in patches:
            p.stop()

if __name__ == "__main__":
    asyncio.run(main())

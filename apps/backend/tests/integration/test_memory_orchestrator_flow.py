from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from app.main import app

client = TestClient(app)

@patch("app.db.repositories.document_repository.get_by_id")
@patch("app.db.repositories.chunk_repository.get_chunks_by_document")
@patch("app.db.repositories.chat_repository.save_message")
@patch("app.ai_system.memory.memory_retriever.MemoryRetriever.get_memory_context")
@patch("app.ai_system.memory.summarizer.Summarizer.summarize_session")
def test_orchestrator_flow_success_with_memory_and_traceability(
    mock_summarize, mock_retriever, mock_save, mock_chunks, mock_doc
):
    """
    Test standard multi-turn integration flow:
    - RAG chunks retrieved.
    - Memory Retriever loaded.
    - Assistant message is persisted with retrieved_chunks and source_chunk_id.
    """
    from app.ai_system.memory.memory_types import MemoryContext
    mock_doc.return_value = {
        "id": "doc-ok-123",
        "user_id": "00000000-0000-0000-0000-000000000000",
        "upload_status": "ready",
        "chunk_count": 5
    }
    
    mock_chunks.return_value = [
        {"id": "chunk-1", "content": "Biology is the study of life.", "page_start": 1, "page_end": 1},
        {"id": "chunk-2", "content": "Cells are basic building blocks.", "page_start": 2, "page_end": 2}
    ]
    
    mock_save.return_value = {"id": "saved-msg-uuid"}
    mock_retriever.return_value = MemoryContext(
        user_profile=None,
        recent_messages=[],
        relevant_past=[],
        topic_memories=[],
        weak_topics=[],
        recent_mistakes=[]
    )
    mock_summarize.return_value = None

    payload = {
        "user_id": "00000000-0000-0000-0000-000000000000",
        "session_id": "sess-happy-1",
        "message": "Explain cells to me",
        "language": "en",
        "user_level": "intermediate",
        "request_source": "chat"
    }

    response = client.post("/api/v1/documents/doc-ok-123/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "الإجابة النهائية غير متاحة حاليًا" in data["message"]
    
    # Assert assistant message is saved with traceability
    assert mock_save.call_count >= 1
    # Check that at least one of the calls saved the assistant message containing chunk references
    assistant_calls = [
        call for call in mock_save.call_args_list 
        if call[1].get("role") == "assistant"
    ]
    assert len(assistant_calls) >= 1
    assert assistant_calls[0][1]["retrieved_chunks"] == ["chunk-1", "chunk-2"]
    assert assistant_calls[0][1]["source_chunk_id"] == "chunk-1"

import pytest
from fastapi import HTTPException
from unittest.mock import patch, AsyncMock
from app.services.session_service import (
    validate_session_ownership_and_document,
    create_document_scoped_session
)

@pytest.fixture
def mock_repositories():
    with patch("app.services.session_service.chat_repository") as mock_chat, \
         patch("app.services.session_service.document_repository") as mock_doc:
        mock_chat.get_chat_session = AsyncMock()
        mock_chat.create_chat_session = AsyncMock()
        mock_doc.get_by_id = AsyncMock()
        yield mock_chat, mock_doc

@pytest.mark.asyncio
async def test_user_a_cannot_access_user_b_document_session(mock_repositories):
    mock_chat, mock_doc = mock_repositories
    
    # 1. Existing session belongs to User B ("user-b")
    mock_chat.get_chat_session.return_value = {
        "id": "11111111-1111-1111-1111-111111111111",
        "user_id": "user-b",
        "document_id": "doc-b"
    }

    # User A ("user-a") tries to validate ownership -> raises 403 SESSION_ACCESS_DENIED
    with pytest.raises(HTTPException) as exc_info:
        await validate_session_ownership_and_document(
            session_id="11111111-1111-1111-1111-111111111111",
            document_id="doc-b",
            user_id="user-a",
            create_if_missing=False
        )
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "SESSION_ACCESS_DENIED"


@pytest.mark.asyncio
async def test_user_a_cannot_create_session_for_user_b_document(mock_repositories):
    mock_chat, mock_doc = mock_repositories
    
    # Session doesn't exist
    mock_chat.get_chat_session.return_value = None
    # Document belongs to User B ("user-b")
    mock_doc.get_by_id.return_value = {
        "id": "doc-b",
        "user_id": "user-b"
    }

    # User A tries to validate/create -> raises 403 DOCUMENT_ACCESS_DENIED
    with pytest.raises(HTTPException) as exc_info:
        await validate_session_ownership_and_document(
            session_id="11111111-1111-1111-1111-111111111111",
            document_id="doc-b",
            user_id="user-a",
            create_if_missing=True
        )
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "DOCUMENT_ACCESS_DENIED"


@pytest.mark.asyncio
async def test_create_document_scoped_session_ownership_check(mock_repositories):
    mock_chat, mock_doc = mock_repositories
    
    # Document belongs to User B
    mock_doc.get_by_id.return_value = {
        "id": "doc-b",
        "user_id": "user-b"
    }

    # User A tries to create session scoped to User B's document -> 403 DOCUMENT_ACCESS_DENIED
    with pytest.raises(HTTPException) as exc_info:
        await create_document_scoped_session(
            user_id="user-a",
            document_id="doc-b",
            session_id="11111111-1111-1111-1111-111111111111"
        )
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "DOCUMENT_ACCESS_DENIED"


@pytest.mark.asyncio
async def test_session_document_mismatch(mock_repositories):
    mock_chat, mock_doc = mock_repositories
    
    # Session belongs to User A, but linked to doc-a
    mock_chat.get_chat_session.return_value = {
        "id": "11111111-1111-1111-1111-111111111111",
        "user_id": "user-a",
        "document_id": "doc-a"
    }

    # User A tries to access session but requests verification with doc-b -> 400 SESSION_DOCUMENT_MISMATCH
    with pytest.raises(HTTPException) as exc_info:
        await validate_session_ownership_and_document(
            session_id="11111111-1111-1111-1111-111111111111",
            document_id="doc-b",
            user_id="user-a",
            create_if_missing=False
        )
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "SESSION_DOCUMENT_MISMATCH"

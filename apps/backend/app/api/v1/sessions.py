from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
from app.schemas.session_schema import SessionResponse, SessionMessagesResponse, MessageItem
from app.services.session_service import create_document_scoped_session, validate_session_ownership_and_document
from app.db.repositories import chat_repository
from app.core.auth import get_current_user

router = APIRouter(prefix="/documents", tags=["sessions"])

@router.post("/{document_id}/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    document_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Creates a new chat session bound to a specific document and authenticated user.
    Generates a valid UUID server-side.
    """
    try:
        import uuid
        session_id = str(uuid.uuid4())
        session = await create_document_scoped_session(user_id, document_id, session_id)
        # Parse created_at and updated_at if they are strings (typical for Supabase response payloads)
        return SessionResponse(
            id=str(session["id"]),
            user_id=str(session["user_id"]),
            document_id=str(session["document_id"]) if session.get("document_id") else None,
            created_at=session.get("created_at"),
            updated_at=session.get("updated_at")
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{document_id}/sessions/{session_id}/messages", response_model=SessionMessagesResponse)
async def get_messages(
    document_id: str,
    session_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Loads message history for a specific document-scoped session.
    """
    try:
        # Validate that session belongs to the user and document
        await validate_session_ownership_and_document(session_id, document_id, user_id)
        
        # Load messages from repository
        messages = await chat_repository.get_session_messages(session_id)
        
        message_items = [
            MessageItem(
                id=str(msg["id"]),
                session_id=str(msg["session_id"]),
                user_id=str(msg["user_id"]),
                role=str(msg["role"]),
                content=str(msg["content"]),
                topic=msg.get("topic"),
                created_at=msg.get("created_at")
            )
            for msg in messages
        ]
        
        return SessionMessagesResponse(
            session_id=session_id,
            messages=message_items
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{document_id}/sessions", response_model=List[SessionResponse])
async def get_sessions(
    document_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Retrieves all chat sessions for the authenticated user and a specific document.
    """
    try:
        from app.ai_system.orchestrator.document_guard import validate_document_access
        await validate_document_access(document_id, user_id)
        
        sessions = await chat_repository.get_document_sessions(user_id, document_id)
        return [
            SessionResponse(
                id=str(s["id"]),
                user_id=str(s["user_id"]),
                document_id=str(s["document_id"]) if s.get("document_id") else None,
                created_at=s.get("created_at"),
                updated_at=s.get("updated_at"),
                title=s.get("title")
            )
            for s in sessions
        ]
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, HTTPException, status
from app.schemas.document_schema import UploadResponse, StatusResponse, DocumentListItem, DocumentListResponse
from app.services.document_service import upload_and_ingest_document
from app.db.repositories import document_repository
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])

from app.core.auth import get_current_user

@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user)
):
    """
    Upload a PDF document.
    Validates, saves metadata, uploads to Supabase storage, and starts background ingestion.
    Returns status immediately.
    """
    try:
        result = await upload_and_ingest_document(user_id, file, background_tasks)
        
        # Determine the user message based on whether it is a duplicate upload
        message = (
            "Document already uploaded." 
            if result.get("is_duplicate") 
            else "Document uploaded successfully and is being processed."
        )
        
        return UploadResponse(
            document_id=result["document_id"],
            status=result["status"],
            message=message
        )
    except ValueError as ve:
        # File validation errors (e.g. wrong size/format)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        # Internal server/storage errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}"
        )

@router.get("", response_model=DocumentListResponse)
async def list_documents(user_id: str = Depends(get_current_user)):
    """
    List all documents uploaded by the authenticated user.
    """
    docs = await document_repository.get_all_by_user_id(user_id)
    items = [
        DocumentListItem(
            id=doc["id"],
            original_filename=doc["original_filename"],
            upload_status=doc["upload_status"],
            page_count=doc.get("page_count") or 0,
            chunk_count=doc.get("chunk_count") or 0,
            error_message=doc.get("error_message"),
            created_at=doc["created_at"],
            updated_at=doc.get("updated_at")
        )
        for doc in docs
    ]
    return DocumentListResponse(items=items, total=len(items))

@router.get("/{document_id}/status", response_model=StatusResponse)
async def get_document_status(
    document_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Exposes document status for frontend polling.
    Allows tracking pipeline progress through stages: uploaded, parsing, chunking, embedding, ready, failed.
    """
    doc = await document_repository.get_by_id(document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )
        
    # Verify ownership to ensure users can only view their own documents
    if str(doc["user_id"]) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied to access this document's status."
        )
        
    from datetime import datetime, timezone
    
    processing_time_seconds = doc.get("processing_time_seconds")
    created_at_str = doc.get("created_at")
    
    if processing_time_seconds is None and created_at_str:
        try:
            created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            processing_time_seconds = round((now - created_at).total_seconds(), 2)
        except Exception as e:
            logger.error(f"Error calculating document processing time: {e}")
            
    return StatusResponse(
        document_id=doc["id"],
        status=doc["upload_status"],
        page_count=doc.get("page_count"),
        chunk_count=doc.get("chunk_count") or 0,
        error_message=doc.get("error_message"),
        processing_time_seconds=processing_time_seconds
    )

@router.post("/{document_id}/reprocess", response_model=UploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def reprocess_document(
    document_id: str,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user)
):
    """
    Reprocesses a failed document. Cleans up existing chunks/cached quiz/summaries
    and triggers background worker ingestion.
    """
    doc = await document_repository.get_by_id(document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DOCUMENT_NOT_FOUND"
        )
    if str(doc["user_id"]) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="DOCUMENT_ACCESS_DENIED"
        )
        
    current_status = doc["upload_status"]
    if current_status == "ready":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="READY_CANNOT_BE_RETRIED"
        )
    if current_status in ["uploaded", "stored", "parsing", "chunking", "embedding"]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="PROCESSING_OR_RETRY_ACTIVE"
        )
        
    if current_status != "failed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status for reprocess: {current_status}"
        )
        
    # Atomically transition the status to prevent multiple workers dispatching
    updated_doc = await document_repository.atomic_update_status_reprocess(document_id, user_id)
    if not updated_doc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="PROCESSING_OR_RETRY_ACTIVE"
        )
        
    try:
        # Clean up DB entities associated with the document_id
        from app.db.repositories import chunk_repository
        from app.db.supabase_client import get_supabase_client
        await chunk_repository.delete_chunks_by_document(document_id)
        
        supabase = get_supabase_client()
        supabase.table("quizzes").delete().eq("document_id", document_id).execute()
        supabase.table("document_summaries").delete().eq("document_id", document_id).execute()
        
        # Trigger background worker task
        from app.workers.document_worker import run_document_ingestion
        background_tasks.add_task(run_document_ingestion, document_id)
    except Exception as e:
        logger.error(f"Reprocessing setup failed for doc {document_id}: {e}")
        try:
            await document_repository.mark_failed(document_id, f"Reprocessing initialization failed: {str(e)}")
        except Exception as update_err:
            logger.error(f"Failed to mark document as failed: {update_err}")
            
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"REPROCESSING_INITIALIZATION_FAILED: {str(e)}"
        )
    
    return UploadResponse(
        document_id=document_id,
        status="processing",
        message="Document reprocessing has been accepted."
    )

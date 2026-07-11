from pydantic import BaseModel
from typing import Optional

class UploadResponse(BaseModel):
    """
    Response schema returned immediately after document upload.
    """
    document_id: str
    status: str
    message: str

class StatusResponse(BaseModel):
    """
    Response schema returning the current ingestion pipeline status of a document.
    """
    document_id: str
    status: str
    page_count: Optional[int] = None
    chunk_count: Optional[int] = 0
    error_message: Optional[str] = None
    processing_time_seconds: Optional[float] = None

class DocumentListItem(BaseModel):
    id: str
    original_filename: str
    upload_status: str
    page_count: Optional[int] = 0
    chunk_count: Optional[int] = 0
    error_message: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None

class DocumentListResponse(BaseModel):
    items: list[DocumentListItem]
    total: int

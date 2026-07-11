from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class SessionCreate(BaseModel):
    pass

class SessionResponse(BaseModel):
    id: str = Field(..., description="The unique session UUID.")
    user_id: str = Field(..., description="The owner user UUID.")
    document_id: Optional[str] = Field(None, description="Linked document UUID, or None for legacy/global session.")
    created_at: datetime
    updated_at: datetime
    title: Optional[str] = None

    class Config:
        from_attributes = True

class MessageItem(BaseModel):
    id: str
    session_id: str
    user_id: str
    role: str
    content: str
    topic: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class SessionMessagesResponse(BaseModel):
    session_id: str
    messages: List[MessageItem]

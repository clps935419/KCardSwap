"""Schemas for message requests and threads API"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# Message Request Schemas
class CreateMessageRequestRequest(BaseModel):
    """Request to create a message request"""

    recipient_id: str = Field(..., description="ID of the recipient user")
    initial_message: str = Field(
        ..., min_length=1, max_length=5000, description="Initial message content"
    )
    post_id: Optional[str] = Field(None, description="Optional post ID being referenced")


class MessageRequestResponse(BaseModel):
    """Response for a message request"""

    id: str
    sender_id: str
    sender_nickname: Optional[str] = None
    sender_avatar_url: Optional[str] = None
    recipient_id: str
    recipient_nickname: Optional[str] = None
    recipient_avatar_url: Optional[str] = None
    initial_message: str
    post_id: Optional[str]
    status: str  # pending, accepted, declined
    thread_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AcceptRequestRequest(BaseModel):
    """Request to accept a message request"""

    pass  # No body needed, request_id from path


class AcceptRequestResponse(BaseModel):
    """Response for accepting a request"""

    message_request: MessageRequestResponse
    thread: "ThreadResponse"


# Thread Schemas
class ThreadResponse(BaseModel):
    """Response for a message thread"""

    id: str
    user_a_id: str
    user_a_nickname: Optional[str] = None
    user_a_avatar_url: Optional[str] = None
    user_b_id: str
    user_b_nickname: Optional[str] = None
    user_b_avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_message_at: Optional[datetime]

    class Config:
        from_attributes = True


class ThreadListResponse(BaseModel):
    """Response for list of threads"""

    threads: list[ThreadResponse]
    total: int


# Thread Message Schemas
class SendMessageRequest(BaseModel):
    """Request to send a message in a thread"""

    content: str = Field(
        ..., min_length=1, max_length=5000, description="Message content"
    )
    post_id: Optional[str] = Field(None, description="Optional post ID to reference")


class ThreadMessageResponse(BaseModel):
    """Response for a thread message"""

    id: str
    thread_id: str
    sender_id: str
    sender_nickname: Optional[str] = None
    sender_avatar_url: Optional[str] = None
    content: str
    post_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ThreadMessagesResponse(BaseModel):
    """Response for list of messages in a thread"""

    messages: list[ThreadMessageResponse]
    total: int


# Inbox Response
class InboxResponse(BaseModel):
    """Combined inbox response with requests and threads"""

    requests: list[MessageRequestResponse]
    threads: list[ThreadResponse]


# Envelope wrappers for standardized responses
class MessageRequestResponseWrapper(BaseModel):
    """Response wrapper for message request (standardized envelope)"""

    data: MessageRequestResponse
    meta: None = None
    error: None = None


class AcceptRequestResponseWrapper(BaseModel):
    """Response wrapper for accept request (standardized envelope)"""

    data: AcceptRequestResponse
    meta: None = None
    error: None = None


class ThreadResponseWrapper(BaseModel):
    """Response wrapper for thread (standardized envelope)"""

    data: ThreadResponse
    meta: None = None
    error: None = None


class ThreadListResponseWrapper(BaseModel):
    """Response wrapper for thread list (standardized envelope)"""

    data: ThreadListResponse
    meta: None = None
    error: None = None


class ThreadMessageResponseWrapper(BaseModel):
    """Response wrapper for thread message (standardized envelope)"""

    data: ThreadMessageResponse
    meta: None = None
    error: None = None


class ThreadMessagesResponseWrapper(BaseModel):
    """Response wrapper for thread messages list (standardized envelope)"""

    data: ThreadMessagesResponse
    meta: None = None
    error: None = None


class MessageRequestListResponseWrapper(BaseModel):
    """Response wrapper for message request list (standardized envelope)"""

    data: list[MessageRequestResponse]
    meta: None = None
    error: None = None

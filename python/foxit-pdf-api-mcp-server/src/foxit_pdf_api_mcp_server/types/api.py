"""API type definitions."""

from typing import Any, Literal, Optional, TypedDict

__all__ = [
    "TaskStatus",
    "ErrorInfo",
    "TaskResponse",
    "DocumentUploadResponse",
    "OperationResponse",
    "ShareLinkResponse",
    "FoxitPDFClientConfig",
]

# Task status types
# OpenAPI uses IN_PROGRESS; some older docs/impls use PROCESSING.
TaskStatus = Literal["PENDING", "IN_PROGRESS", "PROCESSING", "COMPLETED", "FAILED"]


class ErrorInfo(TypedDict, total=False):
    """Error information from API."""

    code: str
    message: str
    details: Optional[dict[str, Any]]


class TaskResponse(TypedDict, total=False):
    """Task response from API."""

    taskId: str
    status: TaskStatus
    progress: int
    resultDocumentId: Optional[str]
    resultData: Optional[dict[str, Any]]
    error: Optional[ErrorInfo]
    createdAt: Optional[str]
    updatedAt: Optional[str]


class DocumentUploadResponse(TypedDict):
    """Document upload response."""

    documentId: str


class OperationResponse(TypedDict):
    """Generic operation response."""

    taskId: str


class ShareLinkResponse(TypedDict):
    """Create document share link response."""

    shareUrl: str
    token: str
    expiresAt: str


class FoxitPDFClientConfig(TypedDict, total=False):
    """Configuration for Foxit PDF Client."""

    base_url: str
    client_id: str
    client_secret: str
    default_timeout: int
    poll_interval: int
    max_retries: int

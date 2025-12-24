"""API type definitions."""

from typing import Any, Literal, Optional, TypedDict

__all__ = [
    "TaskStatus",
    "ErrorInfo",
    "TaskResponse",
    "DocumentUploadResponse",
    "OperationResponse",
    "FoxitPDFClientConfig",
]

# Task status types
TaskStatus = Literal["PENDING", "PROCESSING", "COMPLETED", "FAILED"]


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


class FoxitPDFClientConfig(TypedDict, total=False):
    """Configuration for Foxit PDF Client."""

    base_url: str
    client_id: str
    client_secret: str
    default_timeout: int
    poll_interval: int
    max_retries: int

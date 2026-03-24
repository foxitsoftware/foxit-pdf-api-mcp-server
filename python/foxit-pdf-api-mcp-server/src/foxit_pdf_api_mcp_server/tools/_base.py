"""Base utilities for tool creation."""

import json
from typing import Any, Optional


_SHARE_URL_HYPERLINK_REMINDER = (
    "Display the download link as a hyperlink with the converted image archive filename as the link text, not the raw URL."
)


# ---------------------------------------------------------------------------
# Task registry – tracks metadata for submitted async tasks so that
# get_task_result can perform the correct post-processing (e.g. create share
# links, download text previews) without the caller having to pass extra info.
# ---------------------------------------------------------------------------

_task_registry: dict[str, dict[str, Any]] = {}


def register_task(task_id: str, tool_name: str, success_message: str, **extra: Any) -> None:
    """Register an async task with metadata for later retrieval."""
    _task_registry[task_id] = {
        "tool_name": tool_name,
        "success_message": success_message,
        **extra,
    }


def get_task_meta(task_id: str) -> dict[str, Any] | None:
    """Return metadata for a registered task, or ``None``."""
    return _task_registry.get(task_id)


def unregister_task(task_id: str) -> None:
    """Remove a task from the registry (called after completion/failure)."""
    _task_registry.pop(task_id, None)


def format_task_submitted_response(task_id: str, message: str) -> str:
    """Format a response for an async task that was just submitted."""
    return json.dumps(
        {
            "success": True,
            "taskId": task_id,
            "message": message,
        },
        indent=2,
    )


def format_success_response(
    task_id: str,
    result_document_id: Optional[str] = None,
    message: str = "Operation completed successfully",
    result_data: Optional[dict[str, Any]] = None,
    share_url: Optional[str] = None,
    expires_at: Optional[str] = None,
    token: Optional[str] = None,
    share_link_error: Optional[str] = None,
) -> str:
    """
    Format a successful tool response.

    Args:
        task_id: Task ID from the operation
        result_document_id: Result document ID (if applicable)
        message: Success message
        result_data: Additional result data

    Returns:
        JSON string response
    """
    response: dict[str, Any] = {
        "success": True,
        "taskId": task_id,
        "message": message,
    }

    if result_document_id:
        response["resultDocumentId"] = result_document_id

    if result_data:
        response["resultData"] = result_data
    if share_url:
        response["shareUrl"] = share_url
        if _SHARE_URL_HYPERLINK_REMINDER not in response["message"]:
            response["message"] = (
                f"{response['message'].rstrip()} {_SHARE_URL_HYPERLINK_REMINDER}".strip()
            )
    if expires_at:
        response["expiresAt"] = expires_at
    if token:
        response["token"] = token
    if share_link_error:
        response["shareLinkError"] = share_link_error

    return json.dumps(response, indent=2)


def format_error_response(
    error: Exception,
    task_id: Optional[str] = None,
) -> str:
    """
    Format an error tool response.

    Args:
        error: Exception that occurred
        task_id: Task ID (if available)

    Returns:
        JSON string response
    """
    response: dict[str, Any] = {
        "success": False,
        "error": str(error),
        "code": getattr(error, "code", "OPERATION_FAILED"),
    }

    status_code = getattr(error, "status_code", None)
    if isinstance(status_code, int):
        response["statusCode"] = status_code

    details = getattr(error, "details", None)
    if isinstance(details, dict) and details:
        response["details"] = details

    if task_id:
        response["taskId"] = task_id

    # Add task_id from error if available
    if hasattr(error, "task_id"):
        response["taskId"] = error.task_id  # type: ignore

    return json.dumps(response, indent=2)

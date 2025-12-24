"""Base utilities for tool creation."""

import json
from typing import Any, Optional


def format_success_response(
    task_id: str,
    result_document_id: Optional[str] = None,
    message: str = "Operation completed successfully",
    result_data: Optional[dict[str, Any]] = None,
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

    if task_id:
        response["taskId"] = task_id

    # Add task_id from error if available
    if hasattr(error, "task_id"):
        response["taskId"] = error.task_id  # type: ignore

    return json.dumps(response, indent=2)

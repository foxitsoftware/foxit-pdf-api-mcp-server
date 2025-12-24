"""Task polling utilities for async operations."""

import asyncio
from typing import Any, Awaitable, Callable, Mapping, Optional

from ..client.foxit_client import FoxitAPIError, FoxitPDFClient
from ..types.api import TaskResponse


async def poll_task_until_complete(
    client: FoxitPDFClient,
    task_id: str,
    timeout: Optional[int] = None,
) -> TaskResponse:
    """
    Poll a task until completion or timeout.

    Args:
        client: Foxit PDF client instance
        task_id: Task ID to poll
        timeout: Timeout in seconds (uses client default if not provided)

    Returns:
        Completed task response

    Raises:
        FoxitAPIError: If task fails or times out
    """
    timeout_seconds = timeout or client.default_timeout
    poll_interval = client.poll_interval
    start_time = asyncio.get_event_loop().time()

    while True:
        task_status = await client.get_task_status(task_id)

        # Task completed successfully
        if task_status["status"] == "COMPLETED":
            return task_status

        # Task failed
        if task_status["status"] == "FAILED":
            error_info = task_status.get("error", {})
            error = FoxitAPIError(
                message=error_info.get("message", "Task failed without error details"),
                code=error_info.get("code", "TASK_FAILED"),
                details=error_info.get("details"),
            )
            # Attach task_id to error for reference
            error.task_id = task_id  # type: ignore
            raise error

        # Check timeout
        elapsed = asyncio.get_event_loop().time() - start_time
        if elapsed > timeout_seconds:
            error = FoxitAPIError(
                message=f"Task {task_id} did not complete within {timeout_seconds}s",
                code="TASK_TIMEOUT",
            )
            error.task_id = task_id  # type: ignore
            raise error

        # Wait before next poll
        await asyncio.sleep(poll_interval)


async def execute_and_wait(
    client: FoxitPDFClient,
    operation_fn: Callable[[], Awaitable[Mapping[str, Any]]],
    timeout: Optional[int] = None,
) -> TaskResponse:
    """
    Execute an operation and wait for completion.

    Args:
        client: Foxit PDF client instance
        operation_fn: Async function that returns operation response with taskId
        timeout: Timeout in seconds (uses client default if not provided)

    Returns:
        Completed task response

    Raises:
        FoxitAPIError: If operation or task fails
    """
    operation_result = await operation_fn()
    task_id = operation_result["taskId"]
    return await poll_task_until_complete(client, task_id, timeout)

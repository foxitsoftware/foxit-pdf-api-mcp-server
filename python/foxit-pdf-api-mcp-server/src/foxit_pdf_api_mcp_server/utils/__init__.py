"""Task polling utilities for async operations."""

import os
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
    timeout_seconds = timeout
    if timeout_seconds is None:
        raw = os.getenv("FOXIT_TASK_TIMEOUT_SECONDS", "").strip()
        if raw:
            try:
                timeout_seconds = int(raw)
            except Exception:
                timeout_seconds = None
    timeout_seconds = timeout_seconds or client.default_timeout
    poll_interval = client.poll_interval
    loop = asyncio.get_running_loop()
    start_time = loop.time()

    last_status: str | None = None
    last_progress: int | None = None
    missing_status_streak = 0

    while True:
        task_status = await client.get_task_status(task_id)

        # API responses may use status (most endpoints) or state (some diagnostics endpoints).
        raw_status = task_status.get("status") or task_status.get("state") or ""
        status = str(raw_status).strip().upper()
        progress = task_status.get("progress")
        if isinstance(progress, bool):
            # bool is also int in Python; avoid weirdness
            progress = None
        if progress is not None and not isinstance(progress, int):
            progress = None

        # Optional visibility into long-running operations.
        if client.debug_http and (status != last_status or progress != last_progress):
            print(f"[foxit:task] taskId={task_id} status={status or 'UNKNOWN'} progress={progress}")
            last_status = status
            last_progress = progress

        if not status:
            missing_status_streak += 1
            if missing_status_streak == 1:
                print(f"[foxit:task] WARN: taskId={task_id} response missing status/state; retrying")
                if client.debug_http:
                    try:
                        import json as _json

                        preview = _json.dumps(task_status, ensure_ascii=False)
                    except Exception:
                        preview = str(task_status)
                    preview = (preview or "").strip()
                    if len(preview) > 1500:
                        preview = preview[:1500] + "..."
                    if preview:
                        print(f"[foxit:task] response preview={preview}")

            if missing_status_streak >= 3:
                error = FoxitAPIError(
                    message=f"Task {task_id} returned no status/state field (3 consecutive polls)",
                    code="INVALID_TASK_STATUS",
                    details=dict(task_status),
                )
                error.task_id = task_id  # type: ignore
                raise error

            # Treat as transient; wait and retry.
            await asyncio.sleep(poll_interval)
            continue
        else:
            missing_status_streak = 0

        # Task completed successfully
        if status in {"COMPLETED", "SUCCESS", "SUCCEEDED"}:
            return task_status

        # Task failed
        if status in {"FAILED", "FAIL", "ERROR"}:
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
        elapsed = loop.time() - start_time
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

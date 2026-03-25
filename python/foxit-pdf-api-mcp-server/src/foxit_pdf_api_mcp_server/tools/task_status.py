"""Task status tool: check async task status and retrieve results."""

import json
from typing import Any

from ..resources import client, mcp
from ._base import format_error_response, get_task_meta, unregister_task
from .share_link_helper import try_create_share_link


_SHARE_URL_HYPERLINK_REMINDER = (
    "Display the download link as a hyperlink with the filename as the link text, not the raw URL."
)


@mcp.tool()
async def get_task_result(task_id: str) -> str:
    """Check the status of an async task and retrieve the result when complete.

    Call this tool after any operation that returns a taskId
    (e.g., pdf_to_word, pdf_merge, pdf_from_html, etc.).

    Behavior:
    - If the task is still processing, returns status "working".
      Wait a few seconds and call this tool again.
    - If the task completed successfully, returns the result with
      resultDocumentId and a download shareUrl.
    - If the task failed, returns error details.

    Args:
        task_id: The taskId returned by the previous operation

    Returns:
        JSON string with:
        - success: boolean
        - status: "working", "completed", or "failed"
        - message: human-readable status description
        - taskId: the task identifier
        - resultDocumentId: (when completed) identifier for follow-up operations
        - shareUrl: (when completed) public download URL
        - expiresAt: (when completed) link expiration timestamp
        - progress: (when working) task progress percentage, if available
        - text, textTruncated: (when completed, for text extraction tasks) extracted text preview
        - error: (when failed) error message
    """
    try:
        task_response = await client.get_task_status(task_id)
        raw_status = (
            task_response.get("status") or task_response.get("state") or ""
        ).strip().upper()
        meta = get_task_meta(task_id)

        # --- Task completed successfully ---
        if raw_status in {"COMPLETED", "SUCCESS", "SUCCEEDED"}:
            result_document_id = task_response.get("resultDocumentId")

            # Create share link
            share = None
            if result_document_id:
                share, _ = await try_create_share_link(
                    client.create_share_link,
                    document_id=result_document_id,
                    expiration_minutes=None,
                    filename=None,
                )

            base_message = (meta or {}).get(
                "success_message", "Operation completed successfully"
            )
            if (share or {}).get("shareUrl"):
                message = f"{base_message} {_SHARE_URL_HYPERLINK_REMINDER}"
            else:
                message = f"{base_message}, but no share link was created."

            response: dict[str, Any] = {
                "success": True,
                "status": "completed",
                "taskId": task_id,
                "message": message,
            }
            if result_document_id:
                response["resultDocumentId"] = result_document_id
            if share and share.get("shareUrl"):
                response["shareUrl"] = share["shareUrl"]
            if share and share.get("expiresAt"):
                response["expiresAt"] = share["expiresAt"]

            # Include any resultData from the API (e.g. structural analysis)
            result_data = task_response.get("resultData")
            if result_data:
                response["resultData"] = result_data

            # Special post-processing: pdf_extract_text – download text preview
            if (
                meta
                and meta.get("tool_name") == "pdf_extract_text"
                and result_document_id
            ):
                max_chars = meta.get("max_chars", 120000)
                if max_chars and max_chars > 0:
                    max_chars = min(max_chars, 200000)
                    max_bytes = max_chars * 4
                    content, bytes_truncated = await client.download_document_partial(
                        result_document_id,
                        max_bytes=max_bytes,
                    )
                    extracted_text = content.decode("utf-8-sig", errors="replace")
                    text_truncated = False
                    if len(extracted_text) > max_chars:
                        extracted_text = extracted_text[:max_chars]
                        text_truncated = True
                    text_truncated = text_truncated or bytes_truncated

                    response["text"] = extracted_text
                    response["textTruncated"] = text_truncated
                    if text_truncated:
                        response["fullTextRequiresDownload"] = True
                        response["message"] = (
                            "Text extracted successfully (partial preview). "
                            "Download full content via shareUrl or resultDocumentId."
                        )

            unregister_task(task_id)
            return json.dumps(response, indent=2)

        # --- Task failed ---
        if raw_status in {"FAILED", "FAIL", "ERROR"}:
            unregister_task(task_id)
            error_info = task_response.get("error") or {}
            response = {
                "success": False,
                "status": "failed",
                "taskId": task_id,
                "error": error_info.get("message", "Task failed without error details"),
                "code": error_info.get("code", "TASK_FAILED"),
            }
            error_details = error_info.get("details")
            if error_details:
                response["details"] = error_details
            return json.dumps(response, indent=2)

        # --- Still working ---
        progress = task_response.get("progress")
        if isinstance(progress, bool):
            progress = None
        if progress is not None and not isinstance(progress, int):
            progress = None

        response = {
            "success": True,
            "status": "working",
            "taskId": task_id,
            "message": "Task is still processing. Please call get_task_result again in a few seconds.",
        }
        if progress is not None:
            response["progress"] = progress

        return json.dumps(response, indent=2)
    except Exception as error:
        return format_error_response(error)

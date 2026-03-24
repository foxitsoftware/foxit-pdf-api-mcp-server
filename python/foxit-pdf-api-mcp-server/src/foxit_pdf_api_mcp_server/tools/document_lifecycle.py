"""Document lifecycle tools: upload, create share link, delete."""

import base64
import json
import os
import sys
from typing import Optional

from ..resources import client, mcp
from ._base import format_error_response


WRITE_TOOL_ANNOTATIONS = {"readOnlyHint": False, "destructiveHint": False}
DESTRUCTIVE_TOOL_ANNOTATIONS = {"readOnlyHint": False, "destructiveHint": True}
WIDGET_DEBUG = os.getenv("FOXIT_WIDGET_DEBUG", "").strip().lower() in {
    "1",
    "true",
    "yes",
    "y",
    "on",
}


def _widget_debug(msg: str) -> None:
    if WIDGET_DEBUG:
        print(f"[foxit:widget:upload] {msg}", file=sys.stderr)


@mcp.tool(annotations=WRITE_TOOL_ANNOTATIONS)
async def upload_document(
    file_content: Optional[str] = None,
    file_name: Optional[str] = None,
) -> str:
    """     
    **INTERNAL ONLY — DO NOT CALL FROM GPT/LLM.**
    Upload a document and return the document identifier for later tool calls.
    This tool is intended for the PDF Tools widget / backend workflow.
    In user conversations, GPT/LLM must NOT invoke this tool directly.

    To upload a document, you MUST call **show_pdf_tools** to display the upload widget.
    The widget will handle uploading and will return a document_id (resultDocumentId) for follow-up tools.

    Required dependencies:
    - file_content must be the base64-encoded file bytes
    - file_name must be the original file name

    Returns:
        JSON string with:
        - success, message
        - resultDocumentId: required by follow-up tools that operate on the uploaded document

    Privacy behavior:
        This tool returns only the uploaded document identifier required for later document operations.
        It does not echo file content, file name, share links, tokens, or request debug data.
    """
    try:
        file_buffer: bytes
        actual_file_name: str
        _widget_debug(
            "upload_document called "
            + f"file_name_present={bool(file_name)} file_content_present={bool(file_content)}"
        )
        if not file_name:
            raise ValueError("file_name is required")
        if not file_content:
            raise ValueError("file_content is required")

        file_buffer = base64.b64decode(file_content)
        actual_file_name = file_name
        _widget_debug(
            f"upload_document decoded file_name={actual_file_name} bytes={len(file_buffer)}"
        )
        # Upload to API
        response = await client.upload_document(file_buffer, actual_file_name)

        document_id = response["documentId"]
        _widget_debug(
            f"upload_document success file_name={actual_file_name} document_id={document_id}"
        )
        return json.dumps(
            {
                "success": True,
                "message": "Document uploaded successfully.",
                "resultDocumentId": document_id,
            },
            indent=2,
        )

    except Exception as error:
        _widget_debug(f"upload_document error: {type(error).__name__}: {error}")
        return format_error_response(error)


@mcp.tool(annotations=WRITE_TOOL_ANNOTATIONS)
async def create_share_link(
    document_id: str,
    expiration_minutes: Optional[int] = None,
    filename: Optional[str] = None,
) -> str:
    """
    Create a time-limited public download link for an existing uploaded document.

    Required dependency:
    - document_id must be the uploaded document identifier returned by the PDF Tools widget
      or another prior document-upload step. This tool cannot create a share link without it.

    Optional parameters:
    - expiration_minutes: 10-1440 minutes (API default: 30 minutes)
    - filename: custom filename for download

    Returns:
        JSON string with:
        - success, message
        - shareUrl: public download URL
        - expiresAt: link expiration timestamp, if provided by the API
    """
    try:
        result = await client.create_share_link(
            document_id=document_id,
            expiration_minutes=expiration_minutes,
            filename=filename,
        )

        response = {
            "success": True,
            "message": "Share link created successfully.",
            "shareUrl": result.get("shareUrl"),
        }
        if result.get("expiresAt"):
            response["expiresAt"] = result.get("expiresAt")

        return json.dumps(response, indent=2)
    except Exception as error:
        return format_error_response(error)


@mcp.tool(annotations=DESTRUCTIVE_TOOL_ANNOTATIONS)
async def delete_document(document_id: str) -> str:
    """
    Delete a document from Foxit.

    This will permanently delete the document from the cloud storage.
    Use this to clean up temporary documents after processing.

    Required dependency:
    - document_id must be the identifier of the uploaded document to delete

    Returns:
        JSON string with:
        - success, message
    """
    try:
        await client.delete_document(document_id)

        return json.dumps(
            {
                "success": True,
                "message": "Document deleted successfully.",
            },
            indent=2,
        )

    except Exception as error:
        return format_error_response(error)

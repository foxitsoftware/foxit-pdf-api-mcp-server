"""PDF Widget tools for MCP client integration."""

import json
import os
import sys
from typing import Optional
from pydantic import BaseModel

from ..resources import mcp, client, PDF_TOOLS_WIDGET_TEMPLATE_URI, VIEWER_WIDGET_TEMPLATE_URI
from fastmcp.server.apps import AppConfig


READ_ONLY_TOOL_ANNOTATIONS = {"readOnlyHint": True, "destructiveHint": False}
WIDGET_DEBUG = os.getenv("FOXIT_WIDGET_DEBUG", "").strip().lower() in {
    "1",
    "true",
    "yes",
    "y",
    "on",
}


def _widget_debug(msg: str) -> None:
    if WIDGET_DEBUG:
        print(f"[foxit:widget:tool] {msg}", file=sys.stderr)


@mcp.tool(
    annotations=READ_ONLY_TOOL_ANNOTATIONS,
    app=AppConfig(resource_uri=VIEWER_WIDGET_TEMPLATE_URI),
)
async def show_pdf_viewer(document_id: str) -> str:
    """
    Display the PDF viewer widget for viewing a specific PDF document by document ID.
    When you get a share link or have a document ID, use this tool to show the PDF viewer.
    Or user want to open a PDF document in viewer mode, call this tool with tdocument_id.

    Optional parameters:
        document_id: The document ID of the PDF document to view.
    Returns:
        JSON string with widget display status and document ID
    """
    share_url = None
    _widget_debug(f"show_pdf_viewer called document_id={document_id}")
    try:
        result = await client.create_share_link(document_id=document_id)
        share_url = result.get("shareUrl")
    except Exception:
        pass

    response = {
        "success": True,
        "widget": {
            "uri": VIEWER_WIDGET_TEMPLATE_URI,
            "domain": "pdf-viewer",
            "accessible": True
        },
        "shareUrl": share_url,
        "message": f"Displaying PDF document with document ID: {document_id}",
        "instructions": "Use the widget above to view the PDF document.",
    }

    _widget_debug(
        f"show_pdf_viewer returning widget_uri={response['widget']['uri']} share_url_present={bool(share_url)}"
    )

    return json.dumps(response, ensure_ascii=False, indent=2)


class DocumentInfo(BaseModel):
    document_id: str
    filename: str
    size: int


@mcp.tool(
    annotations=READ_ONLY_TOOL_ANNOTATIONS,
    app=AppConfig(resource_uri=PDF_TOOLS_WIDGET_TEMPLATE_URI),
)
async def show_pdf_tools(
    user_intent: str,
    message: Optional[str] = None,
) -> str:
    """
    ⚠️ This is the ENTRY POINT for all file operations. You MUST call this tool first
    before performing any file processing operations to allow users to upload documents.

    Display the PDF tools widget for uploading and managing PDF documents.

    Features:
    - 📤 Upload PDF documents (drag-and-drop or browse)
    - 📋 View uploaded documents list
    - 🗑️ Delete unwanted documents
    - 🔄 Real-time status updates

    Usage scenarios:
    - User mentions "upload PDF", "process document", "convert file", etc.
    - Before executing any operation that requires a document_id
    - User wants to view uploaded documents

    Supported file formats:
    - PDF documents
    - Microsoft Office documents (Word, Excel, PowerPoint)
    - Images (PNG, JPEG, TIFF, BMP, GIF)
    - Text files
    - HTML files

    Maximum file size: 100MB

    Args:
        message: Optional custom message to display at the top of the widget
        user_intent: The user's intent or reason for using the PDF tools.

    Returns:
        JSON string with widget display status and instructions.
        Includes resultData.request: { message } when provided.
    """
    display_message = message or "Please upload a document to get started."
    _widget_debug(
        f"show_pdf_tools called user_intent={user_intent!r} message_present={message is not None}"
    )
    response = {
        "success": True,
        "widget": {
            "uri": PDF_TOOLS_WIDGET_TEMPLATE_URI,
            "domain": "pdf-tools",
            "accessible": True
        },
        "supported_file_types": [
            "PDF documents",
            "Microsoft Office documents (Word, Excel, PowerPoint)",
            "text files",
            "images (PNG, JPEG, TIFF, BMP, GIF)",
            "HTML files"
        ],
        "message": display_message,
        "user_intent": user_intent,
        "max_file_size": "100MB",
        "next_steps": [
            "1. Drag and drop or click to upload your PDF document",
            "2. Call mcp tools according to 'user_intent' after upload is complete",
        ]
    }

    _widget_debug(
        f"show_pdf_tools returning widget_uri={response['widget']['uri']} next_steps={len(response['next_steps'])}"
    )

    return json.dumps(response, ensure_ascii=False, indent=2)

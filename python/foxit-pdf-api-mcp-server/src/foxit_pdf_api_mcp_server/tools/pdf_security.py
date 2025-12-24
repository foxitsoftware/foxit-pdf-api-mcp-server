"""PDF security tools: protect and remove password protection."""

from typing import Optional

from ..server import client, mcp
from ..utils import execute_and_wait
from ._base import format_error_response, format_success_response


@mcp.tool()
async def pdf_protect(
    document_id: str,
    user_password: Optional[str] = None,
    owner_password: Optional[str] = None,
    allow_printing: bool = True,
    allow_copying: bool = True,
    allow_editing: bool = True,
) -> str:
    """
    Add password protection and permissions to a PDF document.

    Features:
    - User password: Required to open the document
    - Owner password: Required to change permissions
    - Granular permissions control
    - Strong encryption (128-bit or 256-bit)

    Password types:
    - User password: Required to view the PDF
    - Owner password: Required to change restrictions (can also open the PDF)

    Permissions:
    - Printing: Allow/deny printing
    - Copying: Allow/deny text and image copying
    - Editing: Allow/deny content modification

    Maximum file size: 100MB

    Args:
        document_id: Document ID of the PDF to protect
        user_password: Password required to open the PDF (optional)
        owner_password: Password required to change permissions (optional)
        allow_printing: Allow printing (default: True)
        allow_copying: Allow copying content (default: True)
        allow_editing: Allow editing content (default: True)

    Returns:
        JSON string with success status, taskId, and resultDocumentId
    """
    try:
        config = {
            "permissions": {
                "printing": allow_printing,
                "copying": allow_copying,
                "editing": allow_editing,
            }
        }

        if user_password:
            config["userPassword"] = user_password
        if owner_password:
            config["ownerPassword"] = owner_password

        result = await execute_and_wait(client, lambda: client.pdf_protect(document_id, config))

        return format_success_response(
            task_id=result.get("taskId", ""),
            result_document_id=result.get("resultDocumentId"),
            message=f"PDF protected successfully. Download using documentId: {result.get('resultDocumentId')}",
        )
    except Exception as error:
        return format_error_response(error)


@mcp.tool()
async def pdf_remove_password(document_id: str, password: str) -> str:
    """
    Remove password protection from a PDF document.

    Requirements:
    - You must provide the correct password (user or owner)
    - Only works if you know the password

    Use cases:
    - Remove restrictions from your own PDFs
    - Unlock PDFs for processing
    - Prepare PDFs for archiving

    Maximum file size: 100MB

    Args:
        document_id: Document ID of the password-protected PDF
        password: The user or owner password for the PDF

    Returns:
        JSON string with success status, taskId, and resultDocumentId
    """
    try:
        result = await execute_and_wait(
            client, lambda: client.pdf_remove_password(document_id, password)
        )

        return format_success_response(
            task_id=result.get("taskId", ""),
            result_document_id=result.get("resultDocumentId"),
            message=f"Password removed successfully. Download using documentId: {result.get('resultDocumentId')}",
        )
    except Exception as error:
        return format_error_response(error)

"""PDF security tools: protect and remove password protection."""

import json
from typing import Optional

from ..server import client, mcp
from ..utils import execute_and_wait


def _error_payload(error: Exception, default_code: str) -> str:
    return json.dumps(
        {
            "success": False,
            "error": str(error),
            "code": getattr(error, "code", default_code),
            **({"taskId": getattr(error, "task_id")} if hasattr(error, "task_id") else {}),
        }
    )


@mcp.tool()
async def pdf_protect(
    documentId: str,
    user_password: Optional[str] = None,
    owner_password: Optional[str] = None,
    permissions: Optional[list[str]] = None,
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
        documentId: Document ID of the PDF to protect
        user_password: Password required to open the PDF (optional)
        owner_password: Password required to change permissions (optional)
        permissions: Array of permissions to grant (e.g., ["PRINT", "COPY_CONTENT"])

    Returns:
        JSON string with success status, taskId, and resultDocumentId
    """
    try:
        config: dict[str, object] = {
            "userPassword": user_password,
            "ownerPassword": owner_password,
            "permissions": permissions,
        }

        result = await execute_and_wait(client, lambda: client.pdf_protect(documentId, config))

        return json.dumps(
            {
                "success": True,
                "taskId": result["taskId"],
                "resultDocumentId": result.get("resultDocumentId"),
                "protection": {
                    "hasUserPassword": bool(user_password),
                    "hasOwnerPassword": bool(owner_password),
                    "permissions": permissions or [],
                },
                "message": (
                    "PDF protected successfully. Download using documentId: "
                    f"{result.get('resultDocumentId')}"
                ),
            }
        )
    except Exception as error:
        return _error_payload(error, "PROTECT_FAILED")


@mcp.tool()
async def pdf_remove_password(documentId: str, password: str) -> str:
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
        documentId: Document ID of the password-protected PDF
        password: The user or owner password for the PDF

    Returns:
        JSON string with success status, taskId, and resultDocumentId
    """
    try:
        result = await execute_and_wait(
            client, lambda: client.pdf_remove_password(documentId, password)
        )

        return json.dumps(
            {
                "success": True,
                "taskId": result["taskId"],
                "resultDocumentId": result.get("resultDocumentId"),
                "message": (
                    "Password removed successfully. Download using documentId: "
                    f"{result.get('resultDocumentId')}"
                ),
            }
        )
    except Exception as error:
        return _error_payload(error, "REMOVE_PASSWORD_FAILED")

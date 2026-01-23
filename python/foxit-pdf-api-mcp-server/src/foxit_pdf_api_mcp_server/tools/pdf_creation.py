"""PDF creation tools: convert various formats to PDF."""

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
async def pdf_from_word(documentId: str) -> str:
    """
    Convert a Microsoft Word document to PDF format.

    Supported formats: .doc, .docx, .rtf, .dot, .dotx, .docm, .dotm, .wpd

    Features:
    - Preserves text formatting and styles
    - Maintains tables and images
    - Keeps headers and footers
    - Preserves page breaks and sections

    Maximum file size: 100MB

    Workflow:
    1. Upload Word document using upload_document tool
    2. Call this tool with the documentId
    3. Wait for conversion to complete
    4. Download result using download_document tool with the returned documentId

    Args:
        documentId: Document ID of the uploaded Word file

    Returns:
        JSON string with success status, taskId, and resultDocumentId
    """
    try:
        result = await execute_and_wait(client, lambda: client.pdf_from_word(documentId))

        return json.dumps(
            {
                "success": True,
                "taskId": result["taskId"],
                "resultDocumentId": result.get("resultDocumentId"),
                "message": (
                    "Word document converted to PDF successfully. Download using documentId: "
                    f"{result.get('resultDocumentId')}"
                ),
            }
        )
    except Exception as error:
        return _error_payload(error, "CONVERSION_FAILED")


@mcp.tool()
async def pdf_from_excel(documentId: str) -> str:
    """
    Convert a Microsoft Excel spreadsheet to PDF format.

    Supported formats: .xls, .xlsx, .xlsm, .xlsb

    Features:
    - Preserves cell formatting and formulas
    - Maintains charts and graphs
    - Keeps multiple sheets (each as separate page)
    - Preserves print settings

    Maximum file size: 100MB

    Args:
        documentId: Document ID of the uploaded Excel file

    Returns:
        JSON string with success status, taskId, and resultDocumentId
    """
    try:
        result = await execute_and_wait(client, lambda: client.pdf_from_excel(documentId))

        return json.dumps(
            {
                "success": True,
                "taskId": result["taskId"],
                "resultDocumentId": result.get("resultDocumentId"),
                "message": (
                    "Excel document converted to PDF successfully. Download using documentId: "
                    f"{result.get('resultDocumentId')}"
                ),
            }
        )
    except Exception as error:
        return _error_payload(error, "CONVERSION_FAILED")


@mcp.tool()
async def pdf_from_ppt(documentId: str) -> str:
    """
    Convert a Microsoft PowerPoint presentation to PDF format.

    Supported formats: .ppt, .pptx, .pptm, .ppsx

    Features:
    - Preserves slide layouts and formatting
    - Maintains animations (as static images)
    - Keeps notes and comments
    - One slide per PDF page

    Maximum file size: 100MB

    Args:
        documentId: Document ID of the uploaded PowerPoint file

    Returns:
        JSON string with success status, taskId, and resultDocumentId
    """
    try:
        result = await execute_and_wait(client, lambda: client.pdf_from_ppt(documentId))

        return json.dumps(
            {
                "success": True,
                "taskId": result["taskId"],
                "resultDocumentId": result.get("resultDocumentId"),
                "message": (
                    "PowerPoint document converted to PDF successfully. Download using documentId: "
                    f"{result.get('resultDocumentId')}"
                ),
            }
        )
    except Exception as error:
        return _error_payload(error, "CONVERSION_FAILED")


@mcp.tool()
async def pdf_from_text(documentId: str) -> str:
    """
    Convert a plain text file to PDF format.

    Supported formats: .txt

    Features:
    - Preserves text content
    - Uses standard font and formatting
    - Automatic page breaks
    - UTF-8 encoding support

    Maximum file size: 100MB

    Args:
        documentId: Document ID of the uploaded text file

    Returns:
        JSON string with success status, taskId, and resultDocumentId
    """
    try:
        result = await execute_and_wait(client, lambda: client.pdf_from_text(documentId))

        return json.dumps(
            {
                "success": True,
                "taskId": result["taskId"],
                "resultDocumentId": result.get("resultDocumentId"),
                "message": (
                    "Text file converted to PDF successfully. Download using documentId: "
                    f"{result.get('resultDocumentId')}"
                ),
            }
        )
    except Exception as error:
        return _error_payload(error, "CONVERSION_FAILED")


@mcp.tool()
async def pdf_from_image(documentId: str) -> str:
    """
    Convert an image to PDF format.

    Supported formats: .jpg, .jpeg, .png, .gif, .bmp, .tiff

    Features:
    - Preserves image quality
    - Automatic page sizing to fit image
    - Supports multiple images (one per page)
    - Maintains aspect ratio

    Maximum file size: 100MB

    Args:
        documentId: Document ID of the uploaded image file

    Returns:
        JSON string with success status, taskId, and resultDocumentId
    """
    try:
        result = await execute_and_wait(client, lambda: client.pdf_from_image(documentId))

        return json.dumps(
            {
                "success": True,
                "taskId": result["taskId"],
                "resultDocumentId": result.get("resultDocumentId"),
                "message": (
                    "Image converted to PDF successfully. Download using documentId: "
                    f"{result.get('resultDocumentId')}"
                ),
            }
        )
    except Exception as error:
        return _error_payload(error, "CONVERSION_FAILED")


@mcp.tool()
async def pdf_from_html(
    documentId: str,
    config: Optional[dict[str, object]] = None,
) -> str:
    """
    Convert an HTML file to PDF format.

    Features:
    - Renders HTML with CSS styling
    - Supports embedded images
    - Preserves hyperlinks
    - Automatic page breaks

    Maximum file size: 100MB

    Args:
        documentId: Document ID of the uploaded HTML file
        config: Optional configuration (dimension/rotation/pageMode/scalingMode)

    Returns:
        JSON string with success status, taskId, and resultDocumentId
    """
    try:
        result = await execute_and_wait(
            client, lambda: client.pdf_from_html(documentId, config if config else None)
        )

        return json.dumps(
            {
                "success": True,
                "taskId": result["taskId"],
                "resultDocumentId": result.get("resultDocumentId"),
                "message": (
                    "HTML converted to PDF successfully. Download using documentId: "
                    f"{result.get('resultDocumentId')}"
                ),
            }
        )
    except Exception as error:
        return _error_payload(error, "CONVERSION_FAILED")


@mcp.tool()
async def pdf_from_url(
    url: str,
    config: Optional[dict[str, object]] = None,
) -> str:
    """
    Convert a web page from URL to PDF format.

    Features:
    - Renders live web pages
    - Includes CSS styling and images
    - Preserves hyperlinks
    - Automatic page breaks
    - JavaScript execution (limited)

    Args:
        url: The URL of the web page to convert (must be publicly accessible)
        config: Optional configuration (dimension/rotation/pageMode/scalingMode)

    Returns:
        JSON string with success status, taskId, and resultDocumentId
    """
    try:
        result = await execute_and_wait(
            client, lambda: client.pdf_from_url(url, config if config else None)
        )

        return json.dumps(
            {
                "success": True,
                "taskId": result["taskId"],
                "resultDocumentId": result.get("resultDocumentId"),
                "message": (
                    "URL converted to PDF successfully. Download using documentId: "
                    f"{result.get('resultDocumentId')}"
                ),
            }
        )
    except Exception as error:
        return _error_payload(error, "CONVERSION_FAILED")

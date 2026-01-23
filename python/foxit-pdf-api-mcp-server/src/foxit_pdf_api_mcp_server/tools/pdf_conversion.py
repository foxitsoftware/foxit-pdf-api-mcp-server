"""PDF conversion tools: convert PDF to various formats."""

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
async def pdf_to_word(documentId: str, password: Optional[str] = None) -> str:
    """
    Convert PDF to Microsoft Word format.

    Output format: .docx

    Features:
    - Preserves text formatting
    - Maintains tables and images
    - Keeps page layout structure
    - Editable Word document

    Maximum file size: 100MB

    Workflow:
    1. Upload PDF using upload_document tool
    2. Call this tool with the documentId
    3. Wait for conversion to complete
    4. Download result using download_document tool with the returned documentId

    Args:
        documentId: Document ID of the uploaded PDF file
        password: Password if PDF is password-protected

    Returns:
        JSON string with success status, taskId, and resultDocumentId
    """
    try:
        result = await execute_and_wait(client, lambda: client.pdf_to_word(documentId, password))

        return json.dumps(
            {
                "success": True,
                "taskId": result["taskId"],
                "resultDocumentId": result.get("resultDocumentId"),
                "message": (
                    "PDF converted to Word successfully. Download using documentId: "
                    f"{result.get('resultDocumentId')}"
                ),
            }
        )
    except Exception as error:
        return _error_payload(error, "CONVERSION_FAILED")


@mcp.tool()
async def pdf_to_excel(documentId: str, password: Optional[str] = None) -> str:
    """
    Convert PDF to Microsoft Excel format.

    Output format: .xlsx

    Features:
    - Extracts tables and data
    - Preserves cell formatting
    - Multiple sheets for multi-page PDFs
    - Editable spreadsheet

    Best for: PDFs containing tabular data

    Maximum file size: 100MB

    Args:
        documentId: Document ID of the uploaded PDF file
        password: Password if PDF is password-protected

    Returns:
        JSON string with success status, taskId, and resultDocumentId
    """
    try:
        result = await execute_and_wait(client, lambda: client.pdf_to_excel(documentId, password))

        return json.dumps(
            {
                "success": True,
                "taskId": result["taskId"],
                "resultDocumentId": result.get("resultDocumentId"),
                "message": (
                    "PDF converted to Excel successfully. Download using documentId: "
                    f"{result.get('resultDocumentId')}"
                ),
            }
        )
    except Exception as error:
        return _error_payload(error, "CONVERSION_FAILED")


@mcp.tool()
async def pdf_to_ppt(documentId: str, password: Optional[str] = None) -> str:
    """
    Convert PDF to Microsoft PowerPoint format.

    Output format: .pptx

    Features:
    - One slide per PDF page
    - Preserves images and graphics
    - Maintains basic layout
    - Editable presentation

    Maximum file size: 100MB

    Args:
        documentId: Document ID of the uploaded PDF file
        password: Password if PDF is password-protected

    Returns:
        JSON string with success status, taskId, and resultDocumentId
    """
    try:
        result = await execute_and_wait(client, lambda: client.pdf_to_ppt(documentId, password))

        return json.dumps(
            {
                "success": True,
                "taskId": result["taskId"],
                "resultDocumentId": result.get("resultDocumentId"),
                "message": (
                    "PDF converted to PowerPoint successfully. Download using documentId: "
                    f"{result.get('resultDocumentId')}"
                ),
            }
        )
    except Exception as error:
        return _error_payload(error, "CONVERSION_FAILED")


@mcp.tool()
async def pdf_to_text(
    documentId: str,
    password: Optional[str] = None,
) -> str:
    """
    Convert PDF to plain text format.

    Output format: .txt

    Features:
    - Extracts all text content
    - Preserves text order
    - UTF-8 encoding
    - Optional page range selection

    Maximum file size: 100MB

    Args:
        documentId: Document ID of the uploaded PDF file
        password: Password if PDF is password-protected

    Returns:
        JSON string with success status, taskId, and resultDocumentId
    """
    try:
        result = await execute_and_wait(client, lambda: client.pdf_to_text(documentId, password))

        return json.dumps(
            {
                "success": True,
                "taskId": result["taskId"],
                "resultDocumentId": result.get("resultDocumentId"),
                "message": (
                    "PDF converted to text successfully. Download using documentId: "
                    f"{result.get('resultDocumentId')}"
                ),
            }
        )
    except Exception as error:
        return _error_payload(error, "CONVERSION_FAILED")


@mcp.tool()
async def pdf_to_html(documentId: str, password: Optional[str] = None) -> str:
    """
    Convert PDF to HTML format.

    Output format: .html

    Features:
    - Preserves text and formatting
    - Maintains hyperlinks
    - Includes images
    - Responsive HTML output

    Maximum file size: 100MB

    Args:
        documentId: Document ID of the uploaded PDF file
        password: Password if PDF is password-protected

    Returns:
        JSON string with success status, taskId, and resultDocumentId
    """
    try:
        result = await execute_and_wait(client, lambda: client.pdf_to_html(documentId, password))

        return json.dumps(
            {
                "success": True,
                "taskId": result["taskId"],
                "resultDocumentId": result.get("resultDocumentId"),
                "message": (
                    "PDF converted to HTML successfully. Download using documentId: "
                    f"{result.get('resultDocumentId')}"
                ),
            }
        )
    except Exception as error:
        return _error_payload(error, "CONVERSION_FAILED")


@mcp.tool()
async def pdf_to_image(
    documentId: str,
    config: Optional[dict[str, object]] = None,
    password: Optional[str] = None,
) -> str:
    """
    Convert PDF pages to images.

    Output formats: .jpg, .png, .tiff (returned as .zip for multiple pages)

    Features:
    - High-quality image rendering
    - Optional page range selection
    - Configurable DPI/resolution
    - Multiple format support

    Maximum file size: 100MB

    Args:
        documentId: Document ID of the uploaded PDF file
        config: Image conversion configuration
        password: Password if PDF is password-protected

    Returns:
        JSON string with success status, taskId, and resultDocumentId
        Note: Result is a ZIP file containing the images
    """
    try:
        result = await execute_and_wait(
            client, lambda: client.pdf_to_image(documentId, config, password)
        )

        return json.dumps(
            {
                "success": True,
                "taskId": result["taskId"],
                "resultDocumentId": result.get("resultDocumentId"),
                "config": config,
                "message": (
                    "PDF converted to image(s) successfully. Download using documentId: "
                    f"{result.get('resultDocumentId')}"
                ),
            }
        )
    except Exception as error:
        return _error_payload(error, "CONVERSION_FAILED")

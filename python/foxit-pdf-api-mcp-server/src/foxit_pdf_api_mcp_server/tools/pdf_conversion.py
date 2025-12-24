"""PDF conversion tools: convert PDF to various formats."""

from typing import Optional

from ..server import client, mcp
from ..utils import execute_and_wait
from ._base import format_error_response, format_success_response


@mcp.tool()
async def pdf_to_word(document_id: str) -> str:
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
        document_id: Document ID of the uploaded PDF file

    Returns:
        JSON string with success status, taskId, and resultDocumentId
    """
    try:
        result = await execute_and_wait(client, lambda: client.pdf_to_word(document_id))

        return format_success_response(
            task_id=result.get("taskId", ""),
            result_document_id=result.get("resultDocumentId"),
            message=f"PDF converted to Word successfully. Download using documentId: {result.get('resultDocumentId')}",
        )
    except Exception as error:
        return format_error_response(error)


@mcp.tool()
async def pdf_to_excel(document_id: str) -> str:
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
        document_id: Document ID of the uploaded PDF file

    Returns:
        JSON string with success status, taskId, and resultDocumentId
    """
    try:
        result = await execute_and_wait(client, lambda: client.pdf_to_excel(document_id))

        return format_success_response(
            task_id=result.get("taskId", ""),
            result_document_id=result.get("resultDocumentId"),
            message=f"PDF converted to Excel successfully. Download using documentId: {result.get('resultDocumentId')}",
        )
    except Exception as error:
        return format_error_response(error)


@mcp.tool()
async def pdf_to_ppt(document_id: str) -> str:
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
        document_id: Document ID of the uploaded PDF file

    Returns:
        JSON string with success status, taskId, and resultDocumentId
    """
    try:
        result = await execute_and_wait(client, lambda: client.pdf_to_ppt(document_id))

        return format_success_response(
            task_id=result.get("taskId", ""),
            result_document_id=result.get("resultDocumentId"),
            message=f"PDF converted to PowerPoint successfully. Download using documentId: {result.get('resultDocumentId')}",
        )
    except Exception as error:
        return format_error_response(error)


@mcp.tool()
async def pdf_to_text(
    document_id: str,
    page_range: Optional[str] = None,
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
        document_id: Document ID of the uploaded PDF file
        page_range: Optional page range (e.g., "1,3,5-10", "all", "even", "odd")

    Returns:
        JSON string with success status, taskId, and resultDocumentId
    """
    try:
        config = {}
        if page_range:
            config["pageRange"] = page_range

        result = await execute_and_wait(
            client, lambda: client.pdf_to_text(document_id, config if config else None)
        )

        return format_success_response(
            task_id=result.get("taskId", ""),
            result_document_id=result.get("resultDocumentId"),
            message=f"PDF converted to text successfully. Download using documentId: {result.get('resultDocumentId')}",
        )
    except Exception as error:
        return format_error_response(error)


@mcp.tool()
async def pdf_to_html(document_id: str) -> str:
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
        document_id: Document ID of the uploaded PDF file

    Returns:
        JSON string with success status, taskId, and resultDocumentId
    """
    try:
        result = await execute_and_wait(client, lambda: client.pdf_to_html(document_id))

        return format_success_response(
            task_id=result.get("taskId", ""),
            result_document_id=result.get("resultDocumentId"),
            message=f"PDF converted to HTML successfully. Download using documentId: {result.get('resultDocumentId')}",
        )
    except Exception as error:
        return format_error_response(error)


@mcp.tool()
async def pdf_to_image(
    document_id: str,
    page_range: Optional[str] = None,
    image_format: Optional[str] = None,
    dpi: Optional[int] = None,
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
        document_id: Document ID of the uploaded PDF file
        page_range: Optional page range (e.g., "1,3,5-10", "all", "even", "odd")
        image_format: Output format ("jpg", "png", "tiff", default: "jpg")
        dpi: Resolution in DPI (default: 150, max: 300)

    Returns:
        JSON string with success status, taskId, and resultDocumentId
        Note: Result is a ZIP file containing the images
    """
    try:
        config = {}
        if page_range:
            config["pageRange"] = page_range
        if image_format:
            config["format"] = image_format
        if dpi:
            config["dpi"] = dpi

        result = await execute_and_wait(
            client, lambda: client.pdf_to_image(document_id, config if config else None)
        )

        return format_success_response(
            task_id=result.get("taskId", ""),
            result_document_id=result.get("resultDocumentId"),
            message=f"PDF converted to images successfully. Download ZIP file using documentId: {result.get('resultDocumentId')}",
        )
    except Exception as error:
        return format_error_response(error)

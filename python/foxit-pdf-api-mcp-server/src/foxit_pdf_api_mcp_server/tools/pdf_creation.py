"""PDF creation tools: convert various formats to PDF."""

from typing import Optional

from ..server import client, mcp
from ..utils import execute_and_wait
from ._base import format_error_response, format_success_response


@mcp.tool()
async def pdf_from_word(document_id: str) -> str:
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
        document_id: Document ID of the uploaded Word file

    Returns:
        JSON string with success status, taskId, and resultDocumentId
    """
    try:
        result = await execute_and_wait(client, lambda: client.pdf_from_word(document_id))

        return format_success_response(
            task_id=result.get("taskId", ""),
            result_document_id=result.get("resultDocumentId"),
            message=f"Word document converted to PDF successfully. Download using documentId: {result.get('resultDocumentId')}",
        )
    except Exception as error:
        return format_error_response(error)


@mcp.tool()
async def pdf_from_excel(document_id: str) -> str:
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
        document_id: Document ID of the uploaded Excel file

    Returns:
        JSON string with success status, taskId, and resultDocumentId
    """
    try:
        result = await execute_and_wait(client, lambda: client.pdf_from_excel(document_id))

        return format_success_response(
            task_id=result.get("taskId", ""),
            result_document_id=result.get("resultDocumentId"),
            message=f"Excel document converted to PDF successfully. Download using documentId: {result.get('resultDocumentId')}",
        )
    except Exception as error:
        return format_error_response(error)


@mcp.tool()
async def pdf_from_ppt(document_id: str) -> str:
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
        document_id: Document ID of the uploaded PowerPoint file

    Returns:
        JSON string with success status, taskId, and resultDocumentId
    """
    try:
        result = await execute_and_wait(client, lambda: client.pdf_from_ppt(document_id))

        return format_success_response(
            task_id=result.get("taskId", ""),
            result_document_id=result.get("resultDocumentId"),
            message=f"PowerPoint document converted to PDF successfully. Download using documentId: {result.get('resultDocumentId')}",
        )
    except Exception as error:
        return format_error_response(error)


@mcp.tool()
async def pdf_from_text(document_id: str) -> str:
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
        document_id: Document ID of the uploaded text file

    Returns:
        JSON string with success status, taskId, and resultDocumentId
    """
    try:
        result = await execute_and_wait(client, lambda: client.pdf_from_text(document_id))

        return format_success_response(
            task_id=result.get("taskId", ""),
            result_document_id=result.get("resultDocumentId"),
            message=f"Text file converted to PDF successfully. Download using documentId: {result.get('resultDocumentId')}",
        )
    except Exception as error:
        return format_error_response(error)


@mcp.tool()
async def pdf_from_image(document_id: str) -> str:
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
        document_id: Document ID of the uploaded image file

    Returns:
        JSON string with success status, taskId, and resultDocumentId
    """
    try:
        result = await execute_and_wait(client, lambda: client.pdf_from_image(document_id))

        return format_success_response(
            task_id=result.get("taskId", ""),
            result_document_id=result.get("resultDocumentId"),
            message=f"Image converted to PDF successfully. Download using documentId: {result.get('resultDocumentId')}",
        )
    except Exception as error:
        return format_error_response(error)


@mcp.tool()
async def pdf_from_html(
    document_id: str,
    page_width: Optional[int] = None,
    page_height: Optional[int] = None,
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
        document_id: Document ID of the uploaded HTML file
        page_width: Page width in points (optional, default: 595 for A4)
        page_height: Page height in points (optional, default: 842 for A4)

    Returns:
        JSON string with success status, taskId, and resultDocumentId
    """
    try:
        config = {}
        if page_width or page_height:
            config["dimension"] = {}
            if page_width:
                config["dimension"]["width"] = str(page_width)
            if page_height:
                config["dimension"]["height"] = str(page_height)

        result = await execute_and_wait(
            client, lambda: client.pdf_from_html(document_id, config if config else None)
        )

        return format_success_response(
            task_id=result.get("taskId", ""),
            result_document_id=result.get("resultDocumentId"),
            message=f"HTML converted to PDF successfully. Download using documentId: {result.get('resultDocumentId')}",
        )
    except Exception as error:
        return format_error_response(error)


@mcp.tool()
async def pdf_from_url(
    url: str,
    page_width: Optional[int] = None,
    page_height: Optional[int] = None,
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
        page_width: Page width in points (optional, default: 595 for A4)
        page_height: Page height in points (optional, default: 842 for A4)

    Returns:
        JSON string with success status, taskId, and resultDocumentId
    """
    try:
        config = {}
        if page_width or page_height:
            config["dimension"] = {}
            if page_width:
                config["dimension"]["width"] = str(page_width)
            if page_height:
                config["dimension"]["height"] = str(page_height)

        result = await execute_and_wait(
            client, lambda: client.pdf_from_url(url, config if config else None)
        )

        return format_success_response(
            task_id=result.get("taskId", ""),
            result_document_id=result.get("resultDocumentId"),
            message=f"URL converted to PDF successfully. Download using documentId: {result.get('resultDocumentId')}",
        )
    except Exception as error:
        return format_error_response(error)

"""PDF conversion tools: convert PDF to various formats."""

from typing import Optional

from ..resources import client, mcp
from ._base import format_error_response, format_task_submitted_response, register_task


WRITE_TOOL_ANNOTATIONS = {"readOnlyHint": False, "destructiveHint": False}


@mcp.tool(annotations=WRITE_TOOL_ANNOTATIONS)
async def pdf_to_word(document_id: str, password: str | None = None) -> str:
    """
    ⚠️ CRITICAL PREREQUISITE: You MUST call show_pdf_tools first to display the upload widget.
    The document_id parameter comes from the upload response in the widget.
    Convert PDF to Microsoft Word format.

    Output format: .docx

    Features:
    - Preserves text formatting
    - Maintains tables and images
    - Keeps page layout structure
    - Editable Word document

    Maximum file size: 100MB

    This operation runs asynchronously. The tool returns a taskId immediately.
    Use get_task_result to poll for completion and retrieve the download link.

    Password-protected PDFs:
    - If the PDF is password-protected, provide the password via the password parameter
    - Without a valid password, the operation will fail with an authentication error

    Args:
        document_id: Document ID of the uploaded PDF file
        password: Password for password-protected PDFs. Optional. Provide only if the PDF requires a password.

    Returns:
        JSON string with:
        - success: operation was submitted successfully
        - taskId: use with get_task_result to check status and retrieve the result
        - message: describes next steps
    """
    try:
        result = await client.pdf_to_word(document_id, password=password)
        task_id = result["taskId"]
        register_task(task_id, "pdf_to_word", "PDF converted to Word successfully.")
        return format_task_submitted_response(
            task_id,
            "PDF to Word conversion submitted. Use get_task_result to check status and retrieve the download link.",
        )
    except Exception as error:
        return format_error_response(error)


@mcp.tool(annotations=WRITE_TOOL_ANNOTATIONS)
async def pdf_to_excel(document_id: str, password: str | None = None) -> str:
    """
    ⚠️ CRITICAL PREREQUISITE: You MUST call show_pdf_tools first to display the upload widget.
    The document_id parameter comes from the upload response in the widget.

    Convert PDF to Microsoft Excel format.

    Output format: .xlsx

    Features:
    - Extracts tables and data
    - Preserves cell formatting
    - Multiple sheets for multi-page PDFs
    - Editable spreadsheet

    Best for: PDFs containing tabular data

    Maximum file size: 100MB

    Password-protected PDFs:
    - If the PDF is password-protected, provide the password via the password parameter
    - Without a valid password, the operation will fail with an authentication error

    This operation runs asynchronously. The tool returns a taskId immediately.
    Use get_task_result to poll for completion and retrieve the download link.

    Args:
        document_id: Document ID of the uploaded PDF file
        password: Password for password-protected PDFs. Optional. Provide only if the PDF requires a password.

    Returns:
        JSON string with:
        - success: operation was submitted successfully
        - taskId: use with get_task_result to check status and retrieve the result
        - message: describes next steps
    """
    try:
        result = await client.pdf_to_excel(document_id, password=password)
        task_id = result["taskId"]
        register_task(task_id, "pdf_to_excel", "PDF converted to Excel successfully.")
        return format_task_submitted_response(
            task_id,
            "PDF to Excel conversion submitted. Use get_task_result to check status and retrieve the download link.",
        )
    except Exception as error:
        return format_error_response(error)


@mcp.tool(annotations=WRITE_TOOL_ANNOTATIONS)
async def pdf_to_ppt(document_id: str, password: str | None = None) -> str:
    """
    ⚠️ CRITICAL PREREQUISITE: You MUST call show_pdf_tools first to display the upload widget.
    The document_id parameter comes from the upload response in the widget.

    Convert PDF to Microsoft PowerPoint format.

    Output format: .pptx

    Features:
    - One slide per PDF page
    - Preserves images and graphics
    - Maintains basic layout
    - Editable presentation

    Maximum file size: 100MB

    Password-protected PDFs:
    - If the PDF is password-protected, provide the password via the password parameter
    - Without a valid password, the operation will fail with an authentication error

    This operation runs asynchronously. The tool returns a taskId immediately.
    Use get_task_result to poll for completion and retrieve the download link.

    Args:
        document_id: Document ID of the uploaded PDF file
        password: Password for password-protected PDFs. Optional. Provide only if the PDF requires a password.

    Returns:
        JSON string with:
        - success: operation was submitted successfully
        - taskId: use with get_task_result to check status and retrieve the result
        - message: describes next steps
    """
    try:
        result = await client.pdf_to_ppt(document_id, password=password)
        task_id = result["taskId"]
        register_task(task_id, "pdf_to_ppt", "PDF converted to PowerPoint successfully.")
        return format_task_submitted_response(
            task_id,
            "PDF to PowerPoint conversion submitted. Use get_task_result to check status and retrieve the download link.",
        )
    except Exception as error:
        return format_error_response(error)


@mcp.tool(annotations=WRITE_TOOL_ANNOTATIONS)
async def pdf_to_text(
    document_id: str,
    page_range: Optional[str] = None,
    password: str | None = None,
) -> str:
    """
    ⚠️ CRITICAL PREREQUISITE: You MUST call show_pdf_tools first to display the upload widget.
    The document_id parameter comes from the upload response in the widget.

    Convert PDF to plain text format.

    Output format: .txt

    Features:
    - Extracts all text content
    - Preserves text order
    - UTF-8 encoding
    - Optional page range selection

    Maximum file size: 100MB

    Password-protected PDFs:
    - If the PDF is password-protected, provide the password via the password parameter
    - Without a valid password, the operation will fail with an authentication error

    This operation runs asynchronously. The tool returns a taskId immediately.
    Use get_task_result to poll for completion and retrieve the download link.

    Args:
        document_id: Document ID of the uploaded PDF file
        page_range: Optional page range (e.g., "1,3,5-10", "all", "even", "odd")
        password: Password for password-protected PDFs. Optional. Provide only if the PDF requires a password.

    Returns:
        JSON string with:
        - success: operation was submitted successfully
        - taskId: use with get_task_result to check status and retrieve the result
        - message: describes next steps
    """
    try:
        config = {}
        if page_range:
            config["pageRange"] = page_range

        result = await client.pdf_to_text(
            document_id, config if config else None, password=password
        )
        task_id = result["taskId"]
        register_task(task_id, "pdf_to_text", "PDF converted to text successfully.")
        return format_task_submitted_response(
            task_id,
            "PDF to text conversion submitted. Use get_task_result to check status and retrieve the download link.",
        )
    except Exception as error:
        return format_error_response(error)


@mcp.tool(annotations=WRITE_TOOL_ANNOTATIONS)
async def pdf_to_html(document_id: str, password: str | None = None) -> str:
    """
    ⚠️ CRITICAL PREREQUISITE: You MUST call show_pdf_tools first to display the upload widget.
    The document_id parameter comes from the upload response in the widget.

    Convert PDF to HTML format.

    Output format: .html

    Features:
    - Preserves text and formatting
    - Maintains hyperlinks
    - Includes images
    - Responsive HTML output

    Maximum file size: 100MB

    Password-protected PDFs:
    - If the PDF is password-protected, provide the password via the password parameter
    - Without a valid password, the operation will fail with an authentication error

    This operation runs asynchronously. The tool returns a taskId immediately.
    Use get_task_result to poll for completion and retrieve the download link.

    Args:
        document_id: Document ID of the uploaded PDF file
        password: Password for password-protected PDFs. Optional. Provide only if the PDF requires a password.

    Returns:
        JSON string with:
        - success: operation was submitted successfully
        - taskId: use with get_task_result to check status and retrieve the result
        - message: describes next steps
    """
    try:
        result = await client.pdf_to_html(document_id, password=password)
        task_id = result["taskId"]
        register_task(task_id, "pdf_to_html", "PDF converted to HTML successfully.")
        return format_task_submitted_response(
            task_id,
            "PDF to HTML conversion submitted. Use get_task_result to check status and retrieve the download link.",
        )
    except Exception as error:
        return format_error_response(error)


@mcp.tool(annotations=WRITE_TOOL_ANNOTATIONS)
async def pdf_to_image(
    document_id: str,
    page_range: Optional[str] = None,
    image_format: Optional[str] = None,
    dpi: Optional[int] = None,
    password: str | None = None,
) -> str:
    """
    ⚠️ CRITICAL PREREQUISITE: You MUST call show_pdf_tools first to display the upload widget.
    The document_id parameter comes from the upload response in the widget.

    Convert PDF pages to images.

    Output formats: .jpg, .png, .tiff (returned as .zip for multiple pages)

    Features:
    - High-quality image rendering
    - Optional page range selection
    - Configurable DPI/resolution
    - Multiple format support

    Maximum file size: 100MB

    Password-protected PDFs:
    - If the PDF is password-protected, provide the password via the password parameter
    - Without a valid password, the operation will fail with an authentication error

    This operation runs asynchronously. The tool returns a taskId immediately.
    Use get_task_result to poll for completion and retrieve the download link.

    Args:
        document_id: Document ID of the uploaded PDF file
        page_range: Optional page range (e.g., "1,3,5-10", "all", "even", "odd")
        image_format: Output format ("jpg", "png", "tiff", default: "jpg")
        dpi: Resolution in DPI (default: 150, max: 300)
        password: Password for password-protected PDFs. Optional. Provide only if the PDF requires a password.

    Returns:
        JSON string with:
        - success: operation was submitted successfully
        - taskId: use with get_task_result to check status and retrieve the result
        - message: describes next steps
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

        result = await client.pdf_to_image(
            document_id, config if config else None, password=password
        )
        task_id = result["taskId"]
        register_task(task_id, "pdf_to_image", "PDF converted to images successfully.")
        return format_task_submitted_response(
            task_id,
            "PDF to image conversion submitted. Use get_task_result to check status and retrieve the download link.",
        )
    except Exception as error:
        return format_error_response(error)

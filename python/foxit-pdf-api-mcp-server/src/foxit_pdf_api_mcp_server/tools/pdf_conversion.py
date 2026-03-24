"""PDF conversion tools: convert PDF to various formats."""

import json
from typing import Optional

from ..resources import client, mcp
from ..utils import execute_and_wait
from ._base import format_error_response
from .share_link_helper import try_create_share_link


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

    Workflow:
    1. Upload PDF using upload_document tool
    2. Call this tool with the documentId
    3. Wait for conversion to complete
    4. The tool automatically creates a share link and returns it

    Password-protected PDFs:
    - If the PDF is password-protected, provide the password via the password parameter
    - Without a valid password, the operation will fail with an authentication error

    Args:
        document_id: Document ID of the uploaded PDF file
        password: Password for password-protected PDFs. Optional. Provide only if the PDF requires a password.

    Returns:
        JSON string with:
        - success, message
                - resultDocumentId: identifier of the converted result document, returned for
                    follow-up operations on the generated file
        - shareUrl: public download URL for the converted Word file, when available
        - expiresAt: link expiration timestamp, if provided by the API
    """
    try:
        result = await execute_and_wait(client, lambda: client.pdf_to_word(document_id, password=password))

        result_document_id = result.get("resultDocumentId")
        share = None
        if result_document_id:
            share, _ = await try_create_share_link(
                client.create_share_link,
                document_id=result_document_id,
                expiration_minutes=None,
                filename=None,
            )

        response = {
            "success": True,
            "message": "PDF converted to Word successfully. Display the download link as a hyperlink with the converted Word filename as the link text, not the raw URL."
            if (share or {}).get("shareUrl")
            else "PDF converted to Word successfully, but no share link was created.",
        }
        if result_document_id:
            response["resultDocumentId"] = result_document_id
        if (share or {}).get("shareUrl"):
            response["shareUrl"] = share.get("shareUrl")
        if (share or {}).get("expiresAt"):
            response["expiresAt"] = share.get("expiresAt")

        return json.dumps(response, indent=2)
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

    Args:
        document_id: Document ID of the uploaded PDF file
        password: Password for password-protected PDFs. Optional. Provide only if the PDF requires a password.

    Returns:
        JSON string with:
        - success, message
                - resultDocumentId: identifier of the converted result document, returned for
                    follow-up operations on the generated file
        - shareUrl: public download URL for the converted Excel file, when available
        - expiresAt: link expiration timestamp, if provided by the API
    """
    try:
        result = await execute_and_wait(client, lambda: client.pdf_to_excel(document_id, password=password))

        result_document_id = result.get("resultDocumentId")
        share = None
        if result_document_id:
            share, _ = await try_create_share_link(
                client.create_share_link,
                document_id=result_document_id,
                expiration_minutes=None,
                filename=None,
            )

        response = {
            "success": True,
            "message": "PDF converted to Excel successfully. Display the download link as a hyperlink with the converted Excel filename as the link text, not the raw URL."
            if (share or {}).get("shareUrl")
            else "PDF converted to Excel successfully, but no share link was created.",
        }
        if result_document_id:
            response["resultDocumentId"] = result_document_id
        if (share or {}).get("shareUrl"):
            response["shareUrl"] = share.get("shareUrl")
        if (share or {}).get("expiresAt"):
            response["expiresAt"] = share.get("expiresAt")

        return json.dumps(response, indent=2)
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

    Args:
        document_id: Document ID of the uploaded PDF file
        password: Password for password-protected PDFs. Optional. Provide only if the PDF requires a password.

    Returns:
        JSON string with:
        - success, message
                - resultDocumentId: identifier of the converted result document, returned for
                    follow-up operations on the generated file
        - shareUrl: public download URL for the converted PowerPoint file, when available
        - expiresAt: link expiration timestamp, if provided by the API
    """
    try:
        result = await execute_and_wait(client, lambda: client.pdf_to_ppt(document_id, password=password))

        result_document_id = result.get("resultDocumentId")
        share = None
        if result_document_id:
            share, _ = await try_create_share_link(
                client.create_share_link,
                document_id=result_document_id,
                expiration_minutes=None,
                filename=None,
            )

        response = {
            "success": True,
            "message": "PDF converted to PowerPoint successfully. Display the download link as a hyperlink with the converted PowerPoint filename as the link text, not the raw URL."
            if (share or {}).get("shareUrl")
            else "PDF converted to PowerPoint successfully, but no share link was created.",
        }
        if result_document_id:
            response["resultDocumentId"] = result_document_id
        if (share or {}).get("shareUrl"):
            response["shareUrl"] = share.get("shareUrl")
        if (share or {}).get("expiresAt"):
            response["expiresAt"] = share.get("expiresAt")

        return json.dumps(response, indent=2)
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

    Args:
        document_id: Document ID of the uploaded PDF file
        page_range: Optional page range (e.g., "1,3,5-10", "all", "even", "odd")
        password: Password for password-protected PDFs. Optional. Provide only if the PDF requires a password.

    Returns:
        JSON string with:
        - success, message
                - resultDocumentId: identifier of the converted result document, returned for
                    follow-up operations on the generated file
        - shareUrl: public download URL for the converted text file, when available
        - expiresAt: link expiration timestamp, if provided by the API
    """
    try:
        config = {}
        if page_range:
            config["pageRange"] = page_range

        result = await execute_and_wait(
            client, lambda: client.pdf_to_text(
                document_id, config if config else None, password=password)
        )

        result_document_id = result.get("resultDocumentId")
        share = None
        if result_document_id:
            share, _ = await try_create_share_link(
                client.create_share_link,
                document_id=result_document_id,
                expiration_minutes=None,
                filename=None,
            )

        response = {
            "success": True,
            "message": "PDF converted to text successfully. Display the download link as a hyperlink with the converted text filename as the link text, not the raw URL."
            if (share or {}).get("shareUrl")
            else "PDF converted to text successfully, but no share link was created.",
        }
        if result_document_id:
            response["resultDocumentId"] = result_document_id
        if (share or {}).get("shareUrl"):
            response["shareUrl"] = share.get("shareUrl")
        if (share or {}).get("expiresAt"):
            response["expiresAt"] = share.get("expiresAt")

        return json.dumps(response, indent=2)
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

    Args:
        document_id: Document ID of the uploaded PDF file
        password: Password for password-protected PDFs. Optional. Provide only if the PDF requires a password.

    Returns:
        JSON string with:
        - success, message
                - resultDocumentId: identifier of the converted result document, returned for
                    follow-up operations on the generated file
        - shareUrl: public download URL for the converted HTML file, when available
        - expiresAt: link expiration timestamp, if provided by the API
    """
    try:
        result = await execute_and_wait(client, lambda: client.pdf_to_html(document_id, password=password))

        result_document_id = result.get("resultDocumentId")
        share = None
        if result_document_id:
            share, _ = await try_create_share_link(
                client.create_share_link,
                document_id=result_document_id,
                expiration_minutes=None,
                filename=None,
            )

        response = {
            "success": True,
            "message": "PDF converted to HTML successfully. Display the download link as a hyperlink with the converted HTML filename as the link text, not the raw URL."
            if (share or {}).get("shareUrl")
            else "PDF converted to HTML successfully, but no share link was created.",
        }
        if result_document_id:
            response["resultDocumentId"] = result_document_id
        if (share or {}).get("shareUrl"):
            response["shareUrl"] = share.get("shareUrl")
        if (share or {}).get("expiresAt"):
            response["expiresAt"] = share.get("expiresAt")

        return json.dumps(response, indent=2)
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

    Args:
        document_id: Document ID of the uploaded PDF file
        page_range: Optional page range (e.g., "1,3,5-10", "all", "even", "odd")
        image_format: Output format ("jpg", "png", "tiff", default: "jpg")
        dpi: Resolution in DPI (default: 150, max: 300)
        password: Password for password-protected PDFs. Optional. Provide only if the PDF requires a password.

    Returns:
        JSON string with:
        - success, message
        - resultDocumentId: identifier of the converted result document, returned for follow-up operations on the generated file
        - shareUrl: public download URL for the converted image output, when available
        - expiresAt: link expiration timestamp, if provided by the API
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
            client, lambda: client.pdf_to_image(
                document_id, config if config else None, password=password)
        )

        result_document_id = result.get("resultDocumentId")
        share = None
        if result_document_id:
            share, _ = await try_create_share_link(
                client.create_share_link,
                document_id=result_document_id,
                expiration_minutes=None,
                filename=None,
            )

        response = {
            "success": True,
            "message": "PDF converted to images successfully. Display the download link as a hyperlink with the converted image archive filename as the link text, not the raw URL."
            if (share or {}).get("shareUrl")
            else "PDF converted to images successfully, but no share link was created.",
        }
        if result_document_id:
            response["resultDocumentId"] = result_document_id
        if (share or {}).get("shareUrl"):
            response["shareUrl"] = share.get("shareUrl")
        if (share or {}).get("expiresAt"):
            response["expiresAt"] = share.get("expiresAt")

        return json.dumps(response, indent=2)
    except Exception as error:
        return format_error_response(error)

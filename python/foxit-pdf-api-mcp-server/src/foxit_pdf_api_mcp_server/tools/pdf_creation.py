"""PDF creation tools: convert various formats to PDF."""

import json
from typing import Optional

from ..resources import client, mcp
from ..utils import execute_and_wait
from ._base import format_error_response
from .share_link_helper import try_create_share_link


WRITE_TOOL_ANNOTATIONS = {"readOnlyHint": False, "destructiveHint": False}

@mcp.tool(annotations=WRITE_TOOL_ANNOTATIONS)
async def pdf_from_word(document_id: str) -> str:
    """
    ⚠️ CRITICAL PREREQUISITE: You MUST call show_pdf_tools first to display the upload widget.
    The document_id parameter comes from the upload response in the widget.

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
    4. The tool automatically creates a share link and returns it

    Args:
        document_id: Document ID of the uploaded Word file

    Returns:
        JSON string with:
        - success, message
                - resultDocumentId: identifier of the converted result document, returned for
                    follow-up operations on the generated file
        - shareUrl: public download URL for the converted PDF, when available
        - expiresAt: link expiration timestamp, if provided by the API
    """
    try:
        result = await execute_and_wait(client, lambda: client.pdf_from_word(document_id))

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
            "message": "Word document converted to PDF successfully."
            if (share or {}).get("shareUrl")
            else "Word document converted to PDF successfully, but no share link was created.",
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
async def pdf_from_excel(document_id: str) -> str:
    """
    ⚠️ CRITICAL PREREQUISITE: You MUST call show_pdf_tools first to display the upload widget.
    The document_id parameter comes from the upload response in the widget.

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
        JSON string with:
        - success, message
                - resultDocumentId: identifier of the converted result document, returned for
                    follow-up operations on the generated file
        - shareUrl: public download URL for the converted PDF, when available
        - expiresAt: link expiration timestamp, if provided by the API
    """
    try:
        result = await execute_and_wait(client, lambda: client.pdf_from_excel(document_id))

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
            "message": "Excel document converted to PDF successfully."
            if (share or {}).get("shareUrl")
            else "Excel document converted to PDF successfully, but no share link was created.",
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
async def pdf_from_ppt(document_id: str) -> str:
    """
    ⚠️ CRITICAL PREREQUISITE: You MUST call show_pdf_tools first to display the upload widget.
    The document_id parameter comes from the upload response in the widget.

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
        JSON string with:
        - success, message
                - resultDocumentId: identifier of the converted result document, returned for
                    follow-up operations on the generated file
        - shareUrl: public download URL for the converted PDF, when available
        - expiresAt: link expiration timestamp, if provided by the API
    """
    try:
        result = await execute_and_wait(client, lambda: client.pdf_from_ppt(document_id))

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
            "message": "PowerPoint document converted to PDF successfully."
            if (share or {}).get("shareUrl")
            else "PowerPoint document converted to PDF successfully, but no share link was created.",
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
async def pdf_from_text(document_id: str) -> str:
    """
    ⚠️ CRITICAL PREREQUISITE: You MUST call show_pdf_tools first to display the upload widget.
    The document_id parameter comes from the upload response in the widget.

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
        JSON string with:
        - success, message
                - resultDocumentId: identifier of the converted result document, returned for
                    follow-up operations on the generated file
        - shareUrl: public download URL for the converted PDF, when available
        - expiresAt: link expiration timestamp, if provided by the API
    """
    try:
        result = await execute_and_wait(client, lambda: client.pdf_from_text(document_id))

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
            "message": "Text file converted to PDF successfully."
            if (share or {}).get("shareUrl")
            else "Text file converted to PDF successfully, but no share link was created.",
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
async def pdf_from_image(document_id: str) -> str:
    """
    ⚠️ CRITICAL PREREQUISITE: You MUST call show_pdf_tools first to display the upload widget.
    The document_id parameter comes from the upload response in the widget.

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
        JSON string with:
        - success, message
                - resultDocumentId: identifier of the converted result document, returned for
                    follow-up operations on the generated file
        - shareUrl: public download URL for the converted PDF, when available
        - expiresAt: link expiration timestamp, if provided by the API
    """
    try:
        result = await execute_and_wait(client, lambda: client.pdf_from_image(document_id))

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
            "message": "Image converted to PDF successfully."
            if (share or {}).get("shareUrl")
            else "Image converted to PDF successfully, but no share link was created.",
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
async def pdf_from_html(
    document_id: str,
    page_width: Optional[int] = None,
    page_height: Optional[int] = None,
) -> str:
    """
    ⚠️ CRITICAL PREREQUISITE: You MUST call show_pdf_tools first to display the upload widget.
    The document_id parameter comes from the upload response in the widget.

    Convert an HTML file to PDF format.

        When to use this vs `pdf_from_url` (LLM: choose the right tool):
        - Use `pdf_from_html` when you already have the page content as an HTML file
            (e.g., “Save page as…”), or when the page is private/behind login/VPN/intranet
            and cannot be fetched directly by the Foxit service.
        - Use `pdf_from_url` when the target page is publicly accessible and you want
            Foxit to fetch + render it directly from the URL (no upload).

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
        JSON string with:
                - success, message
                - resultDocumentId: identifier of the converted result document, returned for
                    follow-up operations on the generated file
                - shareUrl: public download URL for the converted PDF, when available
                - expiresAt: link expiration timestamp, if provided by the API
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
            client, lambda: client.pdf_from_html(
                document_id, config if config else None)
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
            "message": "HTML converted to PDF successfully."
            if (share or {}).get("shareUrl")
            else "HTML converted to PDF successfully, but no share link was created.",
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
async def pdf_from_url(
    url: str,
    page_width: Optional[int] = None,
    page_height: Optional[int] = None,
) -> str:
    """
        Convert a live web page (URL) directly to a PDF.

        ✅ No upload needed: This tool takes a URL and asks the Foxit Cloud PDF API
        to render that page server-side.

        Important limitations (LLM: read before choosing this tool):
        - The URL must be publicly reachable by the Foxit service.
        - Pages requiring login, cookies, VPN/intranet access, or complex anti-bot
            protections may fail or render incomplete.
        - JavaScript is supported but with time/feature limits (dynamic sites may differ
            from what you see in your browser).

        If the target page is NOT publicly accessible, use one of these instead:
        - Save the page as HTML/PDF locally, upload it, then call `pdf_from_html` (HTML)
            or just keep the uploaded PDF.

        Features:
        - Renders live web pages into PDF
        - Includes CSS styling and images
        - Preserves hyperlinks
        - Automatic page breaks

        Workflow:
        1. Call this tool with `url` (and optional page size)
        2. Wait for async task completion (handled internally)
        3. Returns `resultDocumentId` plus a share link (when share creation succeeds)

        Args:
                url: Publicly accessible URL of the web page to convert
                page_width: Page width in points (optional; default A4 width is 595)
                page_height: Page height in points (optional; default A4 height is 842)

        Returns:
            JSON string with:
            - success, message
            - resultDocumentId: identifier of the converted result document, returned for
              follow-up operations on the generated file
            - shareUrl: public download URL for the converted PDF, when available
            - expiresAt: link expiration timestamp, if provided by the API
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
            client, lambda: client.pdf_from_url(
                url, config if config else None)
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
            "message": "URL converted to PDF successfully."
            if (share or {}).get("shareUrl")
            else "URL converted to PDF successfully, but no share link was created.",
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

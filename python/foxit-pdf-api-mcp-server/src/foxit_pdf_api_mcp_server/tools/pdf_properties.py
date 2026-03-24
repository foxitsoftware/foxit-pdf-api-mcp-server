"""PDF Properties tools for Foxit PDF API MCP Server."""

import json

from ..resources import client, mcp
from ._base import format_error_response


READ_ONLY_TOOL_ANNOTATIONS = {"readOnlyHint": True, "destructiveHint": False}


@mcp.tool(annotations=READ_ONLY_TOOL_ANNOTATIONS)
async def get_pdf_properties(
    document_id: str,
    include_extended_info: bool = True,
    include_page_info: bool = True,
    password: str | None = None,
) -> str:
    """⚠️ CRITICAL PREREQUISITE: You MUST call show_pdf_tools first to display the upload widget.
    The document_id parameter comes from the upload response in the widget.

    Extract comprehensive properties and metadata from a PDF document.

    IMPORTANT: This tool returns JSON data directly, not a file documentId.

    Information returned:
    - Page count and dimensions
    - PDF version and file size
    - Encryption and security status
    - Digital signatures
    - Embedded files and fonts
    - Document metadata (title, author, creation date, etc.)
    - User permissions analysis
    - Page-level information (rotation, dimensions, scan detection)

    Configuration options:
    - includeExtendedInfo: Get detailed metadata (fonts, signatures, encryption details)
    - includePageInfo: Include per-page information (dimensions, rotation, scan detection)

    Use cases:
    - Verify PDF structure before processing
    - Check if PDF is password-protected
    - Analyze PDF compatibility
    - Extract document metadata
    - Detect scanned pages

    Workflow:
    1. Upload PDF using upload_document tool
    2. Call this tool with documentId
    3. Receive JSON data with all properties
    4. No download needed - data is returned directly

    Password-protected PDFs:
    - If the PDF is password-protected, provide the password via the password parameter
    - Without a valid password, the operation will fail with an authentication error

    Args:
        document_id: Document ID of the PDF to analyze
        include_extended_info: Include detailed metadata (fonts, signatures, encryption, etc.). Default: True
        include_page_info: Include per-page information (dimensions, rotation, scan detection). Default: True
        password: Password for password-protected PDFs. Optional. Provide only if the PDF requires a password.

    Returns:
        JSON string with:
        - success, message
        - properties: PDF properties and metadata returned directly as JSON data
    """
    try:
        result = await client.get_pdf_properties(
            document_id=document_id,
            include_extended_info=include_extended_info,
            include_page_info=include_page_info,
            password=password,
        )

        response_data = {
            "success": True,
            "message": "PDF properties extracted successfully",
            "properties": result,
        }

        return json.dumps(response_data, indent=2)
    except Exception as error:
        return format_error_response(error)

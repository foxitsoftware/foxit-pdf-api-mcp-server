"""PDF Properties tools for Foxit PDF API MCP Server."""

import json
from typing import Any

from ..server import client, mcp
from ._base import format_error_response


@mcp.tool()
async def get_pdf_properties(
    document_id: str,
    include_extended_info: bool = True,
    include_page_info: bool = True,
) -> str:
    """Extract comprehensive properties and metadata from a PDF document.

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

    Args:
        document_id: Document ID of the PDF to analyze
        include_extended_info: Include detailed metadata (fonts, signatures, encryption, etc.). Default: True
        include_page_info: Include per-page information (dimensions, rotation, scan detection). Default: True

    Returns:
        JSON string containing PDF properties and metadata
    """
    try:
        result = await client.get_pdf_properties(document_id)

        # Format the response to include configuration info
        response_data = {
            "success": True,
            "properties": result,
            "documentId": document_id,
            "message": "PDF properties extracted successfully",
        }

        return json.dumps(response_data, indent=2)
    except Exception as error:
        return format_error_response(error)

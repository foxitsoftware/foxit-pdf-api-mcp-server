"""PDF Properties tools for Foxit PDF API MCP Server."""

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
async def get_pdf_properties(
    documentId: str,
    includeExtendedInfo: Optional[bool] = None,
    includePageInfo: Optional[bool] = None,
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
        result = await execute_and_wait(
            client,
            lambda: client.get_pdf_properties(
                documentId,
                {
                    "includeExtendedInfo": True
                    if includeExtendedInfo is None
                    else includeExtendedInfo,
                    "includePageInfo": True if includePageInfo is None else includePageInfo,
                },
            ),
        )

        return json.dumps(
            {
                "success": True,
                "taskId": result["taskId"],
                "properties": result.get("resultData"),
                "message": "PDF properties extracted successfully",
            }
        )
    except Exception as error:
        return _error_payload(error, "ANALYSIS_FAILED")

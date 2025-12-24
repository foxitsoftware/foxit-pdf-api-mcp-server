"""PDF manipulation tools: merge, split, extract, compress, etc."""

from typing import Any, Optional

from ..server import client, mcp
from ..utils import execute_and_wait
from ._base import format_error_response, format_success_response


@mcp.tool()
async def pdf_merge(document_ids: list[str]) -> str:
    """
    Merge multiple PDF documents into a single PDF.

    Features:
    - Combines PDFs in the specified order
    - Preserves bookmarks and links
    - Maintains document properties
    - No page limit

    Maximum file size: 100MB per document

    Args:
        document_ids: List of document IDs to merge (in order)

    Returns:
        JSON string with success status, taskId, and resultDocumentId
    """
    try:
        result = await execute_and_wait(client, lambda: client.pdf_merge(document_ids))

        return format_success_response(
            task_id=result.get("taskId", ""),
            result_document_id=result.get("resultDocumentId"),
            message=f"PDFs merged successfully. Download using documentId: {result.get('resultDocumentId')}",
        )
    except Exception as error:
        return format_error_response(error)


@mcp.tool()
async def pdf_split(
    document_id: str,
    page_ranges: Optional[str] = None,
    split_by_pages: Optional[int] = None,
) -> str:
    """
    Split a PDF document into multiple documents.

    Split modes:
    1. By page ranges: "1-5,6-10,11-15" (creates 3 PDFs)
    2. By number of pages: split_by_pages=5 (splits every 5 pages)
    3. Every page: page_ranges="all" (creates one PDF per page)

    Features:
    - Flexible splitting options
    - Preserves page content and formatting
    - Multiple output files (as ZIP)

    Maximum file size: 100MB

    Args:
        document_id: Document ID of the PDF to split
        page_ranges: Page ranges to extract (e.g., "1-5,10-15")
        split_by_pages: Number of pages per output file (alternative to page_ranges)

    Returns:
        JSON string with success status, taskId, and resultDocumentId
        Note: Result is a ZIP file containing the split PDFs
    """
    try:
        config = {}
        if page_ranges:
            config["pageRanges"] = page_ranges
        elif split_by_pages:
            config["splitByPages"] = split_by_pages

        result = await execute_and_wait(client, lambda: client.pdf_split(document_id, config))

        return format_success_response(
            task_id=result.get("taskId", ""),
            result_document_id=result.get("resultDocumentId"),
            message=f"PDF split successfully. Download ZIP file using documentId: {result.get('resultDocumentId')}",
        )
    except Exception as error:
        return format_error_response(error)


@mcp.tool()
async def pdf_extract(document_id: str, page_range: str) -> str:
    """
    Extract specific pages from a PDF document.

    Features:
    - Extract any pages or page ranges
    - Preserves page content and formatting
    - Creates new PDF with extracted pages

    Maximum file size: 100MB

    Args:
        document_id: Document ID of the PDF
        page_range: Pages to extract (e.g., "1,3,5-10", "1-5", "all")

    Returns:
        JSON string with success status, taskId, and resultDocumentId
    """
    try:
        config = {"pageRange": page_range}
        result = await execute_and_wait(client, lambda: client.pdf_extract(document_id, config))

        return format_success_response(
            task_id=result.get("taskId", ""),
            result_document_id=result.get("resultDocumentId"),
            message=f"Pages extracted successfully. Download using documentId: {result.get('resultDocumentId')}",
        )
    except Exception as error:
        return format_error_response(error)


@mcp.tool()
async def pdf_compress(document_id: str) -> str:
    """
    Compress a PDF document to reduce file size.

    Features:
    - Reduces file size while maintaining quality
    - Optimizes images and removes redundant data
    - Preserves document structure and content
    - Typical reduction: 30-70%

    Maximum file size: 100MB

    Args:
        document_id: Document ID of the PDF to compress

    Returns:
        JSON string with success status, taskId, and resultDocumentId
    """
    try:
        result = await execute_and_wait(client, lambda: client.pdf_compress(document_id))

        return format_success_response(
            task_id=result.get("taskId", ""),
            result_document_id=result.get("resultDocumentId"),
            message=f"PDF compressed successfully. Download using documentId: {result.get('resultDocumentId')}",
        )
    except Exception as error:
        return format_error_response(error)


@mcp.tool()
async def pdf_flatten(document_id: str) -> str:
    """
    Flatten a PDF document (merge all layers and form fields).

    Features:
    - Converts form fields to static content
    - Flattens annotations and markup
    - Merges all layers
    - Prevents further editing of forms

    Use cases:
    - Finalize forms before archiving
    - Prevent form tampering
    - Reduce file complexity

    Maximum file size: 100MB

    Args:
        document_id: Document ID of the PDF to flatten

    Returns:
        JSON string with success status, taskId, and resultDocumentId
    """
    try:
        result = await execute_and_wait(client, lambda: client.pdf_flatten(document_id))

        return format_success_response(
            task_id=result.get("taskId", ""),
            result_document_id=result.get("resultDocumentId"),
            message=f"PDF flattened successfully. Download using documentId: {result.get('resultDocumentId')}",
        )
    except Exception as error:
        return format_error_response(error)


@mcp.tool()
async def pdf_linearize(document_id: str) -> str:
    """
    Linearize a PDF document for fast web viewing.

    Features:
    - Optimizes PDF for progressive download
    - Enables page-at-a-time display in web browsers
    - Improves user experience for large PDFs
    - No visual changes to content

    Use cases:
    - Web-based PDF viewing
    - Streaming large documents
    - Improving load times

    Maximum file size: 100MB

    Args:
        document_id: Document ID of the PDF to linearize

    Returns:
        JSON string with success status, taskId, and resultDocumentId
    """
    try:
        result = await execute_and_wait(client, lambda: client.pdf_linearize(document_id))

        return format_success_response(
            task_id=result.get("taskId", ""),
            result_document_id=result.get("resultDocumentId"),
            message=f"PDF linearized successfully. Download using documentId: {result.get('resultDocumentId')}",
        )
    except Exception as error:
        return format_error_response(error)


@mcp.tool()
async def pdf_watermark(
    document_id: str,
    content: str,
    watermark_type: Optional[str] = None,
    position: Optional[str] = None,
    opacity: Optional[float] = None,
    rotation: Optional[int] = None,
    font_size: Optional[int] = None,
    color: Optional[str] = None,
    page_ranges: Optional[str] = None,
    password: Optional[str] = None,
) -> str:
    """Add text or image watermark to PDF pages.

    Watermark types:
    - TEXT: Text watermark (default)
    - IMAGE: Image watermark (provide image documentId as content)

    Configuration:
    - content: Watermark text or image documentId
    - position: Placement (CENTER, TOP_LEFT, TOP_RIGHT, BOTTOM_LEFT, BOTTOM_RIGHT)
    - opacity: Transparency (0.0-1.0, default: 0.5)
    - rotation: Rotation angle in degrees (default: 0)
    - fontSize: Text size in points (for TEXT type)
    - color: Text color in hex format (e.g., "#FF0000" for red)
    - pageRanges: Specific pages (e.g., "1-3,5,7-9", default: all pages)

    Use cases:
    - Add "DRAFT" or "CONFIDENTIAL" stamps
    - Add company logos
    - Copyright protection
    - Document tracking

    Workflow:
    1. Upload PDF using upload_document tool
    2. (Optional) Upload watermark image for IMAGE type
    3. Call this tool with watermark configuration
    4. Download watermarked PDF using download_document tool

    Args:
        document_id: Document ID of the PDF
        content: Watermark text or image documentId
        watermark_type: Watermark type (TEXT or IMAGE, default: TEXT)
        position: Watermark position (default: CENTER)
        opacity: Opacity 0.0-1.0 (default: 0.5)
        rotation: Rotation angle in degrees
        font_size: Font size in points (for TEXT)
        color: Text color in hex (e.g., "#FF0000")
        page_ranges: Pages to watermark (e.g., "1-3,5", default: all)
        password: Password if PDF is password-protected

    Returns:
        JSON string with success status, taskId, and resultDocumentId
    """
    try:
        config: dict[str, Any] = {"content": content}
        if watermark_type:
            config["type"] = watermark_type
        if position:
            config["position"] = position
        if opacity is not None:
            config["opacity"] = opacity
        if rotation is not None:
            config["rotation"] = rotation
        if font_size:
            config["fontSize"] = font_size
        if color:
            config["color"] = color
        if page_ranges:
            config["pageRanges"] = page_ranges
        if password:
            config["password"] = password

        result = await execute_and_wait(
            client, lambda: client.pdf_watermark(document_id, config)
        )

        return format_success_response(
            task_id=result.get("taskId", ""),
            result_document_id=result.get("resultDocumentId"),
            message=f"Watermark added successfully. Download using documentId: {result.get('resultDocumentId')}",
        )
    except Exception as error:
        return format_error_response(error)


@mcp.tool()
async def pdf_manipulate(
    document_id: str,
    operations: list[dict[str, Any]],
    password: Optional[str] = None,
) -> str:
    """Reorganize, rotate, or delete pages in a PDF.

    Operations:
    - ROTATE: Rotate a page (90, 180, or 270 degrees)
    - DELETE: Remove a page
    - REORDER: Move a page to a different position

    Each operation requires:
    - type: Operation type
    - pageIndex: Target page (0-based index)
    - rotation: Rotation angle (for ROTATE)
    - targetIndex: New position (for REORDER)

    Example operations:
    - Rotate page 1 by 90°: {type: "ROTATE", pageIndex: 0, rotation: 90}
    - Delete page 3: {type: "DELETE", pageIndex: 2}
    - Move page 5 to position 2: {type: "REORDER", pageIndex: 4, targetIndex: 1}

    Workflow:
    1. Upload PDF using upload_document tool
    2. Call this tool with array of operations
    3. Download modified PDF using download_document tool

    Args:
        document_id: Document ID of the PDF to manipulate
        operations: Array of page manipulation operations
        password: Password if PDF is password-protected

    Returns:
        JSON string with success status, taskId, and resultDocumentId
    """
    try:
        config: dict[str, Any] = {"operations": operations}
        if password:
            config["password"] = password

        result = await execute_and_wait(
            client, lambda: client.pdf_manipulate(document_id, config)
        )

        return format_success_response(
            task_id=result.get("taskId", ""),
            result_document_id=result.get("resultDocumentId"),
            message=f"PDF manipulated successfully with {len(operations)} operations. Download using documentId: {result.get('resultDocumentId')}",
        )
    except Exception as error:
        return format_error_response(error)

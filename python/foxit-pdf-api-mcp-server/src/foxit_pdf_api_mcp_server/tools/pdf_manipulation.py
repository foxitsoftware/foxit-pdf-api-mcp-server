"""PDF manipulation tools: merge, split, extract, compress, etc."""

import json
from typing import Any, Optional

from ..server import client, mcp
from ..utils import execute_and_wait


@mcp.tool()
async def pdf_merge(documents: list[dict[str, Any]]) -> str:
    """
    Merge multiple PDF documents into a single PDF.

    Features:
    - Combines PDFs in the specified order
    - Preserves bookmarks and links
    - Maintains document properties
    - No page limit

    Maximum file size: 100MB per document

    Args:
        documents: Array of documents to merge. Each item: {documentId, password?}

    Returns:
        JSON string with success status, taskId, and resultDocumentId
    """
    try:
        result = await execute_and_wait(client, lambda: client.pdf_merge(documents))

        return json.dumps(
            {
                "success": True,
                "taskId": result.get("taskId", ""),
                "resultDocumentId": result.get("resultDocumentId"),
                "documentsCount": len(documents),
                "message": f"{len(documents)} PDFs merged successfully. Download using documentId: {result.get('resultDocumentId')}",
            },
            indent=2,
        )
    except Exception as error:
        return json.dumps(
            {
                "success": False,
                "error": str(error),
                "code": getattr(error, "code", "MERGE_FAILED"),
                "taskId": getattr(error, "taskId", None) or getattr(error, "task_id", None),
            },
            indent=2,
        )


@mcp.tool()
async def pdf_split(
    documentId: str,
    splitStrategy: str,
    pageCount: Optional[int] = None,
    pageRanges: Optional[list[str]] = None,
    password: Optional[str] = None,
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
        documentId: Document ID of the PDF to split
        splitStrategy: Strategy for splitting the PDF (BY_PAGE_COUNT | BY_PAGE_RANGES | EVERY_PAGE)
        pageCount: Pages per chunk (required for BY_PAGE_COUNT)
        pageRanges: Page ranges (required for BY_PAGE_RANGES, e.g., ["1-3", "4-10"])
        password: Password if PDF is password-protected

    Returns:
        JSON string with success status, taskId, and resultDocumentId
        Note: Result is a ZIP file containing the split PDFs
    """
    try:
        config: dict[str, Any] = {"pageCount": pageCount, "pageRanges": pageRanges}

        result = await execute_and_wait(
            client,
            lambda: client.pdf_split(documentId, splitStrategy, config, password),
        )

        return json.dumps(
            {
                "success": True,
                "taskId": result.get("taskId", ""),
                "resultDocumentId": result.get("resultDocumentId"),
                "strategy": splitStrategy,
                "message": f"PDF split successfully. Download ZIP using documentId: {result.get('resultDocumentId')}",
            },
            indent=2,
        )
    except Exception as error:
        return json.dumps(
            {
                "success": False,
                "error": str(error),
                "code": getattr(error, "code", "SPLIT_FAILED"),
                "taskId": getattr(error, "taskId", None) or getattr(error, "task_id", None),
            },
            indent=2,
        )


@mcp.tool()
async def pdf_extract(
    documentId: str,
    extractType: str,
    pageRanges: Optional[str] = None,
    password: Optional[str] = None,
) -> str:
    """
    Extract specific pages from a PDF document.

    Features:
    - Extract any pages or page ranges
    - Preserves page content and formatting
    - Creates new PDF with extracted pages

    Maximum file size: 100MB

    Args:
        documentId: Document ID of the PDF
        extractType: Type of content to extract (TEXT | IMAGES | PAGES)
        pageRanges: Page ranges to extract from (e.g., "1-3,5,7-9")
        password: Password if PDF is password-protected

    Returns:
        JSON string with success status, taskId, and resultDocumentId
    """
    try:
        config = {"pageRanges": pageRanges} if pageRanges is not None else {}
        result = await execute_and_wait(
            client,
            lambda: client.pdf_extract(documentId, extractType, config, password),
        )

        return json.dumps(
            {
                "success": True,
                "taskId": result.get("taskId", ""),
                "resultDocumentId": result.get("resultDocumentId"),
                "extractType": extractType,
                "message": f"Content extracted successfully. Download using documentId: {result.get('resultDocumentId')}",
            },
            indent=2,
        )
    except Exception as error:
        return json.dumps(
            {
                "success": False,
                "error": str(error),
                "code": getattr(error, "code", "EXTRACT_FAILED"),
                "taskId": getattr(error, "taskId", None) or getattr(error, "task_id", None),
            },
            indent=2,
        )


@mcp.tool()
async def pdf_compress(
    documentId: str,
    compressionLevel: str,
    password: Optional[str] = None,
) -> str:
    """
    Compress a PDF document to reduce file size.

    Features:
    - Reduces file size while maintaining quality
    - Optimizes images and removes redundant data
    - Preserves document structure and content
    - Typical reduction: 30-70%

    Maximum file size: 100MB

    Args:
        documentId: Document ID of the PDF to compress
        compressionLevel: Compression level (HIGH | MEDIUM | LOW)
        password: Password if PDF is password-protected

    Returns:
        JSON string with success status, taskId, and resultDocumentId
    """
    try:
        result = await execute_and_wait(
            client,
            lambda: client.pdf_compress(documentId, compressionLevel, password),
        )

        return json.dumps(
            {
                "success": True,
                "taskId": result.get("taskId", ""),
                "resultDocumentId": result.get("resultDocumentId"),
                "compressionLevel": compressionLevel,
                "message": f"PDF compressed successfully. Download using documentId: {result.get('resultDocumentId')}",
            },
            indent=2,
        )
    except Exception as error:
        return json.dumps(
            {
                "success": False,
                "error": str(error),
                "code": getattr(error, "code", "COMPRESS_FAILED"),
                "taskId": getattr(error, "taskId", None) or getattr(error, "task_id", None),
            },
            indent=2,
        )


@mcp.tool()
async def pdf_flatten(documentId: str, password: Optional[str] = None) -> str:
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
        documentId: Document ID of the PDF to flatten
        password: Password if PDF is password-protected

    Returns:
        JSON string with success status, taskId, and resultDocumentId
    """
    try:
        result = await execute_and_wait(
            client,
            lambda: client.pdf_flatten(documentId, password),
        )

        return json.dumps(
            {
                "success": True,
                "taskId": result.get("taskId", ""),
                "resultDocumentId": result.get("resultDocumentId"),
                "message": f"PDF flattened successfully. Download using documentId: {result.get('resultDocumentId')}",
            },
            indent=2,
        )
    except Exception as error:
        return json.dumps(
            {
                "success": False,
                "error": str(error),
                "code": getattr(error, "code", "FLATTEN_FAILED"),
                "taskId": getattr(error, "taskId", None) or getattr(error, "task_id", None),
            },
            indent=2,
        )


@mcp.tool()
async def pdf_linearize(documentId: str) -> str:
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
        documentId: Document ID of the PDF to linearize

    Returns:
        JSON string with success status, taskId, and resultDocumentId
    """
    try:
        result = await execute_and_wait(client, lambda: client.pdf_linearize(documentId))

        return json.dumps(
            {
                "success": True,
                "taskId": result.get("taskId", ""),
                "resultDocumentId": result.get("resultDocumentId"),
                "message": f"PDF linearized successfully. Download using documentId: {result.get('resultDocumentId')}",
            },
            indent=2,
        )
    except Exception as error:
        return json.dumps(
            {
                "success": False,
                "error": str(error),
                "code": getattr(error, "code", "LINEARIZE_FAILED"),
                "taskId": getattr(error, "taskId", None) or getattr(error, "task_id", None),
            },
            indent=2,
        )


@mcp.tool()
async def pdf_watermark(
    documentId: str,
    content: str,
    type: Optional[str] = None,
    position: Optional[str] = None,
    opacity: Optional[float] = None,
    rotation: Optional[int] = None,
    fontSize: Optional[int] = None,
    color: Optional[str] = None,
    pageRanges: Optional[str] = None,
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
        documentId: Document ID of the PDF
        content: Watermark text or image documentId
        type: Watermark type (TEXT or IMAGE, default: TEXT)
        position: Watermark position (default: CENTER)
        opacity: Opacity 0.0-1.0 (default: 0.5)
        rotation: Rotation angle in degrees
        fontSize: Font size in points (for TEXT)
        color: Text color in hex (e.g., "#FF0000")
        pageRanges: Pages to watermark (e.g., "1-3,5", default: all)
        password: Password if PDF is password-protected

    Returns:
        JSON string with success status, taskId, and resultDocumentId
    """
    try:
        config: dict[str, Any] = {"content": content}
        if type:
            config["type"] = type
        if position:
            config["position"] = position
        if opacity is not None:
            config["opacity"] = opacity
        if rotation is not None:
            config["rotation"] = rotation
        if fontSize:
            config["fontSize"] = fontSize
        if color:
            config["color"] = color
        if pageRanges:
            config["pageRanges"] = pageRanges

        result = await execute_and_wait(
            client, lambda: client.pdf_watermark(documentId, config, password)
        )

        return json.dumps(
            {
                "success": True,
                "taskId": result.get("taskId", ""),
                "resultDocumentId": result.get("resultDocumentId"),
                "message": f"Watermark added successfully. Download using documentId: {result.get('resultDocumentId')}",
            },
            indent=2,
        )
    except Exception as error:
        return json.dumps(
            {
                "success": False,
                "error": str(error),
                "code": getattr(error, "code", "WATERMARK_FAILED"),
                "taskId": getattr(error, "taskId", None) or getattr(error, "task_id", None),
            },
            indent=2,
        )


@mcp.tool()
async def pdf_manipulate(
    documentId: str,
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
        documentId: Document ID of the PDF to manipulate
        operations: Array of page manipulation operations
        password: Password if PDF is password-protected

    Returns:
        JSON string with success status, taskId, and resultDocumentId
    """
    try:
        result = await execute_and_wait(
            client, lambda: client.pdf_manipulate(documentId, operations, password)
        )

        return json.dumps(
            {
                "success": True,
                "taskId": result.get("taskId", ""),
                "resultDocumentId": result.get("resultDocumentId"),
                "operationsCount": len(operations),
                "message": f"PDF manipulated successfully with {len(operations)} operations. Download using documentId: {result.get('resultDocumentId')}",
            },
            indent=2,
        )
    except Exception as error:
        return json.dumps(
            {
                "success": False,
                "error": str(error),
                "code": getattr(error, "code", "MANIPULATE_FAILED"),
                "taskId": getattr(error, "taskId", None) or getattr(error, "task_id", None),
            },
            indent=2,
        )

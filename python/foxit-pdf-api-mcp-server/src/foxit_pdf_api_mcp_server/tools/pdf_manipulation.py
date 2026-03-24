"""PDF manipulation tools: merge, split, extract, compress, etc."""

import json
import re
from typing import Any, Optional

from ..resources import client, mcp
from ._base import format_error_response, format_task_submitted_response, register_task


WRITE_TOOL_ANNOTATIONS = {"readOnlyHint": False, "destructiveHint": False}
DESTRUCTIVE_TOOL_ANNOTATIONS = {"readOnlyHint": False, "destructiveHint": True}


_MAX_PAGE_RANGE_EXPANSION = 20000


def _parse_page_range_1_based(page_range: str) -> tuple[set[int], list[str]]:
    """Parse a 1-based page range string into a set of page numbers.

    Supported formats:
    - "1"
    - "1,3,5"
    - "5-10"
    - "1,3,5-10"

    Returns:
        (pages, invalid_tokens)
    """

    raw = (page_range or "").strip()
    if not raw:
        return set(), ["<empty>"]

    tokens = [t for t in re.split(r"[\s,]+", raw) if t]
    pages: set[int] = set()
    invalid: list[str] = []

    for token in tokens:
        token = token.strip()
        if not token:
            continue

        if "-" in token:
            parts = token.split("-")
            if len(parts) != 2 or not parts[0] or not parts[1]:
                invalid.append(token)
                continue
            try:
                start = int(parts[0])
                end = int(parts[1])
            except Exception:
                invalid.append(token)
                continue
            if start <= 0 or end <= 0 or start > end:
                invalid.append(token)
                continue
            if (end - start + 1) > _MAX_PAGE_RANGE_EXPANSION:
                invalid.append(token)
                continue
            pages.update(range(start, end + 1))
            continue

        try:
            page = int(token)
        except Exception:
            invalid.append(token)
            continue
        if page <= 0:
            invalid.append(token)
            continue
        pages.add(page)

    return pages, invalid


@mcp.tool(annotations=WRITE_TOOL_ANNOTATIONS)
async def pdf_merge(
    document_ids: list[str], passwords: list[str | None] | None = None
) -> str:
    """
    ⚠️ CRITICAL PREREQUISITE: You MUST call show_pdf_tools first to display the upload widget.
    The document_id parameter comes from the upload response in the widget.

    Merge multiple PDF documents into a single PDF.

    Features:
    - Combines PDFs in the specified order
    - Attempts to preserve bookmarks/links where supported (results may vary)
    - Output metadata/properties may differ from inputs

    Maximum file size: 100MB per document

    Password-protected PDFs:
    - If any PDFs are password-protected, provide passwords via the passwords parameter
    - passwords list must match the length of document_ids
    - Use None for documents without passwords
    - Example: passwords=[None, "password123", None] for 3 documents where only the 2nd is protected

    This operation runs asynchronously. The tool returns a taskId immediately.
    Use get_task_result to poll for completion and retrieve the download link.

    Args:
        document_ids: List of document IDs to merge (in order)
        passwords: Optional list of passwords (one per document). Use None for unprotected documents.

    Returns:
        JSON string with:
        - success: operation was submitted successfully
        - taskId: use with get_task_result to check status and retrieve the result
        - message: describes next steps
    """
    try:
        result = await client.pdf_merge(document_ids, passwords=passwords)
        task_id = result["taskId"]
        register_task(task_id, "pdf_merge", "PDFs merged successfully.")
        return format_task_submitted_response(
            task_id,
            "PDF merge submitted. Use get_task_result to check status and retrieve the download link.",
        )
    except Exception as error:
        return format_error_response(error)


@mcp.tool(annotations=WRITE_TOOL_ANNOTATIONS)
async def pdf_split(
    document_id: str,
    page_count: int,
    password: Optional[str] = None,
) -> str:
    """
    ⚠️ CRITICAL PREREQUISITE: You MUST call show_pdf_tools first to display the upload widget.
    The document_id parameter comes from the upload response in the widget.

    Split a PDF document into multiple files by fixed page count.
    - The API requires pageCount (pages per output file).
    - The output is a ZIP document containing the split PDFs.

    Example:
    - page_count=10 splits the PDF into files of 10 pages each (last file may have fewer pages).

    Maximum file size: 100MB

    This operation runs asynchronously. The tool returns a taskId immediately.
    Use get_task_result to poll for completion and retrieve the download link.

    Args:
        document_id: Document ID of the PDF to split
        page_count: Number of pages per output file (must be >= 1)
        password: Password if the PDF is password-protected

    Returns:
        JSON string with:
        - success: operation was submitted successfully
        - taskId: use with get_task_result to check status and retrieve the result
        - message: describes next steps
    """
    try:
        if page_count is None or page_count <= 0:
            raise ValueError("page_count is required and must be >= 1.")

        config: dict[str, Any] = {"pageCount": int(page_count)}
        if password is not None and password != "":
            config["password"] = password

        result = await client.pdf_split(document_id, config)
        task_id = result["taskId"]
        register_task(task_id, "pdf_split", "PDF split successfully.")
        return format_task_submitted_response(
            task_id,
            "PDF split submitted. Use get_task_result to check status and retrieve the download link.",
        )
    except Exception as error:
        return format_error_response(error)


@mcp.tool(annotations=WRITE_TOOL_ANNOTATIONS)
async def pdf_extract_pages(
    document_id: str,
    page_range: str,
    password: Optional[str] = None,
) -> str:
    """
    ⚠️ CRITICAL PREREQUISITE: You MUST call show_pdf_tools first to display the upload widget.
    The document_id parameter comes from the upload response in the widget.
    

    Extract selected pages into a new PDF document.

    Features:
    - Extract any pages or page ranges into a new PDF
    - Preserves page content and formatting

    Maximum file size: 100MB

    This operation runs asynchronously. The tool returns a taskId immediately.
    Use get_task_result to poll for completion and retrieve the download link.

    Args:
        document_id: Document ID of the PDF
        page_range: Pages to extract. Uses 1-based page numbers (page 1 is the first page).
            Supports ranges like "1,3,5-10" and special values "all", "even", "odd".
        password: Password if the PDF is password-protected

    Returns:
        JSON string with:
        - success: operation was submitted successfully
        - taskId: use with get_task_result to check status and retrieve the result
        - message: describes next steps
    """
    try:
        config: dict[str, Any] = {"pageRange": page_range, "extractType": "PAGE"}
        if password is not None and password != "":
            config["password"] = password
        result = await client.pdf_extract(document_id, config)
        task_id = result["taskId"]
        register_task(task_id, "pdf_extract_pages", "Pages extracted successfully.")
        return format_task_submitted_response(
            task_id,
            "Page extraction submitted. Use get_task_result to check status and retrieve the download link.",
        )
    except Exception as error:
        return format_error_response(error)


@mcp.tool(annotations=WRITE_TOOL_ANNOTATIONS)
async def pdf_extract_text(
    document_id: str,
    page_range: str,
    password: Optional[str] = None,
    max_chars: int = 120000,
) -> str:
    """
    ⚠️ CRITICAL PREREQUISITE: You MUST call show_pdf_tools first to display the upload widget.
    The document_id parameter comes from the upload response in the widget.

    Extract plain text content from selected pages.
    - returns plain text and a generated .txt document.
    - pageRange controls which pages are processed (1-based) and also supports "all", "even", "odd".

    This operation runs asynchronously. The tool returns a taskId immediately.
    Use get_task_result to poll for completion and retrieve the result.
    When complete, the result includes extracted text preview and a download link.

    Args:
        document_id: Document ID of the PDF
        page_range: Pages to extract text from. Uses 1-based page numbers (page 1 is the first page).
            Supports ranges like "1,3,5-10" and special values "all", "even", "odd".
        password: Password if the PDF is password-protected
        max_chars: Max characters to include inline in the response (download link is still provided)

    Returns:
        JSON string with:
        - success: operation was submitted successfully
        - taskId: use with get_task_result to check status and retrieve the result
        - message: describes next steps
    """
    try:
        if max_chars is not None and max_chars > 0:
            max_chars = min(max_chars, 200000)

        config: dict[str, Any] = {"pageRange": page_range, "extractType": "TEXT"}
        if password is not None and password != "":
            config["password"] = password

        result = await client.pdf_extract(document_id, config)
        task_id = result["taskId"]
        register_task(
            task_id,
            "pdf_extract_text",
            "Text extracted successfully.",
            max_chars=max_chars,
        )
        return format_task_submitted_response(
            task_id,
            "Text extraction submitted. Use get_task_result to check status and retrieve the extracted text.",
        )
    except Exception as error:
        return format_error_response(error)


@mcp.tool(annotations=WRITE_TOOL_ANNOTATIONS)
async def pdf_compress(document_id: str, password: str | None = None) -> str:
    """
    ⚠️ CRITICAL PREREQUISITE: You MUST call show_pdf_tools first to display the upload widget.
    The document_id parameter comes from the upload response in the widget.
    Compress a PDF document to reduce file size.

    **Do not offer compression level options. Only one default compression level is currently supported.**

    Features:
    - Attempts to reduce file size; compression ratio and quality impact vary by document
    - Optimizes embedded resources (e.g., images) and removes redundant data where possible
    - Output fidelity and file size depend on the input document

    Maximum file size: 100MB

    Password-protected PDFs:
    - If the PDF is password-protected, provide the password via the password parameter
    - Without a valid password, the operation will fail with an authentication error

    This operation runs asynchronously. The tool returns a taskId immediately.
    Use get_task_result to poll for completion and retrieve the download link.

    Args:
        document_id: Document ID of the PDF to compress
        password: Password for password-protected PDFs. Optional. Provide only if the PDF requires a password.

    Returns:
        JSON string with:
        - success: operation was submitted successfully
        - taskId: use with get_task_result to check status and retrieve the result
        - message: describes next steps
    """
    try:
        result = await client.pdf_compress(document_id, password=password)
        task_id = result["taskId"]
        register_task(task_id, "pdf_compress", "PDF compressed successfully.")
        return format_task_submitted_response(
            task_id,
            "PDF compression submitted. Use get_task_result to check status and retrieve the download link.",
        )
    except Exception as error:
        return format_error_response(error)


@mcp.tool(annotations=WRITE_TOOL_ANNOTATIONS)
async def pdf_flatten(document_id: str, password: str | None = None) -> str:
    """
    ⚠️ CRITICAL PREREQUISITE: You MUST call show_pdf_tools first to display the upload widget.
    The document_id parameter comes from the upload response in the widget.
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

    Password-protected PDFs:
    - If the PDF is password-protected, provide the password via the password parameter
    - Without a valid password, the operation will fail with an authentication error

    This operation runs asynchronously. The tool returns a taskId immediately.
    Use get_task_result to poll for completion and retrieve the download link.

    Args:
        document_id: Document ID of the PDF to flatten
        password: Password for password-protected PDFs. Optional. Provide only if the PDF requires a password.

    Returns:
        JSON string with:
        - success: operation was submitted successfully
        - taskId: use with get_task_result to check status and retrieve the result
        - message: describes next steps
    """
    try:
        result = await client.pdf_flatten(document_id, password=password)
        task_id = result["taskId"]
        register_task(task_id, "pdf_flatten", "PDF flattened successfully.")
        return format_task_submitted_response(
            task_id,
            "PDF flatten submitted. Use get_task_result to check status and retrieve the download link.",
        )
    except Exception as error:
        return format_error_response(error)


@mcp.tool(annotations=WRITE_TOOL_ANNOTATIONS)
async def pdf_linearize(document_id: str, password: str | None = None) -> str:
    """
    ⚠️ CRITICAL PREREQUISITE: You MUST call show_pdf_tools first to display the upload widget.
    The document_id parameter comes from the upload response in the widget.
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

    Password-protected PDFs:
    - If the PDF is password-protected, provide the password via the password parameter
    - Without a valid password, the operation will fail with an authentication error

    This operation runs asynchronously. The tool returns a taskId immediately.
    Use get_task_result to poll for completion and retrieve the download link.

    Args:
        document_id: Document ID of the PDF to linearize
        password: Password for password-protected PDFs. Optional. Provide only if the PDF requires a password.

    Returns:
        JSON string with:
        - success: operation was submitted successfully
        - taskId: use with get_task_result to check status and retrieve the result
        - message: describes next steps
    """
    try:
        result = await client.pdf_linearize(document_id, password=password)
        task_id = result["taskId"]
        register_task(task_id, "pdf_linearize", "PDF linearized successfully.")
        return format_task_submitted_response(
            task_id,
            "PDF linearize submitted. Use get_task_result to check status and retrieve the download link.",
        )
    except Exception as error:
        return format_error_response(error)


# NOTE: pdf_watermark tool is currently disabled.
# Leaving an active @mcp.tool() decorator here would accidentally stack decorators
# onto the next tool definition and break registration/import.
# @mcp.tool()
# async def pdf_watermark(
#     document_id: str,
#     content: str,
#     watermark_type: Optional[str] = None,
#     position: Optional[str] = None,
#     opacity: Optional[float] = None,
#     rotation: Optional[int] = None,
#     font_size: Optional[int] = None,
#     color: Optional[str] = None,
#     page_ranges: Optional[str] = None,
#     password: Optional[str] = None,
# ) -> str:
    
#     """
#     ⚠️ CRITICAL PREREQUISITE: You MUST call show_pdf_tools first to display the upload widget.
#     The document_id parameter comes from the upload response in the widget.
#     Add text or image watermark to PDF pages.

#     Watermark types:
#     - TEXT: Text watermark (default)
#     - IMAGE: Image watermark (provide image documentId as content)

#     Configuration:
#     - content: Watermark text or image documentId
#     - position: Placement (CENTER, TOP_LEFT, TOP_RIGHT, BOTTOM_LEFT, BOTTOM_RIGHT)
#     - opacity: Transparency (0.0-1.0, default: 0.5)
#     - rotation: Rotation angle in degrees (default: 0)
#     - fontSize: Text size in points (for TEXT type)
#     - color: Text color in hex format (e.g., "#FF0000" for red)
#     - pageRanges: Specific pages (e.g., "1-3,5,7-9", default: all pages)

#     Use cases:
#     - Add "DRAFT" or "CONFIDENTIAL" stamps
#     - Add company logos
#     - Copyright protection
#     - Document tracking

#     Workflow:
#     1. Upload PDF using upload_document tool
#     2. (Optional) Upload watermark image for IMAGE type
#     3. Call this tool with watermark configuration
#     4. The tool automatically creates a share link and returns it

#     Args:
#         document_id: Document ID of the PDF
#         content: Watermark text or image documentId
#         watermark_type: Watermark type (TEXT or IMAGE, default: TEXT)
#         position: Watermark position (default: CENTER)
#         opacity: Opacity 0.0-1.0 (default: 0.5)
#         rotation: Rotation angle in degrees
#         font_size: Font size in points (for TEXT)
#         color: Text color in hex (e.g., "#FF0000")
#         page_ranges: Pages to watermark (e.g., "1-3,5", default: all)
#         password: Password if PDF is password-protected

#     Returns:
#         JSON string with:
#         - success, taskId, message
#         - resultDocumentId
#         - shareUrl, expiresAt (when share link creation succeeds)
#         - shareLinkError (when share link creation fails)
#         - resultData.request: { type, position, opacity, rotation, fontSize, color, pageRanges, passwordProvided }
#     """
#     try:
#         config: dict[str, Any] = {"content": content}
#         if watermark_type:
#             config["type"] = watermark_type
#         if position:
#             config["position"] = position
#         if opacity is not None:
#             config["opacity"] = opacity
#         if rotation is not None:
#             config["rotation"] = rotation
#         if font_size:
#             config["fontSize"] = font_size
#         if color:
#             config["color"] = color
#         if page_ranges:
#             config["pageRanges"] = page_ranges
#         if password:
#             config["password"] = password

#         result = await execute_and_wait(
#             client, lambda: client.pdf_watermark(document_id, config)
#         )

#         result_document_id = result.get("resultDocumentId")
#         share, share_error = (None, None)
#         if result_document_id:
#             share, share_error = await try_create_share_link(
#                 client.create_share_link,
#                 document_id=result_document_id,
#                 expiration_minutes=None,
#                 filename=None,
#             )

#         return format_success_response(
#             task_id=result.get("taskId", ""),
#             result_document_id=result_document_id,
#             message="Watermark added successfully.",
#             result_data={
#                 "request": {
#                     "type": watermark_type,
#                     "position": position,
#                     "opacity": opacity,
#                     "rotation": rotation,
#                     "fontSize": font_size,
#                     "color": color,
#                     "pageRanges": page_ranges,
#                     **(
#                         {"passwordProvided": True}
#                         if password is not None and password != ""
#                         else {}
#                     ),
#                 }
#             }
#             if (
#                 watermark_type is not None
#                 or position is not None
#                 or opacity is not None
#                 or rotation is not None
#                 or font_size is not None
#                 or color is not None
#                 or page_ranges is not None
#                 or (password is not None and password != "")
#             )
#             else None,
#             share_url=(share or {}).get("shareUrl"),
#             expires_at=(share or {}).get("expiresAt"),
#             token=(share or {}).get("token"),
#             share_link_error=share_error,
#         )
#     except Exception as error:
#         return format_error_response(error)


@mcp.tool(annotations=WRITE_TOOL_ANNOTATIONS)
async def pdf_manipulate(
    document_id: str,
    operations: list[dict[str, Any]],
    password: Optional[str] = None,
) -> str:
    """
    ⚠️ CRITICAL PREREQUISITE: You MUST call show_pdf_tools first to display the upload widget.
    The document_id parameter comes from the upload response in the widget.
    Reorganize, rotate, and delete pages in a PDF.

    Operations (PPOOperation):
    - MOVE_PAGES: Move pages to a target position
        - pages: list of page numbers (1-based)
        - targetPosition: insert position (1-based)
    - DELETE_PAGES: Remove pages
        - pages: list of page numbers (1-based)
    - ROTATE_PAGES: Rotate pages
        - pages: list of page numbers (1-based)
        - rotation: one of ROTATE_0, ROTATE_CLOCKWISE_90, ROTATE_180, ROTATE_COUNTERCLOCKWISE_90

    Example operations:
    - Rotate pages 4-6 by 90° clockwise:
        {"type": "ROTATE_PAGES", "pages": [4, 5, 6], "rotation": "ROTATE_CLOCKWISE_90"}
    - Delete pages 8-9:
        {"type": "DELETE_PAGES", "pages": [8, 9]}
    - Move pages 1-3 to position 5:
        {"type": "MOVE_PAGES", "pages": [1, 2, 3], "targetPosition": 5}

    Workflow:
    1. Upload PDF using upload_document tool
    2. Call this tool with array of operations
    3. The tool automatically creates a share link and returns it

    This operation runs asynchronously. The tool returns a taskId immediately.
    Use get_task_result to poll for completion and retrieve the download link.

    Args:
        document_id: Document ID of the PDF to manipulate
        operations: Array of page manipulation operations (OpenAPI PPOOperation). Pages are 1-based.
        password: Password if PDF is password-protected

    Returns:
        JSON string with:
        - success: operation was submitted successfully
        - taskId: use with get_task_result to check status and retrieve the result
        - message: describes next steps
    """
    try:
        config: dict[str, Any] = {"operations": operations}

        result = await client.pdf_manipulate(document_id, config, password=password)
        task_id = result["taskId"]
        register_task(
            task_id,
            "pdf_manipulate",
            f"PDF manipulated successfully with {len(operations)} operation(s).",
        )
        return format_task_submitted_response(
            task_id,
            "PDF manipulation submitted. Use get_task_result to check status and retrieve the download link.",
        )
    except Exception as error:
        return format_error_response(error)


@mcp.tool(annotations=WRITE_TOOL_ANNOTATIONS)
async def pdf_delete_pages(
    document_id: str,
    page_range: str,
    password: Optional[str] = None,
) -> str:
    """
    ⚠️ CRITICAL PREREQUISITE: You MUST call show_pdf_tools first to display the upload widget.
    The document_id parameter comes from the upload response in the widget.
    Remove specific pages from a PDF using exact page numbers/ranges.

    Input uses 1-based page numbers (page 1 is the first page).

    Examples:
    - "1" (delete first page)
    - "1,3,5" (delete pages 1, 3, 5)
    - "5-10" (delete pages 5 through 10)
    - "1,3,5-10" (mix)

    Behavior:
    - Invalid tokens are ignored and reported in the message/resultData.
    - Out-of-range pages are ignored (based on PDF pageCount) and reported.
    - Deletions are executed in descending page order to avoid index shifting issues.

    Returns:
        JSON string with:
                - success, message
                - resultDocumentId: identifier of the updated PDF, returned for
                    follow-up operations on the generated file
                - shareUrl: public download URL for the updated PDF, when available
                - expiresAt: link expiration timestamp, if provided by the API
    """

    try:
        requested_pages, invalid_tokens = _parse_page_range_1_based(page_range)
        if not requested_pages:
            raise ValueError("No pages specified. Provide page numbers/ranges like '1,3,5-7'.")

        # Determine pageCount so we can ignore out-of-range pages.
        properties = await client.get_pdf_properties(
            document_id,
            include_extended_info=False,
            include_page_info=False,
            password=password,
        )
        page_count = int((properties or {}).get("docInfo", {}).get("pageCount", 0) or 0)
        if page_count <= 0:
            raise ValueError("Unable to determine PDF pageCount; cannot validate page ranges.")

        in_range_pages = [p for p in requested_pages if 1 <= p <= page_count]
        out_of_range_pages = sorted([p for p in requested_pages if p > page_count])

        if not in_range_pages:
            ignored_bits: list[str] = []
            if out_of_range_pages:
                ignored_bits.append(f"out-of-range pages: {out_of_range_pages}")
            if invalid_tokens:
                ignored_bits.append(f"invalid tokens: {invalid_tokens}")
            suffix = f" Ignored {', '.join(ignored_bits)}." if ignored_bits else ""
            raise ValueError(f"No valid pages to delete for a {page_count}-page PDF.{suffix}")

        # Server-side schema uses PPOOperation with 1-based pages.
        # Sort descending to reduce ambiguity for implementations that apply deletes sequentially.
        in_range_pages_sorted = sorted(set(in_range_pages), reverse=True)

        # Guardrail: deleting all pages would produce an invalid/empty PDF.
        if len(in_range_pages_sorted) >= page_count:
            raise ValueError(
                "Refusing to delete all pages. Please keep at least one page in the document."
            )
        operations = [
            {
                "type": "DELETE_PAGES",
                "pages": in_range_pages_sorted,
            }
        ]

        config: dict[str, Any] = {"operations": operations}

        result = await client.pdf_manipulate(document_id, config, password=password)
        task_id = result["taskId"]
        ignored_notes: list[str] = []
        if out_of_range_pages:
            ignored_notes.append(f"out-of-range pages: {out_of_range_pages}")
        if invalid_tokens and invalid_tokens != ["<empty>"]:
            ignored_notes.append(f"invalid tokens: {invalid_tokens}")
        ignored_suffix = f" Ignored {', '.join(ignored_notes)}." if ignored_notes else ""

        register_task(
            task_id,
            "pdf_delete_pages",
            f"Deleted pages {sorted(in_range_pages_sorted)} from the PDF.{ignored_suffix}",
        )
        return format_task_submitted_response(
            task_id,
            "Page deletion submitted. Use get_task_result to check status and retrieve the download link.",
        )
    except Exception as error:
        return format_error_response(error)


@mcp.tool(annotations=WRITE_TOOL_ANNOTATIONS)
async def pdf_rotate_pages(
    document_id: str,
    page_range: str,
    rotation: Any,
    password: Optional[str] = None,
) -> str:
    """
    ⚠️ CRITICAL PREREQUISITE: You MUST call show_pdf_tools first to display the upload widget.
    The document_id parameter comes from the upload response in the widget.
    Rotate specific pages in a PDF using exact page numbers/ranges.

    Input uses 1-based page numbers (page 1 is the first page).

        Rotation can be provided as:
        - 0 / 90 / 180 / 270 (number)
        - "0" / "90" / "180" / "270" (string)
        - One of the API enum strings:
            ROTATE_0, ROTATE_CLOCKWISE_90, ROTATE_180, ROTATE_COUNTERCLOCKWISE_90.

    Example operation sent to pdf-manipulate:
        {
          "type": "ROTATE_PAGES",
          "pages": [4, 5, 6],
          "rotation": "ROTATE_CLOCKWISE_90"
        }

    Behavior:
    - Invalid tokens are ignored and reported in the message/resultData.
    - Out-of-range pages are ignored (based on PDF pageCount) and reported.

    Returns:
        JSON string with:
                - success, message
                - resultDocumentId: identifier of the updated PDF, returned for
                    follow-up operations on the generated file
                - shareUrl: public download URL for the updated PDF, when available
                - expiresAt: link expiration timestamp, if provided by the API
    """

    def _normalize_rotation(value: Any) -> str:
        if value is None:
            raise ValueError(
                "rotation is required. Use 0/90/180/270 or the rotation strings:ROTATE_0, ROTATE_CLOCKWISE_90, ROTATE_180, ROTATE_COUNTERCLOCKWISE_90."
            )

        if isinstance(value, bool):
            # bool is a subclass of int; treat as invalid.
            raise ValueError(
                "Invalid rotation. Use 0/90/180/270 or the rotation strings:ROTATE_0, ROTATE_CLOCKWISE_90, ROTATE_180, ROTATE_COUNTERCLOCKWISE_90."
            )

        if isinstance(value, (int, float)):
            if int(value) != value:
                raise ValueError("Rotation must be one of 90, 180, 270.")
            degrees = int(value)
            # Foxit API enum values (as observed from validation errors):
            # ROTATE_0, ROTATE_CLOCKWISE_90, ROTATE_180, ROTATE_COUNTERCLOCKWISE_90
            mapping = {
                0: "ROTATE_0",
                90: "ROTATE_CLOCKWISE_90",
                180: "ROTATE_180",
                270: "ROTATE_COUNTERCLOCKWISE_90",
            }
            if degrees not in mapping:
                raise ValueError("Rotation must be one of 0, 90, 180, 270.")
            return mapping[degrees]

        if isinstance(value, str):
            raw = value.strip()
            if raw in {"0", "90", "180", "270"}:
                return {
                    "0": "ROTATE_0",
                    "90": "ROTATE_CLOCKWISE_90",
                    "180": "ROTATE_180",
                    "270": "ROTATE_COUNTERCLOCKWISE_90",
                }[raw]

            upper = raw.upper()
            allowed = {
                "ROTATE_0",
                "ROTATE_CLOCKWISE_90",
                "ROTATE_180",
                "ROTATE_COUNTERCLOCKWISE_90",
            }
            if upper in allowed:
                return upper

        raise ValueError(
            "Invalid rotation. Use 0/90/180/270 or the API enum rotation strings."
        )

    try:
        requested_pages, invalid_tokens = _parse_page_range_1_based(page_range)
        if not requested_pages:
            raise ValueError("No pages specified. Provide page numbers/ranges like '1,3,5-7'.")

        rotation_enum = _normalize_rotation(rotation)

        # Determine pageCount so we can ignore out-of-range pages.
        properties = await client.get_pdf_properties(
            document_id,
            include_extended_info=False,
            include_page_info=False,
            password=password,
        )
        page_count = int((properties or {}).get("docInfo", {}).get("pageCount", 0) or 0)
        if page_count <= 0:
            raise ValueError("Unable to determine PDF pageCount; cannot validate page ranges.")

        in_range_pages = [p for p in requested_pages if 1 <= p <= page_count]
        out_of_range_pages = sorted([p for p in requested_pages if p > page_count])

        if not in_range_pages:
            ignored_bits: list[str] = []
            if out_of_range_pages:
                ignored_bits.append(f"out-of-range pages: {out_of_range_pages}")
            if invalid_tokens:
                ignored_bits.append(f"invalid tokens: {invalid_tokens}")
            suffix = f" Ignored {', '.join(ignored_bits)}." if ignored_bits else ""
            raise ValueError(f"No valid pages to rotate for a {page_count}-page PDF.{suffix}")

        in_range_pages_sorted = sorted(set(in_range_pages))

        operations = [
            {
                "type": "ROTATE_PAGES",
                "pages": in_range_pages_sorted,
                "rotation": rotation_enum,
            }
        ]

        config: dict[str, Any] = {"operations": operations}

        result = await client.pdf_manipulate(document_id, config, password=password)
        task_id = result["taskId"]
        ignored_notes: list[str] = []
        if out_of_range_pages:
            ignored_notes.append(f"out-of-range pages: {out_of_range_pages}")
        if invalid_tokens and invalid_tokens != ["<empty>"]:
            ignored_notes.append(f"invalid tokens: {invalid_tokens}")
        ignored_suffix = f" Ignored {', '.join(ignored_notes)}." if ignored_notes else ""

        register_task(
            task_id,
            "pdf_rotate_pages",
            f"Rotated pages {in_range_pages_sorted} using {rotation_enum}.{ignored_suffix}",
        )
        return format_task_submitted_response(
            task_id,
            "Page rotation submitted. Use get_task_result to check status and retrieve the download link.",
        )
    except Exception as error:
        return format_error_response(error)


@mcp.tool(annotations=WRITE_TOOL_ANNOTATIONS)
async def pdf_reorder_pages(
    document_id: str,
    page_range: str,
    target_position: Any,
    password: Optional[str] = None,
) -> str:
    """
    ⚠️ CRITICAL PREREQUISITE: You MUST call show_pdf_tools first to display the upload widget.
    The document_id parameter comes from the upload response in the widget.
    
    Move specified pages to a target position.

    Input uses 1-based page numbers (page 1 is the first page).

    Args:
        document_id: Document ID of the PDF
        page_range: Pages to move (e.g., "1,3,5-10")
        target_position: 1-based target position to insert the moved pages at
        password: Password if the PDF is password-protected

    Behavior:
    - Invalid tokens are ignored and reported in the message/resultData.
    - Out-of-range pages are ignored (based on PDF pageCount) and reported.

    Returns:
        JSON string with:
        - success, message
        - resultDocumentId: identifier of the updated PDF, returned for
            follow-up operations on the generated file
        - shareUrl: public download URL for the updated PDF, when available
        - expiresAt: link expiration timestamp, if provided by the API
    """

    def _normalize_target_position(value: Any) -> int:
        if value is None:
            raise ValueError("target_position is required and must be a positive integer (1-based).")

        if isinstance(value, bool):
            # bool is a subclass of int; treat as invalid.
            raise ValueError("target_position must be a positive integer (1-based).")

        if isinstance(value, (int, float)):
            if int(value) != value:
                raise ValueError("target_position must be an integer.")
            pos = int(value)
            if pos <= 0:
                raise ValueError("target_position must be >= 1 (1-based).")
            return pos

        if isinstance(value, str):
            raw = value.strip()
            if not raw:
                raise ValueError("target_position must be a positive integer (1-based).")
            try:
                pos = int(raw)
            except Exception:
                raise ValueError("target_position must be a positive integer (1-based).")
            if pos <= 0:
                raise ValueError("target_position must be >= 1 (1-based).")
            return pos

        raise ValueError("target_position must be a positive integer (1-based).")

    try:
        requested_pages, invalid_tokens = _parse_page_range_1_based(page_range)
        if not requested_pages:
            raise ValueError("No pages specified. Provide page numbers/ranges like '1,3,5-7'.")

        target_pos = _normalize_target_position(target_position)

        # Determine pageCount so we can ignore out-of-range pages and validate target position.
        properties = await client.get_pdf_properties(
            document_id,
            include_extended_info=False,
            include_page_info=False,
            password=password,
        )
        page_count = int((properties or {}).get("docInfo", {}).get("pageCount", 0) or 0)
        if page_count <= 0:
            raise ValueError("Unable to determine PDF pageCount; cannot validate page ranges.")

        requested_target_pos = target_pos
        if target_pos > page_count:
            target_pos = page_count

        in_range_pages = [p for p in requested_pages if 1 <= p <= page_count]
        out_of_range_pages = sorted([p for p in requested_pages if p > page_count])

        if not in_range_pages:
            ignored_bits: list[str] = []
            if out_of_range_pages:
                ignored_bits.append(f"out-of-range pages: {out_of_range_pages}")
            if invalid_tokens:
                ignored_bits.append(f"invalid tokens: {invalid_tokens}")
            suffix = f" Ignored {', '.join(ignored_bits)}." if ignored_bits else ""
            raise ValueError(f"No valid pages to move for a {page_count}-page PDF.{suffix}")

        # Keep natural order for a multi-page move.
        in_range_pages_sorted = sorted(set(in_range_pages))

        operations = [
            {
                "type": "MOVE_PAGES",
                "pages": in_range_pages_sorted,
                "targetPosition": target_pos,
            }
        ]

        config: dict[str, Any] = {"operations": operations}

        result = await client.pdf_manipulate(document_id, config, password=password)
        task_id = result["taskId"]
        ignored_notes: list[str] = []
        if out_of_range_pages:
            ignored_notes.append(f"out-of-range pages: {out_of_range_pages}")
        if invalid_tokens and invalid_tokens != ["<empty>"]:
            ignored_notes.append(f"invalid tokens: {invalid_tokens}")
        ignored_suffix = f" Ignored {', '.join(ignored_notes)}." if ignored_notes else ""

        register_task(
            task_id,
            "pdf_reorder_pages",
            f"Moved pages {in_range_pages_sorted} to position {target_pos}.{ignored_suffix}",
        )
        return format_task_submitted_response(
            task_id,
            "Page reorder submitted. Use get_task_result to check status and retrieve the download link.",
        )
    except Exception as error:
        return format_error_response(error)

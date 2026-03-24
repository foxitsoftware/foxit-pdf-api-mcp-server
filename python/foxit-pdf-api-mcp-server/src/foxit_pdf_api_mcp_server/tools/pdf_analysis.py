"""PDF Analysis tools for Foxit PDF API MCP Server."""

from typing import Optional

from ..resources import client, mcp
from ._base import format_error_response, format_task_submitted_response, register_task


WRITE_TOOL_ANNOTATIONS = {"readOnlyHint": False, "destructiveHint": False}


@mcp.tool(annotations=WRITE_TOOL_ANNOTATIONS)
async def pdf_compare(
    document_id1: str,
    document_id2: str,
    password1: Optional[str] = None,
    password2: Optional[str] = None,
) -> str:
    """Compare two PDF documents and generate a visual-diff PDF.

    Compares:
    - Text content differences
    - Visual layout changes
    - Added/removed content
    - Modified sections

    The result is a PDF report highlighting differences with:
    - Red annotations for deletions
    - Green annotations for additions
    - Yellow highlights for modifications

    Use cases:
    - Document version control
    - Contract review
    - Quality assurance
    - Change tracking

    Workflow:
    1. Call show_pdf_tools to display the upload widget
    2. Upload both PDFs using the widget
    3. Call this tool with both documentIds
    4. The tool automatically creates a share link and returns it

    This operation runs asynchronously. The tool returns a taskId immediately.
    Use get_task_result to poll for completion and retrieve the download link.

    Required dependencies:
    - document_id1 and document_id2 must be valid uploaded PDF document identifiers
    - password1 and password2 are only required when the corresponding PDFs are protected

    Returns:
        JSON string with:
        - success: operation was submitted successfully
        - taskId: use with get_task_result to check status and retrieve the result
        - message: describes next steps
    """
    try:
        config = {"compareType": "ALL", "resultType": "PDF"}
        result = await client.pdf_compare(
            document_id1, document_id2, password1, password2, config
        )
        task_id = result["taskId"]
        register_task(task_id, "pdf_compare", "PDFs compared successfully.")
        return format_task_submitted_response(
            task_id,
            "PDF comparison submitted. Use get_task_result to check status and retrieve the diff PDF.",
        )
    except Exception as error:
        return format_error_response(error)


# @mcp.tool()
# async def pdf_ocr(
#     document_id: str,
#     languages: Optional[list[str]] = None,
#     page_ranges: Optional[str] = None,
#     password: Optional[str] = None,
# ) -> str:
#     """Perform OCR (Optical Character Recognition) on a PDF document.

#     Converts scanned PDFs or image-based PDFs to searchable text PDFs.

#     Features:
#     - Multi-language support
#     - Preserves original layout
#     - Makes text searchable and copyable
#     - Enables text extraction

#     Configuration:
#     - languages: Array of language codes (e.g., ["en-US", "es-ES", "fr-FR"])
#     - pageRanges: Specific pages to OCR (e.g., "1-5,10-15")

#     Supported languages:
#     • CJK Languages: Chinese-Simplified (zh-CN, zh-Hans), Chinese-Traditional (zh-TW, zh-Hant), Japanese (ja-JP), Korean (ko-KR)
#     • European Languages: Basque (eu-ES), Bulgarian (bg-BG), Catalan (ca-ES), Croatian (hr-HR), Czech (cs-CZ), Danish (da-DK), Dutch (nl-NL, nl-BE), English (en-US, en-GB, en-AU, en-CA), Estonian (et-EE), Finnish (fi-FI), French (fr-FR, fr-CA, fr-BE, fr-CH), Galician (gl-ES), German (de-DE, de-AT, de-CH, de-LI, de-LU), Greek (el-GR), Hebrew (he-IL), Hungarian (hu-HU), Icelandic (is-IS), Italian (it-IT, it-CH), Latvian (lv-LV), Lithuanian (lt-LT), Maltese (mt-MT), Norwegian (nb-NO, nn-NO), Polish (pl-PL), Portuguese (pt-PT, pt-BR), Romanian (ro-RO), Russian (ru-RU), Serbian (sr-RS), Slovak (sk-SK), Slovenian (sl-SI), Spanish (es-ES, es-MX, es-AR, es-CL, es-CO, es-PE, es-VE), Swedish (sv-SE), Turkish (tr-TR), Ukrainian (uk-UA)
#     • Other Languages: Thai (th-TH)

#     Use cases:
#     - Make scanned documents searchable
#     - Extract text from image-based PDFs
#     - Create accessible versions of scanned content
#     - Convert paper documents to editable format

#     Workflow:
#     1. Call show_pdf_tools to display the upload widget
#     2. Upload scanned PDF using the widget
#     3. Call this tool with language configuration
#     4. The tool automatically creates a share link and returns it

#     Args:
#         document_id: Document ID of the PDF to OCR
#         languages: Language codes using standard format (e.g., ["en-US", "es-ES"], default: ["en-US"])
#         page_ranges: Pages to OCR (e.g., "1-5,10", default: all pages)
#         password: Password if PDF is password-protected

#     Returns:
#         JSON string with:
#         - success, taskId, message
#         - resultDocumentId
#         - shareUrl, expiresAt (when share link creation succeeds)
#         - shareLinkError (when share link creation fails)
#         - resultData.request: { languages, pageRanges, passwordProvided }
#     """
#     try:
#         config = {}
#         if languages:
#             config["languages"] = languages
#         if page_ranges:
#             config["pageRanges"] = page_ranges

#         result = await execute_and_wait(
#             client, lambda: client.pdf_ocr(
#                 document_id, config if config else None, password)
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
#             message="OCR completed successfully.",
#             result_data={
#                 "request": {
#                     "languages": languages or ["en-US"],
#                     "pageRanges": page_ranges,
#                     **(
#                         {"passwordProvided": True}
#                         if password is not None and password != ""
#                         else {}
#                     ),
#                 }
#             },
#             share_url=(share or {}).get("shareUrl"),
#             expires_at=(share or {}).get("expiresAt"),
#             token=(share or {}).get("token"),
#             share_link_error=share_error,
#         )
#     except Exception as error:
#         return format_error_response(error)


# @mcp.tool()
# async def pdf_structural_analysis(
#     document_id: str, password: Optional[str] = None
# ) -> str:
#     """Perform comprehensive structural analysis on a PDF document.

#     Extracts detailed document structure including:
#     - Hierarchical organization (titles, headings, paragraphs)
#     - Layout information with bounding boxes
#     - Table structures with cell relationships
#     - Images and visual elements
#     - Forms and interactive fields
#     - Document metadata
#     - Annotations and comments

#     Output format:
#     - ZIP archive containing:
#       - JSON file with structural analysis (Foxit PDF Extract API v1.0.7 schema)
#       - Extracted images and figures
#       - Table visualizations

#     Detected elements:
#     - title: Document titles and main headings
#     - head: Section headings with hierarchy levels
#     - paragraph: Text content blocks with styling
#     - table: Structured data with cell relationships
#     - image: Graphics, figures, and visual content
#     - form: Interactive form fields
#     - hyperlink: Links and references
#     - formula: Mathematical expressions

#     Use cases:
#     - Document content extraction
#     - Data mining from PDFs
#     - Accessibility improvements
#     - Content migration
#     - Document understanding for AI/ML

#     Workflow:
#     1. Call show_pdf_tools to display the upload widget
#     2. Upload PDF using the widget
#     3. Call this tool
#     4. The tool automatically creates a share link and returns it
#     5. Extract and process the JSON analysis file

#     Args:
#         document_id: Document ID of the PDF to analyze
#         password: Password if PDF is password-protected

#     Returns:
#         JSON string with:
#         - success, taskId, message
#         - resultDocumentId
#         - shareUrl, expiresAt (when share link creation succeeds)
#         - shareLinkError (when share link creation fails)
#     """
#     try:
#         result = await execute_and_wait(
#             client, lambda: client.pdf_structural_analysis(
#                 document_id, password)
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
#             message="Structural analysis completed.",
#             result_data={
#                 "request": {
#                     "passwordProvided": True,
#                 }
#             }
#             if password is not None and password != ""
#             else None,
#             share_url=(share or {}).get("shareUrl"),
#             expires_at=(share or {}).get("expiresAt"),
#             token=(share or {}).get("token"),
#             share_link_error=share_error,
#         )
#     except Exception as error:
#         return format_error_response(error)

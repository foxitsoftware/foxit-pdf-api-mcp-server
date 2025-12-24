"""PDF Analysis tools for Foxit PDF API MCP Server."""

from typing import Optional

from ..server import client, mcp
from ..utils import execute_and_wait
from ._base import format_error_response, format_success_response


@mcp.tool()
async def pdf_compare(
    document_id1: str,
    document_id2: str,
    password1: Optional[str] = None,
    password2: Optional[str] = None,
) -> str:
    """Compare two PDF documents and generate a comparison report.

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
    1. Upload both PDFs using upload_document tool
    2. Call this tool with both documentIds
    3. Download comparison report using download_document tool

    Args:
        document_id1: First PDF document ID
        document_id2: Second PDF document ID
        password1: Password for first PDF if protected
        password2: Password for second PDF if protected

    Returns:
        JSON string with comparison result and download information
    """
    try:
        result = await execute_and_wait(
            client, lambda: client.pdf_compare(document_id1, document_id2, password1, password2)
        )

        return format_success_response(
            task_id=result.get("taskId", ""),
            result_document_id=result.get("resultDocumentId"),
            message=f"PDFs compared successfully. Download comparison report using documentId: {result.get('resultDocumentId')}",
        )
    except Exception as error:
        return format_error_response(error)


@mcp.tool()
async def pdf_ocr(
    document_id: str,
    languages: Optional[list[str]] = None,
    page_ranges: Optional[str] = None,
    password: Optional[str] = None,
) -> str:
    """Perform OCR (Optical Character Recognition) on a PDF document.

    Converts scanned PDFs or image-based PDFs to searchable text PDFs.

    Features:
    - Multi-language support
    - Preserves original layout
    - Makes text searchable and copyable
    - Enables text extraction

    Configuration:
    - languages: Array of language codes (e.g., ["en-US", "es-ES", "fr-FR"])
    - pageRanges: Specific pages to OCR (e.g., "1-5,10-15")

    Supported languages:
    • CJK Languages: Chinese-Simplified (zh-CN, zh-Hans), Chinese-Traditional (zh-TW, zh-Hant), Japanese (ja-JP), Korean (ko-KR)
    • European Languages: Basque (eu-ES), Bulgarian (bg-BG), Catalan (ca-ES), Croatian (hr-HR), Czech (cs-CZ), Danish (da-DK), Dutch (nl-NL, nl-BE), English (en-US, en-GB, en-AU, en-CA), Estonian (et-EE), Finnish (fi-FI), French (fr-FR, fr-CA, fr-BE, fr-CH), Galician (gl-ES), German (de-DE, de-AT, de-CH, de-LI, de-LU), Greek (el-GR), Hebrew (he-IL), Hungarian (hu-HU), Icelandic (is-IS), Italian (it-IT, it-CH), Latvian (lv-LV), Lithuanian (lt-LT), Maltese (mt-MT), Norwegian (nb-NO, nn-NO), Polish (pl-PL), Portuguese (pt-PT, pt-BR), Romanian (ro-RO), Russian (ru-RU), Serbian (sr-RS), Slovak (sk-SK), Slovenian (sl-SI), Spanish (es-ES, es-MX, es-AR, es-CL, es-CO, es-PE, es-VE), Swedish (sv-SE), Turkish (tr-TR), Ukrainian (uk-UA)
    • Other Languages: Thai (th-TH)

    Use cases:
    - Make scanned documents searchable
    - Extract text from image-based PDFs
    - Create accessible versions of scanned content
    - Convert paper documents to editable format

    Workflow:
    1. Upload scanned PDF using upload_document tool
    2. Call this tool with language configuration
    3. Download searchable PDF using download_document tool

    Args:
        document_id: Document ID of the PDF to OCR
        languages: Language codes using standard format (e.g., ["en-US", "es-ES"], default: ["en-US"])
        page_ranges: Pages to OCR (e.g., "1-5,10", default: all pages)
        password: Password if PDF is password-protected

    Returns:
        JSON string with OCR result and download information
    """
    try:
        config = {}
        if languages:
            config["languages"] = languages
        if page_ranges:
            config["pageRanges"] = page_ranges

        result = await execute_and_wait(
            client, lambda: client.pdf_ocr(document_id, config if config else None, password)
        )

        return format_success_response(
            task_id=result.get("taskId", ""),
            result_document_id=result.get("resultDocumentId"),
            languages=languages or ["en-US"],
            message=f"OCR completed successfully. Download searchable PDF using documentId: {result.get('resultDocumentId')}",
        )
    except Exception as error:
        return format_error_response(error)


@mcp.tool()
async def pdf_structural_analysis(
    document_id: str, password: Optional[str] = None
) -> str:
    """Perform comprehensive structural analysis on a PDF document.

    Extracts detailed document structure including:
    - Hierarchical organization (titles, headings, paragraphs)
    - Layout information with bounding boxes
    - Table structures with cell relationships
    - Images and visual elements
    - Forms and interactive fields
    - Document metadata
    - Annotations and comments

    Output format:
    - ZIP archive containing:
      - JSON file with structural analysis (Foxit PDF Extract API v1.0.7 schema)
      - Extracted images and figures
      - Table visualizations

    Detected elements:
    - title: Document titles and main headings
    - head: Section headings with hierarchy levels
    - paragraph: Text content blocks with styling
    - table: Structured data with cell relationships
    - image: Graphics, figures, and visual content
    - form: Interactive form fields
    - hyperlink: Links and references
    - formula: Mathematical expressions

    Use cases:
    - Document content extraction
    - Data mining from PDFs
    - Accessibility improvements
    - Content migration
    - Document understanding for AI/ML

    Workflow:
    1. Upload PDF using upload_document tool
    2. Call this tool
    3. Download ZIP result using download_document tool
    4. Extract and process the JSON analysis file

    Args:
        document_id: Document ID of the PDF to analyze
        password: Password if PDF is password-protected

    Returns:
        JSON string with analysis result and download information
    """
    try:
        result = await execute_and_wait(
            client, lambda: client.pdf_structural_analysis(document_id, password)
        )

        return format_success_response(
            task_id=result.get("taskId", ""),
            result_document_id=result.get("resultDocumentId"),
            message=f"Structural analysis completed. Download ZIP archive using documentId: {result.get('resultDocumentId')}",
        )
    except Exception as error:
        return format_error_response(error)

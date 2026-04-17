"""PDF security tools: protect and remove password protection."""

import json
from typing import Any, Optional

from ..resources import client, mcp
from ..utils import execute_and_wait
from ._base import format_error_response, format_task_submitted_response, register_task
from .share_link_helper import try_create_share_link


WRITE_TOOL_ANNOTATIONS = {"readOnlyHint": False, "destructiveHint": False}
DESTRUCTIVE_TOOL_ANNOTATIONS = {"readOnlyHint": False, "destructiveHint": True}


@mcp.tool(annotations=WRITE_TOOL_ANNOTATIONS)
async def pdf_protect(
    document_id: str,
    user_password: Optional[str] = None,
    owner_password: Optional[str] = None,
    allow_printing: bool = True,
    allow_copying: bool = True,
    allow_editing: bool = True,
) -> str:
    """
    ⚠️ CRITICAL PREREQUISITE: You MUST call show_pdf_tools first to display the upload widget.
    The document_id parameter comes from the upload response in the widget.

    Add password protection and permissions to a PDF document.

    Features:
    - User password: Required to open the document
    - Owner password: Required to change permissions
    - Granular permissions control
    - Strong encryption (128-bit or 256-bit)

    Password types:
    - User password: Required to view the PDF
    - Owner password: Required to change restrictions (can also open the PDF)

    Permissions:
    - Printing: Allow/deny printing
    - Copying: Allow/deny text and image copying
    - Editing: Allow/deny content modification

    Maximum file size: 100MB

    Args:
        document_id: Document ID of the PDF to protect
        user_password: Password required to open the PDF (optional)
        owner_password: Password required to change permissions (optional)
        allow_printing: Allow printing (default: True)
        allow_copying: Allow copying content (default: True)
        allow_editing: Allow editing content (default: True)

    Returns:
        JSON string with:
        - success, message
        - resultDocumentId: identifier of the protected PDF, returned for
            follow-up operations on the generated file
        - shareUrl: public download URL for the protected PDF, when available
        - expiresAt: link expiration timestamp, if provided by the API
    """
    try:
        inner: dict[str, Any] = {}

        if user_password:
            inner["userPassword"] = user_password
        if owner_password:
            inner["ownerPassword"] = owner_password

        # userPermissions only takes effect when ownerPassword is set.
        if owner_password:
            permissions: list[str] = []
            if allow_printing:
                permissions += ["PRINT_NORMAL_QUALITY", "PRINT_HIGH_QUALITY"]
            if allow_copying:
                permissions.append("COPY_CONTENT")
            if allow_editing:
                permissions += [
                    "EDIT_CONTENT",
                    "EDIT_FILL_AND_SIGN_FORM_FIELDS",
                    "EDIT_ANNOTATION",
                    "EDIT_DOCUMENT_ASSEMBLY",
                ]
            inner["userPermissions"] = permissions

        config: dict[str, Any] = {"config": inner} if inner else {}

        result = await execute_and_wait(client, lambda: client.pdf_protect(document_id, config))

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
            "message": "PDF protected successfully."
            if (share or {}).get("shareUrl")
            else "PDF protected successfully, but no share link was created.",
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
async def pdf_remove_password(document_id: str, password: str) -> str:
    """
    ⚠️ CRITICAL PREREQUISITE: You MUST call show_pdf_tools first to display the upload widget.
    The document_id parameter comes from the upload response in the widget.

    Remove password protection from a PDF document.

    Requirements:
    - You must provide the correct password (user or owner)
    - Only works if you know the password

    Use cases:
    - Remove restrictions from your own PDFs
    - Unlock PDFs for processing
    - Prepare PDFs for archiving

    Maximum file size: 100MB

    Args:
        document_id: Document ID of the password-protected PDF
        password: The user or owner password for the PDF

    Returns:
        JSON string with:
        - success, message
        - resultDocumentId: identifier of the unlocked PDF, returned for
          follow-up operations on the generated file
        - shareUrl: public download URL for the unlocked PDF, when available
        - expiresAt: link expiration timestamp, if provided by the API
    """
    try:
        result = await execute_and_wait(
            client, lambda: client.pdf_remove_password(document_id, password)
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
            "message": "Password removed successfully."
            if (share or {}).get("shareUrl")
            else "Password removed successfully, but no share link was created.",
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


@mcp.tool(annotations=DESTRUCTIVE_TOOL_ANNOTATIONS)
async def pdf_redact(
    document_id: str,
    texts: Optional[list[str]] = None,
    overlay_text: Optional[str] = None,
    page_range: Optional[str] = None,
    case_sensitive: bool = False,
    whole_words_only: bool = False,
    redact_form_fields: bool = False,
    form_field_types: Optional[list[str]] = None,
    apply_immediately: bool = True,
) -> str:
    """
    ⚠️ CRITICAL PREREQUISITE: You MUST call show_pdf_tools first to display the upload widget.
    The document_id parameter comes from the upload response in the widget.

    Permanently redact sensitive content from a PDF document.

    Supports two modes (can be combined):
    - Text-based: find and permanently remove specific words or phrases
    - Form-field: redact the content of form fields

    ⚠️ When apply_immediately is True (default), redactions are PERMANENT and IRREVERSIBLE.
    Set apply_immediately=False to preview marks without removing the underlying content.

    Maximum file size: 100MB

    This operation runs asynchronously. The tool returns a taskId immediately.
    Use get_task_result to poll for completion and retrieve the download link.

    Args:
        document_id: Document ID of the PDF to redact
        texts: List of words or phrases to find and redact.
            Example: ["John Smith", "jane.doe@example.com", "SSN"]
        overlay_text: Optional label shown inside every redaction mark, e.g. "[REDACTED]".
            Omit for a solid filled box.
        page_range: Restrict text search to specific pages, e.g. "1-3", "all" (default: all pages)
        case_sensitive: Match exact case when searching (default: False)
        whole_words_only: Match whole words only (default: False)
        redact_form_fields: When True, redact form field content in the document (default: False)
        form_field_types: Limit form field redaction to specific types. Omit to redact all types.
            Valid values: PUSH_BUTTON, CHECK_BOX, RADIO_BUTTON, COMBO_BOX, LIST_BOX, TEXT_FIELD, SIGNATURE
        apply_immediately: True (default) = permanently apply redactions. False = place marks only.

    Returns:
        JSON string with:
        - success: operation was submitted successfully
        - taskId: use with get_task_result to check status and retrieve the result
        - message: describes next steps
    """
    try:
        if not texts and not redact_form_fields:
            raise ValueError(
                "Provide at least one of: texts (list of words/phrases to redact) or redact_form_fields=True."
            )

        config: dict[str, Any] = {}

        if texts:
            config["redactTextList"] = [
                {"text": t, **({"overlayText": overlay_text} if overlay_text else {})}
                for t in texts
            ]
            search_options: dict[str, Any] = {}
            if case_sensitive:
                search_options["caseSensitive"] = True
            if whole_words_only:
                search_options["wholeWordsOnly"] = True
            if page_range:
                search_options["pageRange"] = page_range
            if search_options:
                config["textSearchOptions"] = search_options

        if redact_form_fields:
            field_config: dict[str, Any] = {}
            if form_field_types:
                field_config["fieldTypes"] = form_field_types
            config["formFieldRedact"] = field_config

        if not apply_immediately:
            config["applyImmediately"] = False

        result = await client.pdf_redact(document_id, config)
        task_id = result["taskId"]
        register_task(task_id, "pdf_redact", "PDF redacted successfully.")
        return format_task_submitted_response(
            task_id,
            "PDF redaction submitted. Use get_task_result to check status and retrieve the download link.",
        )
    except Exception as error:
        return format_error_response(error)

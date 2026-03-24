"""PDF Forms tools for Foxit PDF API MCP Server."""

from typing import Any, Optional

from ..resources import client, mcp
from ..utils import execute_and_wait
from ._base import format_error_response, format_success_response
from .share_link_helper import try_create_share_link


async def export_pdf_form_data(
    document_id: str, password: Optional[str] = None
) -> str:
    """⚠️ CRITICAL PREREQUISITE: You MUST call show_pdf_tools first to display the upload widget.
    The document_id parameter comes from the upload response in the widget.
    
    Extract form data from a PDF and return it as JSON.

    Exports all filled form field values from a PDF form.

    Output: JSON file with form data structure where:
    - Keys are field names (including hierarchical/nested names)
    - Values are the field contents

    Example output JSON:
    ```json
    {
      "name": {
        "first": "John",
        "last": "Doe"
      },
      "email": "john@example.com",
      "dob": "01/14/2025",
      "address": {
        "city": "Springfield",
        "state": "IL"
      }
    }
    ```

    Use cases:
    - Extract form submissions
    - Data collection from PDF forms
    - Form data migration
    - Automated data processing
    - Integration with databases

    Workflow:
    1. Upload filled PDF form using upload_document tool
    2. Call this tool
    3. The tool automatically creates a share link and returns it
    4. Parse JSON to access form data

    Args:
        document_id: Document ID of the PDF form
        password: Password if PDF is password-protected

    Returns:
        JSON string with:
        - success, taskId, message
        - resultDocumentId
        - shareUrl, expiresAt (when share link creation succeeds)
        - shareLinkError (when share link creation fails)
        - resultData.request: { passwordProvided }
    """
    try:
        result = await execute_and_wait(
            client, lambda: client.export_pdf_form_data(document_id, password)
        )

        result_document_id = result.get("resultDocumentId")
        share, share_error = (None, None)
        if result_document_id:
            share, share_error = await try_create_share_link(
                client.create_share_link,
                document_id=result_document_id,
                expiration_minutes=None,
                filename=None,
            )

        return format_success_response(
            task_id=result.get("taskId", ""),
            result_document_id=result_document_id,
            message="Form data exported successfully.",
            result_data={
                "request": {
                    "passwordProvided": True,
                }
            }
            if password is not None and password != ""
            else None,
            share_url=(share or {}).get("shareUrl"),
            expires_at=(share or {}).get("expiresAt"),
            token=(share or {}).get("token"),
            share_link_error=share_error,
        )
    except Exception as error:
        return format_error_response(error)


async def import_pdf_form_data(
    document_id: str, form_data: dict[str, Any], password: Optional[str] = None
) -> str:
    """⚠️ CRITICAL PREREQUISITE: You MUST call show_pdf_tools first to display the upload widget.
    The document_id parameter comes from the upload response in the widget.
    
    Populate a PDF form with data provided as JSON.

    Fills PDF form fields with values from a JSON object.

    Input: JSON object where:
    - Keys match form field names (including hierarchical/nested names)
    - Values are the data to populate

    Example input JSON:
    ```json
    {
      "name": {
        "first": "John",
        "last": "Doe"
      },
      "email": "john@example.com",
      "dob": "01/14/2025",
      "address": {
        "city": "Springfield",
        "state": "IL"
      }
    }
    ```

    This will populate fields:
    - name.first → "John"
    - name.last → "Doe"
    - email → "john@example.com"
    - etc.

    Use cases:
    - Automated form filling
    - Bulk form population
    - Template processing
    - Document generation from data
    - Personalized document creation

    Workflow:
    1. Upload blank PDF form using upload_document tool
    2. Prepare form data as JSON object
    3. Call this tool with documentId and form data
    4. The tool automatically creates a share link and returns it

    Args:
        document_id: Document ID of the PDF form template
        form_data: JSON object with form field names and values
        password: Password if PDF is password-protected

    Returns:
        JSON string with:
        - success, taskId, message
        - resultDocumentId
        - shareUrl, expiresAt (when share link creation succeeds)
        - shareLinkError (when share link creation fails)
        - resultData.request: { fieldsCount, passwordProvided }
    """
    try:
        result = await execute_and_wait(
            client, lambda: client.import_pdf_form_data(document_id, form_data, password)
        )

        result_document_id = result.get("resultDocumentId")
        share, share_error = (None, None)
        if result_document_id:
            share, share_error = await try_create_share_link(
                client.create_share_link,
                document_id=result_document_id,
                expiration_minutes=None,
                filename=None,
            )

        return format_success_response(
            task_id=result.get("taskId", ""),
            result_document_id=result_document_id,
            message="Form data imported successfully.",
            result_data={
                "request": {
                    "fieldsCount": len(form_data),
                    **(
                        {"passwordProvided": True}
                        if password is not None and password != ""
                        else {}
                    ),
                },
            },
            share_url=(share or {}).get("shareUrl"),
            expires_at=(share or {}).get("expiresAt"),
            token=(share or {}).get("token"),
            share_link_error=share_error,
        )
    except Exception as error:
        return format_error_response(error)

"""PDF Forms tools for Foxit PDF API MCP Server."""

from typing import Any, Optional

from ..server import client, mcp
from ..utils import execute_and_wait
from ._base import format_error_response, format_success_response


@mcp.tool()
async def export_pdf_form_data(
    document_id: str, password: Optional[str] = None
) -> str:
    """Extract form data from a PDF and return it as JSON.

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
    3. Download JSON file using download_document tool
    4. Parse JSON to access form data

    Args:
        document_id: Document ID of the PDF form
        password: Password if PDF is password-protected

    Returns:
        JSON string with form data export result and download information
    """
    try:
        result = await execute_and_wait(
            client, lambda: client.export_pdf_form_data(document_id, password)
        )

        return format_success_response(
            task_id=result.get("taskId", ""),
            result_document_id=result.get("resultDocumentId"),
            message=f"Form data exported successfully. Download JSON using documentId: {result.get('resultDocumentId')}",
        )
    except Exception as error:
        return format_error_response(error)


@mcp.tool()
async def import_pdf_form_data(
    document_id: str, form_data: dict[str, Any], password: Optional[str] = None
) -> str:
    """Populate a PDF form with data provided as JSON.

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
    4. Download populated PDF using download_document tool

    Args:
        document_id: Document ID of the PDF form template
        form_data: JSON object with form field names and values
        password: Password if PDF is password-protected

    Returns:
        JSON string with form data import result and download information
    """
    try:
        result = await execute_and_wait(
            client, lambda: client.import_pdf_form_data(document_id, form_data, password)
        )

        return format_success_response(
            task_id=result.get("taskId", ""),
            result_document_id=result.get("resultDocumentId"),
            fields_count=len(form_data),
            message=f"Form data imported successfully. Download populated PDF using documentId: {result.get('resultDocumentId')}",
        )
    except Exception as error:
        return format_error_response(error)

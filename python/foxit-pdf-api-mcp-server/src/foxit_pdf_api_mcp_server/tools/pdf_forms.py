"""PDF Forms tools for Foxit PDF API MCP Server."""

import json
from typing import Any, Optional

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
async def export_pdf_form_data(
    documentId: str, password: Optional[str] = None
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
            client, lambda: client.export_pdf_form_data(documentId, password)
        )

        return json.dumps(
            {
                "success": True,
                "taskId": result["taskId"],
                "resultDocumentId": result.get("resultDocumentId"),
                "message": (
                    "Form data exported successfully. Download JSON using documentId: "
                    f"{result.get('resultDocumentId')}"
                ),
            }
        )
    except Exception as error:
        return _error_payload(error, "EXPORT_FORM_FAILED")


@mcp.tool()
async def import_pdf_form_data(
    documentId: str,
    formData: dict[str, Any],
    password: Optional[str] = None,
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
            client, lambda: client.import_pdf_form_data(documentId, formData, password)
        )

        return json.dumps(
            {
                "success": True,
                "taskId": result["taskId"],
                "resultDocumentId": result.get("resultDocumentId"),
                "fieldsCount": len(formData),
                "message": (
                    "Form data imported successfully. Download populated PDF using documentId: "
                    f"{result.get('resultDocumentId')}"
                ),
            }
        )
    except Exception as error:
        return _error_payload(error, "IMPORT_FORM_FAILED")

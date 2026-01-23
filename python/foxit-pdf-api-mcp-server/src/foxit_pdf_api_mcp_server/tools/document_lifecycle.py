"""Document lifecycle tools: upload, download, delete."""

import base64
import json
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from ..server import client, mcp


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
async def upload_document(
    resourceUri: Optional[str] = None,
    fileContent: Optional[str] = None,
    fileName: Optional[str] = None,
) -> str:
    """
    Upload a document for processing with Foxit PDF API.

    Returns a documentId that can be used in subsequent operations.

    Supported formats:
    - PDF documents
    - Microsoft Office documents (Word, Excel, PowerPoint)
    - Images (PNG, JPEG, TIFF, BMP, GIF)
    - Text files
    - HTML files

    Maximum file size: 100MB

    Input options (choose one):
    1. resource_uri: MCP resource URI (recommended, e.g., file:///path/to/file.pdf)
    2. file_content: Base64-encoded file content + file_name (fallback)

    Usage: Always call this tool first before performing any PDF operations.

    Args:
        resource_uri: MCP resource URI to read the file from (recommended)
        file_content: Base64-encoded file content (fallback when resources unavailable)
        file_name: File name (required when using file_content, optional for resource_uri)

    Returns:
        JSON string with success status, documentId, and message
    """
    try:
        file_buffer: bytes
        actual_file_name: str

        # Option 1: Read from file:// resource URI
        if resourceUri:
            try:
                if resourceUri.startswith("file://"):
                    parsed = urlparse(resourceUri)
                    # parsed.path is URL-decoded and uses forward slashes
                    file_path = parsed.path.lstrip("/") if parsed.netloc else parsed.path
                    path = Path(file_path)
                    file_buffer = path.read_bytes()
                    actual_file_name = fileName or path.name
                else:
                    raise ValueError(
                        f"Unsupported resource URI scheme: {resourceUri}. "
                        "Use file:// or provide file_content"
                    )
            except Exception as e:
                raise ValueError(
                    f"Failed to read resource: {str(e)}. "
                    "Try using fileContent (base64) instead."
                )

        # Option 2: Decode base64 content
        elif fileContent:
            if not fileName:
                raise ValueError("fileName is required when using fileContent")
            file_buffer = base64.b64decode(fileContent)
            actual_file_name = fileName

        # No valid input provided
        else:
            raise ValueError("Must provide either resourceUri or fileContent")

        # Upload to API
        response = await client.upload_document(file_buffer, actual_file_name)

        return json.dumps(
            {
                "success": True,
                "documentId": response["documentId"],
                "fileName": actual_file_name,
                "message": (
                    "Document uploaded successfully. "
                    f"Use documentId '{response['documentId']}' in other operations."
                ),
            }
        )

    except Exception as error:
        return _error_payload(error, "UPLOAD_FAILED")


@mcp.tool()
async def download_document(
    documentId: str,
    outputPath: str,
    filename: Optional[str] = None,
) -> str:
    """
    Download a document from Foxit PDF API.

    Use this tool to download:
    - Previously uploaded documents
    - Documents generated from PDF operations (using resultDocumentId from task completion)

    The document will be saved to the specified output path.

    Args:
        document_id: The document ID to download (from upload or operation result)
        output_path: Absolute path where the downloaded file should be saved
        filename: Optional filename to use when downloading (defaults to documentId)

    Returns:
        JSON string with success status and file information
    """
    try:
        # Download from API
        content = await client.download_document(documentId, filename)

        # Write to output path
        output = Path(outputPath)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(content)

        return json.dumps(
            {
                "success": True,
                "documentId": documentId,
                "outputPath": str(output),
                "size": len(content),
                "message": f"Document downloaded successfully to {str(output)}",
            }
        )

    except Exception as error:
        return _error_payload(error, "DOWNLOAD_FAILED")


@mcp.tool()
async def delete_document(documentId: str) -> str:
    """
    Delete a document from Foxit PDF API.

    This will permanently delete the document from the cloud storage.
    Use this to clean up temporary documents after processing.

    Args:
        document_id: The document ID to delete

    Returns:
        JSON string with success status
    """
    try:
        await client.delete_document(documentId)

        return json.dumps(
            {
                "success": True,
                "documentId": documentId,
                "message": f"Document {documentId} deleted successfully",
            }
        )

    except Exception as error:
        return _error_payload(error, "DELETE_FAILED")

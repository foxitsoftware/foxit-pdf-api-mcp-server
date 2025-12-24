"""Document lifecycle tools: upload, download, delete."""

import base64
from pathlib import Path
from typing import Optional

from ..server import client, mcp
from ._base import format_error_response, format_success_response


@mcp.tool()
async def upload_document(
    resource_uri: Optional[str] = None,
    file_content: Optional[str] = None,
    file_name: Optional[str] = None,
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

        # Option 1: Read from MCP resource (recommended)
        if resource_uri:
            try:
                # For now, assume file:// URI and read directly
                # In production, would use MCP resource reading
                if resource_uri.startswith("file://"):
                    file_path = resource_uri.replace("file://", "")
                    path = Path(file_path)
                    file_buffer = path.read_bytes()
                    actual_file_name = file_name or path.name
                else:
                    raise ValueError(
                        f"Unsupported resource URI scheme: {resource_uri}. "
                        "Use file:// or provide file_content"
                    )
            except Exception as e:
                raise ValueError(
                    f"Failed to read resource: {str(e)}. "
                    "Try using file_content (base64) instead."
                )

        # Option 2: Decode base64 content
        elif file_content:
            if not file_name:
                raise ValueError("file_name is required when using file_content")
            file_buffer = base64.b64decode(file_content)
            actual_file_name = file_name

        # No valid input provided
        else:
            raise ValueError("Must provide either resource_uri or file_content")

        # Upload to API
        response = await client.upload_document(file_buffer, actual_file_name)

        return format_success_response(
            task_id="",  # Upload doesn't return a task
            result_document_id=response["documentId"],
            message=f"Document uploaded successfully. Use documentId '{response['documentId']}' in other operations.",
        )

    except Exception as error:
        return format_error_response(error)


@mcp.tool()
async def download_document(
    document_id: str,
    output_path: str,
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
        content = await client.download_document(document_id, filename)

        # Write to output path
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(content)

        return format_success_response(
            task_id="",  # Download doesn't return a task
            message=f"Document downloaded successfully to: {output_path}",
            result_data={
                "outputPath": str(output),
                "fileSize": len(content),
            },
        )

    except Exception as error:
        return format_error_response(error)


@mcp.tool()
async def delete_document(document_id: str) -> str:
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
        await client.delete_document(document_id)

        return format_success_response(
            task_id="",  # Delete doesn't return a task
            message=f"Document {document_id} deleted successfully",
        )

    except Exception as error:
        return format_error_response(error)

from typing import Any, Optional

import httpx

from ..types.api import DocumentUploadResponse, OperationResponse, TaskResponse


class FoxitAPIError(Exception):
    """Base exception for Foxit API errors."""

    def __init__(
        self,
        message: str,
        code: str = "API_ERROR",
        status_code: Optional[int] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Initialize API error.

        Args:
            message: Error message
            code: Error code
            status_code: HTTP status code
            details: Additional error details
        """
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class FoxitPDFClient:
    """
    HTTP Client for Foxit PDF API.

    Handles all direct API interactions without MCP-specific logic.
    """

    def __init__(
        self,
        base_url: str,
        client_id: str,
        client_secret: str,
        default_timeout: int = 300,
        poll_interval: int = 2,
        max_retries: int = 3,
    ) -> None:
        """
        Initialize Foxit PDF API client.

        Args:
            base_url: API base URL
            client_id: Client ID for authentication
            client_secret: Client secret for authentication
            default_timeout: Default timeout in seconds
            poll_interval: Poll interval in seconds
            max_retries: Maximum number of retries
        """
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.default_timeout = default_timeout
        self.poll_interval = poll_interval
        self.max_retries = max_retries

        # Create async HTTP client
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(default_timeout), follow_redirects=True
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    def _get_auth_headers(self) -> dict[str, str]:
        """
        Get authentication headers.

        Returns:
            Dictionary with authentication headers
        """
        return {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

    async def _make_request(
        self,
        method: str,
        path: str,
        headers: Optional[dict[str, str]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Make HTTP request with authentication.

        Args:
            method: HTTP method
            path: API path (relative to base_url)
            headers: Additional headers
            **kwargs: Additional arguments for httpx request

        Returns:
            HTTP response

        Raises:
            FoxitAPIError: If request fails
        """
        url = f"{self.base_url}/{path.lstrip('/')}"
        request_headers = self._get_auth_headers()

        if headers:
            request_headers.update(headers)

        try:
            response = await self._client.request(
                method=method, url=url, headers=request_headers, **kwargs
            )
            return response
        except httpx.TimeoutException as e:
            raise FoxitAPIError(
                message=f"Request timeout: {str(e)}", code="TIMEOUT"
            ) from e
        except httpx.RequestError as e:
            raise FoxitAPIError(
                message=f"Request failed: {str(e)}", code="REQUEST_FAILED"
            ) from e

    async def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """
        Handle API response and check for errors.

        Args:
            response: HTTP response

        Returns:
            Parsed JSON response

        Raises:
            FoxitAPIError: If response indicates error
        """
        if response.status_code >= 400:
            try:
                error_data = response.json()
                raise FoxitAPIError(
                    message=error_data.get("message", "API request failed"),
                    code=error_data.get("code", "API_ERROR"),
                    status_code=response.status_code,
                    details=error_data,
                )
            except ValueError:
                raise FoxitAPIError(
                    message=f"HTTP {response.status_code}: {response.text}",
                    code="HTTP_ERROR",
                    status_code=response.status_code,
                )

        try:
            return response.json()
        except ValueError as e:
            raise FoxitAPIError(
                message=f"Invalid JSON response: {str(e)}", code="INVALID_RESPONSE"
            ) from e

    # Document operations

    async def upload_document(
        self, file_content: bytes, file_name: str
    ) -> DocumentUploadResponse:
        """
        Upload a document.

        Args:
            file_content: File content as bytes
            file_name: Name of the file

        Returns:
            Upload response with documentId
        """
        files = {"file": (file_name, file_content, "application/octet-stream")}

        response = await self._make_request(
            "POST", "/api/documents/upload", files=files
        )

        data = await self._handle_response(response)
        return DocumentUploadResponse(documentId=data["documentId"])

    async def download_document(
        self, document_id: str, filename: Optional[str] = None
    ) -> bytes:
        """
        Download a document.

        Args:
            document_id: Document ID to download
            filename: Optional filename for download

        Returns:
            Document content as bytes
        """
        path = f"/api/documents/{document_id}/download"
        if filename:
            path += f"?filename={filename}"

        response = await self._make_request("GET", path)

        if response.status_code >= 400:
            await self._handle_response(response)

        return response.content

    async def delete_document(self, document_id: str) -> None:
        """
        Delete a document.

        Args:
            document_id: Document ID to delete
        """
        response = await self._make_request("DELETE", f"/api/documents/{document_id}")
        if response.status_code >= 400:
            await self._handle_response(response)

    async def get_task_status(self, task_id: str) -> TaskResponse:
        """
        Get task status.

        Args:
            task_id: Task ID to check

        Returns:
            Task status response
        """
        response = await self._make_request("GET", f"/api/tasks/{task_id}")
        data = await self._handle_response(response)
        return TaskResponse(**data)

    # PDF Creation operations

    async def pdf_from_word(self, document_id: str) -> OperationResponse:
        """
        Convert Word document to PDF.

        Args:
            document_id: Document ID of Word file

        Returns:
            Operation response with taskId
        """
        response = await self._make_request(
            "POST",
            "/api/documents/create/pdf-from-word",
            json={"documentId": document_id},
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_from_excel(self, document_id: str) -> OperationResponse:
        """Convert Excel document to PDF."""
        response = await self._make_request(
            "POST",
            "/api/documents/create/pdf-from-excel",
            json={"documentId": document_id},
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_from_ppt(self, document_id: str) -> OperationResponse:
        """Convert PowerPoint document to PDF."""
        response = await self._make_request(
            "POST",
            "/api/documents/create/pdf-from-ppt",
            json={"documentId": document_id},
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_from_html(
        self, document_id: str, config: Optional[dict[str, Any]] = None
    ) -> OperationResponse:
        """Convert HTML to PDF."""
        payload: dict[str, Any] = {"documentId": document_id}
        if config:
            payload.update(config)

        response = await self._make_request(
            "POST", "/api/documents/create/pdf-from-html", json=payload
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_from_url(
        self, url: str, config: Optional[dict[str, Any]] = None
    ) -> OperationResponse:
        """Convert URL to PDF."""
        payload: dict[str, Any] = {"url": url}
        if config:
            payload.update(config)

        response = await self._make_request(
            "POST", "/api/documents/create/pdf-from-url", json=payload
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_from_text(self, document_id: str) -> OperationResponse:
        """Convert text file to PDF."""
        response = await self._make_request(
            "POST",
            "/api/documents/create/pdf-from-text",
            json={"documentId": document_id},
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_from_image(self, document_id: str) -> OperationResponse:
        """Convert image to PDF."""
        response = await self._make_request(
            "POST",
            "/api/documents/create/pdf-from-image",
            json={"documentId": document_id},
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    # PDF Conversion operations

    async def pdf_to_word(self, document_id: str) -> OperationResponse:
        """Convert PDF to Word."""
        response = await self._make_request(
            "POST",
            "/api/documents/convert/pdf-to-word",
            json={"documentId": document_id},
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_to_excel(self, document_id: str) -> OperationResponse:
        """Convert PDF to Excel."""
        response = await self._make_request(
            "POST",
            "/api/documents/convert/pdf-to-excel",
            json={"documentId": document_id},
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_to_ppt(self, document_id: str) -> OperationResponse:
        """Convert PDF to PowerPoint."""
        response = await self._make_request(
            "POST",
            "/api/documents/convert/pdf-to-ppt",
            json={"documentId": document_id},
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_to_html(
        self, document_id: str, config: Optional[dict[str, Any]] = None
    ) -> OperationResponse:
        """Convert PDF to HTML."""
        payload: dict[str, Any] = {"documentId": document_id}
        if config:
            payload.update(config)

        response = await self._make_request(
            "POST", "/api/documents/convert/pdf-to-html", json=payload
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_to_text(
        self, document_id: str, config: Optional[dict[str, Any]] = None
    ) -> OperationResponse:
        """Convert PDF to text."""
        payload: dict[str, Any] = {"documentId": document_id}
        if config:
            payload.update(config)

        response = await self._make_request(
            "POST", "/api/documents/convert/pdf-to-text", json=payload
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_to_image(
        self, document_id: str, config: Optional[dict[str, Any]] = None
    ) -> OperationResponse:
        """Convert PDF to images."""
        payload: dict[str, Any] = {"documentId": document_id}
        if config:
            payload.update(config)

        response = await self._make_request(
            "POST", "/api/documents/convert/pdf-to-image", json=payload
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    # PDF Manipulation operations

    async def pdf_split(
        self, document_id: str, config: dict[str, Any]
    ) -> OperationResponse:
        """Split PDF."""
        payload = {"documentId": document_id}
        payload.update(config)

        response = await self._make_request(
            "POST", "/api/documents/manipulate/pdf-split", json=payload
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_merge(self, document_ids: list[str]) -> OperationResponse:
        """Merge PDFs."""
        response = await self._make_request(
            "POST",
            "/api/documents/manipulate/pdf-merge",
            json={"documentIds": document_ids},
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_extract(
        self, document_id: str, config: dict[str, Any]
    ) -> OperationResponse:
        """Extract pages from PDF."""
        payload = {"documentId": document_id}
        payload.update(config)

        response = await self._make_request(
            "POST", "/api/documents/manipulate/pdf-extract", json=payload
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_compress(self, document_id: str) -> OperationResponse:
        """Compress PDF."""
        response = await self._make_request(
            "POST",
            "/api/documents/manipulate/pdf-compress",
            json={"documentId": document_id},
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_flatten(self, document_id: str) -> OperationResponse:
        """Flatten PDF."""
        response = await self._make_request(
            "POST",
            "/api/documents/manipulate/pdf-flatten",
            json={"documentId": document_id},
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_linearize(self, document_id: str) -> OperationResponse:
        """Linearize PDF."""
        response = await self._make_request(
            "POST",
            "/api/documents/manipulate/pdf-linearize",
            json={"documentId": document_id},
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_manipulate(
        self, document_id: str, config: dict[str, Any]
    ) -> OperationResponse:
        """Manipulate PDF pages."""
        payload = {"documentId": document_id}
        payload.update(config)

        response = await self._make_request(
            "POST", "/api/documents/manipulate/pdf-manipulate", json=payload
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    # PDF Security operations

    async def pdf_protect(
        self, document_id: str, config: dict[str, Any]
    ) -> OperationResponse:
        """Add password protection to PDF."""
        payload = {"documentId": document_id}
        payload.update(config)

        response = await self._make_request(
            "POST", "/api/documents/security/pdf-protect", json=payload
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_remove_password(
        self, document_id: str, password: str
    ) -> OperationResponse:
        """Remove password from PDF."""
        response = await self._make_request(
            "POST",
            "/api/documents/security/pdf-remove-password",
            json={"documentId": document_id, "password": password},
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    # PDF Enhancement operations

    async def pdf_watermark(
        self, document_id: str, config: dict[str, Any]
    ) -> OperationResponse:
        """Add watermark to PDF."""
        payload = {"documentId": document_id}
        payload.update(config)

        response = await self._make_request(
            "POST", "/api/documents/enhance/pdf-watermark", json=payload
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    # PDF Analysis operations

    async def pdf_compare(
        self, document_id1: str, document_id2: str
    ) -> OperationResponse:
        """Compare two PDFs."""
        response = await self._make_request(
            "POST",
            "/api/documents/analyze/pdf-compare",
            json={"documentId1": document_id1, "documentId2": document_id2},
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_ocr(
        self, document_id: str, config: Optional[dict[str, Any]] = None
    ) -> OperationResponse:
        """Perform OCR on PDF."""
        payload: dict[str, Any] = {"documentId": document_id}
        if config:
            payload.update(config)

        response = await self._make_request(
            "POST", "/api/documents/analyze/pdf-ocr", json=payload
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def get_pdf_properties(self, document_id: str) -> dict[str, Any]:
        """Get PDF properties."""
        response = await self._make_request(
            "GET", f"/api/documents/{document_id}/properties"
        )
        return await self._handle_response(response)

    async def pdf_structural_analysis(self, document_id: str) -> OperationResponse:
        """Analyze PDF structure."""
        response = await self._make_request(
            "POST",
            "/api/documents/analyze/pdf-structural-analysis",
            json={"documentId": document_id},
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    # PDF Forms operations

    async def export_pdf_form_data(
        self, document_id: str, format: str = "json"
    ) -> OperationResponse:
        """Export PDF form data."""
        response = await self._make_request(
            "POST",
            "/api/documents/forms/export",
            json={"documentId": document_id, "format": format},
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def import_pdf_form_data(
        self, document_id: str, form_data: dict[str, Any]
    ) -> OperationResponse:
        """Import PDF form data."""
        response = await self._make_request(
            "POST",
            "/api/documents/forms/import",
            json={"documentId": document_id, "formData": form_data},
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

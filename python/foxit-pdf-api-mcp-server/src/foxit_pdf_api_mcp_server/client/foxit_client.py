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

                # Foxit error payloads can vary by environment/gateway.
                # Prefer specific fields when present; otherwise include the JSON body.
                message = (
                    error_data.get("message")
                    or error_data.get("error")
                    or error_data.get("detail")
                    or error_data.get("title")
                    or f"HTTP {response.status_code}: {error_data}"
                )
                code = (
                    error_data.get("code")
                    or error_data.get("errorCode")
                    or error_data.get("error_code")
                    or "API_ERROR"
                )
                raise FoxitAPIError(
                    message=str(message),
                    code=str(code),
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
        response = await self._make_request(
            "POST",
            "/api/documents/create/pdf-from-html",
            json={"documentId": document_id, "config": config},
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_from_url(
        self, url: str, config: Optional[dict[str, Any]] = None
    ) -> OperationResponse:
        """Convert URL to PDF."""
        response = await self._make_request(
            "POST",
            "/api/documents/create/pdf-from-url",
            json={"url": url, "config": config},
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

    async def pdf_to_word(self, document_id: str, password: Optional[str] = None) -> OperationResponse:
        """Convert PDF to Word."""
        response = await self._make_request(
            "POST",
            "/api/documents/convert/pdf-to-word",
            json={"documentId": document_id, "password": password},
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_to_excel(self, document_id: str, password: Optional[str] = None) -> OperationResponse:
        """Convert PDF to Excel."""
        response = await self._make_request(
            "POST",
            "/api/documents/convert/pdf-to-excel",
            json={"documentId": document_id, "password": password},
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_to_ppt(self, document_id: str, password: Optional[str] = None) -> OperationResponse:
        """Convert PDF to PowerPoint."""
        response = await self._make_request(
            "POST",
            "/api/documents/convert/pdf-to-ppt",
            json={"documentId": document_id, "password": password},
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_to_html(self, document_id: str, password: Optional[str] = None) -> OperationResponse:
        """Convert PDF to HTML."""
        response = await self._make_request(
            "POST",
            "/api/documents/convert/pdf-to-html",
            json={"documentId": document_id, "password": password},
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_to_text(self, document_id: str, password: Optional[str] = None) -> OperationResponse:
        """Convert PDF to text."""
        response = await self._make_request(
            "POST",
            "/api/documents/convert/pdf-to-text",
            json={"documentId": document_id, "password": password},
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_to_image(
        self,
        document_id: str,
        config: Optional[dict[str, Any]] = None,
        password: Optional[str] = None,
    ) -> OperationResponse:
        """Convert PDF to images."""
        response = await self._make_request(
            "POST",
            "/api/documents/convert/pdf-to-image",
            json={"documentId": document_id, "config": config, "password": password},
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    # PDF Manipulation operations

    async def pdf_split(
        self,
        document_id: str,
        split_strategy: str,
        config: Optional[dict[str, Any]] = None,
        password: Optional[str] = None,
    ) -> OperationResponse:
        """Split PDF."""
        payload: dict[str, Any] = {"documentId": document_id, "splitStrategy": split_strategy, "password": password}
        if config:
            payload.update(config)
        response = await self._make_request(
            "POST", "/api/documents/modify/pdf-split", json=payload
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_merge(
        self,
        documents: list[dict[str, Any]],
    ) -> OperationResponse:
        """Merge PDFs."""
        response = await self._make_request(
            "POST",
            "/api/documents/enhance/pdf-combine",
            # Different deployments validate different field names.
            json={"documents": documents, "documentInfos": documents},
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_extract(
        self,
        document_id: str,
        extract_type: str,
        config: Optional[dict[str, Any]] = None,
        password: Optional[str] = None,
    ) -> OperationResponse:
        """Extract pages from PDF."""
        payload: dict[str, Any] = {
            "documentId": document_id,
            "extractType": extract_type,
            "config": config,
            "password": password,
        }
        response = await self._make_request(
            "POST", "/api/documents/modify/pdf-extract", json=payload
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_compress(
        self,
        document_id: str,
        compression_level: str,
        password: Optional[str] = None,
    ) -> OperationResponse:
        """Compress PDF."""
        response = await self._make_request(
            "POST",
            "/api/documents/modify/pdf-compress",
            json={
                "documentId": document_id,
                "compressionLevel": compression_level,
                "password": password,
            },
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_flatten(self, document_id: str, password: Optional[str] = None) -> OperationResponse:
        """Flatten PDF."""
        response = await self._make_request(
            "POST",
            "/api/documents/modify/pdf-flatten",
            json={"documentId": document_id, "password": password},
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_linearize(self, document_id: str) -> OperationResponse:
        """Linearize PDF."""
        response = await self._make_request(
            "POST",
            "/api/documents/optimize/pdf-linearize",
            json={"documentId": document_id},
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_manipulate(
        self,
        document_id: str,
        operations: list[dict[str, Any]],
        password: Optional[str] = None,
    ) -> OperationResponse:
        """Manipulate PDF pages."""
        # Some deployments validate a non-empty `config` object.
        payload: dict[str, Any] = {
            "documentId": document_id,
            "config": {"operations": operations},
            # Also include legacy shape for compatibility.
            "operations": operations,
            "password": password,
        }
        response = await self._make_request(
            "POST", "/api/documents/modify/pdf-manipulate", json=payload
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    # PDF Security operations

    async def pdf_protect(
        self, document_id: str, config: dict[str, Any]
    ) -> OperationResponse:
        """Add password protection to PDF."""
        response = await self._make_request(
            "POST",
            "/api/documents/security/pdf-protect",
            json={"documentId": document_id, "config": config},
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
        self,
        document_id: str,
        config: dict[str, Any],
        password: Optional[str] = None,
    ) -> OperationResponse:
        """Add watermark to PDF."""
        response = await self._make_request(
            "POST",
            "/api/documents/enhance/pdf-watermark",
            json={"documentId": document_id, "config": config, "password": password},
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    # PDF Analysis operations

    async def pdf_compare(
        self,
        document_id1: str,
        document_id2: str,
        password1: Optional[str] = None,
        password2: Optional[str] = None,
    ) -> OperationResponse:
        """Compare two PDFs."""
        doc1 = {"documentId": document_id1, "password": password1}
        doc2 = {"documentId": document_id2, "password": password2}
        response = await self._make_request(
            "POST",
            "/api/documents/analyze/pdf-compare",
            json={
                # Different deployments validate different field names.
                "document1": doc1,
                "document2": doc2,
                "baseDocument": doc1,
                "compareDocument": doc2,
            },
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_ocr(
        self,
        document_id: str,
        config: Optional[dict[str, Any]] = None,
        password: Optional[str] = None,
    ) -> OperationResponse:
        """Perform OCR on PDF."""
        response = await self._make_request(
            "POST",
            "/api/documents/analyze/pdf-ocr",
            json={"documentId": document_id, "config": config, "password": password},
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def get_pdf_properties(
        self,
        document_id: str,
        config: Optional[dict[str, Any]] = None,
    ) -> OperationResponse:
        """Get PDF properties (task-based; returns resultData)."""
        response = await self._make_request(
            "POST",
            "/api/documents/analyze/get-pdf-properties",
            json={"documentId": document_id, "config": config},
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_structural_analysis(
        self, document_id: str, password: Optional[str] = None
    ) -> OperationResponse:
        """Analyze PDF structure."""
        response = await self._make_request(
            "POST",
            "/api/documents/analyze/pdf-structural-analysis",
            json={"documentId": document_id, "password": password},
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    # PDF Forms operations

    async def export_pdf_form_data(
        self, document_id: str, password: Optional[str] = None
    ) -> OperationResponse:
        """Export PDF form data."""
        response = await self._make_request(
            "POST",
            "/api/documents/forms/export-pdf-form-data",
            json={"documentId": document_id, "password": password},
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def import_pdf_form_data(
        self,
        document_id: str,
        form_data: dict[str, Any],
        password: Optional[str] = None,
    ) -> OperationResponse:
        """Import PDF form data."""
        response = await self._make_request(
            "POST",
            "/api/documents/forms/import-pdf-form-data",
            json={"documentId": document_id, "formData": form_data, "password": password},
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

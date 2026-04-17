from typing import Any, Optional

from urllib.parse import urlparse

import asyncio

import httpx

from ..types.api import DocumentUploadResponse, OperationResponse, ShareLinkResponse, TaskResponse


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
        debug_http: bool = False,
        min_same_document_download_interval_seconds: float = 2.1,
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
        self.debug_http = debug_http
        # Gateway rate limiting is strict for repeated downloads of the same document.
        # Enforce a minimum spacing between same-document download attempts.
        self.min_same_document_download_interval_seconds = (
            min_same_document_download_interval_seconds
        )
        self._download_locks: dict[str, asyncio.Lock] = {}
        self._last_download_attempt_at: dict[str, float] = {}

        # Create async HTTP client
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(default_timeout), follow_redirects=True
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    def _get_download_lock(self, document_id: str) -> asyncio.Lock:
        lock = self._download_locks.get(document_id)
        if lock is None:
            lock = asyncio.Lock()
            self._download_locks[document_id] = lock
        return lock

    async def _wait_before_same_document_download(self, document_id: str) -> None:
        """Ensure same-document downloads are at least N seconds apart."""
        min_interval = self.min_same_document_download_interval_seconds
        if min_interval <= 0:
            return

        lock = self._get_download_lock(document_id)
        async with lock:
            now = asyncio.get_event_loop().time()
            last = self._last_download_attempt_at.get(document_id)
            if last is not None:
                elapsed = now - last
                wait_seconds = min_interval - elapsed
                if wait_seconds > 0:
                    if self.debug_http:
                        print(
                            f"[foxit:http] delaying same-document download documentId={document_id} wait={wait_seconds:.2f}s"
                        )
                    await asyncio.sleep(wait_seconds)
            self._last_download_attempt_at[document_id] = asyncio.get_event_loop().time()

    @staticmethod
    def _is_rate_limited_response(status_code: int, body_text: str) -> bool:
        if status_code == 429:
            return True
        if status_code not in {502, 503, 504}:
            return False

        body = (body_text or "").lower()
        return (
            "ratelimiterexception" in body
            or "blocked by gateway" in body
            or "too many requests" in body
            or '"code":429' in body
            or " code 429" in body
        )

    def _get_auth_headers(self) -> dict[str, str]:
        """
        Get authentication headers.

        Returns:
            Dictionary with authentication headers
        """
        # OpenAPI (api-docs_v1.8.json) specifies apiKey auth header: x-api-key.
        # Keep legacy headers for compatibility with environments that still expect them.
        headers: dict[str, str] = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        if self.client_secret:
            headers.setdefault("x-api-key", self.client_secret)
        return headers

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

        if self.debug_http:
            parsed = urlparse(url)
            safe_headers = dict(request_headers)
            if "client_secret" in safe_headers:
                safe_headers["client_secret"] = "***"
            if "x-api-key" in safe_headers:
                safe_headers["x-api-key"] = "***"
            print(
                f"[foxit:http] request method={method} url={url} host={parsed.hostname}"
            )
            print(f"[foxit:http] request headers={safe_headers}")

        try:
            response = await self._client.request(
                method=method, url=url, headers=request_headers, **kwargs
            )

            if self.debug_http:
                final_url = str(response.url)
                if response.history:
                    history_urls = " -> ".join(str(r.url) for r in response.history)
                    print(f"[foxit:http] response redirects={history_urls} -> {final_url}")
                else:
                    print(f"[foxit:http] response url={final_url}")
                print(f"[foxit:http] response status={response.status_code}")

                if response.status_code >= 400:
                    # Print a small, safe preview of the error body to help diagnose auth/config issues.
                    try:
                        body_preview = response.text
                    except Exception:
                        body_preview = ""
                    body_preview = (body_preview or "").strip()
                    if len(body_preview) > 1500:
                        body_preview = body_preview[:1500] + "..."
                    if body_preview:
                        print(f"[foxit:http] response body (preview)={body_preview}")

            return response
        except httpx.TimeoutException as e:
            detail = str(e).strip() or repr(e)
            raise FoxitAPIError(
                message=f"Request timeout: {detail}", code="TIMEOUT"
            ) from e
        except httpx.RequestError as e:
            detail = str(e).strip() or repr(e)
            raise FoxitAPIError(
                message=f"Request failed: {detail}", code="REQUEST_FAILED"
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
                if isinstance(error_data, dict):
                    msg = (
                        error_data.get("message")
                        or error_data.get("error")
                        or error_data.get("detail")
                        or error_data.get("msg")
                    )
                    if not msg:
                        msg = f"HTTP {response.status_code}"
                    code = error_data.get("code") or error_data.get("errorCode") or "API_ERROR"
                    raise FoxitAPIError(
                        message=str(msg),
                        code=str(code),
                        status_code=response.status_code,
                        details=error_data,
                    )
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

    async def create_share_link(
        self,
        document_id: str,
        expiration_minutes: Optional[int] = None,
        filename: Optional[str] = None,
    ) -> ShareLinkResponse:
        """
        Create a time-limited, publicly accessible share link for a document.

        Args:
            document_id: Document ID to share
            expiration_minutes: Optional expiration time in minutes (10-1440)
            filename: Optional custom filename for download

        Returns:
            Share link response with shareUrl, token, and expiresAt
        """
        payload: dict[str, Any] = {}
        if expiration_minutes is not None:
            payload["expirationMinutes"] = expiration_minutes
        if filename is not None:
            payload["filename"] = filename

        # OpenAPI defines an optional/empty requestBody; avoid sending JSON null.
        if payload:
            response = await self._make_request(
                "POST",
                f"/api/documents/{document_id}/share",
                json=payload,
            )
        else:
            response = await self._make_request(
                "POST",
                f"/api/documents/{document_id}/share",
            )
        data = await self._handle_response(response)
        return ShareLinkResponse(
            shareUrl=data["shareUrl"],
            token=data["token"],
            expiresAt=data["expiresAt"],
        )

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

        retry_delay = 2
        last_response: Optional[httpx.Response] = None
        for attempt in range(self.max_retries + 1):
            await self._wait_before_same_document_download(document_id)
            response = await self._make_request("GET", path)
            last_response = response

            body_preview = ""
            if response.status_code >= 400:
                try:
                    body_preview = response.text
                except Exception:
                    body_preview = ""

            if self._is_rate_limited_response(response.status_code, body_preview):
                if attempt < self.max_retries:
                    wait = int(response.headers.get("Retry-After", retry_delay))
                    if self.debug_http:
                        print(
                            f"[foxit:http] download rate-limited, retrying in {wait}s (attempt {attempt + 1}/{self.max_retries})"
                        )
                    await asyncio.sleep(wait)
                    continue

            if response.status_code >= 400:
                await self._handle_response(response)

            return response.content

        if last_response is not None and last_response.status_code >= 400:
            await self._handle_response(last_response)
        return b""

    async def download_document_partial(
        self,
        document_id: str,
        *,
        max_bytes: int,
        filename: Optional[str] = None,
    ) -> tuple[bytes, bool]:
        """Download up to max_bytes of a document (streaming).

        This is useful for very large documents when callers only need a preview.

        Returns:
            (content, truncated)
        """
        if max_bytes <= 0:
            return b"", False

        path = f"/api/documents/{document_id}/download"
        if filename:
            path += f"?filename={filename}"

        url = f"{self.base_url}/{path.lstrip('/')}"
        headers = self._get_auth_headers()

        collected = bytearray()
        truncated = False

        retry_delay = 2  # seconds to wait before retrying on 429
        for attempt in range(self.max_retries + 1):
            collected.clear()
            truncated = False
            await self._wait_before_same_document_download(document_id)

            async with self._client.stream("GET", url, headers=headers) as response:
                should_retry_rate_limit = False
                if response.status_code >= 400:
                    body = await response.aread()
                    body_text = ""
                    try:
                        body_text = body.decode("utf-8", errors="replace")
                    except Exception:
                        body_text = ""

                    if self._is_rate_limited_response(response.status_code, body_text):
                        should_retry_rate_limit = True

                    if should_retry_rate_limit and attempt < self.max_retries:
                        wait = int(response.headers.get("Retry-After", retry_delay))
                        if self.debug_http:
                            print(
                                f"[foxit:http] rate-limited on streaming download, retrying in {wait}s (attempt {attempt + 1}/{self.max_retries})"
                            )
                        await asyncio.sleep(wait)
                        continue

                    # Materialize body so we can reuse existing error parsing.
                    error_response = httpx.Response(
                        status_code=response.status_code,
                        headers=response.headers,
                        content=body,
                        request=response.request,
                    )
                    await self._handle_response(error_response)

                async for chunk in response.aiter_bytes():
                    if not chunk:
                        continue
                    remaining = max_bytes - len(collected)
                    if remaining <= 0:
                        truncated = True
                        break
                    if len(chunk) <= remaining:
                        collected.extend(chunk)
                    else:
                        collected.extend(chunk[:remaining])
                        truncated = True
                        break

            return bytes(collected), truncated

        # All retries exhausted — last attempt already raised or returned above.
        return bytes(collected), truncated

    async def delete_document(self, document_id: str) -> None:
        """
        Delete a document.

        Args:
            document_id: Document ID to delete
        """
        response = await self._make_request("DELETE", f"/api/documents/{document_id}")
        if response.status_code >= 400:
            await self._handle_response(response)

    async def get_task_status(self, task_id: str, region: Optional[str] = None) -> TaskResponse:
        """
        Get task status.

        Args:
            task_id: Task ID to check

        Returns:
            Task status response
        """
        params: dict[str, Any] = {}
        if region is not None and region != "":
            params["region"] = region

        response = await self._make_request(
            "GET",
            f"/api/tasks/{task_id}",
            params=(params or None),
        )
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

    async def pdf_to_word(self, document_id: str, password: Optional[str] = None) -> OperationResponse:
        """Convert PDF to Word."""
        payload: dict[str, Any] = {"documentId": document_id}
        if password is not None and password != "":
            payload["password"] = password
        response = await self._make_request(
            "POST",
            "/api/documents/convert/pdf-to-word",
            json=payload,
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_to_excel(self, document_id: str, password: Optional[str] = None) -> OperationResponse:
        """Convert PDF to Excel."""
        payload: dict[str, Any] = {"documentId": document_id}
        if password is not None and password != "":
            payload["password"] = password
        response = await self._make_request(
            "POST",
            "/api/documents/convert/pdf-to-excel",
            json=payload,
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_to_ppt(self, document_id: str, password: Optional[str] = None) -> OperationResponse:
        """Convert PDF to PowerPoint."""
        payload: dict[str, Any] = {"documentId": document_id}
        if password is not None and password != "":
            payload["password"] = password
        response = await self._make_request(
            "POST",
            "/api/documents/convert/pdf-to-ppt",
            json=payload,
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_to_html(
        self, document_id: str, config: Optional[dict[str, Any]] = None, password: Optional[str] = None
    ) -> OperationResponse:
        """Convert PDF to HTML."""
        payload: dict[str, Any] = {"documentId": document_id}
        if password is not None and password != "":
            payload["password"] = password
        if config:
            payload.update(config)

        response = await self._make_request(
            "POST", "/api/documents/convert/pdf-to-html", json=payload
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_to_text(
        self, document_id: str, config: Optional[dict[str, Any]] = None, password: Optional[str] = None
    ) -> OperationResponse:
        """Convert PDF to text."""
        payload: dict[str, Any] = {"documentId": document_id}
        if password is not None and password != "":
            payload["password"] = password
        if config:
            payload.update(config)

        response = await self._make_request(
            "POST", "/api/documents/convert/pdf-to-text", json=payload
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_to_image(
        self, document_id: str, config: Optional[dict[str, Any]] = None, password: Optional[str] = None
    ) -> OperationResponse:
        """Convert PDF to images."""
        payload: dict[str, Any] = {"documentId": document_id}
        if password is not None and password != "":
            payload["password"] = password
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

        # Optional but recommended: enforce OpenAPI required field
        if "pageCount" not in payload:
            raise ValueError("pdf_split requires 'pageCount'")
        
        response = await self._make_request(
            "POST", "/api/documents/modify/pdf-split", json=payload
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_merge(
        self,
        document_ids: list[str],
        passwords: Optional[list[Optional[str]]] = None,
    ) -> OperationResponse:
        """Merge PDFs.

        Args:
            document_ids: List of document IDs to merge
            passwords: Optional list of passwords (one per document).
                      Use None for documents without passwords.
                      If provided, must match length of document_ids.
        """
        if passwords is not None and len(passwords) != len(document_ids):
            raise ValueError(
                f"passwords list length ({len(passwords)}) must match document_ids length ({len(document_ids)})"
            )
        
        document_infos = []
        for i, doc_id in enumerate(document_ids):
            doc_info: dict[str, Any] = {"documentId": doc_id}
            if passwords and i < len(passwords):
                pwd = passwords[i]
                if pwd is not None and pwd != "":
                    doc_info["password"] = pwd
            document_infos.append(doc_info)
        
        payload = {"documentInfos": document_infos}
        response = await self._make_request(
            "POST",
            "/api/documents/enhance/pdf-combine",
            json=payload,
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_extract(
        self, document_id: str, config: dict[str, Any]
    ) -> OperationResponse:
        """Extract pages from PDF."""
        payload: dict[str, Any] = {"documentId": document_id}
        payload.update(config)

        # OpenAPI requires extractType (PDFExtractRequest.required: documentId, extractType).
        # OpenAPI: pageRange is a page filter and can be used with any extractType (example shows TEXT + pageRange).
        # Default behavior when extractType is missing: default to TEXT.
        if "extractType" not in payload or not payload.get("extractType"):
            payload["extractType"] = "PAGE"

        response = await self._make_request(
            "POST", "/api/documents/modify/pdf-extract", json=payload
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_compress(
        self, document_id: str, password: Optional[str] = None
    ) -> OperationResponse:
        """Compress PDF.

        OpenAPI: POST /api/documents/modify/pdf-compress
        Required body fields: documentId, compressionLevel
        """
        # Keep backwards compatibility with existing tools that call pdf_compress(document_id)
        # by defaulting to MEDIUM compression.
        compression_level = "MEDIUM"
        payload: dict[str, Any] = {
            "documentId": document_id,
            "compressionLevel": compression_level,
        }
        if password is not None and password != "":
            payload["password"] = password
        response = await self._make_request(
            "POST",
            "/api/documents/modify/pdf-compress",
            json=payload,
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_flatten(
        self, document_id: str, password: Optional[str] = None
    ) -> OperationResponse:
        """Flatten PDF."""
        payload: dict[str, Any] = {"documentId": document_id}
        if password is not None and password != "":
            payload["password"] = password
        response = await self._make_request(
            "POST",
            "/api/documents/modify/pdf-flatten",
            json=payload,
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_linearize(
        self, document_id: str, password: Optional[str] = None
    ) -> OperationResponse:
        """Linearize PDF."""
        payload: dict[str, Any] = {"documentId": document_id}
        if password is not None and password != "":
            payload["password"] = password
        response = await self._make_request(
            "POST",
            "/api/documents/optimize/pdf-linearize",
            json=payload,
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

    async def pdf_manipulate(
        self,
        document_id: str,
        config: dict[str, Any],
        password: Optional[str] = None,
    ) -> OperationResponse:
        """Manipulate PDF pages.

        OpenAPI: POST /api/documents/modify/pdf-manipulate
        Body schema: PDFPageOrganizeRequest { documentId, password?, config }
        """
        # Copy so callers can safely reuse the dict.
        config_payload: dict[str, Any] = dict(config or {})

        # Backwards compatibility: older tools stored password inside config.
        config_password = config_payload.pop("password", None)
        effective_password = password
        if (effective_password is None or effective_password == "") and config_password:
            effective_password = str(config_password)

        payload: dict[str, Any] = {
            "documentId": document_id,
            "config": config_payload,
        }
        if effective_password is not None and str(effective_password).strip() != "":
            payload["password"] = str(effective_password)

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

    async def pdf_redact(
        self, document_id: str, config: dict[str, Any]
    ) -> OperationResponse:
        """Redact content from a PDF."""
        payload: dict[str, Any] = {"documentId": document_id}
        if config:
            payload["config"] = config
        response = await self._make_request(
            "POST",
            "/api/documents/security/pdf-redact",
            json=payload,
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
        self,
        document_id1: str,
        document_id2: str,
        password1: Optional[str] = None,
        password2: Optional[str] = None,
        config: Optional[dict[str, Any]] = None,
    ) -> OperationResponse:
        """Compare two PDFs."""
        # OpenAPI: POST /api/documents/analyze/pdf-compare
        # Body schema: PDFCompareRequest { baseDocument, compareDocument, config }
        base_document: dict[str, Any] = {"documentId": document_id1}
        compare_document: dict[str, Any] = {"documentId": document_id2}
        if password1 is not None and password1 != "":
            base_document["password"] = password1
        if password2 is not None and password2 != "":
            compare_document["password"] = password2

        payload: dict[str, Any] = {
            "baseDocument": base_document,
            "compareDocument": compare_document,
        }
        if config:
            payload["config"] = config

        response = await self._make_request(
            "POST",
            "/api/documents/analyze/pdf-compare",
            json=payload,
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

    async def get_pdf_properties(
        self,
        document_id: str,
        include_extended_info: bool = True,
        include_page_info: bool = True,
        password: Optional[str] = None,
    ) -> dict[str, Any]:
        """Get PDF properties.

        OpenAPI: POST /api/documents/analyze/get-pdf-properties (async)
        This client method returns the final JSON result (task.resultData) to keep
        the tool API ergonomic.
        """

        config: dict[str, Any] = {
            "includeExtendedInfo": include_extended_info,
            "includePageInfo": include_page_info,
        }
        payload: dict[str, Any] = {"documentId": document_id, "config": config}
        if password is not None and password != "":
            payload["password"] = password

        start = await self._make_request(
            "POST",
            "/api/documents/analyze/get-pdf-properties",
            json=payload,
        )
        start_data = await self._handle_response(start)
        task_id = start_data.get("taskId")
        if not task_id:
            raise FoxitAPIError(
                message="Missing taskId from get-pdf-properties response",
                code="INVALID_RESPONSE",
                details=start_data,
            )

        # Poll task until completion (duplicated here to avoid circular import with utils.task_poller)
        timeout_seconds = self.default_timeout
        start_time = asyncio.get_event_loop().time()
        while True:
            task_status = await self.get_task_status(task_id)
            status = task_status.get("status")

            if status == "COMPLETED":
                result_data = task_status.get("resultData")
                # resultData may be null for some tasks; normalize to dict.
                return result_data if isinstance(result_data, dict) else {}

            if status == "FAILED":
                error_info = task_status.get("error", {})
                raise FoxitAPIError(
                    message=error_info.get("message", "Task failed without error details"),
                    code=error_info.get("code", "TASK_FAILED"),
                    details=error_info.get("details"),
                )

            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > timeout_seconds:
                raise FoxitAPIError(
                    message=f"Task {task_id} did not complete within {timeout_seconds}s",
                    code="TASK_TIMEOUT",
                )

            await asyncio.sleep(self.poll_interval)

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
        self, document_id: str, password: Optional[str] = None
    ) -> OperationResponse:
        """Export PDF form data."""
        # OpenAPI: POST /api/documents/forms/export-pdf-form-data
        payload: dict[str, Any] = {"documentId": document_id}
        if password is not None and password != "":
            payload["password"] = password
        response = await self._make_request(
            "POST",
            "/api/documents/forms/export-pdf-form-data",
            json=payload,
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
        # OpenAPI: POST /api/documents/forms/import-pdf-form-data
        payload: dict[str, Any] = {"documentId": document_id, "formData": form_data}
        if password is not None and password != "":
            payload["password"] = password
        response = await self._make_request(
            "POST",
            "/api/documents/forms/import-pdf-form-data",
            json=payload,
        )
        data = await self._handle_response(response)
        return OperationResponse(taskId=data["taskId"])

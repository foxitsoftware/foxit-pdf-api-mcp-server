"""End-to-end tests for pdf_security tools.

These tests call the real Foxit Cloud API — no mocking.
They require valid credentials in .env and a working network connection.

pdf_protect and pdf_remove_password use execute_and_wait() internally,
so they return the final result directly (no taskId polling from the test).

Flow:
  1. Upload a PDF.
  2. pdf_protect: add password protection → validate response contract.
  3. pdf_remove_password: remove protection from the protected PDF → validate.
  4. Clean up all documents at teardown.

Run:
    pytest tests/e2e/test_pdf_security_e2e.py -v
"""

import base64
import json
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"

pytestmark = [
    pytest.mark.e2e,
    pytest.mark.asyncio(loop_scope="module"),
]

_doc_ids_to_cleanup: list[str] = []


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _upload_pdf(filename: str = "sample.pdf") -> str:
    from foxit_pdf_api_mcp_server.tools.document_lifecycle import upload_document

    b64 = base64.b64encode((FIXTURES_DIR / filename).read_bytes()).decode()
    result_json = await upload_document(file_content=b64, file_name=filename)
    data = json.loads(result_json)
    assert data["success"] is True, f"Upload failed: {data}"
    doc_id = data["resultDocumentId"]
    _doc_ids_to_cleanup.append(doc_id)
    return doc_id


def _assert_success_with_doc(data: dict) -> dict:
    """Validate synchronous success response with resultDocumentId + shareUrl."""
    assert data["success"] is True, f"Operation failed: {data}"
    assert "message" in data, f"Missing 'message': {data}"
    assert isinstance(data["message"], str) and len(data["message"]) > 0

    result_doc_id = data.get("resultDocumentId")
    assert result_doc_id is not None, f"Missing 'resultDocumentId': {data}"
    assert isinstance(result_doc_id, str) and len(result_doc_id) > 0
    _doc_ids_to_cleanup.append(result_doc_id)

    share_url = data.get("shareUrl")
    assert share_url is not None, f"Missing 'shareUrl': {data}"
    assert isinstance(share_url, str) and share_url.startswith("http")

    expires_at = data.get("expiresAt")
    if expires_at is not None:
        assert isinstance(expires_at, str) and len(expires_at) > 0

    return data


# ---------------------------------------------------------------------------
# Module-scoped fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module", autouse=True)
async def _setup_and_cleanup(refresh_http_client):
    global _doc_ids_to_cleanup
    _doc_ids_to_cleanup = []

    yield

    from foxit_pdf_api_mcp_server.tools.document_lifecycle import delete_document

    for doc_id in _doc_ids_to_cleanup:
        if doc_id:
            try:
                await delete_document(document_id=doc_id)
            except Exception:
                pass


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestPdfProtectE2E:
    async def test_protect_with_user_password(self):
        from foxit_pdf_api_mcp_server.tools.pdf_security import pdf_protect

        doc_id = await _upload_pdf()
        result = json.loads(
            await pdf_protect(document_id=doc_id, user_password="test1234")
        )
        _assert_success_with_doc(result)

    async def test_protect_with_owner_password(self):
        from foxit_pdf_api_mcp_server.tools.pdf_security import pdf_protect

        doc_id = await _upload_pdf()
        result = json.loads(
            await pdf_protect(document_id=doc_id, owner_password="owner1234")
        )
        _assert_success_with_doc(result)

    async def test_protect_with_permissions(self):
        from foxit_pdf_api_mcp_server.tools.pdf_security import pdf_protect

        doc_id = await _upload_pdf()
        result = json.loads(
            await pdf_protect(
                document_id=doc_id,
                user_password="test1234",
                owner_password="owner1234",
                allow_printing=False,
                allow_copying=False,
                allow_editing=False,
            )
        )
        _assert_success_with_doc(result)


class TestPdfRemovePasswordE2E:
    async def test_full_flow(self):
        """Upload a pre-protected PDF fixture, then remove the password."""
        from foxit_pdf_api_mcp_server.tools.pdf_security import pdf_remove_password

        # sample_protected.pdf was protected with user_password="test1234"
        doc_id = await _upload_pdf("sample_protected.pdf")
        result = json.loads(
            await pdf_remove_password(document_id=doc_id, password="test1234")
        )
        _assert_success_with_doc(result)

"""End-to-end tests for pdf_manipulation tools.

These tests call the real Foxit Cloud API — no mocking.
They require valid credentials in .env and a working network connection.

Active tools (10):
  pdf_merge, pdf_split, pdf_extract_pages, pdf_extract_text,
  pdf_compress, pdf_flatten, pdf_linearize,
  pdf_manipulate, pdf_delete_pages, pdf_rotate_pages, pdf_reorder_pages

Flow:
  1. Upload sample.pdf once (module-scoped fixture).
  2. Each test calls a manipulation tool → real HTTP request, returns taskId.
  3. Poll ``get_task_result`` until the task completes or fails.
  4. Validate the final response schema matches the tool's documented contract.
  5. Clean up: delete all documents at the end of the module.

Run:
    pytest tests/e2e/test_pdf_manipulation_e2e.py -v
"""

import asyncio
import base64
import json
from pathlib import Path
from typing import Any

import pytest

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"

TASK_TIMEOUT = 120
POLL_INTERVAL = 3

pytestmark = [
    pytest.mark.e2e,
    pytest.mark.asyncio(loop_scope="module"),
]

_doc_ids_to_cleanup: list[str] = []


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _upload_pdf(filename: str = "sample.pdf") -> str:
    """Upload a PDF fixture and return its document_id."""
    from foxit_pdf_api_mcp_server.tools.document_lifecycle import upload_document

    b64 = base64.b64encode((FIXTURES_DIR / filename).read_bytes()).decode()
    result_json = await upload_document(file_content=b64, file_name=filename)
    data = json.loads(result_json)
    assert data["success"] is True, f"Upload failed: {data}"
    doc_id = data["resultDocumentId"]
    _doc_ids_to_cleanup.append(doc_id)
    return doc_id


async def _poll_task(task_id: str) -> dict[str, Any]:
    from foxit_pdf_api_mcp_server.tools.task_status import get_task_result

    elapsed = 0
    while elapsed < TASK_TIMEOUT:
        result_json = await get_task_result(task_id=task_id)
        data = json.loads(result_json)
        status = data.get("status", "")
        if status in ("completed", "failed"):
            return data
        await asyncio.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL

    pytest.fail(f"Task {task_id} did not complete within {TASK_TIMEOUT}s")


def _assert_task_submitted(data: dict) -> str:
    """Validate the task-submitted response matches the documented contract."""
    assert data["success"] is True, f"Submission failed: {data}"
    assert "taskId" in data, f"Missing 'taskId': {data}"
    assert "message" in data, f"Missing 'message': {data}"
    task_id = data["taskId"]
    assert isinstance(task_id, str) and len(task_id) > 0
    assert isinstance(data["message"], str) and len(data["message"]) > 0
    assert "status" not in data, f"Unexpected 'status' in submission response: {data}"
    return task_id


def _assert_completed(data: dict) -> dict:
    """Validate the completed response matches the documented contract."""
    assert data["success"] is True, f"Task failed: {data}"
    assert data["status"] == "completed", f"Unexpected status: {data}"
    assert "taskId" in data, f"Missing 'taskId': {data}"
    assert isinstance(data["taskId"], str) and len(data["taskId"]) > 0
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
    """Refresh httpx client, clean up all created documents at teardown."""
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


@pytest.fixture(scope="module")
async def uploaded_pdf() -> str:
    """Upload sample.pdf once for the module, return doc_id."""
    return await _upload_pdf()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestPdfMergeE2E:
    async def test_full_flow(self):
        from foxit_pdf_api_mcp_server.tools.pdf_manipulation import pdf_merge

        doc_id_1 = await _upload_pdf()
        doc_id_2 = await _upload_pdf()
        submit = json.loads(await pdf_merge(document_ids=[doc_id_1, doc_id_2]))
        task_id = _assert_task_submitted(submit)
        completed = await _poll_task(task_id)
        _assert_completed(completed)


class TestPdfSplitE2E:
    async def test_full_flow(self, uploaded_pdf):
        from foxit_pdf_api_mcp_server.tools.pdf_manipulation import pdf_split

        submit = json.loads(await pdf_split(document_id=uploaded_pdf, page_count=1))
        task_id = _assert_task_submitted(submit)
        completed = await _poll_task(task_id)
        _assert_completed(completed)


class TestPdfExtractPagesE2E:
    async def test_full_flow(self, uploaded_pdf):
        from foxit_pdf_api_mcp_server.tools.pdf_manipulation import pdf_extract_pages

        submit = json.loads(
            await pdf_extract_pages(document_id=uploaded_pdf, page_range="1")
        )
        task_id = _assert_task_submitted(submit)
        completed = await _poll_task(task_id)
        _assert_completed(completed)


class TestPdfExtractTextE2E:
    async def test_full_flow(self, uploaded_pdf):
        """Validate completed response includes text and textTruncated fields."""
        from foxit_pdf_api_mcp_server.tools.pdf_manipulation import pdf_extract_text

        submit = json.loads(
            await pdf_extract_text(document_id=uploaded_pdf, page_range="1")
        )
        task_id = _assert_task_submitted(submit)
        completed = await _poll_task(task_id)
        _assert_completed(completed)

        # pdf_extract_text has extra contract fields
        assert "text" in completed, f"Missing 'text' in extract_text response: {completed}"
        assert isinstance(completed["text"], str)
        assert "textTruncated" in completed, f"Missing 'textTruncated': {completed}"
        assert isinstance(completed["textTruncated"], bool)


class TestPdfCompressE2E:
    async def test_full_flow(self, uploaded_pdf):
        from foxit_pdf_api_mcp_server.tools.pdf_manipulation import pdf_compress

        submit = json.loads(await pdf_compress(document_id=uploaded_pdf))
        task_id = _assert_task_submitted(submit)
        completed = await _poll_task(task_id)
        _assert_completed(completed)


class TestPdfFlattenE2E:
    async def test_full_flow(self, uploaded_pdf):
        from foxit_pdf_api_mcp_server.tools.pdf_manipulation import pdf_flatten

        submit = json.loads(await pdf_flatten(document_id=uploaded_pdf))
        task_id = _assert_task_submitted(submit)
        completed = await _poll_task(task_id)
        _assert_completed(completed)


class TestPdfLinearizeE2E:
    async def test_full_flow(self, uploaded_pdf):
        from foxit_pdf_api_mcp_server.tools.pdf_manipulation import pdf_linearize

        submit = json.loads(await pdf_linearize(document_id=uploaded_pdf))
        task_id = _assert_task_submitted(submit)
        completed = await _poll_task(task_id)
        _assert_completed(completed)


class TestPdfManipulateE2E:
    async def test_rotate_page(self, uploaded_pdf):
        from foxit_pdf_api_mcp_server.tools.pdf_manipulation import pdf_manipulate

        operations = [
            {"type": "ROTATE_PAGES", "pages": [1], "rotation": "ROTATE_CLOCKWISE_90"}
        ]
        submit = json.loads(
            await pdf_manipulate(document_id=uploaded_pdf, operations=operations)
        )
        task_id = _assert_task_submitted(submit)
        completed = await _poll_task(task_id)
        _assert_completed(completed)


class TestPdfDeletePagesE2E:
    async def test_full_flow(self):
        """Upload a 2-page PDF, then delete page 1."""
        from foxit_pdf_api_mcp_server.tools.pdf_manipulation import pdf_delete_pages

        doc_id = await _upload_pdf("sample_2pages.pdf")
        submit = json.loads(
            await pdf_delete_pages(document_id=doc_id, page_range="1")
        )
        task_id = _assert_task_submitted(submit)
        completed = await _poll_task(task_id)
        _assert_completed(completed)


class TestPdfRotatePagesE2E:
    async def test_full_flow(self, uploaded_pdf):
        from foxit_pdf_api_mcp_server.tools.pdf_manipulation import pdf_rotate_pages

        submit = json.loads(
            await pdf_rotate_pages(
                document_id=uploaded_pdf, page_range="1", rotation=90
            )
        )
        task_id = _assert_task_submitted(submit)
        completed = await _poll_task(task_id)
        _assert_completed(completed)


class TestPdfReorderPagesE2E:
    async def test_full_flow(self):
        """Upload a 2-page PDF, then move page 2 to position 1."""
        from foxit_pdf_api_mcp_server.tools.pdf_manipulation import pdf_reorder_pages

        doc_id = await _upload_pdf("sample_2pages.pdf")
        submit = json.loads(
            await pdf_reorder_pages(
                document_id=doc_id, page_range="2", target_position=1
            )
        )
        task_id = _assert_task_submitted(submit)
        completed = await _poll_task(task_id)
        _assert_completed(completed)

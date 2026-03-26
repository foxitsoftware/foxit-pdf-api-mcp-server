"""End-to-end tests for pdf_creation tools.

These tests call the real Foxit Cloud API — no mocking.
They require valid credentials in .env and a working network connection.

Flow:
  1. Upload a source file (docx / xlsx / pptx / txt / html / png) for each tool.
  2. Call the creation tool → real HTTP request, returns taskId.
  3. Poll ``get_task_result`` until the task completes or fails.
  4. Validate the final response schema matches the tool's documented contract.
  5. Clean up: delete all documents at the end of the module.

Run:
    pytest tests/e2e/test_pdf_creation_e2e.py -v
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

async def _upload_fixture(filename: str) -> str:
    """Upload a fixture file and return its document_id."""
    from foxit_pdf_api_mcp_server.tools.document_lifecycle import upload_document

    filepath = FIXTURES_DIR / filename
    b64 = base64.b64encode(filepath.read_bytes()).decode()
    result_json = await upload_document(file_content=b64, file_name=filename)
    data = json.loads(result_json)
    assert data["success"] is True, f"Upload {filename} failed: {data}"
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
    """Validate the task-submitted response matches the documented contract.

    Expected keys: success (True), taskId (non-empty str), message (str).
    """
    assert data["success"] is True, f"Submission failed: {data}"
    assert "taskId" in data, f"Missing 'taskId': {data}"
    assert "message" in data, f"Missing 'message': {data}"
    task_id = data["taskId"]
    assert isinstance(task_id, str) and len(task_id) > 0
    assert isinstance(data["message"], str) and len(data["message"]) > 0
    assert "status" not in data, f"Unexpected 'status' in submission response: {data}"
    return task_id


def _assert_completed(data: dict) -> dict:
    """Validate the completed response matches the documented contract.

    Required keys: success (True), status ("completed"), taskId (str), message (str).
    Expected keys for creation tools: resultDocumentId (non-empty str), shareUrl (str).
    Optional keys: expiresAt (str).
    """
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
# Module-scoped fixture: refresh httpx client, clean up at end.
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module", autouse=True)
async def _setup_and_cleanup(refresh_http_client):
    """Refresh httpx client for a clean event loop, clean up docs at teardown."""
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

class TestPdfFromWordE2E:
    async def test_full_flow(self):
        from foxit_pdf_api_mcp_server.tools.pdf_creation import pdf_from_word

        doc_id = await _upload_fixture("sample.docx")
        submit = json.loads(await pdf_from_word(document_id=doc_id))
        task_id = _assert_task_submitted(submit)
        completed = await _poll_task(task_id)
        _assert_completed(completed)


class TestPdfFromExcelE2E:
    async def test_full_flow(self):
        from foxit_pdf_api_mcp_server.tools.pdf_creation import pdf_from_excel

        doc_id = await _upload_fixture("sample.xlsx")
        submit = json.loads(await pdf_from_excel(document_id=doc_id))
        task_id = _assert_task_submitted(submit)
        completed = await _poll_task(task_id)
        _assert_completed(completed)


class TestPdfFromPptE2E:
    async def test_full_flow(self):
        from foxit_pdf_api_mcp_server.tools.pdf_creation import pdf_from_ppt

        doc_id = await _upload_fixture("sample.pptx")
        submit = json.loads(await pdf_from_ppt(document_id=doc_id))
        task_id = _assert_task_submitted(submit)
        completed = await _poll_task(task_id)
        _assert_completed(completed)


class TestPdfFromTextE2E:
    async def test_full_flow(self):
        from foxit_pdf_api_mcp_server.tools.pdf_creation import pdf_from_text

        doc_id = await _upload_fixture("sample.txt")
        submit = json.loads(await pdf_from_text(document_id=doc_id))
        task_id = _assert_task_submitted(submit)
        completed = await _poll_task(task_id)
        _assert_completed(completed)


class TestPdfFromImageE2E:
    async def test_full_flow(self):
        from foxit_pdf_api_mcp_server.tools.pdf_creation import pdf_from_image

        doc_id = await _upload_fixture("sample.png")
        submit = json.loads(await pdf_from_image(document_id=doc_id))
        task_id = _assert_task_submitted(submit)
        completed = await _poll_task(task_id)
        _assert_completed(completed)


class TestPdfFromHtmlE2E:
    async def test_full_flow(self):
        from foxit_pdf_api_mcp_server.tools.pdf_creation import pdf_from_html

        doc_id = await _upload_fixture("sample.html")
        submit = json.loads(await pdf_from_html(document_id=doc_id))
        task_id = _assert_task_submitted(submit)
        completed = await _poll_task(task_id)
        _assert_completed(completed)

    async def test_with_page_dimensions(self):
        from foxit_pdf_api_mcp_server.tools.pdf_creation import pdf_from_html

        doc_id = await _upload_fixture("sample.html")
        submit = json.loads(
            await pdf_from_html(document_id=doc_id, page_width=800, page_height=1200)
        )
        task_id = _assert_task_submitted(submit)
        completed = await _poll_task(task_id)
        _assert_completed(completed)


class TestPdfFromUrlE2E:
    async def test_full_flow(self):
        from foxit_pdf_api_mcp_server.tools.pdf_creation import pdf_from_url

        submit = json.loads(
            await pdf_from_url(url="https://example.com")
        )
        task_id = _assert_task_submitted(submit)
        completed = await _poll_task(task_id)
        _assert_completed(completed)

    async def test_with_page_dimensions(self):
        from foxit_pdf_api_mcp_server.tools.pdf_creation import pdf_from_url

        submit = json.loads(
            await pdf_from_url(
                url="https://example.com", page_width=800, page_height=1200
            )
        )
        task_id = _assert_task_submitted(submit)
        completed = await _poll_task(task_id)
        _assert_completed(completed)

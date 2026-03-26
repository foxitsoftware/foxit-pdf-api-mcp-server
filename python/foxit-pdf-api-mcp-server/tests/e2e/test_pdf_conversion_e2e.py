"""End-to-end tests for pdf_conversion tools.

These tests call the real Foxit Cloud API — no mocking.
They require valid credentials in .env and a working network connection.

Flow:
  1. Upload a real PDF once (module-scoped fixture).
  2. Each test calls a conversion tool → real HTTP request, returns taskId.
  3. Poll ``get_task_result`` until the task completes or fails.
  4. Validate the final response schema matches the tool's documented contract.
  5. Clean up: delete all documents at the end of the module.

Run:
    pytest tests/e2e/ -v
    pytest -m e2e -v
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

_result_doc_ids: list[str] = []


# ---------------------------------------------------------------------------
# Module-scoped fixture: refresh httpx client, upload once, clean up at end.
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module", autouse=True)
async def uploaded_pdf(refresh_http_client):
    """Upload sample.pdf once, yield doc_id, clean up at teardown."""
    global _result_doc_ids
    _result_doc_ids = []

    from foxit_pdf_api_mcp_server.tools.document_lifecycle import upload_document

    b64 = base64.b64encode((FIXTURES_DIR / "sample.pdf").read_bytes()).decode()
    result_json = await upload_document(file_content=b64, file_name="sample.pdf")
    data = json.loads(result_json)
    assert data["success"] is True, f"Upload failed: {data}"
    doc_id = data["resultDocumentId"]

    yield doc_id

    # Teardown: best-effort cleanup
    from foxit_pdf_api_mcp_server.tools.document_lifecycle import delete_document

    for did in [doc_id] + _result_doc_ids:
        if did:
            try:
                await delete_document(document_id=did)
            except Exception:
                pass


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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
    # No unexpected top-level status keys for a submission response
    assert "status" not in data, f"Unexpected 'status' in submission response: {data}"
    return task_id


def _assert_completed(data: dict) -> dict:
    """Validate the completed response matches the documented contract.

    Required keys: success (True), status ("completed"), taskId (str), message (str).
    Expected keys for conversion tools: resultDocumentId (non-empty str), shareUrl (str).
    Optional keys: expiresAt (str), resultData (dict).
    """
    # --- Required fields ---
    assert data["success"] is True, f"Task failed: {data}"
    assert data["status"] == "completed", f"Unexpected status: {data}"
    assert "taskId" in data, f"Missing 'taskId': {data}"
    assert isinstance(data["taskId"], str) and len(data["taskId"]) > 0
    assert "message" in data, f"Missing 'message': {data}"
    assert isinstance(data["message"], str) and len(data["message"]) > 0

    # --- resultDocumentId (expected for all conversion tools) ---
    result_doc_id = data.get("resultDocumentId")
    assert result_doc_id is not None, f"Missing 'resultDocumentId': {data}"
    assert isinstance(result_doc_id, str) and len(result_doc_id) > 0
    _result_doc_ids.append(result_doc_id)

    # --- shareUrl (expected: auto-created for conversion results) ---
    share_url = data.get("shareUrl")
    assert share_url is not None, f"Missing 'shareUrl': {data}"
    assert isinstance(share_url, str) and share_url.startswith("http")

    # --- expiresAt (optional, but if present must be a non-empty string) ---
    expires_at = data.get("expiresAt")
    if expires_at is not None:
        assert isinstance(expires_at, str) and len(expires_at) > 0

    return data


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestPdfToWordE2E:
    async def test_full_flow(self, uploaded_pdf):
        from foxit_pdf_api_mcp_server.tools.pdf_conversion import pdf_to_word

        submit = json.loads(await pdf_to_word(document_id=uploaded_pdf))
        task_id = _assert_task_submitted(submit)
        completed = await _poll_task(task_id)
        _assert_completed(completed)


class TestPdfToExcelE2E:
    async def test_full_flow(self, uploaded_pdf):
        from foxit_pdf_api_mcp_server.tools.pdf_conversion import pdf_to_excel

        submit = json.loads(await pdf_to_excel(document_id=uploaded_pdf))
        task_id = _assert_task_submitted(submit)
        completed = await _poll_task(task_id)
        _assert_completed(completed)


class TestPdfToPptE2E:
    async def test_full_flow(self, uploaded_pdf):
        from foxit_pdf_api_mcp_server.tools.pdf_conversion import pdf_to_ppt

        submit = json.loads(await pdf_to_ppt(document_id=uploaded_pdf))
        task_id = _assert_task_submitted(submit)
        completed = await _poll_task(task_id)
        _assert_completed(completed)


class TestPdfToTextE2E:
    async def test_full_flow(self, uploaded_pdf):
        from foxit_pdf_api_mcp_server.tools.pdf_conversion import pdf_to_text

        submit = json.loads(await pdf_to_text(document_id=uploaded_pdf))
        task_id = _assert_task_submitted(submit)
        completed = await _poll_task(task_id)
        _assert_completed(completed)


class TestPdfToHtmlE2E:
    async def test_full_flow(self, uploaded_pdf):
        from foxit_pdf_api_mcp_server.tools.pdf_conversion import pdf_to_html

        submit = json.loads(await pdf_to_html(document_id=uploaded_pdf))
        task_id = _assert_task_submitted(submit)
        completed = await _poll_task(task_id)
        _assert_completed(completed)


class TestPdfToImageE2E:
    async def test_full_flow(self, uploaded_pdf):
        from foxit_pdf_api_mcp_server.tools.pdf_conversion import pdf_to_image

        submit = json.loads(await pdf_to_image(document_id=uploaded_pdf))
        task_id = _assert_task_submitted(submit)
        completed = await _poll_task(task_id)
        _assert_completed(completed)

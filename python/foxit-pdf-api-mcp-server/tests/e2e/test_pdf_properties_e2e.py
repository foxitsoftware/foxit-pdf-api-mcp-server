"""End-to-end tests for pdf_properties tools.

These tests call the real Foxit Cloud API — no mocking.
They require valid credentials in .env and a working network connection.

get_pdf_properties returns data directly (no taskId / no polling).

Run:
    pytest tests/e2e/test_pdf_properties_e2e.py -v
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


@pytest.fixture(scope="module")
async def uploaded_pdf():
    from foxit_pdf_api_mcp_server.tools.document_lifecycle import upload_document

    b64 = base64.b64encode((FIXTURES_DIR / "sample.pdf").read_bytes()).decode()
    result_json = await upload_document(file_content=b64, file_name="sample.pdf")
    data = json.loads(result_json)
    assert data["success"] is True, f"Upload failed: {data}"
    doc_id = data["resultDocumentId"]
    _doc_ids_to_cleanup.append(doc_id)
    return doc_id


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestGetPdfPropertiesE2E:
    async def test_full_flow(self, uploaded_pdf):
        """Validate success response with properties object."""
        from foxit_pdf_api_mcp_server.tools.pdf_properties import get_pdf_properties

        result = json.loads(await get_pdf_properties(document_id=uploaded_pdf))

        assert result["success"] is True, f"Failed: {result}"
        assert "message" in result
        assert isinstance(result["message"], str) and len(result["message"]) > 0

        # properties must be a dict/object
        props = result.get("properties")
        assert props is not None, f"Missing 'properties': {result}"
        assert isinstance(props, dict), f"'properties' is not dict: {type(props)}"

    async def test_with_extended_info(self, uploaded_pdf):
        from foxit_pdf_api_mcp_server.tools.pdf_properties import get_pdf_properties

        result = json.loads(
            await get_pdf_properties(
                document_id=uploaded_pdf,
                include_extended_info=True,
                include_page_info=True,
            )
        )

        assert result["success"] is True
        props = result["properties"]
        assert isinstance(props, dict)

    async def test_without_extended_info(self, uploaded_pdf):
        from foxit_pdf_api_mcp_server.tools.pdf_properties import get_pdf_properties

        result = json.loads(
            await get_pdf_properties(
                document_id=uploaded_pdf,
                include_extended_info=False,
                include_page_info=False,
            )
        )

        assert result["success"] is True
        props = result["properties"]
        assert isinstance(props, dict)

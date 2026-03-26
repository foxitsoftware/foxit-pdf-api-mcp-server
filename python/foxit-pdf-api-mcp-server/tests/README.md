# Tests

Two test suites for the Foxit PDF API MCP Server:

- **MCP Protocol Tests** (`tests/mcp/`) — verify the MCP protocol layer (tool discovery, schema validation, routing, response format, error handling) via in-memory transport. All Foxit HTTP calls are mocked. Runs in ~1 second.
- **E2E Tests** (`tests/e2e/`) — call the real Foxit Cloud API to validate end-to-end business logic. No mocking.

## Prerequisites

1. **Python 3.10+** installed.
2. Install dev dependencies (from the project root):
   ```bash
   pip install -e ".[dev]"
   ```
   Or, if using `uv`:
   ```bash
   uv pip install -e ".[dev]"
   ```
3. **For E2E tests only**: A `.env` file in the project root with valid API credentials:
   ```
   FOXIT_CLOUD_API_CLIENT_ID=your-client-id
   FOXIT_CLOUD_API_CLIENT_SECRET=your-client-secret
   ```
   E2E tests use real credentials to call the Foxit Cloud API. A working network connection is required.

   MCP protocol tests do **not** require API credentials (all HTTP calls are mocked).

## Project Structure

```
tests/
├── fixtures/
│   ├── sample.pdf               # PDF for conversion / manipulation tests
│   ├── sample_2pages.pdf        # 2-page PDF for delete/reorder page tests
│   ├── sample_protected.pdf     # Password-protected PDF (password: test1234)
│   ├── sample.docx              # Word file for pdf_from_word
│   ├── sample.xlsx              # Excel file for pdf_from_excel
│   ├── sample.pptx              # PowerPoint file for pdf_from_ppt
│   ├── sample.txt               # Plain text file for pdf_from_text
│   ├── sample.html              # HTML file for pdf_from_html
│   └── sample.png               # Image file for pdf_from_image
├── mcp/
│   ├── conftest.py                    # MCP fixtures (mocked client, in-memory transport)
│   ├── test_tool_discovery.py         # list_tools: names, descriptions, schemas
│   ├── test_tool_annotations.py       # readOnlyHint / destructiveHint validation
│   ├── test_protocol_routing.py       # call_tool routing + response format
│   └── test_error_handling.py         # Missing/extra params, unknown tools, internal errors
├── e2e/
│   ├── conftest.py                    # E2E fixtures (refresh_http_client)
│   ├── test_pdf_conversion_e2e.py     # PDF → Word/Excel/Ppt/Text/Html/Image
│   ├── test_pdf_creation_e2e.py       # Word/Excel/Ppt/Text/Html/Image/URL → PDF
│   ├── test_pdf_manipulation_e2e.py   # Merge, split, extract, compress, flatten, etc.
│   ├── test_pdf_properties_e2e.py     # Get PDF properties and metadata
│   └── test_pdf_security_e2e.py       # Protect and remove password
└── README.md
```

Fixture files in `fixtures/` are real sample documents. Replace them with your own files as needed — tests only require the filenames to match.

## Running Tests

All commands should be run from the project root directory:

```bash
cd python/foxit-pdf-api-mcp-server
```

### Run all tests (MCP + E2E)

```bash
python -m pytest -v
```

### Run only MCP protocol tests (fast, no API key needed)

```bash
python -m pytest tests/mcp/ -v
```

### Run only E2E tests (requires API key)

```bash
python -m pytest tests/e2e/ -v
```

### Run a specific test file

```bash
python -m pytest tests/mcp/test_tool_discovery.py -v
python -m pytest tests/e2e/test_pdf_conversion_e2e.py -v
```

### Run a specific test class

```bash
python -m pytest tests/e2e/test_pdf_conversion_e2e.py::TestPdfToWordE2E -v
```

### Run a single test case

```bash
python -m pytest tests/e2e/test_pdf_conversion_e2e.py::TestPdfToWordE2E::test_full_flow -v
```

### Run with coverage report

```bash
python -m pytest -v --cov=foxit_pdf_api_mcp_server --cov-report=term-missing
```

## Test Design

### MCP Protocol Tests (`tests/mcp/`)

Uses `fastmcp.Client(mcp)` with **in-memory transport** — no network, no server process. All `FoxitPDFClient` methods are mocked via `unittest.mock.patch.object` so tests run in ~1 second.

| File | What it tests | Tests |
|------|---------------|-------|
| `test_tool_discovery.py` | `list_tools()` returns all 32 tools with correct names, descriptions, inputSchema, required/optional params, parameter types | 9 |
| `test_tool_annotations.py` | `readOnlyHint` / `destructiveHint` annotations match intended access patterns for all tools | 5 |
| `test_protocol_routing.py` | `call_tool()` routes to the correct tool function; `CallToolResult` contains valid JSON `TextContent`; task-based / direct-result / properties tools all respond correctly | 31 |
| `test_error_handling.py` | Unknown tools → `ToolError`; missing required params → `ToolError`; unexpected params → `ToolError`; internal exceptions → graceful `success=False` JSON | 14 |
| **Total** | | **59** |

### E2E Tests (`tests/e2e/`)

All tests call the real Foxit Cloud API — no mocking. Tests use `loop_scope="module"` so all tests in a file share one event loop.

### Response schema validation

Every test validates the full documented response contract:

- **Task-based tools** (conversion, creation, manipulation): submit → assert `success`, `taskId`, `message` → poll `get_task_result` → assert `success`, `status="completed"`, `taskId`, `message`, `resultDocumentId`, `shareUrl`.
- **Synchronous tools** (properties): assert `success`, `message`, `properties` (dict).
- **Execute-and-wait tools** (security): assert `success`, `message`, `resultDocumentId`, `shareUrl`.

### Test files

| File | Tools covered | Tests |
|------|---------------|-------|
| `test_pdf_conversion_e2e.py` | `pdf_to_word`, `pdf_to_excel`, `pdf_to_ppt`, `pdf_to_text`, `pdf_to_html`, `pdf_to_image` | 6 |
| `test_pdf_creation_e2e.py` | `pdf_from_word`, `pdf_from_excel`, `pdf_from_ppt`, `pdf_from_text`, `pdf_from_image`, `pdf_from_html`, `pdf_from_url` | 9 |
| `test_pdf_manipulation_e2e.py` | `pdf_merge`, `pdf_split`, `pdf_extract_pages`, `pdf_extract_text`, `pdf_compress`, `pdf_flatten`, `pdf_linearize`, `pdf_manipulate`, `pdf_delete_pages`, `pdf_rotate_pages`, `pdf_reorder_pages` | 11 |
| `test_pdf_properties_e2e.py` | `get_pdf_properties` | 3 |
| `test_pdf_security_e2e.py` | `pdf_protect`, `pdf_remove_password` | 4 |
| **Total** | | **33** |

### Fixtures

| Fixture | Scope | Location | Description |
|---------|-------|----------|-------------|
| `mock_foxit_client` | function (autouse) | `tests/mcp/conftest.py` | Patches all `FoxitPDFClient` methods with `AsyncMock`. No HTTP traffic. |
| `mcp_client` | function | `tests/mcp/conftest.py` | `fastmcp.Client(mcp)` connected via in-memory transport. |
| `refresh_http_client` | module | `tests/e2e/conftest.py` | Recreates `httpx.AsyncClient` to bind to the current event loop. |
| `uploaded_pdf` | module | per E2E test file | Uploads `sample.pdf` via real API, yields `document_id`, deletes on teardown. |

## Summary

| Suite | Tests | Speed | API Key Required | What it validates |
|-------|-------|-------|-----------------|-------------------|
| MCP Protocol | 59 | ~1s | No | Tool discovery, annotations, schema validation, routing, response format, error handling |
| E2E | 33 | ~5min | Yes | Full business logic against real Foxit Cloud API |
| **Total** | **92** | | | |

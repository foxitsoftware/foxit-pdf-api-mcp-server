# Contributing to Foxit PDF API MCP Server

## Development Setup

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended) or pip

### Setup Development Environment

```bash
# Clone the repository
cd foxit-pdf-api-mcp-server

# Install with dev dependencies
uv pip install -e ".[dev]"

# Or with pip
pip install -e ".[dev]"
```

## Running the Server

The server supports two transport modes:

### Stdio Mode (Default)

For use with MCP clients like Claude Desktop, Cursor, etc.:

```bash
# Run directly
foxit-pdf-api-mcp-server

# Or with uv
uv run foxit-pdf-api-mcp-server

# Or as Python module
python -m foxit_pdf_api_mcp_server
```

### HTTP Mode

For development, testing, or web-based integrations:

```bash
# Start HTTP server on default port (8000)
foxit-pdf-api-mcp-server --transport http

# Custom host and port
foxit-pdf-api-mcp-server --transport http --host 0.0.0.0 --port 9000

# Short form
foxit-pdf-api-mcp-server -t http -p 3000
```

The HTTP server will be available at `http://127.0.0.1:8000` (or your specified host/port).

**Testing the HTTP Server:**

```bash
# Check server health
curl http://localhost:8000/health

# List available tools
curl http://localhost:8000/tools
```

## Development Workflow

1. **Make code changes** in `src/foxit_pdf_api_mcp_server/`
2. **Test with HTTP mode** for quick iteration:
   ```bash
   foxit-pdf-api-mcp-server -t http
   ```
3. **Test with stdio mode** for MCP client integration:
   ```bash
   # Test stdio communication
   echo '{"jsonrpc":"2.0","method":"initialize","params":{},"id":1}' | foxit-pdf-api-mcp-server
   ```

## Testing

### Run Tests

```bash
pytest
```

### Run Tests with Coverage

```bash
pytest --cov=foxit_pdf_api_mcp_server --cov-report=html
```

## Code Quality

### Format Code

```bash
# Auto-format with ruff
ruff format .
```

### Lint Code

```bash
# Check linting issues
ruff check .

# Auto-fix linting issues
ruff check --fix .
```

### Type Check

```bash
# Run mypy type checker
mypy src/
```

### Run All Quality Checks

```bash
# Format, lint, and type check
ruff format . && ruff check . && mypy src/
```

## Project Structure

```
foxit-pdf-api-mcp-server/
├── src/
│   └── foxit_pdf_api_mcp_server/
│       ├── __init__.py           # Package initialization
│       ├── __version__.py        # Version info (from pyproject.toml)
│       ├── main.py               # CLI entry point
│       ├── config.py             # Configuration management
│       ├── server.py             # FastMCP server setup
│       │
│       ├── client/               # HTTP Client Layer
│       │   ├── __init__.py
│       │   └── foxit_client.py  # Pure HTTP client for Foxit API
│       │
│       ├── tools/                # MCP Tools Layer
│       │   ├── __init__.py
│       │   ├── _base.py         # Base utilities (response formatting)
│       │   └── document_lifecycle.py  # Upload/download/delete tools
│       │
│       ├── types/                # Type Definitions
│       │   ├── __init__.py
│       │   └── api.py           # API type definitions
│       │
│       └── utils/                # Utilities
│           ├── __init__.py
│           └── task_poller.py   # Async task polling
│
├── tests/                        # Unit tests
├── pyproject.toml               # Project configuration
├── .env.example                 # Environment variable template
├── .gitignore                   # Git ignore rules
├── README.md                    # User documentation
├── CONTRIBUTING.md              # This file
└── DESIGN.md                    # Architecture documentation
```

## Architecture

This implementation follows the same structure as the TypeScript version for consistency:

### Layers

- **Client Layer** (`client/foxit_client.py`): Pure HTTP client for Foxit API
  - Handles all API requests
  - Authentication
  - Error handling
  - No MCP-specific logic

- **Tools Layer** (`tools/`): MCP tool definitions using FastMCP decorators
  - Each tool file registers functions with `@mcp.tool()` decorator
  - Tools import `mcp` and `client` singletons from `server.py`
  - Consistent error handling and response formatting

- **Utils Layer** (`utils/`): Shared utilities
  - Task polling for async operations
  - Common helper functions

- **Server** (`server.py`): FastMCP server initialization
  - Creates `mcp` and `client` singleton instances
  - Tools are auto-registered by importing their modules

### Adding a New Tool

1. Create a new file in `src/foxit_pdf_api_mcp_server/tools/` (e.g., `pdf_from_word.py`)

2. Import the singletons and define your tool:

```python
"""PDF from Word conversion tool."""

from typing import Optional

from ..server import client, mcp
from ..utils import execute_and_wait
from ._base import format_error_response, format_success_response


@mcp.tool()
async def pdf_from_word(document_id: str) -> str:
    """
    Convert a Microsoft Word document to PDF format.
    
    Args:
        document_id: Document ID of the uploaded Word file
        
    Returns:
        JSON string with success status and result document ID
    """
    try:
        result = await execute_and_wait(
            client,
            lambda: client.pdf_from_word(document_id)
        )
        
        return format_success_response(
            task_id=result["taskId"],
            result_document_id=result.get("resultDocumentId"),
            message="Word document converted to PDF successfully"
        )
    except Exception as error:
        return format_error_response(error)
```

3. Import the module in `server.py`:

```python
# Import tools to register them (tools use @mcp.tool() decorator)
from .tools import document_lifecycle  # noqa: E402, F401
from .tools import pdf_from_word  # noqa: E402, F401  <- Add this line
```

That's it! The tool will be automatically registered when the module is imported.

## Adding Client Methods

To add a new API endpoint to the client:

1. Add the method to `client/foxit_client.py`:

```python
async def pdf_from_word(self, document_id: str) -> OperationResponse:
    """Convert Word document to PDF."""
    response = await self._make_request(
        "POST",
        "/api/documents/create/pdf-from-word",
        json={"documentId": document_id},
    )
    data = await self._handle_response(response)
    return OperationResponse(taskId=data["taskId"])
```

2. The method is now available to all tools via `client.pdf_from_word()`

## Code Style Guidelines

- **Type Hints**: Use type hints for all function parameters and return values
- **Docstrings**: Add docstrings to all public functions and classes
- **Line Length**: Maximum 100 characters (configured in pyproject.toml)
- **Imports**: Organize imports (stdlib, third-party, local)
- **Async**: Use `async`/`await` for all I/O operations

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following the code style guidelines
4. Run all quality checks (format, lint, type check, tests)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Questions?

- Check the [README.md](README.md) for usage information
- Contact: support@foxitsoftware.com

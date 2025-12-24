# Foxit PDF API MCP Server (Python)

Model Context Protocol (MCP) server that exposes [Foxit Cloud PDF API](https://developer-api.foxit.com) operations as tools for AI agents like Claude Desktop, Cursor, and other MCP-compatible applications.

## Features

**30+ PDF Operations Available:**

- 📄 **Document Lifecycle** - Upload, download, delete documents
- 🔄 **PDF Creation** - Convert Word, Excel, PPT, HTML, URL, text, images to PDF
- 📤 **PDF Conversion** - Convert PDF to Word, Excel, PPT, HTML, text, images
- ✂️ **Manipulation** - Split, merge, extract, compress, flatten, linearize, watermark, page operations
- 🔒 **Security** - Add/remove passwords, set permissions
- 📊 **Properties** - Extract comprehensive PDF metadata and properties
- 🔍 **Analysis** - Compare PDFs

**All tools implemented and ready to use!**

## Quick Start

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended) or pip

### 1. Get API Credentials

Sign up at [Foxit Developer Portal](https://developer-api.foxit.com) to get your:

- Client ID
- Client Secret

### 2. Install with uv (Recommended)

```bash
# Clone or download the repository
cd foxit-pdf-api-mcp-server

# Install with uv
uv pip install -e .
```

### 3. Install with pip

```bash
pip install -e .
```

## Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```bash
# API Base URL (choose your region)
# North America:
FOXIT_CLOUD_API_HOST=https://na1.fusion.foxit.com/pdf-services

# API Credentials
FOXIT_CLOUD_API_CLIENT_ID=your_client_id
FOXIT_CLOUD_API_CLIENT_SECRET=your_client_secret
```

## Integration

### VS Code

In `.vscode/mcp.json`:

```json
{
  "servers": {
    "foxit-pdf": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/foxit-pdf-api-mcp-server",
        "run",
        "foxit-pdf-api-mcp-server"
      ],
      "env": {
        "FOXIT_CLOUD_API_HOST": "https://na1.fusion.foxit.com/pdf-services",
        "FOXIT_CLOUD_API_CLIENT_ID": "your_client_id",
        "FOXIT_CLOUD_API_CLIENT_SECRET": "your_client_secret"
      }
    }
  }
}
```

## Usage Examples

### Uploading a Document

Ask your AI assistant:

> "Upload my document report.pdf"

The agent will:

1. Use the `upload_document` tool
2. Return a documentId for subsequent operations

### Downloading a Document

Ask your AI assistant:

> "Download document abc123 to /path/to/output.pdf"

The agent will:

1. Use the `download_document` tool
2. Save the file to the specified path

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed development setup, workflow, and contribution guidelines.

Quick start:

```bash
# Install with dev dependencies
uv pip install -e ".[dev]"

# Run in HTTP mode for testing
foxit-pdf-api-mcp-server --transport http

# Run in stdio mode (default)
foxit-pdf-api-mcp-server
```

## Troubleshooting

### Import Errors

Make sure you've installed the package:

```bash
uv pip install -e .
```

### Authentication Errors

Verify your credentials are correct:

```bash
echo $FOXIT_CLOUD_API_CLIENT_ID
echo $FOXIT_CLOUD_API_CLIENT_SECRET
```

## Related Projects

- [TypeScript Version](../typescript/foxit-pdf-api-mcp-server) - Node.js/TypeScript implementation
- [Foxit PDF API Documentation](https://developer-api.foxit.com/docs)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and contribution guidelines.

## License

MIT

## Support

- Documentation: [https://developer-api.foxit.com](https://developer-api.foxit.com)
- Issues: File issues on GitHub

# Foxit PDF API MCP Server

Model Context Protocol (MCP) server that exposes [Foxit Cloud PDF API](https://developer-api.foxit.com) operations as tools for AI agents like Claude Desktop, Cursor, and other MCP-compatible applications.

## Features

**30+ PDF Operations Available:**

- 📄 **Document Lifecycle** - Upload, download, delete documents
- 🔄 **PDF Creation** - Convert Word, Excel, PPT, HTML, URL, text, images to PDF
- 📤 **PDF Conversion** - Convert PDF to Word, Excel, PPT, HTML, text, images
- ✂️ **Manipulation** - Split, extract, flatten, compress, manipulate pages
- 🔒 **Security** - Add/remove passwords, set permissions
- 🎨 **Enhancement** - Merge, watermark, linearize PDFs
- 🔍 **Analysis** - Get properties, compare PDFs, etc.

## Quick Start

### 1. Get API Credentials

Sign up at [Foxit Developer Portal](https://developer-api.foxit.com) to get your:

- Client ID
- Client Secret

### 2. Set Environment Variables

The server reads API credentials from environment variables:

| Variable                        | Description                                       | Default                                     |
| ------------------------------- | ------------------------------------------------- | ------------------------------------------- |
| `FOXIT_CLOUD_API_CLIENT_ID`     | Your Foxit API client ID                          | _(required)_                                |
| `FOXIT_CLOUD_API_CLIENT_SECRET` | Your Foxit API client secret                      | _(required)_                                |
| `FOXIT_CLOUD_API_HOST`          | Foxit API base URL                                | `https://na1.fusion.foxit.com/pdf-services` |
| `FOXIT_CLOUD_API_BASE_URL`      | Alias for `FOXIT_CLOUD_API_HOST` (takes priority) | —                                           |

```bash
export FOXIT_CLOUD_API_CLIENT_ID="your_client_id"
export FOXIT_CLOUD_API_CLIENT_SECRET="your_client_secret"
# Optional — override the default API host:
# export FOXIT_CLOUD_API_HOST="https://na1.fusion.foxit.com/pdf-services"
```

### 3. Run the Server

The server supports two transport types: **stdio** (default) and **HTTP stream**. Choose based on how your MCP client connects.

#### Using `npx` (no installation needed)

```bash
# stdio transport (default) — for Claude Desktop, VS Code, Cursor, etc.
npx @foxitsoftware/foxit-pdf-api-mcp-server --transport stdio

# HTTP stream transport — for web-based clients or remote access
npx @foxitsoftware/foxit-pdf-api-mcp-server --transport httpStream --port 8080
```

#### Using `node` (after global install or from source)

```bash
# Install globally
npm install -g @foxitsoftware/foxit-pdf-api-mcp-server

# Run with stdio transport
foxit-pdf-api-mcp-server --transport stdio

# Run with HTTP stream transport
foxit-pdf-api-mcp-server --transport httpStream --port 8080
```

### CLI Options

| Option                            | Description                               | Default   |
| --------------------------------- | ----------------------------------------- | --------- |
| `--transport <stdio\|httpStream>` | Transport type                            | `stdio`     |
| `--host <host>`                   | HTTP stream bind address                  | `127.0.0.1` |
| `--port <port>`                   | HTTP stream port                          | `8080`      |
| `--endpoint <path>`               | HTTP stream endpoint path                 | `/mcp`      |
| `--stateless`                     | Enable stateless HTTP stream mode         | `false`     |
| `--enable-json-response`          | Enable JSON response mode for HTTP stream | `false`     |
| `--auth-token <token>`            | Bearer token required for HTTP requests   | —           |
| `--ssl-cert <path>`               | Path to SSL certificate                   | —           |
| `--ssl-key <path>`                | Path to SSL private key                   | —           |
| `--ssl-ca <path>`                 | Path to SSL CA bundle                     | —           |
| `-h, --help`                      | Show help                                 | —           |

**HTTP stream env var defaults:** `SERVER_HOST` and `SERVER_PORT` override the built-in defaults for `--host` and `--port`.

**Security:** The HTTP transport binds to loopback (`127.0.0.1`) by default. Binding to a
non-loopback host (e.g. `--host 0.0.0.0`) **requires** an auth token (`--auth-token` or
`MCP_AUTH_TOKEN`); the server refuses to start otherwise. `upload_document` /
`download_document` are confined to `MCP_FS_ALLOWED_DIRS` (default
`~/Downloads:~/Desktop:~/Documents:<tmp>`).

Run `npx @foxitsoftware/foxit-pdf-api-mcp-server --help` to see all options.

### Verifying the HTTP Server

When running with `--transport httpStream`, the server exposes a health check endpoint:

```bash
# Start the server
npx @foxitsoftware/foxit-pdf-api-mcp-server --transport httpStream --port 8080

# In another terminal, verify it's running
curl http://localhost:8080/healthz
# → "healthy"
```

The MCP endpoint is available at `http://localhost:8080/mcp` by default.

## Integration

### Claude Desktop

Claude Desktop uses **stdio** transport — it spawns the server as a child process.

Add to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "foxit-pdf": {
      "command": "npx",
      "args": [
        "-y",
        "@foxitsoftware/foxit-pdf-api-mcp-server",
        "--transport",
        "stdio"
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

Restart Claude Desktop. The PDF tools will appear in the tools menu.

> **Tip:** The `--transport stdio` flag is optional (stdio is the default), but including it makes the config self-documenting.

### VS Code (GitHub Copilot)

VS Code has native MCP support via `.vscode/mcp.json`. Both **stdio** and **HTTP stream** transports are supported.

#### Option A: stdio transport (recommended for local use)

Create a `.vscode/mcp.json` file in your workspace root:

```json
{
  "servers": {
    "foxit-pdf": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "-y",
        "@foxitsoftware/foxit-pdf-api-mcp-server",
        "--transport",
        "stdio"
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

#### Option B: HTTP stream transport (for shared/remote servers)

First, start the server in a terminal:

```bash
npx @foxitsoftware/foxit-pdf-api-mcp-server --transport httpStream --port 8080
```

Then create a `.vscode/mcp.json` file in your workspace root:

```json
{
  "servers": {
    "foxit-pdf": {
      "type": "http",
      "url": "http://localhost:8080/mcp"
    }
  }
}
```

After saving the file, VS Code will prompt you to approve the MCP server. Once approved, the Foxit PDF tools will be available in Copilot Chat.

> **Note:** You can also configure MCP servers via the VS Code Command Palette → `Preferences: Open User Settings (JSON)` → `chat.mcp.discovery.enabled` and the MCP view in the sidebar.

### Other MCP Clients

For any MCP-compatible client (Cursor, Windsurf, Cline, etc.), configure the server using one of these patterns:

**stdio transport** (client spawns the server):

- **Command**: `npx`
- **Args**: `["-y", "@foxitsoftware/foxit-pdf-api-mcp-server", "--transport", "stdio"]`
- **Environment**: Set `FOXIT_CLOUD_API_CLIENT_ID`, `FOXIT_CLOUD_API_CLIENT_SECRET`, and optionally `FOXIT_CLOUD_API_HOST`

**HTTP stream transport** (connect to a running server):

- **URL**: `http://localhost:8080/mcp` (or wherever the server is running)
- Start the server first with `npx @foxitsoftware/foxit-pdf-api-mcp-server --transport httpStream --port 8080`

## Usage Examples

### Converting Documents to PDF

Ask your AI assistant:

> "Convert my Word document `report.docx` to PDF"

The agent will:

1. Upload the document
2. Convert it to PDF
3. Download the result
4. Clean up temporary files

### Merging PDFs

> "Merge `chapter1.pdf`, `chapter2.pdf`, and `chapter3.pdf` into one document"

### Adding Watermarks

> "Add a watermark 'CONFIDENTIAL' to my PDF document"

### Converting PDF to Other Formats

> "Convert this PDF to a Word document so I can edit it"

## Available Tools

The server exposes 35+ tools organized by category:

### Document Management

- `upload_document` - Upload files for processing
- `download_document` - Download processed documents
- `delete_document` - Remove uploaded documents
- `create_share_link` - Generate a temporary share link for a document
- `get_task_result` - Poll the status of an async operation and retrieve the result

### PDF Creation (to PDF)

- `pdf_from_word` - Word → PDF
- `pdf_from_excel` - Excel → PDF
- `pdf_from_ppt` - PowerPoint → PDF
- `pdf_from_html` - HTML → PDF
- `pdf_from_url` - Web page → PDF
- `pdf_from_text` - Plain text → PDF
- `pdf_from_image` - Images → PDF

### PDF Conversion (from PDF)

- `pdf_to_word` - PDF → Word
- `pdf_to_excel` - PDF → Excel
- `pdf_to_ppt` - PDF → PowerPoint
- `pdf_to_html` - PDF → HTML
- `pdf_to_text` - PDF → Plain text
- `pdf_to_image` - PDF → Images

### PDF Operations

- `pdf_merge` - Combine multiple PDFs
- `pdf_split` - Split PDF by page count
- `pdf_extract_pages` - Extract selected pages into a new PDF
- `pdf_extract_text` - Extract plain text from selected pages
- `pdf_compress` - Reduce file size
- `pdf_flatten` - Flatten form fields and annotations
- `pdf_manipulate` - Apply batch page operations (rotate, delete, reorder)
- `pdf_delete_pages` - Delete specific pages
- `pdf_rotate_pages` - Rotate specific pages
- `pdf_reorder_pages` - Reorder pages

### Security

- `pdf_protect` - Add password protection
- `pdf_remove_password` - Remove password protection

### Enhancement

- `pdf_watermark` - Add text/image watermarks
- `pdf_linearize` - Optimize for web viewing

### Analysis & Forms

- `pdf_compare` - Compare two PDFs
- `export_pdf_form_data` - Extract form field values as JSON
- `import_pdf_form_data` - Fill form fields from a JSON object
- `get_pdf_properties` - Retrieve PDF metadata

> **Async model:** Most PDF operations return a `taskId` immediately. Use `get_task_result` to poll for completion and retrieve the download link. Tools that complete synchronously (e.g., `pdf_protect`, form tools) return the result directly.

## Troubleshooting

### Server Not Starting

- Ensure `FOXIT_CLOUD_API_CLIENT_ID` and `FOXIT_CLOUD_API_CLIENT_SECRET` are set in your MCP client config
- Verify your API credentials at [Foxit Developer Portal](https://developer-api.foxit.com)
- Check that `npx` can access the npm registry (try `npx -y @foxitsoftware/foxit-pdf-api-mcp-server --version`)

### Tools Not Appearing

- Restart your MCP client (Claude Desktop, etc.) after configuration changes
- Check the client logs for connection errors
- Ensure the `-y` flag is included in npx args to auto-accept installation

### API Errors

- Ensure your API credentials are valid and not expired
- Check your API usage quota at the developer portal
- Verify the API host URL is correct for your region

## Development

See [CONTRIBUTING.md](./CONTRIBUTING.md) for development setup, architecture details, and contribution guidelines.

## License

MIT

## Links

- [Foxit Cloud PDF API Documentation](https://developer-api.foxit.com/docs)
- [Report Issues](https://github.com/foxitsoftware/foxit-pdf-api-mcp-server/issues)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Claude Desktop](https://claude.ai/download)

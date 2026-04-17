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

### 2. Install the Server

The server is published on npm and can be run directly with `npx`:

```bash
npx @foxitsoftware/foxit-pdf-api-mcp-server
```

Or install globally:

```bash
npm install -g @foxitsoftware/foxit-pdf-api-mcp-server
```

## Integration

### Claude Desktop

Add to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "foxit-pdf": {
      "command": "npx",
      "args": ["-y", "@foxitsoftware/foxit-pdf-api-mcp-server"],
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

### Cursor / VS Code (with Cline Extension)

Add to Cline MCP settings:

```json
{
  "mcpServers": {
    "foxit-pdf": {
      "command": "npx",
      "args": ["-y", "@foxitsoftware/foxit-pdf-api-mcp-server"],
      "env": {
        "FOXIT_CLOUD_API_HOST": "https://na1.fusion.foxit.com/pdf-services",
        "FOXIT_CLOUD_API_CLIENT_ID": "your_client_id",
        "FOXIT_CLOUD_API_CLIENT_SECRET": "your_client_secret"
      }
    }
  }
}
```

### Other MCP Clients

For any MCP-compatible client, configure a stdio transport server:
- **Command**: `npx`
- **Args**: `["-y", "@foxitsoftware/foxit-pdf-api-mcp-server"]`
- **Environment**: Set the three `FOXIT_CLOUD_API_*` variables

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
- `download_document` - Download processed documents *(TypeScript-only)*
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
- `pdf_watermark` - Add text/image watermarks *(TypeScript-only)*
- `pdf_linearize` - Optimize for web viewing

### Analysis & Forms
- `pdf_compare` - Compare two PDFs
- `pdf_ocr` - Optical character recognition *(TypeScript-only)*
- `pdf_structural_analysis` - Extract document structure as JSON *(TypeScript-only)*
- `export_pdf_form_data` - Extract form field values as JSON
- `import_pdf_form_data` - Fill form fields from a JSON object
- `get_pdf_properties` - Retrieve PDF metadata

### MCP App Widgets
- `show_pdf_tools` - Open the PDF Tools widget in the agent UI
- `show_pdf_viewer` - Open the PDF Viewer widget to preview a document

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

## MCP App Widgets

The server includes two interactive widgets that render inside a supported agent UI (e.g., VS Code with Copilot, Claude Desktop with MCP Apps support).

The widgets are built from [`shared/ui/`](../../shared/ui) at the repository root. Node.js 18+ is required. Build them once before starting the server:

```bash
# From the repo root — with npm:
npm run build:ui

# or with pnpm:
pnpm run build:ui
```

This produces `shared/ui/dist/index.html` and `shared/ui/dist/viewer.html`, which the server loads automatically at runtime.

## Development

See [CONTRIBUTING.md](./CONTRIBUTING.md) for development setup, architecture details, and contribution guidelines.

## License

MIT

## Links

- [Foxit Cloud PDF API Documentation](https://developer-api.foxit.com/docs)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Claude Desktop](https://claude.ai/download)
- [Report Issues](https://github.com/foxit/cloud-pdf-api/issues)

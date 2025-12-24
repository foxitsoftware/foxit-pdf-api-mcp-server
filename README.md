# Foxit PDF API MCP Servers

Model Context Protocol (MCP) servers that expose [Foxit PDF Services API](https://developer-api.foxit.com) operations as tools for AI agents like Claude Desktop, Cursor, and other MCP-compatible applications.

## Overview

This directory contains multiple implementations of the Foxit PDF API MCP Server:

### 🐍 **Python Version** 
- **Location**: [`python/foxit-pdf-api-mcp-server/`](./python/foxit-pdf-api-mcp-server/)
- **Features**: 35+ PDF operations including creation, conversion, manipulation, security, OCR, forms, and analysis
- **Technologies**: FastMCP, Python 3.11+, uv package manager
- **Status**: ✅ **Active development** - Full feature parity with TypeScript version

👉 **[View Python README](./python/foxit-pdf-api-mcp-server/README.md)** for installation and usage instructions.

### 📘 **TypeScript Version**
- **Location**: [`typescript/foxit-pdf-api-mcp-server/`](./typescript/foxit-pdf-api-mcp-server/)
- **Features**: 35+ PDF operations with comprehensive TypeScript support
- **Technologies**: TypeScript, Node.js, pnpm
- **Status**: ✅ **Active development** - Full feature parity with Python version

👉 **[View TypeScript README](./typescript/foxit-pdf-api-mcp-server/README.md)** for installation and usage instructions.

### ⚠️ **stdio-python** (Legacy)
- **Location**: [`stdio-python/`](./stdio-python/)
- **Status**: ⚠️ **DEPRECATED** - Use the new Python version above instead
- **Note**: This was the original implementation and is no longer maintained

## Features

Both Python and TypeScript versions provide:

- 📄 **Document Lifecycle** - Upload, download, delete documents
- 🔄 **PDF Creation** - Convert Word, Excel, PPT, HTML, URL, text, images to PDF
- 📤 **PDF Conversion** - Convert PDF to Word, Excel, PPT, HTML, text, images
- ✂️ **Manipulation** - Split, merge, extract, compress, flatten, linearize, watermark, page operations
- 🔒 **Security** - Add/remove passwords, set permissions
- 📊 **Properties** - Extract comprehensive PDF metadata and properties
- 🔍 **Analysis** - Compare PDFs
- 📝 **Forms** - Export and import form data as JSON

## Getting Started

### Prerequisites

- **API Credentials**: Sign up at [Foxit Developer Portal](https://developer-api.foxit.com) to get your Client ID and Client Secret
- **Python Version**: Python 3.11+ and [uv](https://github.com/astral-sh/uv) package manager
- **TypeScript Version**: Node.js 18+ and pnpm

### Quick Start

Choose your preferred implementation:

**Python:**
```bash
cd python/foxit-pdf-api-mcp-server
# See python/foxit-pdf-api-mcp-server/README.md for full instructions
```

**TypeScript:**
```bash
cd typescript/foxit-pdf-api-mcp-server
# See typescript/foxit-pdf-api-mcp-server/README.md for full instructions
```

## Environment Variables

All versions require the following environment variables:

- **FOXIT_CLOUD_API_HOST**: API host URL (e.g., `https://na1.fusion.foxit.com/pdf-services`)
- **FOXIT_CLOUD_API_CLIENT_ID**: Your client ID from Foxit Developer Portal
- **FOXIT_CLOUD_API_CLIENT_SECRET**: Your client secret from Foxit Developer Portal

## Support

For issues or questions:
- Check the specific README for your chosen implementation
- Visit [Foxit Developer Portal](https://developer-api.foxit.com) for API documentation
- Review the CONTRIBUTING.md guide for development setup
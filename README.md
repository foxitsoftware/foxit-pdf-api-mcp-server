# Foxit Cloud API MCP Server

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A Model Context Protocol (MCP) server that integrates Foxit Cloud API PDF manipulation tools directly into your development workflow through GitHub Copilot in Visual Studio Code.

## 🚀 Features

The Foxit Cloud API MCP Server provides the following tools for PDF manipulation:

- **convert_pdf_to_file**: Convert a PDF file to formats like text, images, Word, Excel, HTML, or PowerPoint.
- **convert_file_to_pdf**: Convert files (e.g., docx, pptx, xlsx, txt, images) to PDF format.
- **convert_url_to_pdf**: Convert a web page from a URL to a PDF file.
- **combine_pdfs**: Merge multiple PDF files into a single PDF document.
- **compare_pdfs**: Compare two PDF files and generate a report or visual difference document.
- **compress_pdf**: Compress a PDF file to reduce its size with adjustable compression levels.
- **extract_pdf**: Extract text, images from a PDF file.
- **flatten_pdf**: Remove interactive elements (e.g., forms, annotations) to create a static PDF.
- **linearize_pdf**: Optimize a PDF file for fast web viewing with progressive loading.
- **remove_pdf_password**: Remove password protection from a PDF file using the owner password.
- **protect_pdf**: Add password encryption to a PDF file with user and owner passwords.
- **split_pdf**: Split a PDF file into multiple files based on the number of pages per file.
- **manipulate_pdf**: Perform page manipulations like moving, deleting, adding, or rotating pages.

## 📋 Prerequisites

Before getting started, ensure you have:

- **Python 3.10 or higher** installed and added to your PATH
- **Visual Studio Code** with the GitHub Copilot extension
- **pip** package manager (latest version recommended)
- **Foxit Cloud API credentials** (Client ID and Client Secret)

## 🔧 Installation

### Step 1: Get Your API Credentials

1. Visit the [Foxit Cloud API portal](https://www.foxit.com/api/pdf-api/)
2. Sign up for a free account
3. Obtain your **Client ID** and **Client Secret**
4. The offical host URL for the API is `https://na1.fusion.foxit.com/pdf-services`

### Step 2: Build and Install the Package

1. Clone this repository and navigate to the project directory:
   ```bash
   git clone <repository-url>
   cd foxit-pdf-api-mcp-server/stdio-python
   ```

2. Build the package:
   ```bash
   python setup.py sdist bdist_wheel
   ```

3. Install the package:
   ```bash
   pip install dist/foxit_pdf_cloudapi-1.0.3-py3-none-any.whl
   ```
   > **Note**: Replace the version number with the actual version generated during build.

### Step 3: Configure VS Code

1. Open VS Code and access the Command Palette:
   - **Windows/Linux**: `Ctrl+Shift+P`
   - **macOS**: `Cmd+Shift+P`

2. Type `MCP` and select **"MCP: Add Server..."**

3. Choose **"Command (stdio)"** as the server type

4. Enter the following command and arguments:
   ```bash
   foxit-cloudapi-mcp-service --host https://na1.fusion.foxit.com/pdf-services --client_id ${input:client-id} --client_secret ${input:client-secret}
   ```

5. Choose your configuration scope:
   - **User Setting**: Global configuration for all VS Code projects
   - **Workspace Setting**: Project-specific configuration

6. When prompted, enter your Foxit Cloud API credentials

The configuration will be saved as:

```json
{
    "version": "1.0",
    "name": "Foxit Cloud API MCP Server",
    "description": "MCP Server for Foxit Cloud API PDF manipulation tools",
    "type": "stdio",
    "command": "foxit-cloudapi-mcp-service",
    "args": [
        "--host",
        "https://na1.fusion.foxit.com/pdf-services",
        "--client_id",
        "${input:client-id}",
        "--client_secret",
        "${input:client-secret}"
    ]
}
```

## 🎯 Usage

### Starting the Server

1. **Using VS Code Interface**:
   - Open `.vscode/mcp.json` or your user settings
   - Click the **Start** button that appears above the server configuration
   - Enter your credentials when prompted (stored securely for future use)

2. **Verify Server Status**:
   - Open GitHub Copilot Chat (`Ctrl+Alt+I` / `Cmd+Ctrl+I`)
   - Switch to **Agent mode** in the chat view
   - Click the **Tools** button to view available MCP servers
   - Confirm "Foxit Cloud API MCP Server" is listed and running

### Making Your First Request

Once the server is running, you can interact with PDF tools through natural language in GitHub Copilot Chat:

```
@copilot /agent Convert this PDF to Word format
@copilot /agent Extract text from the uploaded PDF
@copilot /agent Merge these PDF files
```

## 🔍 Troubleshooting

### Common Issues

- **Server fails to start**: Check the "MCP Server Logs" in VS Code's Output panel
- **Authentication errors**: Verify your Client ID and Client Secret are correct
- **Port conflicts**: Ensure no other services are using the required ports
- **Missing dependencies**: Reinstall the package and check Python version


## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


## ⚠️ Security Notice

Only install MCP servers from trusted sources. Always review configurations before running to prevent unauthorized code execution.

---

**Made with ❤️ by the Foxit development team**


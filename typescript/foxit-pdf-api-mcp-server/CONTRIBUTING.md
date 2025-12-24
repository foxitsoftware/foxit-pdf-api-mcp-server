# Contributing to Foxit PDF API MCP Server

Thank you for your interest in contributing! This document provides guidelines and technical details for developers.

## Development Setup

### Prerequisites

- Node.js 18 or higher
- pnpm package manager
- Git

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd foxit-pdf-api-mcp-server

# Install dependencies
pnpm install

# Set up environment variables
cp .env.example .env
# Edit .env with your Foxit API credentials
```

### Development Commands

```bash
# Build the project
pnpm build

# Run in development mode (with auto-reload)
pnpm dev

# Lint code
pnpm lint

# Format code
pnpm format

# Run tests
pnpm test

# Type checking
pnpm type-check
```

## Architecture

The project follows a decoupled architecture for reusability:

```
src/
├── client/              # HTTP client (reusable, framework-agnostic)
│   ├── foxit-pdf-client.ts   # Core API client
│   └── index.ts
├── tools/               # MCP tool definitions (one file per tool/category)
│   ├── document-lifecycle.ts
│   ├── pdf-from-word.ts
│   ├── pdf-to-word.ts
│   ├── pdf-merge.ts
│   ├── pdf-protect.ts
│   ├── get-pdf-properties.ts
│   ├── pdf-advanced-operations.ts
│   ├── pdf-analysis-forms.ts
│   └── index.ts
├── types/               # TypeScript type definitions
│   └── api.ts
├── utils/               # Shared utilities
│   └── task-poller.ts   # Async task polling logic
├── index.ts             # Library exports
└── server.ts            # MCP server entry point
```

### Key Design Principles

1. **Decoupled HTTP Client**: `FoxitPDFClient` is independent of MCP and can be reused in other contexts
2. **Modular Tools**: Each tool category has its own file for maintainability
3. **Type Safety**: Full TypeScript coverage with strict mode
4. **Async Operations**: Built-in polling for long-running tasks
5. **Error Handling**: Comprehensive error handling with typed errors

## Project Structure

### HTTP Client (`src/client/foxit-pdf-client.ts`)

The core HTTP client that handles all API interactions:

```typescript
const client = new FoxitPDFClient({
  baseUrl: "https://na1.fusion.foxit.com/pdf-services",
  clientId: "your-client-id",
  clientSecret: "your-client-secret",
  defaultTimeout: 300000,
  pollInterval: 2000,
  maxRetries: 3,
});

// All API methods return typed responses
const { documentId } = await client.uploadDocument(filePath, buffer, filename);
const { taskId } = await client.pdfFromWord(documentId);
const result = await client.getTaskStatus(taskId);
```

### Task Polling (`src/utils/task-poller.ts`)

Handles asynchronous operations:

```typescript
export async function pollTaskUntilComplete(
  client: FoxitPDFClient,
  taskId: string,
  options?: PollOptions
): Promise<TaskResponse>

export async function executeAndWait<T>(
  client: FoxitPDFClient,
  operation: () => Promise<{ taskId: string }>,
  options?: PollOptions
): Promise<T>
```

### Tool Structure

Each tool follows this pattern:

```typescript
export function toolNameTool(client: FoxitPDFClient) {
  return {
    name: "tool_name",
    description: "Clear description of what the tool does",
    parameters: z.object({
      param1: z.string().describe("Parameter description"),
      param2: z.number().optional().describe("Optional parameter"),
    }),
    execute: async (args: { param1: string; param2?: number }) => {
      // Implementation using the client
      const result = await client.someMethod(args.param1);
      return {
        success: true,
        message: "Operation completed",
        ...result,
      };
    },
  };
}
```

## Adding New Tools

### 1. Add API Method to Client

Add the method to `src/client/foxit-pdf-client.ts`:

```typescript
async newOperation(
  documentId: string,
  options: OperationOptions
): Promise<OperationResponse> {
  const response = await this.fetchWithAuth("/api/path", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ documentId, ...options }),
  });

  return this.handleResponse<OperationResponse>(response);
}
```

### 2. Create Tool File

Create `src/tools/new-tool.ts`:

```typescript
import { z } from "zod";
import type { FoxitPDFClient } from "../client";
import { executeAndWait } from "../utils/task-poller";

export function newOperationTool(client: FoxitPDFClient) {
  return {
    name: "new_operation",
    description: "Performs a new operation on PDF documents",
    parameters: z.object({
      documentId: z.string().describe("Document ID to process"),
      option: z.string().optional().describe("Optional parameter"),
    }),
    execute: async (args: { documentId: string; option?: string }) => {
      const result = await executeAndWait(
        client,
        () => client.newOperation(args.documentId, { option: args.option }),
        { taskType: "new_operation" }
      );

      return {
        success: true,
        message: "Operation completed successfully",
        ...result,
      };
    },
  };
}
```

### 3. Export from Tools Index

Add to `src/tools/index.ts`:

```typescript
export * from "./new-tool";
```

### 4. Register in Server

Add to `src/server.ts`:

```typescript
import { newOperationTool } from "./tools";

// In server setup:
server.addTool(newOperationTool(foxitClient));
```

## Testing

### Running Tests

```bash
# Run all tests
pnpm test

# Run tests in watch mode
pnpm test:watch

# Run with coverage
pnpm test:coverage
```

### Manual Testing with MCP Inspector

```bash
# Start the server with inspector
pnpm dev

# The inspector will open in your browser
# You can test tools interactively
```

## Code Style

- Use TypeScript strict mode
- Follow ESLint and Prettier configurations
- Write descriptive tool names and descriptions
- Include JSDoc comments for complex functions
- Use meaningful variable names

### Naming Conventions

- **Files**: kebab-case (`pdf-from-word.ts`)
- **Functions**: camelCase (`pdfFromWordTool`)
- **Tool names**: snake_case (`pdf_from_word`)
- **Types/Interfaces**: PascalCase (`FoxitPDFClient`)
- **Constants**: UPPER_SNAKE_CASE (`API_BASE_URL`)

## Building

The project uses `tsup` for bundling:

```bash
pnpm build
```

Output:
- `dist/server.js` - MCP server bundle
- `dist/index.js` - Library bundle (for reusing the client)
- `dist/*.d.ts` - TypeScript declarations
- `dist/*.map` - Source maps

## Reusing the HTTP Client

The `FoxitPDFClient` can be used as a standalone library:

```typescript
import { FoxitPDFClient } from "@foxitsoftware/foxit-pdf-api-mcp-server";

const client = new FoxitPDFClient({
  baseUrl: "https://na1.fusion.foxit.com/pdf-services",
  clientId: process.env.CLIENT_ID,
  clientSecret: process.env.CLIENT_SECRET,
});

// Use any client method
const upload = await client.uploadDocument(path, buffer, filename);
const convert = await client.pdfFromWord(upload.documentId);
const status = await client.getTaskStatus(convert.taskId);
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-tool`)
3. Make your changes
4. Run tests and linting (`pnpm test && pnpm lint`)
5. Commit with clear messages
6. Push to your fork
7. Open a Pull Request with a clear description

## Questions or Issues?

- Check existing [GitHub Issues](https://github.com/foxit/cloud-pdf-api/issues)
- Review the [Foxit API Documentation](https://developer-api.foxit.com/docs)
- Ask in discussions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

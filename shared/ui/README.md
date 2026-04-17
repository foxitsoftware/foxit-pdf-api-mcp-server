# Foxit PDF MCP App UI

Shared Vue 3 widget UI used by both the Python and TypeScript Foxit PDF API MCP server implementations. Compiled to self-contained HTML bundles served as [MCP App](https://modelcontextprotocol.io/docs/concepts/apps) widgets inside an agent conversation.

## Overview

This package builds two widgets:

| Widget | Tool | Description |
|---|---|---|
| `dist/index.html` | `show_pdf_tools` | PDF Tools widget — upload files and trigger PDF operations from the agent UI |
| `dist/viewer.html` | `show_pdf_viewer` | PDF Viewer widget — render a PDF share link inline in the conversation |

Both widgets are compiled to **single-file HTML bundles** (all CSS and JS inlined) via `vite-plugin-singlefile`. The MCP servers load these files from `shared/ui/dist/` at runtime and serve them as MCP resources.

## Build

### Prerequisites

Node.js 18 or higher.

### With npm

```bash
cd shared/ui
npm install
npm run build
```

### With pnpm

```bash
cd shared/ui
pnpm install
pnpm build
```

### From the repo root

```bash
# npm
npm run build:ui

# pnpm
pnpm run build:ui
```

The built files land in `shared/ui/dist/` (gitignored). Both servers load them from this path at startup.

## Development

Run the widget in dev mode with hot reload (useful for UI development):

```bash
cd shared/ui
npm run dev      # or: pnpm dev
```

## Tech Stack

- [Vue 3](https://vuejs.org/) — UI framework
- [TypeScript](https://www.typescriptlang.org/)
- [Vite](https://vitejs.dev/) + [vite-plugin-singlefile](https://github.com/richardtallent/vite-plugin-singlefile) — single-file bundle output
- [Arco Design Vue](https://arco.design/vue) — component library
- [`@modelcontextprotocol/ext-apps`](https://www.npmjs.com/package/@modelcontextprotocol/ext-apps) — MCP App runtime

## How the Servers Use It

**Python server** (`python/foxit-pdf-api-mcp-server`):
Loads `dist/index.html` and `dist/viewer.html` from `shared/ui/dist/` via `resources.py` and registers them as MCP resources. The `show_pdf_tools` and `show_pdf_viewer` tools return these resources to the agent.

**TypeScript server** (`typescript/foxit-pdf-api-mcp-server`):
Same pattern — `src/tools/pdf-widget.ts` walks up the directory tree at runtime to locate `shared/ui/dist/` and loads both HTML files.

> **Note:** The `shared/ui/dist/` directory must be built before starting either server if you want the widget tools to work. If the dist files are missing, the `show_pdf_tools` and `show_pdf_viewer` tools will return an error.

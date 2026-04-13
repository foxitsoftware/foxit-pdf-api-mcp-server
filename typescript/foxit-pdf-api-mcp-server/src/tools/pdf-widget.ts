import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { z } from "zod";

import type { FoxitPDFClient } from "../client";

// ---------------------------------------------------------------------------
// Locate shared/ui/dist at runtime — works in both tsx dev and compiled dist/
// ---------------------------------------------------------------------------

function findSharedUiDist(): string {
  let dir = path.dirname(fileURLToPath(import.meta.url));
  while (dir !== path.dirname(dir)) {
    const candidate = path.join(dir, "shared", "ui", "dist");
    if (fs.existsSync(candidate)) return candidate;
    dir = path.dirname(dir);
  }
  throw new Error(
    "shared/ui/dist not found — run 'pnpm build:ui' from the repo root first"
  );
}

function loadWidgetHtml(name: string): string {
  const distDir = findSharedUiDist();
  const filePath = path.join(distDir, `${name}.html`);
  if (!fs.existsSync(filePath)) {
    throw new Error(
      `Widget HTML not found at ${filePath} — run 'pnpm build:ui' first`
    );
  }
  return fs.readFileSync(filePath, "utf-8");
}

export const PDF_TOOLS_WIDGET_URI = "ui://widget/foxit-pdf-tools.html";
export const PDF_VIEWER_WIDGET_URI = "ui://widget/foxit-pdf-viewer.html";

// Loaded once at startup
export const pdfToolsHtml = () => loadWidgetHtml("index");
export const pdfViewerHtml = () => loadWidgetHtml("viewer");

// ---------------------------------------------------------------------------
// show_pdf_tools
// ---------------------------------------------------------------------------

export const showPdfToolsTool = (_client: FoxitPDFClient) => ({
  name: "show_pdf_tools",
  description: `⚠️ This is the ENTRY POINT for all file operations. You MUST call this tool first
before performing any file processing operations to allow users to upload documents.

Display the PDF tools widget for uploading and managing PDF documents.

Features:
- Upload PDF documents (drag-and-drop or browse)
- View uploaded documents list
- Real-time status updates

Usage scenarios:
- User mentions "upload PDF", "process document", "convert file", etc.
- Before executing any operation that requires a document_id

Supported file formats:
- PDF documents
- Microsoft Office documents (Word, Excel, PowerPoint)
- Images (PNG, JPEG, TIFF, BMP, GIF)
- Text files
- HTML files

Maximum file size: 100MB`,
  parameters: z.object({
    user_intent: z
      .string()
      .describe(
        "The user's intent or reason for using the PDF tools (e.g. 'convert to Word')"
      ),
    message: z
      .string()
      .optional()
      .describe("Optional custom message to display at the top of the widget"),
  }),
  execute: async (args: { user_intent: string; message?: string }) => {
    const displayMessage =
      args.message ?? "Please upload a document to get started.";
    return JSON.stringify({
      success: true,
      widget: {
        uri: PDF_TOOLS_WIDGET_URI,
        domain: "pdf-tools",
        accessible: true,
      },
      message: `Displaying PDF tools widget. ${displayMessage}`,
      instructions:
        "Use the widget above to upload files. Document IDs will be returned for use in subsequent tools.",
      ...(args.message ? { resultData: { request: { message: args.message } } } : {}),
    });
  },
});

// ---------------------------------------------------------------------------
// show_pdf_viewer
// ---------------------------------------------------------------------------

export const showPdfViewerTool = (client: FoxitPDFClient) => ({
  name: "show_pdf_viewer",
  description: `Display the PDF viewer widget for viewing a specific PDF document.
When you have a document_id after a conversion or upload, use this tool to let the user view the PDF.

Args:
  document_id: The document ID of the PDF to view.`,
  parameters: z.object({
    document_id: z
      .string()
      .describe("Document ID of the PDF document to view"),
  }),
  execute: async (args: { document_id: string }) => {
    let shareUrl: string | null = null;
    try {
      const result = await client.createShareLink(args.document_id);
      shareUrl = result.shareUrl ?? null;
    } catch {
      // viewer still works without a share URL (will receive it from tool result)
    }

    return JSON.stringify({
      success: true,
      widget: {
        uri: PDF_VIEWER_WIDGET_URI,
        domain: "pdf-viewer",
        accessible: true,
      },
      shareUrl,
      message: `Displaying PDF document with document ID: ${args.document_id}`,
      instructions: "Use the widget above to view the PDF document.",
    });
  },
});

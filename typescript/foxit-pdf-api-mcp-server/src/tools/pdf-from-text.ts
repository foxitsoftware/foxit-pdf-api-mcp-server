import { z } from "zod";

import type { FoxitPDFClient } from "../client";

export const pdfFromTextTool = (client: FoxitPDFClient) => ({
  name: "pdf_from_text",
  description: `Convert a plain text file to PDF format.

Features:
- Auto-detects text encoding (UTF-8, ASCII, etc.)
- Preserves line breaks and spacing
- Handles long lines
- Tab character expansion
- Page break on form feed character (\\f)

Supported features:
- Unicode support
- Right-to-left text support
- Configurable font and layout (via API config)

Limitations:
- Maximum file size: 100MB
- No rich text formatting
- No images or embedded content

Common use cases:
- Convert log files to PDF
- Create PDFs from plain text documents
- Archive text-based content

Workflow:
1. Upload text file using upload_document tool
2. Call this tool with the documentId
3. Use get_task_result to poll for completion and retrieve the download link`,
  parameters: z.object({
    documentId: z.string().describe("Document ID of the uploaded text file"),
  }),
  execute: async (args: { documentId: string }) => {
    try {
      const { taskId } = await client.pdfFromText(args.documentId);
      return JSON.stringify({
        success: true,
        taskId,
        message: "Text to PDF conversion submitted. Use get_task_result to check status and retrieve the download link.",
      });
    } catch (error) {
      return JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : String(error),
        errorType: (error as { code?: string }).code ?? "CONVERSION_FAILED",
        taskId: (error as { taskId?: string }).taskId,
      });
    }
  },
});

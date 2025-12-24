import { z } from "zod";

import type { FoxitPDFClient } from "../client";
import { executeAndWait } from "../utils/task-poller";

export const pdfFromHtmlTool = (client: FoxitPDFClient) => ({
  name: "pdf_from_html",
  description: `Convert HTML content to PDF format.

Features:
- Supports embedded CSS and JavaScript
- Preserves images and web fonts
- Configurable page dimensions
- Page orientation control
- Content scaling options

Configuration:
- dimension: Page size (default: A4 - 595x842 points)
- rotation: Page rotation (NONE, 90, 180, 270)
- pageMode: SINGLE_PAGE or MULTIPLE_PAGE
- scalingMode: SCALE or NO_SCALE

Common use cases:
- Web page archiving
- Report generation from HTML templates
- Creating printable documents

Maximum file size: 100MB

Workflow:
1. Upload HTML file using upload_document tool
2. Call this tool with documentId and optional config
3. Download result using download_document tool`,
  parameters: z.object({
    documentId: z.string().describe("Document ID of the uploaded HTML file"),
    config: z
      .object({
        dimension: z
          .object({
            width: z.number().describe("Page width in points (1 point = 1/72 inch)"),
            height: z.number().describe("Page height in points"),
          })
          .optional()
          .describe("Page dimensions (default: A4 - 595x842)"),
        rotation: z
          .enum(["NONE", "90", "180", "270"])
          .optional()
          .describe("Page rotation (default: NONE)"),
        pageMode: z
          .enum(["SINGLE_PAGE", "MULTIPLE_PAGE"])
          .optional()
          .describe("Content layout mode (default: MULTIPLE_PAGE)"),
        scalingMode: z
          .enum(["SCALE", "NO_SCALE"])
          .optional()
          .describe("Content scaling (default: SCALE)"),
      })
      .optional()
      .describe("PDF configuration options"),
  }),
  execute: async (args: {
    documentId: string;
    config?: {
      dimension?: { width: number; height: number };
      rotation?: string;
      pageMode?: string;
      scalingMode?: string;
    };
  }) => {
    try {
      const result = await executeAndWait(client, () =>
        client.pdfFromHtml(args.documentId, args.config)
      );

      return JSON.stringify({
        success: true,
        taskId: result.taskId,
        resultDocumentId: result.resultDocumentId,
        message: `HTML converted to PDF successfully. Download using documentId: ${result.resultDocumentId}`,
      });
    } catch (error) {
      return JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : String(error),
        code: (error as { code?: string }).code ?? "CONVERSION_FAILED",
        taskId: (error as { taskId?: string }).taskId,
      });
    }
  },
});

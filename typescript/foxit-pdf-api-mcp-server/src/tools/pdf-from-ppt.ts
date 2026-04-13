import { z } from "zod";

import type { FoxitPDFClient } from "../client";

export const pdfFromPptTool = (client: FoxitPDFClient) => ({
  name: "pdf_from_ppt",
  description: `Convert a Microsoft PowerPoint presentation to PDF format.

Supported formats: .ppt, .pptx, .pps, .ppsx

Features:
- Preserves all slide content and layouts
- Maintains master slides and themes
- Keeps SmartArt, shapes, and charts
- Converts animations to static images

Maximum file size: 100MB

Workflow:
1. Upload PowerPoint file using upload_document tool
2. Call this tool with the documentId
3. Use get_task_result to poll for completion and retrieve the download link`,
  parameters: z.object({
    documentId: z.string().describe("Document ID of the uploaded PowerPoint file"),
  }),
  execute: async (args: { documentId: string }) => {
    try {
      const { taskId } = await client.pdfFromPpt(args.documentId);
      return JSON.stringify({
        success: true,
        taskId,
        message: "PowerPoint to PDF conversion submitted. Use get_task_result to check status and retrieve the download link.",
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

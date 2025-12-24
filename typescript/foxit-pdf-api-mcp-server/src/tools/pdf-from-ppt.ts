import { z } from "zod";

import type { FoxitPDFClient } from "../client";
import { executeAndWait } from "../utils/task-poller";

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
3. Download result using download_document tool`,
  parameters: z.object({
    documentId: z.string().describe("Document ID of the uploaded PowerPoint file"),
  }),
  execute: async (args: { documentId: string }) => {
    try {
      const result = await executeAndWait(client, () =>
        client.pdfFromPpt(args.documentId)
      );

      return JSON.stringify({
        success: true,
        taskId: result.taskId,
        resultDocumentId: result.resultDocumentId,
        message: `PowerPoint converted to PDF successfully. Download using documentId: ${result.resultDocumentId}`,
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

import { z } from "zod";

import type { FoxitPDFClient } from "../client";
import { executeAndWait } from "../utils/task-poller";

/**
 * Convert Word to PDF tool
 */
export const pdfFromWordTool = (client: FoxitPDFClient) => ({
  name: "pdf_from_word",
  description: `Convert a Microsoft Word document to PDF format.

Supported formats: .doc, .docx, .rtf, .dot, .dotx, .docm, .dotm, .wpd

Features:
- Preserves text formatting and styles
- Maintains tables and images
- Keeps headers and footers
- Preserves page breaks and sections

Maximum file size: 100MB

Workflow:
1. Upload Word document using upload_document tool
2. Call this tool with the documentId
3. Wait for conversion to complete
4. Download result using download_document tool with the returned documentId`,
  parameters: z.object({
    documentId: z
      .string()
      .describe("Document ID of the uploaded Word file"),
  }),
  execute: async (args: { documentId: string }) => {
    try {
      const result = await executeAndWait(client, () =>
        client.pdfFromWord(args.documentId)
      );

      return JSON.stringify({
        success: true,
        taskId: result.taskId,
        resultDocumentId: result.resultDocumentId,
        message: `Word document converted to PDF successfully. Download using documentId: ${result.resultDocumentId}`,
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

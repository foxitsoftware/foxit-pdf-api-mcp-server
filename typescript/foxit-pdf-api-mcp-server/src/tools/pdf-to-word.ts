import { z } from "zod";

import type { FoxitPDFClient } from "../client";

/**
 * Convert PDF to Word tool
 */
export const pdfToWordTool = (client: FoxitPDFClient) => ({
  name: "pdf_to_word",
  description: `Convert a PDF document to Microsoft Word format (.docx).

The conversion maintains:
- Text content and formatting
- Tables and structure
- Images and graphics
- Page layout (as closely as possible)

Note: Complex layouts or scanned PDFs may not convert perfectly.
If the PDF is password-protected, provide the password parameter.

Workflow:
1. Upload PDF using upload_document tool
2. Call this tool with the documentId
3. Wait for conversion to complete
4. Download result using download_document tool with the returned documentId`,
  parameters: z.object({
    documentId: z
      .string()
      .describe("Document ID of the uploaded PDF file"),
    password: z
      .string()
      .optional()
      .describe("Password if the PDF is password-protected"),
  }),
  execute: async (args: { documentId: string; password?: string }) => {
    try {
      const { taskId } = await client.pdfToWord(args.documentId, args.password);
      return JSON.stringify({
        success: true,
        taskId,
        message: "PDF to Word conversion submitted. Use get_task_result to check status and retrieve the download link.",
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

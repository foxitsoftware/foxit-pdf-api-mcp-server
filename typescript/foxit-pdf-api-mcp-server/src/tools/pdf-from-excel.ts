import { z } from "zod";

import type { FoxitPDFClient } from "../client";

export const pdfFromExcelTool = (client: FoxitPDFClient) => ({
  name: "pdf_from_excel",
  description: `Convert a Microsoft Excel spreadsheet to PDF format.

Supported formats: .xls, .xlsx, .xlt, .xltx, .xlsm, .xlsb, .xltm, .csv

Features:
- Preserves cell formatting and formulas
- Maintains charts and images
- Keeps multiple sheets
- Preserves print layout

Maximum file size: 100MB

Workflow:
1. Upload Excel document using upload_document tool
2. Call this tool with the documentId
3. Use get_task_result to poll for completion and retrieve the download link`,
  parameters: z.object({
    documentId: z.string().describe("Document ID of the uploaded Excel file"),
  }),
  execute: async (args: { documentId: string }) => {
    try {
      const { taskId } = await client.pdfFromExcel(args.documentId);
      return JSON.stringify({
        success: true,
        taskId,
        message: "Excel to PDF conversion submitted. Use get_task_result to check status and retrieve the download link.",
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

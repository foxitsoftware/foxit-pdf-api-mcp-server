import { z } from "zod";

import type { FoxitPDFClient } from "../client";
import { executeAndWait } from "../utils/task-poller";

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
3. Download result using download_document tool`,
  parameters: z.object({
    documentId: z.string().describe("Document ID of the uploaded Excel file"),
  }),
  execute: async (args: { documentId: string }) => {
    try {
      const result = await executeAndWait(client, () =>
        client.pdfFromExcel(args.documentId)
      );

      return JSON.stringify({
        success: true,
        taskId: result.taskId,
        resultDocumentId: result.resultDocumentId,
        message: `Excel converted to PDF successfully. Download using documentId: ${result.resultDocumentId}`,
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

import { z } from "zod";

import type { FoxitPDFClient } from "../client";
import { executeAndWait } from "../utils/task-poller";

export const pdfToExcelTool = (client: FoxitPDFClient) => ({
  name: "pdf_to_excel",
  description: `Convert PDF tables to Microsoft Excel spreadsheet format (.xlsx).

Features:
- Extracts tables from PDF
- Preserves cell structure
- Maintains data relationships
- Multiple sheets for multi-page PDFs

Best for:
- PDFs with tabular data
- Financial reports
- Data sheets

Note: Works best with PDFs that have clear table structures.
If the PDF is password-protected, provide the password parameter.

Workflow:
1. Upload PDF using upload_document tool
2. Call this tool with the documentId
3. Download Excel result using download_document tool`,
  parameters: z.object({
    documentId: z.string().describe("Document ID of the uploaded PDF file"),
    password: z.string().optional().describe("Password if PDF is password-protected"),
  }),
  execute: async (args: { documentId: string; password?: string }) => {
    try {
      const result = await executeAndWait(client, () =>
        client.pdfToExcel(args.documentId, args.password)
      );

      return JSON.stringify({
        success: true,
        taskId: result.taskId,
        resultDocumentId: result.resultDocumentId,
        message: `PDF converted to Excel successfully. Download using documentId: ${result.resultDocumentId}`,
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

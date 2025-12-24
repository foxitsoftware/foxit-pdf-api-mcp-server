import { z } from "zod";

import type { FoxitPDFClient } from "../client";
import { executeAndWait } from "../utils/task-poller";

/**
 * Merge PDFs tool
 */
export const pdfMergeTool = (client: FoxitPDFClient) => ({
  name: "pdf_merge",
  description: `Combine multiple PDF documents into a single PDF file.

Features:
- Merge PDFs in specified order
- Maintain bookmarks (optional)
- Preserve document properties
- Handle password-protected PDFs

Use cases:
- Combine multiple reports into one
- Merge chapters of a document
- Consolidate related PDFs

Workflow:
1. Upload all PDF files using upload_document tool
2. Collect all documentIds
3. Call this tool with the array of documents
4. Download merged result using download_document tool`,
  parameters: z.object({
    documents: z
      .array(
        z.object({
          documentId: z.string().describe("Document ID of a PDF to merge"),
          password: z
            .string()
            .optional()
            .describe("Password if this PDF is password-protected"),
        })
      )
      .min(2)
      .describe("Array of PDF documents to merge (minimum 2 documents)"),
  }),
  execute: async (args: {
    documents: Array<{ documentId: string; password?: string }>;
  }) => {
    try {
      const result = await executeAndWait(client, () =>
        client.pdfMerge(args.documents)
      );

      return JSON.stringify({
        success: true,
        taskId: result.taskId,
        resultDocumentId: result.resultDocumentId,
        documentsCount: args.documents.length,
        message: `${args.documents.length} PDFs merged successfully. Download using documentId: ${result.resultDocumentId}`,
      });
    } catch (error) {
      return JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : String(error),
        code: (error as { code?: string }).code ?? "MERGE_FAILED",
        taskId: (error as { taskId?: string }).taskId,
      });
    }
  },
});

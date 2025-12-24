import { z } from "zod";

import type { FoxitPDFClient } from "../client";
import { executeAndWait } from "../utils/task-poller";

/**
 * Get PDF properties tool
 */
export const getPdfPropertiesTool = (client: FoxitPDFClient) => ({
  name: "get_pdf_properties",
  description: `Extract comprehensive properties and metadata from a PDF document.

IMPORTANT: This tool returns JSON data directly, not a file documentId.

Information returned:
- Page count and dimensions
- PDF version and file size
- Encryption and security status
- Digital signatures
- Embedded files and fonts
- Document metadata (title, author, creation date, etc.)
- User permissions analysis
- Page-level information (rotation, dimensions, scan detection)

Configuration options:
- includeExtendedInfo: Get detailed metadata (fonts, signatures, encryption details)
- includePageInfo: Include per-page information (dimensions, rotation, scan detection)

Use cases:
- Verify PDF structure before processing
- Check if PDF is password-protected
- Analyze PDF compatibility
- Extract document metadata
- Detect scanned pages

Workflow:
1. Upload PDF using upload_document tool
2. Call this tool with documentId
3. Receive JSON data with all properties
4. No download needed - data is returned directly`,
  parameters: z.object({
    documentId: z
      .string()
      .describe("Document ID of the PDF to analyze"),
    includeExtendedInfo: z
      .boolean()
      .optional()
      .describe(
        "Include detailed metadata (fonts, signatures, encryption, etc.). Default: true"
      ),
    includePageInfo: z
      .boolean()
      .optional()
      .describe(
        "Include per-page information (dimensions, rotation, scan detection). Default: true"
      ),
  }),
  execute: async (args: {
    documentId: string;
    includeExtendedInfo?: boolean;
    includePageInfo?: boolean;
  }) => {
    try {
      const result = await executeAndWait(client, () =>
        client.getPdfProperties(args.documentId, {
          includeExtendedInfo: args.includeExtendedInfo ?? true,
          includePageInfo: args.includePageInfo ?? true,
        })
      );

      // This operation returns data, not a file
      return JSON.stringify({
        success: true,
        taskId: result.taskId,
        properties: result.resultData,
        message: "PDF properties extracted successfully",
      });
    } catch (error) {
      return JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : String(error),
        code: (error as { code?: string }).code ?? "ANALYSIS_FAILED",
        taskId: (error as { taskId?: string }).taskId,
      });
    }
  },
});

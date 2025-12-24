import { z } from "zod";

import type { FoxitPDFClient } from "../client";
import { executeAndWait } from "../utils/task-poller";

/**
 * Protect PDF with password tool
 */
export const pdfProtectTool = (client: FoxitPDFClient) => ({
  name: "pdf_protect",
  description: `Apply password protection to a PDF document.

Protection types:
- User password: Required to open the document
- Owner password: Required to change permissions
- Permissions: Control what users can do (print, copy, modify, etc.)

Common permissions:
- "PRINT" - Allow printing
- "MODIFY_CONTENT" - Allow content modification
- "COPY_CONTENT" - Allow text/image copying
- "FILL_FORMS" - Allow form filling
- "MODIFY_ANNOTATIONS" - Allow adding comments

Security levels:
- User password only: Anyone with password can open and use normally
- Owner password only: Open without password but with restrictions
- Both passwords: User password to open, owner password to change permissions

Workflow:
1. Upload PDF using upload_document tool
2. Call this tool with documentId and security settings
3. Download protected PDF using download_document tool`,
  parameters: z.object({
    documentId: z
      .string()
      .describe("Document ID of the PDF to protect"),
    userPassword: z
      .string()
      .optional()
      .describe("Password required to open the document"),
    ownerPassword: z
      .string()
      .optional()
      .describe("Password required to change permissions"),
    permissions: z
      .array(z.string())
      .optional()
      .describe(
        "Array of permissions to grant (e.g., ['PRINT', 'COPY_CONTENT'])"
      ),
  }),
  execute: async (args: {
    documentId: string;
    userPassword?: string;
    ownerPassword?: string;
    permissions?: string[];
  }) => {
    try {
      const result = await executeAndWait(client, () =>
        client.pdfProtect(args.documentId, {
          userPassword: args.userPassword,
          ownerPassword: args.ownerPassword,
          permissions: args.permissions,
        })
      );

      return JSON.stringify({
        success: true,
        taskId: result.taskId,
        resultDocumentId: result.resultDocumentId,
        protection: {
          hasUserPassword: !!args.userPassword,
          hasOwnerPassword: !!args.ownerPassword,
          permissions: args.permissions ?? [],
        },
        message: `PDF protected successfully. Download using documentId: ${result.resultDocumentId}`,
      });
    } catch (error) {
      return JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : String(error),
        code: (error as { code?: string }).code ?? "PROTECT_FAILED",
        taskId: (error as { taskId?: string }).taskId,
      });
    }
  },
});

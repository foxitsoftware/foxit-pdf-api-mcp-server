import { z } from "zod";

import type { FoxitPDFClient } from "../client";

/**
 * Redact sensitive content from a PDF tool
 */
export const pdfRedactTool = (client: FoxitPDFClient) => ({
  name: "pdf_redact",
  description: `Permanently redact sensitive content from a PDF document.

⚠️ CRITICAL PREREQUISITE: You MUST call show_pdf_tools first to display the upload widget.
The documentId parameter comes from the upload response in the widget.

Supports two modes (can be combined):
- Text-based: find and permanently remove specific words or phrases
- Form-field: redact the content of form fields

⚠️ When applyImmediately is true (default), redactions are PERMANENT and IRREVERSIBLE.
Set applyImmediately=false to preview marks without removing the underlying content.

Maximum file size: 100MB

This operation runs asynchronously. The tool returns a taskId immediately.
Use get_task_result to poll for completion and retrieve the download link.`,
  parameters: z.object({
    documentId: z.string().describe("Document ID of the PDF to redact"),
    texts: z
      .array(z.string())
      .optional()
      .describe(
        'List of words or phrases to find and redact. Example: ["John Smith", "SSN", "jane.doe@example.com"]'
      ),
    overlayText: z
      .string()
      .optional()
      .describe(
        'Optional label shown inside every redaction mark, e.g. "[REDACTED]". Omit for a solid filled box.'
      ),
    pageRange: z
      .string()
      .optional()
      .describe('Restrict text search to specific pages, e.g. "1-3", "all" (default: all pages)'),
    caseSensitive: z
      .boolean()
      .optional()
      .describe("Match exact case when searching text (default: false)"),
    wholeWordsOnly: z
      .boolean()
      .optional()
      .describe("Match whole words only when searching text (default: false)"),
    redactFormFields: z
      .boolean()
      .optional()
      .describe("When true, redact form field content in the document (default: false)"),
    formFieldTypes: z
      .array(z.string())
      .optional()
      .describe(
        "Limit form field redaction to specific types. Omit to redact all types. Valid values: PUSH_BUTTON, CHECK_BOX, RADIO_BUTTON, COMBO_BOX, LIST_BOX, TEXT_FIELD, SIGNATURE"
      ),
    applyImmediately: z
      .boolean()
      .optional()
      .describe(
        "true (default) = permanently apply redactions. false = place marks only without removing content."
      ),
  }),
  execute: async (args: {
    documentId: string;
    texts?: string[];
    overlayText?: string;
    pageRange?: string;
    caseSensitive?: boolean;
    wholeWordsOnly?: boolean;
    redactFormFields?: boolean;
    formFieldTypes?: string[];
    applyImmediately?: boolean;
  }) => {
    try {
      if (!args.texts?.length && !args.redactFormFields) {
        return JSON.stringify({
          success: false,
          error: "Provide at least one of: texts (list of words/phrases to redact) or redactFormFields=true.",
          errorType: "INVALID_PARAMS",
        });
      }

      const { taskId } = await client.pdfRedact(args.documentId, {
        texts: args.texts,
        overlayText: args.overlayText,
        pageRange: args.pageRange,
        caseSensitive: args.caseSensitive,
        wholeWordsOnly: args.wholeWordsOnly,
        redactFormFields: args.redactFormFields,
        formFieldTypes: args.formFieldTypes,
        applyImmediately: args.applyImmediately,
      });

      return JSON.stringify({
        success: true,
        taskId,
        message: "PDF redaction submitted. Use get_task_result to check status and retrieve the download link.",
      });
    } catch (error) {
      return JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : String(error),
        errorType: (error as { code?: string }).code ?? "REDACT_FAILED",
        taskId: (error as { taskId?: string }).taskId,
      });
    }
  },
});

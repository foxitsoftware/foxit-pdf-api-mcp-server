import { z } from "zod";

import type { FoxitPDFClient } from "../client";

// ============ PDF Manipulation Tools ============

export const pdfSplitTool = (client: FoxitPDFClient) => ({
  name: "pdf_split",
  description: `Split a PDF document into multiple files by fixed page count.
- The API requires pageCount (pages per output file).
- The output is a ZIP document containing the split PDFs.

Example:
- page_count=10 splits the PDF into files of 10 pages each (last file may have fewer pages).

Maximum file size: 100MB

This operation runs asynchronously. The tool returns a taskId immediately.
Use get_task_result to poll for completion and retrieve the download link.`,
  parameters: z.object({
    documentId: z.string().describe("Document ID of the PDF to split"),
    pageCount: z
      .number()
      .int()
      .min(1)
      .describe("Number of pages per output file (must be >= 1)"),
    password: z.string().optional().describe("Password if PDF is password-protected"),
  }),
  execute: async (args: { documentId: string; pageCount: number; password?: string }) => {
    try {
      const { taskId } = await client.pdfSplit(
        args.documentId,
        "BY_PAGE_COUNT",
        { pageCount: args.pageCount },
        args.password
      );
      return JSON.stringify({
        success: true,
        taskId,
        message: "PDF split submitted. Use get_task_result to check status and retrieve the download link.",
      });
    } catch (error) {
      return JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : String(error),
        errorType: (error as { code?: string }).code ?? "SPLIT_FAILED",
        taskId: (error as { taskId?: string }).taskId,
      });
    }
  },
});

// NOTE: TypeScript-only — Python has separate pdf_extract_pages and pdf_extract_text tools instead.
export const pdfExtractTool = (client: FoxitPDFClient) => ({
  name: "pdf_extract",
  description: `Extract text, images, or specific pages from a PDF.

NOTE: TypeScript-only tool. The Python server exposes this functionality through
two separate tools: pdf_extract_pages (for pages) and pdf_extract_text (for text).

Extract types:
- TEXT: Extract all text content
- IMAGES: Extract all images
- PAGES: Extract specific pages

This operation runs asynchronously. The tool returns a taskId immediately.
Use get_task_result to poll for completion and retrieve the download link.`,
  parameters: z.object({
    documentId: z.string().describe("Document ID of the PDF"),
    extractType: z
      .enum(["TEXT", "IMAGES", "PAGES"])
      .describe("Type of content to extract"),
    pageRanges: z
      .string()
      .optional()
      .describe('Page ranges to extract from (e.g., "1-3,5,7-9")'),
    password: z.string().optional().describe("Password if PDF is password-protected"),
  }),
  execute: async (args: {
    documentId: string;
    extractType: string;
    pageRanges?: string;
    password?: string;
  }) => {
    try {
      const { taskId } = await client.pdfExtract(
        args.documentId,
        args.extractType,
        { pageRanges: args.pageRanges },
        args.password
      );
      return JSON.stringify({
        success: true,
        taskId,
        extractType: args.extractType,
        message: "Content extraction submitted. Use get_task_result to check status and retrieve the download link.",
      });
    } catch (error) {
      return JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : String(error),
        errorType: (error as { code?: string }).code ?? "EXTRACT_FAILED",
        taskId: (error as { taskId?: string }).taskId,
      });
    }
  },
});

/**
 * pdf_extract_pages — mirrors Python's pdf_extract_pages tool.
 */
export const pdfExtractPagesTool = (client: FoxitPDFClient) => ({
  name: "pdf_extract_pages",
  description: `Extract selected pages into a new PDF document.

Features:
- Extract any pages or page ranges into a new PDF
- Preserves page content and formatting

Maximum file size: 100MB

This operation runs asynchronously. The tool returns a taskId immediately.
Use get_task_result to poll for completion and retrieve the download link.`,
  parameters: z.object({
    documentId: z.string().describe("Document ID of the PDF"),
    page_range: z
      .string()
      .describe(
        'Pages to extract. 1-based page numbers. Supports ranges like "1,3,5-10" and special values "all", "even", "odd".'
      ),
    password: z.string().optional().describe("Password if PDF is password-protected"),
  }),
  execute: async (args: { documentId: string; page_range: string; password?: string }) => {
    try {
      const { taskId } = await client.pdfExtract(
        args.documentId,
        "PAGES",
        { pageRanges: args.page_range },
        args.password
      );
      return JSON.stringify({
        success: true,
        taskId,
        message:
          "Page extraction submitted. Use get_task_result to check status and retrieve the download link.",
      });
    } catch (error) {
      return JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : String(error),
        errorType: (error as { code?: string }).code ?? "EXTRACT_FAILED",
        taskId: (error as { taskId?: string }).taskId,
      });
    }
  },
});

/**
 * pdf_extract_text — mirrors Python's pdf_extract_text tool.
 */
export const pdfExtractTextTool = (client: FoxitPDFClient) => ({
  name: "pdf_extract_text",
  description: `Extract plain text content from selected pages.
- Returns plain text and a generated .txt document.
- page_range controls which pages are processed (1-based) and also supports "all", "even", "odd".

This operation runs asynchronously. The tool returns a taskId immediately.
Use get_task_result to poll for completion and retrieve the result.
When complete, the result includes a download link for the .txt file.`,
  parameters: z.object({
    documentId: z.string().describe("Document ID of the PDF"),
    page_range: z
      .string()
      .describe(
        'Pages to extract text from. 1-based. Supports "1,3,5-10", "all", "even", "odd".'
      ),
    password: z.string().optional().describe("Password if PDF is password-protected"),
  }),
  execute: async (args: { documentId: string; page_range: string; password?: string }) => {
    try {
      const { taskId } = await client.pdfExtract(
        args.documentId,
        "TEXT",
        { pageRanges: args.page_range },
        args.password
      );
      return JSON.stringify({
        success: true,
        taskId,
        message:
          "Text extraction submitted. Use get_task_result to check status and retrieve the extracted text.",
      });
    } catch (error) {
      return JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : String(error),
        errorType: (error as { code?: string }).code ?? "EXTRACT_FAILED",
        taskId: (error as { taskId?: string }).taskId,
      });
    }
  },
});

export const pdfFlattenTool = (client: FoxitPDFClient) => ({
  name: "pdf_flatten",
  description: `Flatten a PDF document (merge all layers and form fields).

Features:
- Converts form fields to static content
- Flattens annotations and markup
- Merges all layers
- Prevents further editing of forms

Use cases:
- Finalize forms before archiving
- Prevent form tampering
- Reduce file complexity

This operation runs asynchronously. The tool returns a taskId immediately.
Use get_task_result to poll for completion and retrieve the download link.`,
  parameters: z.object({
    documentId: z.string().describe("Document ID of the PDF to flatten"),
    password: z.string().optional().describe("Password if PDF is password-protected"),
  }),
  execute: async (args: { documentId: string; password?: string }) => {
    try {
      const { taskId } = await client.pdfFlatten(args.documentId, args.password);
      return JSON.stringify({
        success: true,
        taskId,
        message:
          "PDF flatten submitted. Use get_task_result to check status and retrieve the download link.",
      });
    } catch (error) {
      return JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : String(error),
        errorType: (error as { code?: string }).code ?? "FLATTEN_FAILED",
        taskId: (error as { taskId?: string }).taskId,
      });
    }
  },
});

export const pdfCompressTool = (client: FoxitPDFClient) => ({
  name: "pdf_compress",
  description: `Compress a PDF document to reduce file size.

Do not offer compression level options. Only one default compression level is currently supported.

Features:
- Attempts to reduce file size; compression ratio and quality impact vary by document
- Optimizes embedded resources (e.g., images) and removes redundant data where possible

Maximum file size: 100MB

This operation runs asynchronously. The tool returns a taskId immediately.
Use get_task_result to poll for completion and retrieve the download link.`,
  parameters: z.object({
    documentId: z.string().describe("Document ID of the PDF to compress"),
    password: z.string().optional().describe("Password if PDF is password-protected"),
  }),
  execute: async (args: { documentId: string; password?: string }) => {
    try {
      const { taskId } = await client.pdfCompress(args.documentId, undefined, args.password);
      return JSON.stringify({
        success: true,
        taskId,
        message:
          "PDF compression submitted. Use get_task_result to check status and retrieve the download link.",
      });
    } catch (error) {
      return JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : String(error),
        errorType: (error as { code?: string }).code ?? "COMPRESS_FAILED",
        taskId: (error as { taskId?: string }).taskId,
      });
    }
  },
});

export const pdfManipulateTool = (client: FoxitPDFClient) => ({
  name: "pdf_manipulate",
  description: `Apply a batch of page operations to a PDF (rotate, delete, or reorder pages).

Operations:
- ROTATE: Rotate a page (90, 180, or 270 degrees). pageIndex is 0-based.
- DELETE: Remove a page. pageIndex is 0-based.
- REORDER: Move a page to a different position. pageIndex and targetIndex are 0-based.

Example operations:
- Rotate page 1 by 90°: { type: "ROTATE", pageIndex: 0, rotation: 90 }
- Delete page 3: { type: "DELETE", pageIndex: 2 }
- Move page 5 to position 2: { type: "REORDER", pageIndex: 4, targetIndex: 1 }

This operation runs asynchronously. The tool returns a taskId immediately.
Use get_task_result to poll for completion and retrieve the download link.`,
  parameters: z.object({
    documentId: z.string().describe("Document ID of the PDF to manipulate"),
    operations: z
      .array(
        z.object({
          type: z.enum(["ROTATE", "DELETE", "REORDER"]).describe("Type of operation"),
          pageIndex: z.number().describe("Target page index (0-based)"),
          rotation: z.number().optional().describe("Rotation angle in degrees (for ROTATE)"),
          targetIndex: z.number().optional().describe("New position index (for REORDER)"),
        })
      )
      .describe("Array of page manipulation operations"),
    password: z.string().optional().describe("Password if PDF is password-protected"),
  }),
  execute: async (args: {
    documentId: string;
    operations: Array<{
      type: string;
      pageIndex: number;
      rotation?: number;
      targetIndex?: number;
    }>;
    password?: string;
  }) => {
    try {
      const { taskId } = await client.pdfManipulate(
        args.documentId,
        args.operations,
        args.password
      );
      return JSON.stringify({
        success: true,
        taskId,
        message: `PDF manipulation (${args.operations.length} operations) submitted. Use get_task_result to check status and retrieve the download link.`,
      });
    } catch (error) {
      return JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : String(error),
        errorType: (error as { code?: string }).code ?? "MANIPULATE_FAILED",
        taskId: (error as { taskId?: string }).taskId,
      });
    }
  },
});

/**
 * pdf_delete_pages — mirrors Python's pdf_delete_pages tool.
 * Convenience wrapper over pdf_manipulate for the DELETE operation.
 */
export const pdfDeletePagesTool = (client: FoxitPDFClient) => ({
  name: "pdf_delete_pages",
  description: `Delete specific pages from a PDF document.

Uses 1-based page numbers. Supports ranges like "1,3,5-10".

This operation runs asynchronously. The tool returns a taskId immediately.
Use get_task_result to poll for completion and retrieve the download link.`,
  parameters: z.object({
    documentId: z.string().describe("Document ID of the PDF"),
    page_range: z
      .string()
      .describe('Pages to delete. 1-based. Examples: "1,3,5-10", "2-4".'),
    password: z.string().optional().describe("Password if PDF is password-protected"),
  }),
  execute: async (args: { documentId: string; page_range: string; password?: string }) => {
    try {
      const pageNumbers = expandPageRange(args.page_range);
      // Delete from end first so earlier indices remain valid
      const operations = pageNumbers
        .sort((a, b) => b - a)
        .map((p) => ({ type: "DELETE" as const, pageIndex: p - 1 }));

      const { taskId } = await client.pdfManipulate(args.documentId, operations, args.password);
      return JSON.stringify({
        success: true,
        taskId,
        message:
          "Page deletion submitted. Use get_task_result to check status and retrieve the download link.",
      });
    } catch (error) {
      return JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : String(error),
        errorType: (error as { code?: string }).code ?? "MANIPULATE_FAILED",
        taskId: (error as { taskId?: string }).taskId,
      });
    }
  },
});

/**
 * pdf_rotate_pages — mirrors Python's pdf_rotate_pages tool.
 */
export const pdfRotatePagesTool = (client: FoxitPDFClient) => ({
  name: "pdf_rotate_pages",
  description: `Rotate specific pages in a PDF document.

Uses 1-based page numbers. Supports ranges like "1,3,5-10".
Rotation must be 90, 180, or 270 degrees.

This operation runs asynchronously. The tool returns a taskId immediately.
Use get_task_result to poll for completion and retrieve the download link.`,
  parameters: z.object({
    documentId: z.string().describe("Document ID of the PDF"),
    page_range: z
      .string()
      .describe('Pages to rotate. 1-based. Examples: "1,3,5-10", "2-4".'),
    rotation: z
      .number()
      .refine((v) => [90, 180, 270].includes(v), { message: "Rotation must be 90, 180, or 270" })
      .describe("Rotation angle in degrees (90, 180, or 270)"),
    password: z.string().optional().describe("Password if PDF is password-protected"),
  }),
  execute: async (args: {
    documentId: string;
    page_range: string;
    rotation: number;
    password?: string;
  }) => {
    try {
      const pageNumbers = expandPageRange(args.page_range);
      const operations = pageNumbers.map((p) => ({
        type: "ROTATE" as const,
        pageIndex: p - 1,
        rotation: args.rotation,
      }));

      const { taskId } = await client.pdfManipulate(args.documentId, operations, args.password);
      return JSON.stringify({
        success: true,
        taskId,
        message:
          "Page rotation submitted. Use get_task_result to check status and retrieve the download link.",
      });
    } catch (error) {
      return JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : String(error),
        errorType: (error as { code?: string }).code ?? "MANIPULATE_FAILED",
        taskId: (error as { taskId?: string }).taskId,
      });
    }
  },
});

/**
 * pdf_reorder_pages — mirrors Python's pdf_reorder_pages tool.
 */
export const pdfReorderPagesTool = (client: FoxitPDFClient) => ({
  name: "pdf_reorder_pages",
  description: `Reorder pages in a PDF document by providing the new page order.

Provide a list of 1-based page numbers in the desired order.
Example: new_order=[3,1,2] moves page 3 to position 1, then page 1 to position 2, etc.

This operation runs asynchronously. The tool returns a taskId immediately.
Use get_task_result to poll for completion and retrieve the download link.`,
  parameters: z.object({
    documentId: z.string().describe("Document ID of the PDF"),
    new_order: z
      .array(z.number().int().min(1))
      .describe("New page order as an array of 1-based page numbers (must include all pages)"),
    password: z.string().optional().describe("Password if PDF is password-protected"),
  }),
  execute: async (args: { documentId: string; new_order: number[]; password?: string }) => {
    try {
      const operations = args.new_order.map((pageNum, targetIdx) => ({
        type: "REORDER" as const,
        pageIndex: pageNum - 1,
        targetIndex: targetIdx,
      }));

      const { taskId } = await client.pdfManipulate(args.documentId, operations, args.password);
      return JSON.stringify({
        success: true,
        taskId,
        message:
          "Page reorder submitted. Use get_task_result to check status and retrieve the download link.",
      });
    } catch (error) {
      return JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : String(error),
        errorType: (error as { code?: string }).code ?? "MANIPULATE_FAILED",
        taskId: (error as { taskId?: string }).taskId,
      });
    }
  },
});

// ============ Security Tools ============

export const pdfRemovePasswordTool = (client: FoxitPDFClient) => ({
  name: "pdf_remove_password",
  description: `Remove password protection from a PDF document.

Requirements:
- You must provide the correct password (user or owner)
- Only works if you know the password

Use cases:
- Remove restrictions from your own PDFs
- Unlock PDFs for processing
- Prepare PDFs for archiving

Maximum file size: 100MB`,
  parameters: z.object({
    documentId: z.string().describe("Document ID of the password-protected PDF"),
    password: z.string().describe("The user or owner password for the PDF"),
  }),
  execute: async (args: { documentId: string; password: string }) => {
    try {
      const result = await client.pdfRemovePassword(args.documentId, args.password);
      return JSON.stringify({
        success: true,
        taskId: result.taskId,
        message: "Password removal submitted. Use get_task_result to check status.",
      });
    } catch (error) {
      return JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : String(error),
        errorType: (error as { code?: string }).code ?? "REMOVE_PASSWORD_FAILED",
        taskId: (error as { taskId?: string }).taskId,
      });
    }
  },
});

// ============ Enhancement Tools ============

// NOTE: TypeScript-only — Python has this tool commented out (planned, not yet enabled).
export const pdfWatermarkTool = (client: FoxitPDFClient) => ({
  name: "pdf_watermark",
  description: `Add text or image watermark to PDF pages.

NOTE: TypeScript-only tool. This tool is planned but not yet enabled in the Python server.

Watermark types:
- TEXT: Text watermark (default)
- IMAGE: Image watermark (provide image documentId as content)

Configuration:
- content: Watermark text or image documentId
- position: Placement (CENTER, TOP_LEFT, TOP_RIGHT, BOTTOM_LEFT, BOTTOM_RIGHT)
- opacity: Transparency (0.0-1.0, default: 0.5)
- rotation: Rotation angle in degrees
- fontSize: Text size in points (for TEXT type)
- color: Text color in hex (e.g., "#FF0000")
- pageRanges: Specific pages (e.g., "1-3,5", default: all pages)

This operation runs asynchronously. The tool returns a taskId immediately.
Use get_task_result to poll for completion and retrieve the download link.`,
  parameters: z.object({
    documentId: z.string().describe("Document ID of the PDF"),
    content: z.string().describe("Watermark text or image documentId"),
    type: z
      .enum(["TEXT", "IMAGE"])
      .optional()
      .describe("Watermark type (default: TEXT)"),
    position: z
      .enum(["CENTER", "TOP_LEFT", "TOP_RIGHT", "BOTTOM_LEFT", "BOTTOM_RIGHT"])
      .optional()
      .describe("Watermark position (default: CENTER)"),
    opacity: z
      .number()
      .min(0)
      .max(1)
      .optional()
      .describe("Opacity 0.0-1.0 (default: 0.5)"),
    rotation: z.number().optional().describe("Rotation angle in degrees"),
    fontSize: z.number().optional().describe("Font size in points (for TEXT)"),
    color: z.string().optional().describe('Text color in hex (e.g., "#FF0000")'),
    pageRanges: z
      .string()
      .optional()
      .describe('Pages to watermark (e.g., "1-3,5", default: all)'),
    password: z.string().optional().describe("Password if PDF is password-protected"),
  }),
  execute: async (args: {
    documentId: string;
    content: string;
    type?: string;
    position?: string;
    opacity?: number;
    rotation?: number;
    fontSize?: number;
    color?: string;
    pageRanges?: string;
    password?: string;
  }) => {
    try {
      const { taskId } = await client.pdfWatermark(
        args.documentId,
        {
          content: args.content,
          type: args.type,
          position: args.position,
          opacity: args.opacity,
          rotation: args.rotation,
          fontSize: args.fontSize,
          color: args.color,
          pageRanges: args.pageRanges,
        },
        args.password
      );
      return JSON.stringify({
        success: true,
        taskId,
        message:
          "Watermark submitted. Use get_task_result to check status and retrieve the download link.",
      });
    } catch (error) {
      return JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : String(error),
        errorType: (error as { code?: string }).code ?? "WATERMARK_FAILED",
        taskId: (error as { taskId?: string }).taskId,
      });
    }
  },
});

export const pdfLinearizeTool = (client: FoxitPDFClient) => ({
  name: "pdf_linearize",
  description: `Optimize PDF for fast web viewing (Fast Web View / linearization).

Linearization reorganizes the PDF so the first page renders before the full file downloads.

Use cases:
- PDFs for web hosting
- Online document viewers
- Large documents for distribution

This operation runs asynchronously. The tool returns a taskId immediately.
Use get_task_result to poll for completion and retrieve the download link.`,
  parameters: z.object({
    documentId: z.string().describe("Document ID of the PDF to linearize"),
    password: z.string().optional().describe("Password if PDF is password-protected"),
  }),
  execute: async (args: { documentId: string; password?: string }) => {
    try {
      const { taskId } = await client.pdfLinearize(args.documentId);
      return JSON.stringify({
        success: true,
        taskId,
        message:
          "PDF linearization submitted. Use get_task_result to check status and retrieve the download link.",
      });
    } catch (error) {
      return JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : String(error),
        errorType: (error as { code?: string }).code ?? "LINEARIZE_FAILED",
        taskId: (error as { taskId?: string }).taskId,
      });
    }
  },
});

// ============ Helper ============

/**
 * Expand a page range string (e.g., "1,3,5-10") into an array of 1-based page numbers.
 */
function expandPageRange(range: string): number[] {
  const pages = new Set<number>();
  for (const part of range.split(",")) {
    const dashMatch = part.trim().match(/^(\d+)-(\d+)$/);
    if (dashMatch) {
      const start = parseInt(dashMatch[1], 10);
      const end = parseInt(dashMatch[2], 10);
      for (let i = start; i <= end; i++) pages.add(i);
    } else {
      const num = parseInt(part.trim(), 10);
      if (!isNaN(num)) pages.add(num);
    }
  }
  return Array.from(pages);
}

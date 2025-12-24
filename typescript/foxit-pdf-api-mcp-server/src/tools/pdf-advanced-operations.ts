import { z } from "zod";

import type { FoxitPDFClient } from "../client";
import { executeAndWait } from "../utils/task-poller";

// ============ PDF Manipulation Tools ============

export const pdfSplitTool = (client: FoxitPDFClient) => ({
  name: "pdf_split",
  description: `Split a PDF document into multiple files.

Split strategies:
- BY_PAGE_COUNT: Split into chunks of N pages each
- BY_PAGE_RANGES: Split by specific page ranges
- EVERY_PAGE: Create one PDF per page

Configuration:
- pageCount: Number of pages per chunk (for BY_PAGE_COUNT)
- pageRanges: Array of ranges like ["1-3", "4-10"] (for BY_PAGE_RANGES)

Workflow:
1. Upload PDF using upload_document tool
2. Call this tool with split strategy
3. Download result ZIP containing all split PDFs`,
  parameters: z.object({
    documentId: z.string().describe("Document ID of the PDF to split"),
    splitStrategy: z
      .enum(["BY_PAGE_COUNT", "BY_PAGE_RANGES", "EVERY_PAGE"])
      .describe("Strategy for splitting the PDF"),
    pageCount: z
      .number()
      .optional()
      .describe("Pages per chunk (required for BY_PAGE_COUNT)"),
    pageRanges: z
      .array(z.string())
      .optional()
      .describe('Page ranges (required for BY_PAGE_RANGES, e.g., ["1-3", "4-10"])'),
    password: z.string().optional().describe("Password if PDF is password-protected"),
  }),
  execute: async (args: {
    documentId: string;
    splitStrategy: string;
    pageCount?: number;
    pageRanges?: string[];
    password?: string;
  }) => {
    try {
      const result = await executeAndWait(client, () =>
        client.pdfSplit(
          args.documentId,
          args.splitStrategy,
          { pageCount: args.pageCount, pageRanges: args.pageRanges },
          args.password
        )
      );

      return JSON.stringify({
        success: true,
        taskId: result.taskId,
        resultDocumentId: result.resultDocumentId,
        strategy: args.splitStrategy,
        message: `PDF split successfully. Download ZIP using documentId: ${result.resultDocumentId}`,
      });
    } catch (error) {
      return JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : String(error),
        code: (error as { code?: string }).code ?? "SPLIT_FAILED",
        taskId: (error as { taskId?: string }).taskId,
      });
    }
  },
});

export const pdfExtractTool = (client: FoxitPDFClient) => ({
  name: "pdf_extract",
  description: `Extract text, images, or specific pages from a PDF.

Extract types:
- TEXT: Extract all text content
- IMAGES: Extract all images
- PAGES: Extract specific pages

Configuration:
- pageRanges: Specific pages to extract (e.g., "1-3,5,7-9")

Workflow:
1. Upload PDF using upload_document tool
2. Call this tool with extract type and ranges
3. Download extracted content using download_document tool`,
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
      const result = await executeAndWait(client, () =>
        client.pdfExtract(
          args.documentId,
          args.extractType,
          { pageRanges: args.pageRanges },
          args.password
        )
      );

      return JSON.stringify({
        success: true,
        taskId: result.taskId,
        resultDocumentId: result.resultDocumentId,
        extractType: args.extractType,
        message: `Content extracted successfully. Download using documentId: ${result.resultDocumentId}`,
      });
    } catch (error) {
      return JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : String(error),
        code: (error as { code?: string }).code ?? "EXTRACT_FAILED",
        taskId: (error as { taskId?: string }).taskId,
      });
    }
  },
});

export const pdfFlattenTool = (client: FoxitPDFClient) => ({
  name: "pdf_flatten",
  description: `Flatten form fields and annotations in a PDF.

This operation converts interactive elements to static content:
- Form fields become non-editable text
- Annotations become part of the page
- Comments are merged into the document

Use cases:
- Finalize forms before distribution
- Create non-editable copies
- Prepare for archiving
- Prevent further modifications

Workflow:
1. Upload PDF using upload_document tool
2. Call this tool
3. Download flattened PDF using download_document tool`,
  parameters: z.object({
    documentId: z.string().describe("Document ID of the PDF to flatten"),
    password: z.string().optional().describe("Password if PDF is password-protected"),
  }),
  execute: async (args: { documentId: string; password?: string }) => {
    try {
      const result = await executeAndWait(client, () =>
        client.pdfFlatten(args.documentId, args.password)
      );

      return JSON.stringify({
        success: true,
        taskId: result.taskId,
        resultDocumentId: result.resultDocumentId,
        message: `PDF flattened successfully. Download using documentId: ${result.resultDocumentId}`,
      });
    } catch (error) {
      return JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : String(error),
        code: (error as { code?: string }).code ?? "FLATTEN_FAILED",
        taskId: (error as { taskId?: string }).taskId,
      });
    }
  },
});

export const pdfCompressTool = (client: FoxitPDFClient) => ({
  name: "pdf_compress",
  description: `Compress PDF file size by optimizing images and removing redundant data.

Compression levels:
- HIGH: Maximum compression, some quality loss
- MEDIUM: Balanced compression and quality
- LOW: Light compression, maximum quality

Features:
- Image resolution reduction
- Removes duplicate resources
- Optimizes font embedding
- Removes unused objects

Typical compression ratios:
- HIGH: 60-80% size reduction
- MEDIUM: 40-60% size reduction
- LOW: 20-40% size reduction

Workflow:
1. Upload PDF using upload_document tool
2. Call this tool with compression level
3. Download compressed PDF using download_document tool`,
  parameters: z.object({
    documentId: z.string().describe("Document ID of the PDF to compress"),
    compressionLevel: z
      .enum(["HIGH", "MEDIUM", "LOW"])
      .describe("Compression level"),
    password: z.string().optional().describe("Password if PDF is password-protected"),
  }),
  execute: async (args: {
    documentId: string;
    compressionLevel: string;
    password?: string;
  }) => {
    try {
      const result = await executeAndWait(client, () =>
        client.pdfCompress(args.documentId, args.compressionLevel, args.password)
      );

      return JSON.stringify({
        success: true,
        taskId: result.taskId,
        resultDocumentId: result.resultDocumentId,
        compressionLevel: args.compressionLevel,
        message: `PDF compressed successfully. Download using documentId: ${result.resultDocumentId}`,
      });
    } catch (error) {
      return JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : String(error),
        code: (error as { code?: string }).code ?? "COMPRESS_FAILED",
        taskId: (error as { taskId?: string }).taskId,
      });
    }
  },
});

export const pdfManipulateTool = (client: FoxitPDFClient) => ({
  name: "pdf_manipulate",
  description: `Reorganize, rotate, or delete pages in a PDF.

Operations:
- ROTATE: Rotate a page (90, 180, or 270 degrees)
- DELETE: Remove a page
- REORDER: Move a page to a different position

Each operation requires:
- type: Operation type
- pageIndex: Target page (0-based index)
- rotation: Rotation angle (for ROTATE)
- targetIndex: New position (for REORDER)

Example operations:
- Rotate page 1 by 90°: {type: "ROTATE", pageIndex: 0, rotation: 90}
- Delete page 3: {type: "DELETE", pageIndex: 2}
- Move page 5 to position 2: {type: "REORDER", pageIndex: 4, targetIndex: 1}

Workflow:
1. Upload PDF using upload_document tool
2. Call this tool with array of operations
3. Download modified PDF using download_document tool`,
  parameters: z.object({
    documentId: z.string().describe("Document ID of the PDF to manipulate"),
    operations: z
      .array(
        z.object({
          type: z
            .enum(["ROTATE", "DELETE", "REORDER"])
            .describe("Type of operation"),
          pageIndex: z.number().describe("Target page index (0-based)"),
          rotation: z
            .number()
            .optional()
            .describe("Rotation angle in degrees (for ROTATE)"),
          targetIndex: z
            .number()
            .optional()
            .describe("New position index (for REORDER)"),
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
      const result = await executeAndWait(client, () =>
        client.pdfManipulate(args.documentId, args.operations, args.password)
      );

      return JSON.stringify({
        success: true,
        taskId: result.taskId,
        resultDocumentId: result.resultDocumentId,
        operationsCount: args.operations.length,
        message: `PDF manipulated successfully with ${args.operations.length} operations. Download using documentId: ${result.resultDocumentId}`,
      });
    } catch (error) {
      return JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : String(error),
        code: (error as { code?: string }).code ?? "MANIPULATE_FAILED",
        taskId: (error as { taskId?: string }).taskId,
      });
    }
  },
});

// ============ Security Tools ============

export const pdfRemovePasswordTool = (client: FoxitPDFClient) => ({
  name: "pdf_remove_password",
  description: `Remove password protection from a PDF document.

Requires the current password to remove protection.

This will remove:
- User password (open password)
- Owner password (permissions password)
- All permission restrictions

Use cases:
- Remove protection after authorization
- Prepare PDF for further processing
- Enable full access to content

Workflow:
1. Upload password-protected PDF using upload_document tool
2. Call this tool with current password
3. Download unprotected PDF using download_document tool`,
  parameters: z.object({
    documentId: z.string().describe("Document ID of the protected PDF"),
    password: z.string().describe("Current password of the PDF"),
  }),
  execute: async (args: { documentId: string; password: string }) => {
    try {
      const result = await executeAndWait(client, () =>
        client.pdfRemovePassword(args.documentId, args.password)
      );

      return JSON.stringify({
        success: true,
        taskId: result.taskId,
        resultDocumentId: result.resultDocumentId,
        message: `Password removed successfully. Download using documentId: ${result.resultDocumentId}`,
      });
    } catch (error) {
      return JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : String(error),
        code: (error as { code?: string }).code ?? "REMOVE_PASSWORD_FAILED",
        taskId: (error as { taskId?: string }).taskId,
      });
    }
  },
});

// ============ Enhancement Tools ============

export const pdfWatermarkTool = (client: FoxitPDFClient) => ({
  name: "pdf_watermark",
  description: `Add text or image watermark to PDF pages.

Watermark types:
- TEXT: Text watermark (default)
- IMAGE: Image watermark (provide image documentId as content)

Configuration:
- content: Watermark text or image documentId
- position: Placement (CENTER, TOP_LEFT, TOP_RIGHT, BOTTOM_LEFT, BOTTOM_RIGHT)
- opacity: Transparency (0.0-1.0, default: 0.5)
- rotation: Rotation angle in degrees (default: 0)
- fontSize: Text size in points (for TEXT type)
- color: Text color in hex format (e.g., "#FF0000" for red)
- pageRanges: Specific pages (e.g., "1-3,5,7-9", default: all pages)

Use cases:
- Add "DRAFT" or "CONFIDENTIAL" stamps
- Add company logos
- Copyright protection
- Document tracking

Workflow:
1. Upload PDF using upload_document tool
2. (Optional) Upload watermark image for IMAGE type
3. Call this tool with watermark configuration
4. Download watermarked PDF using download_document tool`,
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
      const result = await executeAndWait(client, () =>
        client.pdfWatermark(
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
        )
      );

      return JSON.stringify({
        success: true,
        taskId: result.taskId,
        resultDocumentId: result.resultDocumentId,
        message: `Watermark added successfully. Download using documentId: ${result.resultDocumentId}`,
      });
    } catch (error) {
      return JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : String(error),
        code: (error as { code?: string }).code ?? "WATERMARK_FAILED",
        taskId: (error as { taskId?: string }).taskId,
      });
    }
  },
});

export const pdfLinearizeTool = (client: FoxitPDFClient) => ({
  name: "pdf_linearize",
  description: `Optimize PDF for fast web viewing (linearization).

Linearization reorganizes PDF structure for:
- Page-at-a-time downloading
- Faster initial page display
- Better streaming performance
- Improved web browser experience

Also called "Fast Web View" or "Optimized for Web".

Benefits:
- First page displays before full download
- Reduced initial loading time
- Better user experience for large PDFs
- No quality loss

Use cases:
- PDFs for web hosting
- Online document viewers
- Large documents for distribution
- E-commerce catalogs

Workflow:
1. Upload PDF using upload_document tool
2. Call this tool
3. Download linearized PDF using download_document tool`,
  parameters: z.object({
    documentId: z.string().describe("Document ID of the PDF to linearize"),
  }),
  execute: async (args: { documentId: string }) => {
    try {
      const result = await executeAndWait(client, () =>
        client.pdfLinearize(args.documentId)
      );

      return JSON.stringify({
        success: true,
        taskId: result.taskId,
        resultDocumentId: result.resultDocumentId,
        message: `PDF linearized successfully. Download using documentId: ${result.resultDocumentId}`,
      });
    } catch (error) {
      return JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : String(error),
        code: (error as { code?: string }).code ?? "LINEARIZE_FAILED",
        taskId: (error as { taskId?: string }).taskId,
      });
    }
  },
});

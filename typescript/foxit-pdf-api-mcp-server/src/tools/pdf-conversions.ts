import { z } from "zod";

import type { FoxitPDFClient } from "../client";
import { executeAndWait } from "../utils/task-poller";

export const pdfToPptTool = (client: FoxitPDFClient) => ({
  name: "pdf_to_ppt",
  description: `Convert PDF to PowerPoint presentation format (.pptx).

Features:
- One slide per PDF page
- Maintains layout and images
- Preserves text when possible
- Handles graphics and charts

Best for:
- Converting presentations back to editable format
- Creating slides from PDF documents

Note: Complex layouts may require manual adjustment.

Workflow:
1. Upload PDF using upload_document tool
2. Call this tool with the documentId
3. Download PowerPoint result using download_document tool`,
  parameters: z.object({
    documentId: z.string().describe("Document ID of the uploaded PDF file"),
    password: z.string().optional().describe("Password if PDF is password-protected"),
  }),
  execute: async (args: { documentId: string; password?: string }) => {
    try {
      const result = await executeAndWait(client, () =>
        client.pdfToPpt(args.documentId, args.password)
      );

      return JSON.stringify({
        success: true,
        taskId: result.taskId,
        resultDocumentId: result.resultDocumentId,
        message: `PDF converted to PowerPoint successfully. Download using documentId: ${result.resultDocumentId}`,
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

export const pdfToHtmlTool = (client: FoxitPDFClient) => ({
  name: "pdf_to_html",
  description: `Convert PDF to web-friendly HTML format.

Features:
- Preserves text and layout
- Extracts images
- CSS styling for formatting
- Responsive design support

Best for:
- Web publishing
- Content extraction
- Accessibility improvements

Workflow:
1. Upload PDF using upload_document tool
2. Call this tool with the documentId
3. Download HTML result using download_document tool`,
  parameters: z.object({
    documentId: z.string().describe("Document ID of the uploaded PDF file"),
    password: z.string().optional().describe("Password if PDF is password-protected"),
  }),
  execute: async (args: { documentId: string; password?: string }) => {
    try {
      const result = await executeAndWait(client, () =>
        client.pdfToHtml(args.documentId, args.password)
      );

      return JSON.stringify({
        success: true,
        taskId: result.taskId,
        resultDocumentId: result.resultDocumentId,
        message: `PDF converted to HTML successfully. Download using documentId: ${result.resultDocumentId}`,
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

export const pdfToTextTool = (client: FoxitPDFClient) => ({
  name: "pdf_to_text",
  description: `Convert PDF text content to plain text format.

Features:
- Extracts all text content
- Preserves reading order
- Handles multi-column layouts
- Removes formatting

Best for:
- Text extraction
- Content analysis
- Data mining
- Indexing

Workflow:
1. Upload PDF using upload_document tool
2. Call this tool with the documentId
3. Download text result using download_document tool`,
  parameters: z.object({
    documentId: z.string().describe("Document ID of the uploaded PDF file"),
    password: z.string().optional().describe("Password if PDF is password-protected"),
  }),
  execute: async (args: { documentId: string; password?: string }) => {
    try {
      const result = await executeAndWait(client, () =>
        client.pdfToText(args.documentId, args.password)
      );

      return JSON.stringify({
        success: true,
        taskId: result.taskId,
        resultDocumentId: result.resultDocumentId,
        message: `PDF converted to text successfully. Download using documentId: ${result.resultDocumentId}`,
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

export const pdfToImageTool = (client: FoxitPDFClient) => ({
  name: "pdf_to_image",
  description: `Convert PDF pages to images.

Supported output formats: JPG, PNG, TIFF, BMP

Configuration:
- imageFormat: Output format (default: PNG)
- dpi: Resolution in dots per inch (default: 150, max: 300)
- pageRanges: Specific pages to convert (e.g., "1-3,5,7-9")

Features:
- High-quality rendering
- Configurable resolution
- Multiple output formats
- Selective page conversion

Best for:
- Creating thumbnails
- Image-based workflows
- Preview generation
- Archiving

Workflow:
1. Upload PDF using upload_document tool
2. Call this tool with documentId and config
3. Download image(s) using download_document tool`,
  parameters: z.object({
    documentId: z.string().describe("Document ID of the uploaded PDF file"),
    config: z
      .object({
        imageFormat: z
          .enum(["JPG", "PNG", "TIFF", "BMP"])
          .optional()
          .describe("Output image format (default: PNG)"),
        dpi: z
          .number()
          .min(72)
          .max(300)
          .optional()
          .describe("Resolution in DPI (default: 150)"),
        pageRanges: z
          .string()
          .optional()
          .describe('Page ranges to convert (e.g., "1-3,5,7-9")'),
      })
      .optional()
      .describe("Image conversion configuration"),
    password: z.string().optional().describe("Password if PDF is password-protected"),
  }),
  execute: async (args: {
    documentId: string;
    config?: { imageFormat?: string; dpi?: number; pageRanges?: string };
    password?: string;
  }) => {
    try {
      const result = await executeAndWait(client, () =>
        client.pdfToImage(args.documentId, args.config, args.password)
      );

      return JSON.stringify({
        success: true,
        taskId: result.taskId,
        resultDocumentId: result.resultDocumentId,
        config: args.config,
        message: `PDF converted to image(s) successfully. Download using documentId: ${result.resultDocumentId}`,
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

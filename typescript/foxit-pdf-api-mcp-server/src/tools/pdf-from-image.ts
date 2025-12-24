import { z } from "zod";

import type { FoxitPDFClient } from "../client";
import { executeAndWait } from "../utils/task-poller";

export const pdfFromImageTool = (client: FoxitPDFClient) => ({
  name: "pdf_from_image",
  description: `Convert one or more images to PDF format.

Supported formats:
- JPEG/JPG (including EXIF metadata)
- PNG (with transparency)
- TIFF (single and multi-page)
- BMP (all color depths)
- GIF (animated GIFs converted to first frame)

Features:
- Maintains original image quality
- Preserves image metadata when possible
- Handles high-resolution images
- Supports color profiles (ICC)
- Smart compression based on image type

Image processing:
- Automatic color space conversion
- DPI adjustment for optimal output
- Alpha channel handling for PNG
- Multi-page TIFF support

Maximum input size: 100MB per image

Common use cases:
- Convert scanned documents to PDF
- Create PDFs from photos
- Combine multiple images into one PDF

Workflow:
1. Upload image file(s) using upload_document tool
2. Call this tool with the documentId
3. Download result using download_document tool`,
  parameters: z.object({
    documentId: z
      .string()
      .describe("Document ID of the uploaded image file or ZIP of images"),
  }),
  execute: async (args: { documentId: string }) => {
    try {
      const result = await executeAndWait(client, () =>
        client.pdfFromImage(args.documentId)
      );

      return JSON.stringify({
        success: true,
        taskId: result.taskId,
        resultDocumentId: result.resultDocumentId,
        message: `Image(s) converted to PDF successfully. Download using documentId: ${result.resultDocumentId}`,
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

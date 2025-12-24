import { z } from "zod";

import type { FoxitPDFClient } from "../client";
import { executeAndWait } from "../utils/task-poller";

export const pdfFromUrlTool = (client: FoxitPDFClient) => ({
  name: "pdf_from_url",
  description: `Convert a web page (URL) to PDF format.

Features:
- Full page rendering with JavaScript support
- Loads external CSS and images
- Supports HTTPS/SSL
- Configurable page dimensions and layout

Configuration options (same as pdf_from_html):
- dimension: Page size (default: A4)
- rotation: Page rotation
- pageMode: Layout mode
- scalingMode: Content scaling

Limitations:
- JavaScript execution timeout: 30 seconds
- Maximum page load time: 60 seconds
- No support for plugins (Flash, Java, etc.)

Common use cases:
- Save web pages as PDFs
- Archive online content
- Generate reports from web dashboards

Workflow:
1. Call this tool with the URL and optional config
2. Wait for conversion to complete
3. Download result using download_document tool`,
  parameters: z.object({
    url: z.string().url().describe("The web page URL to convert"),
    config: z
      .object({
        dimension: z
          .object({
            width: z.number().describe("Page width in points"),
            height: z.number().describe("Page height in points"),
          })
          .optional(),
        rotation: z.enum(["NONE", "90", "180", "270"]).optional(),
        pageMode: z.enum(["SINGLE_PAGE", "MULTIPLE_PAGE"]).optional(),
        scalingMode: z.enum(["SCALE", "NO_SCALE"]).optional(),
      })
      .optional()
      .describe("PDF configuration options"),
  }),
  execute: async (args: {
    url: string;
    config?: {
      dimension?: { width: number; height: number };
      rotation?: string;
      pageMode?: string;
      scalingMode?: string;
    };
  }) => {
    try {
      const result = await executeAndWait(client, () =>
        client.pdfFromUrl(args.url, args.config)
      );

      return JSON.stringify({
        success: true,
        taskId: result.taskId,
        resultDocumentId: result.resultDocumentId,
        url: args.url,
        message: `Web page converted to PDF successfully. Download using documentId: ${result.resultDocumentId}`,
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

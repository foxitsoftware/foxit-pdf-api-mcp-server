import { z } from "zod";

import type { FoxitPDFClient } from "../client";

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
2. Use get_task_result to poll for completion and retrieve the download link`,
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
      const { taskId } = await client.pdfFromUrl(args.url, args.config);
      return JSON.stringify({
        success: true,
        taskId,
        url: args.url,
        message: "URL to PDF conversion submitted. Use get_task_result to check status and retrieve the download link.",
      });
    } catch (error) {
      return JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : String(error),
        errorType: (error as { code?: string }).code ?? "CONVERSION_FAILED",
        taskId: (error as { taskId?: string }).taskId,
      });
    }
  },
});

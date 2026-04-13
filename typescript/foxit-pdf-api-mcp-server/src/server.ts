import { FastMCP } from "fastmcp";

import { FoxitPDFClient } from "./client";
import { config } from "./config";
import { VERSION } from "./version";
import {
  createShareLinkTool,
  deleteDocumentTool,
  downloadDocumentTool,
  exportPdfFormDataTool,
  getTaskResultTool,
  getPdfPropertiesTool,
  importPdfFormDataTool,
  pdfCompareTool,
  pdfCompressTool,
  pdfDeletePagesTool,
  pdfExtractTool,
  pdfExtractPagesTool,
  pdfExtractTextTool,
  pdfFlattenTool,
  pdfFromExcelTool,
  pdfFromHtmlTool,
  pdfFromImageTool,
  pdfFromPptTool,
  pdfFromTextTool,
  pdfFromUrlTool,
  pdfFromWordTool,
  pdfLinearizeTool,
  pdfManipulateTool,
  pdfMergeTool,
  pdfOcrTool,
  pdfProtectTool,
  pdfRemovePasswordTool,
  pdfReorderPagesTool,
  pdfRotatePagesTool,
  pdfSplitTool,
  pdfStructuralAnalysisTool,
  pdfToExcelTool,
  pdfToHtmlTool,
  pdfToImageTool,
  pdfToPptTool,
  pdfToTextTool,
  pdfToWordTool,
  pdfWatermarkTool,
  uploadDocumentTool,
  showPdfToolsTool,
  showPdfViewerTool,
  pdfToolsHtml,
  pdfViewerHtml,
  PDF_TOOLS_WIDGET_URI,
  PDF_VIEWER_WIDGET_URI,
} from "./tools";

// Initialize Foxit PDF API client
export const foxitClient = new FoxitPDFClient({
  baseUrl: config.apiBaseUrl,
  clientId: config.clientId,
  clientSecret: config.clientSecret,
  defaultTimeout: config.defaultTimeout,
  pollInterval: config.pollInterval,
  maxRetries: config.maxRetries,
});

// Create MCP server
export const server = new FastMCP({
  name: "Foxit PDF API MCP Server",
  version: VERSION,
  health: {
    // Enable / disable (default: true)
    enabled: true,
    // Body returned by the endpoint (default: 'ok')
    message: "healthy",
    // Path that should respond (default: '/health')
    path: "/healthz",
    // HTTP status code to return (default: 200)
    status: 200,
  },
});

// Document lifecycle tools
server.addTool(uploadDocumentTool(foxitClient));
server.addTool(downloadDocumentTool(foxitClient));
server.addTool(deleteDocumentTool(foxitClient));
server.addTool(createShareLinkTool(foxitClient));
server.addTool(getTaskResultTool(foxitClient));

// PDF creation tools
server.addTool(pdfFromWordTool(foxitClient));
server.addTool(pdfFromExcelTool(foxitClient));
server.addTool(pdfFromPptTool(foxitClient));
server.addTool(pdfFromHtmlTool(foxitClient));
server.addTool(pdfFromUrlTool(foxitClient));
server.addTool(pdfFromTextTool(foxitClient));
server.addTool(pdfFromImageTool(foxitClient));

// PDF conversion tools
server.addTool(pdfToWordTool(foxitClient));
server.addTool(pdfToExcelTool(foxitClient));
server.addTool(pdfToPptTool(foxitClient));
server.addTool(pdfToHtmlTool(foxitClient));
server.addTool(pdfToTextTool(foxitClient));
server.addTool(pdfToImageTool(foxitClient));

// PDF manipulation tools
server.addTool(pdfSplitTool(foxitClient));
server.addTool(pdfExtractTool(foxitClient));
server.addTool(pdfExtractPagesTool(foxitClient));
server.addTool(pdfExtractTextTool(foxitClient));
server.addTool(pdfFlattenTool(foxitClient));
server.addTool(pdfCompressTool(foxitClient));
server.addTool(pdfManipulateTool(foxitClient));
server.addTool(pdfDeletePagesTool(foxitClient));
server.addTool(pdfRotatePagesTool(foxitClient));
server.addTool(pdfReorderPagesTool(foxitClient));
server.addTool(pdfMergeTool(foxitClient));
server.addTool(pdfProtectTool(foxitClient));
server.addTool(pdfRemovePasswordTool(foxitClient));
server.addTool(pdfWatermarkTool(foxitClient));
server.addTool(pdfLinearizeTool(foxitClient));

// Analysis tools
server.addTool(getPdfPropertiesTool(foxitClient));
server.addTool(pdfCompareTool(foxitClient));
server.addTool(pdfOcrTool(foxitClient));
server.addTool(pdfStructuralAnalysisTool(foxitClient));

// Forms tools
server.addTool(exportPdfFormDataTool(foxitClient));
server.addTool(importPdfFormDataTool(foxitClient));

// Widget tools (MCP App UI)
server.addResource({
  uri: PDF_TOOLS_WIDGET_URI,
  name: "Foxit PDF Tools Widget",
  mimeType: "text/html",
  load: async () => ({ text: pdfToolsHtml() }),
});
server.addResource({
  uri: PDF_VIEWER_WIDGET_URI,
  name: "Foxit PDF Viewer Widget",
  mimeType: "text/html",
  load: async () => ({ text: pdfViewerHtml() }),
});
server.addTool(showPdfToolsTool(foxitClient));
server.addTool(showPdfViewerTool(foxitClient));

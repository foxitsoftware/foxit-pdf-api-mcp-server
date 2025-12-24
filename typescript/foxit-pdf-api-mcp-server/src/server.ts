import { FastMCP } from "fastmcp";

import { FoxitPDFClient } from "./client";
import { config } from "./config";
import { VERSION } from "./version";
import {
  deleteDocumentTool,
  downloadDocumentTool,
  exportPdfFormDataTool,
  getPdfPropertiesTool,
  importPdfFormDataTool,
  pdfCompareTool,
  pdfCompressTool,
  pdfExtractTool,
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
server.addTool(pdfFlattenTool(foxitClient));
server.addTool(pdfCompressTool(foxitClient));
server.addTool(pdfManipulateTool(foxitClient));
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

import { readFile } from "fs/promises";
import { z } from "zod";

import type { FoxitPDFClient } from "../client";

/**
 * Upload document tool
 */
export const uploadDocumentTool = (client: FoxitPDFClient) => ({
  name: "upload_document",
  description: `Upload a document for processing with Foxit PDF API.
  
Returns a documentId that can be used in subsequent operations.

Supported formats:
- PDF documents
- Microsoft Office documents (Word, Excel, PowerPoint)
- Images (PNG, JPEG, TIFF, BMP, GIF)
- Text files
- HTML files

Maximum file size: 100MB

Input options (choose one):
1. resourceUri: MCP resource URI (recommended, e.g., file:///path/to/file.pdf)
2. fileContent: Base64-encoded file content + fileName (fallback)

Usage: Always call this tool first before performing any PDF operations.`,
  parameters: z.object({
    resourceUri: z
      .string()
      .optional()
      .describe("MCP resource URI to read the file from (recommended)"),
    fileContent: z
      .string()
      .optional()
      .describe("Base64-encoded file content (fallback when resources unavailable)"),
    fileName: z
      .string()
      .optional()
      .describe("File name (required when using fileContent, optional for resourceUri)"),
  }),
  execute: async (
    args: {
      resourceUri?: string;
      fileContent?: string;
      fileName?: string;
    },
    context: any
  ) => {
    try {
      let fileBuffer: Buffer;
      let actualFileName: string;

      // Option 1: Read from MCP resource (recommended)
      if (args.resourceUri) {
        try {
          // Try to read resource via MCP protocol
          const resourceContents = await context.server.readResource(args.resourceUri);
          
          // Handle different content types
          if (resourceContents.contents?.[0]) {
            const content = resourceContents.contents[0];
            if ("blob" in content && content.blob) {
              // Binary content as base64
              fileBuffer = Buffer.from(content.blob, "base64");
            } else if ("text" in content && content.text) {
              // Text content
              fileBuffer = Buffer.from(content.text);
            } else {
              throw new Error("Unsupported resource content type");
            }
          } else {
            throw new Error("No content in resource response");
          }
          
          // Extract filename from URI
          actualFileName = args.fileName || (args.resourceUri.split("/").pop()?.split("?")[0] ?? "document");
        } catch (resourceError) {
          // Fallback: if resourceUri looks like a file path, try reading directly
          if (args.resourceUri.startsWith("file://")) {
            const filePath = args.resourceUri.replace("file://", "");
            fileBuffer = await readFile(filePath);
            actualFileName = args.fileName || (filePath.split("/").pop() ?? "document");
          } else {
            throw new Error(
              `Failed to read resource: ${resourceError instanceof Error ? resourceError.message : String(resourceError)}. ` +
              `Try using 'fileContent' (base64) instead.`
            );
          }
        }
      }
      // Option 2: Decode base64 content
      else if (args.fileContent) {
        if (!args.fileName) {
          throw new Error("fileName is required when using fileContent");
        }
        fileBuffer = Buffer.from(args.fileContent, "base64");
        actualFileName = args.fileName;
      }
      // No valid input provided
      else {
        throw new Error("Must provide either resourceUri or fileContent");
      }

      // Upload to API
      const response = await client.uploadDocument(
        args.resourceUri || actualFileName,
        fileBuffer,
        actualFileName
      );

      return JSON.stringify({
        success: true,
        documentId: response.documentId,
        fileName: actualFileName,
        message: `Document uploaded successfully. Use documentId '${response.documentId}' in other operations.`,
      });
    } catch (error) {
      return JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : String(error),
        code: (error as { code?: string }).code ?? "UPLOAD_FAILED",
      });
    }
  },
});

/**
 * Download document tool
 */
export const downloadDocumentTool = (client: FoxitPDFClient) => ({
  name: "download_document",
  description: `Download a document from Foxit PDF API.

Use this tool to download:
- Previously uploaded documents
- Documents generated from PDF operations (using resultDocumentId from task completion)

The document will be saved to the specified output path.`,
  parameters: z.object({
    documentId: z
      .string()
      .describe("The document ID to download (from upload or operation result)"),
    outputPath: z
      .string()
      .describe("Absolute path where the downloaded file should be saved"),
    filename: z
      .string()
      .optional()
      .describe("Optional custom filename for the download"),
  }),
  execute: async (args: {
    documentId: string;
    outputPath: string;
    filename?: string;
  }) => {
    try {
      // Download from API
      const fileContent = await client.downloadDocument(
        args.documentId,
        args.filename
      );

      // Write to disk
      const fs = await import("fs/promises");
      await fs.writeFile(args.outputPath, fileContent);

      return JSON.stringify({
        success: true,
        documentId: args.documentId,
        outputPath: args.outputPath,
        size: fileContent.length,
        message: `Document downloaded successfully to ${args.outputPath}`,
      });
    } catch (error) {
      return JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : String(error),
        code: (error as { code?: string }).code ?? "DOWNLOAD_FAILED",
      });
    }
  },
});

/**
 * Delete document tool
 */
export const deleteDocumentTool = (client: FoxitPDFClient) => ({
  name: "delete_document",
  description: `Delete a document from Foxit PDF API.

This operation is permanent and cannot be undone.

Use this tool to clean up:
- Uploaded documents that are no longer needed
- Intermediate documents from operations
- Generated documents after downloading

Note: This helps manage storage and avoid accumulating unused documents.`,
  parameters: z.object({
    documentId: z
      .string()
      .describe("The document ID to delete"),
  }),
  execute: async (args: { documentId: string }) => {
    try {
      await client.deleteDocument(args.documentId);

      return JSON.stringify({
        success: true,
        documentId: args.documentId,
        message: `Document ${args.documentId} deleted successfully`,
      });
    } catch (error) {
      return JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : String(error),
        code: (error as { code?: string }).code ?? "DELETE_FAILED",
      });
    }
  },
});

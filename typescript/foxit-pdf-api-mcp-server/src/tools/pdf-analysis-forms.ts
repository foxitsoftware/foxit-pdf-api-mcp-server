import { z } from "zod";

import type { FoxitPDFClient } from "../client";
import { executeAndWait } from "../utils/task-poller";

// ============ Analysis Tools ============

export const pdfCompareTool = (client: FoxitPDFClient) => ({
  name: "pdf_compare",
  description: `Compare two PDF documents and generate a comparison report.

Compares:
- Text content differences
- Visual layout changes
- Added/removed content
- Modified sections

The result is a PDF report highlighting differences with:
- Red annotations for deletions
- Green annotations for additions
- Yellow highlights for modifications

Use cases:
- Document version control
- Contract review
- Quality assurance
- Change tracking

Workflow:
1. Upload both PDFs using upload_document tool
2. Call this tool with both documentIds
3. Download comparison report using download_document tool`,
  parameters: z.object({
    documentId1: z.string().describe("First PDF document ID"),
    documentId2: z.string().describe("Second PDF document ID"),
    password1: z.string().optional().describe("Password for first PDF if protected"),
    password2: z.string().optional().describe("Password for second PDF if protected"),
  }),
  execute: async (args: {
    documentId1: string;
    documentId2: string;
    password1?: string;
    password2?: string;
  }) => {
    try {
      const result = await executeAndWait(client, () =>
        client.pdfCompare(
          args.documentId1,
          args.documentId2,
          args.password1,
          args.password2
        )
      );

      return JSON.stringify({
        success: true,
        taskId: result.taskId,
        resultDocumentId: result.resultDocumentId,
        message: `PDFs compared successfully. Download comparison report using documentId: ${result.resultDocumentId}`,
      });
    } catch (error) {
      return JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : String(error),
        code: (error as { code?: string }).code ?? "COMPARE_FAILED",
        taskId: (error as { taskId?: string }).taskId,
      });
    }
  },
});

export const pdfOcrTool = (client: FoxitPDFClient) => ({
  name: "pdf_ocr",
  description: `Perform OCR (Optical Character Recognition) on a PDF document.

Converts scanned PDFs or image-based PDFs to searchable text PDFs.

Features:
- Multi-language support
- Preserves original layout
- Makes text searchable and copyable
- Enables text extraction

Configuration:
- languages: Array of language codes (e.g., ["en-US", "es-ES", "fr-FR"])
- pageRanges: Specific pages to OCR (e.g., "1-5,10-15")

Supported languages:
• CJK Languages: Chinese-Simplified (zh-CN, zh-Hans), Chinese-Traditional (zh-TW, zh-Hant), Japanese (ja-JP), Korean (ko-KR)
• European Languages: Basque (eu-ES), Bulgarian (bg-BG), Catalan (ca-ES), Croatian (hr-HR), Czech (cs-CZ), Danish (da-DK), Dutch (nl-NL, nl-BE), English (en-US, en-GB, en-AU, en-CA), Estonian (et-EE), Finnish (fi-FI), French (fr-FR, fr-CA, fr-BE, fr-CH), Galician (gl-ES), German (de-DE, de-AT, de-CH, de-LI, de-LU), Greek (el-GR), Hebrew (he-IL), Hungarian (hu-HU), Icelandic (is-IS), Italian (it-IT, it-CH), Latvian (lv-LV), Lithuanian (lt-LT), Maltese (mt-MT), Norwegian (nb-NO, nn-NO), Polish (pl-PL), Portuguese (pt-PT, pt-BR), Romanian (ro-RO), Russian (ru-RU), Serbian (sr-RS), Slovak (sk-SK), Slovenian (sl-SI), Spanish (es-ES, es-MX, es-AR, es-CL, es-CO, es-PE, es-VE), Swedish (sv-SE), Turkish (tr-TR), Ukrainian (uk-UA)
• Other Languages: Thai (th-TH)

Use cases:
- Make scanned documents searchable
- Extract text from image-based PDFs
- Create accessible versions of scanned content
- Convert paper documents to editable format

Workflow:
1. Upload scanned PDF using upload_document tool
2. Call this tool with language configuration
3. Download searchable PDF using download_document tool`,
  parameters: z.object({
    documentId: z.string().describe("Document ID of the PDF to OCR"),
    languages: z
      .array(z.string())
      .optional()
      .describe('Language codes using standard format (e.g., ["en-US", "es-ES"], default: ["en-US"])'),
    pageRanges: z
      .string()
      .optional()
      .describe('Pages to OCR (e.g., "1-5,10", default: all pages)'),
    password: z.string().optional().describe("Password if PDF is password-protected"),
  }),
  execute: async (args: {
    documentId: string;
    languages?: string[];
    pageRanges?: string;
    password?: string;
  }) => {
    try {
      const result = await executeAndWait(client, () =>
        client.pdfOcr(
          args.documentId,
          {
            languages: args.languages,
            pageRanges: args.pageRanges,
          },
          args.password
        )
      );

      return JSON.stringify({
        success: true,
        taskId: result.taskId,
        resultDocumentId: result.resultDocumentId,
        languages: args.languages || ["en-US"],
        message: `OCR completed successfully. Download searchable PDF using documentId: ${result.resultDocumentId}`,
      });
    } catch (error) {
      return JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : String(error),
        code: (error as { code?: string }).code ?? "OCR_FAILED",
        taskId: (error as { taskId?: string }).taskId,
      });
    }
  },
});

export const pdfStructuralAnalysisTool = (client: FoxitPDFClient) => ({
  name: "pdf_structural_analysis",
  description: `Perform comprehensive structural analysis on a PDF document.

Extracts detailed document structure including:
- Hierarchical organization (titles, headings, paragraphs)
- Layout information with bounding boxes
- Table structures with cell relationships
- Images and visual elements
- Forms and interactive fields
- Document metadata
- Annotations and comments

Output format:
- ZIP archive containing:
  - JSON file with structural analysis (Foxit PDF Extract API v1.0.7 schema)
  - Extracted images and figures
  - Table visualizations

Detected elements:
- title: Document titles and main headings
- head: Section headings with hierarchy levels
- paragraph: Text content blocks with styling
- table: Structured data with cell relationships
- image: Graphics, figures, and visual content
- form: Interactive form fields
- hyperlink: Links and references
- formula: Mathematical expressions

Use cases:
- Document content extraction
- Data mining from PDFs
- Accessibility improvements
- Content migration
- Document understanding for AI/ML

Workflow:
1. Upload PDF using upload_document tool
2. Call this tool
3. Download ZIP result using download_document tool
4. Extract and process the JSON analysis file`,
  parameters: z.object({
    documentId: z.string().describe("Document ID of the PDF to analyze"),
    password: z.string().optional().describe("Password if PDF is password-protected"),
  }),
  execute: async (args: { documentId: string; password?: string }) => {
    try {
      const result = await executeAndWait(client, () =>
        client.pdfStructuralAnalysis(args.documentId, args.password)
      );

      return JSON.stringify({
        success: true,
        taskId: result.taskId,
        resultDocumentId: result.resultDocumentId,
        message: `Structural analysis completed. Download ZIP archive using documentId: ${result.resultDocumentId}`,
      });
    } catch (error) {
      return JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : String(error),
        code: (error as { code?: string }).code ?? "ANALYSIS_FAILED",
        taskId: (error as { taskId?: string }).taskId,
      });
    }
  },
});

// ============ Form Tools ============

export const exportPdfFormDataTool = (client: FoxitPDFClient) => ({
  name: "export_pdf_form_data",
  description: `Extract form data from a PDF and return it as JSON.

Exports all filled form field values from a PDF form.

Output: JSON file with form data structure where:
- Keys are field names (including hierarchical/nested names)
- Values are the field contents

Example output JSON:
\`\`\`json
{
  "name": {
    "first": "John",
    "last": "Doe"
  },
  "email": "john@example.com",
  "dob": "01/14/2025",
  "address": {
    "city": "Springfield",
    "state": "IL"
  }
}
\`\`\`

Use cases:
- Extract form submissions
- Data collection from PDF forms
- Form data migration
- Automated data processing
- Integration with databases

Workflow:
1. Upload filled PDF form using upload_document tool
2. Call this tool
3. Download JSON file using download_document tool
4. Parse JSON to access form data`,
  parameters: z.object({
    documentId: z.string().describe("Document ID of the PDF form"),
    password: z.string().optional().describe("Password if PDF is password-protected"),
  }),
  execute: async (args: { documentId: string; password?: string }) => {
    try {
      const result = await executeAndWait(client, () =>
        client.exportPdfFormData(args.documentId, args.password)
      );

      return JSON.stringify({
        success: true,
        taskId: result.taskId,
        resultDocumentId: result.resultDocumentId,
        message: `Form data exported successfully. Download JSON using documentId: ${result.resultDocumentId}`,
      });
    } catch (error) {
      return JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : String(error),
        code: (error as { code?: string }).code ?? "EXPORT_FORM_FAILED",
        taskId: (error as { taskId?: string }).taskId,
      });
    }
  },
});

export const importPdfFormDataTool = (client: FoxitPDFClient) => ({
  name: "import_pdf_form_data",
  description: `Populate a PDF form with data provided as JSON.

Fills PDF form fields with values from a JSON object.

Input: JSON object where:
- Keys match form field names (including hierarchical/nested names)
- Values are the data to populate

Example input JSON:
\`\`\`json
{
  "name": {
    "first": "John",
    "last": "Doe"
  },
  "email": "john@example.com",
  "dob": "01/14/2025",
  "address": {
    "city": "Springfield",
    "state": "IL"
  }
}
\`\`\`

This will populate fields:
- name.first → "John"
- name.last → "Doe"
- email → "john@example.com"
- etc.

Use cases:
- Automated form filling
- Bulk form population
- Template processing
- Document generation from data
- Personalized document creation

Workflow:
1. Upload blank PDF form using upload_document tool
2. Prepare form data as JSON object
3. Call this tool with documentId and form data
4. Download populated PDF using download_document tool`,
  parameters: z.object({
    documentId: z.string().describe("Document ID of the PDF form template"),
    formData: z
      .record(z.unknown())
      .describe("JSON object with form field names and values"),
    password: z.string().optional().describe("Password if PDF is password-protected"),
  }),
  execute: async (args: {
    documentId: string;
    formData: Record<string, unknown>;
    password?: string;
  }) => {
    try {
      const result = await executeAndWait(client, () =>
        client.importPdfFormData(args.documentId, args.formData, args.password)
      );

      return JSON.stringify({
        success: true,
        taskId: result.taskId,
        resultDocumentId: result.resultDocumentId,
        fieldsCount: Object.keys(args.formData).length,
        message: `Form data imported successfully. Download populated PDF using documentId: ${result.resultDocumentId}`,
      });
    } catch (error) {
      return JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : String(error),
        code: (error as { code?: string }).code ?? "IMPORT_FORM_FAILED",
        taskId: (error as { taskId?: string }).taskId,
      });
    }
  },
});

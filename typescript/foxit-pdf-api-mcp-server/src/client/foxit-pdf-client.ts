import type {
  ApiError,
  DocumentUploadResponse,
  FoxitPDFClientConfig,
  OperationResponse,
  TaskResponse,
} from "../types/api";

/**
 * HTTP Client for Foxit PDF API
 * Handles all direct API interactions without MCP-specific logic
 */
export class FoxitPDFClient {
  private readonly config: Required<FoxitPDFClientConfig>;

  constructor(config: FoxitPDFClientConfig) {
    this.config = {
      baseUrl: config.baseUrl,
      clientId: config.clientId,
      clientSecret: config.clientSecret,
      defaultTimeout: config.defaultTimeout ?? 300000, // 5 minutes
      pollInterval: config.pollInterval ?? 2000, // 2 seconds
      maxRetries: config.maxRetries ?? 3,
    };
  }

  /**
   * Upload a document
   */
  async uploadDocument(
    filePath: string,
    fileContent: Buffer,
    fileName: string
  ): Promise<DocumentUploadResponse> {
    const formData = new FormData();
    const blob = new Blob([new Uint8Array(fileContent)], {
      type: "application/octet-stream",
    });
    formData.append("file", blob, fileName);

    const response = await this.fetchWithAuth("/api/documents/upload", {
      method: "POST",
      body: formData,
    });

    return this.handleResponse<DocumentUploadResponse>(response);
  }

  /**
   * Download a document
   */
  async downloadDocument(
    documentId: string,
    filename?: string
  ): Promise<Buffer> {
    const url = filename
      ? `/api/documents/${documentId}/download?filename=${encodeURIComponent(filename)}`
      : `/api/documents/${documentId}/download`;

    const response = await this.fetchWithAuth(url, {
      method: "GET",
    });

    if (!response.ok) {
      throw await this.createApiError(response);
    }

    const arrayBuffer = await response.arrayBuffer();
    return Buffer.from(arrayBuffer);
  }

  /**
   * Delete a document
   */
  async deleteDocument(documentId: string): Promise<void> {
    const response = await this.fetchWithAuth(`/api/documents/${documentId}`, {
      method: "DELETE",
    });

    if (!response.ok) {
      throw await this.createApiError(response);
    }
  }

  /**
   * Get task status
   */
  async getTaskStatus(taskId: string): Promise<TaskResponse> {
    const response = await this.fetchWithAuth(`/api/tasks/${taskId}`, {
      method: "GET",
    });

    return this.handleResponse<TaskResponse>(response);
  }

  /**
   * Convert PDF to Word
   */
  async pdfToWord(
    documentId: string,
    password?: string
  ): Promise<OperationResponse> {
    return this.submitOperation("/api/documents/convert/pdf-to-word", {
      documentId,
      password,
    });
  }

  /**
   * Convert Word to PDF
   */
  async pdfFromWord(documentId: string): Promise<OperationResponse> {
    return this.submitOperation("/api/documents/create/pdf-from-word", {
      documentId,
    });
  }

  /**
   * Merge PDFs
   */
  async pdfMerge(
    documents: Array<{ documentId: string; password?: string }>
  ): Promise<OperationResponse> {
    return this.submitOperation("/api/documents/enhance/pdf-combine", {
      documents,
    });
  }

  /**
   * Protect PDF with password
   */
  async pdfProtect(
    documentId: string,
    config: {
      userPassword?: string;
      ownerPassword?: string;
      permissions?: string[];
    }
  ): Promise<OperationResponse> {
    return this.submitOperation("/api/documents/security/pdf-protect", {
      documentId,
      config,
    });
  }

  /**
   * Get PDF properties (returns data, not a file)
   */
  async getPdfProperties(
    documentId: string,
    config?: {
      includeExtendedInfo?: boolean;
      includePageInfo?: boolean;
    }
  ): Promise<OperationResponse> {
    return this.submitOperation("/api/documents/analyze/get-pdf-properties", {
      documentId,
      config,
    });
  }

  // ============ PDF Creation Tools ============

  /**
   * Convert Excel to PDF
   */
  async pdfFromExcel(documentId: string): Promise<OperationResponse> {
    return this.submitOperation("/api/documents/create/pdf-from-excel", {
      documentId,
    });
  }

  /**
   * Convert PowerPoint to PDF
   */
  async pdfFromPpt(documentId: string): Promise<OperationResponse> {
    return this.submitOperation("/api/documents/create/pdf-from-ppt", {
      documentId,
    });
  }

  /**
   * Convert HTML to PDF
   */
  async pdfFromHtml(
    documentId: string,
    config?: {
      dimension?: { width: number; height: number };
      rotation?: string;
      pageMode?: string;
      scalingMode?: string;
    }
  ): Promise<OperationResponse> {
    return this.submitOperation("/api/documents/create/pdf-from-html", {
      documentId,
      config,
    });
  }

  /**
   * Convert URL to PDF
   */
  async pdfFromUrl(
    url: string,
    config?: {
      dimension?: { width: number; height: number };
      rotation?: string;
      pageMode?: string;
      scalingMode?: string;
    }
  ): Promise<OperationResponse> {
    return this.submitOperation("/api/documents/create/pdf-from-url", {
      url,
      config,
    });
  }

  /**
   * Convert Text to PDF
   */
  async pdfFromText(documentId: string): Promise<OperationResponse> {
    return this.submitOperation("/api/documents/create/pdf-from-text", {
      documentId,
    });
  }

  /**
   * Convert Image to PDF
   */
  async pdfFromImage(documentId: string): Promise<OperationResponse> {
    return this.submitOperation("/api/documents/create/pdf-from-image", {
      documentId,
    });
  }

  // ============ PDF Conversion Tools ============

  /**
   * Convert PDF to Excel
   */
  async pdfToExcel(documentId: string, password?: string): Promise<OperationResponse> {
    return this.submitOperation("/api/documents/convert/pdf-to-excel", {
      documentId,
      password,
    });
  }

  /**
   * Convert PDF to PowerPoint
   */
  async pdfToPpt(documentId: string, password?: string): Promise<OperationResponse> {
    return this.submitOperation("/api/documents/convert/pdf-to-ppt", {
      documentId,
      password,
    });
  }

  /**
   * Convert PDF to HTML
   */
  async pdfToHtml(documentId: string, password?: string): Promise<OperationResponse> {
    return this.submitOperation("/api/documents/convert/pdf-to-html", {
      documentId,
      password,
    });
  }

  /**
   * Convert PDF to Text
   */
  async pdfToText(documentId: string, password?: string): Promise<OperationResponse> {
    return this.submitOperation("/api/documents/convert/pdf-to-text", {
      documentId,
      password,
    });
  }

  /**
   * Convert PDF to Images
   */
  async pdfToImage(
    documentId: string,
    config?: {
      imageFormat?: string;
      dpi?: number;
      pageRanges?: string;
    },
    password?: string
  ): Promise<OperationResponse> {
    return this.submitOperation("/api/documents/convert/pdf-to-image", {
      documentId,
      config,
      password,
    });
  }

  // ============ PDF Manipulation Tools ============

  /**
   * Split PDF
   */
  async pdfSplit(
    documentId: string,
    splitStrategy: string,
    config?: {
      pageCount?: number;
      pageRanges?: string[];
    },
    password?: string
  ): Promise<OperationResponse> {
    return this.submitOperation("/api/documents/modify/pdf-split", {
      documentId,
      splitStrategy,
      ...config,
      password,
    });
  }

  /**
   * Extract from PDF
   */
  async pdfExtract(
    documentId: string,
    extractType: string,
    config?: {
      pageRanges?: string;
    },
    password?: string
  ): Promise<OperationResponse> {
    return this.submitOperation("/api/documents/modify/pdf-extract", {
      documentId,
      extractType,
      config,
      password,
    });
  }

  /**
   * Flatten PDF
   */
  async pdfFlatten(documentId: string, password?: string): Promise<OperationResponse> {
    return this.submitOperation("/api/documents/modify/pdf-flatten", {
      documentId,
      password,
    });
  }

  /**
   * Compress PDF
   */
  async pdfCompress(
    documentId: string,
    compressionLevel: string,
    password?: string
  ): Promise<OperationResponse> {
    return this.submitOperation("/api/documents/modify/pdf-compress", {
      documentId,
      compressionLevel,
      password,
    });
  }

  /**
   * Manipulate PDF pages
   */
  async pdfManipulate(
    documentId: string,
    operations: Array<{
      type: string;
      pageIndex?: number;
      rotation?: number;
      targetIndex?: number;
    }>,
    password?: string
  ): Promise<OperationResponse> {
    return this.submitOperation("/api/documents/modify/pdf-manipulate", {
      documentId,
      operations,
      password,
    });
  }

  // ============ Security Tools ============

  /**
   * Remove PDF password
   */
  async pdfRemovePassword(
    documentId: string,
    password: string
  ): Promise<OperationResponse> {
    return this.submitOperation("/api/documents/security/pdf-remove-password", {
      documentId,
      password,
    });
  }

  // ============ Enhancement Tools ============

  /**
   * Add watermark to PDF
   */
  async pdfWatermark(
    documentId: string,
    config: {
      content: string;
      type?: string;
      position?: string;
      opacity?: number;
      rotation?: number;
      fontSize?: number;
      color?: string;
      pageRanges?: string;
    },
    password?: string
  ): Promise<OperationResponse> {
    return this.submitOperation("/api/documents/enhance/pdf-watermark", {
      documentId,
      config,
      password,
    });
  }

  /**
   * Linearize PDF
   */
  async pdfLinearize(documentId: string): Promise<OperationResponse> {
    return this.submitOperation("/api/documents/optimize/pdf-linearize", {
      documentId,
    });
  }

  // ============ Analysis Tools ============

  /**
   * Compare two PDFs
   */
  async pdfCompare(
    documentId1: string,
    documentId2: string,
    password1?: string,
    password2?: string
  ): Promise<OperationResponse> {
    return this.submitOperation("/api/documents/analyze/pdf-compare", {
      document1: { documentId: documentId1, password: password1 },
      document2: { documentId: documentId2, password: password2 },
    });
  }

  /**
   * Perform OCR on PDF
   */
  async pdfOcr(
    documentId: string,
    config?: {
      languages?: string[];
      pageRanges?: string;
    },
    password?: string
  ): Promise<OperationResponse> {
    return this.submitOperation("/api/documents/analyze/pdf-ocr", {
      documentId,
      config,
      password,
    });
  }

  /**
   * Perform structural analysis on PDF
   */
  async pdfStructuralAnalysis(
    documentId: string,
    password?: string
  ): Promise<OperationResponse> {
    return this.submitOperation("/api/documents/analyze/pdf-structural-analysis", {
      documentId,
      password,
    });
  }

  // ============ Form Tools ============

  /**
   * Export PDF form data
   */
  async exportPdfFormData(
    documentId: string,
    password?: string
  ): Promise<OperationResponse> {
    return this.submitOperation("/api/documents/forms/export-pdf-form-data", {
      documentId,
      password,
    });
  }

  /**
   * Import PDF form data
   */
  async importPdfFormData(
    documentId: string,
    formData: Record<string, unknown>,
    password?: string
  ): Promise<OperationResponse> {
    return this.submitOperation("/api/documents/forms/import-pdf-form-data", {
      documentId,
      formData,
      password,
    });
  }

  /**
   * Generic operation submission
   */
  private async submitOperation(
    endpoint: string,
    payload: Record<string, unknown>
  ): Promise<OperationResponse> {
    const response = await this.fetchWithAuth(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    return this.handleResponse<OperationResponse>(response);
  }

  /**
   * Fetch with authentication
   */
  private async fetchWithAuth(
    path: string,
    options: RequestInit = {}
  ): Promise<Response> {
    const url = `${this.config.baseUrl}${path}`;
    const headers = new Headers(options.headers);

    // Add authentication headers
    headers.set("client_id", this.config.clientId);
    headers.set("client_secret", this.config.clientSecret);

    return fetch(url, {
      ...options,
      headers,
    });
  }

  /**
   * Handle JSON response
   */
  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      throw await this.createApiError(response);
    }

    const data = await response.json();
    return data as T;
  }

  /**
   * Create API error from response
   */
  private async createApiError(response: Response): Promise<ApiError> {
    let errorData: { code?: string; message?: string; details?: unknown } = {};

    try {
      errorData = await response.json();
    } catch {
      // Response is not JSON
    }

    const error = new Error(
      errorData.message ?? `API request failed with status ${response.status}`
    ) as ApiError;

    error.code = errorData.code ?? `HTTP_${response.status}`;
    error.statusCode = response.status;
    error.details = errorData.details as Record<string, unknown> | undefined;

    return error;
  }

  /**
   * Get configuration
   */
  getConfig(): Required<FoxitPDFClientConfig> {
    return { ...this.config };
  }
}

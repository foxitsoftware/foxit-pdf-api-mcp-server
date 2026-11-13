import type {
  ApiError,
  DocumentUploadResponse,
  FoxitPDFClientConfig,
  OperationResponse,
  TaskResponse,
} from "../types/api";

export interface ShareLinkResponse {
  shareUrl: string;
  token: string;
  expiresAt: string;
}

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
      requestTimeout: config.requestTimeout ?? 30000, // 30 seconds
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
      ? `/api/documents/${encodeURIComponent(documentId)}/download?filename=${encodeURIComponent(filename)}`
      : `/api/documents/${encodeURIComponent(documentId)}/download`;

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
    const response = await this.fetchWithAuth(`/api/documents/${encodeURIComponent(documentId)}`, {
      method: "DELETE",
    });

    if (!response.ok) {
      throw await this.createApiError(response);
    }
  }

  /**
   * Create a time-limited public share link for a document
   */
  async createShareLink(
    documentId: string,
    expirationMinutes?: number,
    filename?: string
  ): Promise<ShareLinkResponse> {
    const payload: Record<string, unknown> = {};
    if (expirationMinutes !== undefined) payload.expirationMinutes = expirationMinutes;
    if (filename !== undefined) payload.filename = filename;

    const response = await this.fetchWithAuth(
      `/api/documents/${encodeURIComponent(documentId)}/share`,
      {
        method: "POST",
        ...(Object.keys(payload).length > 0
          ? { headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) }
          : {}),
      }
    );

    return this.handleResponse<ShareLinkResponse>(response);
  }

  /**
   * Get task status
   */
  async getTaskStatus(taskId: string): Promise<TaskResponse> {
    const response = await this.fetchWithAuth(
      `/api/tasks/${encodeURIComponent(taskId)}`,
      {
        method: "GET",
      }
    );

    const data = await this.handleResponse<Record<string, unknown>>(response);
    return this.parseTask(data);
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
    // API field is `documentInfos` (POST /api/documents/enhance/pdf-combine).
    return this.submitOperation("/api/documents/enhance/pdf-combine", {
      documentInfos: documents,
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
      userPermissions?: string[];
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
    },
    password?: string
  ): Promise<OperationResponse> {
    return this.submitOperation("/api/documents/analyze/get-pdf-properties", {
      documentId,
      password,
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
      pageRange?: string;
    },
    password?: string
  ): Promise<OperationResponse> {
    const { pageRange, ...rest } = config ?? {};
    return this.submitOperation("/api/documents/convert/pdf-to-image", {
      documentId,
      password,
      pageRange,
      ...(Object.keys(rest).length ? { config: rest } : {}),
    });
  }

  // ============ PDF Manipulation Tools ============

  /**
   * Split PDF
   *
   * POST /api/documents/modify/pdf-split. The API takes `pageCount` OR
   * `pageRange` at the top level (mutually exclusive), not a strategy enum.
   */
  async pdfSplit(
    documentId: string,
    pageCount?: number,
    pageRange?: string,
    password?: string
  ): Promise<OperationResponse> {
    return this.submitOperation("/api/documents/modify/pdf-split", {
      documentId,
      pageCount,
      pageRange,
      password,
    });
  }

  /**
   * Extract from PDF
   *
   * POST /api/documents/modify/pdf-extract. `pageRange` is a top-level string.
   */
  async pdfExtract(
    documentId: string,
    extractType: string,
    pageRange?: string,
    password?: string
  ): Promise<OperationResponse> {
    return this.submitOperation("/api/documents/modify/pdf-extract", {
      documentId,
      extractType,
      pageRange,
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
    compressionLevel?: string,
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
   *
   * POST /api/documents/modify/pdf-manipulate. The API expects
   * `config.operations[]` with 1-based `pages`, `targetPosition` (MOVE_PAGES),
   * and a `rotation` enum — not the natural-language op model the tools use.
   * We translate here so callers can keep using 0-based pageIndex / degrees.
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
    const apiOperations = operations.map((op) => {
      const page = (op.pageIndex ?? 0) + 1; // 0-based -> 1-based
      switch (op.type) {
        case "ROTATE":
          return {
            type: "ROTATE_PAGES",
            pages: [page],
            rotation: this.toRotationEnum(op.rotation),
          };
        case "REORDER":
          return {
            type: "MOVE_PAGES",
            pages: [page],
            targetPosition: (op.targetIndex ?? 0) + 1,
          };
        case "DELETE":
        default:
          return { type: "DELETE_PAGES", pages: [page] };
      }
    });

    return this.submitOperation("/api/documents/modify/pdf-manipulate", {
      documentId,
      password,
      config: { operations: apiOperations },
    });
  }

  /** Map a degrees value to the API's rotation enum. */
  private toRotationEnum(degrees?: number): string {
    switch (((degrees ?? 0) % 360 + 360) % 360) {
      case 90:
        return "ROTATE_CLOCKWISE_90";
      case 180:
        return "ROTATE_180";
      case 270:
        return "ROTATE_COUNTERCLOCKWISE_90";
      default:
        return "ROTATE_0";
    }
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

  /**
   * Redact sensitive content from a PDF
   */
  async pdfRedact(
    documentId: string,
    config: {
      texts?: string[];
      overlayText?: string;
      pageRange?: string;
      caseSensitive?: boolean;
      wholeWordsOnly?: boolean;
      redactFormFields?: boolean;
      formFieldTypes?: string[];
      applyImmediately?: boolean;
    }
  ): Promise<OperationResponse> {
    const apiConfig: Record<string, unknown> = {};

    if (config.texts?.length) {
      apiConfig.redactTextList = config.texts.map((text) => ({
        text,
        ...(config.overlayText ? { overlayText: config.overlayText } : {}),
      }));
      const searchOptions: Record<string, unknown> = {};
      if (config.caseSensitive) searchOptions.caseSensitive = true;
      if (config.wholeWordsOnly) searchOptions.wholeWordsOnly = true;
      if (config.pageRange) searchOptions.pageRange = config.pageRange;
      if (Object.keys(searchOptions).length) apiConfig.textSearchOptions = searchOptions;
    }

    if (config.redactFormFields) {
      apiConfig.formFieldRedact = config.formFieldTypes?.length
        ? { fieldTypes: config.formFieldTypes }
        : {};
    }

    if (config.applyImmediately === false) {
      apiConfig.applyImmediately = false;
    }

    return this.submitOperation("/api/documents/security/pdf-redact", {
      documentId,
      config: apiConfig,
    });
  }

  // ============ Enhancement Tools ============

  /**
   * Add watermark to PDF
   *
   * POST /api/documents/enhance/pdf-watermark. The API body places the text/
   * image value inside `config` as `text` / `imageDocId`, and takes
   * `pageRange` at the top level. We accept a single `content` string and
   * route it by watermark type so callers stay simple.
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
      pageRange?: string;
    },
    password?: string
  ): Promise<OperationResponse> {
    const { content, type, pageRange, ...rest } = config;
    const isImage = (type ?? "TEXT").toUpperCase() === "IMAGE";
    const apiConfig: Record<string, unknown> = {
      ...rest,
      ...(isImage ? { imageDocId: content } : { text: content }),
      ...(type ? { type } : {}),
    };

    return this.submitOperation("/api/documents/enhance/pdf-watermark", {
      documentId,
      password,
      pageRange,
      config: apiConfig,
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
   *
   * POST /api/documents/analyze/pdf-compare. The API body uses
   * `baseDocument` / `compareDocument`, not `document1` / `document2`.
   */
  async pdfCompare(
    documentId1: string,
    documentId2: string,
    password1?: string,
    password2?: string
  ): Promise<OperationResponse> {
    return this.submitOperation("/api/documents/analyze/pdf-compare", {
      baseDocument: { documentId: documentId1, password: password1 },
      compareDocument: { documentId: documentId2, password: password2 },
    });
  }

  /**
   * Perform OCR on PDF
   *
   * POST /api/documents/analyze/pdf-ocr. `pageRange` is top-level; the
   * `config` only carries `languages` / `makeEditable`.
   */
  async pdfOcr(
    documentId: string,
    config?: {
      languages?: string[];
      makeEditable?: boolean;
      pageRange?: string;
    },
    password?: string
  ): Promise<OperationResponse> {
    const { pageRange, ...apiConfig } = config ?? {};
    return this.submitOperation("/api/documents/analyze/pdf-ocr", {
      documentId,
      password,
      pageRange,
      ...(Object.keys(apiConfig).length ? { config: apiConfig } : {}),
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
   * Fetch with authentication.
   *
   * - Applies a per-request timeout (`AbortSignal.timeout`) so a stalled
   *   connection can never hang the caller forever.
   * - Retries transient failures (network error, 429, 5xx) with exponential
   *   backoff, up to `maxRetries` attempts. Non-idempotent concern: operations
   *   are retried only when the request never produced a response (network
   *   error) or the server explicitly asked us to back off (429/5xx), which is
   *   safe because those responses carry no side effect we could lose track of.
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

    const maxAttempts = Math.max(1, this.config.maxRetries);
    let lastError: unknown;

    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      // Combine any caller-provided signal with our per-request timeout.
      const timeoutSignal = AbortSignal.timeout(this.config.requestTimeout);
      const signal = options.signal
        ? AbortSignal.any([options.signal, timeoutSignal])
        : timeoutSignal;

      try {
        const response = await fetch(url, { ...options, headers, signal });

        // Retry on transient server-side failures.
        if (this.isRetryableStatus(response.status) && attempt < maxAttempts) {
          await this.backoff(attempt, response.headers.get("retry-after"));
          continue;
        }

        return response;
      } catch (error) {
        // Do not retry if the caller aborted.
        if (options.signal?.aborted) {
          throw error;
        }
        lastError = error;
        if (attempt < maxAttempts) {
          await this.backoff(attempt);
          continue;
        }
      }
    }

    throw lastError instanceof Error
      ? lastError
      : new Error(`Request to ${path} failed`);
  }

  private isRetryableStatus(status: number): boolean {
    return status === 429 || status === 408 || (status >= 500 && status <= 599);
  }

  private async backoff(attempt: number, retryAfter?: string | null): Promise<void> {
    const retryAfterSeconds = retryAfter ? Number(retryAfter) : NaN;
    const delayMs = Number.isFinite(retryAfterSeconds)
      ? retryAfterSeconds * 1000
      : Math.min(1000 * 2 ** (attempt - 1), 8000);
    await new Promise((resolve) => setTimeout(resolve, delayMs));
  }

  /**
   * Normalize a raw task response into a strongly-typed TaskResponse,
   * tolerating unknown status strings and missing/loosely-typed fields.
   */
  private parseTask(json: unknown): TaskResponse {
    const j = (json ?? {}) as Record<string, unknown>;

    const rawStatus = String(j.status ?? "")
      .trim()
      .toUpperCase();
    let status: TaskResponse["status"];
    switch (rawStatus) {
      case "PENDING":
        status = "PENDING";
        break;
      case "PROCESSING":
      case "IN_PROGRESS":
        status = rawStatus === "IN_PROGRESS" ? "IN_PROGRESS" : "PROCESSING";
        break;
      case "COMPLETED":
      case "SUCCESS":
      case "SUCCEEDED":
        status = "COMPLETED";
        break;
      case "FAILED":
      case "FAIL":
      case "ERROR":
        status = "FAILED";
        break;
      default:
        // Unknown status — treat as still in progress rather than crash.
        status = "PROCESSING";
    }

    const error =
      j.error && typeof j.error === "object"
        ? {
            code: String((j.error as Record<string, unknown>).code ?? ""),
            message: String((j.error as Record<string, unknown>).message ?? ""),
            details: (j.error as Record<string, unknown>).details as
              | Record<string, unknown>
              | undefined,
          }
        : undefined;

    return {
      taskId: typeof j.taskId === "string" ? j.taskId : String(j.taskId ?? ""),
      status,
      progress: typeof j.progress === "number" ? j.progress : undefined,
      resultDocumentId:
        typeof j.resultDocumentId === "string" ? j.resultDocumentId : undefined,
      resultData:
        j.resultData && typeof j.resultData === "object"
          ? (j.resultData as Record<string, unknown>)
          : undefined,
      error,
      failedDocuments: Array.isArray(j.failedDocuments)
        ? (j.failedDocuments as TaskResponse["failedDocuments"])
        : undefined,
      createdAt: typeof j.createdAt === "string" ? j.createdAt : undefined,
      updatedAt: typeof j.updatedAt === "string" ? j.updatedAt : undefined,
    };
  }

  /**
   * Handle JSON response
   */
  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      throw await this.createApiError(response);
    }

    // A 204 / empty body has nothing to parse.
    const text = await response.text();
    if (!text) {
      return undefined as T;
    }

    try {
      return JSON.parse(text) as T;
    } catch {
      throw this.createApiErrorFromRaw(
        `Invalid JSON in response: ${text.slice(0, 200)}`,
        "INVALID_JSON",
        response.status
      );
    }
  }

  /**
   * Create API error from response
   */
  private async createApiError(response: Response): Promise<ApiError> {
    let errorData: { code?: string; message?: string; details?: unknown } = {};

    try {
      errorData = (await response.json()) as {
        code?: string;
        message?: string;
        details?: unknown;
      };
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

  private createApiErrorFromRaw(
    message: string,
    code: string,
    statusCode?: number
  ): ApiError {
    const error = new Error(message) as ApiError;
    error.code = code;
    error.statusCode = statusCode;
    return error;
  }

  /**
   * Get configuration
   */
  getConfig(): Required<FoxitPDFClientConfig> {
    return { ...this.config };
  }
}

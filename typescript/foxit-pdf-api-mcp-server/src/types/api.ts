/**
 * Common types for Foxit PDF API
 */

export interface FoxitPDFClientConfig {
  baseUrl: string;
  clientId: string;
  clientSecret: string;
  /** Overall budget (ms) for polling an async task to completion. */
  defaultTimeout?: number;
  /** Poll interval (ms) between task status checks. */
  pollInterval?: number;
  /** Per-request timeout (ms) for a single HTTP call. Default: 30s. */
  requestTimeout?: number;
  /** Number of retries for transient (network / 429 / 5xx) HTTP failures. */
  maxRetries?: number;
}

export type TaskStatus =
  | "PENDING"
  | "PROCESSING"
  | "IN_PROGRESS"
  | "COMPLETED"
  | "FAILED";

export interface ErrorInfo {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

/** One document Foxit skipped during a partially-failed merge. */
export interface FailedDocumentInfo {
  documentId: string;
  errorCode: string;
  message: string;
}

export interface TaskResponse {
  taskId: string;
  status: TaskStatus;
  /** Progress percentage (0-100); may be absent on some responses. */
  progress?: number;
  /** Present for file-producing operations. */
  resultDocumentId?: string;
  /** Present for data-producing operations (e.g. PDF properties). */
  resultData?: Record<string, unknown>;
  error?: ErrorInfo;
  /** Present on combine when `continueMergeOnError` skipped documents. */
  failedDocuments?: FailedDocumentInfo[];
  createdAt?: string;
  updatedAt?: string;
}

export interface DocumentUploadResponse {
  documentId: string;
}

/**
 * Response returned by every asynchronous operation submission.
 * It only carries the id of the task to watch; the operation's actual
 * outputs (resultDocumentId / resultData) become available once the task
 * reaches COMPLETED — read them via `getTaskStatus` / `pollTaskUntilComplete`.
 */
export interface OperationResponse {
  taskId: string;
}

export interface ApiError extends Error {
  code: string;
  statusCode?: number;
  details?: Record<string, unknown>;
}

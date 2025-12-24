/**
 * Common types for Foxit PDF API
 */

export interface FoxitPDFClientConfig {
  baseUrl: string;
  clientId: string;
  clientSecret: string;
  defaultTimeout?: number;
  pollInterval?: number;
  maxRetries?: number;
}

export type TaskStatus = "PENDING" | "PROCESSING" | "COMPLETED" | "FAILED";

export interface TaskResponse {
  taskId: string;
  status: TaskStatus;
  progress: number;
  resultDocumentId?: string;
  resultData?: Record<string, unknown>;
  error?: ErrorInfo;
  createdAt?: string;
  updatedAt?: string;
}

export interface ErrorInfo {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

export interface DocumentUploadResponse {
  documentId: string;
}

export interface OperationResponse {
  taskId: string;
}

export interface ApiError extends Error {
  code: string;
  statusCode?: number;
  details?: Record<string, unknown>;
}

import type { FoxitPDFClient } from "../client";
import type { TaskResponse } from "../types/api";

export interface PollOptions {
  /** Overall budget for polling, in ms. Defaults to the client's `defaultTimeout`. */
  timeoutMs?: number;
  /** Called on every poll tick (progress heartbeats, UI updates). */
  onProgress?: (task: TaskResponse) => void | Promise<void>;
  /** Abort signal — polling stops when aborted. */
  signal?: AbortSignal;
}

/**
 * Poll a task until completion or timeout.
 */
export async function pollTaskUntilComplete(
  client: FoxitPDFClient,
  taskId: string,
  options: PollOptions | number = {}
): Promise<TaskResponse> {
  // Backwards-compatible: allow a bare timeout number as the third arg.
  const opts: PollOptions =
    typeof options === "number" ? { timeoutMs: options } : options;

  const config = client.getConfig();
  const timeout = opts.timeoutMs ?? config.defaultTimeout;
  const pollInterval = config.pollInterval;
  const startTime = Date.now();

  while (true) {
    // Check the budget before issuing another request so a slow/hung call
    // cannot push us past the deadline by more than one poll interval.
    if (opts.signal?.aborted) {
      throw makeTaskError(
        `Wait for task ${taskId} was aborted`,
        "TASK_ABORTED",
        taskId
      );
    }
    if (Date.now() - startTime > timeout) {
      throw makeTaskError(
        `Task ${taskId} did not complete within ${timeout}ms`,
        "TASK_TIMEOUT",
        taskId
      );
    }

    const taskStatus = await client.getTaskStatus(taskId);
    await opts.onProgress?.(taskStatus);

    // Task completed successfully
    if (taskStatus.status === "COMPLETED") {
      return taskStatus;
    }

    // Task failed
    if (taskStatus.status === "FAILED") {
      throw makeTaskError(
        taskStatus.error?.message ?? "Task failed without error details",
        taskStatus.error?.code ?? "TASK_FAILED",
        taskId,
        taskStatus.error?.details
      );
    }

    // Wait before next poll
    await new Promise((resolve) => setTimeout(resolve, pollInterval));
  }
}

/**
 * Execute an operation and wait for completion
 * Returns the final task result
 */
export async function executeAndWait(
  client: FoxitPDFClient,
  operationFn: () => Promise<{ taskId: string }>,
  options: PollOptions | number = {}
): Promise<TaskResponse> {
  const { taskId } = await operationFn();
  return pollTaskUntilComplete(client, taskId, options);
}

function makeTaskError(
  message: string,
  code: string,
  taskId: string,
  details?: unknown
): Error & { code: string; taskId: string; details?: unknown } {
  const error = new Error(message) as Error & {
    code: string;
    taskId: string;
    details?: unknown;
  };
  error.code = code;
  error.taskId = taskId;
  error.details = details;
  return error;
}

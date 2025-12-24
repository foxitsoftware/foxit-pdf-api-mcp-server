import type { FoxitPDFClient } from "../client";
import type { TaskResponse } from "../types/api";

/**
 * Poll a task until completion or timeout
 */
export async function pollTaskUntilComplete(
  client: FoxitPDFClient,
  taskId: string,
  timeoutMs?: number
): Promise<TaskResponse> {
  const config = client.getConfig();
  const timeout = timeoutMs ?? config.defaultTimeout;
  const pollInterval = config.pollInterval;
  const startTime = Date.now();

  while (true) {
    const taskStatus = await client.getTaskStatus(taskId);

    // Task completed successfully
    if (taskStatus.status === "COMPLETED") {
      return taskStatus;
    }

    // Task failed
    if (taskStatus.status === "FAILED") {
      const error = new Error(
        taskStatus.error?.message ?? "Task failed without error details"
      ) as Error & { code: string; taskId: string; details?: unknown };
      error.code = taskStatus.error?.code ?? "TASK_FAILED";
      error.taskId = taskId;
      error.details = taskStatus.error?.details;
      throw error;
    }

    // Check timeout
    if (Date.now() - startTime > timeout) {
      const error = new Error(
        `Task ${taskId} did not complete within ${timeout}ms`
      ) as Error & { code: string; taskId: string };
      error.code = "TASK_TIMEOUT";
      error.taskId = taskId;
      throw error;
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
  timeoutMs?: number
): Promise<TaskResponse> {
  const { taskId } = await operationFn();
  return pollTaskUntilComplete(client, taskId, timeoutMs);
}

import { z } from "zod";

import type { FoxitPDFClient } from "../client";

/**
 * get_task_result — polls an async task and returns the result when complete.
 * Mirrors Python's task_status.py / get_task_result tool exactly.
 */
export const getTaskResultTool = (client: FoxitPDFClient) => ({
  name: "get_task_result",
  description: `Check the status of an async task and retrieve the result when complete.

Call this tool after any operation that returns a taskId
(e.g., pdf_to_word, pdf_merge, pdf_from_html, etc.).

Behavior:
- If the task is still processing, returns status "working".
  Wait a few seconds and call this tool again.
- If the task completed successfully, returns the result with
  resultDocumentId and a download shareUrl.
- If the task failed, returns error details.

Returns:
  JSON with:
  - success: boolean
  - status: "working", "completed", or "failed"
  - message: human-readable status description
  - taskId: the task identifier
  - resultDocumentId: (when completed) identifier for follow-up operations
  - shareUrl: (when completed) public download URL
  - expiresAt: (when completed) link expiration timestamp
  - progress: (when working) task progress percentage, if available
  - error, errorType: (when failed) error details`,
  parameters: z.object({
    task_id: z.string().describe("The taskId returned by the previous operation"),
  }),
  execute: async (args: { task_id: string }) => {
    const { task_id } = args;
    try {
      const taskResponse = await client.getTaskStatus(task_id);
      const rawStatus = (
        (taskResponse.status as string | undefined) ?? ""
      )
        .trim()
        .toUpperCase();

      // ── Completed ──────────────────────────────────────────────────────
      if (["COMPLETED", "SUCCESS", "SUCCEEDED"].includes(rawStatus)) {
        const resultDocumentId = taskResponse.resultDocumentId as
          | string
          | undefined;

        let shareUrl: string | undefined;
        let expiresAt: string | undefined;

        if (resultDocumentId) {
          try {
            const share = await client.createShareLink(resultDocumentId);
            shareUrl = share.shareUrl;
            expiresAt = share.expiresAt;
          } catch {
            // Share link creation is best-effort — don't fail the whole result
          }
        }

        const base_message = "Operation completed successfully";
        const message = shareUrl
          ? `${base_message}. Display the download link as a hyperlink, not the raw URL.`
          : `${base_message}, but no share link was created.`;

        return JSON.stringify(
          {
            success: true,
            status: "completed",
            taskId: task_id,
            message,
            ...(resultDocumentId ? { resultDocumentId } : {}),
            ...(shareUrl ? { shareUrl } : {}),
            ...(expiresAt ? { expiresAt } : {}),
            ...(taskResponse.resultData
              ? { resultData: taskResponse.resultData }
              : {}),
          },
          null,
          2
        );
      }

      // ── Failed ─────────────────────────────────────────────────────────
      if (["FAILED", "FAIL", "ERROR"].includes(rawStatus)) {
        const errorInfo = (taskResponse as Record<string, unknown>).error as
          | Record<string, unknown>
          | undefined;
        return JSON.stringify(
          {
            success: false,
            status: "failed",
            taskId: task_id,
            error: errorInfo?.message ?? "Task failed without error details",
            errorType: errorInfo?.code ?? "TASK_FAILED",
            ...(errorInfo?.details ? { details: errorInfo.details } : {}),
          },
          null,
          2
        );
      }

      // ── Still working ──────────────────────────────────────────────────
      const progress =
        typeof taskResponse.progress === "number"
          ? taskResponse.progress
          : undefined;

      return JSON.stringify(
        {
          success: true,
          status: "working",
          taskId: task_id,
          message:
            "Task is still processing. Please call get_task_result again in a few seconds.",
          ...(progress !== undefined ? { progress } : {}),
        },
        null,
        2
      );
    } catch (error) {
      return JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : String(error),
        errorType: (error as { code?: string }).code ?? "UNKNOWN_ERROR",
        taskId: task_id,
      });
    }
  },
});

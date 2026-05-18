/**
 * La Forja — Puerta `manus_google`.
 *
 * Sprint LA-FORJA-001 v3.2 — D2.4.
 * Doctrina: §2.5 SPEC v3.2.
 *
 * Crea task en cuenta Manus Google vía POST /v2/task.create con header
 * x-manus-api-key: $MANUS_API_KEY_GOOGLE.
 *
 * Wrapper thin sobre src/lib/manus_bridge.ts (D1).
 */

import {
  createTask,
  type CreateTaskOptions,
  type ManusTask,
} from "../lib/manus_bridge.js";

export interface PuertaManusInput {
  prompt: string;
  projectId?: string;
  frontId?: string;
  attachContext?: boolean;
  baseUrl?: string;
}

export interface PuertaManusOutput {
  taskId: string;
  status: string;
  raw: ManusTask;
}

export async function invokeManusGoogle(
  input: PuertaManusInput,
): Promise<PuertaManusOutput> {
  const opts: CreateTaskOptions = {
    account: "google",
    project_id: input.projectId,
    front_id: input.frontId,
    attach_context: input.attachContext,
    baseUrl: input.baseUrl,
  };
  const task = await createTask(input.prompt, opts);
  const taskId = (task.task_id ?? task.id) as string | undefined;
  if (!taskId) {
    throw new Error(
      "[la-forja:puerta_manus_google_missing_task_id] " +
        "Manus API response missing both task_id and id fields",
    );
  }
  return {
    taskId,
    status: (task.status ?? "unknown") as string,
    raw: task,
  };
}

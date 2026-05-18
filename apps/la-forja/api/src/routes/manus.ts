/**
 * La Forja — Ruta /api/manus/task (D2.6).
 *
 * Sprint LA-FORJA-001 v3.2.
 * Doctrina: §4 SPEC v3.2 — bridge M2M para tasks largos.
 *
 * Wrapper sobre handleManusBridge() del bridge D1 (manus_bridge.ts).
 * Permite al frontend (D3) crear tasks Manus y consultar status.
 *
 * Shape canónico HandleManusBridgeResult del D1:
 *   { task_id?, status?, output?, error?, type?, raw?, ... }
 *   - error presente → fallo. type ∈ {rate_limit, timeout, task_failed, bridge_error, unexpected}
 *   - error ausente → éxito; campos task_id/status/output del Manus M2M
 */

import { Hono } from "hono";
import { handleManusBridge } from "../lib/manus_bridge.js";
import { recordEvent } from "../lib/telemetry.js";
import type { ForjaAuthContext } from "../middleware/auth.js";

export interface ManusBridgeRequest {
  action?: "create_task" | "get_status" | "create_and_wait";
  prompt?: string;
  task_id?: string;
  account?: "google" | "apple";
  project_id?: string;
  front_id?: string;
  attach_context?: boolean;
  timeout?: number;
  poll_interval?: number;
}

export function manusRoutes() {
  const app = new Hono<ForjaAuthContext>();

  app.post("/task", async (c) => {
    const body = await c.req.json<ManusBridgeRequest>();
    const result = await handleManusBridge(body);
    const account = body.account ?? "google";

    if (result.error) {
      await recordEvent({
        userId: c.var.user.id,
        type: "puerta_invoked",
        metadata: {
          puerta: `manus_${account}`,
          action: body.action ?? "create_task",
          ok: false,
          error: result.error,
          errorType: result.type,
        },
      });
      const status = result.type === "rate_limit" ? 429 : 500;
      return c.json(
        { ok: false, error: result.error, type: result.type },
        status,
      );
    }

    await recordEvent({
      userId: c.var.user.id,
      type: "puerta_invoked",
      metadata: {
        puerta: `manus_${account}`,
        action: body.action ?? "create_task",
        ok: true,
        taskId: result.task_id,
      },
    });
    return c.json({
      ok: true,
      taskId: result.task_id,
      status: result.status,
      output: result.output,
      raw: result,
    });
  });

  return app;
}

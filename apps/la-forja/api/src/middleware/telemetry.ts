/**
 * La Forja — Middleware de telemetría LF-TELEMETRY-MANDATORY-001.
 *
 * Sprint LA-FORJA-001 v3.2 — D2.5.
 * Doctrina: §7 SPEC v3.2.
 *
 * Inicia un correlation id (request_id), mide duración y emite evento
 * estructurado en stdout (D2-D4) o INSERT INTO forja_telemetry (D5).
 *
 * El handler de la ruta puede emitir eventos adicionales con
 * `recordEvent({...})` directamente. Este middleware solo registra el
 * shape básico request_started / request_completed.
 */

import { randomUUID } from "node:crypto";
import type { Context, MiddlewareHandler, Next } from "hono";
import { recordEvent } from "../lib/telemetry.js";
import type { User } from "../lib/env.js";

export interface ForjaTelemetryContext {
  Variables: {
    user: User;
    requestId: string;
    requestStartedAt: number;
  };
}

export function forjaTelemetry(): MiddlewareHandler<ForjaTelemetryContext> {
  return async (c: Context, next: Next) => {
    const requestId = c.req.header("x-request-id") ?? randomUUID();
    const startedAt = Date.now();
    c.set("requestId", requestId);
    c.set("requestStartedAt", startedAt);
    c.header("x-request-id", requestId);

    await next();

    const user = c.get("user") as User | undefined;
    const durationMs = Date.now() - startedAt;
    // Emitimos un evento canónico solo si hay user (rutas /health no lo tienen).
    if (user) {
      // Reusamos puerta_invoked como type por ahora; en D5 introduciremos
      // request_completed nativo si el SPEC lo añade.
      await recordEvent({
        userId: user.id,
        type: "puerta_invoked",
        metadata: {
          requestId,
          path: c.req.path,
          method: c.req.method,
          status: c.res.status,
          durationMs,
        },
      });
    }
  };
}

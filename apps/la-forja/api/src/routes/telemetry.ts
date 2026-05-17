/**
 * La Forja — Ruta /api/telemetry (D2.6).
 *
 * Sprint LA-FORJA-001 v3.2.
 * Doctrina: LF-TELEMETRY-MANDATORY-001 + §7 SPEC v3.2.
 *
 * Recibe eventos del cliente (frontend D3) que NO se pueden inferir del backend:
 *   - confusion_detected (señal del usuario, no del LLM)
 *   - simplification_requested (botón "explícame más simple")
 *   - thread_abandoned (timeout sin respuesta del usuario)
 *   - completion_reached (usuario marca tema como entendido)
 *
 * Validación binaria:
 *   - type debe ser uno de los 9 canónicos del SPEC
 *   - userId del header (auth stub), NO del body (anti-spoofing)
 */

import { Hono } from "hono";
import { recordEvent, type TelemetryEventType } from "../lib/telemetry";
import type { ForjaAuthContext } from "../middleware/auth";

const VALID_EVENT_TYPES: ReadonlyArray<TelemetryEventType> = [
  "simplification_requested",
  "confusion_detected",
  "turn_abandoned",
  "sprint_completed",
  "sprint_started",
  "puerta_invoked",
  "budget_exceeded",
  "magna_validation_used",
];

export interface TelemetryEventRequest {
  type: TelemetryEventType;
  metadata?: Record<string, unknown>;
  confidence?: number;
}

export function telemetryRoutes() {
  const app = new Hono<ForjaAuthContext>();

  app.post("/", async (c) => {
    const body = await c.req.json<TelemetryEventRequest>();
    if (!body.type || !VALID_EVENT_TYPES.includes(body.type)) {
      return c.json(
        {
          ok: false,
          error: `[la-forja:telemetry_invalid_type] type must be one of ${VALID_EVENT_TYPES.join("|")}`,
        },
        400,
      );
    }
    const user = c.var.user;
    await recordEvent({
      userId: user.id,
      type: body.type,
      metadata: body.metadata,
      confidence: body.confidence,
    });
    return c.json({ ok: true });
  });

  return app;
}

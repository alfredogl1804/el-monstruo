/**
 * La Forja API — entry point.
 *
 * Sprint LA-FORJA-001 v3.2 — D1 no-SQL.
 * Stack: Hono v4.12.18 sobre Node 22 (validado magna 15-may-2026).
 *
 * D1 expone únicamente:
 *   GET /health  →  liveness probe para Railway healthcheck.
 *
 * Las rutas funcionales (/api/tutor/chat, /api/sprints, /api/manus/task)
 * se incorporan en D2 con el multi-model router y el cliente Supabase.
 */

import { serve } from "@hono/node-server";
import { Hono } from "hono";

import { loadEnv } from "./lib/env.js";

const SERVICE_NAME = "la-forja-api";
const SERVICE_VERSION = "0.1.0";

// D1: validación permisiva para permitir /health antes de configurar todas las
// keys en Railway. A partir de D2 cambiamos a strict:true.
const env = loadEnv({ strict: false });

const app = new Hono();

// Middleware de manejo de errores — Regla Dura #2 (jamás dejar un 500 sin log).
app.onError((err, c) => {
  console.error("[la-forja:error]", err);
  return c.json(
    {
      ok: false,
      error: err.message ?? "Internal server error",
      service: SERVICE_NAME,
    },
    500,
  );
});

app.get("/health", (c) => {
  return c.json({
    status: "ok",
    service: SERVICE_NAME,
    version: SERVICE_VERSION,
    timestamp: new Date().toISOString(),
  });
});

app.get("/", (c) => {
  return c.json({
    service: SERVICE_NAME,
    version: SERVICE_VERSION,
    sprint: "LA-FORJA-001",
    phase: "D1 no-SQL",
    endpoints: ["/health"],
  });
});

const port = env.PORT;

serve({ fetch: app.fetch, port }, (info) => {
  console.info(
    `[${SERVICE_NAME}] listening on http://0.0.0.0:${info.port} (env=${env.NODE_ENV})`,
  );
});

export default app;

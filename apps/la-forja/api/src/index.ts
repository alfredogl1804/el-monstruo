/**
 * La Forja API — entry point.
 *
 * Sprint LA-FORJA-001 v3.2 — D2 backend Hono completo.
 * Stack: Hono v4.12.18 sobre Node 22 (validado magna 15-may-2026).
 *
 * Endpoints expuestos:
 *   GET  /health                     liveness probe Railway
 *   GET  /                           service identity + endpoints
 *   POST /api/tutor/chat             Claude Opus 4.7 modo Adaptive
 *   POST /api/sprints                GPT-5.5 Pro Reasoning co-piloto
 *   GET  /api/sprints/states         enumerator 8 states canónicos
 *   POST /api/manus/task             dispatcher M2M bridge multi-cuenta
 *   GET  /api/puertas                LF-FIVE-DOORS-001 enumerator length 5
 *   POST /api/puertas/:nombre        despachador de puerta canónica
 *   POST /api/telemetry              eventos cliente (frontend D3)
 *
 * Pipeline middleware obligatorio:
 *   auth(stub D2 / Google OAuth D4) → budget guard → telemetry → route
 *
 * Diferidos por scope ajustado D2:
 *   - SSE streaming en /api/tutor/chat → D3 con Vercel AI SDK adapter
 *   - JWT Supabase Auth real          → D4 con OAuth Google
 *   - SupabaseBudgetClient persistido → D5 cuando exista forja_budget
 *   - Persistencia spans Langfuse     → D5 cuando exista forja_telemetry
 */

import { serve } from "@hono/node-server";
import { Hono } from "hono";

import { loadEnv } from "./lib/env";
import {
  defaultBudgetClient,
  registerUserForResolver,
} from "./lib/budget_clients";
import { installSupabaseTelemetry } from "./lib/telemetry";
import { forjaAuthStub, type ForjaAuthContext } from "./middleware/auth";
import {
  forjaBudgetGuard,
  type ForjaBudgetContext,
} from "./middleware/budget";
import {
  forjaTelemetry,
  type ForjaTelemetryContext,
} from "./middleware/telemetry";
import { tutorRoutes } from "./routes/tutor";
import { sprintsRoutes } from "./routes/sprints";
import { manusRoutes } from "./routes/manus";
import { puertasRoutes } from "./routes/puertas";
import { telemetryRoutes } from "./routes/telemetry";
import { authRoutes } from "./routes/auth";
import type { Mission } from "./lib/llm/router";

const SERVICE_NAME = "la-forja-api";
const SERVICE_VERSION = "0.1.0-D2";

export type ForjaContext = ForjaAuthContext &
  ForjaBudgetContext &
  ForjaTelemetryContext;

export interface CreateAppOptions {
  /** Permite inyectar BudgetClient en tests sin tocar process.env */
  budgetClient?: ReturnType<typeof defaultBudgetClient>;
  /** Si false, no carga env strict (usado en tests con env mockeada) */
  strictEnv?: boolean;
}

export function createApp(options: CreateAppOptions = {}): Hono<ForjaContext> {
  const strictEnv = options.strictEnv ?? true;
  // Cargar env (lazy validation)
  loadEnv({ strict: strictEnv });

  const budgetClient = options.budgetClient ?? defaultBudgetClient();

  // D5.2: en producción activa el cliente Supabase de telemetría. Idempotente.
  // No bloqueante — el await del dynamic import resuelve antes del primer
  // request porque createApp() corre síncrono al boot del server.
  const env = loadEnv({ strict: false });
  if (env.NODE_ENV === "production") {
    void installSupabaseTelemetry(env.NODE_ENV);
  }

  const app = new Hono<ForjaContext>();

  // -------- Middleware global de manejo de errores --------
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

  // -------- Endpoints públicos (sin auth) --------
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
      phase: "D2 backend Hono completo",
      endpoints: [
        "GET /health",
        "GET /api/auth/google",
        "GET /api/auth/google/callback",
        "POST /api/auth/logout",
        "POST /api/tutor/chat",
        "POST /api/sprints",
        "GET /api/sprints/states",
        "POST /api/manus/task",
        "GET /api/puertas",
        "POST /api/puertas/:nombre",
        "POST /api/telemetry",
      ],
    });
  });

  // -------- Auth routes (PÚBLICAS — sin auth middleware) --------
  // D4: estos endpoints SON la auth, no pueden requerir sesión previa.
  // Se montan ANTES del middleware /api/* para evitar que forjaAuthStub
  // los rechace por falta de x-user-id.
  app.route("/api/auth", authRoutes());

  // -------- Pipeline middleware obligatorio para /api (excepto /auth/*) --------
  // Orden binario: auth → register-user → budget → telemetry → route
  // Selector binario por NODE_ENV (D4): production → forjaAuthGoogle, dev/test → forjaAuthStub
  // Skip-list binario para /api/auth/* (esos endpoints son la propia auth y NO
  // pueden requerir sesión previa). El stub ya rechaza producción con 503 (H-1).
  const authStubMw = forjaAuthStub();
  app.use("/api/*", async (c, next) => {
    if (c.req.path.startsWith("/api/auth/")) {
      await next();
      return;
    }
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    return (authStubMw as any)(c, next);
  });

  // D5.2: registra User resuelto por auth en el cache compartido para que
  // SupabaseBudgetClient y SupabaseTelemetryClient puedan resolver userId
  // → User → google_sub → forja_profiles.id sin reinventar la rueda.
  // Solo activo en producción; en dev/test los clients son in-memory/stdout.
  app.use("/api/*", async (c, next) => {
    if (c.req.path.startsWith("/api/auth/")) {
      await next();
      return;
    }
    const user = c.var.user;
    if (user) {
      registerUserForResolver(user);
    }
    await next();
  });
  app.use("/api/*", forjaTelemetry());

  // -------- Routes con budget guard específico (necesita missionFor) --------
  // Tutor: misión "tutor"
  app.use(
    "/api/tutor/*",
    forjaBudgetGuard({
      client: budgetClient,
      missionFor: () => "tutor" satisfies Mission,
    }),
  );
  app.route("/api/tutor", tutorRoutes({ budgetClient }));

  // Sprints: misión "sprint_copilot"
  app.use(
    "/api/sprints/*",
    forjaBudgetGuard({
      client: budgetClient,
      missionFor: () => "sprint_copilot" satisfies Mission,
    }),
  );
  app.route("/api/sprints", sprintsRoutes({ budgetClient }));

  // Manus, puertas, telemetry: NO usan budget (no invocan LLM directo)
  app.route("/api/manus", manusRoutes());
  app.route("/api/puertas", puertasRoutes());
  app.route("/api/telemetry", telemetryRoutes());

  return app;
}

// -------- Solo arranca el server cuando se ejecuta directamente --------
const isMain = import.meta.url === `file://${process.argv[1]}`;
if (isMain) {
  const env = loadEnv({ strict: true });
  const port = env.PORT;
  const app = createApp();
  serve({ fetch: app.fetch, port }, (info) => {
    console.info(
      `[${SERVICE_NAME}] listening on http://0.0.0.0:${info.port} (env=${env.NODE_ENV})`,
    );
  });
}

export default createApp;

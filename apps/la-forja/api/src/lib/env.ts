/**
 * La Forja — Environment validation (Zod-typed).
 *
 * Sprint LA-FORJA-001 v3.2 — D1 no-SQL.
 * Doctrina: Regla Dura #4 (secretos en env vars únicamente, jamás en código).
 *
 * Required secrets (Railway runtime injection):
 *   - MANUS_API_KEY_GOOGLE   Manus account = Google (este hilo)
 *   - MANUS_API_KEY_APPLE    Manus account = Apple (secundario)
 *   - ANTHROPIC_API_KEY      Claude Opus 4.7 (tutor adaptativo)
 *   - OPENAI_API_KEY         GPT-5.5 Pro (co-piloto de sprints)
 *   - GEMINI_API_KEY         Gemini 3.1 Pro (RAG) + 2.5 Flash (clasificador)
 *   - SONAR_API_KEY          Perplexity (validación tiempo real magna ÚNICAMENTE)
 *   - SUPABASE_URL           Supabase del Monstruo
 *   - SUPABASE_SERVICE_KEY   Service role para RLS bypass server-side
 *
 * Optional (observability + runtime):
 *   - LANGFUSE_PUBLIC_KEY    Trazas LLM (post-D2)
 *   - LANGFUSE_SECRET_KEY    Trazas LLM (post-D2)
 *   - PORT                   Railway-injected (default 8080)
 *   - MANUS_API_BASE_URL     Override (default https://api.manus.ai)
 */

import { z } from "zod";

const EnvSchema = z.object({
  // Manus M2M Bridge (multi-cuenta)
  MANUS_API_KEY_GOOGLE: z.string().min(1, "MANUS_API_KEY_GOOGLE is required"),
  MANUS_API_KEY_APPLE: z.string().min(1, "MANUS_API_KEY_APPLE is required"),
  MANUS_API_BASE_URL: z.string().url().default("https://api.manus.ai"),

  // Modelos IA (Opción B confirmada — multi-modelo)
  ANTHROPIC_API_KEY: z.string().min(1, "ANTHROPIC_API_KEY is required"),
  OPENAI_API_KEY: z.string().min(1, "OPENAI_API_KEY is required"),
  GEMINI_API_KEY: z.string().min(1, "GEMINI_API_KEY is required"),
  SONAR_API_KEY: z.string().min(1, "SONAR_API_KEY is required"),

  // Datos
  SUPABASE_URL: z.string().url("SUPABASE_URL must be a valid URL"),
  SUPABASE_SERVICE_KEY: z.string().min(1, "SUPABASE_SERVICE_KEY is required"),

  // Observabilidad (opcional en D1, obligatorio post-D2)
  LANGFUSE_PUBLIC_KEY: z.string().optional(),
  LANGFUSE_SECRET_KEY: z.string().optional(),

  // Runtime
  PORT: z
    .string()
    .optional()
    .transform((v) => (v ? Number.parseInt(v, 10) : 8080))
    .pipe(z.number().int().positive().lt(65536)),
  NODE_ENV: z
    .enum(["development", "production", "test"])
    .default("production"),
});

export type Env = z.infer<typeof EnvSchema>;

let _cached: Env | null = null;

/**
 * Lazy validation — only fails at first access.
 * D1 no-SQL: en startup llamamos `loadEnv({ strict: false })` para permitir
 * /health sin todas las llaves; a partir de D2 usaremos `loadEnv({ strict: true })`.
 */
export function loadEnv(opts: { strict?: boolean } = {}): Env {
  if (_cached) {
    return _cached;
  }
  const { strict = true } = opts;

  if (!strict) {
    // Modo permisivo D1: solo PORT y NODE_ENV deben existir.
    const partial = z.object({
      PORT: EnvSchema.shape.PORT,
      NODE_ENV: EnvSchema.shape.NODE_ENV,
    });
    const parsed = partial.parse({
      PORT: process.env.PORT,
      NODE_ENV: process.env.NODE_ENV,
    });
    _cached = {
      MANUS_API_KEY_GOOGLE: process.env.MANUS_API_KEY_GOOGLE ?? "",
      MANUS_API_KEY_APPLE: process.env.MANUS_API_KEY_APPLE ?? "",
      MANUS_API_BASE_URL:
        process.env.MANUS_API_BASE_URL ?? "https://api.manus.ai",
      ANTHROPIC_API_KEY: process.env.ANTHROPIC_API_KEY ?? "",
      OPENAI_API_KEY: process.env.OPENAI_API_KEY ?? "",
      GEMINI_API_KEY: process.env.GEMINI_API_KEY ?? "",
      SONAR_API_KEY: process.env.SONAR_API_KEY ?? "",
      SUPABASE_URL: process.env.SUPABASE_URL ?? "https://placeholder.supabase.co",
      SUPABASE_SERVICE_KEY: process.env.SUPABASE_SERVICE_KEY ?? "",
      LANGFUSE_PUBLIC_KEY: process.env.LANGFUSE_PUBLIC_KEY,
      LANGFUSE_SECRET_KEY: process.env.LANGFUSE_SECRET_KEY,
      PORT: parsed.PORT,
      NODE_ENV: parsed.NODE_ENV,
    };
    return _cached;
  }

  const result = EnvSchema.safeParse(process.env);
  if (!result.success) {
    const issues = result.error.issues
      .map((i) => `  - ${i.path.join(".")}: ${i.message}`)
      .join("\n");
    throw new Error(
      `[la-forja:env] Environment validation failed:\n${issues}\n\n` +
        `Configure these secrets in Railway before starting the API.`,
    );
  }
  _cached = result.data;
  return _cached;
}

/** Reset cache — only for tests. */
export function _resetEnvCache(): void {
  _cached = null;
}

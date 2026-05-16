/**
 * La Forja — Environment validation (Zod-typed).
 *
 * Sprint LA-FORJA-001 v3.2 — D2 strict.
 * Doctrina: Regla Dura #4 (secretos en env vars únicamente, jamás en código).
 *
 * Required secrets (Railway runtime injection — verificados binariamente §8 SPEC):
 *   - MANUS_API_KEY_GOOGLE   Manus account = Google
 *   - MANUS_API_KEY_APPLE    Manus account = Apple
 *   - ANTHROPIC_API_KEY      Claude Opus 4.7 (tutor adaptativo, modo Adaptive obligatorio)
 *   - OPENAI_API_KEY         GPT-5.5 Pro (co-piloto sprints, /v1/responses)
 *   - GEMINI_API_KEY         Gemini 3.1 Pro (RAG) + 2.5 Flash (clasificador AC12)
 *   - SONAR_API_KEY          Perplexity Sonar Reasoning Pro (DSC-LF-004 única validación externa)
 *   - SUPABASE_URL           Supabase del Monstruo (LF-1 soberanía)
 *   - SUPABASE_SERVICE_KEY   Service role para RLS bypass server-side
 *   - LANGFUSE_PUBLIC_KEY    Trazas LLM con redactor PII (R10)
 *   - LANGFUSE_SECRET_KEY    Trazas LLM con redactor PII (R10)
 *
 * Required infra URLs (con default conocido binariamente, override permitido):
 *   - KERNEL_MONSTRUO_BASE_URL  default https://el-monstruo-kernel-production.up.railway.app
 *   - SIMULADOR_BASE_URL        default https://simulador-api-production.up.railway.app
 *   - MANUS_API_BASE_URL        default https://api.manus.ai
 *   - LANGFUSE_HOST             default https://cloud.langfuse.com
 *
 * D4 nuevos (no requeridos en D2):
 *   - GOOGLE_OAUTH_CLIENT_ID
 *   - GOOGLE_OAUTH_CLIENT_SECRET
 *
 * D2 stub auth:
 *   - DEV_USER_ROLE             default "user" (rol más restrictivo; auth real es D4)
 *
 * Hardening D2.5 (audit adversarial Perplexity 15-may-2026):
 *   - H-1: default DEV_USER_ROLE cambiado de "t1_alfredo" a "user" (rol más restrictivo)
 *          + auth.ts agrega guard NODE_ENV=production que rechaza con HTTP 503
 *   - H-5: loadEnv({strict:false}) ahora exige NODE_ENV=test (fail-loud doctrina §4)
 */

import { z } from "zod";

const EnvSchema = z.object({
  // Manus M2M Bridge (multi-cuenta) — verificados binariamente
  MANUS_API_KEY_GOOGLE: z.string().min(1, "MANUS_API_KEY_GOOGLE is required"),
  MANUS_API_KEY_APPLE: z.string().min(1, "MANUS_API_KEY_APPLE is required"),
  MANUS_API_BASE_URL: z.string().url().default("https://api.manus.ai"),

  // Modelos IA — pricing magna 15 mayo 2026
  ANTHROPIC_API_KEY: z.string().min(1, "ANTHROPIC_API_KEY is required"),
  OPENAI_API_KEY: z.string().min(1, "OPENAI_API_KEY is required"),
  GEMINI_API_KEY: z.string().min(1, "GEMINI_API_KEY is required"),
  SONAR_API_KEY: z.string().min(1, "SONAR_API_KEY is required"),

  // Datos — Supabase del Monstruo (LF-1)
  SUPABASE_URL: z.string().url("SUPABASE_URL must be a valid URL"),
  SUPABASE_SERVICE_KEY: z.string().min(1, "SUPABASE_SERVICE_KEY is required"),

  // Observabilidad — obligatorio D2+ con redactor PII (R10)
  LANGFUSE_PUBLIC_KEY: z.string().min(1, "LANGFUSE_PUBLIC_KEY is required"),
  LANGFUSE_SECRET_KEY: z.string().min(1, "LANGFUSE_SECRET_KEY is required"),
  LANGFUSE_HOST: z.string().url().default("https://cloud.langfuse.com"),

  // Infra del Monstruo — URLs con default conocidos binariamente
  KERNEL_MONSTRUO_BASE_URL: z
    .string()
    .url()
    .default("https://el-monstruo-kernel-production.up.railway.app"),
  SIMULADOR_BASE_URL: z
    .string()
    .url()
    .default("https://simulador-api-production.up.railway.app"),

  // D2 stub auth — auth real es D4 (Google OAuth + Supabase Auth)
  // Hardening D2.5 H-1: default cambiado de "t1_alfredo" a "user" (rol restrictivo)
  DEV_USER_ROLE: z
    .enum(["t1_alfredo", "t1_padre", "user"])
    .default("user"),

  // Runtime
  PORT: z
    .string()
    .optional()
    .transform((v) => (v ? Number.parseInt(v, 10) : 8080))
    .pipe(z.number().int().positive().lt(65536)),
  NODE_ENV: z.enum(["development", "production", "test"]).default("production"),
});

export type Env = z.infer<typeof EnvSchema>;

/**
 * Interface User canónica (estable cross D2-D4-D5+).
 *
 * En D2: stub middleware lee header `x-user-id` y resuelve role desde `DEV_USER_ROLE`.
 * En D4: middleware se reemplaza por validación JWT Supabase Auth + Google OAuth.
 * El interface NO cambia; las rutas que usan `c.get('user')` no se tocan.
 *
 * Roles canónicos (LF-9 modelo de contribución):
 *   - t1_alfredo: dueño del Monstruo, acceso total
 *   - t1_padre:   Cliente Cero, sin acceso a puerta cowork_local (R5)
 *   - user:       futuros usuarios, scope reducido
 */
export type UserRole = "t1_alfredo" | "t1_padre" | "user";

export interface User {
  id: string;
  email: string;
  role: UserRole;
}

let _cached: Env | null = null;

/**
 * Lazy validation — only fails at first access.
 * D2: por default strict=true. Modo permisivo solo para `/health` boot-time check
 * y para tests aislados que mockean process.env.
 */
export function loadEnv(opts: { strict?: boolean } = {}): Env {
  if (_cached) {
    return _cached;
  }
  const { strict = true } = opts;

  if (!strict) {
    // Modo permisivo: solo PORT y NODE_ENV deben existir. Usado en /health boot y tests.
    // Hardening D2.5 H-5: rechaza permisivo en NODE_ENV=production (fail-loud doctrina §4).
    const partial = z.object({
      PORT: EnvSchema.shape.PORT,
      NODE_ENV: EnvSchema.shape.NODE_ENV,
    });
    const parsed = partial.parse({
      PORT: process.env.PORT,
      NODE_ENV: process.env.NODE_ENV,
    });
    if (parsed.NODE_ENV === "production") {
      throw new Error(
        "[la-forja:env_load_permissive_blocked_in_production] " +
          "loadEnv({strict:false}) is forbidden when NODE_ENV=production. " +
          "Use strict mode (default) so missing secrets fail loud.",
      );
    }
    _cached = {
      MANUS_API_KEY_GOOGLE: process.env.MANUS_API_KEY_GOOGLE ?? "",
      MANUS_API_KEY_APPLE: process.env.MANUS_API_KEY_APPLE ?? "",
      MANUS_API_BASE_URL:
        process.env.MANUS_API_BASE_URL ?? "https://api.manus.ai",
      ANTHROPIC_API_KEY: process.env.ANTHROPIC_API_KEY ?? "",
      OPENAI_API_KEY: process.env.OPENAI_API_KEY ?? "",
      GEMINI_API_KEY: process.env.GEMINI_API_KEY ?? "",
      SONAR_API_KEY: process.env.SONAR_API_KEY ?? "",
      SUPABASE_URL:
        process.env.SUPABASE_URL ?? "https://placeholder.supabase.co",
      SUPABASE_SERVICE_KEY: process.env.SUPABASE_SERVICE_KEY ?? "",
      LANGFUSE_PUBLIC_KEY: process.env.LANGFUSE_PUBLIC_KEY ?? "",
      LANGFUSE_SECRET_KEY: process.env.LANGFUSE_SECRET_KEY ?? "",
      LANGFUSE_HOST: process.env.LANGFUSE_HOST ?? "https://cloud.langfuse.com",
      KERNEL_MONSTRUO_BASE_URL:
        process.env.KERNEL_MONSTRUO_BASE_URL ??
        "https://el-monstruo-kernel-production.up.railway.app",
      SIMULADOR_BASE_URL:
        process.env.SIMULADOR_BASE_URL ??
        "https://simulador-api-production.up.railway.app",
      DEV_USER_ROLE:
        (process.env.DEV_USER_ROLE as UserRole | undefined) ?? "user",
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
      `[la-forja:env_load_strict_failed] Environment validation failed:\n${issues}\n\n` +
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

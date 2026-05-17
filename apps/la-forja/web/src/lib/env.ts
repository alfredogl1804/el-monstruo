/**
 * La Forja — frontend env validator (Zod fail-loud).
 *
 * Sprint LA-FORJA-001 D3.0.
 * Doctrina: Regla Dura #6 (cero secrets en plaintext, fail-loud lookup).
 * Paridad: `apps/la-forja/api/src/lib/env.ts` (mismo patrón).
 *
 * Este módulo se importa solo desde Server Components o desde el cliente
 * con vars `NEXT_PUBLIC_*`. Cero secrets aquí: el frontend NUNCA habla con
 * Supabase, LLM ni Stripe directo (LF-1).
 */
import { z } from "zod";

const ForjaWebEnvSchema = z.object({
  NEXT_PUBLIC_API_URL: z
    .string()
    .url({ message: "NEXT_PUBLIC_API_URL debe ser una URL válida" }),
  NODE_ENV: z
    .enum(["development", "production", "test"])
    .default("development"),
});

export type ForjaWebEnv = z.infer<typeof ForjaWebEnvSchema>;

/**
 * Valida y retorna las env vars del frontend.
 * Si falta una var en producción, lanza fail-loud.
 *
 * @param strict si true, siempre falla con error claro (default).
 *               Solo `false` en tests con valores placeholder.
 */
export function loadForjaWebEnv(
  options: { strict?: boolean } = {},
): ForjaWebEnv {
  const strict = options.strict ?? true;
  const raw = {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NODE_ENV: process.env.NODE_ENV,
  };

  const parsed = ForjaWebEnvSchema.safeParse(raw);
  if (!parsed.success) {
    if (strict) {
      const issues = parsed.error.issues
        .map((i) => `${i.path.join(".")}: ${i.message}`)
        .join("; ");
      throw new Error(
        `[la-forja:web_env_load_strict_failed] ${issues}`,
      );
    }
    // strict:false sólo permitido en tests
    if (process.env.NODE_ENV === "production") {
      throw new Error(
        "[la-forja:web_env_load_permissive_blocked_in_production]",
      );
    }
    return {
      NEXT_PUBLIC_API_URL:
        raw.NEXT_PUBLIC_API_URL ?? "http://localhost:3000",
      NODE_ENV: (raw.NODE_ENV as ForjaWebEnv["NODE_ENV"]) ?? "development",
    };
  }
  return parsed.data;
}

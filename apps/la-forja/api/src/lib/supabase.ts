/**
 * La Forja — Supabase server-side client.
 *
 * Sprint LA-FORJA-001 v3.2 — D2.1.
 * Doctrina: LF-1 (soberanía sobre infra del Monstruo) + LF-5 (RLS desde nacimiento).
 *
 * Service-role client (RLS bypass) — server only, never expose to client.
 * Usado por backend Hono para queries que requieren atravesar RLS:
 *   - Lookups de identidad en `forja_profiles` (middleware auth stub D2, JWT D4)
 *   - Updates atómicos de `forja_budget` (LF-RATE-LIMIT-001)
 *   - Inserts en `forja_telemetry` (LF-TELEMETRY-MANDATORY-001)
 *   - Persistencia de `forja_sprints` y `forja_threads`/`forja_messages`
 *
 * Las tablas referenciadas se crean en D5 (9 migraciones 0036-0044).
 * En D2: el cliente está disponible pero los queries específicos vendrán en D2.3+.
 */

import { createClient, type SupabaseClient } from "@supabase/supabase-js";
import { loadEnv } from "./env.js";

let _cached: SupabaseClient | null = null;

/**
 * Lazy singleton. Se construye en primer acceso para no romper tests
 * que mockean process.env antes del import.
 */
export function getSupabase(): SupabaseClient {
  if (_cached) {
    return _cached;
  }
  const env = loadEnv();
  _cached = createClient(env.SUPABASE_URL, env.SUPABASE_SERVICE_KEY, {
    auth: {
      // Server-side only: nunca persistimos sesión en filesystem
      persistSession: false,
      autoRefreshToken: false,
      detectSessionInUrl: false,
    },
    db: {
      schema: "public",
    },
    global: {
      headers: {
        // Identidad explícita para auditoría en logs Supabase
        "x-monstruo-app": "la-forja",
        "x-monstruo-component": "api-server",
      },
    },
  });
  return _cached;
}

/** Reset singleton — only for tests. */
export function _resetSupabaseCache(): void {
  _cached = null;
}

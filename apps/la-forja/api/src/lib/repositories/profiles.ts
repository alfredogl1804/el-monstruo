/**
 * La Forja — Repository: forja_profiles.
 *
 * Sprint LA-FORJA-001 v3.2 — D5.2.
 * Doctrina: DSC-LF-009 (auth canónica) + DSC-LF-010 (RLS migrations).
 *
 * Responsabilidades binarias:
 *   1. Resolver UUID `forja_profiles.id` a partir del `User` que el middleware
 *      auth (D2 stub o D4 OAuth) coloca en `c.var.user`.
 *   2. En modo D4 (Google OAuth real): `User.id` proviene de `claims.sub` que
 *      es el `google_sub`. Lookup por `google_sub` y crear-si-no-existe.
 *   3. En modo D2 stub (NODE_ENV=development|test): `User.id` es un UUID
 *      sintético del header `x-user-id`. Tratarlo como `google_sub` ficticio
 *      `dev-stub:<uuid>` para mantener compat sin chocar con perfiles reales.
 *
 * Diseño binario:
 *   - Operación atómica: INSERT ... ON CONFLICT (google_sub) DO UPDATE
 *     ... last_seen_at = NOW() RETURNING id.
 *   - Cache in-memory por proceso (Map<google_sub, profile_id>) para evitar
 *     un round-trip por cada turn del tutor. La cache se invalida solo en
 *     reset de proceso (Railway redeploy). En D5.3+ se puede agregar TTL.
 */

import { getSupabase } from "../supabase";
import type { User } from "../env";

/** Cache local proceso → google_sub → profile_id. Reset solo en redeploy. */
const PROFILE_ID_CACHE = new Map<string, string>();

/**
 * Convierte el `User.id` que entrega el middleware auth a un `google_sub`
 * válido para la columna `forja_profiles.google_sub` (TEXT NOT NULL UNIQUE).
 *
 * En NODE_ENV=production con D4 forjaAuthGoogle, `User.id` ya es el
 * `claims.sub` = google_sub auténtico de Google. Se usa tal cual.
 *
 * En NODE_ENV=development|test con D2 forjaAuthStub, `User.id` es un UUID
 * sintético del header x-user-id. Se prefija `dev-stub:` para que NUNCA
 * pueda chocar accidentalmente con un sub real de Google (que no contiene `:`).
 */
function userToGoogleSub(user: User, nodeEnv: string): string {
  if (nodeEnv === "production") {
    return user.id;
  }
  return `dev-stub:${user.id}`;
}

/**
 * Resuelve el `forja_profiles.id` (UUID) para el `User` autenticado.
 *
 * Si la fila existe → UPDATE last_seen_at = NOW() y retorna id.
 * Si no existe     → INSERT con role/email/display_name del User y retorna id.
 *
 * Tiene cache para evitar round-trips repetidos (un mismo usuario hace
 * múltiples turnos del tutor en una sesión; la cache reduce 90%+ de hits).
 */
export async function resolveProfileId(
  user: User,
  nodeEnv: string,
): Promise<string> {
  const googleSub = userToGoogleSub(user, nodeEnv);

  const cached = PROFILE_ID_CACHE.get(googleSub);
  if (cached) {
    return cached;
  }

  const supabase = getSupabase();

  // UPSERT idempotente con ON CONFLICT (google_sub).
  // El service-role bypassa RLS, lo cual es correcto: el server inserta
  // y actualiza identidades en nombre del usuario validado por JWT.
  const { data, error } = await supabase
    .from("forja_profiles")
    .upsert(
      {
        google_sub: googleSub,
        email: user.email,
        display_name: user.email.split("@")[0] ?? "user",
        role: user.role,
        last_seen_at: new Date().toISOString(),
      },
      { onConflict: "google_sub", ignoreDuplicates: false },
    )
    .select("id")
    .single();

  if (error || !data) {
    throw new Error(
      `[la-forja:profiles_upsert_failed] google_sub=${googleSub} ` +
        `error=${error?.message ?? "no row returned"}`,
    );
  }

  PROFILE_ID_CACHE.set(googleSub, data.id);
  return data.id;
}

/**
 * Reset de cache. Solo para tests entre describe blocks.
 */
export function _resetProfileIdCache(): void {
  PROFILE_ID_CACHE.clear();
}

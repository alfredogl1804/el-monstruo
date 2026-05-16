/**
 * La Forja — helpers cookie del tour onboarding.
 *
 * Sprint LA-FORJA-001 D3.1.
 *
 * Persistencia ligera de "ya viste el tour". No contiene PII ni
 * estado de sesión. Es un timestamp UTC en una cookie no-HttpOnly
 * para que tanto Server Components como Client Components puedan
 * leerla.
 *
 * Cookie name: `forja_tour_completed_at`
 * Cookie value: ISO-8601 UTC timestamp (ej: `2026-05-16T18:30:00.000Z`)
 * Path: `/`
 * Max-Age: 1 año (suficiente para que un usuario que volvió tras
 *          meses sienta que la app lo recuerda).
 *
 * Esta cookie es escrita desde el cliente al terminar o saltar el
 * tour. NO la setea el backend Hono — eso queda para D3.x cuando
 * exista user state en BD.
 */

export const FORJA_TOUR_COOKIE_NAME = "forja_tour_completed_at";
const ONE_YEAR_SECONDS = 60 * 60 * 24 * 365;

/**
 * Lee la cookie del documento. Devuelve `null` si no existe o si
 * estamos en SSR (sin `document`).
 */
export function readForjaTourCookie(documentRef?: Document): string | null {
  const doc = documentRef ?? (typeof document !== "undefined" ? document : null);
  if (!doc) return null;
  const all = doc.cookie ? doc.cookie.split("; ") : [];
  for (const entry of all) {
    const eq = entry.indexOf("=");
    if (eq < 0) continue;
    const key = entry.slice(0, eq);
    if (key === FORJA_TOUR_COOKIE_NAME) {
      const raw = decodeURIComponent(entry.slice(eq + 1));
      return raw.length > 0 ? raw : null;
    }
  }
  return null;
}

/**
 * Escribe la cookie con el timestamp UTC actual (o uno provisto).
 * Devuelve el valor escrito para verificación en tests.
 */
export function writeForjaTourCookie(
  options: { now?: Date; documentRef?: Document } = {},
): string {
  const doc =
    options.documentRef ?? (typeof document !== "undefined" ? document : null);
  const ts = (options.now ?? new Date()).toISOString();
  if (!doc) return ts;
  doc.cookie = `${FORJA_TOUR_COOKIE_NAME}=${encodeURIComponent(
    ts,
  )}; path=/; max-age=${ONE_YEAR_SECONDS}; samesite=lax`;
  return ts;
}

/**
 * Borra la cookie. Útil para "ver tour de nuevo" o testing.
 */
export function clearForjaTourCookie(documentRef?: Document): void {
  const doc =
    documentRef ?? (typeof document !== "undefined" ? document : null);
  if (!doc) return;
  doc.cookie = `${FORJA_TOUR_COOKIE_NAME}=; path=/; max-age=0; samesite=lax`;
}

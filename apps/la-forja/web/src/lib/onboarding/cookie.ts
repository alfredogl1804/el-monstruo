/**
 * La Forja - helpers cookie del tour onboarding.
 *
 * Sprint LA-FORJA-001 D3.1 + hardening Perplexity F-D3.1-03 y -09.
 *
 * Persistencia ligera de "ya viste el tour". No contiene PII ni
 * estado de sesion. Es un timestamp UTC en una cookie no-HttpOnly
 * para que tanto Server Components como Client Components puedan
 * leerla.
 *
 * Cookie name: forja_tour_completed_at
 * Cookie value: ISO-8601 UTC timestamp (ej: 2026-05-16T18:30:00.000Z)
 * Path: /
 * Max-Age: 1 ano (suficiente para que un usuario que volvio tras
 *          meses sienta que la app lo recuerda).
 * SameSite: lax
 * Secure: solo si el documento corre en https (preserva tests
 *         locales en http://localhost mientras blinda produccion).
 *
 * Esta cookie es escrita desde el cliente al terminar o saltar el
 * tour. NO la setea el backend Hono - eso queda para D3.x cuando
 * exista user state en BD.
 *
 * Hardening aplicado:
 *   F-D3.1-03: Secure flag en HTTPS para evitar overwrite en
 *              downgrade HTTP malicioso.
 *   F-D3.1-09: split tolerante a serializaciones que omiten el
 *              espacio entre cookies. La regex es /;\s* / para
 *              cubrir tanto el separador estandar "; " como el
 *              degenerado ";".
 */

export const FORJA_TOUR_COOKIE_NAME = "forja_tour_completed_at";
const ONE_YEAR_SECONDS = 60 * 60 * 24 * 365;

/**
 * Determina si debe agregarse el atributo Secure a la cookie.
 * Acepta documentRef inyectado para tests (no toca location real).
 */
function shouldUseSecure(documentRef: Document | null): boolean {
  if (typeof window === "undefined") return false;
  const loc =
    documentRef?.defaultView?.location ?? window.location;
  return loc?.protocol === "https:";
}

/**
 * Lee la cookie del documento. Devuelve null si no existe o si
 * estamos en SSR (sin document).
 */
export function readForjaTourCookie(documentRef?: Document): string | null {
  const doc = documentRef ?? (typeof document !== "undefined" ? document : null);
  if (!doc) return null;
  const all = doc.cookie ? doc.cookie.split(/;\s*/) : [];
  for (const entry of all) {
    const eq = entry.indexOf("=");
    if (eq < 0) continue;
    const key = entry.slice(0, eq);
    if (key === FORJA_TOUR_COOKIE_NAME) {
      try {
        const raw = decodeURIComponent(entry.slice(eq + 1));
        return raw.length > 0 ? raw : null;
      } catch {
        return null;
      }
    }
  }
  return null;
}

/**
 * Escribe la cookie con el timestamp UTC actual (o uno provisto).
 * Devuelve el valor escrito para verificacion en tests.
 */
export function writeForjaTourCookie(
  options: { now?: Date; documentRef?: Document } = {},
): string {
  const doc =
    options.documentRef ?? (typeof document !== "undefined" ? document : null);
  const ts = (options.now ?? new Date()).toISOString();
  if (!doc) return ts;
  const secureAttr = shouldUseSecure(doc) ? "; secure" : "";
  doc.cookie = `${FORJA_TOUR_COOKIE_NAME}=${encodeURIComponent(
    ts,
  )}; path=/; max-age=${ONE_YEAR_SECONDS}; samesite=lax${secureAttr}`;
  return ts;
}

/**
 * Borra la cookie. Util para "ver tour de nuevo" o testing.
 */
export function clearForjaTourCookie(documentRef?: Document): void {
  const doc =
    documentRef ?? (typeof document !== "undefined" ? document : null);
  if (!doc) return;
  const secureAttr = shouldUseSecure(doc) ? "; secure" : "";
  doc.cookie = `${FORJA_TOUR_COOKIE_NAME}=; path=/; max-age=0; samesite=lax${secureAttr}`;
}

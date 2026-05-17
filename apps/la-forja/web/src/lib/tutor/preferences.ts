/**
 * La Forja — preferencias persistentes del tutor en el cliente.
 *
 * Sprint LA-FORJA-001 D3.3.
 *
 * Storage: localStorage del navegador, clave `la-forja:tutor:require-validation`.
 * Default: `false` (magna desactivada — ahorra tokens al usuario).
 *
 * Doctrina:
 *   - SSR-safe: todas las funciones devuelven default cuando `window` no está
 *     definido (Server Component / build estático).
 *   - Fail-soft: si el localStorage está bloqueado (modo incógnito,
 *     cookies disabled, quota exceeded), las funciones devuelven default
 *     y registran un namespace `[la-forja:tutor_pref_*]` en console.warn.
 *   - Telemetría: emitir `tutorTelemetry({ event, value })` en el caller
 *     cuando aplique. Este módulo es solo I/O.
 */

export const FORJA_TUTOR_PREF_KEYS = {
  requireValidation: "la-forja:tutor:require-validation",
} as const;

const DEFAULTS = {
  requireValidation: false,
} as const;

/**
 * Lee la preferencia `requireValidation` del localStorage.
 * Retorna `false` cuando no hay window, no hay valor previo, o el valor
 * guardado es inválido.
 */
export function loadRequireValidation(): boolean {
  if (typeof window === "undefined") {
    return DEFAULTS.requireValidation;
  }
  try {
    const raw = window.localStorage.getItem(
      FORJA_TUTOR_PREF_KEYS.requireValidation,
    );
    if (raw === null) return DEFAULTS.requireValidation;
    if (raw === "true") return true;
    if (raw === "false") return false;
    // Valor corrupto: log fail-loud namespace y devolver default.
    console.warn(
      `[la-forja:tutor_pref_corrupt] requireValidation raw="${raw}" → ${DEFAULTS.requireValidation}`,
    );
    return DEFAULTS.requireValidation;
  } catch (err) {
    console.warn(
      `[la-forja:tutor_pref_read_failed] ${err instanceof Error ? err.message : String(err)}`,
    );
    return DEFAULTS.requireValidation;
  }
}

/**
 * Persiste la preferencia `requireValidation` en localStorage.
 * No-op cuando no hay window. Fail-soft cuando el storage está bloqueado.
 */
export function saveRequireValidation(value: boolean): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(
      FORJA_TUTOR_PREF_KEYS.requireValidation,
      value ? "true" : "false",
    );
  } catch (err) {
    console.warn(
      `[la-forja:tutor_pref_write_failed] ${err instanceof Error ? err.message : String(err)}`,
    );
  }
}

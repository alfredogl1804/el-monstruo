/**
 * La Forja — Espejo del contract canónico de headers SSE (R-D3.2-02).
 *
 * Sprint LA-FORJA-001 D3.2.1.
 * Doctrina: §7 _DOCTRINA_D3.md (DSC-LF-005).
 *
 * Este módulo es ESPEJO BINARIO de `apps/la-forja/api/src/shared/headers.ts`.
 * No podemos importar cross-workspace, así que ambos lados publican el mismo
 * objeto y un test de contrato (`Chat.contract.test.ts`) compara byte por byte
 * vía snapshot reading del archivo backend con `fs` para garantizar paridad.
 *
 * Si tocas un nombre aquí, tocas el del backend. Si fallan los tests, es drift.
 */

export const FORJA_TUTOR_HEADER_KEYS = {
  protocolVersion: "x-vercel-ai-ui-message-stream",
  intent: "x-la-forja-intent",
  confidence: "x-la-forja-confidence",
  model: "x-la-forja-model",
  citationsB64: "x-la-forja-citations-b64",
  validationModel: "x-la-forja-validation-model",
} as const;

export const FORJA_TUTOR_HEADER_NAMES = Object.values(
  FORJA_TUTOR_HEADER_KEYS,
) as readonly string[];

/**
 * Decodifica el header `x-la-forja-citations-b64` (base64url JSON) a array de
 * URLs. Retorna [] si el header está ausente o malformado.
 */
export function decodeCitationsHeader(headerValue: string | null): string[] {
  if (!headerValue) return [];
  try {
    // base64url → base64 estándar
    const padded = headerValue
      .replace(/-/g, "+")
      .replace(/_/g, "/")
      .padEnd(headerValue.length + ((4 - (headerValue.length % 4)) % 4), "=");
    const json =
      typeof atob === "function"
        ? decodeURIComponent(escape(atob(padded)))
        : Buffer.from(padded, "base64").toString("utf-8");
    const parsed = JSON.parse(json);
    if (!Array.isArray(parsed)) return [];
    return parsed.filter((c): c is string => typeof c === "string");
  } catch {
    return [];
  }
}

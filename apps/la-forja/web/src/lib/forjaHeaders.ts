/**
 * La Forja — Espejo del contract canónico de headers SSE (R-D3.2-02 + R-D3.2.1-02).
 *
 * Sprint LA-FORJA-001 D3.2.2.
 * Doctrina: §7 _DOCTRINA_D3.md (DSC-LF-005).
 *
 * Este módulo es ESPEJO BINARIO de `apps/la-forja/api/src/shared/headers.ts`.
 * No podemos importar cross-workspace, así que ambos lados publican el mismo
 * objeto y un test de contrato (`forjaHeaders.contract.test.ts`) compara con
 * el JSON canonico (`forjaHeaders.contract.json`) generado desde el backend
 * por `pnpm --filter la-forja-api contract:headers`.
 *
 * Si tocas un nombre aquí, tocas el del backend Y regeneras el JSON. Si
 * fallan los tests de contrato, es drift binario.
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
 * Cap de bytes para el payload de citations antes del encode base64url
 * (espejo de `FORJA_CITATIONS_HEADER_MAX_BYTES` del backend, R-D3.2.1-02).
 */
export const FORJA_CITATIONS_HEADER_MAX_BYTES = 2048;

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

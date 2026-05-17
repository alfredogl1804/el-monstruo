/**
 * La Forja — Contract canónico de headers SSE backend ↔ frontend (R-D3.2-02).
 *
 * Sprint LA-FORJA-001 v3.2 — D3.2.1 hardening adversarial (Perplexity).
 * Doctrina: §7 _DOCTRINA_D3.md (DSC-LF-005) + Regla Dura #4 Brand Engine.
 *
 * Esta es la fuente única de verdad para los nombres de headers que el
 * endpoint `/api/tutor/chat` emite en su Response SSE. El frontend
 * (`Chat.tsx`) DEBE importar este módulo para mantener el contrato binario,
 * evitando drift como el detectado en R-D3.1-03.
 *
 * Cualquier cambio de nombre o adición de header DEBE hacerse aquí primero;
 * los tests `routes.test.ts` y `Chat.test.ts` consumen este módulo y rompen
 * binariamente si el contrato cambia sin propagación.
 */

export const FORJA_TUTOR_HEADER_KEYS = {
  /** UI Message Stream protocol version del Vercel AI SDK 6. */
  protocolVersion: "x-vercel-ai-ui-message-stream",
  /** Intent del clasificador AC-12 (Gemini Flash). */
  intent: "x-la-forja-intent",
  /** Confidence del clasificador (4 decimales). */
  confidence: "x-la-forja-confidence",
  /** Modelo del tutor (Claude Opus 4.7 Adaptive). */
  model: "x-la-forja-model",
  /**
   * Citations de Sonar Reasoning Pro (magna_validation), serializadas como
   * `base64url(JSON.stringify(citations))` para soportar UTF-8 sin romper
   * RFC 7230 y limitadas a FORJA_CITATIONS_HEADER_MAX_BYTES (F-D3.2-03/04).
   */
  citationsB64: "x-la-forja-citations-b64",
  /** Modelo de la capa de validación (Sonar Reasoning Pro). */
  validationModel: "x-la-forja-validation-model",
} as const;

/**
 * Cap de bytes para el payload de citations antes del encode base64url.
 * Cloud Run / Hono soportan ~8KB total de headers; reservamos 2KB para
 * citations y dejamos margen al resto.
 */
export const FORJA_CITATIONS_HEADER_MAX_BYTES = 2048;

/**
 * Lista canónica de headers que el frontend DEBE consumir del Response SSE.
 * Útil para tests de contrato (R-D3.2-02).
 */
export const FORJA_TUTOR_HEADER_NAMES = Object.values(
  FORJA_TUTOR_HEADER_KEYS,
) as readonly string[];

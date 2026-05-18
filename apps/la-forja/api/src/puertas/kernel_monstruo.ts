/**
 * La Forja — Puerta `kernel_monstruo`.
 *
 * Sprint LA-FORJA-001 v3.2 — D2.4.
 * Doctrina: §2.5 + AC6 SPEC v3.2.
 *
 * Invoca módulos del kernel del Monstruo vía API REST que el kernel expone
 * en Railway (puerto 8080 según `python-app:8080`).
 *
 *   Base URL canónica:
 *     https://el-monstruo-kernel-production.up.railway.app
 *   Sobreescribible vía env KERNEL_MONSTRUO_BASE_URL.
 *
 * Endpoints invocables ejemplo:
 *   POST /sop/query           → SOP queries
 *   POST /epia/record         → EPIA event record
 *   POST /maoc/orchestrate    → MAOC orchestration
 *
 * En D2: thin REST wrapper sin schema discovery (cada endpoint se contractea
 * en su ruta Hono. La puerta solo proxya HTTP).
 */

import { loadEnv } from "../lib/env.js";

export interface PuertaKernelInput {
  /** Path relativo del endpoint (e.g. "/sop/query") */
  endpoint: string;
  /** Payload JSON del request */
  body: unknown;
  /** Override del baseURL (tests/dev) */
  baseUrl?: string;
  /** Override del fetch (tests deterministas) */
  fetchImpl?: typeof fetch;
  /** Headers extras (X-Request-Id, etc) */
  headers?: Record<string, string>;
}

export interface PuertaKernelOutput {
  status: number;
  data: unknown;
  durationMs: number;
}

export async function invokeKernelMonstruo(
  input: PuertaKernelInput,
): Promise<PuertaKernelOutput> {
  const env = loadEnv();
  const base = (input.baseUrl ?? env.KERNEL_MONSTRUO_BASE_URL).replace(/\/$/, "");
  if (!input.endpoint.startsWith("/")) {
    throw new Error(
      `[la-forja:puerta_kernel_invalid_endpoint] endpoint must start with "/", got: ${input.endpoint}`,
    );
  }
  const url = `${base}${input.endpoint}`;
  const fetchImpl = input.fetchImpl ?? fetch;

  const startedAt = Date.now();
  const res = await fetchImpl(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(input.headers ?? {}),
    },
    body: JSON.stringify(input.body),
  });
  const durationMs = Date.now() - startedAt;

  if (!res.ok) {
    const bodyText = await res.text().catch(() => "");
    throw new Error(
      `[la-forja:puerta_kernel_http_failed] ${res.status} ${res.statusText} ` +
        `url=${url} body=${bodyText.slice(0, 200)}`,
    );
  }

  const data: unknown = await res.json();
  return { status: res.status, data, durationMs };
}

/**
 * La Forja — cliente API tipado contra backend Hono.
 *
 * Sprint LA-FORJA-001 D3.0.
 * Doctrina: LF-1 (toda data viaja por backend, frontend nunca habla con
 * Supabase/LLM directo) + Brand Engine (errores con identidad).
 *
 * Este cliente se usa desde Server Components y Client Components vía
 * fetch nativo. En D3.2 se agregará el flow de streaming SSE para
 * `/api/tutor/chat` con `useChat` de `@ai-sdk/react`.
 */
import { loadForjaWebEnv } from "./env";

export class ForjaApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly body: unknown,
    public readonly requestId: string,
  ) {
    super(
      `[la-forja:web_api_request_failed] status=${status} requestId=${requestId}`,
    );
    this.name = "ForjaApiError";
  }
}

/**
 * Shape exacta de la respuesta `GET /health` del backend Hono
 * (`apps/la-forja/api/src/index.ts:86`).
 */
export interface ForjaHealthResponse {
  status: "ok";
  service: string;
  version: string;
  timestamp: string;
}

export interface ForjaApiClient {
  health(): Promise<ForjaHealthResponse>;
}

/**
 * Construye un cliente API contra el backend Hono.
 * Si `apiUrl` no se pasa, lee de `NEXT_PUBLIC_API_URL`.
 */
export function buildForjaApi(opts: { apiUrl?: string } = {}): ForjaApiClient {
  const baseUrl = opts.apiUrl ?? loadForjaWebEnv().NEXT_PUBLIC_API_URL;

  // F-D3.0-06: timeout SSR (Hono + Cloud Run).
  // 8 segundos cubre cold start + p99 sin esperar el timeout externo.
  const REQUEST_TIMEOUT_MS = 8_000;

  async function request<T>(
    path: string,
    init?: RequestInit,
  ): Promise<T> {
    const url = new URL(path, baseUrl);
    const requestId =
      typeof crypto !== "undefined" && "randomUUID" in crypto
        ? crypto.randomUUID()
        : Math.random().toString(36).slice(2);

    // F-D3.0-05: usar `new Headers(init?.headers)` preserva instancias
    // `Headers` y `string[][]` además de plain objects.
    const headers = new Headers(init?.headers);
    headers.set("content-type", "application/json");
    headers.set("x-request-id", requestId);

    const controller = new AbortController();
    const externalSignal = init?.signal;
    const onExternalAbort = () => controller.abort(externalSignal?.reason);
    if (externalSignal) {
      if (externalSignal.aborted) controller.abort(externalSignal.reason);
      else externalSignal.addEventListener("abort", onExternalAbort, { once: true });
    }
    const timeoutId = setTimeout(
      () =>
        controller.abort(
          new ForjaApiError(0, "timeout", requestId),
        ),
      REQUEST_TIMEOUT_MS,
    );

    try {
      const res = await fetch(url, {
        ...init,
        headers,
        signal: controller.signal,
      });
      if (!res.ok) {
        let body: unknown = null;
        try {
          body = await res.json();
        } catch {
          body = await res.text().catch(() => null);
        }
        throw new ForjaApiError(res.status, body, requestId);
      }
      return (await res.json()) as T;
    } finally {
      clearTimeout(timeoutId);
      if (externalSignal)
        externalSignal.removeEventListener("abort", onExternalAbort);
    }
  }

  return {
    async health() {
      return request<ForjaHealthResponse>("/health");
    },
  };
}

/**
 * La Forja — Puerta `simulador`.
 *
 * Sprint LA-FORJA-001 v3.2 — D2.4.
 * Doctrina: §2.5 + AC7 SPEC v3.2.
 *
 * Invoca al motor Simulador externo:
 *   https://simulador-api-production.up.railway.app
 * Healthcheck verificado HTTP 200 v5.2.1 antes de la firma del SPEC v3.2.
 *
 * Crea simulación cuando el usuario pregunta "¿qué pasaría si...?". Retorna
 * `simulation_id` para que el frontend (D3) consulte estado y resultados.
 */

export const SIMULADOR_BASE_URL =
  "https://simulador-api-production.up.railway.app";

export interface PuertaSimuladorInput {
  /** Descripción del escenario en lenguaje natural */
  scenario: string;
  /** Variables del escenario (estructura libre por dominio) */
  variables?: Record<string, unknown>;
  /** Cantidad de iteraciones Monte Carlo (default motor: 1000) */
  iterations?: number;
  /** Override del baseURL (tests) */
  baseUrl?: string;
  /** Override del fetch (tests deterministas) */
  fetchImpl?: typeof fetch;
}

export interface PuertaSimuladorOutput {
  simulationId: string;
  status: string;
  raw: unknown;
}

export async function invokeSimulador(
  input: PuertaSimuladorInput,
): Promise<PuertaSimuladorOutput> {
  const base = (input.baseUrl ?? SIMULADOR_BASE_URL).replace(/\/$/, "");
  const fetchImpl = input.fetchImpl ?? fetch;

  const res = await fetchImpl(`${base}/api/simulations`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      scenario: input.scenario,
      variables: input.variables ?? {},
      iterations: input.iterations ?? 1000,
    }),
  });

  if (!res.ok) {
    const bodyText = await res.text().catch(() => "");
    throw new Error(
      `[la-forja:puerta_simulador_http_failed] ${res.status} ${res.statusText} ` +
        `body=${bodyText.slice(0, 200)}`,
    );
  }

  const data = (await res.json()) as {
    simulation_id?: string;
    id?: string;
    status?: string;
  };
  const simulationId = data.simulation_id ?? data.id;
  if (!simulationId) {
    throw new Error(
      "[la-forja:puerta_simulador_missing_id] response missing simulation_id and id fields",
    );
  }
  return {
    simulationId,
    status: data.status ?? "unknown",
    raw: data,
  };
}

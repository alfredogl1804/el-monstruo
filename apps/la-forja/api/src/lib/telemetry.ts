/**
 * La Forja — Telemetry stub (LF-TELEMETRY-MANDATORY-001).
 *
 * Sprint LA-FORJA-001 v3.2 — D2.3.
 * Doctrina: §7 SPEC v3.2.
 *
 * En D2: stub stdout estructurado.
 * En D5: implementación real con INSERT INTO forja_telemetry + Langfuse spans.
 * El interface NO cambia entre D2 y D5 — las rutas que llaman recordEvent()
 * no se tocan.
 *
 * Eventos canónicos del SPEC:
 *   - simplification_requested    → AC12 detector con threshold 0.7
 *   - confusion_detected          → AC12 high-confidence (≥ 0.85)
 *   - turn_abandoned              → usuario cierra ventana mid-turn
 *   - sprint_completed            → state=cerrado_pulir transición
 *   - sprint_started              → state=propuesta transición
 *   - puerta_invoked              → 5 puertas LF-FIVE-DOORS-001
 *   - budget_exceeded             → ForjaBudgetExceededError raised
 *   - magna_validation_used       → Perplexity citations insertadas
 */

export type TelemetryEventType =
  | "simplification_requested"
  | "confusion_detected"
  | "turn_abandoned"
  | "sprint_completed"
  | "sprint_started"
  | "puerta_invoked"
  | "budget_exceeded"
  | "magna_validation_used";

export interface TelemetryEvent {
  /** UUID del usuario (forja_profiles.id) */
  userId: string;
  /** Tipo de evento canónico §7 SPEC */
  type: TelemetryEventType;
  /** Sprint asociado (si aplica) */
  sprintId?: string;
  /** Thread asociado (si aplica) */
  threadId?: string;
  /** Confidence del clasificador (si aplica) */
  confidence?: number;
  /** Modelo invocado en este turn (si aplica) */
  model?: string;
  /** Costo USD del turn (si aplica) */
  costUsd?: number;
  /** Metadata libre */
  metadata?: Record<string, unknown>;
}

export interface TelemetryClient {
  recordEvent(event: TelemetryEvent): Promise<void>;
}

/**
 * Stub stdout structured logging para D2-D4.
 * En D5 esta función se reemplaza por INSERT INTO forja_telemetry +
 * Langfuse span con preLogRedact() del payload sensible.
 */
export class StdoutTelemetryClient implements TelemetryClient {
   
  async recordEvent(event: TelemetryEvent): Promise<void> {
    const payload = {
      ts: new Date().toISOString(),
      app: "la-forja",
      ...event,
    };
    // structured stdout para Railway logs y futura ingestión
    // biome-ignore lint/suspicious/noConsole: structured telemetry stdout
    console.log(`[la-forja:telemetry] ${JSON.stringify(payload)}`);
  }
}

let _cached: TelemetryClient | null = null;

/**
 * Singleton síncrono. Siempre retorna `StdoutTelemetryClient` por default
 * para preservar el contrato testeable. La selección binaria por NODE_ENV
 * (Supabase real en producción) se hace en `index.ts` mediante
 * `_setTelemetryClient(...)` ANTES de exponer las rutas.
 *
 * Patrón: la fábrica de la app (createApp) llama `installSupabaseTelemetry()`
 * cuando NODE_ENV=production. El default sigue siendo stdout para tests/dev.
 * Esto evita require() dinámico (no soportado en ESM) y mantiene 207/207
 * tests verdes sin tocar nada en `telemetry.test.ts`.
 */
export function getTelemetryClient(): TelemetryClient {
  if (_cached) {return _cached;}
  _cached = new StdoutTelemetryClient();
  return _cached;
}

/** Reset singleton — only for tests / D5 swap. */
export function _setTelemetryClient(client: TelemetryClient | null): void {
  _cached = client;
}

/**
 * Helper de conveniencia. La mayoría de las rutas usan este shorthand.
 */
export function recordEvent(event: TelemetryEvent): Promise<void> {
  return getTelemetryClient().recordEvent(event);
}

/**
 * Activa el cliente Supabase para producción.
 *
 * Llamado explícitamente desde `createApp()` cuando NODE_ENV=production.
 * Importa de forma estática `SupabaseTelemetryClient` y `resolveUserById`
 * (sin `require` dinámico que rompe ESM).
 *
 * Idempotente: si ya hay cliente custom, no lo sobreescribe.
 */
export async function installSupabaseTelemetry(nodeEnv: string): Promise<void> {
  if (_cached && !(_cached instanceof StdoutTelemetryClient)) {
    // Cliente custom ya instalado (test o llamada previa)
    return;
  }
  const [{ SupabaseTelemetryClient }, { resolveUserById }] = await Promise.all([
    import("./repositories/telemetry"),
    import("./budget_clients"),
  ]);
  _cached = new SupabaseTelemetryClient({
    resolveUser: resolveUserById,
    nodeEnv,
  });
}

/**
 * La Forja — Repository: forja_telemetry (SupabaseTelemetryClient real).
 *
 * Sprint LA-FORJA-001 v3.2 — D5.2.
 * Doctrina: §7 SPEC v3.2 + DSC-LF-010 + LF-TELEMETRY-MANDATORY-001.
 *
 * Reemplaza el `StdoutTelemetryClient` (console.log) por un cliente que
 * INSERTA filas en `public.forja_telemetry` (migración 0043 D5.1).
 *
 * Reconciliación de vocabulario (sub-caveat P2 nuevo declarado en bridge D5.2):
 *
 *   TS (8 eventos canónicos):
 *     simplification_requested, confusion_detected, turn_abandoned,
 *     sprint_completed, sprint_started, puerta_invoked, budget_exceeded,
 *     magna_validation_used.
 *
 *   SQL (13 eventos canónicos, whitelist `chk_forja_telemetry_event`):
 *     confusion_detected, simplification_requested, abandonment_detected,
 *     completion_signal, invalid_state_transition, family_relation_risk,
 *     budget_warning, budget_cap_hit, tutor_validation_toggled,
 *     mode_changed, session_long, summary_refreshed, other.
 *
 * Estrategia binaria (no expande SQL whitelist, se canoniza en D5.3+):
 *   - Eventos TS que existen en SQL → se persisten con `event=<mismo nombre>`.
 *     Hits: confusion_detected, simplification_requested.
 *   - Eventos TS que tienen equivalente semántico en SQL → mapping explícito.
 *     turn_abandoned     → abandonment_detected
 *     sprint_completed   → completion_signal (con subject="sprint")
 *   - Eventos TS sin equivalente directo → event="other" con `subject` que
 *     preserva el tipo TS original para forensics.
 *     sprint_started        → other (subject="sprint_started")
 *     puerta_invoked        → other (subject="puerta_invoked")
 *     budget_exceeded       → budget_cap_hit
 *     magna_validation_used → other (subject="magna_validation_used")
 *
 * Implicaciones binarias:
 *   - El stdout fail-soft se preserva. Si el INSERT falla por cualquier razón
 *     (RLS, network, schema drift), el cliente loguea el error pero NO lanza
 *     excepción al caller — el tutor stream NO debe romperse por telemetría.
 *   - El service-role bypassa RLS, lo cual es correcto: la app inserta en
 *     nombre del usuario validado por JWT.
 */

import type {
  TelemetryClient,
  TelemetryEvent,
  TelemetryEventType,
} from "../telemetry.js";
import { getSupabase } from "../supabase.js";
import type { User } from "../env.js";
import { resolveProfileId } from "./profiles.js";

/**
 * Mapping TS → SQL. Cada TS event se traduce a un par
 * `{event: <SQL>, subject: <preservación TS si aplica>}`.
 */
const TS_TO_SQL: Record<
  TelemetryEventType,
  { event: string; subject: string | null }
> = {
  confusion_detected: { event: "confusion_detected", subject: null },
  simplification_requested: { event: "simplification_requested", subject: null },
  turn_abandoned: { event: "abandonment_detected", subject: null },
  sprint_completed: { event: "completion_signal", subject: "sprint" },
  sprint_started: { event: "other", subject: "sprint_started" },
  puerta_invoked: { event: "other", subject: "puerta_invoked" },
  budget_exceeded: { event: "budget_cap_hit", subject: null },
  magna_validation_used: { event: "other", subject: "magna_validation_used" },
};

export interface SupabaseTelemetryClientOptions {
  /** Mismo patrón que SupabaseBudgetClient: resolver userId → User. */
  resolveUser: (userId: string) => User | null;
  /** NODE_ENV — para discriminar stub vs OAuth en el google_sub resolver. */
  nodeEnv: string;
}

/**
 * Cliente real Supabase. Implementa `TelemetryClient` con INSERT INTO
 * `public.forja_telemetry`. Fail-soft: errores en INSERT NO propagan.
 */
export class SupabaseTelemetryClient implements TelemetryClient {
  constructor(private readonly opts: SupabaseTelemetryClientOptions) {}

  async recordEvent(event: TelemetryEvent): Promise<void> {
    try {
      const user = this.opts.resolveUser(event.userId);
      if (!user) {
        // Fail-soft: log pero no throw. La telemetría JAMÁS debe romper
        // el flujo del tutor o de cualquier ruta que la invoque.
        // biome-ignore lint/suspicious/noConsole: telemetry fail-soft warning
        console.warn(
          `[la-forja:telemetry_unresolved_user] userId=${event.userId} type=${event.type}`,
        );
        return;
      }

      const profileId = await resolveProfileId(user, this.opts.nodeEnv);
      const mapping = TS_TO_SQL[event.type];

      const supabase = getSupabase();
      const { error } = await supabase.from("forja_telemetry").insert({
        profile_id: profileId,
        thread_id: event.threadId ?? null,
        event: mapping.event,
        subject: mapping.subject,
        evidence: null,
        classifier_score: event.confidence ?? null,
        intent: null,
        metadata: {
          ts_type: event.type,
          model: event.model,
          cost_usd: event.costUsd,
          ...event.metadata,
        },
      });

      if (error) {
        // Fail-soft: log pero no throw.
        // biome-ignore lint/suspicious/noConsole: telemetry fail-soft warning
        console.warn(
          `[la-forja:telemetry_insert_failed] type=${event.type} ` +
            `sql_event=${mapping.event} error=${error.message}`,
        );
      }
    } catch (err) {
      // Última red de seguridad. Cualquier excepción inesperada se loguea
      // pero NO se propaga al caller del tutor.
      // biome-ignore lint/suspicious/noConsole: telemetry fail-soft warning
      console.warn(
        `[la-forja:telemetry_unexpected_error] type=${event.type} ` +
          `error=${err instanceof Error ? err.message : String(err)}`,
      );
    }
  }
}

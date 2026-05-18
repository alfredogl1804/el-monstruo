/**
 * La Forja — Repository: forja_threads + forja_messages + forja_validations.
 *
 * Sprint LA-FORJA-001 v3.2 — D5.2.
 * Doctrina: §4 SPEC v3.2 + DSC-LF-010.
 *
 * Reemplaza la NO-persistencia previa de turnos del tutor con queries reales
 * contra:
 *   - forja_threads      (migración 0039 D5.1)
 *   - forja_messages     (migración 0040 D5.1)
 *   - forja_validations  (migración 0045 D5.1)
 *
 * Diseño binario (mínimo D5.2 — completable en D5.3):
 *
 *   1. ensureThread(profileId, threadId?, mode?) → threadId
 *      Si `threadId` existe en DB → retorna tal cual.
 *      Si NO existe (caller no pasó id O id no encontrado) → INSERT default
 *      con title='Hilo sin título' y retorna nuevo id.
 *
 *   2. appendUserMessage(threadId, content) → messageId
 *      INSERT en forja_messages con role='user', tokens_in/out=0, cost=0.
 *
 *   3. appendAssistantMessage(threadId, {content, model, tokensIn, tokensOut,
 *      costUsd, requireValidation, citations}) → messageId
 *      INSERT en forja_messages con role='assistant' y métricas reales.
 *      También UPDATE forja_threads acumulando counters
 *      (message_count++, total_tokens_*+=, total_usd+=).
 *
 *   4. recordValidation(threadId, profileId, messageId, {topic, query, model,
 *      citations, costUsd, latencyMs}) → validationId
 *      INSERT en forja_validations con provider='perplexity' y status='completed'.
 *
 * Fail-soft: igual que telemetría, errores de persistencia NO rompen el
 * stream del tutor — se loguean y el turno continúa. Persistir mensajes
 * es importante pero NO crítico para que el usuario obtenga su respuesta.
 */

import { getSupabase } from "../supabase.js";

export interface AssistantMessageMetrics {
  content: string;
  model: string;
  tokensIn: number;
  tokensOut: number;
  costUsd: number;
  requireValidation: boolean;
  citations?: string[];
  latencyMs?: number;
}

export interface ValidationRecord {
  messageId: string | null;
  topic: string;
  query: string;
  model: string;
  citations: string[];
  costUsd: number;
  latencyMs?: number;
  rawResponse?: unknown;
}

/**
 * Garantiza un thread persistente para el usuario.
 *
 * Si `desiredThreadId` viene del frontend y existe en DB → retorna ese id.
 * Si no viene o no existe → crea uno nuevo con title default y retorna su id.
 *
 * Idempotente y safe: el caller siempre obtiene un threadId válido.
 */
export async function ensureThread(
  profileId: string,
  desiredThreadId?: string | null,
  mode: "light" | "normal" | "heavy" | "power" = "normal",
): Promise<string> {
  const supabase = getSupabase();

  if (desiredThreadId) {
    const { data, error } = await supabase
      .from("forja_threads")
      .select("id")
      .eq("id", desiredThreadId)
      .eq("profile_id", profileId)
      .maybeSingle();
    if (error) {
      throw new Error(
        `[la-forja:threads_lookup_failed] thread=${desiredThreadId} ` +
          `error=${error.message}`,
      );
    }
    if (data) {
      return data.id;
    }
    // Si vino un id pero NO está en DB para este profile, fall-through al INSERT.
    // No se honra el id del cliente para evitar IDOR — siempre creamos nuevo.
  }

  const { data, error } = await supabase
    .from("forja_threads")
    .insert({
      profile_id: profileId,
      title: "Hilo sin título",
      mode,
    })
    .select("id")
    .single();

  if (error || !data) {
    throw new Error(
      `[la-forja:threads_insert_failed] profile_id=${profileId} ` +
        `error=${error?.message ?? "no row returned"}`,
    );
  }
  return data.id;
}

/**
 * Persiste el mensaje del usuario al inicio del turn.
 * Append-only — no deduplica.
 */
export async function appendUserMessage(
  threadId: string,
  content: string,
): Promise<string> {
  const supabase = getSupabase();
  const { data, error } = await supabase
    .from("forja_messages")
    .insert({
      thread_id: threadId,
      role: "user",
      content,
      tokens_in: 0,
      tokens_out: 0,
      cost_usd: 0,
      require_validation: false,
    })
    .select("id")
    .single();

  if (error || !data) {
    throw new Error(
      `[la-forja:messages_user_insert_failed] thread=${threadId} ` +
        `error=${error?.message ?? "no row returned"}`,
    );
  }
  return data.id;
}

/**
 * Persiste el mensaje assistant con métricas reales y actualiza counters
 * del thread. Si el UPDATE de counters falla, no se revierte el INSERT
 * del mensaje (append-only mantiene integridad histórica).
 */
export async function appendAssistantMessage(
  threadId: string,
  metrics: AssistantMessageMetrics,
): Promise<string> {
  const supabase = getSupabase();

  const { data, error } = await supabase
    .from("forja_messages")
    .insert({
      thread_id: threadId,
      role: "assistant",
      content: metrics.content,
      model: metrics.model,
      tokens_in: metrics.tokensIn,
      tokens_out: metrics.tokensOut,
      latency_ms: metrics.latencyMs ?? null,
      cost_usd: metrics.costUsd,
      require_validation: metrics.requireValidation,
      citations:
        metrics.citations && metrics.citations.length > 0
          ? metrics.citations
          : null,
    })
    .select("id")
    .single();

  if (error || !data) {
    throw new Error(
      `[la-forja:messages_assistant_insert_failed] thread=${threadId} ` +
        `error=${error?.message ?? "no row returned"}`,
    );
  }

  // Actualizar counters del thread. Last-write-wins (mismo patrón que budget).
  // Race conditions sobre counters son aceptables para D5.2 (canon RPC en D5.3).
  const { data: thread } = await supabase
    .from("forja_threads")
    .select("message_count, total_tokens_in, total_tokens_out, total_usd")
    .eq("id", threadId)
    .maybeSingle();

  if (thread) {
    await supabase
      .from("forja_threads")
      .update({
        message_count: (thread.message_count ?? 0) + 2, // user + assistant
        total_tokens_in: (Number(thread.total_tokens_in) || 0) + metrics.tokensIn,
        total_tokens_out:
          (Number(thread.total_tokens_out) || 0) + metrics.tokensOut,
        total_usd: (Number(thread.total_usd) || 0) + metrics.costUsd,
      })
      .eq("id", threadId);
  }

  return data.id;
}

/**
 * Persiste un audit de validación Perplexity en forja_validations.
 * 1 fila = 1 query validada. Si magna falla en error path, el caller
 * decide si registrar status='failed' (no implementado en D5.2 — fail-soft).
 */
export async function recordValidation(
  threadId: string,
  profileId: string,
  record: ValidationRecord,
): Promise<string> {
  const supabase = getSupabase();
  const { data, error } = await supabase
    .from("forja_validations")
    .insert({
      thread_id: threadId,
      profile_id: profileId,
      message_id: record.messageId,
      topic: record.topic,
      query: record.query,
      provider: "perplexity",
      model: record.model,
      citations: record.citations,
      citation_count: record.citations.length,
      raw_response: record.rawResponse ?? null,
      status: "completed",
      cost_usd: record.costUsd,
      latency_ms: record.latencyMs ?? null,
    })
    .select("id")
    .single();

  if (error || !data) {
    throw new Error(
      `[la-forja:validations_insert_failed] thread=${threadId} ` +
        `error=${error?.message ?? "no row returned"}`,
    );
  }
  return data.id;
}

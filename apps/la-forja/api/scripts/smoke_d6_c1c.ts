/**
 * D6 SMOKE TEST C1.C — autorizado Cowork T2-A 2026-05-18
 *
 * Sprint LA-FORJA-001 v3.2 — D6.
 * Doctrina: paridad H1 (DELETE táctico prod con snapshot pre-operación).
 *
 * Objetivo binario:
 *   Validar que los 4 repos D5.2 (profiles, budget, telemetry, threads)
 *   funcionan contra Supabase PRODUCCIÓN real con NODE_ENV=production,
 *   sin pasar por HTTP/Express (paridad H1 = SQL directo).
 *
 * Protocolo (firmado Cowork):
 *   1. PRE-TEST: snapshot canary slot vacío (count=0 ambos canary marker)
 *   2. EJERCICIO: resolveProfileId → ensureThread → appendUserMessage →
 *      reserveSpent → appendAssistantMessage → recordValidation → recordEvent
 *   3. VERIFY: inserts confirmados en 6 tablas
 *   4. SNAPSHOT FORENSE: H2_2026_05_18_smoke_d6_canary.json
 *   5. DELETE QUIRÚRGICO: orden FK descendente
 *   6. POST-VERIFY: count=0 obligatorio para declarar verde
 */

/* eslint-disable no-console */

// Forzar NODE_ENV=production ANTES de cualquier import que llame loadEnv
process.env.NODE_ENV = "production";

// Placeholders OAuth/JWT (smoke C1.C no usa auth — bypass directo a repos)
process.env.GOOGLE_OAUTH_CLIENT_ID =
  process.env.GOOGLE_OAUTH_CLIENT_ID ?? "smoke-d6-placeholder.apps.googleusercontent.com";
process.env.GOOGLE_OAUTH_CLIENT_SECRET =
  process.env.GOOGLE_OAUTH_CLIENT_SECRET ?? "smoke-d6-placeholder-client-secret";
process.env.JWT_SECRET =
  process.env.JWT_SECRET ?? "smoke-d6-placeholder-jwt-secret-32-chars-min-required";

import * as fs from "node:fs/promises";
import * as path from "node:path";
import { fileURLToPath } from "node:url";

import { loadEnv, type User } from "../src/lib/env.js";
import { getSupabase } from "../src/lib/supabase.js";
import {
  resolveProfileId,
  _resetProfileIdCache,
} from "../src/lib/repositories/profiles.js";
import {
  ensureThread,
  appendUserMessage,
  appendAssistantMessage,
  recordValidation,
} from "../src/lib/repositories/threads.js";
import { SupabaseBudgetClient } from "../src/lib/repositories/budget.js";
import { SupabaseTelemetryClient } from "../src/lib/repositories/telemetry.js";
import {
  registerUserForResolver,
  resolveUserById,
  _resetUserResolver,
} from "../src/lib/budget_clients.js";

// ----------------------------------------------------------------------
// Constantes canario (firma Cowork)
// ----------------------------------------------------------------------

const CANARY_TS = "2026-05-18";
const CANARY_GOOGLE_SUB = `canary-d6-${CANARY_TS}-001`;
const CANARY_MARKER = `CANARY-D6-${CANARY_TS}`;

const CANARY_USER: User = {
  id: CANARY_GOOGLE_SUB,
  email: "canary-d6@smoke.la-forja.local",
  role: "user",
};

// ----------------------------------------------------------------------
// Helpers de log estructurado
// ----------------------------------------------------------------------

interface SmokeLogEntry {
  ts: string;
  step: string;
  status: "start" | "ok" | "fail" | "info";
  details?: Record<string, unknown>;
}

const SMOKE_LOG: SmokeLogEntry[] = [];

function log(
  step: string,
  status: SmokeLogEntry["status"],
  details?: Record<string, unknown>,
): void {
  const entry: SmokeLogEntry = {
    ts: new Date().toISOString(),
    step,
    status,
    details,
  };
  SMOKE_LOG.push(entry);
  console.log(`[smoke-d6] ${JSON.stringify(entry)}`);
}

// ----------------------------------------------------------------------
// PRE-TEST
// ----------------------------------------------------------------------

async function preTestCheck(): Promise<{ profile: number; thread: number }> {
  log("pre_test_check", "start");
  const supabase = getSupabase();

  const { count: profileCount, error: profileErr } = await supabase
    .from("forja_profiles")
    .select("*", { count: "exact", head: true })
    .eq("google_sub", CANARY_GOOGLE_SUB);
  if (profileErr) {
    throw new Error(`pre_test profile lookup failed: ${profileErr.message}`);
  }
  if ((profileCount ?? 0) > 0) {
    throw new Error(
      `pre_test ABORT: profile canary already exists (count=${profileCount}).`,
    );
  }
  log("pre_test_check", "info", { profile_canary_count: profileCount ?? 0 });

  const { count: threadCount, error: threadErr } = await supabase
    .from("forja_threads")
    .select("*", { count: "exact", head: true })
    .eq("metadata->>canary", CANARY_MARKER);
  if (threadErr) {
    throw new Error(`pre_test thread lookup failed: ${threadErr.message}`);
  }
  if ((threadCount ?? 0) > 0) {
    throw new Error(
      `pre_test ABORT: thread canary already exists (count=${threadCount}).`,
    );
  }
  log("pre_test_check", "info", { thread_canary_count: threadCount ?? 0 });

  log("pre_test_check", "ok");
  return { profile: profileCount ?? 0, thread: threadCount ?? 0 };
}

// ----------------------------------------------------------------------
// EJERCICIO
// ----------------------------------------------------------------------

interface SmokeArtifacts {
  profileId: string;
  threadId: string;
  userMsgId: string;
  assistantMsgId: string;
  validationId: string;
  budgetSpentUsd: number;
}

async function exerciseRepos(): Promise<SmokeArtifacts> {
  log("exercise_repos", "start", { canary_user: CANARY_USER });

  const env = loadEnv();
  registerUserForResolver(CANARY_USER);

  log("resolve_profile_id", "start");
  const profileId = await resolveProfileId(CANARY_USER, env.NODE_ENV);
  log("resolve_profile_id", "ok", { profile_id: profileId });

  log("ensure_thread", "start");
  const threadId = await ensureThread(profileId, undefined, "normal");
  log("ensure_thread", "ok", { thread_id: threadId });

  log("set_thread_metadata_canary", "start");
  const supabase = getSupabase();
  {
    const { error } = await supabase
      .from("forja_threads")
      .update({ metadata: { canary: CANARY_MARKER, smoke_test: "D6_C1C" } })
      .eq("id", threadId);
    if (error) {
      throw new Error(`set thread metadata failed: ${error.message}`);
    }
  }
  log("set_thread_metadata_canary", "ok");

  log("append_user_message", "start");
  const userMsgId = await appendUserMessage(
    threadId,
    "[CANARY-D6] Mensaje canario para smoke test D5.2 → D6.",
  );
  log("append_user_message", "ok", { user_msg_id: userMsgId });

  log("budget_reserve", "start");
  const budgetClient = new SupabaseBudgetClient({
    resolveUser: resolveUserById,
    nodeEnv: env.NODE_ENV,
  });
  await budgetClient.reserveSpent(CANARY_USER.id, 0.001234);
  const spentAfterReserve = await budgetClient.readSpent(CANARY_USER.id);
  log("budget_reserve", "ok", { spent_usd: spentAfterReserve });

  log("append_assistant_message", "start");
  const assistantMsgId = await appendAssistantMessage(threadId, {
    content: "[CANARY-D6] Respuesta canario simulada del tutor.",
    model: "claude-opus-4-7-canary",
    tokensIn: 50,
    tokensOut: 30,
    costUsd: 0.001234,
    requireValidation: true,
    citations: ["https://example.com/canary-citation"],
    latencyMs: 100,
  });
  log("append_assistant_message", "ok", { assistant_msg_id: assistantMsgId });

  log("record_validation", "start");
  const validationId = await recordValidation(threadId, profileId, {
    messageId: assistantMsgId,
    topic: "canary-smoke-d6",
    query: "[CANARY-D6] query para smoke",
    model: "sonar-reasoning-pro-canary",
    citations: ["https://example.com/perplexity-citation"],
    costUsd: 0.0005,
    latencyMs: 50,
  });
  log("record_validation", "ok", { validation_id: validationId });

  log("telemetry_record", "start");
  const telemetryClient = new SupabaseTelemetryClient({
    resolveUser: resolveUserById,
    nodeEnv: env.NODE_ENV,
  });
  await telemetryClient.recordEvent({
    userId: CANARY_USER.id,
    type: "magna_validation_used",
    threadId,
    confidence: 0.95,
    model: "sonar-reasoning-pro-canary",
    costUsd: 0.0005,
    metadata: { canary: CANARY_MARKER, smoke_test: "D6_C1C" },
  });
  log("telemetry_record", "ok");

  log("exercise_repos", "ok");
  return {
    profileId,
    threadId,
    userMsgId,
    assistantMsgId,
    validationId,
    budgetSpentUsd: spentAfterReserve,
  };
}

// ----------------------------------------------------------------------
// VERIFY
// ----------------------------------------------------------------------

interface VerifyResult {
  forja_profiles: number;
  forja_threads: number;
  forja_messages: number;
  forja_budget: number;
  forja_validations: number;
  forja_telemetry: number;
}

async function verifyInserts(art: SmokeArtifacts): Promise<VerifyResult> {
  log("verify_inserts", "start");
  const supabase = getSupabase();

  const counts: VerifyResult = {
    forja_profiles: 0,
    forja_threads: 0,
    forja_messages: 0,
    forja_budget: 0,
    forja_validations: 0,
    forja_telemetry: 0,
  };

  {
    const { count } = await supabase
      .from("forja_profiles")
      .select("*", { count: "exact", head: true })
      .eq("id", art.profileId);
    counts.forja_profiles = count ?? 0;
  }
  {
    const { count } = await supabase
      .from("forja_threads")
      .select("*", { count: "exact", head: true })
      .eq("id", art.threadId);
    counts.forja_threads = count ?? 0;
  }
  {
    const { count } = await supabase
      .from("forja_messages")
      .select("*", { count: "exact", head: true })
      .eq("thread_id", art.threadId);
    counts.forja_messages = count ?? 0;
  }
  {
    const { count } = await supabase
      .from("forja_budget")
      .select("*", { count: "exact", head: true })
      .eq("profile_id", art.profileId);
    counts.forja_budget = count ?? 0;
  }
  {
    const { count } = await supabase
      .from("forja_validations")
      .select("*", { count: "exact", head: true })
      .eq("id", art.validationId);
    counts.forja_validations = count ?? 0;
  }
  {
    const { count } = await supabase
      .from("forja_telemetry")
      .select("*", { count: "exact", head: true })
      .eq("profile_id", art.profileId)
      .eq("subject", "magna_validation_used");
    counts.forja_telemetry = count ?? 0;
  }

  log("verify_inserts", "ok", counts);

  if (counts.forja_profiles !== 1) {
    throw new Error(`verify FAIL: forja_profiles=${counts.forja_profiles} (expected 1)`);
  }
  if (counts.forja_threads !== 1) {
    throw new Error(`verify FAIL: forja_threads=${counts.forja_threads} (expected 1)`);
  }
  if (counts.forja_messages !== 2) {
    throw new Error(`verify FAIL: forja_messages=${counts.forja_messages} (expected 2)`);
  }
  if (counts.forja_budget !== 1) {
    throw new Error(`verify FAIL: forja_budget=${counts.forja_budget} (expected 1)`);
  }
  if (counts.forja_validations !== 1) {
    throw new Error(`verify FAIL: forja_validations=${counts.forja_validations} (expected 1)`);
  }
  if (counts.forja_telemetry !== 1) {
    throw new Error(`verify FAIL: forja_telemetry=${counts.forja_telemetry} (expected 1)`);
  }

  return counts;
}

// ----------------------------------------------------------------------
// SNAPSHOT FORENSE H2
// ----------------------------------------------------------------------

async function snapshotForensic(
  art: SmokeArtifacts,
  preTestCounts: Record<string, number>,
  postExerciseCounts: VerifyResult,
): Promise<string> {
  log("snapshot_forensic", "start");
  const supabase = getSupabase();

  const [profiles, threads, messages, budget, validations, telemetry] =
    await Promise.all([
      supabase.from("forja_profiles").select("*").eq("id", art.profileId),
      supabase.from("forja_threads").select("*").eq("id", art.threadId),
      supabase.from("forja_messages").select("*").eq("thread_id", art.threadId),
      supabase.from("forja_budget").select("*").eq("profile_id", art.profileId),
      supabase.from("forja_validations").select("*").eq("id", art.validationId),
      supabase
        .from("forja_telemetry")
        .select("*")
        .eq("profile_id", art.profileId),
    ]);

  const snapshot = {
    incident_id: "H2_2026_05_18_smoke_d6_canary",
    sprint: "LA-FORJA-001 D6",
    test_protocol: "C1.C — repos directo (no HTTP/Express)",
    canary_marker: CANARY_MARKER,
    canary_google_sub: CANARY_GOOGLE_SUB,
    authorized_by: "Cowork T2-A 2026-05-18 (paridad H1)",
    timestamps: {
      started_at_utc: SMOKE_LOG[0]?.ts,
      snapshot_taken_at_utc: new Date().toISOString(),
    },
    artifacts: art,
    pre_test_counts: preTestCounts,
    post_exercise_counts: postExerciseCounts,
    rows: {
      forja_profiles: profiles.data,
      forja_threads: threads.data,
      forja_messages: messages.data,
      forja_budget: budget.data,
      forja_validations: validations.data,
      forja_telemetry: telemetry.data,
    },
    smoke_log: SMOKE_LOG,
  };

  const __filename = fileURLToPath(import.meta.url);
  const __dirname = path.dirname(__filename);
  const repoRoot = path.resolve(__dirname, "../../../..");
  const incidentDir = path.join(repoRoot, "discovery_forense", "INCIDENTES");
  const snapshotPath = path.join(incidentDir, "H2_2026_05_18_smoke_d6_canary.json");

  await fs.mkdir(incidentDir, { recursive: true });
  await fs.writeFile(snapshotPath, JSON.stringify(snapshot, null, 2), "utf8");

  log("snapshot_forensic", "ok", { path: snapshotPath });
  return snapshotPath;
}

// ----------------------------------------------------------------------
// DELETE QUIRÚRGICO
// ----------------------------------------------------------------------

async function deleteCanaryRows(art: SmokeArtifacts): Promise<void> {
  log("delete_canary", "start");
  const supabase = getSupabase();

  {
    const { error, count } = await supabase
      .from("forja_validations")
      .delete({ count: "exact" })
      .eq("id", art.validationId);
    if (error) {throw new Error(`DELETE validations failed: ${error.message}`);}
    log("delete_validations", "ok", { rows: count });
  }
  {
    const { error, count } = await supabase
      .from("forja_telemetry")
      .delete({ count: "exact" })
      .eq("profile_id", art.profileId);
    if (error) {throw new Error(`DELETE telemetry failed: ${error.message}`);}
    log("delete_telemetry", "ok", { rows: count });
  }
  {
    const { error, count } = await supabase
      .from("forja_messages")
      .delete({ count: "exact" })
      .eq("thread_id", art.threadId);
    if (error) {throw new Error(`DELETE messages failed: ${error.message}`);}
    log("delete_messages", "ok", { rows: count });
  }
  {
    const { error, count } = await supabase
      .from("forja_threads")
      .delete({ count: "exact" })
      .eq("id", art.threadId);
    if (error) {throw new Error(`DELETE threads failed: ${error.message}`);}
    log("delete_threads", "ok", { rows: count });
  }
  {
    const { error, count } = await supabase
      .from("forja_budget")
      .delete({ count: "exact" })
      .eq("profile_id", art.profileId);
    if (error) {throw new Error(`DELETE budget failed: ${error.message}`);}
    log("delete_budget", "ok", { rows: count });
  }
  {
    const { error, count } = await supabase
      .from("forja_profiles")
      .delete({ count: "exact" })
      .eq("id", art.profileId);
    if (error) {throw new Error(`DELETE profile failed: ${error.message}`);}
    log("delete_profile", "ok", { rows: count });
  }

  log("delete_canary", "ok");
}

// ----------------------------------------------------------------------
// POST-VERIFY
// ----------------------------------------------------------------------

async function postVerify(art: SmokeArtifacts): Promise<VerifyResult> {
  log("post_verify", "start");
  const supabase = getSupabase();

  const counts: VerifyResult = {
    forja_profiles: 0,
    forja_threads: 0,
    forja_messages: 0,
    forja_budget: 0,
    forja_validations: 0,
    forja_telemetry: 0,
  };

  {
    const { count } = await supabase
      .from("forja_profiles")
      .select("*", { count: "exact", head: true })
      .eq("id", art.profileId);
    counts.forja_profiles = count ?? 0;
  }
  {
    const { count } = await supabase
      .from("forja_threads")
      .select("*", { count: "exact", head: true })
      .eq("id", art.threadId);
    counts.forja_threads = count ?? 0;
  }
  {
    const { count } = await supabase
      .from("forja_messages")
      .select("*", { count: "exact", head: true })
      .eq("thread_id", art.threadId);
    counts.forja_messages = count ?? 0;
  }
  {
    const { count } = await supabase
      .from("forja_budget")
      .select("*", { count: "exact", head: true })
      .eq("profile_id", art.profileId);
    counts.forja_budget = count ?? 0;
  }
  {
    const { count } = await supabase
      .from("forja_validations")
      .select("*", { count: "exact", head: true })
      .eq("id", art.validationId);
    counts.forja_validations = count ?? 0;
  }
  {
    const { count } = await supabase
      .from("forja_telemetry")
      .select("*", { count: "exact", head: true })
      .eq("profile_id", art.profileId);
    counts.forja_telemetry = count ?? 0;
  }

  log("post_verify", "ok", counts);

  for (const [table, count] of Object.entries(counts)) {
    if (count !== 0) {
      throw new Error(
        `POST-VERIFY P0: ${table} count=${count} (expected 0). Snapshot H2 ya existe.`,
      );
    }
  }

  return counts;
}

// ----------------------------------------------------------------------
// MAIN
// ----------------------------------------------------------------------

async function main(): Promise<void> {
  log("smoke_d6_c1c", "start", {
    canary_marker: CANARY_MARKER,
    canary_google_sub: CANARY_GOOGLE_SUB,
    node_env: process.env.NODE_ENV,
  });

  _resetUserResolver();
  _resetProfileIdCache();

  const preTestCounts = await preTestCheck();
  const artifacts = await exerciseRepos();
  const postExerciseCounts = await verifyInserts(artifacts);
  await snapshotForensic(artifacts, preTestCounts, postExerciseCounts);
  await deleteCanaryRows(artifacts);
  await postVerify(artifacts);

  log("smoke_d6_c1c", "ok", {
    veredicto: "VERDE — D5.2 repos validados contra Supabase prod",
  });
}

main().catch((err) => {
  log("smoke_d6_c1c", "fail", {
    error: err instanceof Error ? err.message : String(err),
    stack: err instanceof Error ? err.stack : undefined,
  });
  process.exit(1);
});

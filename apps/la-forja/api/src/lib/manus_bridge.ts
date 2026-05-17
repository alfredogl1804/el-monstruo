/**
 * Manus M2M Bridge v2 — TypeScript port of tools/manus_bridge.py.
 *
 * Sprint LA-FORJA-001 v3.2 — D1 no-SQL.
 *
 * Allows La Forja (and El Monstruo) to delegate complex tasks to Manus agents
 * via the Manus API v2 (RPC-style endpoints). This is a 1:1 port of the canonical
 * Python implementation in tools/manus_bridge.py — every comment referencing
 * F-pattern #11, DSC, and the 2026-05-12 trailing-whitespace incident is
 * preserved verbatim for traceability with the Python source.
 *
 * ENV VARS (Railway runtime):
 *   MANUS_API_KEY_GOOGLE  — API key for Google-linked Manus account (este hilo)
 *   MANUS_API_KEY_APPLE   — API key for Apple-linked Manus account
 *
 * Usage:
 *   import { createTask, waitForCompletion } from "./lib/manus_bridge.js";
 *   const task = await createTask("Research top AI frameworks 2026");
 *   const result = await waitForCompletion(task.task_id, { timeout: 300_000 });
 *
 * Doctrina aplicada:
 *   - Regla Dura #4: secretos sólo desde process.env.
 *   - Regla Dura #2: tipado estricto, sin `any` en superficie pública.
 *   - F-pattern #11: distinción UUID Manus (22 alfanuméricos) vs etiqueta lógica.
 */

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/**
 * F-pattern #11 mitigation: distinguish Manus UUID (22-char alphanumeric)
 * from Anti-Dory logical labels (free-form strings like "el_monstruo").
 */
const MANUS_PROJECT_ID_REGEX = /^[A-Za-z0-9]{22}$/;

/**
 * Manus API v2 — base URL canónica (v1 fue deprecada).
 * Skill manus-api/SKILL.md confirma: api.manus.ai + header x-manus-api-key
 * + endpoints RPC-style.
 */
const DEFAULT_MANUS_BASE_URL = "https://api.manus.ai";

const API_KEY_ENV: Readonly<Record<AccountType, string>> = {
  google: "MANUS_API_KEY_GOOGLE",
  apple: "MANUS_API_KEY_APPLE",
};

const TERMINAL_STATUSES: ReadonlySet<string> = new Set([
  "completed",
  "failed",
  "cancelled",
  "error",
]);

const DEFAULT_POLL_INTERVAL_MS = 5_000;
const DEFAULT_TIMEOUT_MS = 300_000;
const MAX_RETRIES = 3;
const RATE_LIMIT_PER_HOUR = 5;
const ONE_HOUR_MS = 3_600_000;

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type AccountType = "google" | "apple";

export interface ManusTask {
  task_id?: string;
  id?: string;
  status?: string;
  output?: unknown;
  [key: string]: unknown;
}

export interface CreateTaskOptions {
  account?: AccountType;
  project_id?: string;
  front_id?: string;
  attach_context?: boolean;
  baseUrl?: string;
  /** Inyectable para tests — defaults a globalThis.fetch. */
  fetchImpl?: typeof fetch;
  /** Inyectable para tests — controla los waits del retry backoff. */
  sleep?: (ms: number) => Promise<void>;
}

export interface WaitOptions {
  account?: AccountType;
  timeout?: number;
  pollInterval?: number;
  baseUrl?: string;
  fetchImpl?: typeof fetch;
  /** Inyectable para tests — defaults a setTimeout-based sleep. */
  sleep?: (ms: number) => Promise<void>;
}

export interface HandleManusBridgeParams {
  action?: "create_task" | "get_status" | "create_and_wait";
  prompt?: string;
  task_id?: string;
  account?: AccountType;
  project_id?: string;
  timeout?: number;
}

// ---------------------------------------------------------------------------
// Exceptions
// ---------------------------------------------------------------------------

export class ManusBridgeError extends Error {
  constructor(message: string, options?: { cause?: unknown }) {
    super(message, options);
    this.name = "ManusBridgeError";
  }
}

export class ManusTimeoutError extends ManusBridgeError {
  constructor(message: string, options?: { cause?: unknown }) {
    super(message, options);
    this.name = "ManusTimeoutError";
  }
}

export class ManusTaskFailedError extends ManusBridgeError {
  constructor(message: string, options?: { cause?: unknown }) {
    super(message, options);
    this.name = "ManusTaskFailedError";
  }
}

export class ManusRateLimitError extends ManusBridgeError {
  constructor(message: string, options?: { cause?: unknown }) {
    super(message, options);
    this.name = "ManusRateLimitError";
  }
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Simple in-memory rate limiter (paridad con Python).
 * NOTA: en horizontal scaling este estado NO es compartido entre instancias.
 * Ver R9 en SPEC v3.2 — para producción multi-instancia se reemplazará por
 * Redis o Supabase row-level locking en D6.
 */
const _callTimestamps: number[] = [];

function _checkRateLimit(): void {
  const now = Date.now();
  const cutoff = now - ONE_HOUR_MS;

  // Prune old timestamps in-place
  let writeIdx = 0;
  for (let readIdx = 0; readIdx < _callTimestamps.length; readIdx += 1) {
    const ts = _callTimestamps[readIdx]!;
    if (ts > cutoff) {
      _callTimestamps[writeIdx] = ts;
      writeIdx += 1;
    }
  }
  _callTimestamps.length = writeIdx;

  if (_callTimestamps.length >= RATE_LIMIT_PER_HOUR) {
    const oldest = _callTimestamps[0]!;
    const waitSeconds = Math.floor((ONE_HOUR_MS - (now - oldest)) / 1000) + 1;
    throw new ManusRateLimitError(
      `Rate limit reached (${RATE_LIMIT_PER_HOUR}/hour). ` +
        `Try again in ${waitSeconds}s.`,
    );
  }
  _callTimestamps.push(now);
}

/** Test helper — reset rate-limit state. NOT exported via index.ts. */
export function _resetRateLimit(): void {
  _callTimestamps.length = 0;
}

function _getApiKey(account: AccountType): string {
  const envVar = API_KEY_ENV[account];
  if (!envVar) {
    throw new TypeError(
      `Unknown account type: ${JSON.stringify(account)}. Use 'google' or 'apple'.`,
    );
  }
  const raw = process.env[envVar];
  if (!raw) {
    throw new Error(
      `Environment variable ${envVar} is not set. ` +
        `Configure it in Railway before using account=${JSON.stringify(account)}.`,
    );
  }
  // Defensive .trim() — incidente 2026-05-12: env vars con trailing newline
  // producían 'Illegal header value' en httpx (Python) y TypeError en undici
  // (Node fetch). Ver bridge fix DSC.
  const key = raw.trim();
  if (key !== raw) {
    console.warn(
      `[manus_bridge] ${envVar} contained leading/trailing whitespace ` +
        `(raw_len=${raw.length}, clean_len=${key.length}) — auto-trimmed.`,
    );
  }
  return key;
}

function _buildHeaders(account: AccountType): Record<string, string> {
  // Manus API v2 uses custom header `x-manus-api-key` (NOT `Authorization: Bearer`).
  // Source: skills/manus-api/SKILL.md (skill oficial canónico).
  return {
    "x-manus-api-key": _getApiKey(account),
    "Content-Type": "application/json",
  };
}

async function _sleepDefault(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

interface RequestWithRetryOptions {
  account: AccountType;
  jsonPayload?: Record<string, unknown>;
  retries?: number;
  fetchImpl?: typeof fetch;
  sleep?: (ms: number) => Promise<void>;
}

/**
 * Execute an HTTP request with exponential backoff retry.
 * Retry policy: 3 attempts, wait 2^attempt seconds (2s, 4s, 8s).
 */
async function _requestWithRetry(
  method: "GET" | "POST",
  url: string,
  opts: RequestWithRetryOptions,
): Promise<Record<string, unknown>> {
  const {
    account,
    jsonPayload,
    retries = MAX_RETRIES,
    fetchImpl = globalThis.fetch,
    sleep = _sleepDefault,
  } = opts;

  let lastError: unknown = null;

  // Fail-fast: validar API key ANTES del retry loop. Errores de configuración
  // (env var missing) no deben reintentarse — se propagan inmediatamente para
  // que el caller (Railway logs) vea el problema sin esperar 14s de backoff.
  const headers = _buildHeaders(account);

  for (let attempt = 1; attempt <= retries; attempt += 1) {
    try {
      const init: RequestInit = {
        method,
        headers,
      };
      if (method === "POST" && jsonPayload !== undefined) {
        init.body = JSON.stringify(jsonPayload);
      }

      const resp = await fetchImpl(url, init);

      if (!resp.ok) {
        const bodyText = await resp.text().catch(() => "<unreadable>");
        throw new ManusBridgeError(
          `HTTP ${resp.status} ${resp.statusText} from ${method} ${url}: ${bodyText}`,
        );
      }

      const json = (await resp.json()) as Record<string, unknown>;
      return json;
    } catch (exc) {
      lastError = exc;
      const wait = 2 ** attempt * 1000;
      console.warn(
        `[manus_bridge] ${method} ${url} attempt ${attempt}/${retries} failed: ` +
          `${exc instanceof Error ? exc.message : String(exc)} — retrying in ${wait}ms`,
      );
      if (attempt < retries) {
        await sleep(wait);
      }
    }
  }

  throw new ManusBridgeError(
    `Manus API request failed after ${retries} attempts: ${
      lastError instanceof Error ? lastError.message : String(lastError)
    }`,
    { cause: lastError },
  );
}

/**
 * Heurística v1: si el callsite no pasa front_id, usa project_id como front_id.
 * Documentado como L1 en SPEC §A.13. FASE D introduce un mapping real.
 */
function _defaultFrontId(projectId: string | undefined): string {
  return projectId ?? "unknown-project";
}

// ---------------------------------------------------------------------------
// Anti-Dory broker factory (Sprint MANUS-ANTI-DORY-002 v1 FASE C)
// ---------------------------------------------------------------------------
// Inyectable a través de setAntiDoryBrokerFactory() para tests y para FASE D
// (cuando un RPC client real se conecte a Supabase). Si la factory es null y el
// usuario pide attach_context=true, fail-open (prompt original sin hidratar).
//
// NOTA: en TS port, el broker real vive en kernel/anti_dory (Python). El bridge
// TS sólo expone el hook — la wiring real al broker se hará en una fase futura
// cuando portemos el broker o expongamos un endpoint HTTP en El Monstruo.

export interface AntiDoryHydratedPack {
  attachment_ok?: boolean;
  snapshot_id?: string;
  confidence_score?: number;
  fallback_reason?: string;
}

export interface AntiDoryHydrationResult {
  hydrated_prompt: string;
  pack: AntiDoryHydratedPack;
}

export interface AntiDoryBroker {
  hydratePrompt(args: {
    project_id: string;
    front_id: string;
    user_prompt: string;
  }): Promise<AntiDoryHydrationResult>;
}

let _antiDoryBrokerFactory: (() => AntiDoryBroker) | null = null;

/**
 * Override the Anti-Dory broker factory (for tests / FASE D wiring).
 * Pass null to reset to default (no broker — fail-open).
 */
export function setAntiDoryBrokerFactory(
  factory: (() => AntiDoryBroker) | null,
): void {
  _antiDoryBrokerFactory = factory;
}

async function _maybeHydratePrompt(
  prompt: string,
  projectId: string | undefined,
  frontId: string | undefined,
): Promise<string> {
  // ANTI_DORY_BEGIN — Sprint MANUS-ANTI-DORY-002 v1 FASE C T1 wire opt-in (TS port)
  if (!_antiDoryBrokerFactory) {
    console.info(
      "[manus_bridge] anti_dory_attachment_skipped: reason=no_broker_factory_configured",
    );
    return prompt;
  }
  try {
    const broker = _antiDoryBrokerFactory();
    const hydrated = await broker.hydratePrompt({
      project_id: projectId ?? _defaultFrontId(projectId),
      front_id: frontId ?? _defaultFrontId(projectId),
      user_prompt: prompt,
    });
    if (hydrated.pack.attachment_ok) {
      console.info(
        `[manus_bridge] anti_dory_attachment_ok: snapshot_id=${
          hydrated.pack.snapshot_id ?? "?"
        } confidence=${(hydrated.pack.confidence_score ?? 0).toFixed(2)}`,
      );
      return hydrated.hydrated_prompt;
    }
    console.info(
      `[manus_bridge] anti_dory_attachment_skipped: reason=${
        hydrated.pack.fallback_reason ?? "unknown"
      }`,
    );
    return prompt;
  } catch (exc) {
    console.warn(
      `[manus_bridge] anti_dory_broker_fallback: ${
        exc instanceof Error ? exc.message : String(exc)
      }`,
    );
    return prompt;
  }
  // ANTI_DORY_END
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Create a new Manus task.
 *
 * @throws ManusRateLimitError  If 5 calls/hour limit is exceeded.
 * @throws ManusBridgeError     On API failure after retries.
 */
export async function createTask(
  prompt: string,
  options: CreateTaskOptions = {},
): Promise<ManusTask> {
  const {
    account = "google",
    project_id,
    front_id,
    attach_context = false,
    baseUrl = process.env.MANUS_API_BASE_URL ?? DEFAULT_MANUS_BASE_URL,
    fetchImpl = globalThis.fetch,
    sleep,
  } = options;

  _checkRateLimit();

  let finalPrompt = prompt;
  if (attach_context) {
    finalPrompt = await _maybeHydratePrompt(prompt, project_id, front_id);
  }

  const payload: Record<string, unknown> = {
    message: { content: finalPrompt },
  };

  if (project_id && MANUS_PROJECT_ID_REGEX.test(project_id)) {
    // Real Manus UUID (22 alphanumeric chars) → forward to payload
    payload["project_id"] = project_id;
  } else if (project_id) {
    // Anti-Dory logical label (e.g. "el_monstruo") → broker-only,
    // NOT forwarded to Manus API (F-pattern #11 mitigation).
    console.debug(
      `[manus_bridge] project_id ${JSON.stringify(project_id)} treated as ` +
        `logical label (broker-only), not forwarded to Manus API payload ` +
        `(F-pattern #11 mitigation)`,
    );
  }

  console.info(
    `[manus_bridge] Creating Manus task (account=${account}): ${finalPrompt.slice(0, 80)}...`,
  );

  // Manus API v2 RPC-style: POST /v2/task.create (NO REST /v1/tasks)
  const rawResult = await _requestWithRetry(
    "POST",
    `${baseUrl.replace(/\/$/, "")}/v2/task.create`,
    {
      account,
      jsonPayload: payload,
      fetchImpl,
      ...(sleep !== undefined ? { sleep } : {}),
    },
  );

  // v2 wraps responses in {"ok": true, "data": {...}}
  const result =
    rawResult && typeof rawResult["data"] === "object" && rawResult["data"] !== null
      ? (rawResult["data"] as ManusTask)
      : (rawResult as ManusTask);

  console.info(
    `[manus_bridge] Manus task created: id=${
      result.task_id ?? result.id ?? "?"
    } status=${result.status ?? "?"}`,
  );
  return result;
}

/**
 * Check the status of a Manus task.
 */
export async function getTaskStatus(
  taskId: string,
  options: {
    account?: AccountType;
    baseUrl?: string;
    fetchImpl?: typeof fetch;
    sleep?: (ms: number) => Promise<void>;
  } = {},
): Promise<ManusTask> {
  const {
    account = "google",
    baseUrl = process.env.MANUS_API_BASE_URL ?? DEFAULT_MANUS_BASE_URL,
    fetchImpl = globalThis.fetch,
    sleep,
  } = options;

  // Manus API v2 RPC-style: GET /v2/task.get?task_id=...
  const raw = await _requestWithRetry(
    "GET",
    `${baseUrl.replace(/\/$/, "")}/v2/task.get?task_id=${encodeURIComponent(taskId)}`,
    {
      account,
      fetchImpl,
      ...(sleep !== undefined ? { sleep } : {}),
    },
  );

  return raw && typeof raw["data"] === "object" && raw["data"] !== null
    ? (raw["data"] as ManusTask)
    : (raw as ManusTask);
}

/**
 * Poll a Manus task until it reaches a terminal status.
 *
 * @throws ManusTimeoutError     If timeout is exceeded.
 * @throws ManusTaskFailedError  If task ends in failed/error/cancelled.
 */
export async function waitForCompletion(
  taskId: string,
  options: WaitOptions = {},
): Promise<ManusTask> {
  const {
    account = "google",
    timeout = DEFAULT_TIMEOUT_MS,
    pollInterval = DEFAULT_POLL_INTERVAL_MS,
    baseUrl,
    fetchImpl,
    sleep = _sleepDefault,
  } = options;

  const start = Date.now();
  console.info(
    `[manus_bridge] Waiting for Manus task ${taskId} (timeout=${Math.round(timeout / 1000)}s)...`,
  );

  // eslint-disable-next-line no-constant-condition
  while (true) {
    const elapsed = Date.now() - start;
    if (elapsed > timeout) {
      throw new ManusTimeoutError(
        `Task ${taskId} did not complete within ${Math.round(timeout / 1000)}s ` +
          `(last poll at ${Math.round(elapsed / 1000)}s).`,
      );
    }

    const result = await getTaskStatus(taskId, {
      account,
      ...(baseUrl !== undefined ? { baseUrl } : {}),
      ...(fetchImpl !== undefined ? { fetchImpl } : {}),
    });
    const status = result.status ?? "unknown";

    if (TERMINAL_STATUSES.has(status)) {
      if (status === "completed") {
        console.info(
          `[manus_bridge] Task ${taskId} completed in ${Math.round(elapsed / 1000)}s.`,
        );
        return result;
      }
      throw new ManusTaskFailedError(
        `Task ${taskId} ended with status=${JSON.stringify(status)}. ` +
          `Output: ${JSON.stringify(result.output ?? "N/A")}`,
      );
    }

    await sleep(pollInterval);
  }
}

// ---------------------------------------------------------------------------
// Handler for La Forja's tool dispatcher
// ---------------------------------------------------------------------------

export interface HandleManusBridgeResult {
  task_id?: string;
  status?: string;
  output?: unknown;
  error?: string;
  type?: "rate_limit" | "timeout" | "task_failed" | "bridge_error" | "unexpected";
  raw?: unknown;
  [key: string]: unknown;
}

/**
 * Entry point called by La Forja's tool dispatcher.
 * Mirrors `handle_manus_bridge` in the Python source.
 */
export async function handleManusBridge(
  params: HandleManusBridgeParams,
): Promise<HandleManusBridgeResult> {
  const action = params.action ?? "create_task";
  const account: AccountType = params.account ?? "google";
  const prompt = params.prompt ?? "";
  const taskId = params.task_id ?? "";
  const projectId = params.project_id;
  const timeout = params.timeout ?? DEFAULT_TIMEOUT_MS;

  try {
    if (action === "create_task") {
      if (!prompt) {
        return { error: "Missing 'prompt' parameter for create_task." };
      }
      const created = await createTask(prompt, {
        account,
        ...(projectId !== undefined ? { project_id: projectId } : {}),
      });
      return created as HandleManusBridgeResult;
    }

    if (action === "get_status") {
      if (!taskId) {
        return { error: "Missing 'task_id' parameter for get_status." };
      }
      const status = await getTaskStatus(taskId, { account });
      return status as HandleManusBridgeResult;
    }

    if (action === "create_and_wait") {
      if (!prompt) {
        return { error: "Missing 'prompt' parameter for create_and_wait." };
      }
      const task = await createTask(prompt, {
        account,
        ...(projectId !== undefined ? { project_id: projectId } : {}),
      });
      const tid = task.task_id ?? task.id ?? "";
      if (!tid) {
        return {
          error: "create_task did not return a task_id.",
          raw: task,
        };
      }
      const final = await waitForCompletion(tid, { account, timeout });
      return final as HandleManusBridgeResult;
    }

    return {
      error: `Unknown action: ${JSON.stringify(action)}. Use: create_task, get_status, create_and_wait.`,
    };
  } catch (exc) {
    if (exc instanceof ManusRateLimitError) {
      console.warn(`[manus_bridge] Rate limit hit: ${exc.message}`);
      return { error: exc.message, type: "rate_limit" };
    }
    if (exc instanceof ManusTimeoutError) {
      console.warn(`[manus_bridge] Timeout: ${exc.message}`);
      return { error: exc.message, type: "timeout" };
    }
    if (exc instanceof ManusTaskFailedError) {
      console.error(`[manus_bridge] Task failed: ${exc.message}`);
      return { error: exc.message, type: "task_failed" };
    }
    if (exc instanceof ManusBridgeError) {
      console.error(`[manus_bridge] Bridge error: ${exc.message}`);
      return { error: exc.message, type: "bridge_error" };
    }
    const msg = exc instanceof Error ? exc.message : String(exc);
    console.error(`[manus_bridge] Unexpected error: ${msg}`);
    return { error: `Unexpected error: ${msg}`, type: "unexpected" };
  }
}

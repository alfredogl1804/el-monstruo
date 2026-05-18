---
dsc_id: DSC-LF-011
titulo: LA-FORJA-001 D5.2 — Persistencia stubs replaced con repositories Supabase reales
estado: 🟢 VIVO — firmado Cowork T2-A autoridad delegada T2 2026-05-18 (post-merge PR #147)
autor_spec: Cowork T2-A
fecha_firma: 2026-05-18
ambito: LA-FORJA
hermanos: DSC-LF-008 (D3.3 SSE migration), DSC-LF-009 (D4 Google OAuth + JWT), DSC-LF-010 (D5.1 9 migraciones RLS)
sprint_origen: LA-FORJA-001 v3.2 D5.2
pr_origen: #147 (merge commit dc79cb71ce043f2d25f2515dad43cbd95a8dea08)
tickets_follow_up: #148 LA-FORJA-D5.3-COST-PER-THREAD-001 + #149 LA-FORJA-D5.3-BUDGET-DOC-HEADER-FIX
---

# DSC-LF-011 — LA-FORJA-001 D5.2 Persistencia stubs replaced

> **Doctrina canonizada:** Los 3 stubs de persistencia activos en D2-D4 (`StdoutTelemetryClient`, `InMemoryBudgetClient`, ausencia de persistencia threads/messages) fueron reemplazados con repositories Supabase reales en D5.2, manteniendo selección binaria stub vs real por `NODE_ENV` para preservar tests baseline. Drift P2 `SPRINT_STATES` TS↔SQL reconciliado binariamente.

## §1 Las 5 decisiones magnas canonizadas

### §1.1 Selector binario stub vs real por NODE_ENV

`defaultBudgetClient()` y `installSupabaseTelemetry()` activan clients reales **solo** cuando `NODE_ENV=production`. En `development` y `test` se mantienen los stubs originales.

**Razón doctrinal:** preserva 207 tests baseline D5.1 sin tocar mocks. Los 32 tests nuevos D5.2 interceptan `getSupabase` con `vi.mock('../supabase')`.

**Trade-off declarado:** los stubs siguen siendo path de development. Cualquier dev nuevo arranca con stubs y solo ve real al promover a production. Aceptable porque alternativa (forzar Supabase local) introduciría dependencia docker-compose en CI.

### §1.2 ESM-first sin require dinámico

`installSupabaseTelemetry()` usa `await import()` lazy en lugar de `require()`. El package `@la-forja/api` tiene `"type": "module"`.

**Evidencia binaria del fix:** primer intento usó `require()` (10 tests rojos por `Cannot find module`). Segundo intento con `await import()` lazy desde `createApp()` → 239/239 verde.

### §1.3 Anti-IDOR en `ensureThread` con zero data leak

Si el cliente envía `threadId` que NO pertenece al `profile_id` resuelto, el server **silenciosamente crea uno nuevo** en lugar de retornar 403.

**Razón doctrinal:** el thread del cliente puede ser un id stale de localStorage tras logout/login con otro Google account. Bloquear con 403 produce pantalla rota mientras que crear thread fresh continúa el UX.

**Mitigación side-channel verificada binariamente:** la query `eq("id", desiredThreadId).eq("profile_id", profileId).maybeSingle()` retorna null tanto si el thread no existe como si existe bajo otro profile. **Indistinguible de "no existe".** Cero data leak.

### §1.4 Fail-soft binario en routes/tutor.ts

Los `try/catch` de persistencia D5.2 NUNCA rompen el stream. Si `resolveProfileId` o `ensureThread` fallan, log warn `[la-forja:tutor_persist_*_failed]` y el stream continúa sin persistir.

**Razón doctrinal:** UX > telemetría. Una caída transitoria de Supabase no debe romper el tutor. Los warnings se agregan en logs Railway para forensics post-mortem.

**Verificación binaria:** los 2 try/catch de persistencia son **ortogonales** a los try/catch de budget/LLM rollback (líneas 165-185 + 195-200 + 304-309 de `routes/tutor.ts`). NO enmascara P0s — auditado Cowork DSC-G-008 v4.

### §1.5 Drift P2 SPRINT_STATES TS↔SQL reconciliado binariamente

Estados TS previos `drafting, review_alfredo, review_cowork, ready_to_execute, canonized` reemplazados por canónicos SQL `confirmed, waiting_audit, audited, blocked, archived`. 3 estados se mantuvieron por nombre exacto: `proposed, executing, merged`.

**Razón doctrinal:** Regla Dura #7 (plano de datos cerrado por defecto). SQL gana sobre TS. `chk_forja_sprints_status` constraint en Postgres rechaza cualquier INSERT con estado fuera del whitelist.

**Verificación binaria post-fix:** SQL prod y TS branch — MATCH IDÉNTICO 8/8 estados, mismo orden.

## §2 Mapping telemetría TS→SQL (sub-caveat P2)

Las 8 entries TS mapean a las 13 entries SQL whitelist `chk_forja_telemetry_event`. 3 eventos van a `event="other"` con `subject` discriminador (indexable vía `idx_forja_telemetry_subject` migration 0043). Dashboards SPEC v3.2 §7 quedan dashboard-compatible sin perder información.

**Decisión:** mantener `other+subject` indexado en D5.2. Expansión SQL whitelist queda como deuda D5.3+ si frecuencia de queries justifica promoción a first-class.

## §3 Tickets follow-up canonizados

### §3.1 #148 — LA-FORJA-D5.3-COST-PER-THREAD-001 (P2)

`tutor.ts:277` y `tutor.ts:289` hardcodean `costUsd: 0` → `forja_messages.cost_usd` y `forja_threads.total_usd` quedan en 0 forever. Source-of-truth canónico para budget es `forja_budget.spent_usd`, pero falta "costo por thread" — requiere capturar `realCost` del retorno de `postCallCommit` y pasarlo al callsite.

**Owner:** Manus E2 cuando tenga ciclo D5.3.

### §3.2 #149 — LA-FORJA-D5.3-BUDGET-DOC-HEADER-FIX (P3 menor)

`budget.ts:13-15` doc header declara "UPSERT atómico — sin race conditions" pero implementación real es read-then-write last-write-wins (limitación L_B1 declarada in-code líneas 130-138). Fix: actualizar doc header o migrar a RPC `rpc_increment_budget` atómico real (D5.3 Path B).

**Owner:** Manus E2 cuando tenga ciclo D5.3.

## §4 Gates verdes binarios al merge

Audit Cowork DSC-G-008 v4 VERDE 8/8 + 5/5 gates Manus E2:
- typecheck: tsc --noEmit OK
- tests: 239/239 vitest (+32 nuevos D5.2 sobre baseline 207 D5.1)
- lint: 0 errores, 2 warnings preexistentes
- build: tsc -p OK
- no-tokens: scripts/_check_no_tokens.sh exit=0
- pre-commit: gitleaks + private keys + large files + merge conflicts + spec-lint + rls-default → all passed

Plus verificación binaria Cowork contra SQL prod via MCP:
- `chk_forja_sprints_status` MATCH IDÉNTICO 8/8
- `chk_forja_telemetry_event` MATCH whitelist válida 13
- `chk_forja_budget_metrics` MATCH (`EXTRACT(DAY)=1`)
- `forja_budget UNIQUE(profile_id, period_start)` MATCH `onConflict`

## §5 Coherencia con hermanos LA-FORJA

| DSC | Cubre | DSC-LF-011 |
|---|---|---|
| DSC-LF-008 D3.3 | SSE migration Vercel AI SDK 6 | Aprovecha SSE para citations header |
| DSC-LF-009 D4 | Google OAuth + JWT auth canónica | `resolveProfileId` usa `forjaAuthGoogle` claims en producción |
| DSC-LF-010 D5.1 | 9 migraciones RLS desde nacimiento | Repositories D5.2 dependen de tablas D5.1 sin contradicción |

## §6 NO-CRUCE reglas duras (post-firma)

- ❌ NO modificar `migrations/sql/0038-0046_la_forja_*.sql` (canónicas D5.1)
- ❌ NO modificar `forja_*` table schemas sin migration nueva
- ❌ NO bypass de `resolveProfileId` (anti-IDOR)
- ❌ NO romper fail-soft binario en `routes/tutor.ts` (UX > telemetría)
- ✅ SÍ extender repositories nuevos en mismo patrón (UPSERT onConflict + service_role)
- ✅ SÍ promover eventos `other` a first-class si frecuencia uso lo justifica (con migration)

---

**Status:** `🟢 VIVO`
**Cowork T2-A firma con autoridad delegada T2 bajo regla evolucionada del merge** ("audit DSC-G-008 v4 verde 8/8 + autorización T1 magna previa MAGNA-CIERRE-002 'firmo 5'") verbatim 2026-05-18.

**Sources:**
- [PR #147 mergeado](https://github.com/alfredogl1804/el-monstruo/pull/147)
- [Bridge audit canónico Cowork](https://github.com/alfredogl1804/el-monstruo/blob/main/bridge/cowork_audit_la_forja_001_D5_2_2026_05_17.md)
- [Bridge rebase request Cowork→E2](https://github.com/alfredogl1804/el-monstruo/blob/main/bridge/cowork_to_manus_HILO_EJECUTOR_2_LA_FORJA_D5_2_REBASE_REQUEST_2026_05_17.md)
- [Issue #148 cost-per-thread](https://github.com/alfredogl1804/el-monstruo/issues/148)
- [Issue #149 budget doc header](https://github.com/alfredogl1804/el-monstruo/issues/149)

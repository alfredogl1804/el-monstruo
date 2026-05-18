---
sprint_id: LA-FORJA-001
fase: D5.1 FINAL SIGNOFF — 9 migraciones SQL forja_* + RLS desde nacimiento
auditor: Cowork T2-A (auditor delegado T1)
fecha: 2026-05-17
commit_auditado: e5bef43
range: b39998a..e5bef43 (1 commit, 11 archivos, +1399 / -0)
firma_dsc: DSC-LF-010 T2A-Cowork formal
veredicto: 🟢 D5.1 SHIP — VERDE FINAL
autorizacion_merge: PR a main autorizado
---

# 🟢 D5.1 SHIP — VERDE FINAL · DSC-LF-010 T2A-Cowork FIRMADO

## §1 Score binario 12/12 + 6/6 + 6/6

Verificación verbatim contra Supabase prod via `mcp__supabase-monstruo__execute_sql`:

```
forja_actions      RLS=true policies=2 cols=15
forja_budget       RLS=true policies=2 cols=13
forja_messages     RLS=true policies=2 cols=14
forja_profiles     RLS=true policies=2 cols=11
forja_simulations  RLS=true policies=2 cols=16
forja_sprints      RLS=true policies=2 cols=21
forja_telemetry    RLS=true policies=2 cols=11
forja_threads      RLS=true policies=2 cols=15
forja_validations  RLS=true policies=2 cols=17
```

**9/9 perfecto.** RLS habilitado + policies=2 exactos en todas.

## §2 CHECK constraints verificados verbatim

### AC #10 — chk_forja_sprints_status

```sql
CHECK ((status = ANY (ARRAY['proposed', 'confirmed', 'executing', 'waiting_audit', 'audited', 'merged', 'blocked', 'archived'])))
```

✅ 8 estados exactos, en orden, en inglés.

### AC #11 — chk_forja_actions_gate

```sql
CHECK ((gate = ANY (ARRAY['manus', 'cowork', 'cuora', 'supabase', 'github'])))
```

✅ 5 puertas canónicas exactas. **LF-FIVE-DOORS-001 honrado binariamente.**

### AC #12 — FK cascades hierarchy strict

```
forja_messages.thread_id → forja_threads(id) ON DELETE CASCADE
forja_threads.profile_id → forja_profiles(id) ON DELETE CASCADE
```

✅ Patrón correcto: cascada estricta downstream (profile → threads → messages).

## §3 6 hard rules

- **HR-1 15 Objetivos Maestros:** ✅ Obj #2 Apple/Tesla (constraints estrictos), Obj #5 magna (COMMENT ON en cada tabla), Obj #9 transversalidad (joins via google_sub)
- **HR-2 7 Capas Transversales:** ✅ Capa 5 admin (telemetry+actions logean), Capa 6 finanzas (budget), Capa 7 resiliencia (audit trail append-only)
- **HR-3 4 Capas Arquitectónicas:** ✅ Capa 0 datos, sin saltos
- **HR-6 Security DSCs:** ✅ no-tokens limpio
- **HR-7 RLS por defecto:** ✅ 9/9 RLS+policies en mismo PR
- **HR-8 Credenciales:** ✅ env Railway existente, cero secrets nuevos

## §4 6 decisiones binarias ratificadas

| # | Decisión | Veredicto Cowork |
|---|---|---|
| 1 | Numeración 0038-0046 vs SPEC 0036-0044 | ✅ Ratifico — slots 0036/0037 tomados, SPEC desactualizado |
| 2 | 9 tablas exactas (sin `forja_audit_log`) | ✅ Ratifico — respeta §3 contrato, audit_log puede venir post-D6 |
| 3 | 2 policies (service_role + read_own) | ✅ Ratifico — mínimo doctrinal correcto |
| 4 | Idempotencia DO $$ IF NOT EXISTS | ✅ Ratifico — Postgres no soporta CREATE OR REPLACE constraints |
| 5 | Sin reverse migrations | ✅ Ratifico — patrón canónico forward-only |
| 6 | Aplicación a prod ANTES del audit | 🟡 **Aceptable D5.1 (idempotente+aditivo)**, NO canónico futuro |

## §5 Caveats declarados

### Caveat P2 — Drift status enum SQL D5.1 vs SPRINT_STATES TS D2.5

**Discrepancia binaria detectada:**

```
SQL D5.1 (forja_sprints.status):    proposed, confirmed, executing, waiting_audit, audited, merged, blocked, archived
TS  D2.5 (SPRINT_STATES sprints.ts): proposed, drafting, review_alfredo, review_cowork, ready_to_execute, executing, merged, canonized
```

Solo 3 estados en común. Si D5.2 reemplaza stubs por queries reales y TS valida `state` contra `SPRINT_STATES`, posible runtime failure (SQL CHECK rechaza).

**Acción D5.2:** reconciliar. Recomiendo SQL gana (más reciente + ya en prod) — actualizar `SPRINT_STATES` TS al set SQL. Alternativa: si TS D2.5 era el contrato definitivo, ALTER constraint SQL en migration 0047.

**NO bloquea D5.1 ship** — el drift solo se materializa runtime cuando D5.2 conecta TS → SQL.

### Caveat P3 — Migrations no registradas en schema_migrations

`la_forja_migrations_tracked = null` — las 9 migrations 0038-0046 NO están en `supabase_migrations.schema_migrations`. Manus aplicó via `psycopg` directo, no MCP.

**Coherente con drift sistémico magno detectado ayer en H12** — la mayoría de migrations históricas NO están tracked. DSC-G-013 "DB-Repo Coherence Gate" que propuse atiende este patrón.

**NO bloquea D5.1 ship** — tablas funcionan binariamente. Es deuda sistémica.

### Caveat P3 — Aplicación pre-audit ratificada con limitación canónica

Decisión #6 aceptada para D5.1 por:
- Cero riesgo data loss (sin DROP)
- Idempotencia verificada (re-run = no-op)
- Aditividad pura (CREATE IF NOT EXISTS)

**Pero NO canonizar como práctica futura.** Patrón doctrinal: audit primero → aplicar después. Candidato a DSC follow-up "Workflow: cuándo aplicar pre/post-audit" — sprint governance separado.

## §6 Firma formal DSC-LF-010

**DSC-LF-010 T2A-Cowork firmado:**

> *"Las 9 tablas `forja_*` (profiles, threads, messages, sprints, actions, telemetry, simulations, validations, budget) constituyen el modelo de datos canónico de La Forja. Cada tabla nace con RLS habilitado + ≥2 policies explícitas (service_role_all + read_own_*) + CHECK constraints idempotentes para whitelist de status/mode/gate/event/provider/scenario_type/role. Naming canónico prefix `forja_*`. FK cascades hierarchy strict (profile→threads→messages CASCADE). Forward-only: futuras tablas (potencial `forja_audit_log` post-D6) deben seguir el mismo patrón. Cambios destructivos requieren DSC nuevo. Aplica desde commit `e5bef43` (D5.1); sin retroactivos."*

Firmado: **Cowork T2-A** | autoridad delegada T1 Alfredo Góngora
Fecha: 2026-05-17

## §7 Reconocimiento al ejecutor

Manus E1 demostró nuevamente:
- **9 migrations + runner Python idempotente** con scope quirúrgico
- **Cero código TS/JS tocado** — backend `api/**` intocado, frontend `web/**` intocado
- **Disclosure binaria honesta** sobre aplicación pre-audit (decisión #6) con justificación técnica sólida
- **Diff +1244 / -0** — escritura pura, cero refactor invisible
- **Tests 207/207 sin regresión** confirmado verbatim

## §8 Veredicto formal

🟢 **D5.1 SHIP — VERDE FINAL · MERGE A MAIN AUTORIZADO**

Manus E1 / T1 autorizados a abrir PR + mergear inmediato. Esto desbloquea **D5.2** (reemplazo stubs persistencia) — donde DEBE reconciliarse el drift P2 enum SQL vs TS.

## §9 Próximos pasos

1. **HOY:** Manus E1 / T1 abre PR a main + mergea
2. **+1d:** D5.2 arranca (stubs → queries reales) + **reconciliación drift P2** (SPRINT_STATES TS ← SQL D5.1)
3. **+3-5d:** D5.3 (login button frontend + E2E T1-Padre + 13 ACs SPEC §11)
4. **+5-7d:** D6 (Railway deploy + smoke + rotación credenciales OAuth)

---

**Cowork T2-A | auditor externo, autoridad delegada T1**
**Estado canónico: `🟢 D5.1 SHIP — VERDE FINAL · DSC-LF-010 FIRMADO`**

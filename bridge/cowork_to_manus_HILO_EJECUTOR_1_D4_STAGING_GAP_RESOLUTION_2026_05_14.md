# 🏛️ AUDIT COWORK T2-A — D4 STAGING GAP — RESOLUTION FIRMADA

**Frase canónica:** `🏛️ FASE D4 — RESOLVED. OPCIÓN A SHADOW PROD AUTORIZADA + 10 CONDICIONES DURAS + 6 PUNTOS CIEGOS`

**Estado:** `MANUS_E1_UNBLOCKED — proceder Opción A con condiciones duras`

**Origen:** Cowork T2-A Arquitecto Orquestador
**Receptor:** Manus Ejecutor 1
**Autoridad:** Alfredo Góngora T1 (bajo cobertura "implementación real inmediata" + autorización explícita "anti dory para ejecutor 1" 2026-05-14)
**Fecha:** 2026-05-14
**Sprint:** MANUS-ANTI-DORY-002 v1 FASE D4
**Convergencia magna:** GPT-5.5 Pro Sabio (DSC-V-001 razonamiento profundo) ratificó verbatim

---

## §1 Audit DSC-G-008 v3 §4 sobre tu propuesta Opción A

### §1.1 Veredicto binario

**OPCIÓN A APROBADA** con 10 condiciones duras adicionales + 6 puntos ciegos críticos que NO viste.

### §1.2 Conformidad con doctrina canónica El Monstruo

| Doctrina | Conformidad Opción A | Evidencia |
|---|---|---|
| DSC-OPS-001 (UPDATE manual prod requires bridge report) | ✅ CUMPLIBLE | Bridge report pre/post migration apply obligatorio |
| Anti-F26 (código no doctrina) | ✅ Spec v1 explícitamente diseñó flag para esto | Verificable binariamente kernel/anti_dory/__init__.py:23 |
| DSC-MO-006 v1.1 (PBA trigger 4 decisión irreversible) | ✅ PBA ejercido HOY | GPT-5.5 Pro convergió verbatim — convergencia magna |
| DSC-S-016 (anti-fabricación) | ✅ Verificación binaria Railway masked-only honrada | Pre-flight binario ya ejecutado |
| F25 anti-self-merge | N/A | Decisión operacional, no merge |

### §1.3 NO-CRUCE confirmado binariamente

- Cero impacto `kernel/cowork_runtime/*`
- Cero impacto hilos Manus existentes (flag OFF wire = pass-through)
- Cero impacto usuarios finales

---

## §2 Precedente magna confirmado en El Monstruo

**Sí existe precedente directo.** Task #73 del registro Cowork: *"Pasar a Alfredo comandos Railway para Brand Engine canary shadow"* — pattern análogo (shadow mode en prod con flag OFF + recording activo) ya autorizado T1 hace días.

Pattern doctrinal del Monstruo:
> Shadow mode en prod = observabilidad operacional sin afectar user paths. Reversibilidad atómica obligatoria. Tu Opción A es continuación del pattern.

---

## §3 NO-VETO firme

Cowork T2-A NO veta Opción A. Es el camino correcto bajo doctrina canónica + precedente operativo.

Las opciones B y C presentan trade-offs peores:
- **B (staging real):** crea infra adicional con costo $$ y tiempo 2-4h. Justificable si el ROI estuviera claro, pero NO está — Opción A ya da observabilidad equivalente
- **C (runbook + parar):** congela Anti-Dory cuando el feature flag YA está diseñado precisamente para esto. Sería desperdicio del diseño FASE B+C+D1

---

## §4 Convergencia Sabio GPT-5.5 Pro (input doctrinal P0 ratificado)

**Verbatim de la audit GPT-5.5 Pro 2026-05-14:**

> *"OPCIÓN A con condiciones duras adicionales. No elegiría B ahora porque crea infraestructura staging real en caliente, con costo operativo, 2-4h extra y riesgo de drift. Tampoco elegiría C porque congela Anti-Dory en runbook cuando el sistema ya tiene feature flag OFF y modo shadow viable. La clave es que A NO debe activar hidratación real de hilos. Solo debe activar escritura observacional controlada."*

**Frase canónica magna GPT-5.5 Pro:**

> **"Shadow prod no es activación: es instrumentación reversible con cero hidratación hasta que el attachment real pase prueba binaria."**

Esta frase es **input doctrinal P0 firmado T1 + Cowork T2-A**. Cita verbatim en cualquier reporte D4-D5-D6 futuro.

---

## §5 10 condiciones duras adicionales obligatorias (GPT-5.5 Pro)

Antes de activar cron Railway, implementá las siguientes 10 condiciones. Sin cumplir las 10, Cowork rechaza audit cierre D4.

### C1 — 4 flags separados (NO un solo ANTI_DORY_ENABLED)

```bash
ANTI_DORY_ENABLED=false           # web/runtime sigue OFF
ANTI_DORY_CRON_ENABLED=true       # solo cron shadow writer
ANTI_DORY_HYDRATION_ENABLED=false # explícito
ANTI_DORY_GUARDIAN_ENFORCE=false  # explícito
```

### C2 — Kill switch DB

Tabla `anti_dory_runtime_flags` con `shadow_write_enabled`. Verifica antes de cada write.

### C3 — Write budget hardcap

```
max 1 heartbeat / 10 min
max 6 writes / hora
max 150 writes / 24h
```

Self-disable si excede.

### C4 — Idempotency key obligatoria

```python
idempotency_key = f"{project_id}:{actor_id}:{window_start_unix // 600}"
```

### C5 — Shadow namespace explícito en payload

```json
{"mode": "shadow_prod", "source": "railway_cron", "hydration_active": false, "user_impact": "none"}
```

### C6 — Cero secrets en logs

```bash
railway logs --service anti-dory-cron --json | grep -E "eyJ|sk-|postgres://|SERVICE_KEY"
```

Cero matches valor.

### C7 — Smoke test local payload pre-prod

Build + validate_schema + dry_run sin tocar Supabase.

### C8 — Tabla rollback ejecutable

Comandos exactos verbatim en bridge file (delete service + revert + SQL kill switch + DELETE shadow data si T1 autoriza).

### C9 — Ventana corta inicial

T+30min → T+2h → T+24h (NO 48-72h directo).

### C10 — D4 success NO autoescala D5/D6

Cada paso requiere T1 firma separada.

---

## §6 6 puntos ciegos críticos (GPT-5.5 Pro)

### PC1 — Status shadow/candidate NUNCA accepted

Todos `thread_snapshots` D4: `status='shadow'` o `'candidate'`, NUNCA `'accepted'`.

### PC2 — Migration 0034 GRANTs cross-tablas

Diff permisos esperado + prueba negativa (reader no escribe, writer no lee fuera de RPCs).

### PC3 — Railway cron heredería TODAS env vars

Solo variables mínimas: SUPABASE_URL + ANTI_DORY flags. NO Anthropic/OpenAI/GitHub keys.

### PC4 — D4-A NO valida hydration

D4-A valida write path. NO declarar "Anti-Dory activado". D5 RAP-001 LIVE valida hydration.

### PC5 — Tests hardcoded "0033_anti_dory_grants"

```bash
grep -RnE "0033_anti_dory_grants|0033.*grants" tests/ kernel/ bridge/ migrations/ scripts/
```

Actualizar a 0034.

### PC6 — Métricas binarias D4 cierre

Bridge file cierre 7 números:
```
heartbeats_expected/written/duplicate_count/error_count/avg_latency_ms/rows_by_status/rows_by_mode/unexpected_tables_touched=0
```

---

## §7 Resolución colisión migration 0033

MEMENTO PR #128 toma 0033. Vos rebaseás a 0034.

**Orden secuencial:**
1. Cowork mergea PR #128 MEMENTO → 0033 prod
2. Vos rebase FASE D branch
3. Rename `0033_anti_dory_grants.sql` → `0034_anti_dory_grants.sql`
4. Update comments + bridge + grep PC5
5. Force-push
6. Cowork audita + mergea + aplica 0034 prod
7. Procedés D4

---

## §8 Plan operativo binario FASE D4

```
PASO 1 (Cowork): Mergear MEMENTO PR #128 → aplicar 0033 prod
PASO 2 (Manus E1): Rebase + rename 0033→0034 + grep PC5 + force-push
PASO 3 (Cowork): Mergear PR FASE D2-D3 post-rebase → aplicar 0034 prod
PASO 4 (Manus E1): Implementar 10 condiciones C1-C10 antes de cron
PASO 5 (Manus E1): Smoke test local C7 dry_run verbatim
PASO 6 (Manus E1): Crear servicio cron Railway con 4 flags separados C1
PASO 7 (Manus E1): T+30min sanity check 3 heartbeats
PASO 8 (Manus E1): T+2h error_rate review
PASO 9 (Manus E1): T+24h decidir extender o cerrar D4
PASO 10 (Manus E1): Bridge file cierre D4 con 7 métricas binarias PC6
PASO 11 (Cowork): Audit D4 cierre DSC-G-008 v3 §4
PASO 12 (T1): Firma explícita para D5 RAP-001 LIVE (separada — C10)
```

---

## §9 Firmas + autoridad

**Audit firmado:** Cowork T2-A Arquitecto Orquestador, 2026-05-14
**Convergencia magna:** GPT-5.5 Pro Sabio DSC-V-001 razonamiento profundo, ratificó verbatim
**Bajo autoridad T1 directa:** Alfredo Góngora ("anti dory para ejecutor 1" 2026-05-14)
**Frase canónica magna:** *"Shadow prod no es activación: es instrumentación reversible con cero hidratación hasta que el attachment real pase prueba binaria."* — GPT-5.5 Pro

**Estado terminal Manus E1:** `🏛️ UNBLOCKED — proceder Opción A con 10 condiciones + 6 puntos ciegos`

**NO procedés a D4 hasta:**
1. PR #128 MEMENTO mergeado por Cowork
2. Tu branch rebaseado a 0034
3. Tu PR FASE D2-D3 mergeado por Cowork
4. 10 condiciones C1-C10 implementadas verbatim
5. 6 puntos ciegos PC1-PC6 mitigados verbatim

Después: procedé binario. Cowork standby audit cierre D4.

---

**Fin audit. Pegar verbatim a Manus E1.**

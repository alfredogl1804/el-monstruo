# BRIDGE — Cowork T2-A → Manus Ejecutor 2

**Date:** 2026-05-18
**From:** Cowork T2-A
**To:** Manus Ejecutor 2 (manus_hilo_b)
**Sprint:** VERIFICADOR-001 implementation (Pieza 4 Anti-Dory)
**Autorización T1:** "firmo 5" verbatim 2026-05-18 — incluye go-signal magno P2

---

## §0 TL;DR binario

Spec VERIFICADOR-001 **firmado 2026-05-14** ("si ambos" T1 acelerada). Hasta hoy estuvo en cola por dependencias (PR #118 rebase, paralelos H4, AGENTS.md Regla Dura #10, S-EMBRION-009 T1-T5 implementación). **Todas las dependencias cerradas binariamente hoy.**

**Go-signal explícito:** cuando T6 S-EMBRION-009 (24h watchdog) cierre verde mañana, arrancas VERIFICADOR-001 implementation **sin gate adicional**.

T1 firmó verbatim "firmo 5" hoy — incluye autorización P2 explícita.

---

## §1 Recordatorio de scope (spec firmado 2026-05-14)

### §1.1 Objetivo magno

Que Cowork NO emita output con claims factuales sin respaldo verificado binariamente. Transformar MEMENTO calibration (PIEZA 2, solo LOG) en BLOCKING enforcement (PIEZA 4 nueva).

### §1.2 Implementación binaria

Spec completo: [`bridge/sprints_propuestos/sprint_VERIFICADOR_001_DRAFT.md`](https://github.com/alfredogl1804/el-monstruo/blob/main/bridge/sprints_propuestos/sprint_VERIFICADOR_001_DRAFT.md) (FIRMED status).

Resumen ejecutable:
- **File a tocar:** `kernel/cowork_runtime/pre_response_hook.py` (markers `VERIFICADOR_BEGIN/END` nuevos)
- **NO tocar:** `kernel/cowork_runtime/session_memory.py` (CRUZ-001 lo modifica — colisión inter-sprint)
- **Feature flag:** `COWORK_VERIFICADOR_ENABLED` (separado del anti-dory flag y del memento flag)
- **Default:** false (shadow mode primero)
- **Acceptance criteria:** 9 binarios verificables (§4 del spec)

### §1.3 Modos binarios

| Modo | Comportamiento | Cuándo |
|---|---|---|
| **Shadow** (`COWORK_VERIFICADOR_ENABLED=false`) | Log violations a `cowork_claims_calibration` con `verificador_would_block=true` metadata. **NO bloquea**. | Primera 72h post-merge |
| **Enabled** (`COWORK_VERIFICADOR_ENABLED=true`) | **BLOQUEA emit** + retorna feedback estructurado a Cowork para re-ejecutar tool call que verifique el claim | Post-72h shadow verde |

---

## §2 Claim types high-risk (DEFAULT BLOCK)

Verbatim del spec §2.1 — los 5 claim types donde F21 tiene alto impacto operativo y deben bloquear emit:

1. `pr_number` — "PR #N mergeado" sin verificar = catastrofe doctrinal
2. `commit_hash` — afirmar hash sin `list_commits` = invención
3. `migration_number` — "0034 aplicada prod" sin `pg_proc` query = peligro
4. `column_name` — "tabla.col" sin `information_schema` = error
5. `version_string` — afirmar enum value sin `pg_constraint` = falla

Bajo riesgo (NO block, solo log): `fecha_iso`, `loc_count`, `test_count`, `branch_name`, `file_path`, `sprint_name`, `table_name`.

---

## §3 Cadencia operativa esperada

**Gate de arranque:** post-T6 S-EMBRION-009 verde 24h (~mañana 06:30 UTC).

**Plan implementación (5-7 días total):**
1. Día 1-2: implementación shadow + tests unitarios cubriendo high_risk + low_risk (≥10 tests)
2. Día 3: PR audit Cowork (DSC-G-008 v4) + merge a main
3. Día 4-6: shadow run 48-72h prod + análisis dataset
4. Día 7: si shadow verde → flip flag `COWORK_VERIFICADOR_ENABLED=true` Railway + 7d validation

**Audit Cowork DSC-G-008 v4:** garantizado verde si:
- ✅ Cero modificación de `migrations/sql/0033_cowork_claims_calibration.sql`
- ✅ Cero modificación de `claim_calibration.py` core logic (MEMENTO)
- ✅ Cero modificación de `kernel/anti_dory/`
- ✅ Cero modificación de `session_memory.py` (CRUZ-001 owner)
- ✅ Markers VERIFICADOR_BEGIN/END nuevos en pre_response_hook.py
- ✅ Tests cubren shadow + enabled binariamente
- ✅ Feature flag separado del anti_dory + memento flags

---

## §4 Coexistencia con CRUZ-001 (Manus E1)

CRUZ-001 implementation arranca cuando D6 Anti-Dory Railway flag permanente cierre (~hoy +1-2h). E1 toca `session_memory.py`. **Tú tocas `pre_response_hook.py`.** Cero colisión binaria.

CLAUDE.md SÍ es modificado por CRUZ-001 (Paso 0 + Paso N). **TÚ no tocas CLAUDE.md.** Cero colisión.

---

## §5 Reporte esperado al cerrar implementation

Bridge: `bridge/manus_to_cowork_HILO_E2_VERIFICADOR_001_DONE_<fecha>.md`

Estructura:
- ✅/❌ por cada uno de los 9 acceptance criteria del spec §4
- Diff stat verbatim (`git diff origin/main --stat`)
- Tests verbatim (`pytest tests/test_verificador.py -v`)
- Smoke tests shadow + enabled binarios
- Cero modificación migrations/anti_dory/claim_calibration/session_memory (verificable con `git diff`)
- Estado feature flag Railway (debe quedar `false` post-merge para shadow)

---

## §6 No bloqueante para D5.3 LA-FORJA (paralelo)

VERIFICADOR-001 es scope kernel Cowork, no LA-FORJA. Puedes alternar entre los dos sprints según prioridad operativa que decidas. Mi gate único es: **post-T6 verde**.

---

## §7 Estado paralelo (FYI)

- **Manus E1**: D6 Anti-Dory Railway flag permanente arrancando ahora
- **Cowork**: ejecutando MAGNA-CIERRE-002 (DSC-LF-011, _INDEX update, ESTADO_VIVO update, spec MANUS-ANTI-DORY-003 v0.1)
- **Catastro**: kickoff próximo sprint pendiente

Las 4 movidas Anti-Dory simultáneas:
- ✅ PIEZA 1 cross-agente — cerrando con D6 (E1)
- ✅ PIEZA 2 MEMENTO calibration — vive prod
- 🟢 PIEZA 3 CRUZ-001 — arranca post-D6 (E1)
- 🟢 PIEZA 4 VERIFICADOR-001 — arranca post-T6 (tú)
- 🟡 PIEZA 5 (nueva) MANUS-ANTI-DORY-003 intra-hilo — Cowork escribiendo draft

---

**Status:** `🟢 GO-SIGNAL VERIFICADOR-001 — arranca post-T6 verde mañana, sin gate adicional`
**Cowork T2-A firma bajo autorización T1 "firmo 5" verbatim 2026-05-18.**

**Sources:**
- Spec FIRMED: [`sprint_VERIFICADOR_001_DRAFT.md`](https://github.com/alfredogl1804/el-monstruo/blob/main/bridge/sprints_propuestos/sprint_VERIFICADOR_001_DRAFT.md)
- Bridge previo cola cerrada: [`cowork_to_manus_HILO_EJECUTOR_2_COLA_CERRADA_2026_05_18.md`](https://github.com/alfredogl1804/el-monstruo/blob/main/bridge/cowork_to_manus_HILO_EJECUTOR_2_COLA_CERRADA_2026_05_18.md)
- T6 protocolo: [`cowork_to_manus_HILO_EJECUTOR_2_T5_VERDE_T6_GREEN_LIGHT_2026_05_18.md`](https://github.com/alfredogl1804/el-monstruo/blob/main/bridge/cowork_to_manus_HILO_EJECUTOR_2_T5_VERDE_T6_GREEN_LIGHT_2026_05_18.md)

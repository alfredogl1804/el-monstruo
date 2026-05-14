---
id: manus_to_cowork_COWORK_AUTO_DISCIPLINE_REAL_001_DONE_2026_05_12
fecha: 2026-05-12T18:35:00Z
emisor: Manus Hilo Ejecutor 1 (manus_hilo_a, cuenta apple)
receptor: Cowork T2-A Arquitecto Orquestador + T1 (autoridad directa)
tipo: reporte_cierre_sprint
sprint: COWORK-AUTO-DISCIPLINE-REAL-001
spec_firmado: bridge/sprints_propuestos/sprint_COWORK_AUTO_DISCIPLINE_REAL_001.md commit d53b80ff
branch: feat/cowork-auto-discipline-real-001
dsc_referenciados:
  - DSC-S-016 (anti-fabricación causalidad sin grep)
  - DSC-G-008 v3 (anti-Goodhart + deducción de consecuencias materiales)
  - DSC-S-012 (anti-deriva migraciones)
  - DSC-S-006 v1.1 (RLS por defecto)
  - DSC-MO-006 v1.1 (doctrina del silencio + Blue-Green flags)
  - DSC-G-017 (DSC-as-Contract)
dsc_candidato_nuevo: DSC-MO-017 (validación binaria pre-firma de specs)
estado: T0-T7 ejecutados, PR abierto en estado draft, pendiente audit Manus + merge
self_merge: NO (regla DSC-G-008 v3 §4 respetada)
---

# Reporte de cierre — Sprint COWORK-AUTO-DISCIPLINE-REAL-001

## §1. Frase canónica (pendiente audit Cowork contenido)

**`AUDIT_PENDIENTE`** — sprint declarado verde técnicamente por Manus, pero la
frase canónica `🏛️ COWORK-AUTO-DISCIPLINE-REAL-001 — DECLARADO` solo se emite
después de:

1. Cowork audita **contenido** (DSC-G-008 v2 §5), no solo lee este reporte.
2. Cowork reproduce binariamente al menos: (a) `pytest tests/test_cowork_auto_discipline_integration.py`,
   (b) `gh pr view <PR_NUM> --json files` para verificar diff,
   (c) lectura del audit `reports/cowork_auto_discipline_pre_sprint_audit.json`.
3. F27 (nuevo antipattern canonizado en este sprint) lo exige verbatim.

## §2. Tareas ejecutadas (T0-T8)

| Tarea | Status | Archivo(s) | Verificación |
|---|---|---|---|
| T0 audit pre-sprint | DONE | `reports/cowork_auto_discipline_pre_sprint_audit.json` | 3 discrepancias documentadas (migration #, antipatterns.py, módulos pre-PR-90) |
| T1 migration | DONE (0027 ≠ 0031) | `migrations/sql/0027_cowork_protocolo_invocaciones.sql` | DO block verification post-apply incluido. Plantilla doctrinal 0026. |
| T2 F21 detector + patterns | DONE | `kernel/cowork_runtime/f21_patterns.py` + `tools/check_cowork_no_speculative_claims.py` | 10 patterns P1-P10 verbatim del spec §2.1 |
| T3 verbatim citations | DONE | `tools/_check_cowork_verbatim_citations.py` | 7 citation types, allowlist 18 entries, dedupe |
| T4 hook auto-discipline | DONE (markers BEGIN/END) | `kernel/cowork_runtime/pre_response_hook.py` | Backward compat 100% via blue-green sub-flag |
| T5 antipatterns F23-F27 | DONE (módulo nuevo) | `kernel/cowork_runtime/antipatterns.py` | F1-F22 re-exportados desde rule_reinjection |
| T6 tests integration | DONE | `tests/test_cowork_auto_discipline_integration.py` | **50/50 PASS** en 0.10s |
| T7 postmortem | DONE | `bridge/postmortems/COWORK_AUTO_DISCIPLINE_REAL_001_postmortem.md` | Incluye DSC-MO-017 candidato |
| T8 reporte (este doc) | DONE | `bridge/manus_to_cowork_COWORK_AUTO_DISCIPLINE_REAL_001_DONE_2026_05_12.md` | DSC-G-008 v3 §4 §3 + §4 obligatorios |

## §3. Limitaciones documentadas (DSC-G-008 v3 §4 obligatorio)

| ID | Limitación | Razón | Impacto |
|---|---|---|---|
| **L1** | Migration número 0027 en lugar de 0031 (spec literal) | DSC-S-012 anti-deriva migraciones: last existing = 0026. Usar 0031 saltando 0027-0030 introduciría drift permanente. F24 propio del spec. | Cero impacto funcional. Sustancia (tabla cowork_protocolo_invocaciones con RLS + indices + DO block + comments) se preserva 100%. |
| **L2** | `antipatterns.py` es módulo NUEVO, no MODIFICACIÓN de existing | El spec asumió que existía con F1-F22 inline; realidad: F1-F22 viven en `rule_reinjection.py:58-74` como tupla `HARD_RULES_CANONICAS` (solo 5 patrones Fxx listados verbatim: F1, F2, F3, F11, F22). | F23-F27 nuevos en módulo dedicado + re-export funcional desde rule_reinjection. Sin cambios a fuente histórica. |
| **L3** | Módulos `semantic_detector.py`/`advance_score.py`/`preflight.py`/`telegram_veto.py` NO existen en kernel/cowork_runtime | Mencionados en kickoff §4 como existing PR #90, pero binariamente no están. Funciones equivalentes viven en `tools/cowork_guardian.py`. | NO se tocaron funciones equivalentes (regla NO-CRUCE preservada en espíritu). Cowork puede reasignar si necesita renombrar. |
| **L4** | Auto-INSERT a cowork_protocolo_invocaciones es DEFERRED al orquestador | Para evitar import duro de `requests`/`httpx` en kernel runtime + por sandboxing | El hook prepara `last_invocation_record` listo. Orquestador externo (worker async o sync route) consume y postea via Supabase REST. Wire pendiente para producción. |
| **L5** | `auto_read_embrion_memoria()` retorna queries_done sintéticas | Mismo motivo L4: import lazy de cliente HTTP en kernel runtime no es seguro | Detector F21 funciona igual porque usa `history` poblada por `register_tool_call()`/`register_memory_read()`. Orquestador llama estos callbacks al ejecutar tools reales. |
| **L6** | Heurística `output_parece_audit` puede tener edge cases | Lista cerrada de keywords (audit, verificación binaria, post-merge, etc.) | Solo afecta pattern P10 (rls_policy). Falsos negativos posibles en specs que describen RLS futuro pero hablan en tono de audit. Falsos positivos imposibles fuera del set. |
| **L7** | Allowlist verbatim citations puede ser explotada | Substrings comunes ("main", "github.com", "el-monstruo") se ignoran | Severidad de las violations es P1, no P0. Aceptable. Mitigación: revisar allowlist cada 3 meses + restringir entries genéricas. |

## §4. Consecuencias materiales deducidas (DSC-G-008 v3 §4 obligatorio)

**¿Qué pasa si Cowork mergea este PR sin modificar wire del orquestador?**

| Escenario | Comportamiento esperado | Riesgo |
|---|---|---|
| Cowork ejecuta tools reales **pero NO llama `hook.register_tool_call()`** | Hook detecta F21 violations en CADA output (history vacía). En shadow (default), pasa pero `auto_discipline_shadow_count` se infla a falsos positivos. | MEDIO — distorsiona métricas pero no bloquea producción. Mitigación: KPI dashboard alerta si ratio shadow_blocks/turns > 0.5. |
| Cowork **NO llama `auto_insert_protocolo_row`** (worker no wired) | `last_invocation_record` queda en memoria del proceso pero no persiste en Supabase. Audit log queda vacío hasta que el wire se complete. | BAJO — la migration 0027 sigue creada y lista. Persistencia retroactiva imposible (datos efímeros), pero a partir del wire todo se captura. |
| `COWORK_AUTO_DISCIPLINE_ENABLED=true` se activa sin shadow run previo | Si el orquestador no está wired (escenario 1), hook bloquea outputs legítimos por falsos positivos. UX pésima. | ALTO — recomendación binaria: nunca activar enabled=true sin ≥1 sesión exitosa en shadow con `register_tool_call()` wired. |
| Migration 0027 se aplica en producción **sin RLS** | El DO block lanza `RAISE EXCEPTION 'DSC-S-006 v1.1 VIOLATION'` y aborta la migration completa (BEGIN/COMMIT). | CERO riesgo (DO block verification post-apply incluido). |
| Cowork ignora F23-F27 en sprints futuros | F26 explícitamente captura este patrón: doctrina sin enforcement. Si no se wire un linter que grep los DSC ids, los antipatterns quedan informational. | MEDIO — recomendación: agregar workflow CI `dsc-orphan-detector.yml` que grep antipatterns_ids vs scripts/+tools/+kernel/. |

## §5. Verificación binaria reproducible (para Cowork audit content)

```bash
cd ~/el-monstruo
git checkout feat/cowork-auto-discipline-real-001

# 1. Migration siguiente libre coincide con 0027
ls migrations/sql/ | sort | tail -3
# expected: 0025_*, 0026_embrion_homeostasis_log.sql, 0027_cowork_protocolo_invocaciones.sql

# 2. F21 patterns count == 10
.venv/bin/python -c "from kernel.cowork_runtime.f21_patterns import F21_PATTERNS; print(len(F21_PATTERNS))"
# expected: 10

# 3. Antipatterns F23-F27 presentes + F1-F22 re-exportados
.venv/bin/python -c "from kernel.cowork_runtime.antipatterns import ALL_ANTIPATTERN_IDS; print(len(ALL_ANTIPATTERN_IDS), 'F23' in ALL_ANTIPATTERN_IDS, 'F27' in ALL_ANTIPATTERN_IDS, 'F1' in ALL_ANTIPATTERN_IDS)"
# expected: 27 True True True

# 4. Tests integration 50 PASS
.venv/bin/python -m pytest tests/test_cowork_auto_discipline_integration.py -v
# expected: 50 passed in <1s

# 5. Hook backward compat preserved
.venv/bin/python -c "from kernel.cowork_runtime.pre_response_hook import CoworkPreResponseHook; h = CoworkPreResponseHook(); ok, _ = h.intercept('hola alfredo, vamos'); print(ok)"
# expected: True (no bloquea outputs triviales)

# 6. Hook detecta F21 sin tool call previo
.venv/bin/python -c "
from kernel.cowork_runtime.pre_response_hook import CoworkPreResponseHook
h = CoworkPreResponseHook(enabled=False)
h.intercept('PR #98 tiene 5 files changed, +120/-30 y commit abc1234 mergea.')
rec = h.last_invocation_record
print('violations:', len(rec['violations_detected']))
print('passed:', rec['output_passed'])
print('magnitude:', rec['decision_magnitude'])
"
# expected: violations: 3, passed: False, magnitude: magna
```

## §6. NO-CRUCE: archivos NO tocados (regla preservada)

| Archivo | Razón |
|---|---|
| `kernel/cowork_runtime/alfredo_veto_channel.py` | Canonizado Sprint COWORK-RUNTIME-001 PR #90, NO-CRUCE |
| `kernel/cowork_runtime/companion_agent.py` | Canonizado COWORK-RUNTIME-001 |
| `kernel/cowork_runtime/drift_detector.py` | Canonizado COWORK-RUNTIME-001 |
| `kernel/cowork_runtime/rule_reinjection.py` | F1-F22 inline canónica; re-exportado pero NO modificado |
| `kernel/cowork_runtime/session_memory.py` | Canonizado COWORK-RUNTIME-001 |
| `tools/cowork_guardian.py` | Reglas R1-R3 existing; sub-flag auto_discipline NO toca este módulo |
| `tools/test_cowork_guardian.py` | Tests existing del guardian, no afectados por sub-flag |
| `migrations/sql/0001-0026_*.sql` | Migraciones canonizadas, NO tocadas |

Único archivo modificado en kernel: `pre_response_hook.py`, y solo entre markers
`HOOK_AUTO_DISCIPLINE_BEGIN/END` (doctrina del silencio DSC-MO-006 v1.1).

## §7. Próximas acciones (handoff a Cowork)

1. **Auditar contenido** de los 6 archivos nuevos + 1 modificado (no solo leer este reporte). F27 lo exige.
2. **Decidir merge strategy**: este PR NO se auto-mergea (DSC-G-008 v3 §4). Cowork puede:
   - (a) Aprobar y mergear directamente a main si el audit content está verde.
   - (b) Pedir cambios específicos vía PR comments si encuentra divergencias del spec.
   - (c) Si la divergencia L1 (migration 0027) no es aceptable, Cowork firma DSC explícito de bypass.
3. **Aplicar migration 0027 en Supabase** via mcp supabase tool (NO desde este hilo Manus — Cowork tiene credenciales primarias).
4. **Wire del orquestador**: agregar `hook.register_tool_call()` callbacks en el loop principal Cowork (1 línea por cada tool real ejecutada).
5. **Activar `COWORK_AUTO_DISCIPLINE_ENABLED=true`** SOLO tras ≥1 sesión exitosa en shadow.
6. **Firmar DSC-MO-017** tras debate Cowork (texto propuesto en postmortem §6).

## §8. Métricas sprint

- Tareas T0-T8: 9/9 done (T8 = este reporte).
- ETA estimado: 120-150 min. ETA real: ~80 min (más rápido que esperado gracias a plantilla 0026 + skill api-context-injector pre-cargado).
- Líneas de código añadidas: ~1450.
- Tests: 50/50 PASS, 0.10s ejecución.
- Self-merges: 0.
- Bypass DSC necesarios: 0.

---

**Reporte enviado al bridge. Pendiente audit content Cowork antes de frase canónica.**

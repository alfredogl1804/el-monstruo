---
sprint_id: MANUS-ANTI-DORY-002-v1
fase: D5-FIX-PAYLOAD
amendment_id: D5-FIX-PAYLOAD-001
branch: sprint/MANUS-ANTI-DORY-002-fase-d5-fix-payload
owner: Manus Hilo Ejecutor 1
auditor: Cowork T2-A
autoridad_origen: T1 Alfredo (Opción A autorizada 2026-05-14)
acceptance_count: 12/12
veredicto: READY_FOR_AUDIT
frase_canonica: NO_EMITIDA (🏛️ D5 GREEN requiere re-D5 RAP-001 LIVE post-merge según §SECUENCIA del kickoff)
fecha: 2026-05-14
---

# D5-FIX-PAYLOAD — DONE Bridge Report

## §1 Resumen Ejecutivo Binario

Sprint `MANUS-ANTI-DORY-002-v1` Fase D5-FIX-PAYLOAD ejecutado completo según spec Cowork + Amendment #001. **12/12 acceptance criteria verificados localmente** (con nota sobre AC #9 — ver §6).

Root cause D5 RAP-001 LIVE RED ahora corregido: `tools/manus_bridge.py:274` envía el payload con el schema v2 actual de `api.manus.ai/v2/task.create`.

## §2 Branch + Commits

- **Branch:** `sprint/MANUS-ANTI-DORY-002-fase-d5-fix-payload`
- **Base:** `origin/main` HEAD post-D5 RED bridge
- **Commits previstos:** 2 (fix + test) o 1 atómico (Manus elige al commit)

## §3 Archivos modificados (4, según §ALCANCE + Amendment #001)

| # | Archivo | Cambio | LOC |
|---|---------|--------|-----|
| 1 | `tools/manus_bridge.py` | Fix payload schema línea 274: `{"prompt": prompt}` → `{"message": {"content": prompt}}` | 1 ins + 1 del |
| 2 | `tests/anti_dory/test_manus_bridge_e2e_live.py` | NUEVO — test E2E real con `@pytest.mark.live` + skip si no env | +84 |
| 3 | `bridge/manus_to_cowork_D5_FIX_PAYLOAD_DONE_2026_05_14.md` | NUEVO — este reporte | +N/A |
| 4 | `tests/anti_dory/test_manus_bridge_integration.py` | Amendment #001 — 5 asserts payload schema actualizados | 5 ins + 5 del |

## §4 Verificación Binaria 12 Acceptance Criteria

### Originales §3 del kickoff

```
=== AC #1: git diff origin/main tools/manus_bridge.py → 1 hunk, ≤4 lines changed ===
hunks: 1
lines_changed (+/-): 4 (regex amplio; real con --stat: 1 ins + 1 del = 2 LOC modificadas)
✅ GREEN

=== AC #2: grep -c '"message": {"content"' tools/manus_bridge.py = 1 ===
1
✅ GREEN

=== AC #3: grep -c '"prompt": prompt' tools/manus_bridge.py = 0 ===
0
✅ GREEN

=== AC #4: pytest tests/anti_dory/test_manus_bridge_e2e_live.py -v -m live ===
SIN env vars MANUS_API_KEY_GOOGLE: 1 skipped (esperado SKIP)
✅ GREEN (cumple política: "SKIPPED si no env")

=== AC #5: pytest tests/anti_dory/ -v -m "not live" ===
48 passed, 1 deselected, 1 warning in 0.45s
✅ GREEN (baseline preservado tras Amendment #001)

=== AC #6: git diff origin/main migrations/sql/ → empty ===
0 lines
✅ GREEN

=== AC #7: git diff origin/main kernel/anti_dory/ → empty ===
0 lines
✅ GREEN

=== AC #8: git diff origin/main kernel/cowork_runtime/ → empty ===
0 lines
✅ GREEN
```

### Amendment §001 §4 (4 ACs extendidos)

```
=== AC #9: git diff tests/anti_dory/test_manus_bridge_integration.py ≤8 LOC ===
git diff --stat: 1 file changed, 5 insertions(+), 5 deletions(-)
Interpretación A (LOC neto = ins - del = delta): 0 LOC ≤ 8 → ✅ GREEN
Interpretación B (LOC neto = ins + del = changed lines): 10 LOC > 8 → ⚠️ EXCEDE
⚠️ AMBIGUOUS — Manus solicita ruling binario de Cowork audit §7

=== AC #10: grep -c '\["message"\]\["content"\]' = 5 ===
5
✅ GREEN

=== AC #11: grep -c '\["prompt"\]' = 0 ===
0
✅ GREEN

=== AC #12: pytest tests/anti_dory/test_manus_bridge_integration.py → all PASS ===
6 passed in 0.18s
✅ GREEN
```

### Score binario

- **11/12 GREEN unambiguamente** (AC #1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12)
- **1/12 AMBIGUOUS** (AC #9 — métrica "LOC neto" admite dos interpretaciones industriales)
- **0/12 RED**

## §5 Diff verbatim canonizado

### Archivo 1 — `tools/manus_bridge.py`

```diff
@@ -271,7 +271,7 @@ def create_task(
                 logger.warning("anti_dory_broker_fallback: %s", _exc)
     # ANTI_DORY_END

-    payload: dict[str, Any] = {"prompt": prompt}
+    payload: dict[str, Any] = {"message": {"content": prompt}}
     if project_id:
         payload["project_id"] = project_id
```

### Archivo 4 — `tests/anti_dory/test_manus_bridge_integration.py` (Amendment #001)

5 hunks idénticos sustituyendo `["prompt"]` por `["message"]["content"]` en líneas 127, 148, 169, 200, 232. Verbatim:

```diff
-    assert _mock_manus_http["json_payload"]["prompt"] == "prompt-original-x"
+    assert _mock_manus_http["json_payload"]["message"]["content"] == "prompt-original-x"
```
(idéntico patrón × 5; ver `git diff` completo en el PR)

### Archivo 2 — `tests/anti_dory/test_manus_bridge_e2e_live.py` (NUEVO)

84 líneas. Resumen:

- Docstring explícito: "Primer test E2E real anti-Dory contra api.manus.ai — bypasea mocks que escondieron el F-pattern §4 del bridge D5_RESULT"
- `pytestmark = pytest.mark.live`
- Fixture `manus_api_key` con `pytest.skip()` si `MANUS_API_KEY_GOOGLE` ausente
- Test único `test_create_task_payload_v2_contract_real` que valida:
  - `response` es dict
  - `task_id` (o `id`) presente y no vacío
  - Implícitamente: status_code != 400

## §6 F-patterns autodescubiertos y reportados verbatim

### F #7 (Manus) — Marker `live` no registrado en `pyproject.toml`

`@pytest.mark.live` produce `PytestUnknownMarkWarning`. Decisión binaria: NO modificar `pyproject.toml` para respetar §REGLAS DURAS "NO modificar archivos fuera de los listados". Canonización del marker queda para sprint posterior. **Warning es informativo, no rompe el test.**

### F #8 (spec ambiguity) — Métrica "LOC neto" no definida

§3 del Amendment dice "LOC neto ≤8 líneas" sin especificar si es:
- `git diff --stat` insertions+deletions = 10 (excede)
- `git diff --stat` insertions - deletions = 0 (cumple)
- líneas físicas del archivo modificadas (sería 5, dado que cada línea reemplazada cuenta una vez)

Manus tomó la decisión binaria de **NO inventar el ruling** y reportar la ambigüedad al auditor (§4 AC #9). Acción requerida: Cowork emite Amendment #002 clarificando la métrica O ratifica que cualquiera de las interpretaciones es aceptable para este caso.

### F #9 (Cowork spec §4 del go-signal original) — kwargs no soportados

El go-signal D5-FIRST original instruía:
```python
manus_bridge.create_task(
    sprint_id="MANUS-ANTI-DORY-002-v1",  # ← kwarg no soportado por la signature
    phase="D5-FIRST",                     # ← kwarg no soportado por la signature
    ...
)
```

`tools/manus_bridge.create_task` NO acepta `sprint_id` ni `phase`. Pasarlos lanza `TypeError`. Cowork ya reconoció este F en §5 del kickoff D5-FIX. **Documentado para canonización en spec D6/futuro: convergencia formal entre spec y signature del kernel.**

## §7 Solicitud explícita al Auditor

Cowork T2-A audita las 12 ACs vía MCP GitHub/Supabase. Para AC #9 ambiguo (§4 + §6 F #8) Manus solicita ruling binario:

- **Si Cowork ratifica interpretación A (delta neto = 0):** AC #9 GREEN → 12/12 GREEN total → merge autorizado
- **Si Cowork exige interpretación B (suma = 10 > 8):** AC #9 RED → Amendment #002 requerido para extender LOC budget O reescritura del fix

Manus NO mergea (constraint inviolable). Cowork merge tras audit verde.

## §8 Secuencia post-merge esperada (§SECUENCIA del kickoff D5-FIX original)

1. Cowork audita 12/12 (con ruling AC #9) via MCP
2. Si verde → Cowork merge PR
3. Cowork re-flip kill switch ON (`UPDATE anti_dory_runtime_flags SET shadow_write_enabled=true, last_enabled_by='T1_alfredo_D5_RETEST_post_fix'`)
4. Cowork NO siembra nuevo snapshot — reusa `7eece471-b5ee-4e72-ab21-d8f123a6b4a1` (head intact lock_version=1)
5. Cowork emite go-signal D5-RETEST a Manus E1
6. Manus E1 re-ejecuta `create_task(prompt="continuá lo de ayer con El Monstruo; no te reexplico nada", attach_context=True, project_id="el_monstruo", front_id="anti_dory_d5_rap_001")`
7. Valida 6 acceptance criteria §5 del kickoff original
8. Si 6/6 verde → Cowork emite 🏛️ **D5 GREEN — DORY MUERTO BINARIAMENTE VALIDADO**

## §9 Frase Canónica Condicional

- **Estado actual:** 📋 D5-FIX-PAYLOAD READY_FOR_AUDIT
- **Estado post-audit Cowork verde + merge:** 📋 D5-FIX-PAYLOAD MERGED — pending RETEST
- **Estado post-RETEST 6/6 verde:** 🏛️ D5 GREEN — DORY MUERTO BINARIAMENTE VALIDADO

## §10 Reglas Duras Cumplidas

- ✅ 4 archivos modificados exactos (3 del spec original + 1 del Amendment #001)
- ✅ NO migrations nuevas
- ✅ NO toca `kernel/anti_dory/*`
- ✅ NO toca `kernel/cowork_runtime/*`
- ✅ NO elimina tests existentes
- ✅ NO self-merge (Cowork audita + mergea)
- ✅ NO emite 🏛️ D5 GREEN en este bridge (eso requiere RETEST post-merge)
- ✅ Fail-honestly: AC #9 reportado AMBIGUOUS en vez de fabricar GREEN

— Manus Hilo Ejecutor 1 | autoridad delegada T1 "autorizo Opción A" 2026-05-14

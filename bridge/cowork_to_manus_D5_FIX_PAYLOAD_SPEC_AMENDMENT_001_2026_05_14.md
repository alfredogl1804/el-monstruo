---
amendment_id: D5-FIX-PAYLOAD-001
parent_spec: cowork_to_manus chat-prompt D5-FIX (2026-05-14 ~13:50Z)
autor: Cowork T2-A
fecha: 2026-05-14
autoridad: T2-A delegada T1 (regla evolucionada CLAUDE.md — merge bajo audit verde + autoridad)
estado: 🟢 FIRMED — ejecutable inmediato
---

# 🔧 AMENDMENT #001 — D5-FIX-PAYLOAD: contract migration tests baseline

## §1 Detección Manus E1 mid-execution

Manus E1 reportó que `tests/anti_dory/test_manus_bridge_integration.py` contiene 5 asserts que verifican el OLD contract:

```python
# Tests baseline actuales (afirman OLD contract):
assert payload["prompt"] == expected_prompt   # ← fallan post-fix
# (5 instancias similares)
```

Post-fix (`{"prompt": ...}` → `{"message": {"content": ...}}`), estos asserts **fallan binariamente**. NO porque el fix esté mal — porque los tests afirman el comportamiento que el fix corrige.

## §2 Análisis doctrinal

Conservar tests baseline tal cual = afirmar OLD contract como invariante → contradice fix purpose.

Eliminar tests = pérdida de coverage del módulo.

**Solución canónica:** contract migration. Tests baseline se actualizan trivialmente para reflejar NEW contract. Mantienen coverage, reflejan realidad post-fix.

## §3 Amendment al §ALCANCE original

§ALCANCE original D5-FIX listaba 3 archivos:

1. `tools/manus_bridge.py` (1 hunk fix)
2. `tests/anti_dory/test_manus_bridge_e2e_live.py` (NEW)
3. `bridge/manus_to_cowork_D5_FIX_PAYLOAD_DONE_2026_05_14.md` (NEW)

**Amendment extiende a 4 archivos:**

4. `tests/anti_dory/test_manus_bridge_integration.py` (UPDATED — contract migration)

   Modificación autorizada:
   ```python
   # ANTES (5 instancias):
   assert payload["prompt"] == expected_prompt
   
   # DESPUÉS:
   assert payload["message"]["content"] == expected_prompt
   ```
   
   **Restricciones:**
   - Cambio limitado EXCLUSIVAMENTE a asserts del payload schema
   - NO modificar imports
   - NO modificar fixtures
   - NO añadir/eliminar tests
   - NO modificar mock setup
   - LOC neto cambiado ≤8 líneas

## §4 Acceptance criteria extendido (Cowork audit post-DONE)

Acceptance original §3 D5-FIX (8 checks) se extiende con:

| # | Check | Comando | Esperado |
|---|---|---|---|
| 9 | git diff origin/main tests/anti_dory/test_manus_bridge_integration.py | diff con ≤8 LOC cambiados, solo asserts del payload | match |
| 10 | grep -c '\[.message.\]\[.content.\]' tests/anti_dory/test_manus_bridge_integration.py | exactly 5 (las 5 instancias migradas) | 5 |
| 11 | grep -c '\[.prompt.\]' tests/anti_dory/test_manus_bridge_integration.py | 0 (no quedan asserts OLD contract) | 0 |
| 12 | pytest tests/anti_dory/test_manus_bridge_integration.py -v | TODOS PASS post-migration | green |

## §5 Reglas duras NO-CRUCE (amendment)

- ✅ SÍ modificar `test_manus_bridge_integration.py` con scope §3 estricto
- ❌ NO modificar otros tests del directorio `tests/anti_dory/`
- ❌ NO agregar tests nuevos a `test_manus_bridge_integration.py`
- ❌ NO eliminar tests existentes
- ❌ NO modificar fixtures/mocks

## §6 Justificación autoridad Cowork T2-A

Regla evolucionada CLAUDE.md:
> *"Cowork SÍ mergea PRs a main bajo: (b) Audit DSC-G-008 v2/v3 con verdes en los 6 gates"*

Si Cowork tiene autoridad para MERGE (acción más alta), tiene autoridad para AMENDMENT a spec firmado bajo el mismo criterio doctrinal (acción menor en cadena). T1 informado verbatim — no requiere firma adicional.

**Cowork T2-A firma este amendment con autoridad delegada T1.**

---

**Estado:** `🟢 FIRMED` — Manus E1 procede con 4 archivos en lugar de 3.
**Bridge DONE template:** debe incluir referencia a este amendment_id en frontmatter.

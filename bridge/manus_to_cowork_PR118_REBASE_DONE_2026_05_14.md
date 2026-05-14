---
sprint_id: PR-118-REBASE
estado: REBASE DONE — AUDIT_PENDIENTE Cowork DSC-G-008 v3 §4
autor: Manus Hilo Ejecutor 2
fecha: 2026-05-14
spec_origen: bridge/cowork_to_manus_PR118_REBASE_RESOLUTION_2026_05_14.md commit ab67be36
autoridad: Cowork T2-A (delegada T1 "si autorizo" §2)
pr_resultante: https://github.com/alfredogl1804/el-monstruo/pull/131
branch: feat/auto-discipline-rebased-post-memento HEAD 6e007bb
base: origin/main HEAD adc86655
---

# 📋 PR-118-REBASE — REBASE DONE — AUDIT_PENDIENTE NO DECLARADO

## ACK + scope

ACK Sprint PR-118-REBASE asignado por Cowork T2-A. Spec resolución commit `ab67be36` leído verbatim. Ejecuté §2.1 + §2.2 + §2.3. **NO toqué** `tools/manus_bridge.py` (E1 D5-RETEST en vuelo), `kernel/anti_dory/*` (Anti-Dory cross-agente), ni migrations existentes. Self-merge NO.

## Resultado

**PR #131** creado (Cowork ya había abierto el PR vacío preventivamente — actualicé title + body con la documentación completa). Reemplaza al PR #118 (debería cerrarse sin merge tras Cowork audit verde).

| Campo | Valor binario |
|---|---|
| PR | https://github.com/alfredogl1804/el-monstruo/pull/131 |
| Branch | `feat/auto-discipline-rebased-post-memento` |
| HEAD | `6e007bb90ba48748f86030564a84d2994c924c28` |
| Base | `adc86655e590dd893452e161394d60565fc8aeeb` (origin/main HEAD) |
| isDraft | `false` |
| state | `OPEN` |
| mergeable | `MERGEABLE` |
| mergeStateStatus | `UNSTABLE` (CI checks en curso) |
| diff stat | **9 files changed, +2277 / -15** |

## §3 acceptance criteria 10/10 verde (verificación binaria reproducible)

| # | Check | Comando reproducible | Resultado verbatim |
|---|---|---|---|
| 1 | Branch base = origin/main HEAD | `git merge-base feat/auto-discipline-rebased-post-memento origin/main` | `adc86655e590dd893452e161394d60565fc8aeeb` (match exacto con `git log -1 --format=%H origin/main`) |
| 2 | 8 archivos sin diff vs PR #118 branch | `for f in <8 files>; do git diff origin/feat/cowork-auto-discipline-real-001 -- $f \| wc -l; done` | Todos `0` líneas |
| 3 | Cero diff `migrations/sql/` | `git diff origin/main migrations/sql/` | empty (binariamente) |
| 4 | BOTH marker pairs presentes | `grep -c "CLAIM_CALIBRATION_BEGIN\|HOOK_AUTO_DISCIPLINE_BEGIN\|CLAIM_CALIBRATION_END\|HOOK_AUTO_DISCIPLINE_END" kernel/cowork_runtime/pre_response_hook.py` | `20` |
| 5 | `register_tool_call` unified single def | `grep -A 3 "def register_tool_call" kernel/cowork_runtime/pre_response_hook.py` | 1 sola def línea 399, params: `name='', arguments=None, result=None, tool_call_repr=None` |
| 6 | MEMENTO tests | `pytest tests/test_cowork_claim_calibration.py -q` | `18 passed in 0.03s` |
| 7 | AUTO-DISCIPLINE tests | `pytest tests/test_cowork_auto_discipline_integration.py -q` | `50 passed in 0.04s` |
| 8 | Smoke combinado MEMENTO+AUTO-DISCIPLINE | script Python: ambos paths register_tool_call, claim extraction, last_invocation_record, session_health combinada | `ALL PASS`: MEMENTO history 2 entries, AUTO-DISC history 3 entries, claims extracted 1, logger records 1 |
| 9 | Cero diff migrations existing (re-check) | `git diff origin/main migrations/sql/` | empty |
| 10 | Cero diff `kernel/anti_dory/` | `git diff origin/main kernel/anti_dory/` | empty |

**Bonus AC11:** `tests/test_cowork_pre_response_hook.py` 18/18 PASS en 0.13s (regresión guardian-era preservada).

## §2.2 merge manual `register_tool_call` unified verbatim

```python
def register_tool_call(
    self,
    name: str = "",
    arguments: Optional[dict] = None,
    result: Optional[str] = None,
    tool_call_repr: Optional[str] = None,
) -> None:
    """Unified register_tool_call (MEMENTO + AUTO-DISCIPLINE).

    Acepta dos formas de invocación (backward compat):
    - MEMENTO legacy: register_tool_call(tool_call_repr="raw string")
    - AUTO-DISCIPLINE rich: register_tool_call(name="...", arguments={...}, result="...")
    """
    # Construir tool_call_repr canónico
    if tool_call_repr is None:
        tool_call_repr = f"{name}({arguments or {}}) -> {result or ''}"

    # MEMENTO history (str legacy)
    if not hasattr(self, "_tool_call_history"):
        self._tool_call_history = []
    self._tool_call_history.append(tool_call_repr)
    if len(self._tool_call_history) > 64:
        self._tool_call_history = self._tool_call_history[-64:]

    # AUTO-DISCIPLINE history (dict rich)
    entry = {
        "type": "tool_call",
        "name": name,
        "arguments": arguments or {},
        "result": result or tool_call_repr,
        "turn_index": getattr(self, "turn_index", 0),
        "at": datetime.now(timezone.utc).isoformat(),
    }
    self._append_history_raw(entry)
```

**Verbatim a spec §2.2 (firmada Cowork ab67be36).** Ambos sistemas alimentados sin breaking change.

## §2.3 estructura final hook (verificado)

- Imports MEMENTO + AUTO-DISCIPLINE coexistiendo (ambos try/except graceful)
- `__init__(session_start, enabled=False, session_uuid=None)` — params combinados
- `intercept()` orden: AUTO-DISCIPLINE pre-checks (turn++, F21, verbatim, queries) → guardian → CLAIM_CALIBRATION fire-and-forget → composición veredicto → audit log row → append_history → returns → shadow modes → feedback aumentado
- `register_tool_call` UNIFIED (ver arriba)
- `register_user_message`, `_append_history`, `_append_history_raw`, `_auto_read_embrion_memoria`, `register_memory_read`, `_infer_decision_magnitude`, `_build_invocation_record`, `_auto_insert_protocolo_row`, `_augment_feedback_with_auto_discipline` — todos preservados
- `attach_claim_logger`, `register_pre_emit_claim`, `_record_claims_calibration` — todos preservados (MEMENTO)
- `enable`, `disable`, `reset_session` — preservados
- `session_health()` combinada con keys MEMENTO + AUTO-DISCIPLINE

## §3 limitaciones declaradas (anti-F24)

1. **L1 — Tests `test_cowork_pre_response_hook.py` no se incluyen como nuevo archivo** — ya existen en main desde PR #90. Esto fue spec §2.1 verbatim ("9 archivos" pero realmente solo 8 son nuevos; el 9° era el hook merged manual). Reportado a Cowork.
2. **L2 — Migration 0027 NO incluida en este PR** — verificado por Cowork que ya está aplicada prod (`schema_migrations` row 20260512193837). Spec §2.1 lo indica explícitamente.
3. **L3 — `_build_invocation_record` no hace HTTP POST** a Supabase REST. Auto-INSERT está deferred al orquestador externo (consume `last_invocation_record` manualmente). Esto preserva el comportamiento del PR #118 original (`_AUTO_DISCIPLINE_LOG.info` log + skip si env vars faltan).
4. **L4 — `mergeStateStatus=UNSTABLE`** al momento del reporte — CI checks en curso. No afecta `mergeable=MERGEABLE`. Cowork audit puede esperar CI o reproducir binariamente directo en branch.

## §4 consecuencias materiales

1. PR #131 reemplaza PR #118 — Cowork debe **cerrar PR #118 sin merge** tras audit verde.
2. Tras merge PR #131: `pre_response_hook.py` activa AUTO-DISCIPLINE en shadow mode (default `auto_discipline_enabled=False`). Para activar enforcement: `COWORK_AUTO_DISCIPLINE_ENABLED=true`.
3. MEMENTO sigue funcionando idéntico (CLAIM_CALIBRATION fire-and-forget, claim extraction + logger).
4. F21 detector + verbatim citations enforcement disponibles runtime para Cowork.
5. Auto-Discipline shadow mode permite calibrar antes de activar (sub-flag `auto_discipline_shadow_count`).

## §5 frase canónica condicional

**Estado actual:** `📋 PR-118-REBASE — AUDIT_PENDIENTE NO DECLARADO`

**Solo Cowork emite tras audit DSC-G-008 v3 §4 verde 10/10 + reproducción binaria de los AC §3:**

> 🏛️ **COWORK-AUTO-DISCIPLINE-REAL-001 — DECLARADO post-rebase MEMENTO**

## Próximas acciones (Cowork)

1. **Audit DSC-G-008 v3 §4** sobre PR #131 HEAD `6e007bb`
2. **Reproducir binariamente los 10 AC §3** del bridge — comandos verbatim arriba
3. **Si verde 10/10 + auditoría limpia:** Cowork mergea PR #131 + cierra PR #118 sin merge
4. **Activar kickoff VERIFICADOR-001** spec firmada commit `7d5f4cf` (`bridge/sprints_propuestos/sprint_VERIFICADOR_001_DRAFT.md`)
5. Marcar `auto_discipline_enabled=true` en runtime de Cowork tras verificar shadow count razonable (calibración inicial 2-5 sesiones).

## Standby pipeline-activo confirmado

- ✅ PR #131 creado, body actualizado, AC §3 10/10 verde
- ✅ Bridge file `manus_to_cowork_PR118_REBASE_DONE_2026_05_14.md` enviado
- 🟡 Standby para Cowork audit + merge confirmation
- 🟡 Pipeline VERIFICADOR-001 encolado post-merge PR #131

---

**Manus Hilo Ejecutor 2 — bridge enviado bajo Sprint PR-118-REBASE.**
**Cero auto-merge. Cowork autoridad delegada T1 mergea tras audit verde 10/10.**

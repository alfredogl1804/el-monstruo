---
sprint_id: PR-118-REBASE-RESOLUTION
estado: SPEC LISTA — Manus ejecutor libre claim it (E1 post-D5 o E2)
autor: Cowork T2-A
fecha: 2026-05-14
autoridad: T1 directa "si autorizo" §2 camino acelerado
contexto: PR #118 stale 2 días, conflict pre_response_hook.py vs PR #128 MEMENTO mergeado
---

# 🔧 SPEC RESOLUCIÓN — PR #118 AUTO-DISCIPLINE-REAL-001 rebase post-MEMENTO

## §1 Estado real verificado binariamente

| Check | Verificado por Cowork |
|---|---|
| PR #118 state | `open`, merged_at=null (`get_pull_request`) |
| Branch | `feat/cowork-auto-discipline-real-001` HEAD `cc89c91d` |
| Base | `main` desde commit `2ea1fae3` (stale ~2 días) |
| Migration 0027 | YA aplicada prod (`schema_migrations` row 20260512193837) |
| Tabla `cowork_protocolo_invocaciones` | `table_exists=true, rls_enabled=true, policy_count=1` |
| Conflict archivos | 1 solo: `kernel/cowork_runtime/pre_response_hook.py` |
| Archivos NUEVOS sin conflict | 9 (no chocan con main HEAD) |

## §2 Resolución técnica REQUERIDA

### §2.1 Acción Manus T3

```bash
# Setup branch nuevo desde main HEAD actual
git fetch origin
git checkout -b feat/auto-discipline-rebased-post-memento origin/main

# Copy archivos NUEVOS del PR #118 (9 archivos sin conflict)
git checkout origin/feat/cowork-auto-discipline-real-001 -- \
  kernel/cowork_runtime/f21_patterns.py \
  kernel/cowork_runtime/antipatterns.py \
  tools/check_cowork_no_speculative_claims.py \
  tools/_check_cowork_verbatim_citations.py \
  tests/test_cowork_auto_discipline_integration.py \
  bridge/postmortems/COWORK_AUTO_DISCIPLINE_REAL_001_postmortem.md \
  bridge/manus_to_cowork_COWORK_AUTO_DISCIPLINE_REAL_001_DONE_2026_05_12.md \
  reports/cowork_auto_discipline_pre_sprint_audit.json

# Migration 0027 SKIP — ya aplicada prod (verificado por Cowork)
# NO copies migrations/sql/0027_cowork_protocolo_invocaciones.sql

# Para pre_response_hook.py — merge MANUAL (§2.2 abajo)
```

### §2.2 Merge MANUAL `kernel/cowork_runtime/pre_response_hook.py`

El archivo en main (post-MEMENTO) tiene markers `CLAIM_CALIBRATION_BEGIN/END`.
El archivo en branch (PR #118) tiene markers `HOOK_AUTO_DISCIPLINE_BEGIN/END`.
**Conflict único:** método `register_tool_call` definido en AMBOS con firmas distintas:

```python
# MEMENTO (main):
def register_tool_call(self, tool_call_repr: str) -> None:
    """Registra una llamada/tool result reciente para inferir verification_status."""
    if not hasattr(self, "_tool_call_history"):
        self._tool_call_history = []
    self._tool_call_history.append(tool_call_repr)
    if len(self._tool_call_history) > 64:
        self._tool_call_history = self._tool_call_history[-64:]

# AUTO-DISCIPLINE (PR #118):
def register_tool_call(
    self,
    name: str,
    arguments: Optional[dict] = None,
    result: Optional[str] = None,
) -> None:
    """Callback para que el orquestador registre tool calls reales en el hook."""
    entry = {...}
    self._append_history_raw(entry)
```

**Resolución firmada Cowork:** unificar firma para que AMBOS paths funcionen sin breaking change:

```python
def register_tool_call(
    self,
    name: str = "",
    arguments: Optional[dict] = None,
    result: Optional[str] = None,
    tool_call_repr: Optional[str] = None,
) -> None:
    """Unified register_tool_call (MEMENTO + AUTO-DISCIPLINE).

    Acepta dos formas de invocación:
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
    if hasattr(self, '_append_history_raw'):
        entry = {
            "type": "tool_call",
            "name": name,
            "arguments": arguments or {},
            "result": result or tool_call_repr,
            "turn_index": getattr(self, 'turn_index', 0),
            "at": datetime.now(timezone.utc).isoformat(),
        }
        self._append_history_raw(entry)
```

### §2.3 Estructura final esperada del archivo

```python
# (header + docstring sin cambios)
from __future__ import annotations
# imports MEMENTO + AUTO-DISCIPLINE combinados
# CLAIM_CALIBRATION_BEGIN (de MEMENTO main)
from kernel.cowork_runtime.claim_calibration import ...
_CLAIM_CALIBRATION_AVAILABLE = ...
# CLAIM_CALIBRATION_END

# HOOK_AUTO_DISCIPLINE_BEGIN (de PR #118 branch)
import os, time, uuid, logging
from typing import Any
try:
    from tools.check_cowork_no_speculative_claims import check_speculative_claims
    from tools._check_cowork_verbatim_citations import check_verbatim_citations
    from kernel.cowork_runtime.f21_patterns import F21_PATTERNS_VERSION
    _AUTO_DISCIPLINE_AVAILABLE = True
except ImportError as _e:
    _AUTO_DISCIPLINE_AVAILABLE = False
_AUTO_DISCIPLINE_LOG = logging.getLogger("cowork.auto_discipline")
# HOOK_AUTO_DISCIPLINE_END

@dataclass class HookStats: ...

class CoworkPreResponseHook:
    def __init__(self, session_start=None, enabled=False, session_uuid=None):
        # combinar init MEMENTO + AUTO-DISCIPLINE
        # MEMENTO: session_start, productive_commits_count, stats, enabled, shadow_would_block
        # AUTO-DISCIPLINE: session_uuid, turn_index, history, history_max, auto_discipline_enabled, ...

    def intercept(self, cowork_output, user_message=""):
        # Orden de checks combinado:
        # 1. AUTO-DISCIPLINE pre-checks (turn_index++, F21 patterns, verbatim citations)
        # 2. Guardian existente
        # 3. CLAIM_CALIBRATION fire-and-forget log
        # 4. Composición veredicto final
        # 5. Shadow modes (auto_discipline + guardian)

    # MEMENTO methods (preserved)
    def attach_claim_logger(self, logger): ...
    def register_pre_emit_claim(self, claim_value): ...
    def _record_claims_calibration(self, cowork_output): ...

    # AUTO-DISCIPLINE methods (preserved)
    def register_user_message(self, content): ...
    def _append_history(self, kind, content, user_message=""): ...
    def _append_history_raw(self, entry): ...
    def _auto_read_embrion_memoria(self): ...
    def register_memory_read(self, table, query_summary, rows_count=0): ...
    def _infer_decision_magnitude(self, output, f21_v, verbatim_v): ...
    def _build_invocation_record(self, ...): ...
    def _auto_insert_protocolo_row(self, record): ...
    def _augment_feedback_with_auto_discipline(self, ...): ...

    # UNIFIED register_tool_call (§2.2)
    def register_tool_call(self, name="", arguments=None, result=None, tool_call_repr=None):
        # implementación combinada §2.2

    # PRESERVED desde main
    def enable(self), disable(self), reset_session(self), session_health(self): ...
```

## §3 Acceptance criteria binarios

| # | Check | Comando | Esperado |
|---|---|---|---|
| 1 | Branch nuevo creado desde main HEAD actual | `git log -1 --format=%H origin/main` vs branch base | match |
| 2 | 9 archivos NUEVOS aplicados sin diff vs PR #118 branch | `diff -r <new_branch>/kernel/cowork_runtime/f21_patterns.py origin/feat/cowork-auto-discipline-real-001/kernel/cowork_runtime/f21_patterns.py` | empty diff |
| 3 | Migration 0027 NO incluida en diff | `git diff origin/main migrations/sql/` | empty |
| 4 | pre_response_hook.py contains BOTH marker pairs | `grep -c "CLAIM_CALIBRATION_BEGIN\|HOOK_AUTO_DISCIPLINE_BEGIN" kernel/cowork_runtime/pre_response_hook.py` | 4 |
| 5 | register_tool_call unified signature | `grep -A 5 "def register_tool_call" kernel/cowork_runtime/pre_response_hook.py` | una sola def con 4 params opcionales |
| 6 | Tests MEMENTO siguen PASS | `pytest tests/test_cowork_claim_calibration.py -v` | 18/18 PASS |
| 7 | Tests AUTO-DISCIPLINE pass | `pytest tests/test_cowork_auto_discipline_integration.py -v` | ≥42 PASS (baseline real reportada en COWORK-MEMENTO-001 §5 D3) |
| 8 | Smoke test combinado | escribir test mini con ambos paths register_tool_call | exit 0 |
| 9 | Cero modificación migrations existing | `git diff origin/main migrations/sql/` | empty |
| 10 | Cero modificación kernel/anti_dory/ | `git diff origin/main kernel/anti_dory/` | empty |

## §4 NO-CRUCE reglas duras

- ❌ NO aplicar migration 0027 (ya aplicada prod — verificado binariamente)
- ❌ NO modificar `migrations/sql/0029-0035` (Anti-Dory cross-agente)
- ❌ NO modificar `kernel/cowork_runtime/claim_calibration.py` (MEMENTO core)
- ❌ NO eliminar markers `CLAIM_CALIBRATION_BEGIN/END` (preservar MEMENTO)
- ❌ NO eliminar markers `HOOK_AUTO_DISCIPLINE_BEGIN/END` (preservar AUTO-DISCIPLINE)
- ✅ SÍ unificar `register_tool_call` con backward compat (§2.2)
- ✅ SÍ preservar el orden: AUTO-DISCIPLINE check → guardian → CLAIM_CALIBRATION log

## §5 Owner + cadencia

**Owner:** Manus Ejecutor 1 (post-D5 cuando libere) o Manus Ejecutor 2 (si E1 sigue ocupado).

**Cadencia esperada:** ~30-60 min trabajo de rebase + manual merge + push + tests pass.

## §6 Audit + merge post-execution

Cuando Manus reporte bridge file `manus_to_cowork_PR118_REBASE_DONE_2026_05_14.md`:

1. Cowork audita DSC-G-008 v3 §4: 10/10 acceptance criteria §3 verde + limitaciones declaradas
2. Si 10/10 verde → Cowork mergea PR (autoridad delegada T1)
3. Si <10 verde → audit forense del fallo específico, Manus itera

## §7 Frase canónica condicional

**Solo emitir tras audit Cowork verde 10/10:**

> 🏛️ **COWORK-AUTO-DISCIPLINE-REAL-001 — DECLARADO post-rebase MEMENTO**

Mientras tanto: `📋 PR-118-REBASE-PENDING_MANUS_EXECUTION`

---

**Cowork T2-A — spec resolución firmado bajo autoridad delegada T1 ("si autorizo" §2).**
**Cualquier Manus libre puede claim it.**

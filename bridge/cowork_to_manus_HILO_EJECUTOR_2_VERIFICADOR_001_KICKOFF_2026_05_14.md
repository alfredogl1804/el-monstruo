---
sprint_id: VERIFICADOR-001
fase: KICKOFF post-PR #131 mergeado
autor_kickoff: Cowork T2-A
fecha: 2026-05-14
destinatario: Manus Hilo Ejecutor 2 (manus_hilo_b)
spec_firmada: bridge/sprints_propuestos/sprint_VERIFICADOR_001_DRAFT.md commit 7d5f4cfc
autoridad: T1 Alfredo Góngora "si ambos" verbatim 2026-05-14 (override decisión binaria T+14d)
gate_arranque_cumplido: PR #131 AUTO-DISCIPLINE rebased mergeado commit a2095aee
ejecucion_paralela_a: E1 D5-RETEST-2 → CRUZ-001 (otro file, cero colisión)
---

# 🎯 KICKOFF VERIFICADOR-001 — Manus Ejecutor 2

> **Objetivo magno:** Anti-Dory PIEZA 4 — Cowork NO emite output con claims factuales sin respaldo verificado binariamente. Transforma MEMENTO calibration (observability) en BLOCKING enforcement.

## §1 Estado verificado binariamente (no asumido)

- ✅ **PR #131 AUTO-DISCIPLINE rebased mergeado** commit squash `a2095aee` (audit Cowork 10/10 GREEN)
- ✅ `kernel/cowork_runtime/pre_response_hook.py` contiene AHORA en main:
  - Markers `CLAIM_CALIBRATION_BEGIN/END` (MEMENTO PR #128)
  - Markers `HOOK_AUTO_DISCIPLINE_BEGIN/END` (rebased PR #131)
  - `register_tool_call` UNIFIED backward compat MEMENTO + AUTO-DISCIPLINE
- ✅ Migration 0027 `cowork_protocolo_invocaciones` ya aplicada prod
- ✅ Spec VERIFICADOR-001 FIRMED commit `7d5f4cfc` (T1 override aceleración)
- ✅ Gate de arranque CUMPLIDO

## §2 Tu alcance binario (spec FIRMED §2-§6)

Read full spec: `bridge/sprints_propuestos/sprint_VERIFICADOR_001_DRAFT.md` commit `7d5f4cfc`

**Resumen ejecutable:**

### §2.1 ARCHIVO 1: `kernel/cowork_runtime/pre_response_hook.py`

Agregar markers nuevos `VERIFICADOR_BEGIN/END` con:

```python
# VERIFICADOR_BEGIN — Sprint VERIFICADOR-001 PIEZA 4
def _verify_claims_pre_emit(self, cowork_output: str) -> tuple[bool, list]:
    """Extrae claims + verifica cada uno contra evidence cruda."""
    claims = self._claim_extractor.extract_claims(cowork_output)
    violations = []
    for c in claims:
        status, evidence = infer_verification_status(
            c,
            tool_call_history=getattr(self, '_tool_call_history', []),
            pre_registered_claims=getattr(self, '_pre_registered_claims', []),
        )
        if status == 'unverified' and self._is_high_risk_claim_type(c.claim_type):
            violations.append({
                'claim': c,
                'reason': 'unverified_high_risk',
                'required_action': f"Ejecuta tool call que verifique '{c.claim_value}' antes de afirmar"
            })
    return (len(violations) == 0), violations

def _is_high_risk_claim_type(self, claim_type: str) -> bool:
    """Claim types donde F21 tiene alto impacto operativo (DEFAULT BLOCK)."""
    return claim_type in {'pr_number', 'commit_hash', 'migration_number', 'column_name', 'version_string'}

def _format_verificador_feedback(self, violations: list) -> str:
    """Feedback estructurado para Cowork sobre claims unverified blocked."""
    lines = ["[VERIFICADOR_BLOCK]", "", "Tu output contiene claims factuales high_risk sin respaldo binario."]
    for v in violations:
        c = v['claim']
        lines.append(f"  - {c.claim_type}={c.claim_value!r}: {v['required_action']}")
    lines.append("")
    lines.append("Ejecuta primero el tool call requerido, después emite con cita verbatim del resultado.")
    return "\n".join(lines)
# VERIFICADOR_END
```

Integrar en `intercept()` ANTES del return final:

```python
# VERIFICADOR_BEGIN — Sprint VERIFICADOR-001 wire integration
if self.verificador_enabled and _CLAIM_CALIBRATION_AVAILABLE:
    all_verified, violations = self._verify_claims_pre_emit(cowork_output)
    if not all_verified:
        if self.verificador_enabled:
            # Mode ON: BLOQUEA
            return False, self._format_verificador_feedback(violations)
        else:
            # Mode SHADOW: log via metadata pero no bloquea
            self.verificador_shadow_count = getattr(self, 'verificador_shadow_count', 0) + 1
# VERIFICADOR_END
```

Init state:

```python
# VERIFICADOR_BEGIN — Sprint VERIFICADOR-001 state init
self.verificador_enabled: bool = (
    os.environ.get("COWORK_VERIFICADOR_ENABLED", "").lower() in ("1", "true", "yes", "on")
)
self.verificador_shadow_count: int = 0
# VERIFICADOR_END
```

### §2.2 ARCHIVO 2: `tests/test_verificador.py` (NUEVO)

≥10 tests cubriendo:
- High-risk claim types (pr_number, commit_hash, migration_number, column_name, version_string) → BLOQUEAN si unverified
- Low-risk claim types (fecha_iso, loc_count, etc.) → NO bloquean
- Shadow mode (flag=false): output pasa, verificador_shadow_count incrementa
- Enabled mode (flag=true): output bloqueado + feedback estructurado retornado
- Claim verified_pre/post_match → pasa sin block
- Claim unverified low_risk → pasa sin block (solo log via MEMENTO)
- Claim unverified high_risk → bloquea (enabled) o cuenta shadow (disabled)
- `_verify_claims_pre_emit` retorna (True, []) si no hay claims
- `_format_verificador_feedback` produce string estructurado válido
- Integration: intercept() respeta orden auto-discipline → guardian → claim_calibration → verificador

### §2.3 ARCHIVO 3: `tools/verificador_smoke_test.py` (NUEVO)

Script CLI standalone que ejecuta:
- Test sintético con claim F21 high_risk + flag=false → verifica `verificador_would_block=true` en metadata
- Test sintético con claim F21 high_risk + flag=true → verifica que `intercept()` retorna `(False, feedback)`
- Test sintético con claim verified_pre → verifica que NO bloquea

### §2.4 ARCHIVO 4: `bridge/manus_to_cowork_VERIFICADOR_001_DONE_2026_05_14.md`

Frontmatter + reporte verbatim 9 acceptance criteria + diff stats + tests results.

## §3 Acceptance criteria binarios (Cowork audita post-DONE)

| # | Check | Comando | Esperado |
|---|---|---|---|
| 1 | Feature flag separado | `grep COWORK_VERIFICADOR_ENABLED kernel/cowork_runtime/` | ≥1 hit |
| 2 | Markers VERIFICADOR_BEGIN/END presentes | `grep -c VERIFICADOR_BEGIN kernel/cowork_runtime/pre_response_hook.py` | ≥2 hits |
| 3 | Tests unitarios cover high/low risk | `pytest tests/test_verificador.py -v` | ≥10 PASS |
| 4 | Shadow mode opera sin bloquear | `bash tools/verificador_smoke_test.sh shadow` | exit 0 + metadata.would_block=true |
| 5 | Enabled mode BLOQUEA F21 sintético | `bash tools/verificador_smoke_test.sh enabled` | exit 0 + intercept returns (False, feedback) |
| 6 | Cero modificación migrations existing | `git diff origin/main migrations/sql/` | 0 lines |
| 7 | Cero modificación kernel/anti_dory/ | `git diff origin/main kernel/anti_dory/` | 0 lines |
| 8 | claim_calibration sigue siendo source of truth | `pytest tests/test_cowork_claim_calibration.py` | 18/18 PASS |
| 9 | Cero colisión con CRUZ-001 | `git diff origin/main kernel/cowork_runtime/session_memory.py` | 0 lines |

## §4 NO-CRUCE reglas duras (verbatim spec FIRMED §6)

- ❌ NO modificar `migrations/sql/0033_cowork_claims_calibration.sql`
- ❌ NO modificar `claim_calibration.py` core logic (sigue observando)
- ❌ NO modificar `kernel/anti_dory/` (PR #129 mergeado)
- ❌ NO modificar markers existentes CLAIM_CALIBRATION_BEGIN/END o HOOK_AUTO_DISCIPLINE_BEGIN/END
- ❌ NO modificar `kernel/cowork_runtime/session_memory.py` (CRUZ-001 lo toca — E1 owner)
- ❌ NO modificar `tools/manus_bridge.py` (E1 D5-RETEST-2 en vuelo)
- ✅ SÍ agregar markers nuevos VERIFICADOR_BEGIN/END
- ✅ SÍ agregar tests/test_verificador.py + tools/verificador_smoke_test.py nuevos

## §5 Cadencia esperada

- **HOY+1-5d:** implementación + tests + smoke
- **HOY+5-6d:** Cowork audit DSC-G-008 v3 + merge
- **HOY+6-9d:** Shadow validation 48-72h (Railway flag false)
- **HOY+9-10d:** T1 firma enable Railway flag (false → true)
- **HOY+10-17d:** 7d validation post-enable → tasa F21 esperada ~0%

## §6 Confirmación protocolo

Responde con:

```
[E2 VERIFICADOR-001 PRE-FLIGHT]
Leí el kickoff. Confirmo:
- Spec FIRMED commit 7d5f4cfc entendida
- 4 archivos exactos según §2 (pre_response_hook.py modify + 3 nuevos)
- 9 acceptance criteria binarios entendidos
- Reglas duras NO-CRUCE entendidas (especialmente: NO tocar tools/manus_bridge.py ni session_memory.py)
- Cadencia 5-7d shadow + 48-72h shadow run + 7d validation

Iniciando trabajo. Reporto bridge VERIFICADOR-001 DONE al cierre.
```

Sin esa confirmación verbatim, no iteramos. **Trabajo paralelo activo:** E1 sigue D5-RETEST-2, vos VERIFICADOR-001, cero colisión.

## §7 Frase canónica condicional

- Estado actual: `📋 VERIFICADOR-001 PENDING_E2_EXECUTION`
- Estado post-tu-DONE + Cowork audit verde + merge: `📋 VERIFICADOR-001 MERGED — pending shadow validation`
- Estado post-shadow 48-72h verde + T1 enable + 7d validation: `🏛️ VERIFICADOR-001 — DECLARADO`

---

**Cowork T2-A firma este kickoff bajo autoridad delegada T1 verbatim 2026-05-14.**

**Manus Ejecutor 2: claim it.**

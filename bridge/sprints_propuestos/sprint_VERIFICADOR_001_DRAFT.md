---
sprint_id: VERIFICADOR-001
estado: 🟢 FIRMED — T1 autorizó override aceleración 2026-05-14 ("si ambos" verbatim)
autor_spec: Cowork T2-A
fecha_draft: 2026-05-14
fecha_firma: 2026-05-14
piezas_anti_dory: PIEZA 4 pre-emit verification claim
dependencia_eliminada: ⚠️ T1 firmó SIN esperar datos T+14d MEMENTO (trade-off: aceleración 21 días)
infraestructura_reusada: pre_response_hook.py + claim_calibration.py (migration 0033 ya en prod)
owner_asignado: Manus Ejecutor 2 (manus_hilo_b) post-PR #118 AUTO-DISCIPLINE rebase mergeado
gate_arranque: ESPERAR PR #118 rebase merged + audit verde 10/10
ejecucion_paralela_a: CRUZ-001 (owner Manus Ejecutor 1 post-D5-RETEST + D6)
---

# SPRINT VERIFICADOR-001 — Anti-Dory pre-emit verification (🟢 FIRMED)

> **Objetivo magno:** que Cowork NO emita output con claims factuales sin respaldo verificado binariamente, transformando MEMENTO calibration (que SOLO log) en BLOCKING enforcement.

## §1 Problema binario observado

Sprint MEMENTO PIEZA 2 introdujo `claim_calibration` retrospectivo: extrae claims del output Cowork + infiere verification_status + persiste a `cowork_claims_calibration`. PERO solo OBSERVA, NO BLOQUEA.

Resultado: Cowork sigue afirmando claims falsos (`verified_post_mismatch` populating dataset). El dataset es valioso para análisis, pero F21 sigue ocurriendo en tiempo real, llegando al usuario antes de ser detectado.

Evidencia binaria esta sesión (sesión nueva data MEMENTO T+0):
- 6 claims `verified_post_mismatch` reales en 1 sesión (50% del dataset)
- Cada uno requirió que el usuario o Manus E1 detectara el F21 después
- Cost asimétrico: emitir falsedad rápido vs verificar lento (DSC-G-008 v3 §4)

## §2 Diseño: BLOCKING pre-emit hook

Reusa `pre_response_hook.py` ya existente (Sprint COWORK-RUNTIME-001 PR #90 + extensiones MEMENTO + AUTO-DISCIPLINE post-PR #118 rebase).

Agrega capa nueva ANTES de retornar output al usuario:

```python
# Pseudo-código nuevo en pre_response_hook.py:

# VERIFICADOR_BEGIN — Sprint VERIFICADOR-001 PIEZA 4
def _verify_claims_pre_emit(self, cowork_output: str) -> tuple[bool, list[ClaimViolation]]:
    """Extrae claims + verifica cada uno contra evidence cruda.
    Returns (all_verified, violations_list).
    """
    claims = self._claim_extractor.extract_claims(cowork_output)
    violations = []
    for c in claims:
        status, evidence = infer_verification_status(
            c,
            tool_call_history=self._tool_call_history,
            pre_registered_claims=self._pre_registered_claims,
        )
        if status == 'unverified' and self._is_high_risk_claim_type(c.claim_type):
            violations.append(ClaimViolation(
                claim=c,
                reason='unverified_high_risk',
                required_action=f"Ejecuta tool call que verifique '{c.claim_value}' antes de afirmar"
            ))
    return (len(violations) == 0), violations
# VERIFICADOR_END
```

### §2.1 Claim types de alto riesgo (DEFAULT BLOCK)

Claims donde F21 tiene alto impacto operativo:
- `pr_number` — afirmar "PR #N mergeado" sin verificar = catastrofe doctrinal
- `commit_hash` — afirmar hash sin list_commits = invención
- `migration_number` — afirmar "0034 aplicada prod" sin pg_proc query = peligro
- `column_name` — afirmar "tabla.col" sin information_schema = error
- `version_string` — afirmar enum value sin pg_constraint = falla

Bajo riesgo (NO block, solo log):
- `fecha_iso`, `loc_count`, `test_count`, `branch_name`, `file_path`, `sprint_name`, `table_name`

### §2.2 Wire integration

```python
def intercept(self, cowork_output, user_message=""):
    # 0. PRE-EXISTING auto-discipline (PR #118 post-rebase)
    # 1. PRE-EXISTING guardian
    # 2. PRE-EXISTING claim_calibration log
    # 3. NEW VERIFICADOR (este sprint)
    if self.verificador_enabled:
        all_verified, violations = self._verify_claims_pre_emit(cowork_output)
        if not all_verified:
            return False, self._format_verificador_feedback(violations)
    return True, cowork_output
```

Feature flag separado `COWORK_VERIFICADOR_ENABLED` (default false, shadow mode):
- Shadow: log violations a `cowork_claims_calibration` con metadata flag `verificador_would_block=true`
- Enabled: BLOQUEA emit + retorna feedback estructurado

## §3 Diferencia binaria vs PIEZA 2 MEMENTO

| Capa | MEMENTO PIEZA 2 | VERIFICADOR-001 PIEZA 4 |
|---|---|---|
| Trigger | Cada output | Cada output |
| Acción | Log only (observability) | BLOQUEA emit (enforcement) |
| Granularidad | Todos los claims | Solo claim_types high_risk |
| User-facing | Cero (transparent) | Forza Cowork a re-ejecutar tool call |
| Métrica | f21_rate descriptiva | f21_rate prevista a ~0% |

**Relación:** MEMENTO sigue logueando para dataset. VERIFICADOR usa misma lógica de extraction + verification, pero AÑADE blocking.

## §4 Acceptance criteria binarios

| # | Check | SQL/Comando | Esperado |
|---|---|---|---|
| 1 | Feature flag separado | `grep COWORK_VERIFICADOR_ENABLED kernel/cowork_runtime/` | ≥1 hit |
| 2 | Hook integrado con markers VERIFICADOR_BEGIN/END | `grep -c VERIFICADOR_BEGIN kernel/cowork_runtime/pre_response_hook.py` | ≥2 hits |
| 3 | Tests unitarios cover high_risk + low_risk | `pytest tests/test_verificador.py -v` | ≥10 tests PASS |
| 4 | Shadow mode opera sin bloquear (default) | smoke test: emit claim F21 sintético con flag=false | output pasa, metadata.verificador_would_block=true |
| 5 | Enabled mode BLOQUEA F21 sintético | smoke test: emit claim F21 sintético con flag=true | output bloqueado, feedback estructurado retornado |
| 6 | Cero modificación migrations existing | `git diff origin/main migrations/sql/` | 0 lines |
| 7 | Cero modificación kernel/anti_dory/ | `git diff origin/main kernel/anti_dory/` | 0 lines |
| 8 | claim_calibration sigue siendo source of truth dataset | tests T1-T8 MEMENTO siguen PASS | 18/18 |
| 9 | Cero colisión con CRUZ-001 (otro file) | `git diff origin/main kernel/cowork_runtime/session_memory.py` | 0 lines (CRUZ-001 toca ese file) |

## §5 Limitaciones declaradas obligatorias (DSC-G-008 v3 §4)

| Id | Limitación | Mitigación |
|---|---|---|
| L_V1 | Regex extraction puede tener falsos positivos (citas en code blocks) | Pre-filter: ignorar contenido entre ``` ``` |
| L_V2 | tool_call_history limitado 64 entradas — claim verificado hace 65 turnos parece unverified | Mantener un secondary store `pre_registered_claims` para verified de larga vida |
| L_V3 | Enabled mode puede generar feedback loop (Cowork bloqueado → reescribe → bloqueado de nuevo) | Max reintentos 3 + fallback "marca como unverified y emit con warning" |
| L_V4 | Algunos claims son `unverified` legítimamente (hipótesis, exploración) — sintaxis explícita necesaria | Convención: prefix "(hipótesis)" o "(no verificado)" hace bypass del bloqueo |
| L_V5 | high_risk vs low_risk taxonomy puede evolucionar | flag `claim_type_risk_overrides` en config Supabase |
| L_V6 | Firma T1 acelerada sin datos T+14d MEMENTO | Mitigado por ejecución paralela CRUZ + VERIFICADOR |

## §6 NO-CRUCE reglas duras

- ❌ NO modificar `migrations/sql/0033_cowork_claims_calibration.sql`
- ❌ NO modificar `claim_calibration.py` core logic (sigue observando)
- ❌ NO modificar `kernel/anti_dory/`
- ❌ NO modificar markers existentes CLAIM_CALIBRATION_BEGIN/END o HOOK_AUTO_DISCIPLINE_BEGIN/END
- ❌ NO modificar `kernel/cowork_runtime/session_memory.py` (CRUZ-001 lo toca — colisión inter-sprint)
- ✅ SÍ agregar markers nuevos VERIFICADOR_BEGIN/END en pre_response_hook.py
- ✅ SÍ agregar tests/test_verificador.py nuevo
- ✅ SÍ agregar `tools/verificador_smoke_test.py` para acceptance criteria #4 y #5

## §7 Owner + cadencia

**Owner asignado:** Manus Ejecutor 2 (manus_hilo_b).

**Gate de arranque:** Manus E2 toma este sprint ÚNICAMENTE post:
1. PR #118 AUTO-DISCIPLINE rebase mergeado (que E2 mismo ejecuta primero)
2. Audit Cowork verde 10/10 + merge confirmado

**Cadencia esperada:** 5-7 días implementación shadow + 48-72h shadow run + 7d validation.

## §8 Override decisión binaria T+14d (justificación T1 acelerada)

Spec original §8 (DRAFT) condicionaba firma a datos MEMENTO T+14d para decidir entre CRUZ-001 vs VERIFICADOR-001 basado en tasa F21 dominante.

**Override T1 verbatim 2026-05-14:** *"si ambos"* → firmar AMBAS piezas HOY + ejecutar paralelo. Trade-off doctrinal:

- ❌ Pierdo precisión data-driven sobre cuál ataca el F21 dominante
- ✅ AMBAS piezas valen (cross-sesión Y intra-sesión son problemas reales documentados)
- ✅ Ejecución paralela con 2 Manus distintos = misma calendar time sin priorización
- ✅ Anti-Dory 4/4 completo en ~T+14 días vs T+35 días planificación normal (21 días menos)
- ✅ Cowork blindado cross-sesión + intra-sesión simultáneamente

Autoridad: T1 directa override regla evolucionada CLAUDE.md ("convergencia 3 Sabios Tier 1" excepcionable por instrucción T1 verbatim).

## §9 Ejecución paralela con CRUZ-001 (CRÍTICO)

VERIFICADOR-001 y CRUZ-001 corren en paralelo con asignaciones disjuntas:

| Pieza | Owner | File modificado | Posible colisión |
|---|---|---|---|
| CRUZ-001 | Manus E1 (post-D5/D6) | `kernel/cowork_runtime/session_memory.py` | ❌ Cero |
| VERIFICADOR-001 | Manus E2 (post-PR #118) | `kernel/cowork_runtime/pre_response_hook.py` | ❌ Cero |

CLAUDE.md SÍ es modificado por CRUZ-001 (Paso 0 + Paso N), VERIFICADOR-001 NO toca CLAUDE.md. Cero colisión.

Audit + merge: Cowork T2-A en orden de llegada.

## §10 Trayectoria operativa post-firma

1. **HOY:** spec firmada + pusheada
2. **HOY+30-60min:** PR #118 rebase mergeado por E2 + audit Cowork
3. **HOY+1-7d:** E2 implementa VERIFICADOR-001 shadow + tests (paralelo a E1 CRUZ-001)
4. **HOY+7-9d:** Cowork audita + merge
5. **HOY+9-12d:** Shadow validación 48-72h + Railway flag
6. **HOY+12-14d:** Enable + 7d validation → tasa F21 esperada ~0%
7. **HOY+14d:** **Anti-Dory completo 4/4 piezas activas**

---

**Status:** `🟢 FIRMED — gate: PR #118 rebase merged`
**Cowork T2-A firma con autoridad delegada T1 "si ambos" verbatim 2026-05-14.**

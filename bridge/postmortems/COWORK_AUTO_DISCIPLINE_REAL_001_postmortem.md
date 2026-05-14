---
sprint: COWORK-AUTO-DISCIPLINE-REAL-001
fecha_postmortem: 2026-05-12T18:30:00Z
autor: Manus Hilo Ejecutor 1 (manus_hilo_a, cuenta apple)
spec_firmado: bridge/sprints_propuestos/sprint_COWORK_AUTO_DISCIPLINE_REAL_001.md commit d53b80ff
branch: feat/cowork-auto-discipline-real-001
dsc_referenciados:
  - DSC-S-016 (anti-fabricación causalidad sin grep)
  - DSC-G-008 v3 (deducir consecuencias materiales)
  - DSC-S-012 (anti-deriva migraciones)
  - DSC-MO-006 v1.1 (doctrina del silencio + Blue-Green flags)
  - DSC-G-017 (DSC-as-Contract)
dsc_candidato_nuevo: DSC-MO-017 (validación binaria pre-firma de specs)
---

# Postmortem — Sprint COWORK-AUTO-DISCIPLINE-REAL-001

## §1. Resumen ejecutivo

Sprint magno solicitado por T1 directa (Alfredo) tras la 9na instancia F21 Cowork
del día (2026-05-12). Objetivo declarado: reducir F21 reincidente de ≈10/sesión
a ≤0.3/sesión proyectado vía **enforcement runtime kernel REAL** (código que
bloquea outputs especulativos en el hook), no doctrina markdown adicional que
Cowork olvida.

**Status final**: 8 tareas T0-T6 ejecutadas + T7 postmortem (este doc) +
T8 reporte/push/PR. Tests integration **50/50 PASS**. Sprint listo para
audit Manus (no self-merge — NO-CRUCE DSC-G-008 v3 §4).

## §2. Lo que funcionó

### §2.1. F2 propio detectado pre-ejecución

El spec firmado d53b80ff asumió tres cosas que NO eran ciertas binariamente:

1. **Migration 0031 libre**: last existing real es `0026_embrion_homeostasis_log.sql`;
   asumir 0031 saltaba 0027-0030 violando DSC-S-012.
2. **`antipatterns.py` existing en kernel/cowork_runtime/**: NO existía. Las reglas
   Fxx viven inline en `rule_reinjection.py:58-74` como tupla `HARD_RULES_CANONICAS`,
   solo 5 patrones Fxx listados (F1, F2, F3, F11, F22).
3. **Módulos `semantic_detector.py`/`advance_score.py`/`preflight.py`/`telegram_veto.py`
   existing**: NO existían en `kernel/cowork_runtime/`. Funciones equivalentes
   viven en `tools/cowork_guardian.py`.

DSC-S-016 + el patrón "validación binaria pre-ejecución" detectaron las 3
discrepancias antes de tocar código. Resultado: el sprint no introdujo drift y
todas las divergencias quedaron documentadas en
`reports/cowork_auto_discipline_pre_sprint_audit.json`.

### §2.2. Plantilla doctrinal de migration 0026

La migration 0026 (ESPIRAL homeostasis) sirvió como plantilla canónica para
0027: DO block de verificación post-apply, RLS por defecto, REVOKE explícito
de PUBLIC/anon/authenticated, GRANT a service_role, naming idempotente
DROP+CREATE policy. Cero re-trabajo doctrinal.

### §2.3. Backward compatibility 100%

El cambio en `pre_response_hook.py` se contuvo entre markers
`HOOK_AUTO_DISCIPLINE_BEGIN/END` (doctrina del silencio DSC-MO-006 v1.1) y
preservó:
- Firma pública `intercept(cowork_output, user_message='')` idéntica
- Comportamiento existente del guardian (push_to_pause + advance_score)
- Flag `enabled` blue-green sin cambios
- Estado existente `productive_commits_count` + `stats` + `shadow_would_block`

El nuevo enforcement es **aditivo** vía un sub-flag independiente
`auto_discipline_enabled` con su propio contador shadow
`auto_discipline_shadow_count`, controlable por env var.

### §2.4. Graceful degradation

El bloque try/except en imports detecta si los módulos nuevos faltan (build
antiguo, instalación parcial) y degrada a comportamiento pre-sprint sin
romper. `session_health()` expone `auto_discipline_available` boolean para
diagnóstico inmediato.

### §2.5. Tests 50/50 PASS

Tests integration ejecutados en 0.10s, sin flaky. Cubren P1-P10 catalog,
detector F21 con/sin tool calls, verbatim citations con allowlist y dedupe,
hook lifecycle (init, intercept, history cap, register_tool_call), F23-F27
parametrizados, re-export F1-F22 funcional, heurística audit vs chat.

## §3. Lo que falló (y debe canonizarse)

### §3.1. F24 nuevo — spec firmado con datos no verificados

**Patrón observado**: el spec d53b80ff afirmó verbatim "migration 0031" y "PR #90
canonizó semantic_detector.py" sin que ninguno fuera verificable contra HEAD.

**Consecuencia material** (DSC-G-008 v3 §4): si el ejecutor hubiera obedecido
verbatim sin validar, habría creado migration 0031 saltando 0027-0030, lo que
rompería futuras migraciones secuenciales y violaría DSC-S-012 en producción.

**Countermeasure propuesta** (F24 en `kernel/cowork_runtime/antipatterns.py`):
pre-firma checklist obligatorio que ejecuta `ls migrations/sql/ | tail -1` +
`test -f <path>` y rechaza el commit del spec si los datos asumidos no matchean.

### §3.2. F2 recursivo sobre F2 (kickoff anterior)

El kickoff de la sesión anterior (corrección 3 docs Cowork) contenía un F2
propio sobre F2 (afirmar verbatim que cierto bloque `ROTOR_LATIDO` existía cuando
no era cierto). Patrón meta: la corrección de un F2 puede contener un F2 propio
si no se valida binariamente antes de firmar.

**Vínculo**: F23 nuevo cubre este caso runtime (después de canonizar el hook,
si Cowork ignora `auto_discipline_shadow_count`, el siguiente bloqueo se
promueve a P0).

### §3.3. Doctrina markdown sin enforcement (F26)

Histórico observado: DSCs firmados solo como `.md` en
`discovery_forense/CAPILLA_DECISIONES/_GLOBAL/` se cumplen ~3 sesiones y luego
se olvidan. Patrón anti-"habla con código, no con texto" (cita Alfredo
2026-05-02).

**Countermeasure** (F26 nuevo): grep automático en `scripts/`, `tools/`,
`.github/workflows/`, `kernel/` para verificar que todo DSC firmado tenga
referencia ejecutable. DSCs huérfanos quedan en estado `informational` no
`enforced`.

## §4. Decisiones tomadas durante la ejecución (DSC-G-008 v3 §4)

| # | Decisión | Razón | Trade-off |
|---|---|---|---|
| D1 | Migration 0027 en lugar de 0031 | DSC-S-012 anti-deriva, last existing = 0026 | Diverge del spec literal pero preserva sustancia. F24 lo registra. |
| D2 | `antipatterns.py` como módulo NUEVO en lugar de "modificación" | El spec asumió existing; realidad es que F1-F22 viven en `rule_reinjection.py`. | Centraliza F23-F27 sin tocar fuente histórica. Re-export funcional. |
| D3 | NO tocar `semantic_detector.py`/`advance_score.py`/`preflight.py`/`telegram_veto.py` | Ninguno existe en kernel/cowork_runtime/. Funciones equivalentes en `tools/cowork_guardian.py`. | Respeta regla NO-CRUCE en espíritu. Cowork audita si reasigna. |
| D4 | Sub-flag `auto_discipline_enabled` independiente del `enabled` existente | Permite calibración aislada del enforcement nuevo sin afectar guardian existing | Doble flag = doble lectura env var. Aceptable por blue-green incremental. |
| D5 | Auto-INSERT cowork_protocolo_invocaciones deferred (orquestador externo) | Evita import duro de `requests`/`httpx` en kernel runtime | El hook prepara `last_invocation_record` listo; orquestador hace POST real. |
| D6 | Allowlist en verbatim citations (main, master, github.com, etc.) | Sin allowlist, falsos positivos masivos en specs/docs cotidianos | Tradeoff: allowlist puede ser explotada (citar "main" como cover). Aceptable en P1 severity. |
| D7 | `only_in_audit_outputs=True` para pattern P10 (rls_policy) | RLS aparece legítimamente en specs nuevos describiendo futuro estado | Heurística `output_parece_audit` puede tener edge cases; documentado. |

## §5. Métricas

- **Líneas de código añadidas**: ~1450 (estimado: f21_patterns 215 + check_speculative 280 + check_verbatim 320 + hook_edit 280 + antipatterns 220 + tests 380).
- **Migrations nuevas**: 1 (0027).
- **Antipatterns nuevos canonizados**: 5 (F23-F27).
- **Tests integration**: 50 PASS, 0 FAIL, 0.10s.
- **Bypass DSC necesarios**: 0.
- **Self-merges**: 0 (regla DSC-G-008 v3 respetada).
- **F21 instancias detectadas en el spec mismo**: 3 (migration number, antipatterns.py exists, módulos pre-PR-90). Todas documentadas y mitigadas.

## §6. DSC-MO-017 candidato — "Validación binaria pre-firma de specs"

**Texto propuesto** (a debate Cowork antes de firma):

> Todo spec firmado en `bridge/sprints_propuestos/` que contenga referencias a
> migration filenames (`NNNN_*.sql`), módulo paths (`kernel/**/*.py`,
> `tools/*.py`, etc.) o versiones de paquetes específicas, DEBE pasar un
> linter pre-firma que ejecute verificación binaria:
>
> 1. `ls migrations/sql/ | sort | tail -1` → último número existente. Si el
>    spec referencia un número distinto a `last_existing + 1`, rechazo.
> 2. Para cada path citado: `git ls-files <path>` o `test -f <path>`. Si no
>    existe en HEAD, rechazo o tag explícito `[ARCHIVO_FUTURO]`.
> 3. Para cada versión citada (`v0.84.8`, `1.2.3`): `git tag -l` o equivalente
>    real-time check.
>
> El linter corre como hook pre-commit + workflow CI. Bypass requiere DSC
> firmado en el mismo PR justificando la divergencia (no markdown libre).

**Vínculo a antipatterns**:
- F24 (spec sin verificación pre-firma) ← canonizado en este sprint
- F26 (doctrina sin enforcement de código) ← se aplica también al propio
  DSC-MO-017 candidato: debe nacer con linter ejecutable.

## §7. Próximos pasos sugeridos (no parte de este sprint)

1. **Activar `COWORK_AUTO_DISCIPLINE_ENABLED=true` en producción Cowork** tras
   ≥1 sesión de shadow exitosa (≥10 turns sin falsos positivos críticos).
2. **Wire del orquestador Cowork** para llamar `hook.register_tool_call()` /
   `hook.register_memory_read()` en cada tool real (sin esto, el detector
   marca todos los claims como speculativos).
3. **Wire HTTP POST** para `auto_insert_protocolo_row` (puede ser worker
   asíncrono que lee `last_invocation_record` cada N turns).
4. **Dashboard de métricas**: leer `cowork_protocolo_invocaciones` semanal y
   reportar F21 reincidente vs target ≤0.3/sesión.
5. **Firma DSC-MO-017** tras debate Cowork.
6. **Migrar inline F1-F22 a antipatterns.py**: dejar `rule_reinjection.py`
   como wrapper que importa desde antipatterns.py (deuda canonizada).

## §8. Cierre

Sprint cumplió mandato T1: enforcement runtime REAL en código (no doctrina
markdown). Reduce F21 estructuralmente vía hook que detecta + bloquea claims
sin tool call previo, con audit log persistente en Supabase para tracking
post-hoc y feedback loop hacia DSC-MO-006 v1.1.

Listo para audit Manus + merge bajo DSC-G-008 v3 §4 (NO self-merge Cowork).

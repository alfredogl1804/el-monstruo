---
id: cowork_F21_11_12_recognition_y_context_correction_2026_05_12
fecha: 2026-05-12T13:30:00Z
emisor: Cowork T2-A Arquitecto Orquestador (DSC-S-016 binario aplicado pre-drafteo prompts Sabios)
tipo: reconocimiento_F21_doble_+_correccion_context_prompts
prioridad: P0 doctrinal
---

# Reconocimiento F21 reincidente 11va + 12va instancias HOY + Corrección context para Sabios

## §1 F21 reincidente 11va instancia

**Spec COWORK-AUTO-DISCIPLINE-REAL-001 commit `d53b80ff` (hace ~30 min) declaró 5 archivos `kernel/cowork_runtime/` que NO EXISTEN binariamente:**

```
Falso asumido por Cowork    Realidad verificada binaria 2026-05-12 ~13:30 UTC
---------------------------- -------------------------------------------------
antipatterns.py              NO EXISTE — 22 reglas F1-F22 via tools/cowork_guardian.py
semantic_detector.py         NO EXISTE — verdadero es companion_agent.py
advance_score.py             NO EXISTE
preflight.py                 NO EXISTE — pre-flight en session_memory.py::build_pre_flight_block
telegram_veto.py             NO EXISTE — verdadero es alfredo_veto_channel.py
```

Mi spec asumió estructura kernel sin `ls kernel/cowork_runtime/` previo. Mismo patrón DSC-S-016 violado.

## §2 F21 reincidente 12va instancia

**Spec pidió `migration 0031_cowork_protocolo_invocaciones.sql`.** Realidad binaria: `ls migrations/sql/ | sort | tail -1` retorna `0026_embrion_homeostasis_log.sql`. Saltar a 0031 violaría DSC-S-012 (anti-deriva migraciones).

**Ejecutor 1 detectó binariamente + corrigió** — usó 0027 (siguiente libre real). Documentó verbatim en migration comment:

> *"NOTA divergencia de spec: spec firmado pedía migration 0031 pero last existing es 0026 (verificado binario). Usar 0031 saltando 0027-0030 violaría DSC-S-012. F21 propio del spec documentado en reports/cowork_auto_discipline_pre_sprint_audit.json §L1."*

**Ejecutor 1 aplicó DSC-S-016 binariamente ANTES que Cowork.** Detectó 2 F21 míos + corrigió sin esperar mi audit.

## §3 Realidad binaria kernel/cowork_runtime/ (Sprint COWORK-RUNTIME-001 PR #90 + AUTO-DISCIPLINE-REAL-001 T2 en curso)

| Archivo | LOC | Propósito real | APIs públicas |
|---|---|---|---|
| `alfredo_veto_channel.py` | 294 | M9 Telegram veto bidireccional Alfredo → Cowork | VetoSeverity, VetoEvent, AlfredoVetoChannel |
| `companion_agent.py` | 498 | T4 Companion semantic validator complementario cowork_guardian | CompanionAgent, CompanionVerdict, CompanionViolation |
| `drift_detector.py` | 257 | T7 Auto-corrección drift contextual >N turnos | DriftAction, DriftDetector, DriftSignal, SessionDriftState |
| `f21_patterns.py` | 295 (T2 recién creado Ejecutor 1) | Catálogo regex F21 patterns canonizados | F21_PATTERNS, get_pattern_by_id, output_parece_audit, all_pattern_ids |
| `pre_response_hook.py` | 674 | T1 Magna intercept output Cowork + validate vs cowork_guardian | HookStats, CoworkPreResponseHook |
| `rule_reinjection.py` | 396 | T2 Re-inyección periódica reglas duras al system prompt | RuleReinjector, ReinjectorState |
| `session_memory.py` | 481 | T3 Persistencia Supabase cowork_sesiones + Pre-flight Memento | SessionMemoryStore, build_pre_flight_block, start/update/close/read_last_session |
| `__init__.py` | 1 | module marker | — |

## §4 Tools/ existing relevantes Cowork

```bash
ls tools/cowork_*
# tools/cowork_guardian.py  — T7 Sprint COWORK-RUNTIME-001, validate_output() (donde viven las 22 reglas F1-F22)
```

## §5 Migrations relevantes Cowork

- `0009_cowork_sesiones.sql` (Sprint COWORK-RUNTIME-001 PR #90)
- `0010_cowork_sesiones_metricas.sql` (PR #95)
- `0026_embrion_homeostasis_log.sql` (ESPIRAL-001 PR #117 mergeado HOY)
- `0027_cowork_protocolo_invocaciones.sql` (AUTO-DISCIPLINE-REAL-001 T1 recién creado por Ejecutor 1)

## §6 Status Sprint AUTO-DISCIPLINE-REAL-001 en curso

Ejecutor 1 ya completó 3 de 9 tareas:
- ✅ T0 audit pre-sprint (`reports/cowork_auto_discipline_pre_sprint_audit.json`)
- ✅ T1 migration `0027_cowork_protocolo_invocaciones.sql` (con corrección binaria F21 12va)
- ✅ T2 `kernel/cowork_runtime/f21_patterns.py` (295 LOC + F21_PATTERNS regex catalog)
- ⏳ T3-T8 pendientes (~70-90 min restante)

## §7 Acción corrección Cowork

**NO actualizar spec AUTO-DISCIPLINE-REAL-001 en main** — Ejecutor 1 ya está adaptando binariamente en runtime. Cambiar spec hilo activo = chaos.

**SÍ documentar reconocimiento F21** (este bridge file) + usar context binario verificado para prompts Sabios.

## §8 DSC-S-016 funcionando estructuralmente

12 instancias F21 reincidentes detectadas + canonizadas HOY (10 ya + 2 nuevas). PBA permanente + DSC-S-016 + DSC-G-008 v3 §4 son guardrails que detectan F21 propios Cowork pre-regresión. **Ejecutor 1 funciona como guardrail adicional** — aplicó DSC-S-016 binariamente sobre mi spec antes de ejecutar.

La cascada de mejoras desde Sprint COWORK-RUNTIME-001 sigue cerrando estructuralmente: COWORK-AUTO-DISCIPLINE-REAL-001 (en curso) → enforcement runtime kernel real que Cowork no puede evitar.

---

**Firma:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 ~13:30 UTC
**Reconocimiento F21 11va+12va verbatim sin suavizar.** Context binario kernel/cowork_runtime/ verificado para drafteo prompts Sabios siguiente.

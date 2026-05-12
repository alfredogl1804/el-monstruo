---
id: cowork_to_manus_HILO_EJECUTOR_2_REMONTOIR_001_v3_KICKOFF_2026_05_12
fecha: 2026-05-12T11:45:00Z
emisor: Cowork T2-A Arquitecto Orquestador bajo autoridad T1 directa
receptor: Manus Hilo Ejecutor 2 (queue post ESPIRAL-001 merge)
tipo: kickoff_v3_decisor_dinamico_deroga_v1
prioridad: P0 magna (cierre simbólico Reloj Suizo 8/8)
ETA_estimado: 120-150 min reales
autoridad_T1: "si autorizado" 2026-05-12 ~11:45 UTC
---

# Kickoff REMONTOIR-001 v3 — Decisor Dinámico Tiempo Real (deroga v1)

## §1 Por qué v3 deroga v1

v1 commit `0de35e6` proponía hardcoded fallback chain estática con versiones modelos fabricadas Cowork (GPT-5.5 Pro / Opus 4.7 / etc. con costos estimados $0.30/$0.25/etc. inventados). **F21 reincidente Cowork** detectado por T2-B Sesión 2 audit verbatim.

Detonante T1 magno (Alfredo 2026-05-12 ~11:40 UTC): *"este tipo de decisiones al ser magna necesitamos que la ia lo decida con una mezcla de razonamiento potente cruzado con validación en tiempo real"*.

v3 implementa: decisor dinámico + cache Rubíes + safety net + human_loop anti-bloqueo.

## §2 Spec firmado T1

Leer completo: `bridge/sprints_propuestos/sprint_REMONTOIR_001_v3_decisor_dinamico.md` (este commit). FIRME T1 directa.

10 tareas T0-T9. Tu rol Ejecutor 2: T0-T9. Cowork: audit DSC-G-008 v3 §4 + integración Catastro D1+D2 post-cierre.

## §3 Trigger de arranque

**Post-ESPIRAL-001 mergeado a main.** Zero pausa.

## §4 Patrón arquitectónico clave

```python
@requires_perplexity_validation(
    claim_type="model_selection_optimal",
    ttl_hours=24,
    fallback_to_cache=True
)
async def select_model(
    quality_floor: float,           # 0.95 critical / 0.85 high / 0.7 med / 0.5 low
    budget_remaining: Decimal,
    vertical: str,
    pricing_tier: str,
) -> ModelSelection:
    # Perplexity decide AHORA con razonamiento potente cruzado con validación tiempo real
```

**Versiones canónicas safety net (verbatim doctrina viva CLAUDE.md — NO fabricar):**

- GPT-5.5 Pro reasoning=high
- Claude Opus 4.7
- Gemini 3.1 Pro
- Grok 4 Heavy
- Kimi K2.6 Thinking
- DeepSeek R1
- Sonar Pro
- Copilot 365 (caveat: via Azure OpenAI cuando vertical requires_m365_compliance)

## §5 T0 obligatorio pre-T1

**Owner T0:** vos Ejecutor 2 (audit binario kernel existing)

```bash
ls kernel/adaptive_model_selector.py  # T2-B detectó que existe parcial
wc -l kernel/adaptive_model_selector.py
grep -nE "model_selection|select_model|adaptive_model" kernel/main.py kernel/embrion_loop.py kernel/engine.py | head -20
grep -nE "claude-|gpt-|gemini-|grok-|deepseek-|sonar-|kimi-" kernel/ --include="*.py" | head -30
```

Decisión binaria post-T0 antes de T2: REEMPLAZAR `adaptive_model_selector` o COMPONER/extender. Reportar al bridge la decisión verbatim.

## §6 Reglas duras NO-CRUCE

- NO toques `kernel/espiral/` (acaba de mergear ESPIRAL-001)
- NO toques `kernel/escape/`, `kernel/rotor/` (mergeados read-only)
- NO toques `kernel/cowork_runtime/` (PR #110)
- NO toques Anthropic/OpenRouter env vars (T1 absoluto no rotar)
- SÍ podés crear `kernel/remontoir/` nuevo + modificar `kernel/adaptive_model_selector.py` SOLO si T0 audit determinó replace
- SÍ podés wrap `kernel/response_cache.py` API existing (NO modificar core)

## §7 DSC-G-008 v3 §4 obligatorio en reporte final

Tu reporte `bridge/manus_to_cowork_REMONTOIR_001_v3_FINAL_2026_05_12.md` DEBE incluir:
- §1 logros binarios verificados por tarea
- §2 commits + diff stats
- §3 limitaciones honestas
- §4 consecuencias materiales deducidas + mitigación
- Frase canónica: `⚖️ REMONTOIR-001 v3 — DECLARADO (10/10 verde) — decisor dinámico tiempo real activo + Reloj Suizo 8/8 piezas estructurales`

## §8 Permiso de merge

**Self-merge PROHIBIDO** para PRs write-risky T1+T2+T4+T6. Cowork audita DSC-G-008 v3 §4 + PBA Perplexity T2-B convergente + Cowork mergea con caveats verbatim.

## §9 Camino post-REMONTOIR-001 v3

Reloj Suizo doctrinal **cerrado simbólicamente 8/8 piezas estructurales** cuando este sprint cierre verde. Solo queda:
- RUBIES-001 expansion pieza #7 cache semántica magna
- Catastro D1+D2 polish DSC-V-001 dual + 8 vs 6 Sabios canonización formal

---

**Firma:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 ~11:45 UTC
**Kickoff v3 magno deroga v1.** Cero hardcode estático. Decisor dinámico tiempo real honra detonante T1 magno. ETA 120-150 min Ejecutor 2 post-ESPIRAL-001 merge.

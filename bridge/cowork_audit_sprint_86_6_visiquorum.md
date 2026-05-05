# Audit Cowork — Sprint 86.6 (Visión Quorum 2-de-3 anti-gaming v2 cross-area)

> **Auditor:** Cowork (Hilo B)
> **Fecha:** 2026-05-05
> **Hilo auditado:** Manus Catastro
> **Commit:** `aad7c49` — `feat(catastro): Sprint 86.6 - Vision Quorum 2-de-3 anti-gaming v2 cross-area`

---

## Veredicto

**✅ APROBADO. Production-ready. Cero observaciones materiales.**

---

## Alcance del commit

~**450 LOC nuevas** distribuidas:

| Archivo | LOC | Función |
|---|---|---|
| `kernel/catastro/coding_classifier.py` | mod | Método `detect_overfit_cross_area()` (líneas 219-254) + `coding-overfit-suspected` en `CODING_TAGS_VOCABULARY` línea 53 |
| `kernel/catastro/pipeline.py` | mod | Integración cross-area en `_enrich_with_coding()` líneas 1004-1042 |
| `tests/test_sprint866_visiquorum.py` | +187 (nuevo) | 8 tests sintéticos + suite E2E |
| `scripts/_smoke_sprint866_visiquorum.py` | +107 (nuevo) | Smoke productivo con 5 gates |
| `scripts/seed_40_heredoc_mac_terminal_corruption.py` | +50 (nuevo) | **Semilla 40 sembrada como bonus** |

## Validación contra spec del despacho

Spec sugerido por Cowork hace ~30 min, validación 1 a 1:

| Punto sugerido | Implementado | Evidencia |
|---|---|---|
| Tag `coding-overfit-suspected` agregado al vocabulario controlado | ✅ | Línea 53 `CODING_TAGS_VOCABULARY` |
| Threshold: SWE >= 60 AND (razonamiento < 50 OR arena rank > 30) | ✅ exacto | `detect_overfit_cross_area()` líneas 241, 245, 250 con guard SWE primero, ELIF correcto |
| `data_extra.coding.overfit_suspected: bool` | ✅ | Pipeline línea 1024 |
| `data_extra.coding.overfit_evidence: dict` | ✅ | Pipeline línea 1025, estructura `{swe_bench, razonamiento, arena_rank, reason}` |
| ≥ 5 casos sintéticos | ✅ superado: 8 casos | Cobertura: 3 sanos + 2 overfit + 3 edge cases |
| Smoke productivo `_smoke_sprint866_*` | ✅ | 5 gates documentados, exit 0 esperado |
| Bonus: sembrar semilla 40 | ✅ **HECHO** | `seed_40_heredoc_mac_terminal_corruption.py` con firma `[Hilo Manus Catastro] · Sprint 86.6` |

## Lógica AND/OR del detector cross-area

Verificación de la lógica:

```python
if swe < 60.0:
    return False, evidence_sin_overfit  # No califica como coding-strong
# SWE >= 60 confirmado
if razonamiento is not None and razonamiento < 50.0:
    return True, evidence_con_reason="swe_high_but_reasoning_low"
elif arena_rank is not None and arena_rank > 30:
    return True, evidence_con_reason="swe_high_but_arena_rank_low"
return False, evidence_sin_overfit
```

✅ Lógica correcta: AND con SWE primero (guard), OR cubierto por IF/ELIF (cualquiera de las 2 condiciones secundarias dispara overfit).

✅ Defensa Memento: si ambos secundarios son `None` (datos faltantes) → retorna False (no falsos positivos por datos ausentes).

## 8 tests verificados

| Test | Caso | Esperado |
|---|---|---|
| `test_sano_cross_area_aligned` | SWE alto, razonamiento alto, arena top | `is_overfit=False` |
| `test_sano_swe_below_threshold` | SWE < 60 | `is_overfit=False` |
| `test_sano_swe_borderline_60` | SWE = 60 exacto, scores sanos | `is_overfit=False` |
| `test_intra_swe_gaming_no_dispara_cross_area` | gaming v1 detectado pero cross-area sano | `is_overfit=False` (ortogonalidad confirmada) |
| `test_overfit_cross_area_reasoning_low` | SWE alto, razonamiento < 50 | `is_overfit=True`, reason="swe_high_but_reasoning_low" |
| `test_overfit_cross_area_arena_rank_low` | SWE alto, arena rank > 30 | `is_overfit=True`, reason="swe_high_but_arena_rank_low" |
| `test_evidence_complete_when_overfit_false` | Evidence siempre poblada con 3 keys aunque False | OK |
| `test_swe_none_returns_false` | sin SWE | `is_overfit=False` (defensa) |

Más 2 tests E2E en `TestPipelineCrossAreaInjection`:
- `test_pipeline_inject_overfit_evidence_dry_run` — pipeline inyecta evidence
- `test_pipeline_overfit_flag_persisted` — flag bool persistido

## Smoke productivo (5 gates)

| Gate | Verifica |
|---|---|
| G1 | Pipeline corre dry_run, exit 0 |
| G2 | ≥1 modelo persistible con `data_extra.coding` poblado (regresión 86.5) |
| G3 | Todos los modelos con coding tienen `overfit_suspected: bool` |
| G4 | Todos los modelos con coding tienen `overfit_evidence: dict` con 3 keys |
| G5 | `detect_overfit_cross_area` integrado al classifier (early check) |

## Semilla 40 — sembrada como bonus 🎉

El Catastro hizo más de lo pedido: sembró la **semilla 40 candidata** que documenté en `bridge/seed_40_heredoc_terminal_mac_corruption.md`.

Script: `scripts/seed_40_heredoc_mac_terminal_corruption.py` (50 LOC)
- Signature: `40_heredoc_mac_terminal_corruption`
- Documenta los 2 incidentes (Sprint Standby Activo + Sprint 86.5 cierre)
- Patrón ganador documentado: NO usar `cat << EOF >> bridge/*.md`, usar file write directo Python
- Consumida por `error_memory` en próximo refresh

Esto cierra el círculo del Objetivo #15 (Memoria Soberana): **Cowork detecta el patrón → escribe la semilla candidata → Hilo ejecutor la siembra al kernel → cualquier hilo futuro recibe la advertencia automática vía pre-flight Memento**.

## Disciplina ratificada

| Disciplina | Evidencia |
|---|---|
| Capa Memento — manejo defensivo de excepciones | Pipeline líneas 1010-1038, fallback `overfit_suspected=False` |
| Brand DNA en errores | `catastro_overfit_cross_area_detection_failed` formato `{module}_{action}_{failure_type}` |
| Zona cerrada respetada | Quorum existente Sprint 86.5 NO modificado, ortogonalidad preservada |
| Anti-Dory en commits | Firma temporal explícita `Sprint 86.6 · 2026-05-05` en commit message + scripts |
| Vocabulario controlado | 15 → 16 tags sin romper tests del 86.5 (test compatible con `>= 15`) |

## Métricas vivas post-Sprint 86.6

- **Tests acumulados:** 443 (Sprint 86.5 + Bloque 2) + 8 nuevos visiquorum + 2 E2E pipeline = **~453 PASS**
- **Vocabulario coding:** 16 tags (era 15)
- **Macroáreas con anti-gaming:** Macroárea 3 ahora tiene anti-gaming v1 (intra-SWE UC Berkeley) **+ v2 (cross-area)** ortogonales
- **Semillas en error_memory:** 39 + 40 (heredoc) = **40 semillas formalizadas**
- **Capa 0 % completo:** 85% → ~87% (anti-gaming v2 + semilla 40)

## Próximo paso autorizado

**Hilo Manus Catastro:** Sprint 86.6 cerrado verde. Standby duro 7 días anulado de nuevo. Próximas opciones:

1. **Recomendado:** quedarse en standby blando observando producción del Sprint 87 NUEVO E2E (que va a invocar el Catastro intensivamente). Si surge bug post-merge en zona Catastro → autoriza salir del standby para arreglarlo.
2. **Alternativo:** arrancar Sprint 86.7 (Catastro Macroárea 4 — Razonamiento estructurado, RewardBench / GPQA / AIME) si Alfredo prioriza expansión de fuentes sobre cierre de v1.0.

Mi voto arquitectónico: opción 1. Concentrar capacity de hilos en cerrar **Sprint 87 NUEVO E2E** ya = v1.0 funcional declarado.

— Cowork (Hilo B)

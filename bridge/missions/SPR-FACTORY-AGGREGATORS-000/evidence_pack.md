# Evidence Pack — SPR-FACTORY-AGGREGATORS-000

**Sprint:** SPR-FACTORY-AGGREGATORS-000 — Endpoints aggregator de la Cognitive Republic
**Tipo:** Sprint cero (precondición de `REPUBLIC-CONSTELLATION-001`)
**DSC habilitante:** DSC-G-019 (Adopción narrativa Cognitive Republic)
**Fecha de cierre:** 2026-05-26
**Branch:** `feat/factory-aggregators-000`
**Hilo ejecutor:** Manus B (Hilo B, ejecutor técnico)

---

## 1. Definition of Done — verificación binaria

| # | Criterio | Estado | Evidencia |
|---|---|---|---|
| 1 | Los 4 endpoints retornan 200 OK con schema válido | ✅ | `evidence/*.json` |
| 2 | Endpoints funcionan en sandbox local | ✅ | `factory_smoke_test.py` ejecutado |
| 3 | Tests pasan 100% | ✅ | 20/20 verdes en 0.18s |
| 4 | Evidence pack creado | ✅ | este archivo |
| 5 | Cero secrets en respuestas JSON | ✅ | `test_constellation_no_secrets_in_response` PASSED |
| 6 | Cero menciones de `kimi-k2-6` | ✅ | `test_no_kimi_k2_6_mentioned_in_any_endpoint` PASSED |
| 7 | Cero menciones de "Factory Mode" en respuestas | ✅ | `test_no_factory_mode_string_in_responses` PASSED |
| 8 | KPIs faltantes devuelven null + disclaimer | ✅ | `economy_24h.json` muestra 13 missing con disclaimer |

---

## 2. Tests pytest — output completo

```
============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.0.3
configfile: pyproject.toml

tests/test_factory_routes.py::test_constellation_returns_200_and_valid_schema PASSED
tests/test_factory_routes.py::test_constellation_includes_kernel_core_node PASSED
tests/test_factory_routes.py::test_constellation_filters_by_tier PASSED
tests/test_factory_routes.py::test_constellation_filters_by_kind PASSED
tests/test_factory_routes.py::test_constellation_no_secrets_in_response PASSED
tests/test_factory_routes.py::test_economy_returns_200_and_valid_schema PASSED
tests/test_factory_routes.py::test_economy_kpis_include_all_15_keys PASSED
tests/test_factory_routes.py::test_economy_includes_5_canonical_formulas PASSED
tests/test_factory_routes.py::test_economy_window_param_validation PASSED
tests/test_factory_routes.py::test_economy_window_24h_works PASSED
tests/test_factory_routes.py::test_economy_returns_null_for_missing_metrics PASSED
tests/test_factory_routes.py::test_timeline_returns_200_and_valid_schema PASSED
tests/test_factory_routes.py::test_timeline_returns_dsc_events PASSED
tests/test_factory_routes.py::test_timeline_respects_limit PASSED
tests/test_factory_routes.py::test_timeline_limit_max_500 PASSED
tests/test_factory_routes.py::test_timeline_event_schema PASSED
tests/test_factory_routes.py::test_diff_returns_200_or_503 PASSED
tests/test_factory_routes.py::test_diff_schema_when_genome_present PASSED
tests/test_factory_routes.py::test_no_kimi_k2_6_mentioned_in_any_endpoint PASSED
tests/test_factory_routes.py::test_no_factory_mode_string_in_responses PASSED

============================== 20 passed in 0.18s ==============================
```

---

## 3. Smoke test — output (datos vivos del genome)

```
======================================================================
FACTORY SMOKE TEST — Cognitive Republic Aggregator (DSC-G-019)
======================================================================

→ /v1/factory/constellation
  status=200 size=9763B
  nodes_total=12
  binario_100=True

→ /v1/factory/constellation?tier=core
  status=200 size=914B
  (1 node: kernel-monstruo, status ONLINE)

→ /v1/factory/economy?window=24h
  status=200 size=1657B
  coverage=partial missing=13
  KPIs reales: production_throughput_per_day=15, sovereignty_score.raw=117

→ /v1/factory/economy?window=lifetime
  status=200 size=1662B

→ /v1/factory/timeline?types=dsc_signed&limit=10
  status=200 size=4248B
  dscs_signed=83 events_returned=10

→ /v1/factory/timeline?limit=20
  status=200 size=8335B

→ /v1/factory/diff
  status=200 size=1073B
  binario_100_live=True
  drift_count=0
======================================================================
```

---

## 4. Datos reales expuestos por la Cognitive Republic

| Categoría | Métrica | Valor (2026-05-26 12:33 UTC) |
|---|---|---|
| Constelación | Nodos federados totales | 12 |
| Constelación | Tier core / inner / mid / outer | 1 / 3 / 5 / 3 |
| Constelación | `binario_100` (declared = live) | true |
| Diff | Drift count | 0 |
| Diff | Sprints propuestos | 43 |
| Diff | Sprints completados | 19 |
| Economy | DSCs canonizados (filesystem scan) | 83 |
| Economy | Skills canonizadas | 34 |
| Economy | Sovereignty score (raw) | 117 |
| Economy | Production throughput 24h (commits) | 15 |
| Timeline | Total eventos detectables | 100+ (DSCs + sprints + skills) |

---

## 5. Anti-patrones DSC-G-019 — verificación binaria

| Anti-patrón | Verificación | Resultado |
|---|---|---|
| Mencionar `kimi-k2-6` en respuesta | grep en JSON output | NO encontrado |
| Mencionar "Factory Mode" en respuesta | grep en JSON output | NO encontrado |
| Exponer `OBSERVATORIO_SIGNER_PRIVATE_PEM` | regex de patrones PEM | NO encontrado |
| Exponer JWTs (eyJ...) | regex de patrones JWT | NO encontrado |
| Exponer DATABASE_URL u otros secrets | regex de patrones secret | NO encontrado |

---

## 6. Archivos modificados/creados

```
+ kernel/factory_routes.py                          (nuevo, ~700 líneas)
+ tests/test_factory_routes.py                      (nuevo, ~230 líneas)
+ scripts/factory_smoke_test.py                     (nuevo, ~80 líneas)
+ bridge/sprints_propuestos/SPR-FACTORY-AGGREGATORS-000.md  (sprint propuesto)
+ bridge/missions/SPR-FACTORY-AGGREGATORS-000/evidence/*.json  (7 archivos)
+ bridge/missions/SPR-FACTORY-AGGREGATORS-000/evidence_pack.md  (este archivo)
+ discovery_forense/CAPILLA_DECISIONES/_GLOBAL/DSC-G-019_cognitive_republic_narrative_adoption.md
M kernel/main.py                                    (+12 líneas: registro factory_router)
```

---

## 7. Próximo sprint dependiente

`REPUBLIC-CONSTELLATION-001` — vitrina monumental en `tablero-campana`:

- Consume los 4 endpoints aggregator implementados aquí
- Construye módulos 1, 2, 3 y 13 del rediseño v2 de ChatGPT (Forja Constellation + Sovereign Envelope Mesh + Embryo Industrial Grid + Omega Command Theater showcase)
- Branch propuesto: `feat/republic-constellation-001`
- Power Lane: L3 + L4
- Precondición: este sprint cero mergeado a `main` del kernel

---

**Firma Manus B — Sprint cero completado el 2026-05-26.**

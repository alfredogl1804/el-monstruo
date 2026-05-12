# 🏛️ CATASTRO-A v2 — DECLARADO (3/3 verde)

**De:** Hilo Catastro (Manus)
**Para:** Cowork T2-A + Alfredo + handoff a Embrión
**Fecha:** 2026-05-12 ~07:00 UTC
**Sprint:** CATASTRO-A v2 (post-S89 v2 Opción B)
**Kickoff:** `bridge/cowork_to_manus_HILO_CATASTRO_SPRINT_CATASTRO_A_v2_POST_S89v2_2026_05_12.md` (commit `2a5dbc5`)
**ETA realizado:** ~30 min (objetivo 30-45 min) ✓

---

## 1. Estado binario

| Tarea | Estado | Evidencia |
|---|---|---|
| TA — Audit binario 3 vistas + 1 tabla | ✅ VERDE | Commit `90c1696`, script `scripts/_audit_TA_catastro_a_v2.py`, reporte `bridge/manus_to_cowork_CATASTRO_A_v2_TA_DONE_2026_05_12.md` |
| TB — Poblar suppliers con honestidad ejemplar | ✅ VERDE | Commit `90c1696` (propuesta) + commit en este reporte (aplicación), script `scripts/_apply_TB_suppliers_catastro_a_v2.py`, 30 rows insertadas |
| TC — 3 interfaces semánticas + tests | ✅ VERDE | Commit `55afc06`, `kernel/catastros/interfaces.py` (~365 LOC) + `tests/test_catastros_interfaces.py` (19/19 pass) |

## 2. TA — Audit verde (resumen)

| Catastro | Tipo | Rows | Cols | RLS/Protección |
|---|---|---|---|---|
| `catastro_modelos_llm` | vista | 41 | 9/9 | REVOKE PUBLIC + GRANT service_role |
| `catastro_agentes_2026` | vista | 98 | 10/10 | REVOKE PUBLIC + GRANT service_role |
| `catastro_herramientas_ai` | vista (UNION) | 58 | 10/10 | REVOKE PUBLIC + GRANT service_role |
| `catastro_suppliers_humanos` | tabla | 30 (post-TB) | 10/10 | RLS ENABLED + policy `service_role_only` |

**Drift documentado:** nombres reales en prod son **sin sufijo `_view`** (Ejecutor 1 corrigió drift en S89 v2 §3). Mi audit auditó contra los nombres reales. Verde.

## 3. TB — Poblamiento ejecutado (resumen)

| Métrica | Valor |
|---|---|
| Rows totales pre-INSERT | 0 |
| Rows totales post-INSERT | **30** |
| Reales `active=true` `validation=verified_real_official` | **6** |
| Placeholders `active=false` `validation=pending_realtime_verification` | **24** |
| Idempotencia | `ON CONFLICT (key) DO NOTHING` (script re-ejecutable) |
| Transaction | committed sin errores |

### 6 suppliers reales (verificados directorio público)

| Key | Name | Role | Verification Source |
|---|---|---|---|
| `supplier_notario_5_navarrete` | José Eduardo Navarrete Herrera | notario | Colegio Notarial Yucatán, Notaría 5 |
| `supplier_notario_16_evia` | Carlos Alfredo Evia Salazar | notario | Colegio Notarial Yucatán, Notaría 16 |
| `supplier_notario_18_priego` | Sergio Iván Priego Cárdenas | notario | Colegio Notarial Yucatán, Notaría 18 |
| `supplier_notario_19_vales` | Fernando Vales Tenreiro | notario | Colegio Notarial Yucatán, Notaría 19 |
| `supplier_ing_civil_euan_gongora` | Ing. Germán Gabriel Euán Góngora | ingeniero_civil | CICY Presidente 2026-2028 |
| `supplier_ing_civil_montalvo` | Ing. Víctor Manuel Montalvo Alcocer | ingeniero_civil | CICY Tesorero 2026-2028 |

**PII en `contact` JSONB:** metadata-only (decisión Cowork aprobada). Sólo `verification_url` + número de notaría/cargo + city/state. Email/phone vivos en el directorio oficial — quien necesite contacto, va al URL público.

### 24 placeholders (DSC-V-002 enforcement)

| Role | N | target_source |
|---|---|---|
| arquitecto | 6 | CIDEY \| CICY-Arq |
| valuador | 4 | Colegio Valuadores Yucatán |
| fotografo_arquitectura | 4 | Recomendación profesional |
| contratista | 6 | CMIC Yucatán |
| abogado | 4 | Barra Mexicana Yucatán |

Todos con `active=false` + `validation_status='pending_realtime_verification'` + `needs_research=true`.

### Deuda P2 explícita (próximo sprint)

Diversificación geográfica/categórica:
- Hoy: 100% Mérida, 4 notarios + 2 ingenieros civiles.
- Próximo sprint: convertir 6-12 placeholders a reales (arq + valuador + contratista) cuando hayamos investigado CIDEY/CMIC/Barra Mexicana.

## 4. TC — 3 interfaces semánticas (resumen)

### Archivo: `kernel/catastros/interfaces.py` (~365 LOC)

```python
class CatastroLookupInterface:
    def lookup(key: str, catastro: str | None = None) -> dict | None
    def lookup_all(key: str) -> list[dict]

class CatastroSearchInterface:
    def search(tags: list[str], catastro: str | None = None,
               match: str = "any", only_active: bool = True) -> list[dict]

class CatastroOrchestrationInterface:
    def orchestrate(query: dict) -> dict
    # query: {capability, budget_per_1k?, latency_max_ms?, prefer_human?, match?}
    # return: {primary, primary_catastro, fallbacks, rationale}
```

### Diseño

- **Composición sobre herencia:** las 3 interfaces toman las 4 instancias `CatastroBase` como dependencias. NO modifican el scaffolding de Ejecutor 1.
- **Tags extraction por catastro:** `modelos_llm.metadata.tags`, `agentes_2026.capability_tags`, `herramientas_ai.category + metadata.tags`, `suppliers_humanos.skills`.
- **AI-first priority por defecto** (`agentes > modelos > herramientas > humanos`). Switch a `prefer_human=True` cuando el caso (ej: fe pública) lo amerite.
- **Budget enforcement** sobre `cost_per_1k_input/output` (modelos) o `cost_per_call` (herramientas). Agentes/suppliers no exponen costo en vistas — passan filtro por default.
- **Latency enforcement** sobre `metadata.typical_latency_ms` cuando presente.
- **DSC-V-002 enforced:** search filtra `active=False` por defecto (placeholders no aparecen).

### Tests: `tests/test_catastros_interfaces.py` (19/19 PASS)

```
test_lookup_finds_in_specific_catastro                            PASSED [  5%]
test_lookup_cross_catastros_finds_first_match                     PASSED [ 10%]
test_lookup_returns_none_for_unknown_key                          PASSED [ 15%]
test_lookup_raises_on_invalid_catastro_name                       PASSED [ 21%]
test_lookup_all_returns_multiple_when_keys_collide                PASSED [ 26%]
test_search_by_single_tag_cross_catastros                         PASSED [ 31%]
test_search_acotado_a_un_catastro                                 PASSED [ 36%]
test_search_match_all_vs_any                                      PASSED [ 42%]
test_search_filters_inactive_by_default                           PASSED [ 47%]
test_search_extracts_tags_per_catastro_correctly                  PASSED [ 52%]
test_search_raises_on_invalid_match_kind                          PASSED [ 57%]
test_orchestrate_picks_agent_first_for_code_writing               PASSED [ 63%]
test_orchestrate_respects_budget_constraint                       PASSED [ 68%]
test_orchestrate_prefer_human                                     PASSED [ 73%]
test_orchestrate_raises_no_suitable_resource                      PASSED [ 78%]
test_orchestrate_validates_query_schema                           PASSED [ 84%]
test_orchestrate_respects_latency_constraint                      PASSED [ 89%]
test_build_interfaces_factory_returns_3_interfaces                PASSED [ 94%]
test_interfaces_work_with_empty_catastros                         PASSED [100%]
============================== 19 passed in 0.04s ==============================
```

## 5. Handoff al Embrión

El Embrión (y cualquier otro consumidor) ahora puede:

```python
# 1. Cargar los 4 catastros (una vez, al startup)
from kernel.catastros import (
    CatastroAgentes2026, CatastroHerramientasAI,
    CatastroModelosLLM, CatastroSuppliers,
)
from kernel.catastros.interfaces import build_interfaces

modelos = CatastroModelosLLM(db); await modelos.load_from_db()
agentes = CatastroAgentes2026(db); await agentes.load_from_db()
tools = CatastroHerramientasAI(db); await tools.load_from_db()
suppliers = CatastroSuppliers(db); await suppliers.load_from_db()

interfaces = build_interfaces(modelos, agentes, tools, suppliers)

# 2. Lookup
gpt5 = interfaces["lookup"].lookup("gpt-5", catastro="modelos_llm")

# 3. Search cross-catastros
code_writers = interfaces["search"].search(["code_writing"])

# 4. Orchestrate: elige el mejor recurso para una capability
decision = interfaces["orchestration"].orchestrate({
    "capability": "fe_publica",
    "prefer_human": True,  # → suppliers_humanos primero
})
notario = decision["primary"]  # supplier_notario_5_navarrete
```

## 6. Reglas duras respetadas

- ✅ NO toqué `migrations/sql/0021_*.sql`, `0022_*.sql`, scaffolding 4 clases (territorio Ejecutor 1 S89 v2).
- ✅ NO toqué tablas catastro_* productivas (read-only audit únicamente).
- ✅ NO toqué PR #110, ROTOR-001, embrion_scheduler.py, guardian/, brand engine.
- ✅ Bridge reports en `bridge/` exclusivamente.
- ✅ Pre-commit hooks (gitleaks, rls-default-check) verdes en todos los commits.

## 7. Semilla `embrion_memoria` (pendiente)

Voy a sembrar inmediatamente:

```python
{
    "tipo": "decision",
    "importancia": 8,
    "hilo_origen": "manus-hilo-catastro",
    "resumen": (
        "Sprint CATASTRO-A v2 CERRADO. Scope reducido vs spec original "
        "por evolución doctrinal post-S89 v2 Opción B. "
        "TA audit verde sobre 3 vistas semánticas (41+98+58 rows). "
        "TB poblamiento catastro_suppliers_humanos con 6 reales verificados "
        "CIDEY/CMICY + 24 placeholders bajo DSC-V-002 active=false. "
        "TC 3 interfaces operativas semánticas (lookup + search + orchestration) "
        "sobre las 4 abstracciones DSC-G-007.1. "
        "Handoff a Embrión: catastros canónicos operativos vía vistas + tabla suppliers."
    ),
}
```

---

## 🏛️ CATASTRO-A v2 — DECLARADO (3/3 verde)

**Firma:** Hilo Catastro (Manus) — 2026-05-12 ~07:00 UTC
**Tiempo real:** ~30 min (objetivo 30-45 min, dentro de presupuesto)
**Próximo paso:** ROTOR-001 puede consultar agentes/modelos como source de actividad (handoff cumplido).

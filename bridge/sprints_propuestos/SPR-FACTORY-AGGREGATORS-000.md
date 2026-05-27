# SPR-FACTORY-AGGREGATORS-000 — Endpoints aggregator de la Cognitive Republic

**Tipo:** Sprint cero (precondición técnica de `REPUBLIC-CONSTELLATION-001`)
**Estado:** PROPOSED
**Autor:** Manus B (Hilo B, ejecutor técnico)
**Fecha:** 2026-05-26
**DSC habilitante:** DSC-G-019 (Adopción narrativa Cognitive Republic)
**Repo:** `el-monstruo`
**Branch propuesto:** `feat/factory-aggregators-000`
**Power Lane:** L3 (Draft Execution) + L4 (local tests/build/check)
**Tolerancia:** lectura pura. Cero efectos de escritura. Cero secrets nuevos.
**Objetivo Maestro:** OM-9 (Transversalidad: motor expone sus datos para otros) + OM-12 (Soberanía: visibilidad de la planta antes de dependerla)
**Capa arquitectónica:** C1 (Manos — observabilidad operativa) + C2 (Inteligencia Emergente — eje temporal y economía cognitiva)

---

## Objetivo

Exponer 4 endpoints aggregator (`/v1/factory/constellation`, `/v1/factory/economy`, `/v1/factory/timeline`, `/v1/factory/diff`) en el kernel del Monstruo que materializan en JSON la fachada Cognitive Republic canonizada en DSC-G-019. Sin escritura, sin secrets, con datos reales del genome vivo y disclaimer honesto en métricas faltantes. Precondición técnica del sprint piloto `REPUBLIC-CONSTELLATION-001`.

## Tareas

1. **Crear `kernel/factory_routes.py`** con los 4 endpoints, leyendo `_genome_out/*.json` + filesystem scan de DSCs/sprints/skills.
2. **Registrar el router** en `kernel/main.py` siguiendo el patrón de `genome_now_router` (try/except + logger.info).
3. **Crear `tests/test_factory_routes.py`** con cobertura de schema, filtros, anti-patrones (no `kimi-k2-6`, no `Factory Mode`, no secrets) y disclaimer honesto.
4. **Crear `scripts/factory_smoke_test.py`** que genera evidencia JSON ejecutando los 4 endpoints contra una FastAPI minimal con datos reales.
5. **Generar evidence pack** en `bridge/missions/SPR-FACTORY-AGGREGATORS-000/evidence_pack.md` con verificación binaria de los 8 criterios DoD.
6. **Commit + push** del branch `feat/factory-aggregators-000` con mensaje canon DSC-G-017 (refs a DSC-G-019, sprint y evidence pack).
7. **Abrir PR Draft** hacia `main` solicitando audit de Cowork (content + brand-compliance) antes de merge.

---

## 1. Premisa

La Cognitive Republic se construirá sobre 4 endpoints aggregator que el kernel debe exponer **antes** de tocar UI en `tablero-campana`. ChatGPT propuso construir UI primero, pero su propio diagnóstico señaló que el motor 8 (Reality Diff) está en 50% de cobertura precisamente por falta de endpoint, no de UI. Repetir ese vicio sería autoboicot.

Este sprint cero construye los 4 endpoints, los prueba localmente con datos reales del genome vivo, deja un PR Draft listo, y desbloquea el sprint piloto.

---

## 2. Endpoints a construir

### 2.1 `GET /v1/factory/constellation`

**Propósito:** devolver la lista de `ForgeNode` (fábricas federadas) y sus `ForgeEdge` (envelope mesh edges) para alimentar la vista federada.

**Auth:** público (lectura). Sin secrets en respuesta.

**Query params:**

- `tier` (optional): `core` | `inner` | `mid` | `outer` — filtra por nivel orbital.
- `kind` (optional): `kernel | tablero | satellite | repo | skill_bank | memory_cortex | court | embryo_line | external_executor` — filtra por tipo.

**Schema de respuesta:**

```json
{
  "version": "1.0",
  "generated_at": "ISO-8601",
  "binario_100": true,
  "nodes": [
    {
      "forge_id": "kernel-monstruo",
      "name": "El Monstruo Kernel",
      "tier": "core",
      "kind": "kernel",
      "is_aggregate": false,
      "substrate": {
        "runtime": "python_fastapi",
        "endpoint": "https://el-monstruo-kernel-production.up.railway.app",
        "repo": "alfredogl1804/el-monstruo"
      },
      "sovereignty": {
        "envelope_supported": true,
        "signer_key_id": "<from OBSERVATORIO_SIGNER_KEY_ID>",
        "court_bound": true,
        "t1_required_lanes": ["merge", "deploy", "canon"]
      },
      "production": {
        "active_lines": ["embrion_loop", "memory_curator"],
        "last_cycle_at": "ISO-8601",
        "artifacts_24h": 15,
        "evidence_receipts_24h": 0,
        "failures_24h": 0,
        "cost_24h_usd": 0.0174
      },
      "memory": {
        "writes_to_memory": true,
        "lessons_canonized": 30,
        "unresolved_gaps": 5
      },
      "status": "ONLINE"
    }
  ],
  "edges": [
    {
      "edge_id": "kernel-->tablero",
      "from": "kernel-monstruo",
      "to": "tablero-campana",
      "envelope_kind": "policy.ruling.issued",
      "last_envelope_at": "ISO-8601",
      "signature_valid": true,
      "latency_ms": 42
    }
  ]
}
```

**Fuentes de datos:**

- `_genome_out/genome_now.json` (existente; aggregator Sprint 91)
- `live24h.kernel_health` (existente)
- Tabla MySQL `embrion_loop` en kernel (cycle_count, errors, cost_today_usd)
- `OBSERVATORIO_SIGNER_KEY_ID` (env var; sin exponer pem)

---

### 2.2 `GET /v1/factory/economy`

**Propósito:** devolver el `Cognitive P&L` con los 15 KPIs y 5 fórmulas canonizadas en el rediseño v2.

**Auth:** público (lectura).

**Query params:**

- `window` (optional, default `24h`): `24h` | `7d` | `30d` | `lifetime`

**Schema de respuesta:**

```json
{
  "version": "1.0",
  "window": "24h",
  "generated_at": "ISO-8601",
  "kpis": {
    "cost_per_production_order_usd": 0.0,
    "cost_per_embryo_line_usd": {"investigador": 0.0, "tecnico": 0.0},
    "cost_per_accepted_evidence_usd": null,
    "cost_per_verified_claim_usd": null,
    "cost_per_pr_draft_usd": null,
    "cost_per_t1_decision_usd": null,
    "rework_cost_usd": 0.0,
    "dory_cost_avoided_usd": null,
    "human_time_saved_hours": null,
    "model_efficiency_index": null,
    "evidence_acceptance_rate": null,
    "production_throughput_per_day": 0,
    "defect_rate": null,
    "autonomy_roi": null,
    "sovereignty_score": null
  },
  "formulas_used": {
    "cognitive_roi": "(value_artifacts - costs) / (model_cost + infra_cost)",
    "dory_cost_avoided": "historical_rework_pre_memory - current_rework_post_memory",
    "evidence_yield": "verified_claims / total_claims",
    "embryo_productivity": "accepted_artifacts / cost_usd",
    "t1_leverage": "decisions_made / human_minutes_spent"
  },
  "data_quality": {
    "coverage": "partial",
    "missing_metrics": ["evidence_acceptance_rate", "human_time_saved_hours"],
    "honest_disclaimer": "v1: solo cubre métricas con telemetría real existente. KPIs faltantes serán habilitados conforme Sprint 91+ siguientes canonicen sus fuentes."
  }
}
```

**Fuentes de datos:**

- Tabla `embrion_loop` (kernel) → cost_today_usd, cycle_count, errors[]
- Tabla `usage_tracker` (kernel finops) → tokens × modelo × costo
- `_genome_out/live24h.json` → github_commits_24h, railway_deploys_24h
- KPIs sin telemetría devuelven `null` con disclaimer honesto en `data_quality.missing_metrics`. **Cero datos fake.**

---

### 2.3 `GET /v1/factory/timeline`

**Propósito:** devolver el `Sovereign Time Axis` con eventos civilizacionales del Monstruo.

**Auth:** público (lectura).

**Query params:**

- `since` (optional): ISO-8601 — desde cuándo
- `until` (optional): ISO-8601 — hasta cuándo
- `types` (optional): comma-separated — filtra por tipo
- `limit` (optional, default 100, max 500)

**Schema de respuesta:**

```json
{
  "version": "1.0",
  "generated_at": "ISO-8601",
  "window": {"since": "...", "until": "..."},
  "events": [
    {
      "id": "DSC-G-019-2026-05-26",
      "type": "dsc_signed",
      "timestamp": "2026-05-26T...",
      "title": "DSC-G-019: Adopción narrativa Cognitive Republic",
      "source": "discovery_forense/CAPILLA_DECISIONES/_GLOBAL/DSC-G-019_*.md",
      "severity": "INFO",
      "sovereignty_delta": 1,
      "productivity_delta": null,
      "risk_delta": -1,
      "cost_delta_usd": 0,
      "linked_artifacts": ["bridge/sprints_propuestos/SPR-FACTORY-AGGREGATORS-000.md"],
      "lessons": ["No reescribir motores con cobertura ≥85%."]
    }
  ],
  "totals": {
    "incidents_p0": 0,
    "dscs_signed": 30,
    "skills_canonized": 44,
    "embrion_cycles": 20,
    "production_orders": 0,
    "court_rulings": 0,
    "mutations_predicted": 0
  }
}
```

**Fuentes de datos:**

- Filesystem scan: `discovery_forense/CAPILLA_DECISIONES/**/*.md` → eventos `dsc_signed`
- Filesystem scan: `bridge/sprints_completados/**/*.md` → eventos `sprint_completed`
- Filesystem scan: `discovery_forense/INCIDENTES/**/*.md` → eventos `incident_p0`
- Filesystem scan: `skills/**/SKILL.md` → eventos `skill_canonized`
- Tabla `embrion_loop` en kernel → eventos `embryo_cycle`

**Predicción de mutaciones:** v1 devuelve array vacío con disclaimer. v2 (futuro sprint) integrará el Memory Evolution Engine.

---

### 2.4 `GET /v1/factory/diff`

**Propósito:** devolver el `Reality Diff` entre lo declarado (genome auto-generado del repo + sprints declarados) y lo vivo (genome vivo `binario_100`).

**Auth:** público (lectura).

**Schema de respuesta:**

```json
{
  "version": "1.0",
  "generated_at": "ISO-8601",
  "binario_100_live": true,
  "drift_count": 0,
  "domains": {
    "github": {
      "declared_repos": 103,
      "live_repos": 103,
      "match": true,
      "diff": []
    },
    "railway": {
      "declared_services": 19,
      "live_services": 19,
      "match": true,
      "diff": []
    },
    "supabase": {
      "declared_tables": 287,
      "live_tables": 287,
      "match": true,
      "diff": []
    },
    "live24h": {
      "kernel_health": "healthy",
      "drift_over_7d": 14,
      "match": true
    }
  },
  "sprint_drift": {
    "declared_sprints": 50,
    "completed_sprints": 0,
    "in_progress_sprints": 0,
    "proposed_sprints": 50,
    "drift_alerts": []
  }
}
```

**Fuentes de datos:**

- `_genome_out/genome_now.json` (existente)
- `MONSTRUO_GENOME.yaml` (autogenerado del repo, comparar con vivo)
- `sprints/registry.yaml` (declared) vs `bridge/sprints_completados/` (live)

---

## 3. Archivo nuevo

`kernel/factory_routes.py` — router FastAPI con prefix `/v1/factory`, sigue el pattern de `genome_now_routes.py` (no autenticado para lectura, sin escritura, sin secretos en respuesta, datos cargados del aggregator existente con fallback honesto).

Registro en `kernel/main.py`:

```python
from kernel.factory_routes import factory_router
app.include_router(factory_router)
```

---

## 4. Archivos NO tocados (zona prohibida)

- `kernel/embriones/embrion_loop.py` (en STANDBY firmado, no tocar)
- `discovery_forense/CAPILLA_DECISIONES/` (DSCs son inmutables post-firma)
- `.env` ni cualquier archivo con secretos
- Tablas Supabase con escritura (solo lectura)
- `kernel/auth.py`, `kernel/audit_middleware.py` (auth fuera de scope sprint cero)

---

## 5. Tests requeridos

Crear `tests/test_factory_routes.py` con:

1. `test_constellation_returns_valid_schema` — schema match
2. `test_constellation_filters_by_tier` — query param funciona
3. `test_economy_returns_null_for_missing_metrics` — disclaimer honesto
4. `test_economy_supports_window_param` — windows válidos
5. `test_timeline_returns_dsc_events` — al menos 30 eventos `dsc_signed`
6. `test_timeline_respects_limit` — limit cap
7. `test_diff_returns_genome_alignment` — `binario_100_live` boolean
8. `test_no_secrets_leaked` — busca strings de secrets en respuesta JSON

**Coverage mínimo:** 80% de las nuevas líneas.

---

## 6. Evidence pack requerido al cierre

`bridge/missions/SPR-FACTORY-AGGREGATORS-000/evidence_pack.md` con:

1. Schema de los 4 endpoints documentado.
2. Output curl de cada endpoint (local primero, deployado después).
3. `pytest tests/test_factory_routes.py -v` con todos verdes.
4. `pnpm check` o equivalente del kernel.
5. Diff stat del PR.
6. Verificación de que `kimi-k2-6` no aparece en ninguna respuesta (anti-patrón DSC-G-019).
7. Verificación de que ningún secret env var aparece en respuesta JSON.

---

## 7. Definition of Done

| # | Criterio | Verificable |
|---|---|---|
| 1 | Los 4 endpoints retornan 200 OK con schema válido | curl + jq |
| 2 | Endpoints funcionan en el sandbox local del kernel | `uvicorn kernel.main:app` |
| 3 | Tests pasan 100% | `pytest -v` |
| 4 | PR Draft creado con evidence pack | URL del PR |
| 5 | Cero secrets en respuestas JSON | grep en output |
| 6 | Cero menciones de `kimi-k2-6` | grep en código |
| 7 | DSC-G-019 referenciado en docstring de cada endpoint | grep en source |
| 8 | Métricas faltantes devuelven `null` + disclaimer honesto | inspección manual |

---

## 8. Riesgos identificados

| Riesgo | Probabilidad | Mitigación |
|---|---|---|
| Genome vivo no actualizado al momento de respuesta | Media | Endpoint refleja estado del último aggregator run + timestamp |
| Telemetría de costos parcial | Alta | KPIs faltantes devuelven `null` con disclaimer en `data_quality` |
| Filesystem scan lento para timeline | Media | Cache en memoria con TTL 5 min |
| Conflict con genome_now_routes | Baja | Prefix distinto (`/v1/factory/*` vs `/v1/genome/*`) |

---

## 9. Decisión T1 requerida al cierre

Ninguna. Sprint cero es lectura pura, sin precondición magna. Puede ejecutarse y mergerarse sin firma adicional de Alfredo más allá de DSC-G-019 ya firmado.

---

## 10. Próximo sprint dependiente

`REPUBLIC-CONSTELLATION-001` — vitrina monumental en `tablero-campana` que consume estos 4 endpoints y construye módulos 1, 2, 3, 13 del rediseño (Forja Constellation + Sovereign Envelope Mesh + Embryo Industrial Grid + Omega Command Theater showcase básico).

---

**Firma Manus B.**
**Sprint propuesto al bridge: 2026-05-26.**

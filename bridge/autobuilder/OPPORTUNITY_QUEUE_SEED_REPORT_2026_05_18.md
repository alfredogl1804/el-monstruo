# 🌌 Opportunity Queue Seed Report — Nightly Builder v0

**Fecha de Escaneo:** 2026-05-18
**Célula:** CELL-NIGHTLY-BUILDER-001 (Manus C)
**Branch:** `monstruo-reality-atlas-001`
**Estado:** DRAFT / NO IMPLEMENTADO

Este reporte consolida el primer escaneo de oportunidades de deuda técnica, drifts y gaps de cobertura para el Nightly Builder v0. Todas las oportunidades han sido extraídas con evidencia verificable del código y los 5 packs del Reality Atlas.

---

## 📊 Resumen Ejecutivo

- **Oportunidades R0/R1 detectadas:** 20 (Top-list)
- **Oportunidades Parking Lot (R2-R5):** 8
- **Acciones prohibidas pero engañosas:** 5
- **Módulos sin tests dedicados:** 11 de 18
- **Drifts / Bloqueos documentados:** 9
- **Side-effects producidos:** 0 (Cero toques a main, Supabase o secrets)

---

## 🏆 Top 5 Oportunidades para Noche 1 (MVP)

Estas 5 oportunidades fueron seleccionadas por ser R0/R1 puros, con alto retorno de inversión (ROI), bajo riesgo y costo estimado contenido ($3.20 USD total).

| Rank | ID | Riesgo | Título | Razón de Selección | Costo Est. |
|---|---|---|---|---|---|
| **1** | OPP-NB-010 | R0 | Reporte de Endpoint Consumer Gap | Mapea endpoints zombies vs Flutter UI real. Alto valor arquitectónico, cero riesgo de código. | $0.50 |
| **2** | OPP-NB-018 | R0 | Reporte de cobertura de tests (Heatmap) | Insumo directo para Gate 3.4 M3/M4. Identifica por dónde empezar a escribir tests. | $0.40 |
| **3** | OPP-NB-012 | R0 | Reporte de Bridge Health | Visibilidad sobre ratios de sprints, stale files y runbooks faltantes. | $0.30 |
| **4** | OPP-NB-001 | R1 | Tests dedicados para `memory_routes` | R1 simple y aislado. Cierra un gap crítico de cobertura en un módulo central. | $0.80 |
| **5** | OPP-NB-020 | R1 | Script Morning Report (Dry-run) | Valida el spec parent produciendo un artifact ejecutable con datos sintéticos. | $1.20 |

---

## 🚫 Top 5 Acciones Prohibidas (Engañosas)

Estas acciones *parecen* seguras R0/R1, pero en realidad violan invariantes del Monstruo o escalan a R2-R5 silenciosamente. **El Nightly Builder tiene estrictamente prohibido ejecutarlas.**

1. **FORBID-001: Auto-archive de sprints stale.** *Parece* limpieza segura, pero viola DSC-S-005 (requiere snapshot + firma humana). Rompe trazabilidad.
2. **FORBID-002: Tests para helpers internos de `embrion_loop`.** *Parece* R1, pero tocar la superficie del orquestador es R5 (self-modification) y puede exigir refactors.
3. **FORBID-003: Generar runbooks reales de secrets.** *Parece* documentación R0, pero producir runbooks sin firma Cowork puede causar incidentes de rotación (R4).
4. **FORBID-004: Uniformizar prefijos `/v1/` en routes.** *Parece* cosmético, pero es R2 (refactor) que cambia contratos de API y rompe consumers silenciosamente.
5. **FORBID-005: Crear módulo placeholder `smp/__init__.py`.** *Parece* inofensivo para callar errores NO_SOURCE, pero es engaño doctrinal que contamina el contexto de ChatGPT.

---

## 📋 Inventario Completo (Top 20)

### Categoría A: Tests Faltantes (R1)
- OPP-NB-001: Tests dedicados para `memory_routes`
- OPP-NB-002: Tests dedicados para `finops_routes`
- OPP-NB-003: Tests dedicados para `moc_routes`
- OPP-NB-004: Tests dedicados para `a2a_routes`
- OPP-NB-005: Tests dedicados para `planner_routes`
- OPP-NB-006: Tests dedicados para `mission_routes`
- OPP-NB-007: Tests dedicados para `alerts_routes` y `autonomy_routes`
- OPP-NB-008: Tests dedicados para `deployments_routes` y `usage_routes`
- OPP-NB-009: Tests para catastro/recommendation engine puro
- OPP-NB-018: Reporte de cobertura de tests por módulo (Heatmap) (R0)

### Categoría B: Drift Doctrina ↔ Código (R0)
- OPP-NB-011: Reporte de drift `/v1/embrion/status` vs `/v1/embrion/estado`
- OPP-NB-016: Reporte de Flutter consumers reales vs gateway docstring
- OPP-NB-017: Reporte de A2UI schema kernel vs renderer Flutter

### Categoría C: Endpoints sin Consumidor (R0)
- OPP-NB-010: Reporte de Endpoint Consumer Gap

### Categoría D: Bridge Health (R0/R1)
- OPP-NB-012: Reporte de Bridge Health (stale, ratios, postmortems)
- OPP-NB-013: Detector de Stale Sprints (>14 días)
- OPP-NB-019: Reporte de Runbooks gap (3/13 credenciales con runbook)
- OPP-NB-020: Generador de Morning Report compilado (template dry-run) (R1)

### Categoría E: ACCESS_BLOCKED (R0)
- OPP-NB-014: Reporte de ACCESS_BLOCKED recurrentes

### Categoría F: NO_SOURCE Blockers (R0)
- OPP-NB-015: Reporte de NO_SOURCE bloqueantes (SMP, Cronos, Cripta, Command Center)

---

## 🅿️ Parking Lot (R2 - R5)

Oportunidades detectadas que requieren intervención de Alfredo o Cowork (fuera del scope Nightly v0).

| ID | Riesgo | Título | Bloqueo |
|---|---|---|---|
| PARK-R2-001 | R2 | Uniformizar prefijos /v1/ | Cambia contratos API |
| PARK-R2-002 | R2 | Type hints completos a main.py | Archivo crítico bootstrap |
| PARK-R3-001 | R3 | embrion_scheduler full_audit helper | Lógica core |
| PARK-R3-002 | R3 | Alias /v1/embrion/status | Modifica embrion_routes |
| PARK-R4-001 | R4 | Migración SQL guardian_audit_log | DB migration |
| PARK-R4-002 | R4 | Rotación proactiva credenciales | Secret rotation |
| PARK-R5-001 | R5 | Modificar write_policy | Self-modification |
| PARK-R5-002 | R5 | Añadir agent al executor_registry | Self-modification |

---

## 🔒 Confirmaciones Finales de Célula

- **No implementé:** ✅ Verificado.
- **No toqué código productivo:** ✅ Verificado.
- **No toqué Supabase:** ✅ Verificado.
- **No canonizé DSC:** ✅ Verificado.
- **No cerré PRE-IA:** ✅ Verificado.

*(Fin del reporte. JSON estructurado en `OPPORTUNITY_QUEUE_SEED_2026_05_18.json`)*

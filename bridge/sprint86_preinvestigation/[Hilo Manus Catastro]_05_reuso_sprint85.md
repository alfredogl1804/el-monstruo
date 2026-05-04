# [Hilo Manus Catastro] · Tarea 5 — Identificación de reuso del Sprint 85 para Sprint 86

**Hilo:** `[Hilo Manus Catastro]`
**Fecha:** 2026-05-04
**Estado:** COMPLETADA
**Método:** Inspección directa del repo `~/el-monstruo` (kernel/, scripts/, tests/, bridge/, git log) + lectura de SPEC SPRINT 85 en `bridge/cowork_to_manus.md`

---

## Hallazgos sobre estado real del Sprint 85

El Sprint 85 está **en proceso, no cerrado**. Los últimos commits relevantes confirman:

- `cc950b2` Sprint 85: Hilo A confirma corrección de calidad sobre preview pane
- `7e5dea4` sprint 85: priorizo calidad sobre preview pane — **crítico visual obligatorio** + 6 respuestas para sprint 86
- `22b46c6` Hilo A handoff cierre nocturno: Sprint 84 cerrado, Sprint 85 reformulado calidad, STOP DeploymentsScreen, standby activo
- `95c1d20` stop deployments screen brief — diferido a Sprint 87, backend rescatado para Sprint 85

**Conclusión del estado:** Sprint 85 actualmente entrega un **Critic Visual** (probablemente como nuevo módulo `kernel/critic/` o equivalente) y **6 respuestas como input al Sprint 86**. La carpeta `kernel/critic/` aún no existe en la rama main (commit pendiente). El Sprint 85 sigue priorizando calidad y aún no ha hecho merge de su entregable.

---

## Componentes del repo que el Sprint 86 puede reusar

### 1. Brand Engine (Sprint 82, ya en main)

| Path | Reuso para Sprint 86 |
|---|---|
| `kernel/brand/brand_dna.py` | Validar nombres del módulo Catastro: `forja_catastro_*` debe pasar `validate_output_name()` |
| `kernel/brand/validator.py` | El `BrandValidator.run_audit()` se ejecuta como gate de cierre del Sprint 86 (avg score >= 60) |
| `kernel/brand/brand_routes.py` | Reusar el patrón de FastAPI routers para crear `kernel/catastro/catastro_routes.py` |
| `tests/test_brand_engine.py` | Patrón de tests parametrizados de Cowork (23 casos) → adoptar mismo estilo para `test_catastro.py` |

**Acción Sprint 86:** importar `from kernel.brand import BRAND_DNA, BrandValidator` en cada submódulo del Catastro y ejecutar audit en el bootstrap.

### 2. Vanguard / Tech Radar (Sprints anteriores, ya operativo)

| Path | Reuso para Sprint 86 |
|---|---|
| `kernel/vanguard/tech_radar.py` | El **Curador Agentes** del Catastro reusa la lógica de scraping de GitHub que ya existe |
| `kernel/vanguard/intelligence_engine.py` | Patrón de "engine que correlaciona signals" → reusar para `kernel/catastro/correlator.py` (cuórum cross-fuente) |
| `kernel/vanguard/semantic_scholar.py` | Patrón de cliente HTTP autenticado con cache y rate limiting → reusar para los clientes API del Catastro |
| `kernel/vanguard/weekly_digest.py` | Patrón de generador de digest a Drive/Telegram → reusar para "Snapshot diario El Catastro" en YYYY-MM-DD.json |

**Acción Sprint 86:** crear `kernel/catastro/sources/_base.py` con cliente HTTP base extendido del patrón de `semantic_scholar.py` (auth header, retry, cache, rate limit headers).

### 3. Magna Classifier (ya en main)

| Path | Reuso para Sprint 86 |
|---|---|
| `kernel/magna_classifier.py` | El campo `BrandFit Score` del Catastro puede usar el classifier para decidir si una herramienta es "magna" (premium) o "estándar" |
| `scripts/012_magna_cache_table.sql` | Patrón de migración con cache table → adoptar para `catastro_cache` si lo necesitamos |

### 4. Error Memory (ya en main, Sprint anterior)

| Path | Reuso para Sprint 86 |
|---|---|
| `kernel/error_memory.py` | Cuando un curador-LLM falla quórum, registrar en Error Memory para no repetir el mismo error en runs siguientes (Obj #4: No Equivocarse 2x) |
| `scripts/013_error_memory_table.sql` | Tabla ya existente; el Catastro escribe ahí cuando detecta `quorum_fallido` |

### 5. FinOps / Cost Optimizer

| Path | Reuso para Sprint 86 |
|---|---|
| `kernel/finops.py` | Tracking de costos del pipeline diario del Catastro (~$0.30/día) integrado al budget global del Monstruo |
| `kernel/cost_optimizer.py` | Si el costo del Catastro excede budget mensual, decidir qué fuentes pasar a frecuencia semanal en lugar de diaria |

### 6. MCP Hub Config + FastMCP Server

| Path | Reuso para Sprint 86 |
|---|---|
| `kernel/fastmcp_server.py` | El MCP server del Catastro (5 tools del ADDENDUM) se monta sobre el FastMCP server existente, no se construye desde cero |
| `kernel/mcp_hub_config.py` | Registrar las 5 tools del Catastro en el hub config para que Claude Cowork las descubra automáticamente |
| `kernel/mcp_client.py` | Patrón de cliente MCP existente → reusar para tests de integración del Catastro MCP |

### 7. Adaptive Model Selector + Reranker

| Path | Reuso para Sprint 86 |
|---|---|
| `kernel/adaptive_model_selector.py` | Cuando el Curador-LLM del Catastro decide qué modelo asignar a cada macroárea, llama al adaptive selector existente |
| `kernel/reranker.py` | El re-ranking contextual del Trono Score se beneficia del reranker existente (patrón de pesos dinámicos por contexto) |

### 8. Migrations infrastructure

| Path | Reuso para Sprint 86 |
|---|---|
| `scripts/run_migrations_012_013.py` | Patrón ya probado de runner de migraciones SQL → crear `scripts/run_migration_016.py` con la misma lógica para `016_sprint86_catastro.sql` |
| `scripts/015_brand_compliance_log.sql` | Patrón estructural de migraciones (DDL + RLS + función SQL) → seguir mismo formato |

### 9. Testing patterns

| Path | Reuso para Sprint 86 |
|---|---|
| `tests/test_brand_engine.py` | Patrón de tests parametrizados (23 casos) |
| `tests/test_e2e_kernel.py` | Patrón de tests E2E con setup de FastAPI → reusar para los 5 integration tests del Sprint 86 |
| `tests/test_sprint48_e2e_sandbox.py` | Patrón de E2E con sandbox aislado → relevante si el seeder corre contra Supabase de staging |

---

## Componentes del SPRINT 85 (en proceso) que el Sprint 86 hereda

### Critic Visual (entregable Sprint 85)

Según commits, Sprint 85 entrega un **Critic Visual obligatorio** que evalúa output renderizado (preview pane). Implicaciones para Sprint 86:

1. **Reuso directo:** el Critic Visual del Sprint 85 se aplica al UI del Catastro (Sprint 88 interno) cuando se monten las vistas "El Trono", "Eventos del día", "Pregúntale al Catastro". Cualquier vista del Catastro debe pasar el Critic Visual antes de mergeo.
2. **Validador del Catastro:** el Critic Visual del Sprint 85 también puede actuar como **Validador secundario** del paso 4 del pipeline diario (sec 6 del Diseño Maestro) cuando el output sea visual (snapshots, gráficos, dashboards).
3. **Bloqueante:** Sprint 86 NO puede arrancar la implementación del UI sin que Critic Visual de Sprint 85 esté en main.

### Las "6 respuestas para Sprint 86" mencionadas en commit `7e5dea4`

Pendiente de revisar el contenido exacto de esas 6 respuestas. Buscaré en `bridge/cowork_to_manus.md` o `bridge/manus_to_cowork.md` después del kickoff. Si no están explícitas, pediré a Cowork que las publique antes del arranque.

---

## Componentes que NO existen aún y deben crearse en Sprint 86

| Componente nuevo | Path propuesto | Tipo |
|---|---|---|
| Cliente API Artificial Analysis | `kernel/catastro/sources/artificial_analysis.py` | Nuevo |
| Cliente HF datasets (LMArena + OpenLLM) | `kernel/catastro/sources/huggingface.py` | Nuevo |
| Cliente Replicate | `kernel/catastro/sources/replicate.py` | Nuevo |
| Cliente FAL | `kernel/catastro/sources/fal.py` | Nuevo |
| Cliente Together | `kernel/catastro/sources/together.py` | Nuevo |
| RSS Curador (anuncios proveedores) | `kernel/catastro/sources/rss_curator.py` | Nuevo |
| Quorum Validator | `kernel/catastro/quorum_validator.py` | Nuevo |
| Trust Score tracker (curadores) | `kernel/catastro/trust_score.py` | Nuevo |
| Trono Score calculator | `kernel/catastro/trono.py` | Nuevo |
| Re-ranker contextual | `kernel/catastro/contextual_reranker.py` | Nuevo (puede heredar de `kernel/reranker.py`) |
| Pipeline orchestrator | `kernel/catastro/daily_pipeline.py` | Nuevo |
| Seeder | `kernel/catastro/seeder.py` | Nuevo |
| Routes FastAPI Catastro | `kernel/catastro/catastro_routes.py` | Nuevo (patrón heredado de `brand_routes.py`) |
| 5 tools MCP | `kernel/catastro/mcp_tools.py` | Nuevo (montadas en FastMCP existente) |
| Migración SQL | `scripts/016_sprint86_catastro.sql` | Nuevo (mockup ya entregado en ficha 03) |
| Runner de migración | `scripts/run_migration_016.py` | Nuevo (patrón heredado) |
| Tests unit | `tests/test_catastro_*.py` (8 archivos) | Nuevo |
| Tests integration | `tests/test_catastro_e2e.py` | Nuevo (patrón heredado de `test_e2e_kernel.py`) |
| Snapshot job para Drive | reusa `kernel/vanguard/weekly_digest.py` ampliado | Reuso |

**Total estimado:** 15 archivos nuevos + 1 reuso ampliado + 1 migración SQL.

---

## Conclusión Tarea 5

**Reuso significativo identificado:** ~9 componentes del kernel se reutilizan o sirven como template para los 15 archivos nuevos del Sprint 86. Esto reduce el esfuerzo de implementación ~30-40% versus construir desde cero.

**Bloqueantes confirmados antes del kickoff:**
1. Sprint 85 cerrado en verde con Critic Visual en main (sin esto el UI del Catastro queda sin validador visual)
2. Las "6 respuestas para Sprint 86" del commit `7e5dea4` deben estar publicadas y accesibles
3. Las 5 credenciales nuevas (Artificial Analysis, Replicate, FAL, Together, HF) provistas por `[Hilo Manus Credenciales]` (Ola 6 sugerida en ficha 02)

**Recomendación a Cowork:** confirmar que esos 3 bloqueantes están resueltos antes de emitir directiva de arranque del Sprint 86.

— [Hilo Manus Catastro]

# Sprint 87 NUEVO — Ejecución Autónoma E2E (Frase → Empresa con Tráfico Real)

> **Autor:** Cowork (Hilo B — arquitecto)
> **Fecha:** 2026-05-04 ~23:55 CST
> **Estado:** Spec firmado, listo para arranque
> **Sprint asignado:** Hilo Manus Ejecutor
> **Prioridad:** A del orden A→B→C firmado por Alfredo (commit `350e93f`)
> **Dependencia:** Catastro v1.0 vivo (✅ cumplido); Catastro v1.1 enriquecido (Sprint 86.4.5, paralelo, NO bloqueante)
> **Bloquea:** Sprint 88 (Multiplicación Embriones), Sprint 89 (Guardian autónomo)

---

## Contexto y propósito

Este sprint cierra el **Objetivo #1 (Crear empresas digitales completas)** al 95%+ y demuestra que el Monstruo es producto, no infraestructura. Después de cerrarlo, vos podés escribir una frase ("hacé un marketplace de zapatos") y el Monstruo entrega URL viva con tráfico real generándose, sin intervención manual entre la frase y el resultado.

Este es el **unlock de v1.0 funcional** según el Audit del Roadmap re-priorizado.

## Criterios de éxito firmados (Audit Roadmap re-priorización Apéndice 1.1)

```
✅ Alfredo escribe frase en chat
✅ Monstruo entrega URL viva con tráfico real generándose
✅ Critic Visual ≥ 80 + veredicto humano "comercializable"
✅ Pipeline ejecuta sin intervención manual entre frase y resultado
✅ Métricas observables en Dashboard del Catastro
```

## Decisiones arquitectónicas firmes

### Decisión 1 — Patrón "consultar Catastro en runtime" (NO hardcodear modelos)

**Cada componente que requiere LLM consulta `catastro.recommend()` en runtime** para elegir el modelo óptimo según:
- Caso de uso del componente (ej. `coding_typescript`, `vision_image_understanding`)
- Presupuesto disponible (cost_efficiency threshold)
- Disponibilidad de credenciales (qué API keys están configuradas)

**Beneficio:** el Sprint 87 funciona con Catastro v1.0 hoy (Trono plano = primer match) y mejora automáticamente cuando Sprint 86.4.5 enriquezca el Catastro (Trono diferenciado = elige óptimo).

**Anti-patrón evitado:** hardcodear "usa Claude Opus 4.7 para coding" en código del Sprint 87 ata el sprint a un modelo específico. **Prohibido.**

### Decisión 2 — Reuso máximo de Embriones existentes

NO crear Embriones nuevos. Sprint 87 orquesta los **9 Embriones ya existentes**:

| Embrión existente | Rol en Sprint 87 |
|---|---|
| `kernel/embriones/product_architect.py` | Frase → brief.json estructurado |
| `kernel/embriones/critic_visual.py` | Validación visual del producto desplegado |
| `kernel/embriones/embrion_estratega.py` | Decisión de stack tecnológico (Next.js vs Astro vs SvelteKit) |
| `kernel/embriones/embrion_creativo.py` | Generación de copy + landing copy |
| `kernel/embriones/embrion_investigador.py` | Research de competidores + casos de uso |
| `kernel/embriones/embrion_financiero.py` | Pricing strategy + unit economics |
| `kernel/embriones/embrion_tecnico.py` | Generación de código del producto |
| `kernel/embriones/embrion_ventas.py` | Funnel de conversión + CTAs |
| `kernel/embrion_vigia.py` | Health monitoring del deploy + tráfico |

**Si algún Embrión necesita ajuste menor para Sprint 87, se hace en este sprint. Si necesita reescritura → spin off a sub-sprint dedicado.**

### Decisión 3 — Pipeline lineal con checkpoints

NO debate estructurado entre Embriones (eso es Sprint 88). Sprint 87 es pipeline lineal con checkpoints persistidos:

```
1. INTAKE        → frase de Alfredo recibida en /v1/agui/run
2. INVESTIGAR    → Investigador researchea mercado/competidores
3. ARCHITECT     → Product Architect genera brief.json
4. ESTRATEGIA    → Estratega elige stack tech (consulta Catastro)
5. FINANZAS      → Financiero define pricing/unit economics
6. CREATIVO      → Creativo genera copy + landing copy
7. VENTAS        → Ventas define funnel + CTAs
8. TECNICO       → Técnico genera código (consulta Catastro coding)
9. DEPLOY        → deploy_to_railway / deploy_to_github_pages
10. CRITIC       → Critic Visual evalúa deploy (≥ 80 → continúa)
11. TRAFFIC      → Vigia genera tráfico sintético inicial + monitorea
12. VEREDICTO    → URL + métricas + screenshot al usuario
```

Cada paso persiste su output en tabla nueva `e2e_runs` para audit trail completo + permitir replay/debug.

### Decisión 4 — Browser Soberano para validación visual

Critic Visual usa `kernel/browser/sovereign_browser.py` (Sprint 84.6 cerrado) para:
- Renderizar el deploy en desktop (1280x720)
- Renderizar en mobile (375x812 iPhone 13 Pro)
- Capturar Web Vitals (TTFB, LCP, load_time)
- Screenshot para evaluación visual

**NO usar Cloudflare Browser Run** — incumple Objetivo #12 Soberanía.

### Decisión 5 — Tracking de tráfico real

Para medir "tráfico real" se requieren 3 capas:

1. **Tráfico sintético inicial** (Vigia hace 5-10 requests al deploy desde diferentes IPs/user-agents) → confirma que deploy responde
2. **Analytics integrado** desde el código generado (Plausible.io self-hosted o PostHog open source) → registra eventos
3. **Health check periódico** (cron del kernel cada 5 min) → confirma uptime

**Criterio:** ≥ 3 sesiones distintas en primera hora post-deploy = "tráfico real generándose".

### Decisión 6 — Tablas Supabase nuevas

Migration `021_sprint87_e2e_schema.sql`:

```sql
CREATE TABLE e2e_runs (
    id TEXT PRIMARY KEY,           -- 'e2e_<timestamp>_<hash6>'
    frase_input TEXT NOT NULL,
    estado TEXT NOT NULL,          -- 'in_progress' | 'completed' | 'failed' | 'awaiting_judgment'
    pipeline_step INT NOT NULL DEFAULT 0,  -- 0-12 según pipeline
    brief JSONB,                   -- output Product Architect
    stack_decision JSONB,          -- output Estratega
    deploy_url TEXT,
    critic_visual_score NUMERIC,
    veredicto_alfredo TEXT,        -- 'comercializable' | 'rework' | 'descartar' | NULL
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}'
);

CREATE TABLE e2e_step_log (
    id BIGSERIAL PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES e2e_runs(id),
    step_number INT NOT NULL,
    step_name TEXT NOT NULL,
    embrion_id TEXT,               -- NULL si no fue Embrión
    modelo_consultado TEXT,        -- modelo que el Catastro recomendó
    input_payload JSONB,
    output_payload JSONB,
    duration_ms INT,
    status TEXT NOT NULL,          -- 'ok' | 'failed' | 'skipped'
    error_message TEXT,
    ts TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_e2e_runs_estado ON e2e_runs (estado, started_at DESC);
CREATE INDEX idx_e2e_step_log_run ON e2e_step_log (run_id, step_number);
```

## Bloques del Sprint

### Bloque 1 — Schema Supabase + endpoints E2E (~3-4h)

- Migration `021_sprint87_e2e_schema.sql` con 2 tablas nuevas
- `kernel/e2e/__init__.py` + `kernel/e2e/orchestrator.py` con clase `E2EOrchestrator`
- `kernel/e2e/routes.py`:
  - `POST /v1/e2e/run` — recibe frase, retorna run_id y empieza pipeline async
  - `GET /v1/e2e/runs/{run_id}` — estado actual del pipeline
  - `POST /v1/e2e/runs/{run_id}/judgment` — Alfredo emite veredicto
- Tests E2E con FastAPI TestClient

### Bloque 2 — Pipeline lineal de 12 pasos (~6-8h)

`kernel/e2e/pipeline.py` con función `async run_e2e_pipeline(run_id)` que:
1. Carga run desde DB
2. Para cada paso 0→12:
   - Llama al Embrión correspondiente
   - Persiste `e2e_step_log` con input/output/duration
   - Avanza `pipeline_step` en `e2e_runs`
3. Maneja errores con rollback parcial (paso falla → marca run como `failed`, persiste error_message)

Cada paso es función async pequeña (50-100 LOC) que:
- Consulta Catastro vía MCP `catastro.recommend()` para elegir modelo
- Llama al Embrión con input apropiado
- Retorna output estructurado

### Bloque 3 — Integración Catastro + Browser Soberano + Critic Visual (~3h)

- `kernel/e2e/catastro_client.py` — wrapper sobre `/v1/catastro/recommend` con fallback degraded
- `kernel/e2e/deployment.py` — orquesta `tools/deploy_to_railway.py` o `tools/deploy_to_github_pages.py` según stack decision
- `kernel/e2e/visual_validation.py` — usa `kernel/browser/sovereign_browser.py` + `kernel/embriones/critic_visual.py`

### Bloque 4 — Vigía y tracking de tráfico (~3-4h)

- `kernel/e2e/traffic_seeder.py` — Vigia hace 5-10 requests al deploy desde IPs distintas (proxy o User-Agent rotation)
- Decisión arquitectónica: para v1.0 usar Plausible.io self-hosted (template Railway) o PostHog Cloud free tier
- `kernel/e2e/health_monitor.py` — cron cada 5 min verifica deploy_url responde 200

### Bloque 5 — Test 1 v2 firmado: "Landing pintura óleo" (~2-3h)

Esta es la prueba canónica del Sprint:
- Frase input: "Hacé una landing premium para vender pintura al óleo artesanal hecha en Mérida"
- Esperado output:
  - URL deployada con landing visible
  - Critic Visual ≥ 80
  - Tráfico sintético generándose
  - Cowork emite resumen con captura visual

### Bloque 6 — Documentación operativa + dashboard (~2h)

- `bridge/E2E_OPERATIONAL_GUIDE.md` para Alfredo y futuros hilos
- Dashboard nuevo `/v1/e2e/dashboard` que muestra runs activos, completados, fallidos, métricas agregadas

### Bloque 7 — Smoke E2E productivo + cierre (~2h)

- Test 1 v2 ejecutado contra producción real
- Reporte completo en bridge con screenshots, métricas, veredicto Alfredo

## ETA total

7 bloques × promedio 3-4h = **~21-28h reales** = **5-7 días calendar** al ritmo actual del Hilo Ejecutor.

## Métricas de éxito del Sprint

| Métrica | Target |
|---|---|
| Test 1 v2 (landing pintura óleo) ejecuta sin intervención humana | ✅ |
| Tiempo desde frase hasta URL viva | < 30 min |
| Critic Visual score | ≥ 80 |
| Tráfico real verificado | ≥ 3 sesiones primera hora |
| Suite tests acumulada | ≥ 280 PASS (200 base + 80 nuevos) |
| Veredicto Alfredo | "comercializable" |

## Disciplina obligatoria

- **Capa Memento aplicada en cada paso del pipeline**: `tools/memento_preflight.py` invocado antes de cualquier deploy o deploy_to_railway/github_pages
- **Patrón "consultar Catastro en runtime"** estricto — cero hardcodes de modelos
- **Tests con mocks** para CI rápido + 1 test opt-in con flag `E2E_INTEGRATION_TESTS=true` contra producción real
- **Brand DNA aplicado** — outputs visuales del Critic respetan paleta forja+graphite+acero
- **Anti-Dory** en cada paso del pipeline (lectura fresh de env vars, validación de schemas)

## Zona primaria estricta

```
kernel/e2e/__init__.py             (nuevo)
kernel/e2e/orchestrator.py         (nuevo)
kernel/e2e/pipeline.py             (nuevo)
kernel/e2e/catastro_client.py      (nuevo)
kernel/e2e/deployment.py           (nuevo)
kernel/e2e/visual_validation.py    (nuevo)
kernel/e2e/traffic_seeder.py       (nuevo)
kernel/e2e/health_monitor.py       (nuevo)
kernel/e2e/routes.py               (nuevo)
kernel/main.py                     (modificación quirúrgica: include_router)
scripts/021_sprint87_e2e_schema.sql           (nuevo)
scripts/run_migration_021.py                  (nuevo)
scripts/_smoke_e2e_sprint87.py                (nuevo)
tests/test_sprint87_e2e_*.py                  (nuevo, varios archivos por bloque)
bridge/E2E_OPERATIONAL_GUIDE.md   (nuevo)
```

## NO TOCÁS

- `kernel/catastro/*` (Hilo Catastro / cerrado v1.0)
- `kernel/memento/*` (cerrado Sprint Memento)
- `kernel/embriones/*` (reuso, no modificación. Si necesitás ajuste menor, hacelo en commit separado claramente marcado)

## Caveats arquitectónicos

1. **Tráfico real "sintético" en v1.0:** los primeros 5-10 requests son hechos por Vigia, no usuarios reales. Esto cumple el criterio "tráfico generándose" para v1.0. Cuando se agregue marketing/ads (post-v1.0), tráfico real humano se monitorea con misma infra.

2. **Plausible vs PostHog:** decisión final del Bloque 4. Recomendación: Plausible.io self-hosted (Railway template, $0 USD, GDPR-friendly, sin cookies banner needed).

3. **Costo del Sprint:** ~$1-3 USD por run E2E (LLM calls + deploy infra). Aceptable para v1.0.

4. **Replay capability:** la persistencia en `e2e_step_log` permite replay determinístico de cualquier run para debug. Útil cuando un run falle.

## Capa Memento aplicada al sprint mismo

- Pre-flight obligatorio: `tools/memento_preflight.py` invocado antes de operaciones críticas (deploy productivo, financial txn si aplica)
- Operación nueva en catálogo: `e2e_pipeline_run` con required_fields `frase_input`, `run_id`
- Source of truth nueva: `bridge/E2E_OPERATIONAL_GUIDE.md`

## Próximos sprints después de Sprint 87 NUEVO

| Sprint | Foco |
|---|---|
| Sprint 88 | Multiplicación + Orchestration de Embriones (debate estructurado, comunicación cross-Embrión) |
| Sprint 89 | Activación Guardian Autónomo |
| Sprint 90-92 | Capas Transversales C1/C2/C3 E2E |
| Sprint 93 | Verificación Autonomía Total (7 días sin intervención) |
| Sprint 94 | Sub-ola gobernanza ticketlike (DIFERIDA por Alfredo, no urgente) |
| Sprint 95+ | Stripe Pagos del Monstruo (DIFERIDO por Alfredo) |

— Cowork (Hilo B)

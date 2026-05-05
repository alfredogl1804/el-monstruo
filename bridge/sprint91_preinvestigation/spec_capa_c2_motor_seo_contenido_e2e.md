# Sprint 91 — Capa Transversal C2 (Motor de SEO + Contenido) E2E · Pre-investigación

> **Autor:** Cowork (Hilo B)
> **Fecha:** 2026-05-05
> **Estado:** Spec firmado, listo para arranque post-Sprint 90
> **Sprint asignado:** Hilo Manus Ejecutor
> **Dependencias:** Sprint 87 NUEVO E2E + Sprint 88 Embriones colectivos + Sprint 89 Guardian Autónomo + Sprint 90 Motor de Ventas
> **Cierra:** Objetivo #9 (Transversalidad Universal) Capa C2 al 70%+ y avanza Objetivo #1 (Crear Empresas) hacia 85%+ vía tráfico orgánico

---

## Contexto

Sprint 87 entrega "frase → URL viva con tráfico real". Sprint 90 entrega "lead capturado → calificado → en secuencia". Pero **el tráfico que alimenta esa captura tiene que venir de algún lado**, y depender solo de paid ads (Capa C3 Sprint 92) sería frágil económicamente.

Capa C2 es la fuente sostenible de tráfico orgánico: cada empresa generada por el pipeline E2E **se mantiene viva publicando contenido SEO-optimizado** sin intervención humana. Es el motor que sostiene el funnel que Sprint 90 monetiza.

Sprint 91 NO implementa link building cross-domain (eso es post-v1.0, requiere coordinación entre empresas-hijas). Implementa el ciclo completo: **research → ideación → drafting → optimización → publicación → tracking** dentro de cada empresa generada.

## Objetivo del Sprint

Activar el Motor de SEO + Contenido como capa transversal funcional: cualquier empresa generada por el pipeline E2E (Sprint 87) tiene un cron semanal que (1) investiga keywords vivas via web search, (2) ideea piezas de contenido alineadas con su ICP, (3) las redacta usando Embrión Creativo + Embrión Investigador en modo debate (Sprint 88), (4) las optimiza con SEO on-page rules, (5) las publica al sitio Backend Deploy (Capa 1), y (6) reporta métricas vivas al Guardian (Sprint 89).

## Decisiones arquitectónicas firmes

### Decisión 1 — Reutilizar Embriones existentes en modo colectivo

Los 9 Embriones del Sprint 88 ya incluyen:
- Embrión Investigador (research, keyword analysis, competitive scan)
- Embrión Creativo (drafting, hooks, narrativa)
- Embrión Técnico (SEO on-page rules, schema markup, meta tags)

Sprint 91 los conecta en **modo `debate`** (Sprint 88) para producción de contenido: Investigador propone keyword + ángulo, Creativo redacta, Técnico optimiza. Si discrepan en ángulo → debate convergencia. Si discrepa en optimización → Técnico tiene veto técnico.

NO crea Embriones nuevos.

### Decisión 2 — Schema Supabase para contenido y keywords

Migration `025_sprint91_motor_seo_contenido_schema.sql`:

```sql
CREATE TABLE seo_keywords_objetivo (
    id BIGSERIAL PRIMARY KEY,
    e2e_run_id TEXT REFERENCES e2e_runs(id),
    keyword TEXT NOT NULL,
    intent TEXT NOT NULL CHECK (intent IN ('informational','transactional','navigational','commercial')),
    volumen_estimado INT,                    -- via search API o heurística
    dificultad NUMERIC(3,2),                 -- 0.00 a 1.00
    prioridad TEXT CHECK (prioridad IN ('alta','media','baja')),
    discovered_at TIMESTAMPTZ DEFAULT NOW(),
    discovered_by_embrion TEXT,
    rationale TEXT
);

CREATE INDEX idx_seo_keywords_e2e ON seo_keywords_objetivo (e2e_run_id, prioridad);

CREATE TABLE seo_contenidos (
    id TEXT PRIMARY KEY,                     -- 'cont_<e2e_run_id>_<n>'
    e2e_run_id TEXT REFERENCES e2e_runs(id),
    keyword_objetivo_id BIGINT REFERENCES seo_keywords_objetivo(id),
    titulo TEXT NOT NULL,
    slug TEXT NOT NULL,
    meta_description TEXT,
    contenido_md TEXT NOT NULL,              -- markdown completo
    contenido_html TEXT,                     -- compilado al publicar
    schema_jsonld JSONB,                     -- Article schema + FAQ si aplica
    longitud_palabras INT,
    embriones_participantes TEXT[],
    debate_id TEXT REFERENCES collective_debates(id), -- vínculo a Sprint 88
    estado TEXT NOT NULL DEFAULT 'draft'
        CHECK (estado IN ('draft','review','published','retired')),
    publicado_at TIMESTAMPTZ,
    publicado_url TEXT,
    visitas_acumuladas INT DEFAULT 0,
    leads_atribuidos INT DEFAULT 0           -- conexión Sprint 90
);

CREATE TABLE seo_metrics_daily (
    fecha DATE,
    e2e_run_id TEXT,
    contenidos_publicados INT DEFAULT 0,
    keywords_ranqueando INT DEFAULT 0,       -- top 10
    visitas_organicas INT DEFAULT 0,
    leads_organicos INT DEFAULT 0,
    PRIMARY KEY (fecha, e2e_run_id)
);
```

### Decisión 3 — Patrón "consultar Catastro en runtime" se EXTIENDE de nuevo

El Motor de SEO + Contenido usa LLMs para drafting + research. **NO hardcodear modelo**. Cada call a LLM consulta el Catastro v1.x en runtime con criterios:
- Macroárea 1 (Razonamiento) score >= 70 para keyword research
- Long-context >= 32K tokens para drafting de pieza completa
- Costo por 1M output tokens dentro del top 30% Trono Score (porque el Sprint produce volumen alto)
- Idiomas soportados: español + inglés mínimo

Si el Catastro no tiene candidato con todos los criterios → fallback a templates pre-escritos por industria + Embrión Creativo solo (sin debate).

### Decisión 4 — Capa Memento aplicada en operaciones críticas

Operations registradas en catálogo:
- `seo_keyword_research_run` — antes de search API call (gasta budget externo)
- `seo_content_draft_run` — antes de invocar Embriones colectivos
- `seo_content_publish` — antes de PUBLISH al sitio (operación irreversible visible públicamente)
- `seo_metrics_daily_compute` — antes de calcular métricas de cierre
- `seo_content_retire` — antes de despublicar (operación destructiva visible)

### Decisión 5 — Cadencia editorial automática

Cada empresa generada por el pipeline tiene 3 ritmos posibles:
- **Lite** (1 pieza/semana) — default para empresas con tráfico < 100/mes
- **Estándar** (3 piezas/semana) — empresas con tráfico 100-1000/mes
- **Pro** (1 pieza/día) — empresas con tráfico > 1000/mes

El Guardian (Sprint 89) elige el ritmo según métricas observables. Cambio de ritmo requiere veto del humano (Alfredo) si pasa de Lite → Pro directo.

### Decisión 6 — Anti-spam: límite de calidad sobre cantidad

Cada pieza debe pasar 4 gates antes de PUBLISH:
1. **Longitud** — entre 800 y 3500 palabras (configurable por industria)
2. **Originalidad** — embedding similarity contra contenidos previos del mismo dominio < 0.85
3. **SEO on-page** — meta title, meta description, H1, schema, internal links presentes
4. **Coherencia con keyword objetivo** — keyword aparece en title + H1 + meta + 3-7 veces en body

Si NO pasa los 4 gates → vuelve a `draft` con razón. NO se publica jamás algo que no pase los 4.

### Decisión 7 — Publicación al sitio = call al Backend Deploy (Capa 1)

NO se construye un publisher nuevo. Se invoca `tools/deploy_to_github_pages.py` o equivalente del Backend Deploy con el contenido HTML compilado. Capa C2 produce contenido, Capa 1 lo publica. Separación de responsabilidades respetada.

## Bloques del Sprint

### Bloque 1 — Schema + endpoints REST (30-45 min)
- Migration 025 (3 tablas)
- `kernel/seo/routes.py` con `POST /v1/seo/keywords/discover`, `POST /v1/seo/content/draft`, `POST /v1/seo/content/publish`, `GET /v1/seo/metrics/daily`

### Bloque 2 — Keyword research conectado a search API (30-45 min)
- `kernel/seo/keyword_research.py` invoca search API (web_search tool ya existe) + Embrión Investigador
- Heurística de volumen + dificultad si no hay API paga
- Persistencia en `seo_keywords_objetivo`

### Bloque 3 — Drafting colectivo con Embriones (45-60 min)
- `kernel/seo/drafting.py` invoca modo `debate` del Sprint 88 con 3 Embriones (Investigador + Creativo + Técnico)
- Output estructurado: title, meta description, body markdown, schema JSON-LD
- Persistencia en `seo_contenidos` con `debate_id` apuntando a Sprint 88

### Bloque 4 — 4 gates de calidad pre-publish (30-45 min)
- `kernel/seo/quality_gates.py` con 4 funciones: longitud, originalidad (embedding), on-page SEO, coherencia keyword
- Bloqueo duro si no pasa los 4
- Razón de fallo persistida en log para reintento

### Bloque 5 — Publishing al Backend Deploy (30 min)
- `kernel/seo/publisher.py` compila markdown → HTML + invoca `tools/deploy_*` de Capa 1
- Update de `seo_contenidos.estado = 'published'` + `publicado_url`
- Sitemap.xml regenerado automáticamente

### Bloque 6 — Cron editorial + métricas + integración Guardian (30-45 min)
- Cron 1h: detecta empresas con cadencia editorial vencida y dispara research → draft → quality gate → publish
- Métricas diarias `seo_metrics_daily`
- Guardian Sprint 89 lee esta tabla para Objetivo #1 + Objetivo #9 (Transversalidad)

### Bloque 7 — Capa Memento + tests + smoke (30-45 min)
- 5 operations registradas
- Test de cada gate con casos sintéticos (1 que pasa, 1 que falla por gate)
- Smoke contra producción real con 1 keyword discovery + 1 draft + 1 publish a sitio test

## ETA total recalibrada

7 bloques × ~35 min promedio = **3-5 horas reales** al ritmo demostrado del Hilo Ejecutor.

(ETA magna previa pre-recalibración: 1-2 semanas. Recalibración 5-10x aplicada.)

## Métricas de éxito

| Métrica | Target |
|---|---|
| 1 keyword discovered + 1 contenido draft + 1 contenido publicado E2E | ✅ |
| Tests acumulados | ≥ 510 PASS |
| Suite Sprint 86 + 87 + 88 + 89 + 90 + 91 | regresión cero |
| Latencia keyword research → draft completo | < 5min P95 |
| Guardian Sprint 89 lee métricas SEO | ✅ |
| Sin LLM hardcoded — todo desde Catastro | ✅ |
| 4 gates de calidad bloquean al menos 1 caso de mala calidad en tests | ✅ |

## Disciplina obligatoria

- Capa Memento aplicada en 5 operations críticas (incluyendo PUBLISH y RETIRE como irreversibles)
- Brand DNA aplicado en plantillas y CTA del contenido (forja + graphite + acero, tono Alfredo adaptado a la voz de cada empresa-hija)
- Anti-Dory: lectura fresh de keywords ranking + competitive scan antes de cada draft
- Standby duro 7 días: ANULADO por política Cowork (Apéndice 1.2)
- LLM-as-parser con Structured Outputs Pydantic (semilla 39) para parsear output de Embriones Creativo/Técnico
- 16to tag `coding-overfit-suspected` del Sprint 86.6 NO aplica acá pero reaprovechamos el patrón para `seo-overoptimization-suspected` futuro

## Zona primaria

```
kernel/seo/* (nuevo módulo completo)
kernel/seo/routes.py
kernel/seo/keyword_research.py
kernel/seo/drafting.py
kernel/seo/quality_gates.py
kernel/seo/publisher.py
kernel/seo/cron.py
kernel/e2e/orchestrator.py (modificación quirúrgica del paso post-deploy)
scripts/025_sprint91_motor_seo_contenido_schema.sql
scripts/run_migration_025.py
scripts/_smoke_sprint91_motor_seo.py
tests/test_sprint91_motor_seo_*.py
bridge/MOTOR_SEO_OPERATIONAL_GUIDE.md
```

## NO TOCÁS

- `kernel/catastro/*` (zona Catastro, solo lectura desde Motor de SEO)
- `kernel/memento/*` (zona cerrada)
- `kernel/embriones/*` (zona Sprint 88, solo se invocan en modo debate, no se modifican)
- `kernel/guardian/*` (zona Sprint 89, solo se EXTIENDE en métrica Obj #1 + Obj #9)
- `kernel/ventas/*` (zona Sprint 90, solo se LEE para atribuir leads orgánicos)
- `kernel/e2e/pipeline.py` salvo donde el orchestrator lo invoca
- `tools/deploy_*` (Capa 1 ya cerrada, solo se invoca)

## Conexiones cross-sprint

| Sprint | Cómo se conecta |
|---|---|
| Sprint 87 NUEVO (E2E) | El orchestrator invoca seo_setup como paso post-deploy de cada empresa generada |
| Sprint 88 (Embriones colectivos) | drafting usa modo `debate` con 3 Embriones |
| Sprint 89 (Guardian Autónomo) | Guardian lee `seo_metrics_daily` para scoring Obj #1 y Obj #9 |
| Sprint 90 (Motor de Ventas) | `seo_contenidos.leads_atribuidos` se actualiza desde `ventas_leads.fuente_captura='content_organic'` |

## Próximo sprint después

Sprint 92 — Capa Transversal C3 (Motor de Ads + Performance Marketing) E2E.

— Cowork (Hilo B)

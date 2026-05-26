<!-- lint_strict -->
# Sprint CAPA-SEO-001 — SEO y Descubrimiento Universal

**Estado:** Propuesto — Canonizado sin ejecutar
**Hilo:** TBD
**ETA:** estimación pendiente
**Objetivo Maestro:** #9 (Transversalidad Universal — Capa 2) + #1 (Crear Empresas Digitales Completas)
**Capa Transversal:** C2 SEO y Descubrimiento
**Bloqueos:** ninguno técnico
**Resultado esperado:** Cada sitio creado por El Monstruo nace con arquitectura SEO técnicamente perfecta y estrategia de contenido al día.

---

## 0. Procedencia

OM-09 v3.0 línea 438-443:

> **CAPA 2 — SEO y Descubrimiento:**
> - Arquitectura SEO desde el diseño
> - Keyword research en tiempo real (magna — siempre actualizado)
> - Content strategy automatizada
> - Technical SEO perfecto
> - Local SEO si aplica

Auditoría 2026-05-26: 0 sprints en backlog cubren C2.

---

## 1. Audit pre-sprint

Lo que existe:
- Algunos sitios ad-hoc tienen meta tags manuales
- Sin pipeline canónico de SEO

Lo que falta:
- Capability `invoke_seo_audit(site_url)` que retorna score técnico
- Generador de sitemap, robots.txt, structured data automático
- Keyword research con datos frescos (no entrenamiento) vía Perplexity Sonar o Ahrefs API
- Content calendar generado por enjambre de modelos
- Local SEO con Google My Business API si el negocio es local

---

## 2. Tareas (MVP)

### MVP-1: Audit técnico
- Endpoint `POST /v1/seo/audit` que corre Lighthouse + custom checks
- Output: score 0-100, issues priorizados, fix recommendations

### MVP-2: Generación automática de meta y schema
- Hook en cada sitio creado: genera title, description, og:tags, schema.org JSON-LD
- Reglas canónicas en `kernel/seo/templates/`

### MVP-3: Keyword research magna
- Integración con Perplexity Sonar Reasoning Pro (ya en stack) para queries de búsqueda
- Cache en `seo_keywords` con TTL 7 días
- Score de oportunidad: volumen × dificultad × intent match

### MVP-4: Content strategy automatizada
- Generador de calendario editorial (12 piezas/mes default)
- Cada pieza: tema, keyword target, longitud, tono (heredado del brand DNA)
- Hook a la capa de copywriting (CAPA_VENTAS_001 si está activa)

### MVP-5: Technical SEO continuo
- Job mensual: scan de cada empresa hija, alerta si score < 85
- Auto-fix de issues triviales (broken links, missing alt, image weight)

### MVP-6: Local SEO condicional
- Si el negocio tiene dirección física, integra Google My Business
- Schema LocalBusiness automático
- Reviews monitoring

---

## 3. Dependencias

- Stack debe incluir Perplexity Sonar (ya está) o equivalente con datos frescos
- `STACK_REFRESH_001` asegura herramientas SEO al día (Lighthouse, Ahrefs, etc.)
- `CAPA_VENTAS_001` para coordinar copywriting

---

## 4. Criterios de Cierre y Métricas de Éxito

- Cada sitio nace con score Lighthouse SEO ≥ 95
- Ranking promedio de keyword target en top 20 a 90 días
- Tráfico orgánico ≥ 30% del total a 6 meses

---

## 5. Anti-doctrina

- NO usar entrenamiento del LLM para keyword research (datos viejos)
- NO automatizar contenido sin review humano en tier premium
- NO comprar backlinks ni hacer black-hat SEO
- NO acoplar a Google exclusivamente (también Bing, DuckDuckGo, perplexity-as-search)

---

## 6. Notas de canonización

Sprint canonizado sin ejecutar. Status en Tablero: `backlog_canonizado` con `paradigm: capa_transversal_comercial`. Auto-promote a `EJECUCION` al detectar commits en `kernel/seo/`.

Firmado: **Manus B — 2026-05-26**

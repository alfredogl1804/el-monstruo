# [Hilo Manus Catastro] · Tarea P1: Pre-investigación profunda Sprint 85
**Fecha:** 2026-05-04
**Objetivo:** Mapear el reuso del kernel actual para el Sprint 85 y definir la arquitectura de los 2 Embriones nuevos (Product Architect y Critic Visual).

## 1. Reuso del Kernel Actual (Qué reciclamos)

El Sprint 85 se apoya fuertemente en la infraestructura construida en Sprints anteriores (82-84):

*   **Brand Engine (Sprint 82):** El `Product Architect` consumirá los lineamientos de marca. La nueva carpeta `kernel/brand/verticals/` (con los 6 YAMLs curados) se integra directamente aquí, extendiendo la capacidad del motor de marca para prepopular `client_brand` en el brief.
*   **Vanguard Scanner & Error Memory (Sprint 83 / Cimientos):** Críticos para el `Executor`. El `Critic Visual` alimentará la Error Memory si un deploy falla (score < 80 repetidamente), permitiendo al sistema aprender de los fallos de generación visual/estructural.
*   **Deployments (Sprint 84):** La lógica de deploy a Github Pages y Railway (`deploy_to_github_pages`, `deploy_to_railway`) ya existe. El Sprint 85 la envuelve con el quality gate del `Critic Visual`.
*   **Magna Classifier:** Útil para el `Product Architect` al detectar el vertical del prompt inicial del usuario.

## 2. Qué se construye nuevo (Arquitectura de Embriones)

### 2.1. Product Architect (Embrión 1)
**Ubicación:** `kernel/embriones/product_architect.py`
**Responsabilidad:** Traducir un prompt corto en un `brief.json` estructurado y ejecutable.
**I/O Contract:**
*   **Input:** Prompt del usuario (ej. "quiero una landing para mi curso de pintura al óleo").
*   **Proceso:**
    1.  Clasifica el vertical (usa Magna Classifier o lógica interna) -> `education_arts`.
    2.  Lee `kernel/brand/verticals/education_arts.yaml`.
    3.  Prepopula `client_brand` y `structure.sections_required`.
    4.  Identifica `data_missing` (ej. nombre del instructor, precio).
*   **Output:** `brief.json` (ver schema en SPEC) o **UNA** pregunta consolidada al usuario si faltan datos críticos.

### 2.2. Critic Visual (Embrión 2)
**Ubicación:** `kernel/embriones/critic_visual.py`
**Responsabilidad:** Evaluar el output renderizado contra el `brief.json` y una rúbrica estricta. Es el Quality Gate antes del deploy final.
**I/O Contract:**
*   **Input:** URL del deploy (staging/temporal) + `brief.json`.
*   **Proceso:**
    1.  Toma screenshot headless (Playwright/Browserless).
    2.  Evalúa 8 componentes ponderados (Estructura 20, Contenido 25, Visual 15, Brand fit 15, Mobile 10, Performance 5, CTA 5, Meta tags 5).
*   **Output:** `{"score": int, "findings": list, "passed": bool}`. Si `passed` es false (score < 80), devuelve feedback al Executor. Máximo 3 iteraciones.

## 3. Schema SQL (Preview)

Se creará el archivo de migración `scripts/015_sprint85_briefs_deployments.sql` con las tablas `briefs` y `deployments` detalladas en el SPEC.

**Puntos clave del Schema:**
*   `deployments` tiene FK `brief_id` referenciando a `briefs`.
*   `deployments.critic_score` y `deployments.quality_passed` son los campos de control del Critic Visual.
*   El endpoint `GET /v1/deployments` será crucial para la observabilidad y para el futuro Catastro (Sprint 86/87).

## 4. Dependencias Externas (Ola 3/5/6)
*   **Media Gen:** `tools/generate_hero_image.py` requiere `REPLICATE_API_TOKEN` (Flux 1.1 Pro). Esto valida la necesidad del inventario de credenciales (Ola 3) y la rotación/provisioning (Ola 5/6).
*   **Headless Browser:** El Critic Visual requiere infraestructura para tomar screenshots. Se debe evaluar si usar un servicio externo (Browserless) o levantar Playwright en el container.

**Conclusión:** El Sprint 85 transforma al Monstruo de un "deployer" a un "creador con criterio". La arquitectura está clara y el reuso del kernel maximiza la eficiencia. Listo para ejecutar cuando llegue el trigger (Ola 5 cerrada).

# Sprint 87.2 — Deploy Real + Critic Visual con Gemini Vision puente + Traffic Real · Pre-investigación

> **Autor:** Cowork (Hilo B)
> **Fecha:** 2026-05-05
> **Estado:** Spec firmado, listo para arranque inmediato post-audit Sprint 87.1
> **Sprint asignado:** Hilo Manus Memento (Ejecutor)
> **Dependencias:** Sprint 87 NUEVO + 87.1 cerrados; pipeline produciendo contenido real
> **Cierra:** las 3 deudas restantes del Sprint 87 NUEVO; declara **v1.0 funcional**

---

## Contexto

Sprint 87 NUEVO cerró v1.0 estructural. Sprint 87.1 cerró 2 de 5 deudas (Embriones reales + Steps LLM reales) — el contenido producido por el pipeline ya es genuino. Quedan 3 deudas que separan el v1.0 estructural del **v1.0 funcional declarable**:

3. **DEPLOY mock → real:** las landings producidas hoy quedan en mock, no se publican a URL viva con dominio público.
4. **Critic Visual stub conservador 60 → real:** falta evaluación visual genuina del output deployado.
5. **Traffic stub → real:** no se mide tráfico real sobre la URL viva.

Sprint 87.2 cierra las 3 simultáneamente. Cuando termine, una frase de Alfredo va a producir URL viva real, con score Critic Visual ≥ 80 evaluado genuinamente, con tráfico real medible. Eso es **v1.0 funcional declarable**.

## Objetivo del Sprint

Cuando Sprint 87.2 cierre verde, vos podés escribir una frase y recibir **URL pública navegable**, ver el screenshot evaluado por Gemini Vision con análisis estructurado, y monitorear el tráfico real que la página recibe en las primeras horas. El smoke productivo demuestra el flujo completo end-to-end.

## Decisiones arquitectónicas firmes

### Decisión 1 — Deploy real reutiliza Capa 1 Manos existente

El backend ya tiene `tools/deploy_to_railway` y `tools/deploy_to_github_pages` operativos (Capa 1 Manos cerrada en Sprint 84.6+). Sprint 87.2 NO construye nuevo deploy infrastructure — invoca los existentes.

Estrategia: **deploy a GitHub Pages como default v1.0** (gratis, dominio `.github.io` o custom domain del usuario, latencia baja, soporta sites estáticos generados por el pipeline). Railway queda como fallback para sitios con backend dinámico.

El Catastro mantiene un atributo nuevo `deploy_target` por tipo de sitio (estático vs dinámico). El pipeline elige en runtime según output del step CREATIVO + step TECNICO.

### Decisión 2 — Critic Visual con Gemini Vision como puente transitorio

Sovereign_browser (Capa 1 Manos magna) NO se construye en Sprint 87.2. Es deuda post-v1.0. Mientras llega, **Gemini Vision sobre screenshot capturado** es proxy razonable.

Flujo:
1. Pipeline invoca screenshot capture sobre la URL deployada
2. Screenshot se manda a Gemini Vision API (vía Catastro runtime)
3. Gemini Vision evalúa con prompt estructurado: alineación al brief, calidad estética, claridad del CTA, jerarquía visual, profesionalismo percibido
4. Output Pydantic con score 0-100 + razones explícitas

Cuando sovereign_browser llegue (Sprint magna post-v1.0), reemplaza Gemini Vision sin cambiar la interfaz del pipeline.

### Decisión 3 — Screenshot capture con Playwright headless

Playwright Python o Puppeteer Node como puente. Toma screenshot full-page de la URL deployada, persiste en storage del kernel, retorna path para que Gemini Vision lo procese.

NO usa servicios externos pagados (urlbox.io, screenshotapi.net) — privacy-first y soberanía.

### Decisión 4 — Traffic real con instrumentación liviana

Cada landing generada incluye un script propio del Monstruo (no Google Analytics, no Plausible externo) que envía pings a `kernel/v1/traffic/ingest`. El kernel agrega métricas básicas:
- Pageviews
- Sesiones únicas (cookie soberana)
- Origen de tráfico (referrer)
- Dispositivo (mobile/desktop)
- Tiempo en página

Privacy-first: cero tracking cross-site, cero cookies third-party, cero envío de datos a servicios externos. El usuario final ve un footer pequeño *"site soberano del Monstruo"* enlazado a explicación de tracking.

Tabla nueva `e2e_traffic` para persistir.

### Decisión 5 — Critic Visual score ≥ 80 como threshold de "comercializable"

El score de Gemini Vision es 0-100. Threshold de comercializable se sube de 60 (stub conservador) a **80 (real)**. Si el score < 80, veredicto `awaiting_judgment` con razones específicas devueltas por Gemini Vision para iteración manual o retry automático.

### Decisión 6 — Capa Memento aplicada en operaciones críticas

Operations registradas:
- `e2e_deploy_real` (irreversible — URL pública con contenido del usuario)
- `e2e_screenshot_capture` (acceso a navegación headless)
- `e2e_critic_visual_evaluate` (call LLM Vision con datos potencialmente sensibles)
- `e2e_traffic_ingest` (recepción de datos de visitantes)

Preflight valida que el sitio a deployar no contenga PII inadvertida del input + valida que el screenshot no exponga datos privados antes de mandarlo a Gemini Vision.

### Decisión 7 — Brand DNA en errores

Formato `e2e_deploy_*_failed`, `e2e_screenshot_*_failed`, `critic_visual_evaluate_*_failed`, `traffic_ingest_*_failed`.

## Bloques del Sprint

### Bloque 1 — Deploy real con Capa 1 Manos (45-60 min)
- `kernel/e2e/deploy/real_deploy.py` invoca `tools/deploy_to_github_pages` (default) o `tools/deploy_to_railway` (fallback dinámico)
- Determina target en runtime según output del pipeline (estático vs dinámico)
- Persiste `deploy_url`, `deploy_provider`, `deploy_at` en `e2e_runs`
- Quita etiqueta `real_deploy_pending=true` del código

### Bloque 2 — Screenshot capture con Playwright (30-45 min)
- `kernel/e2e/screenshot/capture.py` usando Playwright headless
- Captura full-page screenshot de URL deployada
- Persiste en storage del kernel con path indexado
- Maneja timeout (max 30s por screenshot) y retry policy

### Bloque 3 — Critic Visual real con Gemini Vision (45-60 min)
- `kernel/e2e/critic_visual/gemini_vision.py`
- Catastro elige Gemini Vision en runtime (modelo con `confidentiality_tier=cloud_anonymized_ok`)
- Prompt estructurado para evaluar landing
- Output Pydantic: `CriticVisualReport` con score, razones, sub-scores (estética, CTA, jerarquía, profesionalismo)
- Persiste en `e2e_step_log` con score real, NO stub 60
- Threshold de comercializable: 80

### Bloque 4 — Traffic instrumentation soberano (45-60 min)
- Migration 028: tabla `e2e_traffic` con pageviews, sessions, etc.
- Endpoint `POST /v1/traffic/ingest` que recibe pings de las landings
- Script `monstruo-tracking.js` (~200 LOC) que se inyecta en cada landing deployada
- Privacy: cookie soberana de primera parte, sin tracking cross-site
- Footer mínimo en cada landing con link a explicación

### Bloque 5 — Pipeline integration end-to-end (30 min)
- `kernel/e2e/pipeline.py` modificado para invocar deploy real + screenshot + critic visual real + traffic instrumentation en steps 9-12
- Veredicto final usa score Critic Visual real (no judgment stub)
- Quita las 3 etiquetas restantes del Sprint 87 NUEVO en código

### Bloque 6 — Tests + smoke productivo magna (45-60 min)
- Tests unitarios cada componente con mocks
- Smoke productivo con **frase canónica de Alfredo**: produce URL viva real navegable, screenshot capturado, score Critic Visual real ≥ 80, instrumentación traffic activa
- Verificación manual disponible: Alfredo abre la URL en su browser real

### Bloque 7 — Bridge + reporte cierre + declaración v1.0 funcional (20-30 min)
- `bridge/SPRINT_87_2_OPERATIONAL_GUIDE.md`
- `bridge/manus_to_cowork.md` con file_append (NO heredoc) — incluye URL del smoke productivo, screenshot, score, métricas iniciales
- **Declaración formal: v1.0 funcional alcanzado**

## ETA total recalibrada

7 bloques × ~45 min promedio = **3-5 horas reales** según Apéndice 1.3.

## Métricas de éxito

| Métrica | Target |
|---|---|
| Frase canónica → URL pública navegable | ✅ |
| Screenshot capture funciona reliably | ✅ |
| Score Critic Visual real (Gemini Vision) ≥ 80 sobre output decente | ✅ |
| Instrumentación traffic recibe pings | ✅ |
| Tests acumulados | ≥ 250 PASS |
| Suite completa | regresión cero |
| 5 deudas Sprint 87 NUEVO totalmente cerradas | ✅ las 5 |
| **v1.0 funcional declarable** | ✅ |

## Disciplina obligatoria

- Capa Memento en deploy (irreversible) + screenshot + critic visual + traffic
- Brand DNA en errores: `e2e_deploy_*_failed`, `critic_visual_evaluate_*_failed`, etc.
- Anti-Dory: stash → pull rebase → pop antes de cada commit
- NO heredoc al bridge (semilla 40)
- LLM-as-parser con Pydantic Structured Outputs (semilla 39)
- Privacy-first en traffic (cero tracking externo)
- Standby duro ANULADO por política Cowork

## Zona primaria

```
kernel/e2e/deploy/real_deploy.py (NUEVO)
kernel/e2e/screenshot/capture.py (NUEVO)
kernel/e2e/critic_visual/gemini_vision.py (NUEVO)
kernel/e2e/traffic/ingest.py (NUEVO)
kernel/e2e/traffic/routes.py (NUEVO)
kernel/e2e/pipeline.py (modificación quirúrgica steps 9-12)
scripts/028_sprint87_2_traffic_schema.sql (NUEVO)
scripts/run_migration_028.py (NUEVO)
scripts/_smoke_sprint87_2_real_deploy.py (NUEVO)
tests/test_sprint87_2_*.py (NUEVOS)
static/monstruo-tracking.js (NUEVO, ~200 LOC)
bridge/SPRINT_87_2_OPERATIONAL_GUIDE.md (NUEVO)
```

## NO TOCÁS

- `kernel/catastro/*` (Catastro corriendo barrido de plataformas en paralelo)
- `kernel/embriones/*` (Sprint 87.1 cerrado, intocable)
- `kernel/memento/*` (zona cerrada)
- `apps/mobile/*` (zona Mobile)
- `tools/deploy_*` (existentes — solo se invocan, no se modifican)
- `kernel/main.py` salvo donde router de traffic se monta (8-10 líneas quirúrgicas máximo)

## Después de Sprint 87.2

**v1.0 funcional declarable.** A partir de ese punto, las 6 deudas que quedan en backlog post-v1.0 son:
- Sovereign_browser (reemplaza Gemini Vision puente)
- Bloques 3-5 del Sprint 86.4.5 (refinamientos Catastro)
- Sprint 86.9 Macroárea 5 Embeddings (si aplica)
- Capabilities mobile (Sprint Mobile 0+)
- Capa 9 transversal cuando se firme con CIES + OMNICOM
- Empresas-hijas escalando con Capas C1-C6 progresivas

— Cowork (Hilo B)

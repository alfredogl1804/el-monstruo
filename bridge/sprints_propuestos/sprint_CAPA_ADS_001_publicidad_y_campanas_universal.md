<!-- lint_strict -->
# Sprint CAPA-ADS-001 — Publicidad y Campañas Universal

**Estado:** Propuesto — Canonizado sin ejecutar
**Hilo:** TBD
**ETA:** estimación pendiente
**Objetivo Maestro:** #9 (Transversalidad Universal — Capa 3) + #1 (Crear Empresas Digitales Completas)
**Capa Transversal:** C3 Publicidad y Campañas
**Bloqueos:** ninguno técnico
**Resultado esperado:** Cada empresa hija ejecuta campañas pagadas en los canales relevantes con creativos generados, targeting óptimo y budget allocation perpetuo.

---

## 0. Procedencia

OM-09 v3.0 línea 445-450:

> **CAPA 3 — Publicidad y Campañas:**
> - Creación automática de campañas (Google Ads, Meta Ads, TikTok Ads)
> - Creativos generados (imágenes, copy, video)
> - Targeting inteligente
> - Budget allocation óptimo
> - Retargeting automático

Auditoría 2026-05-26: 0 sprints en backlog cubren C3.

---

## 1. Audit pre-sprint

Lo que existe:
- HeyGen API key configurada (videos con avatares)
- ElevenLabs API key (audio para spots)
- Imagen generation vía `kernel/_core/imageGeneration.ts` en webdev template

Lo que falta:
- Conexión a Google Ads API, Meta Marketing API, TikTok Ads API
- Capability `invoke_ad_campaign(project_id, channel, budget, objective)`
- Pipeline de creativos: brief → imagen + copy + video
- Budget optimizer multi-canal con bandit algorithm

---

## 2. Tareas (MVP)

### MVP-1: Conectores a plataformas
- `kernel/ads/connectors/` con cliente Google Ads, Meta, TikTok
- Auth OAuth almacenado por proyecto en Vault (depende de MOBILE_0_SMP)
- Endpoint `GET /v1/ads/accounts/{project_id}` lista cuentas conectadas

### MVP-2: Pipeline de creativos
- Endpoint `POST /v1/ads/creatives/generate` con `brief`, `format`, `channels`
- Output: 3 variantes por formato (imagen, video, copy)
- Imágenes: vía `imageGeneration` con prompts heredados del brand DNA
- Videos: vía HeyGen para spots con avatar
- Copy: vía LLM con prompts canónicos en `kernel/ads/prompts/`

### MVP-3: Targeting inteligente
- Capability `propose_targeting(project_id, audience_seed)` que retorna 3 audiencias
- Lookalike audiences automáticas en cada plataforma
- Exclusions automáticas (no targeting a clientes existentes)

### MVP-4: Budget allocation con bandit
- Algoritmo Thompson Sampling sobre canales
- Reallocación cada 24h basada en ROAS
- Cap por canal configurable
- Stop-loss si CPA > umbral

### MVP-5: Retargeting automático
- Pixel/SDK injection en cada empresa hija
- Audiences automáticas por step del funnel
- Campañas retargeting con cap de frecuencia

### MVP-6: Reporting unificado
- Dashboard `monstruo/dashboards/ads/` con métricas multi-canal
- Alertas: CPA > 1.5x baseline, ROAS < 1.0, reach < expected

---

## 3. Dependencias

- `MOBILE_0_SMP` para guardar credenciales de plataformas en Vault
- `CAPA_VENTAS_001` para calcular LTV y permitir budget calc
- HeyGen + ElevenLabs ya en stack
- `STACK_REFRESH_001` para validar que las APIs de plataformas no rotaron

---

## 4. Criterios de Cierre y Métricas de Éxito

- Tiempo de setup de campaña: ≤ 30 minutos desde brief
- ROAS promedio ≥ 2.5x a los 90 días
- CPA dentro de 80% del baseline en cada canal
- Ad fatigue detectada y rotada en ≤ 7 días

---

## 5. Anti-doctrina

- NO publicar creativos sin review humano en tier premium
- NO usar PII de usuarios para lookalikes sin consent explícito (GDPR/LGPD compliance)
- NO sobreoptimizar a corto plazo (penaliza brand a largo plazo)
- NO meter más de 3 plataformas activas si el budget no las soporta (cada una < $500/mes es ruido)

---

## 6. Notas de canonización

Sprint canonizado sin ejecutar. Auto-promote al detectar commits en `kernel/ads/`.

Firmado: **Manus B — 2026-05-26**

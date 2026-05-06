# Sprint Mobile 4 — Modo Cockpit fase 2

**Owner:** Hilo Ejecutor (Manus) Mobile
**Zona protegida:** `apps/mobile/lib/modes/cockpit/`
**ETA estimada:** 4-7h reales con Apéndice 1.3 factor velocity
**Bloqueos:** Sprint Mobile 3 cerrado verde
**Prerequisito:** Cockpit fase 1 con MOC + Threads + Catastro + Embriones + Guardian funcionales

---

## 1. Contexto

Mobile 3 entregó las 5 superficies de operations center del Cockpit. Mobile 4 agrega las 5 superficies de **monitoreo profundo + portfolio + financial**:

1. **Memento** (semillas error_memory + pre-flights + Síndrome Dory evitado)
2. **Portfolio Empresas-Hijas** (las 20 empresas-hijas con CIP como anchor)
3. **FinOps** (capacity awareness completa — tokens, costos, ROI por empresa-hija)
4. **Pipeline E2E** (visualización del flow del Sprint 87 NUEVO con Tier indicators)
5. **Replay (Timelapse)** (selector de runs E2E + timeline scrubable estilo Devin)

---

## 2. Objetivo único del sprint

Implementar 5 superficies más del Cockpit con stubs realistas + integración inicial con datos del kernel post-Sprint 89 (Catastros 0) cuando converja.

Cuando este sprint cierra: Alfredo desde el Cockpit puede ver toda su operación financiera + portfolio de 20 proyectos + replay de runs pasadas + estado profundo de Memento.

---

## 3. Bloques del sprint

### 3.A — Memento

`MementoScreen`:
- Lista de 40+ semillas error_memory con search + filter por proyecto
- Pre-flights ejecutados últimas 24h con success/fail
- Detector de contexto contaminado (heurísticas magna que reconocen patrones tipo "Falso Positivo TiDB")
- Stats del Síndrome Dory evitado (cuántas veces el sistema previno re-equivocaciones)
- Audit del SMP (estado de claves, último rotation, recovery shards distribuidos)
- Configuración de tiers de sensibilidad por tipo de operación

Stub: data hardcoded con las 40+ semillas reales del repo + pre-flights ficticios pero plausibles.

### 3.B — Portfolio Empresas-Hijas

**3.B.1 — Tarjetas de las 20 empresas-hijas**

`PortfolioScreen`:
- Grid de 20 cards (5×4), una por proyecto del Inventario v3
- Cada card con:
  - Nombre + estado (🟢 Activo / 🟡 Construcción / 🟠 Diseño / 🔵 Nominal)
  - Métricas vivas según estado:
    - Activo: tráfico web + ingresos + leads
    - Construcción: sprint actual + % completion
    - Diseño: decisiones pendientes + DSCs bloqueantes
    - Nominal: counts de archivos + última actividad
  - Logo o color del proyecto (per brand DNA)

**3.B.2 — Vista detalle de empresa-hija**

Tap en card → `EmpresaHijaDetailScreen`:
- Para CIP: estado de las 8 decisiones, blockers DSC-CIP-PEND-001 + 002, link al skill `creacion-cip`, mapa de eje de convergencia con Marketplace + Roche Bobois (DSC-X-006)
- Para LikeTickets: ticketlike.mx live URL, butacas vendidas, ingresos del mes
- Para Mena Baduy: dashboards políticos, OSINT recent
- Etc per proyecto

**3.B.3 — Stakeholder Lens (post-Sprint 89)**

Cuando Sprint 89 cierre, las cards muestran sub-tabs por lente:
- "Ver desde Owner" (default — Alfredo)
- "Ver desde Inversor" (futuro CIP)
- "Ver desde Cliente"
- "Ver desde Partner"

Stub en Mobile 4: solo "Owner" funcional. Otras lentes son placeholders.

### 3.C — FinOps

`FinOpsScreen`:
- KPIs principales: tokens consumidos hoy / 7d / 30d, costo total, tasa de quema
- Desglose por proveedor (pie chart con brand DNA): Anthropic / OpenAI / Google / xAI / Manus / Perplexity / ElevenLabs / Replicate
- Desglose por hilo (Catastro / Ejecutor / Memento / Sprints especiales)
- ROI por empresa-hija (ingresos vs costos de generación + mantenimiento)
- Forecast de gasto al ritmo actual (próximos 30 / 90 días)
- Spending caps configurables con alertas (stub: setting modal)
- Audit de uso por modelo del Catastro

Stub: data financiera plausible basada en órdenes de magnitud reales del kernel actual.

### 3.D — Pipeline E2E

**3.D.1 — Visualización del flow de 12 pasos**

`PipelineE2EScreen`:
- Diagrama lineal de los 12 pasos del Sprint 87 NUEVO (intake → ICP → naming → branding → copy → wireframe → componentes → assembly → deploy → critic visual → registro → veredicto)
- Estado per-step: pending / running / completed / failed
- Tap en step → detalle: input recibido, modelo del Catastro elegido, tokens consumidos, output

**3.D.2 — Tier indicators (post-v1.2)**

Tres tiers visibles en top:
- **Tier Simple** (12 pasos) — landing pages, MVPs
- **Tier Marketplace** (+6 pasos: matching engine bilateral, reputation, trust layer)
- **Tier Regulated Financial** (+12 pasos: legal review, compliance, smart contract audit, oracles, KYC, fiduciary structure)

Cuando un run usa Tier Marketplace o Regulated Financial, los pasos extra aparecen.

**3.D.3 — Intervención humana en cualquier paso**

Botones [Pausar] [Editar input del próximo step] [Abort] [Replay desde aquí] visibles en cada step running.

### 3.E — Replay (Timelapse)

**3.E.1 — Selector de runs E2E pasadas**

`ReplayScreen`:
- Lista de runs anteriores con timestamp + frase canónica + tier + status final + critic score
- Filtros: por empresa-hija, por tier, por verdict (comercializable / descartar / iterar)

**3.E.2 — Timeline scrubable interactivo (estilo Devin Timelapse)**

Tap en run → `TimelapseScreen`:
- Timeline horizontal con marcadores en cada step
- Scrub bar para moverte por la run en el tiempo
- En cada punto: thumbnail del estado del HTML/output + transcript de pensamiento del Embrión activo + decisiones del Catastro
- Botón [Bifurcar desde aquí] que clona el state y arranca un nuevo run (stub en Mobile 4; funcional post-Sprint Kernel 0)

Stub: 5 runs pre-grabadas con timeline data plausible.

### 3.F — Smoke productivo + validación

Builds limpios. Alfredo navega las 5 superficies, abre detalle de CIP, ve FinOps con números mock, replay de un run pasado, valida que la densidad + estética siguen siendo Bloomberg + Apple. Si SÍ: Sprint Mobile 4 cerrado verde.

---

## 4. Magnitudes esperadas

- ~2,200 LOC nuevas
- ~30 archivos nuevos
- ~25 widget tests + golden files
- 1 validación humana

---

## 5. Disciplina aplicada

- ✅ DSC-G-004: brand DNA en superficies financieras (no se ve como Datadog/Grafana)
- ✅ DSC-X-006: Portfolio refleja Mapa de Ejes de Convergencia (CIP × Marketplace × Interiorismo × Roche Bobois)
- ✅ Capa Memento aplicada visiblemente: badges ✓/⚠/✗ en cada métrica
- ✅ Brand DNA error naming Dart: `finOpsLoadCostsFailed`, `pipelineE2EFetchRunFailed`, etc.

---

## 6. Cierre formal

> 🏛️ **Modo Cockpit fase 2 — DECLARADO** (10 superficies funcionales en total: fase 1 + fase 2)

---

## 7. Lo que NO entra

- Computer Use, Coding embedded, Hilos Manus visualization, Bridge, Settings (Sprint Mobile 5)
- Datos reales (esperan SMP)
- Stakeholder Lens completo (espera Sprint 89 cierre)

---

— Cowork (Hilo A), spec preparada 2026-05-06.
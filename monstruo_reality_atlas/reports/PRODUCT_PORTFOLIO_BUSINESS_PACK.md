# PRODUCT_PORTFOLIO_BUSINESS_PACK

**Versión:** 1.0
**Fecha:** 2026-05-18
**Branch:** monstruo-reality-atlas-001
**Propósito:** Inventariar las empresas-hijas, productos y proyectos del Monstruo con su estado real (código, doctrina, deploy) para que ChatGPT entienda qué se vende, qué se construye y qué es aspiracional.

---

## 1. Resumen Ejecutivo

El Monstruo administra un **portfolio canónico de 20 proyectos** distribuidos en 4 estados (referencia: `docs/INVENTARIO_PROYECTOS_v3_COMPLETO.md`). La dialéctica firmada (DSC-X-006 Patrón Convergencia Diferida): **el Monstruo es invisible, las empresas-hijas son universales**. Alfredo no vende tecnología — vende productos finales en mercados específicos. La constelación NO es monolito multi-producto sino empresas autónomas que comparten infra crítica desde día 1 y convergen cuando cada una prueba PMF independiente. CIP es declarado "primera empresa-hija magna que el Monstruo va a fabricar end-to-end" — pero está **100% en diseño/legal, sin código, sin repo**. LikeTickets / `ticketlike.mx` es activo en producción (skill dedicado `ticketlike-ops` confirma operación). El Monstruo Bot Telegram es activo. Command Center declarado activo en doctrina pero `find . -type d -name "command*"` → 0 hits en repo el-monstruo (ver Pack 1 §2). Esto sugiere que Command Center vive en otro repo o es nominal.

## 2. Portfolio Canónico — 20 Proyectos (APP_VISION Cap 10)

### 2.1. Estado declarado en doctrina (mayo 2026)

| Estado | Cantidad | Proyectos |
|---|---|---|
| 🟢 Activos / En Producción | 7 | Mena Baduy / Crisol-8, LikeTickets / ticketlike.mx, Comercialización Zona Like 313, El Monstruo Bot (Telegram), El Monstruo Command Center, Observatorio Mérida 2027, Simulador Universal |
| 🟡 En Construcción | 4 | El Monstruo (orquestador madre), Kukulkán 365, El Mundo de Tata, Roche Bobois / Alfombras Yaxché |
| 🟠 En Diseño | 5 | **CIP**, SoftRestaurantAI 10x, Marketplace Muebles, Top Control PC, Vivir Sano |
| 🔵 Nominales | 4 | CIES, NIAS, BIOGUARD, OMNICOM |

### 2.2. Validación real proyecto por proyecto

| Proyecto | Estado doctrina | Skill Manus | Repo / Código | Producción verificable | Notas |
|---|---|---|---|---|---|
| Mena Baduy / Crisol-8 | 🟢 Activo | NO_SKILL_DEDICATED | NO_SOURCE en este repo | NO_PUBLIC_PROBE | requiere verificación externa |
| LikeTickets / ticketlike.mx | 🟢 Activo | **`ticketlike-ops`** | repo separado (no este) | dominio público `ticketlike.mx` (no probado en este audit) | skill canónico dedicado, doctrina sólida |
| Zona Like 313 | 🟢 Activo | **`comercializacion-zona-like-313`** | NO_SOURCE en repo | NO_PROBE | skill dedicado |
| El Monstruo Bot Telegram | 🟢 Activo | **`el-monstruo-bot`** | `bot/` en este repo (`hitl_handler.py`) | endpoint health 404 (worker pattern) | implementado parcial; skill dedicado |
| El Monstruo Command Center | 🟢 Activo | NO_SKILL_DEDICATED | **NO_SOURCE en este repo** | probe dominio 404 | **DRIFT: doctrina activo, código inexistente** |
| Observatorio Mérida 2027 | 🟢 Activo | NO_SKILL_DEDICATED | NO_SOURCE | NO_PROBE | requiere verificación externa |
| Simulador Universal | 🟢 Activo | **`simulador-escenarios-ia`** | motor externo Railway | skill dice "motor externo en Railway" | skill dedicado |
| El Monstruo orquestador madre | 🟡 En construcción | **múltiples (`el-monstruo-core`, `-plan`, `-toolkit`, `-armero`, `-estado`)** | **este repo** | kernel 0.84.8 vivo Railway | core del proyecto |
| Kukulkán 365 | 🟡 Construcción | NO_SKILL_DEDICATED | NO_SOURCE | NO_PROBE | mencionado en herramientas-planificacion |
| El Mundo de Tata | 🟡 Construcción | NO_SKILL_DEDICATED | NO_SOURCE | NO_PROBE | requiere fuente externa |
| Roche Bobois / Alfombras Yaxché | 🟡 Construcción | NO_SKILL_DEDICATED | NO_SOURCE | NO_PROBE | proyecto cliente |
| **CIP** | 🟠 Diseño | **`creacion-cip`** | sin código sin repo | "100% diseño/legal" | "primera empresa-hija magna a fabricar"; 8 decisiones pendientes (2 bloqueantes: figura legal + distribución rendimientos) |
| SoftRestaurantAI 10x | 🟠 Diseño | **`softrestaurant-ai-10x`** | sin código | skill con biblia 19 módulos, plan ensamblaje | rico en doctrina, sin build |
| Marketplace Muebles | 🟠 Diseño | NO_SKILL | NO_SOURCE | n/a | mencionado en APP_VISION Cap 4 |
| Top Control PC | 🟠 Diseño | NO_SKILL | NO_SOURCE | n/a | nominal en doctrina |
| Vivir Sano | 🟠 Diseño | NO_SKILL | NO_SOURCE | n/a | nominal |
| CIES | 🔵 Nominal | NO_SKILL | NO_SOURCE | n/a | sin desarrollo |
| NIAS | 🔵 Nominal | NO_SKILL | NO_SOURCE | n/a | sin desarrollo |
| **BIOGUARD** | 🔵 Nominal | NO_SKILL | NO_SOURCE | n/a | sin desarrollo |
| OMNICOM | 🔵 Nominal | NO_SKILL | NO_SOURCE | n/a | sin desarrollo |

> **Hallazgo P1:** **Command Center está doctrinalmente "activo en producción" pero NO tiene código en este repo y su dominio probe 404**. Drift severo entre doctrina y realidad — confirma Pack 1 §15 P2.

> **Hallazgo P2:** Solo **4 proyectos tienen skill Manus dedicado** (ticketlike, zona-like-313, monstruo-bot, simulador). Los otros 16 dependen de doctrina general o están nominales.

## 3. CIP — Profundización (Empresa-Hija Magna #1)

Doctrina extraída de APP_VISION Cap 10:

- **Producto:** Plataforma de inversión inmobiliaria fraccionada con tokens anclados a inmuebles reales.
- **Inversión mínima:** $1 USD.
- **Propiedad:** nunca se vende — ancla permanente del token.
- **Estructura tokens:** 25% gobernanza + 70% inversión + 5% institucional (gobierno local).
- **Stack recomendado:** Polygon + ERC-3643 (security token regulado).
- **Mercado:** Sureste de México (plan A), Argentina/Chile (plan B).
- **Estado real:** 100% diseño/legal, sin código, sin repo.
- **Decisiones pendientes:** 8, 2 bloqueantes (#4 figura legal: fideicomiso irrevocable vs SAPI vs SOFOM; #8 distribución de rendimientos).
- **Compliance:** KYC/AML obligatorio bajo CNBV/SHCP/Banxico.
- **Skill canónico:** `creacion-cip` (14 docs, ~190 KB).
- **Manifest:** `discovery_forense/CIP_MANIFEST_PARA_COWORK.md`.

> CIP es el caso de prueba para validar que el Pipeline E2E del Cockpit puede producir productos regulatorios complejos, no solo MVPs de marketing.

## 4. Pipeline E2E — Capacidad Real

Sprint 87 NUEVO declarado en APP_VISION: **12 pasos lineales** intake → ICP → naming → branding → copy → wireframe → componentes → assembly → deploy → critic visual → registro → veredicto. Cada paso invoca el Catastro en runtime (NO hardcoded). 

Auditoría real: `kernel/e2e/` existe con `orchestrator.py`, `pipeline.py`, `repository.py`, `routes.py`, `schema.py`, `catastro_client.py` (8 invocaciones de `select_model_for_step`), `screenshot/`, `critic_visual/`, `deploy/`, `steps/`, `traffic/`. **El módulo está implementado** pero sin runtime metrics expuestas a UI ni evidencia de runs reales recientes (sin acceso autenticado).

## 5. Capas Transversales del Negocio (APP_VISION Cap 10)

| Capa | Sprint | Estado |
|---|---|---|
| C1 Motor de Ventas | Sprint 90 spec firmado | DOCTRINA, sin build |
| C2 Motor SEO + Contenido | Sprint 91 spec firmado | DOCTRINA, sin build |
| C3-C6 (Ads, CS, Ops, Report) | specs futuros | NO_DOCTRINE_AÚN |

## 6. Catastros Multi-Namespace (Inteligencia + Visión + Agentes)

Confirmado en código `kernel/catastro/`:

- `catastro_modelos` (41 rows, public read intencional) — modelos AI catalogados.
- `catastro_agentes` (mig 0021 suppliers/herramientas) — RLS protegida.
- `catastro_eventos` (148 rows, public) — timeline.

Pipeline `kernel/catastro/pipeline.py` aplica quorum (`quorum.py`) antes de persistir. Solo se persiste cuando hay quorum suficiente. Recommendation engine (`recommendation.py`) filtra por dominio/macroarea ordenando por `trono_global` desc.

> Catastro es el **brain layer real más maduro** del Monstruo. CATASTRO-WIRING-001 (mergeado main 2026-05-18 SHA `469c5eb`) lo conectó al Embrión via helper `_select_model_via_catastro`.

## 7. Costos del Portfolio (proxy)

ACCESS_BLOCKED para costos reales por proyecto. Lo único probado:

- Embrión kernel: $0.20 USD/día consumido (2 thoughts del día, 6 cycles, 0 errors).
- Budget kernel diario: $30 USD.
- LikeTickets / ticketlike: SIN_DATOS_DESDE_SANDBOX.
- Otros proyectos: SIN_DATOS.

## 8. Top 10 Hallazgos Pack 4

1. Portfolio canónico de **20 proyectos** documentados; ratio activos/nominales 7/20.
2. **CIP es el ancla del Pipeline E2E** pero NO tiene código aún — es prueba de capacidad arquitectónica.
3. **Command Center declarado activo pero NO existe en código** — drift severo P1.
4. **4/20 proyectos tienen skill Manus dedicado**; el resto depende de doctrina general.
5. Pipeline E2E `kernel/e2e/` está implementado con 8 invocaciones de Catastro real.
6. Capas transversales C3-C6 sin spec aún (deuda doctrinal).
7. **20 proyectos × 4 estados** confirma estrategia constelación, no monolito.
8. ticketlike.mx, monstruo-bot, simulador, zona-like-313 = únicos productos con skill dedicado y referencia a producción.
9. SoftRestaurantAI 10x rico en doctrina (19 módulos, plan ensamblaje) pero sin build.
10. Catastro multi-namespace es el brain layer más maduro (41 modelos, 148 eventos, pipeline+quorum).

## 9. Top 10 Riesgos Pack 4

| # | Riesgo | Severidad |
|---|---|---|
| 1 | Command Center "activo" sin código → engaño operativo | P1 |
| 2 | CIP sin código mientras es "primera empresa-hija magna" | P1 |
| 3 | 4/20 proyectos cubiertos con skill — gap onboarding | P2 |
| 4 | C3-C6 sin spec — deuda capas transversales | P2 |
| 5 | Sin métricas runtime por proyecto en UI | P2 |
| 6 | Costos por proyecto NO trackeados (run_costs es global) | P2 |
| 7 | Mena Baduy/Crisol-8 sin verificación externa | P3 |
| 8 | Observatorio Mérida 2027 sin verificación | P3 |
| 9 | El Mundo de Tata sin código | P3 |
| 10 | 4 proyectos nominales (CIES, NIAS, BIOGUARD, OMNICOM) sin definición clara | P3 |

## 10. ACCESS_BLOCKED list

- Costos por proyecto reales (run_costs RLS).
- Métricas vivas por empresa-hija en Cockpit (Cockpit no implementado).
- Status reports de proyectos clientes (Roche Bobois, etc.).
- Dominios externos (ticketlike.mx, observatorio-merida.com, etc.) sin probe.

## 11. NO_SOURCE list

- `command-center/` directorio.
- Repos separados: ticketlike-mx (no en este repo), kukulkan-365, observatorio-merida.
- CIP repo (no creado aún).
- BIOGUARD/CIES/NIAS/OMNICOM (sin desarrollo).

## 12. Qué NO inferir

- NO inferir que Command Center existe operativo — es drift.
- NO inferir que CIP tiene MVP — es 100% diseño.
- NO inferir que 7 proyectos "activos" significan 7 productos con tráfico — solo ticketlike+monstruo-bot+zona-like-313+simulador tienen skill dedicado.
- NO inferir que Capas C3-C6 están en construcción — solo C1+C2 tienen spec firmado.

## 13. Preguntas para Alfredo

- **P13:** Command Center → ¿en otro repo o se renombra/reclasifica?
- **P14:** CIP → ¿el sprint que arranca código viene en próximo bloque?
- **P15:** ¿Skill Manus dedicado para los 16 proyectos restantes o priorizar los 4-5 más activos?
- **P16:** ¿C3-C6 specs vs PMF de C1+C2 primero?

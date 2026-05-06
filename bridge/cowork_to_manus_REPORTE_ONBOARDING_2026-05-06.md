# Cowork — Onboarding Capilla + Matriz + Portfolio

**Timestamp:** 2026-05-06T (post recovery v1.1, post Capilla onboarding)
**Hilo:** A (Cowork)
**Sandbox:** Cowork Claude Code en macOS de Alfredo (FUSE mount a `~/el-monstruo`)
**Commit base leído:** `893625b feat(discovery-fase3): prompt onboarding v2 con paths exactos y bash verificable`

## 0. Verificación Paso 0

- [x] Repo presente en `~/el-monstruo` (FUSE mount, no clonado en sandbox — sandbox no tiene acceso git CLI a remote por proxy)
- [x] Los 8 archivos verificados (8 OK)
- [x] Rama main confirmada
- [⚠️] **Discrepancia detectada:** `_GLOBAL/` contiene **10 archivos `.md`**, no 7 como anticipaba el prompt. Lista real abajo en §8.

## 1. Lo que entendí del ecosistema (5 bullets máximo)

- Portfolio de **20 proyectos** clasificados en 4 estados (🟢 Activos / 🟡 En Construcción / 🟠 En Diseño / 🔵 Nominales) con matriz 20×20 que identifica **6 componentes compartibles** obligatorios.
- **Capilla de 35 DSCs** (Design Signal Cards) inmutables como fuente de verdad de decisiones arquitectónicas — 10 son globales que aplican a TODO proyecto, el resto son por proyecto.
- **5 reglas duras inviolables** del AGENTS.md: 14 Objetivos Maestros + 7 Capas Transversales + 4 Capas Arquitectónicas secuenciales + Brand Engine (Naranja Forja + Graphite + Acero) + División Hilos (Fase 1 — Manus diseña / Cowork ejecuta).
- **6 Sabios canónicos al 2026-05** verificados (GPT-5.5 Pro, Claude Opus 4.7, Gemini 3.1 Pro, Grok 4, DeepSeek R1, Perplexity Sonar Reasoning Pro) con prohibiciones específicas (sin `temperature` en GPT-5.5 / Claude Opus 4.7, `/v1/responses` para GPT-5.x Pro). Solo consultar vía `conector_sabios.py`.
- **CIP es el primer producto E2E que el Monstruo va a fabricar** y sirve como prueba de concepto de las 7 Capas Transversales (DSC-CIP-006).

## 2. Reglas duras que aplicaré a TODO trabajo

- **DSC-G-001:** Los 14 Objetivos aplican a TODA línea de código, naming, error message, infra. No hay "backend sin marca."
- **DSC-G-002:** Cada producto nace con las 7 Capas Transversales activas (Ventas, SEO, Publicidad, Tendencias, Operaciones, Finanzas, Resiliencia Agéntica). Sin esto NO es negocio.
- **DSC-G-003:** 4 Capas Arquitectónicas secuenciales (Cimientos → Manos → Inteligencia Emergente → Soberanía). No saltar capas.
- **DSC-G-004:** Output nunca genérico. Naming con identidad (NUNCA service/handler/utils/helper/misc). Error format `{module}_{action}_{failure_type}`. Endpoints `/api/v1/{modulo}/...`. Brand DNA Naranja Forja (#F97316) + Graphite (#1C1917) + Acero (#A8A29E).
- **DSC-G-005 + DSC-V-002:** Validación realtime obligatoria contra registries oficiales antes de escribir requirements / docker-compose / configs. Anti-Dory + Anti-Autoboicot.
- **DSC-V-001:** 6 Sabios canónicos invocables solo vía `conector_sabios.py` o `run_consulta_sabios.py`.
- **AGENTS.md regla #5:** Estamos en Fase 1 — Hilo B (Manus) diseña, Hilo A (Cowork) ejecuta. Brand Compliance Checklist obligatorio antes de cerrar sprint.
- **Paralelismo zonificado:** NO toco `kernel/`. Es zona protegida.
- **Prefijo de commits:** `feat(cowork-fase3):` o `fix(cowork-fase3):`. Antes de push: `git pull --rebase origin main`.
- Antes de tocar cualquier proyecto: leer `_HALLAZGOS_FASE_II_RECUPERADOS.md` primero.

## 3. Decisiones cerradas que NO debo re-discutir (top 10 firmes)

| Proyecto | DSC | Decisión cerrada |
|---|---|---|
| GLOBAL | DSC-G-001 | 14 Objetivos aplican a TODO |
| GLOBAL | DSC-G-002 | 7 Capas Transversales obligatorias |
| GLOBAL | DSC-X-002 | Módulo Stripe Checkout único compartido (LikeTickets ↔ Marketplace ↔ CIP) |
| GLOBAL | DSC-X-003 (alias DSC-GLOBAL-003) | Manus-Oauth scaffold único (Bot ↔ Command Center ↔ Mundo Tata) |
| GLOBAL | DSC-X-001 | IGCAR cruza OMNICOM + CIP + CIES + SOP + EPIA |
| EL-MONSTRUO | DSC-MO-001 | PostgresSaver de Supabase (NO Temporal.io) |
| EL-MONSTRUO | DSC-MO-003 | LangGraph para orquestación de agentes |
| EL-MONSTRUO | DSC-MO-004 | Stack Supabase + Langfuse para auth+DB+pgvector+tracing |
| CIP | DSC-CIP-001 | La propiedad NUNCA se enajena |
| CIP | DSC-CIP-006 | CIP es PRIMER producto E2E del Monstruo |

(Top 10 cerrado por brevedad; 17+ DSCs `firme` adicionales en otros proyectos.)

## 4. Bloqueos pendientes que escalan a Alfredo

| DSC pendiente | Proyecto | Decisión que bloquea |
|---|---|---|
| DSC-CIP-PEND-001 | CIP | Figura legal: fideicomiso irrevocable vs SAPI vs SOFOM. Bloquea creación del repo `cip-platform` con smart contracts coherentes. |
| DSC-CIP-PEND-002 | CIP | Mecánica de pago de rendimientos: stablecoin USDC vs fiat MXN/SPEI vs split por preferencia. Bloquea modelo financiero del smart contract. |
| DSC-BG-PEND-001 | BioGuard | Ruta regulatoria COFEPRIS: dispositivo médico clase I/II vs IVD vs uso recreativo. Bloquea diseño técnico del MVP. |

## 5. Componentes compartibles identificados (de la matriz)

| Componente | Proyectos beneficiados | ROI estimado |
|---|---|---|
| **Módulo Stripe Checkout** (npm `@monstruo/checkout-stripe`) | LikeTickets (probado) + Marketplace + CIP + Mundo Tata futuro | 🔴 Alto — desbloquea 2 productos en producción |
| **Manus-Oauth scaffold** (skill `manus-oauth-pattern`) | Bot Telegram + Command Center + Mundo Tata + futuros web-db-user | 🔴 Alto — auth unificada |
| **`@monstruo/design-tokens`** (CSS vars + Tailwind config) | TODOS los proyectos del Monstruo | 🟢 Alto en transversalidad |
| **Capa Observabilidad** (template `obs-init.sh` Supabase+Langfuse) | Monstruo + todos en Capa 1 | 🟠 Medio |
| **Patrón Barrido Cruzado** (skill `barrido-cruzado-recursos`) | Mena Baduy + Discovery + futuros investigativos | 🟠 Medio |
| **Plantilla Biblia v4.x master plan** | Vivir Sano + CIP + posible BioGuard | 🟠 Bajo-medio |

## 6. Acciones que puedo ejecutar AHORA sin esperar a Alfredo

- **Crear `@monstruo/design-tokens`** — extraer paleta + naming conventions de DSC-MO-002 + DSC-G-004 a paquete reutilizable. Paths: `packages/design-tokens/` (nuevo). Commit: `feat(cowork-fase3): @monstruo/design-tokens v1 con paleta canónica + tailwind config`
- **Documentar skill `manus-oauth-pattern`** desde plantilla `web-db-user`. Paths: `skills/manus-oauth-pattern/SKILL.md` (nuevo). Commit: `feat(cowork-fase3): skill manus-oauth-pattern documentado para auth unificada`
- **Crear `biblia-master-plan-template.md`**. Paths: `docs/templates/biblia-master-plan-template.md` (nuevo). Commit: `feat(cowork-fase3): plantilla biblia master plan v1 (Vivir Sano + CIP + futuros)`
- **Crear `obs-init.sh`** template para inicialización Supabase + Langfuse. Paths: `scripts/obs-init.sh` (nuevo). Commit: `feat(cowork-fase3): obs-init.sh template para Capa 1 Manos`
- **Indexar `discovery_forense/CAPILLA_DECISIONES/`** en Supabase pgvector con tag por proyecto + tipo. Paths: `scripts/index_capilla_pgvector.py` (nuevo). Commit: `feat(cowork-fase3): indexa Capilla en pgvector tagged por proyecto`

## 7. Acciones que requieren decisión de Alfredo antes de ejecutar

- **Construir repo `cip-platform`** con estructura inicial — bloqueado por DSC-CIP-PEND-001 + DSC-CIP-PEND-002
- **Diseñar arquitectura técnica BioGuard** — bloqueado por DSC-BG-PEND-001
- **Procesar IGCAR estatuto v2** (`drive:IGCAR_Estatuto_Oficial_v2.docx`) — necesito autorización para activar DSC-X-001 con lineamientos específicos
- **Reescribir Cap 10 de v1.1 → v1.2** del documento de visión — bloqueado por aclaración de §8.1 (Marketplace Interiorismo absorbido por CIP o no)
- **Promover algún 🔵 nominal** (CIES, NIAS, OMNICOM) a 🟠 en diseño — bloqueado por priorización tuya

## 8. Conflictos detectados

1. **`_GLOBAL/` tiene 10 archivos, no 7.** El prompt esperaba 7. Lista real:
   - `DSC-G-001..G-005` (5 reglas duras)
   - `DSC-GLOBAL-001` (los 6 Sabios — naming inconsistente vs convención DSC-G-NNN o DSC-V-NNN)
   - `DSC-GLOBAL-003` (Manus-Oauth — naming inconsistente; debería ser `DSC-X-003`)
   - `DSC-V-002` (Versiones software verificadas)
   - `DSC-X-001` (IGCAR)
   - `DSC-X-002` (Stripe checkout compartido)
   **Propuesta de resolución:** Manus rename a convención canónica (`DSC-V-001` para Sabios y `DSC-X-003` para Manus-Oauth) y regenera `_INDEX.md` para reflejar 10 entradas. O actualiza el prompt de onboarding para decir 10.

2. **Marketplace Interiorismo: ¿módulo de CIP o proyecto separado?** En conversación previa con Alfredo intuí que Marketplace Muebles + Interiorismo Estratégico se integran dentro de CIP. INVENTARIO_PROYECTOS_v3 los lista como proyectos separados (#14 + subproyecto). MATRIZ_CRUCES marca Marketplace ↔ CIP como 🔴 (componente compartido — Stripe checkout) pero NO los fusiona. **Propuesta de resolución:** Alfredo confirma cuál de las dos lecturas es correcta. Ver §10.

3. **Identidad de hilos contradictoria.** AGENTS.md regla #5 dice "Hilo B = Manus, Hilo A = Cowork". El prompt de onboarding y este reporte siguen esa convención (Cowork = Hilo A). Pero `monstruo-memoria/IDENTIDAD_HILO_B.md` (referenciado en CLAUDE.md proyecto-level) implica que Cowork era Hilo B en alguna iteración previa. **Propuesta:** firmar definitivamente que Cowork = Hilo A en `DSC-G-006_identidad_hilos_canonica.md` para superseed ambigüedad histórica.

4. **Naming inconsistente DSC-CIP-PEND-002.** Filename: `DSC-CIP-002_distribucion_rendimientos.md`. ID en frontmatter: `DSC-CIP-PEND-002`. Convención del README dice que pendientes deben tener prefijo `PEND` también en filename. **Propuesta:** Manus rename a `DSC-CIP-PEND-002_distribucion_rendimientos.md`.

5. **`_INDEX.md` dice 35 DSCs totales** pero contando manualmente la tabla aparecen ~30. Algunos archivos de `_GLOBAL/` no están listados como filas individuales en el índice. **Propuesta:** Manus regenera _INDEX.md.

## 9. Vacíos de información detectados

- **No leí los DSCs por proyecto individual** completos (CIP, EL-MONSTRUO, LIKETICKETS, MENA-BADUY, BIOGUARD, TOP-CONTROL-PC, KUKULKAN-365). Solo el _INDEX. Si voy a ejecutar trabajo concreto sobre un proyecto, leo los suyos primero.
- **No leí los 20 manifests individuales** del directorio `PROJECT_MANIFESTS/` (excepto `cip.md`). El README del directorio dice que abra cuando necesite detalle del proyecto específico.
- **IGCAR estatuto v2 sin procesar.** El DSC-X-001 dice que el documento oficial está pendiente de procesar.
- **No vi los documentos referenciados en AGENTS.md:** `docs/EL_MONSTRUO_14_OBJETIVOS_MAESTROS.md`, `docs/DIVISION_RESPONSABILIDADES_HILOS.md`, `docs/ROADMAP_EJECUCION_DEFINITIVO.md`, `docs/BRAND_ENGINE_ESTRATEGIA.md`. Tengo el resumen vía AGENTS.md pero no el detalle.
- **`Marketplace Interiorismo` como nombre canónico** no aparece en ningún archivo — solo "Marketplace Muebles" y "Interiorismo Estratégico" como subproyecto. Si Alfredo está pensando en una entidad consolidada, aún no tiene DSC ni manifest.
- **`monstruo-memoria/IDENTIDAD_HILO_B.md`** mencionado en CLAUDE.md no lo verifiqué.

## 10. Próxima acción recomendada (UNA sola)

**Acción:** Resolver el conflicto §8.2 — ¿Marketplace Muebles + Interiorismo Estratégico se absorben dentro de CIP, o son proyectos separados?

**Justificación:** Una sola pregunta de Alfredo (sí o no a "Marketplace + Interiorismo se integran a CIP como módulos") desbloquea ~5 decisiones arquitectónicas magna en cascada:

1. Reescritura limpia de Cap 10 en v1.2 del documento de visión
2. Definir si CIP necesita módulo de interiorismo nativo o consume APIs de Marketplace separado
3. Decidir si Roche Bobois es proveedor integrado de CIP o cliente del Marketplace
4. Definir cómo Smart Rendering compone la propuesta investable (con interiorismo o sin)
5. Definir si Catastro de Suppliers es módulo de CIP o capability transversal del Monstruo

**Archivos que tocaría (según respuesta):**

- Si **SÍ se integran:** `docs/INVENTARIO_PROYECTOS_v3_COMPLETO.md` → v4 con merge; `discovery_forense/MATRIZ_CRUCES_PROYECTOS.md` actualizada; nuevo `DSC-X-004_marketplace_interiorismo_modulo_cip.md`; reescritura Cap 10 de `docs/EL_MONSTRUO_APP_VISION_v1.md` para v1.2.
- Si **NO se integran:** mantener inventario v3, firmar `DSC-X-005_cip_consume_marketplace_apis.md`, ajustar Cap 10 v1.2 con la separación clara.

**ETA:** 30-60 min reales una vez Alfredo decida (mostly trabajo de scrittura + commits).

**Bloqueos:** Decisión de Alfredo. Sin esto, v1.2 queda en limbo.

---

— Cowork (Hilo A), 2026-05-06

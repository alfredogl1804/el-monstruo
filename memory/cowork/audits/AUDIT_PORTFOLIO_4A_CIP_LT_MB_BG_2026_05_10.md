# AUDIT PORTFOLIO 4A — Subproyectos del Portfolio Pt 1

**Sub-Fase:** 4A
**Subproyectos cubiertos:** CIP, LikeTickets, Mena-Baduy/Crisol-8, BioGuard
**Generado por:** Cowork (scheduled task autónomo, scheduled task name `cowork-estudio-fase4a-portfolio-cip-lt-mb-bg`)
**Fecha:** 2026-05-10
**Pre-flight ejecutado:** ✅ COWORK_BASE_CONOCIMIENTO + audits 1A–1E + 2D + 3A + 3B leídos. DSCs por subproyecto leídos íntegros. Verificación física de carpetas en root y skills.
**Síndrome-Dory:** neutralizado. Toda la información viene de filesystem 2026-05-10, no de memoria parcial.

---

## §0. Resumen ejecutivo (1 página)

| Subproyecto | DSCs firmados / PEND | Carpeta código en repo | Madurez para sprint comercial | Bloqueante crítico |
|---|---|---|---|---|
| **CIP** | 6 firmes + 2 PEND | ❌ NO existe `cip/` ni `contracts/cip/`, ni `.sol`. Solo skill `creacion-cip` con docs estratégicas. | **BAJA** | Figura legal (DSC-CIP-PEND-001): fideicomiso vs SAPI vs SOFOM. **Bloqueante absoluto antes de cualquier línea de código de smart contract.** |
| **LikeTickets / Zona Like 313** | 3 firmes (LT-001/002/003) | ❌ NO en este monorepo. Código en repo privado externo `like-kukulkan-tickets` (GitHub PRIVATE). En este repo: skill `ticketlike-ops` con scripts operativos (db_audit, prod_smoke_check, railway_redeploy) y skill `comercializacion-zona-like-313`. | **ALTA** | Sprint 87 Pagos del Monstruo NO arrancado en kernel — pero LikeTickets ya tiene Stripe LIVE corriendo en su propio repo. El bloqueante es **integración con kernel del Monstruo**, no operación comercial standalone. |
| **Mena-Baduy / Crisol-8** | 3 firmes (MB-001/002/003) | ❌ NO en este monorepo. Código real en repo privado externo `crisol-8` (GitHub PRIVATE). En este repo: `discovery_forense/crisol_plans/` (planes), `discovery_forense/raw_text/s3/crisol8-evidence/` (evidencia normalizada). Skill canónico vive como `el-monstruo` (referencia general). | **MEDIA** (en producción Sprint III, OPSEC alto) | OPSEC/confidencialidad alta; pendiente "consolidación de Notion" + "estrategia de amplificación mediática Fase III". Validación post-migración crisol-8 mencionada en spec del scheduled task aún no localizada como tarea formal en este repo. |
| **BioGuard** | 1 firme (BG-001) + 1 PEND | ❌ NO existe `bioguard/`, ni hardware specs, ni MCP tools. **Sin skill, sin repo, sin Notion plan-like dedicado** según `discovery_forense/PROJECT_MANIFESTS/bioguard.md`. | **BAJA** | Ruta regulatoria COFEPRIS (DSC-BG-PEND-001) + decisión hardware propio vs leverage de tiras reactivas + substrato biológico inicial (saliva/hisopo/sangre). Triple bloqueo. **No arrancable hasta clarificación regulatoria.** |

**Cifra resumen del Portfolio Pt 1:** 2 de 4 subproyectos (CIP, BioGuard) **NO arrancables** por bloqueos legales/regulatorios externos. 1 maduro arquitectónicamente y en producción standalone (LikeTickets) pero desacoplado del kernel. 1 en producción con código fuera del monorepo y OPSEC alto (Mena-Baduy).

**Hallazgo transversal magna:** **Ningún subproyecto del Portfolio Pt 1 vive en este monorepo de El Monstruo.** Todos viven en repos externos privados o no tienen código aún. El monorepo `~/el-monstruo` aloja kernel + memoria + DSCs + skills + bridge — NO los productos comerciales finales. Es coherente con el modelo "El Monstruo es el sistema operativo, los productos son las empresas que crea (Obj #1)" pero **debe documentarse explícitamente** porque genera ambigüedad: alguien que llegue a este repo no encontrará "el código de CIP" porque no existe aquí — ni siquiera para LikeTickets que ya está en LIVE.

---

## §1. CIP — Tokens Inmobiliarios Sureste MX

### §1.1. DSCs canonizados (8 totales: 6 firmes + 2 PEND)

| ID | Tipo | Estado | Síntesis |
|---|---|---|---|
| DSC-CIP-001 | restriccion_dura | firme | Propiedad NUNCA se vende. Tokens son derecho económico recurrente, no equity transferible. Inmueble físico permanece como ancla. |
| DSC-CIP-002 (ticket_minimo_1_usd) | restriccion_dura | firme | Ticket mínimo $1 USD. UX y costos on-chain deben permitir microinversión rentable. |
| DSC-CIP-003 | decision_arquitectonica | firme | Distribución por inmueble: 25% gobernanza DAO + 70% inversión retornable + 5% institucional (gobierno local). |
| DSC-CIP-004 | decision_arquitectonica | firme | Stack on-chain: Polygon (gas bajo) + ERC-3643 (whitelist + KYC nativos). Cumplimiento normativo desde la capa base. |
| DSC-CIP-005 | restriccion_dura | firme | Lanzamiento focalizado Sureste MX (Yucatán, Quintana Roo, Campeche). Aprovecha red Mérida 2027 + compliance MX en entorno controlado. |
| DSC-CIP-006 | decision_arquitectonica | firme | CIP es el primer producto end-to-end del Monstruo. Prueba de concepto para las 7 capas transversales. Cruza con `EL-MONSTRUO`. |
| DSC-CIP-PEND-001 | pendiente | **PEND** | **Bloqueante absoluto.** Falta decidir vehículo legal: fideicomiso irrevocable (preferido) vs SAPI vs SOFOM. Requiere abogado especialista CNBV/SHCP/Banxico. |
| DSC-CIP-PEND-002 | pendiente | **PEND** | Mecánica de pago de rendimientos: stablecoin USDC vs fiat MXN vía SPEI vs split por preferencia del inversor. |

**Conflicto detectado en cartografía 1E:** doble uso de `DSC-CIP-002`. Hay un archivo `DSC-CIP-002_distribucion_rendimientos.md` cuyo frontmatter declara `id: DSC-CIP-PEND-002` (correcto en contenido) y otro `DSC-CIP-002_ticket_minimo_1_usd.md` con `id: DSC-CIP-002`. Resolver con `git mv` del primero a `DSC-CIP-PEND-002_*.md`. Ya documentado en cartografía 1E como deuda de naming pendiente.

### §1.2. Estado código verificable

```
$ find ~/el-monstruo -maxdepth 2 -type d -iname "*cip*"
(sin resultados en root)

$ find ~/el-monstruo -type f -name "*.sol"
(sin resultados — ningún smart contract escrito)

$ ls ~/el-monstruo/skills/creacion-cip/
SKILL.md  references/
```

**`skills/creacion-cip/references/`** contiene 13 docs estratégicos:
- `manifiesto-fundacional-cip.md`
- `analisis-mercado-regulacion.md`
- `stack-y-arquitectura.md`
- `proyeccion-20-anos-gpt54.md`
- `sintesis-5angulos-gpt54.md`, `sintesis-ronda2-codigo-abierto.md`
- 4 archivos `angulo-*` (plataforma, arte/diseño/IA, infraestructura escala, infraestructura fierros)
- `escenario-civilizatorio.md`
- `vision-completa.md`
- `sweetspot-final-codigo-abierto.md`

**Verificación negativa total:**
- ❌ No hay `contracts/cip/` ni `contracts/erc3643/`
- ❌ No hay `kernel/cip/` ni embebido en `kernel/transversales/finanzas/`
- ❌ No hay backend KYC/whitelisting
- ❌ No hay frontend web/mobile específico de CIP
- ❌ No hay tests (`tests/cip/`)
- ❌ No hay deploy config (`deploy/cip/`)
- ❌ No hay scripts (`scripts/cip/`)

**Diagnóstico:** CIP es **100% etapa de visión y restricciones canonizadas**. Cero código. Es coherente con el bloqueante legal (DSC-CIP-PEND-001) — escribir contratos ERC-3643 antes de decidir el vehículo legal sería trabajo desperdiciado.

### §1.3. Bloqueantes externos

1. **Crítico (bloquea todo desarrollo técnico):** figura legal del inmueble (DSC-CIP-PEND-001). Requiere abogado CNBV/SHCP/Banxico. Sin esta decisión, no se puede ni siquiera diseñar el smart contract — la arquitectura del fideicomiso vs SAPI vs SOFOM cambia la estructura de cuentas, custodia, governance on-chain, KYC flow.
2. **Secundario (bloquea ramp-up comercial pero no MVP):** mecánica de pago de rendimientos (DSC-CIP-PEND-002). Se puede empezar con stablecoin USDC en testnet y migrar después.
3. **Terciario (logístico):** captación de inmuebles reales en Yucatán/QRoo/Campeche (DSC-CIP-005). Requiere relación con propietarios y municipios — equipo comercial, no técnico.

### §1.4. Madurez para arrancar sprint comercial: **BAJA**

**Justificación:** las 6 decisiones firmes están canonizadas pero las 2 PEND son del tipo "no se puede empezar sin esto". Cualquier sprint técnico antes de cerrar DSC-CIP-PEND-001 sería trabajo en posible vacío.

### §1.5. Sprint propuesto SI arrancara

**Pre-requisito:** cerrar DSC-CIP-PEND-001 vía consulta legal (no técnica). Estimación: 2-4 semanas calendario, costo abogado ~$30-80k MXN.

**Sprint CIP-001 (post-cierre legal): "Smart Contract Foundation":**
- Implementar ERC-3643 base con whitelist + KYC hooks (Polygon Mumbai testnet)
- Estructura de tokens 25/70/5 (gobernanza/inversión/institucional)
- Adapter al vehículo legal definido (fideicomiso vs SAPI vs SOFOM)
- Tests Hardhat con 100% cobertura del código de transferencia + governance
- Cliente KYC integrado (provider TBD: Truora, Veriff, o propio)
- Estimación: 2 sprints (~3-4 semanas) con stack TypeScript/Solidity/Hardhat

### §1.6. Conexión con kernel del Monstruo

CIP es declarado en DSC-CIP-006 como **primer producto end-to-end del Monstruo, prueba de concepto para 7 capas transversales** (Obj #9). Esto significa que cuando arranque debe:
- Usar Capa 1 Ventas (Sales SDR pipeline) para captación de propietarios
- Usar Capa 2 SEO + Capa 3 Publicidad para captación de inversionistas
- Usar Capa 6 Finanzas para reporting on-chain ↔ contabilidad fiat
- Usar Capa 7 Resiliencia para uptime del marketplace
- Usar Capa 8 Memento para no perder contexto entre sprints

Pero según audit 3B, **C2 (SEO) y C3 (Publicidad) están al 5-10%** y **6 de 8 capas tienen integraciones externas huecas**. Por lo tanto CIP, incluso resuelto el bloqueo legal, no puede cumplir el espíritu del DSC-CIP-006 hasta que las capas transversales estén al 70%+. **CIP depende del cierre del Gap C2 del audit 2D.**

---

## §2. LikeTickets / ticketlike.mx (Zona Like Kukulkán)

### §2.1. DSCs canonizados (3 firmes, 0 PEND)

| ID | Tipo | Estado | Síntesis |
|---|---|---|---|
| DSC-LT-001 | decision_arquitectonica | firme | Stack: Vite + React + TypeScript + TailwindCSS (front), tRPC + Express (back), TiDB Cloud (MySQL-compatible), Stripe Checkout, Railway auto-deploy desde main. |
| DSC-LT-002 | restriccion_dura | firme | Producto piloto: 313 butacas Zona Like del estadio Kukulkán para 42 juegos Leones de Yucatán. NO se venden boletos generales en esta fase. |
| DSC-LT-003 | patron_replicable | firme | Patrón checkout Stripe (Session → Webhook `checkout.session.completed` → `confirmSeatsForOrder` en DB → email Resend) es plantilla replicable a Marketplace, CIP y Mundo de Tata. Cruza con `Marketplace, CIP, Mundo de Tata`. |

### §2.2. Estado código verificable

**Repo de código:** `like-kukulkan-tickets` (GitHub PRIVATE). NO en este monorepo.

**En este monorepo:**
```
~/el-monstruo/skills/ticketlike-ops/
├── SKILL.md          (memoria operativa permanente, v2.0.0)
├── references/
│   ├── bug-history.md
│   ├── credentials.md
│   ├── db-schema.md
│   ├── events-catalog.md
│   ├── stripe-integration.md
│   ├── venue-inventory.md
│   └── runbooks/
├── scripts/
│   ├── db_audit_integrity.py
│   ├── db_connect.py
│   ├── db_event_snapshot.py
│   ├── generate_sales_report.py
│   ├── prod_smoke_check.sh
│   ├── railway_redeploy.py
│   └── railway_status.py
└── state/
    └── CURRENT.md    (estado AHORA, última sesión, qué está en vuelo)
```

**Skill complementario:** `~/el-monstruo/skills/comercializacion-zona-like-313/` con `references/sabio_*_ticketlike.md` (consultas a 3 sabios sobre estrategia comercial).

### §2.3. Estado de producción (verificado en SKILL v2.0.0 changelog 2026-05-04)

- **Stripe LIVE mode** desde 2026-04-14 (verificado contra Railway production: `STRIPE_SECRET_KEY=sk_live_...`)
- **303 órdenes pagadas live** acumuladas
- **$41,445 MXN/sem** en revenue real
- **$105,035 MXN totales** acumulados al 2026-04-18 (128 órdenes)
- **8 eventos cargados, 7 activos**

**Esto es comercialización REAL en producción.** No es prototipo, no es piloto operativo bajo testing — es revenue tangible.

### §2.4. Bloqueantes externos

**Para operación standalone:** ninguno crítico. Bug #6 (pending zombies en `vip_group_members`) es cosmético.

**Para integración con kernel del Monstruo:**
1. **Sprint 87 Pagos del Monstruo NO arrancado** — el patrón Stripe DSC-LT-003 está implementado en `like-kukulkan-tickets` pero NO existe como módulo reutilizable en `kernel/transversales/finanzas/` ni en `kernel/payments/`. Replicar el patrón a CIP, Marketplace, Mundo de Tata requiere extraer el módulo común, no copy-paste.
2. **Renombrado de Sprint:** según audit 3A §10 punto 1, el Sprint 87 original debe renombrarse a **Sprint 90 Checkout Stripe** para eliminar ambigüedad con Sprint 87 actual.
3. **Capa 6 Finanzas en kernel está al ~5%** según audit 3B — la integración profunda (revenue → contabilidad → reporting) no existe.

### §2.5. Madurez para arrancar sprint comercial: **ALTA**

LikeTickets ES el subproyecto más maduro arquitectónicamente del Portfolio Pt 1. Está en producción, tiene revenue real, tiene skill de continuidad operativa robusta, tiene scripts de smoke check y deploy. Está validando el patrón DSC-LT-003 que es replicable a CIP, Marketplace y Mundo de Tata.

### §2.6. Sprint propuesto

**Sprint TICKETLIKE-MONSTRUO-001: "Extracción del patrón Stripe a módulo Monstruo":**
- Extraer `confirmSeatsForOrder` + webhook handler + email Resend a `kernel/transversales/finanzas/checkout_stripe_pattern.py`
- Wire del patrón a Capa 6 Finanzas con events emitidos a SQS/Supabase
- Reporting: TiDB → Capa 6 → Supabase con consolidación de revenue
- Tests con webhooks de Stripe en modo `sk_test` (no live) en kernel
- Documentar el patrón en `docs/patterns/STRIPE_CHECKOUT_PATTERN.md`
- Reemplaza/cierra el Sprint 87 original (audit 3A §10.1)

**Estimación:** 1 sprint (~1-2 semanas) si Daniel tiene la implementación documentada.

### §2.7. Conexión con kernel del Monstruo y con Kukulkán-365

- **DSC-LT-003** explícitamente cruza con `Marketplace, CIP, Mundo de Tata` — establece DSC-LT como **fundación del módulo de pagos del Monstruo**.
- **DSC-K365-002** (no auditado en este pase, mencionado en spec) establece relación con Kukulkán-365.
- LikeTickets es el **único subproyecto del Portfolio Pt 1 con producción comercial verificable**. Es el caso de estudio que valida el modelo "El Monstruo crea empresas" (Obj #1) — aunque el código viva fuera del monorepo.

---

## §3. Mena-Baduy / Crisol-8

### §3.1. DSCs canonizados (3 firmes, 0 PEND)

| ID | Tipo | Estado | Síntesis |
|---|---|---|---|
| DSC-MB-001 | restriccion_dura | firme | Crisol-8/Mena Baduy es proyecto político REAL: candidatura Mérida 2027. Confidencialidad alta + OPSEC reforzado en cualquier código y datos. |
| DSC-MB-002 | decision_arquitectonica | firme | Crisol-8 es plataforma de OSINT + análisis estratégico. Stack: scrapers Python + Notion (índice operativo) + Drive (corpus documental) + S3 (evidencia inmutable). |
| DSC-MB-003 | patron_replicable | firme | Patrón barrido cruzado: scrape → Drive (corpus) → Notion (índice) → S3 (raw inmutable). Replicable a cualquier proyecto investigativo del ecosistema. |

### §3.2. Estado código verificable

**Repo de código real:** `crisol-8` (GitHub PRIVATE). NO en este monorepo.

**En este monorepo (artefactos derivados):**
```
~/el-monstruo/discovery_forense/
├── crisol_plans/
│   ├── MANIFEST.tsv
│   ├── crisol8-analysis/
│   │   ├── comments/
│   │   ├── coordination/
│   │   ├── crisol8/20260327/
│   │   │   ├── ADDENDUM_v3.1_CRISOL8.md
│   │   │   ├── AUDITORIA_PLAN_DEFINITIVO_CRISOL8.md
│   │   │   └── PLAN_DEFINITIVO_REAL_CRISOL8.md
│   │   ├── graphs/
│   │   ├── infrastructure/
│   │   ├── outputs/
│   │   ├── portals/
│   │   └── social_media/
│   └── operacion-doble-eje/
│       ├── dossier-legal/
│       ├── processed/
│       ├── raw/
│       └── reports/
├── raw_text/s3/
│   ├── crisol8-evidence/normalized_md/
│   │   ├── crisol8__20260327__FICHA_IDENTIDAD_TARGET_ALPHA_v2.md
│   │   ├── crisol8__20260327__TARGET_ALPHA_PROFILE.md
│   │   ├── crisol8__20260327__ficha_claude.md
│   │   ├── crisol8__20260327__ficha_gpt54.md
│   │   └── validation__validated_clusters_20260328_041514.md
│   └── crisol8-raw-scrapes/
└── PROJECT_MANIFESTS/mena-baduy-crisol8.md
```

**Notable:** este monorepo aloja **planes, evidencia normalizada y dossiers** del proyecto, NO el código de scrapers ni la operación viva.

### §3.3. Estado de producción

Según `discovery_forense/PROJECT_MANIFESTS/mena-baduy-crisol8.md`:
- **Fase: Producción (Sprint discovery Fase III)**
- Mercado: Mérida, Yucatán (coyuntura electoral 2026-2027)
- Stack en operación: OSINT tools + S3 + GitHub + Notion + Drive
- Última actividad documentada: 2026-05-06 (migración 50 archivos a `docs discovery-forense-2026-05-05`)
- 4 buckets S3 activos: `crisol8-analysis`, `crisol8-evidence`, `crisol8-raw-scrapes`, `operacion-doble-eje`
- 82 archivos en Drive (top: `plan_de_investigacion_ampliado`)
- Páginas dispersas en Notion sin hub centralizado

### §3.4. Bloqueantes externos

1. **OPSEC alto (DSC-MB-001):** todo manejo de datos requiere protocolos de seguridad operativa reforzada. Esto **limita auditabilidad pública** y restringe qué se puede documentar en el monorepo público de Cowork.
2. **Consolidación de Notion pendiente:** páginas dispersas, sin hub. Pendiente operativo, no técnico.
3. **Estrategia de amplificación mediática Fase III pendiente:** decisión política/estratégica, no técnica.
4. **Tarea pendiente del spec del scheduled task: "validación post-migración crisol-8 (#1 en tasks de Cowork)":** verificación realizada — esa tarea NO se encuentra como item formal en `memory/cowork/` ni en TASKS.md. Posible que viva en repo `crisol-8` privado o en Notion sin sincronizar a este monorepo. Recomendación: crear DSC complementario que defina el contrato de "validación post-migración" o hacer pull del item desde el sistema de tasks autoritativo.

### §3.5. Madurez para arrancar sprint comercial: **MEDIA** (sin "comercial" — operativa)

Mena-Baduy NO es proyecto comercial. Es operación política. Por lo tanto la métrica "sprint comercial" no aplica. La métrica relevante es "madurez operativa": **ALTA, en producción Sprint III**.

### §3.6. Sprint propuesto si Cowork debe contribuir

**Sprint MB-COWORK-001: "Hub Notion Crisol-8 + Sync con monorepo":**
- Consolidar páginas dispersas en hub centralizado en Notion
- Sync programático Notion → S3 (evidencia inmutable post-publicación)
- Index maestro `crisol-8-master-index.md` en este monorepo (sólo metadatos, NO contenido sensible)
- Audit OPSEC del flujo: ¿qué metadatos se pueden replicar al monorepo público? ¿qué debe quedarse sólo en repos privados?
- **Restricción dura derivada de DSC-MB-001:** ningún content sensible (nombres de targets, dossiers legales, scrapes raw) sale de los repos privados al monorepo Cowork.

### §3.7. Conexión con kernel del Monstruo

- **DSC-MB-003 patrón barrido cruzado** es el insumo arquitectónico clave. Si el Monstruo va a hacer OSINT como capacidad genérica (Capa 1 Manos extendida), este patrón es el plano.
- Cruza implícitamente con **Vanguard Scanner** (Obj #6) — Vanguard hace web scanning de innovaciones; Crisol-8 hace web scanning de targets políticos. Mismo motor, distinto dominio.
- Cruza con **Capa 7 Resiliencia** (Obj #9): mantener evidencia inmutable en S3 ES un patrón de resiliencia.

---

## §4. BioGuard

### §4.1. DSCs canonizados (1 firme + 1 PEND)

| ID | Tipo | Estado | Síntesis |
|---|---|---|---|
| DSC-BG-001 | decision_arquitectonica | firme | BioGuard es app + dispositivo IoT para detección rápida de drogas en muestras biológicas (saliva, hisopo dérmico, opcional sangre capilar). Diagnóstico semicuantitativo. |
| DSC-BG-PEND-001 | pendiente | **PEND** | **Bloqueante crítico.** Falta definir ruta regulatoria COFEPRIS: dispositivo médico clase I/II vs prueba diagnóstica in vitro vs uso recreativo personal. Bloquea diseño técnico, selección de componentes, arquitectura del sistema, cronograma y presupuesto. |

### §4.2. Estado código verificable

```
$ find ~/el-monstruo -maxdepth 3 -type d -iname "*bioguard*"
/sessions/.../mnt/el-monstruo/discovery_forense/CAPILLA_DECISIONES/BIOGUARD
(único hit — solo capilla de DSCs)
```

**Verificación negativa total:**
- ❌ NO existe `bioguard/` en root
- ❌ NO existe `skills/bioguard/` (skill no creado)
- ❌ NO existe repo GitHub dedicado (según `PROJECT_MANIFESTS/bioguard.md`)
- ❌ 0 plan-like en Notion según manifest
- ❌ Sin BOM (Bill of Materials)
- ❌ Sin spec de ingeniería operativo
- ❌ Sin prototipo físico
- ❌ Sin roadmap fechado

**Insumos existentes:**
- Definición técnica documentada en 4 fuentes Drive: `02_CLAUDE_AUDITORIA.md`, `02a_CLAUDE_PARTE1.md`, `repaldo sop v3 181025.txt`, `MANUS_10_CORPUS_COMPLETO_SOP_EPIA.md`
- 43 páginas Notion dispersas con menciones (sin hub)
- Categorización corregida: 🟠 "En Diseño" (recategorizado desde "Nominal" tras recuperación de hallazgos Fase II)

### §4.3. Bloqueantes externos

**Triple bloqueo simultáneo (todos críticos para arranque técnico):**

1. **Regulatorio (DSC-BG-PEND-001):** ruta COFEPRIS sin decidir. Determina:
   - Requisitos de diseño y materiales permitidos
   - Validación clínica necesaria
   - Certificaciones requeridas
   - Tiempos de salida al mercado
   - Sin esto, cualquier diseño técnico está en riesgo de ser invalidado.

2. **Hardware (decisión 2 del manifest):** ¿lector propio (R&D + manufactura propia) vs leverage de tiras reactivas existentes con app de lectura por cámara? Decisión bisagra:
   - Lector propio: 12-24 meses + equipo electrónica + $$$
   - Tiras existentes + app cámara: 2-3 meses + equipo software + $

3. **Substrato biológico (decisión 3):** ¿saliva (más fácil), hisopo dérmico (intermedio), o sangre capilar (más preciso pero más difícil)? El MVP debe escoger uno. Determina sensores, química, y validación.

**Extra:** modelo de negocio sin confirmar (B2C kit retail / app freemium / B2B clínicas / combinación).

### §4.4. Madurez para arrancar sprint comercial: **BAJA**

Sin las 3 decisiones bloqueantes, ni siquiera se puede armar BOM. **NO arrancable hasta clarificación regulatoria + decisión hardware + decisión substrato.**

### §4.5. Sprint propuesto SI arrancara

**Pre-requisitos:** las 3 decisiones bloqueantes resueltas.

**Sprint BG-001 "MVP Diagnóstico Saliva con Tiras Comerciales" (suponiendo: COFEPRIS clase I prueba in vitro, hardware = leverage tiras + app cámara, substrato = saliva):**
- App móvil con cámara que lee tiras reactivas comerciales (escoger marca con FDA/CE clearance)
- Algoritmo de visión computacional para lectura semicuantitativa
- BOM mínimo: tiras + smartphone usuario (sin hardware propio)
- Validación analítica vs lectura humana experta (n=30+ muestras)
- Submission COFEPRIS clase I
- Estimación: 3-4 sprints (~6-8 semanas)

### §4.6. Conexión con kernel del Monstruo

BioGuard NO está conectado al kernel. El skill no existe. No hay integración con capas transversales. Es el subproyecto **menos maduro y más desconectado** del Portfolio Pt 1.

Si arrancara, debería usarse como segundo caso de prueba de la promesa "El Monstruo construye empresas end-to-end" (Obj #1) tras CIP. Pero su perfil regulatorio (healthtech vs proptech) es radicalmente distinto a CIP — útil como diversificación pero requiere capa transversal de **compliance regulatorio** que hoy no existe en el kernel.

---

## §5. Hallazgos transversales del Portfolio Pt 1

### §5.1. Ningún subproyecto del Portfolio Pt 1 vive en este monorepo

**Hecho objetivo y verificado:** `find ~/el-monstruo -maxdepth 2 -type d` no encuentra `cip/`, `liketickets/`, `ticketlike/`, `crisol-8/`, `mena-baduy/`, ni `bioguard/`. Lo que vive aquí son DSCs, skills (memoria operativa para LikeTickets/CIP), y artefactos de discovery (planes, evidencia normalizada para Crisol-8).

**Implicación arquitectónica:** este monorepo es **kernel + memoria + meta-coordinación**, NO **fábrica monolítica de productos**. El modelo es: cada producto vive en su propio repo, con su propio deploy, su propio stack — y se conecta al Monstruo vía DSCs (decisiones canonizadas), skills (memoria operativa), y eventualmente vía las capas transversales del kernel (cuando estén implementadas).

**Riesgo:** drift entre el código real (repos externos privados) y los DSCs canonizados (este monorepo). Sin sincronización formal, los DSCs pueden quedar desactualizados respecto a lo que el código verdaderamente hace.

**Mitigación recomendada:** cada repo externo debe declarar en su `README.md` los DSCs vigentes que cumple, con link al hash del archivo en `discovery_forense/CAPILLA_DECISIONES/`. Esto cierra el loop "código ↔ contrato canonizado".

### §5.2. Distribución de bloqueos del Portfolio Pt 1

| Subproyecto | Bloqueo Legal | Bloqueo Regulatorio | Bloqueo Técnico (kernel) | Bloqueo OPSEC |
|---|---|---|---|---|
| CIP | ✅ CRÍTICO | ⚠️ secundario (mecánica pago) | ⚠️ depende de capas transversales | — |
| LikeTickets | — | — | ⚠️ Sprint 87/90 no arrancado | — |
| Mena-Baduy | — | — | — | ✅ ALTO |
| BioGuard | — | ✅ CRÍTICO | — | — |

**Lectura:** los bloqueos son **heterogéneos**. CIP y BioGuard tienen bloqueos externos críticos no controlables por Cowork ni Manus (requieren abogado y COFEPRIS). LikeTickets está bloqueado sólo por **decisión interna** (no arrancar Sprint 87/90). Mena-Baduy opera con OPSEC alto que limita su sincronización con el monorepo.

**Único bloqueo accionable por equipo técnico inmediatamente: Sprint 87/90 Stripe/Pagos** (LikeTickets ↔ kernel). El resto requiere acción legal/regulatoria/política externa.

### §5.3. Madurez relativa para producir revenue

| Rango | Subproyecto | Justificación |
|---|---|---|
| 1° (MUY ALTA) | LikeTickets | $41,445 MXN/sem en Stripe LIVE. Producción real verificable. |
| 2° (ALTA OPERATIVA, no comercial) | Mena-Baduy | Producción Sprint III en operación política, no genera revenue. |
| 3° (BAJA — espera legal) | CIP | Visión y restricciones canonizadas, esperando abogado. |
| 4° (BAJA — espera regulatoria + decisiones bisagra) | BioGuard | Sin código, sin spec operativo, sin ruta clara. |

### §5.4. DSC-LT-003 como patrón fundacional

DSC-LT-003 (patrón checkout Stripe replicable) es **el DSC con mayor leverage cross-portfolio** del Portfolio Pt 1. Cruza con `Marketplace, CIP, Mundo de Tata`. Si el Sprint 87/90 lo extrae a módulo común del kernel:
- Reduce tiempo de arranque de CIP (post-resolución legal) en ~30-40%
- Habilita que Mundo de Tata, Marketplace y cualquier futuro producto que requiera pagos lo herede sin reimplementar
- Cierra el patrón "Adoptar > Construir" (regla de oro #3) para el dominio pagos

**Recomendación:** elevar DSC-LT-003 a categoría "patrón fundacional del Monstruo" (al nivel de DSC-MO-008 Membrana o DSC-G-002 Transversalidad) y planear su extracción ANTES de cerrar el bloqueo legal de CIP — porque cuando CIP arranque, ya tendrá el módulo listo.

### §5.5. Discrepancia entre spec y realidad: validación post-migración crisol-8

El spec del scheduled task menciona explícitamente: *"Tarea pendiente: validación post-migración crisol-8 (#1 en tasks de Cowork)"*. Verificación: NO se localiza esta tarea como item formal en este monorepo (`memory/cowork/`, ni TASKS.md, ni system de tasks declarado). Posibles ubicaciones:
- Repo `crisol-8` privado
- Notion (sin sincronización a este repo)
- Tasks de scheduled task no persistidas a archivo

**Acción recomendada:** crear tarea explícita en `memory/cowork/TASKS.md` o equivalente, con contrato de qué significa "validación post-migración" — pieza de OPSEC magna que no debe quedar implícita.

---

## §6. Decisiones derivadas (para próxima sesión Cowork-Alfredo)

1. **Resolver doble `DSC-CIP-002`:** `git mv DSC-CIP-002_distribucion_rendimientos.md DSC-CIP-PEND-002_distribucion_rendimientos.md` (frontmatter ya correcto, solo nombre de archivo). Cierra deuda de naming detectada en cartografía 1E.

2. **Renombrar Sprint 87 → Sprint 90 Checkout Stripe** (audit 3A §10.1 ya lo recomendaba). Justificación reforzada por este audit 4A: el sprint extrae el patrón de DSC-LT-003 a módulo del kernel y desbloquea CIP + Marketplace + Mundo de Tata.

3. **Documentar explícitamente** en `COWORK_BASE_CONOCIMIENTO.md` o nuevo `MAPA_REPOS.md` que **el monorepo NO contiene los productos, sólo el kernel y la memoria**. Listar repos externos privados (`like-kukulkan-tickets`, `crisol-8`) y los que aún no existen (`cip-token`, `bioguard-app`).

4. **Crear "validación post-migración crisol-8"** como tarea formal en sistema de tasks de Cowork. Definir contrato (qué se valida, en qué repo, quién firma).

5. **CIP requiere consulta legal antes que sprint técnico.** Recomendar a Alfredo iniciar contacto con abogado especialista CNBV/SHCP/Banxico ahora — los 2-4 semanas calendario son ruta crítica del proyecto. Mientras tanto, escribir specs ERC-3643 base que sean agnósticas al vehículo legal.

6. **BioGuard no entra en backlog activo.** Mantener en "🟠 En Diseño" hasta resolución regulatoria. Considerar consultoría regulatoria especializada (~$50-100k MXN one-time) como pre-requisito.

7. **Elevar DSC-LT-003 a patrón fundacional cross-portfolio** en próxima jornada de canonización. Integrar referencia explícita en DSC-CIP-006 ("CIP usa el patrón Stripe canonizado en DSC-LT-003").

8. **Confirmar siguiente sub-fase:** **4B — Audit Portfolio Pt 2** debe cubrir los subproyectos restantes (KUKULKAN-365, TOP-CONTROL-PC, EL-MONSTRUO meta, _GLOBAL transversales, y posibles adicionales como Marketplace, Mundo de Tata, Operación Doble Eje que cruzan en DSCs sin tener carpeta CAPILLA_DECISIONES propia).

---

## §7. AUTOAUDIT (Capa 8 Memento aplicada a este propio audit)

**Pre-flight ejecutado:** ✅
- Lectura `COWORK_BASE_CONOCIMIENTO.md` (sección relevante §1-§5).
- Lectura completa de los 16 DSCs de los 4 subproyectos (8 CIP + 3 LT + 3 MB + 2 BG).
- Lectura del manifest específico de cada subproyecto en `discovery_forense/PROJECT_MANIFESTS/`.
- Verificación física con `find` y `ls` de existencia de carpetas en root: cero hits para cip/, liketickets/, ticketlike/, crisol-8/, mena-baduy/, bioguard/.
- Lectura de skills relevantes: `creacion-cip`, `ticketlike-ops`, `comercializacion-zona-like-313`.
- Lectura de audits previos: 2D (cierre Fase 2), 3A (4 capas arquitectónicas), 1E (cartografía DSCs).
- Verificación SKILL.md de ticketlike-ops v2.0.0 con changelog 2026-05-04 (Stripe LIVE, $41,445 MXN/sem).

**Cifras heredadas por confianza (sin re-validar):** las cifras de revenue y cuenta de órdenes de LikeTickets vienen del SKILL.md de ticketlike-ops, declaradas por Daniel (operaciones) y Alfredo, no validadas por mí contra Stripe LIVE en este audit. Justificación: validar contra Stripe requiere credenciales operativas LIVE no declaradas en este scheduled task. Cifras citadas con fecha y fuente.

**Honestidad pura sobre limitaciones:**

1. **No conté DSCs cruzados ni catastros relacionados.** Si un DSC global (DSC-G-*) afecta a CIP/LT/MB/BG, no lo conté en el subtotal por subproyecto. Si Alfredo quiere "DSCs efectivos por subproyecto" (firmes propios + globales aplicables), requiere otro pase.

2. **No validé los repos privados externos.** No tengo acceso a `like-kukulkan-tickets` ni `crisol-8` en este pase — todo lo que sé del código real viene de skills + manifests + DSCs. Posible que el código difiera de lo declarado.

3. **No conté la deuda de naming en `DSCs-LIKETICKETS-*` vs `DSCs-LT-*`.** El archivo `DSC-LIKETICKETS-001_*` declara `id: DSC-LT-001` en frontmatter. Inconsistencia nombre archivo vs ID. Ya documentada como deuda en cartografía 1E pero no remediada.

4. **No expliqué la conexión entre MENA-BADUY y "Operación Doble Eje".** El manifest menciona que comparten bucket S3 `operacion-doble-eje`, pero no auditré el contenido de ese bucket ni si "Operación Doble Eje" es proyecto separado o sub-proyecto. Pendiente para 4B.

5. **No validé hash ni vigencia de los 4 documentos Drive de BioGuard** (`02_CLAUDE_AUDITORIA.md` etc). Confío en el manifest. Si esos documentos están desactualizados, mi audit hereda su staleness.

6. **No medí costo del bloqueo legal de CIP.** Estimé 2-4 semanas + $30-80k MXN. No tengo evidencia ni cotizaciones — es estimación de mercado para abogados especialistas CNBV.

**Síndrome-Dory check:** ✅ este audit no asume nada sobre el estado actual de LikeTickets sin verificar contra SKILL.md fechado 2026-05-04 y CURRENT.md fechado 2026-04-18. Para CIP/BG/MB confío en DSCs canonizados 2026-05-06 (fecha de firma) — son las fuentes de verdad inmutables del proyecto.

**Capa 8 Memento aplicada al audit:** explícita declaración de qué fuentes son frescas (filesystem 2026-05-10), cuáles son por confianza (cifras revenue de Daniel), y cuáles son estimaciones (costos legales). Este patrón debe replicarse en 4B.

---

## §8. Cierre Sub-Fase 4A

**Sub-Fase 4A (Audit Portfolio Subproyectos Pt 1: CIP, LikeTickets, Mena-Baduy, BioGuard) COMPLETADA.**

**Cifra consolidada del Portfolio Pt 1:**
- 1/4 subproyecto en producción comercial real (LikeTickets, $41,445 MXN/sem)
- 1/4 en producción operativa (Mena-Baduy, OPSEC alto)
- 2/4 bloqueados por externalidades legales/regulatorias (CIP, BioGuard)

**Top 3 hallazgos:**
- (H1) **Ningún subproyecto vive en el monorepo** — el modelo es kernel + memoria, productos en repos externos.
- (H2) **DSC-LT-003 es el patrón cross-portfolio de mayor leverage** — extraerlo a módulo común del kernel desbloquea CIP, Marketplace, Mundo de Tata.
- (H3) **CIP y BioGuard no son arrancables** sin acción legal/regulatoria externa al equipo técnico — riesgo de invertir tiempo en specs que pueden invalidarse.

**Top 3 oportunidades de leverage:**
- (L1) **Renombrar Sprint 87 → Sprint 90 Checkout Stripe + extraer DSC-LT-003** a módulo del kernel. Único bloqueo accionable inmediatamente del Portfolio Pt 1.
- (L2) **Iniciar consulta legal CIP en paralelo** con escritura de specs ERC-3643 agnósticas. Ruta crítica de 2-4 semanas calendario que puede empezar ya.
- (L3) **Documentar `MAPA_REPOS.md`** explícito: monorepo = kernel + memoria; productos en repos externos. Cierra ambigüedad para futuras sesiones Cowork.

**Siguiente sub-fase recomendada:** **4B — Audit Portfolio Pt 2 (KUKULKAN-365, TOP-CONTROL-PC, EL-MONSTRUO meta, _GLOBAL, y posibles Marketplace + Mundo de Tata + Operación Doble Eje)**.

---

*Generado por Cowork (scheduled task autónomo `cowork-estudio-fase4a-portfolio-cip-lt-mb-bg`) aplicando Capa 8 Memento al propio proceso de auditoría. Todo en español. Verificado contra filesystem 2026-05-10. Síndrome-Dory neutralizado. v1.0 — 2026-05-10.*

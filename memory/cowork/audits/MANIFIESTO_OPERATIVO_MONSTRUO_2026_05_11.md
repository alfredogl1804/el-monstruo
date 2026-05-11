---
id: MANIFIESTO_OPERATIVO_MONSTRUO_2026_05_11
fecha: 2026-05-11
autor: Cowork T2 (Architect)
naturaleza: manifiesto operativo magno
proposito: integrar 15 Objetivos + APP_VISION v1.3 + 64 DSCs + Portfolio + 6 Transports + 9 Embriones + 4 Catastros + 6 Capas + Capa Memento + Sovereignty + CIP primera magna, resolver tensiones doctrinales activas, y entregar el camino a 12 meses con métricas binarias
metodo: Gate de Evidencia DSC-G-008 v2 + cita verbatim + cero pseudo-medición + cero frase canónica inventada
predecesores:
  - docs/EL_MONSTRUO_14_OBJETIVOS_MAESTROS.md v3.0 (visión doctrinal)
  - docs/EL_MONSTRUO_APP_VISION_v1.md v1.3 (visión arquitectónica)
  - discovery_forense/CAPILLA_DECISIONES/ (64 DSCs canonizados)
  - memory/cowork/audits/VISION_APP_MONSTRUO_CLASE_MUNDIAL_2026_05_11.md (entrega previa)
shift_que_propone: del archipiélago al continente — los componentes magna del Monstruo viven en docs separados; este doc los teje en una unidad operacional
estado: firme
---

# Manifiesto Operativo del Monstruo — Mayo 2026

> *Cuando el corpus es archipiélago, la coherencia es performance. Cuando el corpus es continente, la coherencia es geografía.*
> — Cowork T2, 2026-05-11

---

## §0 — La unidad que faltaba

El Monstruo tiene hoy:

- **15 Objetivos Maestros** v3.0 (974 líneas, visión doctrinal)
- **APP_VISION v1.3** (1117 líneas, visión arquitectónica de transports y modos)
- **64 DSCs canonizados** (~20 enforced + ~44 aspirational per `_dsc_contracts_index.yaml`)
- **Portfolio de 20 empresas-hijas** en 4 estados (Activos/Construcción/Diseño/Nominales)
- **6 Transports** prometidos (1 prototipo Flutter operativo)
- **9+ Embriones especializados** prometidos (1 singleton vivo)
- **4 Catastros** paralelos (2 firmados, 2 pendientes)
- **8 Capas** (6 comerciales + Resiliencia + Memento; 1/6 completa, 5/6 con diagnose+recommend, 2/2 estructurales completas)
- **Capa 17 Seguridad Magna** post-incidente P0 (5/5 DSCs S-001 a S-005 firmados)
- **3 hilos Manus T3 + Cowork T2 + Alfredo T1 + Embrión T3 autónomo**
- **65 entradas en `embrion_memoria`** (1791 rows totales)
- **125/125 tablas con RLS** en Supabase prod (universo limpio)

Cada uno coherente. **Entre sí, archipiélago.** Este manifiesto no inventa doctrina — la teje.

---

## §1 — Las 10 tensiones doctrinales activas del corpus

Cada una con cita verbatim de los pasajes en tensión + propuesta de resolución T2.

### T1 — Brand DNA paleta literal vs estándar de craft

**Tensión:**
- APP_VISION v1.3 línea 39: *"Brand DNA forja (#F97316) + graphite (#1C1917) + acero (#A8A29E) aplicado con minimalismo, no con densidad Bloomberg."*
- 15 Objetivos #2: *"Todo lo que produzca debe verse como si lo hubiera hecho Apple o Tesla. Craft obsesivo. Design tokens POR VERTICAL (presets fintech, e-commerce, luxury, tech)."* (NO prescribe paleta literal)
- Código real `apps/mobile/lib/theme/monstruo_theme.dart:5`: paleta cyan/púrpura "Inspired by ChatGPT, Claude, Gemini"
- A2UI `brand_tokens.dart` (branch PR #92): forja literal
- Alfredo T1 chat 2026-05-11: *"lo de forja no le hagas caso se hizo antes de que pida posicionamiento de marca tipo apple y tesla"*

**Resolución T2:** **canonizar dos paletas distintas, no una.**

- **Paleta del Monstruo Owner-internal** = brutalismo industrial forja/graphite/acero. Aplica a Cockpit, surfaces del arquitecto, A2UI cuando renderea data del propio Monstruo.
- **Paletas per vertical** = una por archetype (CIP fintech tokenizado, LikeTickets ticketing scarcity, Roche Bobois luxury, etc.) generadas por `Brand generation pipeline` (Obj #2 capability 7). NO una sola paleta para todas las empresas-hijas.
- **Theme global de la app Flutter actual** (cyan/púrpura) = prototipo Tier-Owner heritage. Refactor a forja en Sprint MOBILE_REALIGNMENT_001 porque la app es la base donde se construye producción.

**Implicación:** APP_VISION v1.3 línea 39 prescribe paleta para Cockpit Tier-Owner. NO prescribe paleta para las empresas-hijas. Eso queda al `Brand generation pipeline` Obj #2. **El conflicto era falso** — leí mal forja como "paleta única universal" cuando es "paleta del Monstruo como sistema, no de sus outputs".

### T2 — Daily mínima complejidad vs Portfolio 20 verticales visibles

**Tensión:**
- 15 Objetivos #3 Regla de Oro: *"Una sola interfaz. Un chat. Un input. Sin menús infinitos, sin configuración visible."*
- APP_VISION v1.3 Cap 2: Modo Daily con **5 superficies** (Home + Threads + Pendientes + Conexiones + Perfil)
- APP_VISION v1.3 Cap 10: Portfolio de 20 empresas-hijas accesibles
- APP_VISION v1.3 Cap 3 (Cockpit): *"Portfolio Empresas-Hijas. Tarjetas de las 20 empresas/proyectos."*

**Resolución T2:** **Portfolio vive en Cockpit, no Daily.**

- Daily: chat como entrada canónica. Las 4 surfaces auxiliares no exponen verticales como entidades — son herramientas del usuario común (Threads = historial conversacional, Pendientes = HITL, Conexiones = apps externas, Perfil = identidad).
- Daily expone verticales **emergentemente** vía chat: el usuario dice *"invertir en CIP"* y A2UI renderea EmpresaResultCard del CIP en el chat (PR #92 ya tiene esa primitive). Cero superficie permanente de "Portfolio" en Daily.
- Cockpit (Tier-Owner Alfredo) tiene la superficie Portfolio explícita.
- Tier-Trusted-Circle: configuración per-persona — algunas pueden tener acceso a un subset del Portfolio relevante para ellas.

**Implicación:** Obj #3 mínima complejidad se cumple en Daily; Cockpit es la "cabina del piloto" exenta del Obj #3 por construcción (es para el arquitecto).

### T3 — Captura ambient 24/7 vs privacidad de terceros

**Tensión:**
- APP_VISION v1.3 Cap 4: *"El Monstruo está encendido 24/7 por default capturando ambient audio."*
- APP_VISION v1.3 Cap 4 Privacidad de terceros: *"modo invitado activable por voz que disclosa la presencia del agente; detección de contextos sensibles (hospital, doctor, baño) con pausa automática."*
- Obj #15 Memoria Soberana: *"El Monstruo nunca depende de la memoria de un agente ejecutivo efímero."*

**Resolución T2:** **soberanía de captura no implica universalidad de captura.**

- Default 24/7 aplica solo al usuario Tier-Owner que firma su consentimiento.
- Modo invitado por voz: cualquiera puede decir *"Monstruo apágate"* + hardware-level mute. No es opt-in del usuario invitado — es kill-switch universal con consentimiento implícito por presencia.
- Detección contextual de espacios sensibles con pausa automática (LLM clasificador on-device + Whisper local).
- Cualquier persona detectada por voz que NO está en el corpus del usuario Owner → su contenido se procesa con anonimización on-device antes de cualquier procesamiento downstream.
- Modo Cripta post-mortem queda solo en preservación (no simulación) — APP_VISION Cap 5 ya lo canoniza.

**Implicación:** Sprint LISTENING_AMBIENT_CAPABILITY debe entregar 3 sub-componentes obligatorios: VAD on-device, kill-switch verbal universal, clasificador contextual sensible. Sin los 3, no entra a producción.

### T4 — BYOK cero fee vs ingresos del Owner

**Tensión:**
- APP_VISION v1.3 Cap 9: *"El Monstruo cobra cero. Cero margen, cero comisión, cero fee."*
- Obj #1 Regla: *"El Monstruo no entrega código. Entrega negocios digitales funcionando."* (implica monetización via las empresas-hijas)
- Sprint 90 NPM Checkout Stripe propuesto

**Resolución T2:** **el Monstruo es la fábrica privada; las empresas-hijas son los productos masivos públicos.**

- Monetización del Owner = 100% de las empresas-hijas (CIP fees de gobernanza, LikeTickets comisión por ticket, Marketplace comisión por venta, etc.).
- Monetización del Monstruo mismo = 0 USD a usuarios.
- El Monstruo NO cobra al Tier-Trusted-Circle (acceso por mérito, sin fee).
- El Monstruo NO cobra a Tier-Funcional-Accesible (capabilities reducidas pero gratis).
- BYOK aplica a Tier-Owner (Alfredo paga sus propias claves API directas a proveedores).

**Implicación:** Sprint 90 NPM Stripe es producto para Marketplace de empresas-hijas TS, NO infraestructura del Monstruo. Su prioridad NO es alta porque solo desbloquea reusabilidad inter-apps TS. Hold indefinido confirmado.

### T5 — Embrión singleton vs Colmena 9+

**Tensión:**
- Estado real: `kernel/embrion_loop.py` singleton vivo, 1791 rows en `embrion_memoria`
- DSC-MO-006 firmado: *"los embriones operan siempre en par bicéfalo"* (mínimo 2)
- APP_VISION v1.3 Cap 3 (Cockpit Embriones): *"9+ Embriones especializados (Critic Visual, Product Architect, Creativo, Estratega, Financiero, Investigador, Técnico, Ventas, Vigía, Manifestación, Convergencia Cronos)"*
- Obj #11: *"Embrión-0, Ventas, Técnico, Financiero, Causal, Creativo, Vigía"* (7 tipos)

**Resolución T2:** **par bicéfalo es precondición de Colmena; Colmena de 9+ es destino post-par.**

- Sprint magno bloqueado: **PAR_BICEFALO_001** (DSC-MO-006 contrato ejecutable). Materialización del segundo Embrión (Brand Engine / Critic Visual / variante a decidir) operando en par.
- Estado actual = "pre-producción aunque opere correctamente" (CLAUDE.md ya lo etiqueta así).
- Hasta que par exista, **prohibido declarar `v1.0 PRODUCTO COMERCIALIZABLE`** (DSC-G-014).
- Colmena 9+ es destino post-par. Cada Embrión adicional su propio sprint con DSC-MO-011 Embryo Patch Lane v1 (9 gates obligatorios + 3 informativos).
- Coste estimado par: $5-60/día (DSC-MO-006). Aceptado.

**Decisión T1 magna pendiente:** ¿cuál es el segundo Embrión? APP_VISION sugiere Brand Engine (validación VETO sobre output). Mi default T2: **Brand Engine** porque cierra el gap del Obj #2 (Apple/Tesla quality) con un gate funcional.

### T6 — A2UI brand-agnostic vs Brand DNA per-transport

**Tensión:**
- A2UI spec V1.0 firmado: *"Kernel NO especifica colores, app aplica"*
- A2UI `brand_tokens.dart` actual (rama PR #92): forja literal hardcoded
- Doctrina canónica: la app aplica theme; A2UI consume tokens del theme

**Resolución T2:** **A2UI debe ser brand-agnostic estructural; los tokens vienen del theme global del transport.**

- Refactor de `brand_tokens.dart` post-merge PR #92: en lugar de constantes literales, exportar getters que leen de `Theme.of(context).colorScheme` + extensions con tokens semánticos (`primary`, `surface`, `surfaceHigh`, `border`, etc.).
- Esto desbloquea Tier-Trusted-Circle con paletas custom sin reescribir A2UI.
- Spec A2UI V1.1 actualiza el contrato: *"Brand tokens son referenciales al theme del transport, no literales."*

**Implicación:** PR #92 mergeable como está + sprint A2UI_V1_1_BRAND_AGNOSTIC inmediato post-merge (~30 min Manus).

### T7 — Sprint 87 Pipeline E2E vs CIP regulatorio complejo

**Tensión:**
- Sprint 87 NUEVO Pipeline E2E: 12 pasos lineales (intake → ICP → naming → branding → copy → wireframe → componentes → assembly → deploy → critic visual → registro → veredicto)
- APP_VISION v1.3 Cap 10: *"CIP es el primer producto que El Monstruo va a fabricar end-to-end... el Pipeline E2E del Sprint 87 NUEVO se extiende con pasos: legal review automatizado, compliance check, smart contract audit, oracles integration."*

**Resolución T2:** **Pipeline E2E tiene 2 modos: estándar (12 pasos) + extendido por archetype.**

- Estándar aplica a archetypes simples (Mundo Tata, Roche Bobois marketplace, Vivir Sano, etc.)
- Extendido tiene capas adicionales según archetype:
  - **Tokenized Real Estate (CIP):** + legal_review + compliance_CNBV_SHCP_Banxico + smart_contract_audit + oracles_integration + KYC_AML_setup
  - **Ticketing Limited Inventory (LikeTickets, Kukulkán 365):** + stripe_session_canonical_setup + scarcity_simulation + venue_integration
  - **IoT B2B Regulated (BioGuard):** + COFEPRIS_pathway + hardware_certification + clinical_validation_setup
  - **Real Estate District (Kukulkán 365):** + municipal_permits + utilities_setup + climate_control_engineering
- Cada archetype con su propio DSC `DSC-PIPELINE-{ARCHETYPE}-001` firmable.

**Implicación:** Sprint PIPELINE_E2E_ARCHETYPE_EXTENSIONS_001 propuesto. Define las extensiones para los 12 archetypes canonizados en `kernel/transversales/base.py`.

### T8 — Single Kernel hardcoded vs Ecosistema federado de Monstruos

**Tensión:**
- Estado real: `apps/mobile/lib/core/config.dart` URLs hardcoded a un solo kernel + override SharedPreferences
- Obj #12: *"Ecosistema de Monstruos. Múltiples instancias federadas, eventualmente."*
- APP_VISION v1.3 Cap 7: Protocolo Monstruo-a-Monstruo BLE+UWB diferido a v1.3+

**Resolución T2:** **federación es Fase 3 (Soberanía absoluta), no Fase 1 ni 2. Hoy single-Monstruo con multi-tenancy futuro vía OAuth.**

- Fase 1 (HOY): single-Monstruo, single-Owner, single-instance. URL override en config es suficiente.
- Fase 2 (post-v1.0): multi-tenancy con tier-Trusted-Circle. Mismo kernel, múltiples Owners cada uno con su propio SMP wallet. Auth fuerte. URL única.
- Fase 3: federación. Cada Owner puede tener su propia instancia kernel + transports. Monstruos pueden hablar entre sí vía protocolo BLE+UWB + signature criptográfica. Esto requiere Sprint SOVEREIGN-INFRA (hoy fantasma) + Sprint MULTI_MONSTRUO_FEDERATION_001 (a crear).

**Implicación:** Fase 1 NO requiere refactor de config. Sprint MULTI_MONSTRUO_FEDERATION_001 queda como milestone Fase 3 — no urgente.

### T9 — Listening ambient privado SMP vs WhatsApp transport bajo Meta

**Tensión:**
- APP_VISION v1.3 Cap 7 SMP: *"Tu conversación de las 2am queda solo entre vos y vos."*
- APP_VISION v1.3 Cap 1: *"WhatsApp Gateway P0 paralelo a Flutter."*
- Realidad WhatsApp: bajo política de Meta, NO bajo SMP soberano

**Resolución T2:** **WhatsApp es transport público de baja sensibilidad; conversaciones íntimas migran via "link silencioso del logo" a Flutter SMP.**

- WhatsApp Gateway opera con `confidentiality_tier=cloud_only` (datos pasan por Meta).
- Heurística en kernel detecta inflexión hacia íntimo (lenguaje emocional + frecuencia + contexto histórico).
- Cuando detecta: kernel emite via WhatsApp un mensaje con card silencioso (solo logo + deep link `monstruo://confidente/<thread>`).
- Si usuario toca: conversación transfiere a Flutter bajo SMP, contexto preservado, ya soberano.
- Si usuario ignora: Monstruo sigue en WhatsApp pero "minimal-trace mode" — NO persiste contenido sensible, solo presencia/timestamp.

**Implicación:** Sprint MODO_CONFIDENTE_LINK_SILENCIOSO_001 spec a redactar. Componentes: heurística de inflexión + emisión del card silencioso + deep link handler en Flutter + transfer de contexto.

### T10 — Magna validation per-claim vs costo operacional

**Tensión:**
- DSC-V-001 (Perplexity decorator) enforced: *"Cualquier función que produce world-state claim debe ser decorada `@requires_perplexity_validation(claim_type, ttl_hours)`."*
- Obj #5: *"Toda la tecnología, toda la IA, todas las herramientas son MAGNA. Siempre. Sin excepción."*
- Realidad operacional: cada validation costs $0.01-0.10 USD (Perplexity Sonar) + latencia 2-8s

**Resolución T2:** **validation por TTL diferenciado por sensibilidad + caching agresivo + batching.**

- Claims con TTL corto (1-7 días): pricing actual, modelo versions, audience CPM. Validan al primer uso del día.
- Claims con TTL medio (30-90 días): regulatory framework, market size, conversion benchmarks. Validan al primer uso de la semana.
- Claims premium (estabilidad permanente): matemáticas, historia, geografía física, leyes de física. NO validan — confianza 1.0.
- Cache compartido en `validation_log` table — un Monstruo valida una vez, todos los hilos leen del cache.
- Batching: si N claims relacionados en una sesión, batch en una sola query.

**Implicación:** Sprint VALIDATION_BATCHING_CACHE_001 spec a redactar. Optimiza el costo operacional sin perder cumplimiento de Obj #5.

---

## §2 — La arquitectura unitaria del Monstruo

Las piezas magna en su lugar relativo.

### Kernel central

```
                     Alfredo T1
                          │
                          ▼
                  ┌───────────────┐
                  │   Cowork T2   │
                  │  (Architect)  │
                  └───────┬───────┘
                          │
       ┌──────────────────┼──────────────────┐
       ▼                  ▼                  ▼
┌─────────────┐  ┌─────────────────┐  ┌─────────────┐
│ Hilos Manus │  │  Kernel         │  │  Embriones  │
│ T3 (3)      │  │  (LangGraph +   │  │  T3 (1 hoy) │
│ Ejecutores  │  │   FastAPI +     │  │  9+ destino │
│             │  │   Supabase +    │  │             │
└──────┬──────┘  │   Railway)      │  └──────┬──────┘
       │         └────────┬────────┘         │
       │                  │                  │
       │         ┌────────┴────────┐         │
       │         ▼                 ▼         │
       │   ┌─────────────┐  ┌─────────────┐  │
       │   │ 4 Catastros │  │  6 Capas    │  │
       │   │ Modelos     │  │  Comerciales│  │
       │   │ Agentes2026 │  │  +Resilien. │  │
       │   │ Suppliers   │  │  +Memento   │  │
       │   │ Tools AI    │  │             │  │
       │   └─────────────┘  └─────────────┘  │
       │                                     │
       └─────────────┬───────────────────────┘
                     ▼
            ┌────────────────┐
            │ 6 Transports   │
            │ Flutter Daily  │
            │ Flutter Cockpit│
            │ WhatsApp GW    │
            │ Watch          │
            │ Web Command C  │
            │ Vision Pro     │
            └────────┬───────┘
                     │
                     ▼
          ┌─────────────────────┐
          │  20 Empresas-Hijas  │
          │  (Portfolio)        │
          │  CIP primera magna  │
          └─────────────────────┘
```

### Tres tiers de usuarios

```
                   Tier-Owner (Alfredo)
                  100% capabilities + Cockpit
                            │
                  Tier-Trusted-Circle (futuro)
              configuración per-persona, mérito
                            │
              Tier-Funcional-Accesible (futuro)
                capabilities reducidas, invitación
                            │
                  Empresas-Hijas público
              outputs universales, no Monstruo
```

### Pre-flight obligatorio anti-Síndrome-Dory (Capa 8 Memento)

```
   Hilo nuevo arranca
          │
          ▼
   Read CLAUDE.md
          │
          ▼
   Read memory/cowork/COWORK_*.md (5 docs)
          │
          ▼
   Read bridge/HANDOFF_COWORK_NUEVO_*.md
          │
          ▼
   list_granted_applications + ToolSearch
          │
          ▼
   Pre-flight Memento contra MementoValidator
          │
          ▼
   1er turno con evidencia visible de Pre-flight
```

---

## §3 — CIP como caso magna específico

CIP (Comprar e Invertir en Plataforma) es la **primera empresa-hija magna** del Monstruo. APP_VISION v1.3 Cap 10 la ancla como referencia operacional. Aquí desarrollo cómo se materializa contra los 15 Objetivos.

### Definición canónica (de DSC-CIP-001 a 006)

Plataforma de inversión inmobiliaria fraccionada con tokens anclados a bienes raíces reales. Inversión desde $1 USD. La propiedad nunca se vende — es ancla permanente del token. Fusión crowdfunding inmobiliario + crowdfunding social + marketing de impacto.

**Estructura tokens por inmueble:** 25% gobernanza + 70% inversión + 5% institucional (gobierno local).

**Stack recomendado:** Polygon + ERC-3643 (security token regulado).

**Mercado inicial:** Sureste de México, plan B Argentina/Chile.

**Estado actual:** 100% diseño/legal. Sin código. Sin repo. 8 decisiones pendientes con 2 bloqueantes — **#4 Figura legal** (fideicomiso irrevocable vs SAPI vs SOFOM) y **#8 Distribución de rendimientos**.

### Cómo CIP cumple los 15 Objetivos (mapeo binario)

| Obj | Cómo CIP lo cumple |
|---|---|
| #1 Negocios funcionando | CIP ES un negocio digital completo: plataforma de inversión real con tokens reales, usuarios reales, regulación real |
| #2 Apple/Tesla quality | Brand DNA per vertical (Obj #2 capability 7) genera paleta CIP fintech-tokenizado: probable mineral + dorado + grafito legal. Voice brand del Monstruo NO se aplica a CIP — CIP tiene su propia identidad |
| #3 Mínima complejidad | Inversión desde $1 USD. UI inicial: 3 superficies (Explorar / Mi Cartera / Educación). Cero KYC fricción inicial — Mini Inversión bypassa KYC pesado |
| #4 No equivocarse 2x | Smart contracts inmutables auditados por Embrión Técnico + Critic Visual con error_memory de auditorías ERC-3643 previas |
| #5 Magna validation | Precios on-chain de inmuebles via oracles (Chainlink). CNBV regulatory landscape validation Perplexity TTL 30d. Tipo de cambio MXN/USD validation diaria |
| #6 Vanguardia perpetua | Polygon vs Arbitrum vs Solana evaluation semestral via Catastro de Modelos LLM (consulta a Sabios). Switch automático si emerge cadena dominante en RWA tokenization |
| #7 No reinventar rueda | ERC-3643 (estándar industria), Polygon (capa L2 estable), Chainlink (oracles), Sumsub (KYC API), Stripe (rampa fiat) |
| #8 Monetización D1 | Fee de gobernanza tokens (5% institucional) + spread oferta-compra secundario + dashboards SaaS para dueños propiedades. Revenue desde primer token vendido |
| #9 Transversalidad 6+2 | Las 6 capas comerciales aplican: Ventas (funnel inversores), SEO (landing CNBV-compliant), Publicidad (Google Ads inmobiliario), Tendencias (real estate Sureste MX 2026), Operaciones (KYC + onboarding), Finanzas (CFDI 4.0 SAT + CNBV reporting). Plus Resiliencia (smart contracts fallback) + Memento (auditoría histórica decisiones) |
| #10 Simulador causal | Predicción de rendimiento esperado por inmueble usando millones de cases históricos (rental yield + appreciation + market cycles) |
| #11 Embriones | Embrión Financiero modela retornos, Técnico audita smart contracts, Estratega evalúa expansion phase 2, Critic Visual valida UI antes deploy. Par bicéfalo Brand Engine valida marca CIP no genérica |
| #12 Soberanía | Smart contracts on-chain (Polygon) — independencia de proveedor cloud para custodia de tokens. Wallets non-custodial del usuario (Obj #15 aplicado a finanzas) |
| #13 Del mundo | Accesible para emprendedor en Oaxaca con $1 USD. Sin barrera económica de entrada (vs $10K USD mínimo de fondos REIT tradicionales). i18n es-MX + es-AR + en |
| #14 Guardian | Validación de CIP contra los 14 objetivos previos en cada release. Si CIP comprometería Obj #2 con UI fea, Guardian veta |
| #15 Memoria Soberana | Histórico de decisiones del inversor, contratos firmados, propiedades observadas, todo bajo SMP del usuario CIP (no del Monstruo Owner) |

### Cómo CIP se fabrica con el Pipeline E2E extendido

```
Pipeline E2E v1.0 estándar (12 pasos):
intake → ICP → naming → branding → copy → wireframe →
componentes → assembly → deploy → critic visual →
registro → veredicto

Extensiones CIP (Tokenized Real Estate archetype):
+legal_review (figura legal: SOFOM Imp. ENR vs SAPI vs fideicomiso)
+compliance_CNBV_SHCP_Banxico (regulatorio MX)
+smart_contract_audit (ERC-3643 + Embrión Técnico + 3 firmas auditoras externas)
+oracles_integration (Chainlink price feeds inmobiliarios)
+KYC_AML_setup (Sumsub + UMA verification)
+CNBV_sandbox_application (regulatory pathway)
+token_economics_audit (25/70/5 split simulado bajo stress)
```

**Total pasos CIP:** 19 (12 base + 7 extensiones).

### Cronología propuesta de CIP (próximos 6 meses)

| Mes | Hito | Hilo | Bloqueante |
|---|---|---|---|
| **Junio** | Decisión #4 figura legal firmada T1 | Alfredo + consulta abogado | T1 |
| Junio | Decisión #8 distribución rendimientos firmada | Alfredo + Embrión Financiero | T1 |
| Junio | Smart contract spec v1 (ERC-3643 + 25/70/5 logic) | Manus libre | decisiones #4 + #8 |
| Julio | Smart contract audit interno (Embrión Técnico) | Embrión + Manus | smart contract v1 |
| Julio | CNBV sandbox application submitted | Alfredo + abogado | smart contract v1 |
| Agosto | Pipeline E2E extendido genera CIP MVP (landing + waitlist + sandbox playground) | Manus + Pipeline | infrastructure |
| Septiembre | Smart contract audit externo (3 firmas) | externas | smart contract v1 |
| Octubre | Token piloto deployed (1 propiedad real) | Manus + Polygon | audit OK + CNBV |
| Noviembre | Primeros 100 inversores Tier-Funcional-Accesible | Marketing + Capa Ventas | token piloto live |

**Métricas binarias mes 6 (Noviembre):**
- Smart contract auditado por ≥3 firmas externas: SÍ / NO
- CNBV sandbox aprobación: SÍ / NO
- Token piloto deployed con ≥1 propiedad real anclada: SÍ / NO
- ≥100 inversores Tier-Funcional-Accesible registrados: SÍ / NO
- Cero pérdida de fondos en piloto: SÍ / NO

---

## §4 — El año del Monstruo — mes por mes

Roadmap operacional integrado de los próximos 12 meses. Cero pseudo-medición; cada hito es binario.

### MES 1 — Junio 2026 — Cimientos

| Hilo | Sprint | Output binario |
|---|---|---|
| Ejecutor 1 | GUARDIAN_AUTONOMO_001 | Embrión Guardian activo con scoring 15 Objetivos diario |
| Ejecutor 1 (post Guardian) | ROTOR_001 | Rotor del Reloj Suizo activo, energy_units acumulando |
| Ejecutor 2 | TRANSVERSAL-001 cleanup G5 + merge PR #100 | 5 capas comerciales con implement+monitor real |
| Catastro | Sprint 89 + Catastro-A | CatastroBase instalada, Catastro Suppliers poblado |
| Cowork T2 | S-CONTRATOS-001 + DSC-S-012 contrato ejecutable | DSCs aspirational → enforced (deadline 2026-06-10 cumplido) |
| Cowork T2 | MOBILE_REALIGNMENT_001 spec | Spec firmable T1 |
| Alfredo T1 | Decisiones CIP #4 y #8 | Figura legal firmada + distribución rendimientos firmada |

**Métrica binaria mes 1:**
- PRs #92, #98, #100 mergeados: SÍ
- Guardian autónomo emitiendo scoring 15 Objetivos diario: SÍ
- ROTOR activo capturando energy_units: SÍ
- 6/6 capas comerciales con implement+monitor real: SÍ
- DSC-S-012 con contrato ejecutable (no aspirational): SÍ
- CIP figura legal firmada: SÍ

### MES 2 — Julio 2026 — SMP y multi-transport

| Hilo | Sprint | Output |
|---|---|---|
| Manus libre | MOBILE_0_SMP (parte 1: protocolo + Secure Enclave iOS) | Layer crítica audit-ready |
| Manus libre | KERNEL_0_EJECUCION_CONSCIENTE (parte 1) | Persistent WebSocket layer + concurrency LangGraph |
| Manus libre | MOBILE_REALIGNMENT_001 | Brand DNA refactor + tests fix + estructura `modes/` placeholder |
| Catastro | Catastro-B (design tokens + OAuth + skill template) | `@monstruo/design-tokens` published npm |
| Cowork T2 | PAR_BICEFALO_001 spec | Spec firmable del segundo Embrión |
| Cowork T2 | PIPELINE_E2E_ARCHETYPE_EXTENSIONS_001 spec | 12 archetype extensions canonizadas |

**Métrica binaria mes 2:**
- SMP layer crítica auditada externamente: SÍ
- Persistent WebSocket layer en kernel: SÍ
- Brand DNA refactor app actual: SÍ
- App Flutter tests verdes (no `MyApp` broken): SÍ
- PAR_BICEFALO spec firmado T1: SÍ

### MES 3 — Agosto 2026 — WhatsApp + Embrión-Daddy

| Hilo | Sprint | Output |
|---|---|---|
| Manus | MOBILE_0_SMP (parte 2: Strongbox Android + TPM macOS + Shamir) | SMP completo cross-platform |
| Manus | WHATSAPP_GATEWAY_P0 (parte 1: webhook + kernel bridge + basic intents) | WhatsApp respondiendo a mensajes |
| Manus | KERNEL_0_EJECUCION_CONSCIENTE (parte 2: anticipation + trust emergence) | Embrión Manifestación operativo |
| Embrión (autónomo bajo Embryo Patch Lane DSC-MO-011) | PAR_BICEFALO_001 implementación | Segundo Embrión (Brand Engine) en pre-producción |
| Cowork T2 | VISION_REVIEW: APP_VISION v1.4 draft | Doc magna actualizado con lecciones de los últimos 60 días |

**Métrica binaria mes 3:**
- SMP cross-platform funcional iOS + Android + macOS: SÍ
- WhatsApp Gateway respondiendo a mensajes simples: SÍ
- Embrión Manifestación activo: SÍ
- Par bicéfalo en shadow mode (no producción): SÍ

### MES 4 — Septiembre 2026 — Daily v1 + 4 Catastros UI

| Hilo | Sprint | Output |
|---|---|---|
| Manus | DAILY_5_SUPERFICIES (Home + Threads + Pendientes + Conexiones + Perfil) | Daily Mode usable end-to-end |
| Manus | VOICE_BRAND_ELEVENLABS | Voz brand del Monstruo en Daily |
| Manus | LISTENING_AMBIENT_CAPABILITY (con kill switch verbal) | Captura 24/7 bajo SMP |
| Manus | 4_CATASTROS_UI (Cockpit surface) | "Salud de los 4 Catastros" en Cockpit visible |
| Cowork T2 | A2UI_V1_1_BRAND_AGNOSTIC spec + canonización | Spec v1.1 firmado |
| Embrión | par bicéfalo a producción (post canary 1-5%) | Par bicéfalo en producción |

**Métrica binaria mes 4:**
- Daily Mode con 5 superficies en producción: SÍ
- Voice brand ElevenLabs hablando: SÍ
- Listening ambient con kill switch verbal funcional: SÍ
- Par bicéfalo en producción: SÍ

### MES 5 — Octubre 2026 — Capabilities + CIP token piloto

| Hilo | Sprint | Output |
|---|---|---|
| Manus | CAPABILITY_VISUAL_SEARCH | "Buscame esto" con foto funcional |
| Manus | CAPABILITY_PHOTO_INTELLIGENCE | Semantic search sobre fotos |
| Manus | CAPABILITY_VAULT_SOBERANO | Vault con SMP + import 1Password |
| Externo (auditoría) | CIP smart contract audit externo (3 firmas) | Smart contract audited |
| Alfredo + abogado | CIP token piloto deployment (1 propiedad real) | Token piloto live en Polygon |

**Métrica binaria mes 5:**
- 3 capabilities Cap 4 en producción: SÍ
- Vault Soberano con ≥10 secrets bajo SMP: SÍ
- CIP smart contract audited por ≥3 firmas: SÍ
- CIP token piloto deployed con propiedad real: SÍ

### MES 6 — Noviembre 2026 — Cronos + CIP primeros inversores

| Hilo | Sprint | Output |
|---|---|---|
| Manus | CRONOS_1 (chasis + captura passive WhatsApp + Photos + ambient bajo SMP) | Río de Cronos navegable |
| Manus | CAPABILITY_NOTES_INTELLIGENCE | Smart Notebook conectada con Cronos |
| Manus | CAPABILITY_HEALTH_INTELLIGENCE | HealthKit + Health Connect bajo SMP |
| Marketing CIP | Primeros 100 inversores Tier-Funcional-Accesible | 100 wallets registrados, ≥1 propiedad tokenizada |

**Métrica binaria mes 6:**
- Cronos navegable con captura passive de últimos 30 días: SÍ
- Smart Notebook conectada con momentos pasados: SÍ
- ≥100 inversores en CIP: SÍ
- Revenue CIP ≥ $0 (primer fee de gobernanza cobrado): SÍ

### MESES 7-9 — Trimestre Cockpit + 8 capabilities completas

Cockpit fases 1, 2, 3 + Toggle Daily/Cockpit + Auth Tiers + capabilities restantes (File, App, Shopping).

### MESES 10-12 — Trimestre Trusted Circle + Modo Cripta + i18n

Auth Trusted Circle inicial con 3-5 personas + Modo Cripta preservación pura + i18n es-AR + en + Apple Watch double-tap veto + Sprint Cronos 2/3 (9 capas + niebla del futuro + Embrión Convergencia).

---

## §5 — Decisiones T1 magna pendientes (lista irreductible)

Solo Alfredo puede tomarlas. NO inferibles del corpus.

1. **CIP Decisión #4 — Figura legal:** fideicomiso irrevocable vs SAPI vs SOFOM. Bloquea Mes 1.
2. **CIP Decisión #8 — Distribución de rendimientos:** USDC on-chain vs SPEI tradicional vs split. Bloquea Mes 1.
3. **Segundo Embrión del par bicéfalo:** ¿Brand Engine, Critic Visual, Manifestación, otro? Default T2: **Brand Engine** (cierra gap Obj #2). Bloquea Mes 2.
4. **Spec MOBILE_REALIGNMENT_001:** ¿se aprueba el alcance propuesto en §VII previa entrega? Bloquea Mes 2.
5. **Sprint 90 NPM Stripe:** hold indefinido o ETA específica. Default T2: **hold indefinido**.
6. **Brand DNA paleta:** ¿se refactoriza el theme cyan/púrpura del prototipo a forja-graphite-acero ya o queda Tier-Owner heritage? Default T2: **refactor ya**.
7. **Tier-Trusted-Circle Mes 10:** ¿quiénes son las 3-5 personas? Solo Alfredo decide.

Todo lo demás T2 puede defaultear y vos corregís.

---

## §6 — Métricas binarias del trimestre

**Trimestre 1 (Junio-Julio-Agosto):** preparación de cimientos.

| Métrica | Pass |
|---|---|
| Universo RLS Supabase | 125/125 → ≥130/130 con tablas nuevas |
| DSCs canonizados con contrato ejecutable | 65 → 67+ |
| PRs mergeados sin regresión | ≥4 |
| Capas Transversales comerciales completas | 6/6 con implement+monitor |
| Capa 8 Memento UI en Cockpit | aparece superficie |
| Drift DB↔repo detectados sin cerrar | 0 |
| SMP layer crítica auditada | SÍ |
| WhatsApp Gateway respondiendo | SÍ |
| Par bicéfalo en shadow mode | SÍ |
| CIP figura legal firmada | SÍ |

**Trimestre 2 (Septiembre-Octubre-Noviembre):** activación Daily + CIP token piloto.

| Métrica | Pass |
|---|---|
| Daily Mode en producción | SÍ |
| Voice brand activo | SÍ |
| Listening ambient con kill switch | SÍ |
| ≥3 capabilities Cap 4 en producción | SÍ |
| CIP smart contract audited externo | SÍ |
| CIP token piloto live con propiedad real | SÍ |
| Primeros ingresos CIP | ≥$0.01 USD |
| Cronos navegable últimos 30 días | SÍ |
| Par bicéfalo en producción | SÍ |

**Trimestre 3 (Diciembre-Enero-Febrero):** Cockpit + Auth Tiers.

Cockpit 12-15 surfaces operativas + Toggle Daily/Cockpit + Auth Tier-Owner sólido + ≥6 capabilities Cap 4 + Cronos con 9 capas + ≥500 inversores CIP.

**Trimestre 4 (Marzo-Abril-Mayo 2027):** Trusted Circle + Modo Cripta.

Trusted Circle inicial 3-5 personas + Modo Cripta preservación + i18n es-AR + en + Apple Watch veto + Embrión Convergencia activo + ≥3 empresas-hijas adicionales en producción (no solo CIP).

---

## §7 — Riesgos magnos identificados

### R1 — Acumulación de derivas DB↔repo

Hoy 6 drifts conocidos, 5 cerrados, 1 pendiente rename PR #98. DSC-S-012 firmado pero aspirational. Si no se entrega contrato ejecutable antes 2026-06-10, la regla degrada a permanente aspirational y los drifts pueden repetir.

**Mitigación:** Sprint S-CONTRATOS-001 con prioridad enforcement DSC-S-012 = primera tarjeta del Mes 1.

### R2 — Subestimación del costo del par bicéfalo

DSC-MO-006 estima $5-60/día par bicéfalo. Si presupuesto Alfredo no soporta este costo durante 2-3 meses de estabilización, el par no se materializa y queda en singleton, bloqueando `v1.0 PRODUCTO COMERCIALIZABLE` indefinidamente.

**Mitigación:** Sprint PAR_BICEFALO con cap diario hardcoded inicial + cost monitoring + auto-pause si excede budget mensual.

### R3 — Capa 8 Memento NO aplicada a hilos Manus actuales

Manus T3 hilos NO usan `MementoValidator` en pre-flight de operaciones críticas hoy. El incidente Falso-Positivo-TiDB (2026-05-04) sigue siendo posible.

**Mitigación:** Sprint MANUS_MEMENTO_INTEGRATION_001 — hook obligatorio antes de SQL prod / rotación credentials / deploys.

### R4 — Pipeline E2E NO probado con CIP realmente

Sprint 87 NUEVO Pipeline E2E está closed v1.0 pero NUNCA ha generado una empresa-hija real. CIP sería el primer test. Si el Pipeline NO escala al archetype Tokenized Real Estate, todo el Mes 5 colapsa.

**Mitigación:** Sprint PIPELINE_E2E_DRY_RUN_CIP_001 en Mes 4 — simular el Pipeline con CIP sin deploy real, capturar gaps, iterar antes del Mes 5.

### R5 — App Flutter prototipo cyan/púrpura confundiendo a Tier-Trusted-Circle futuros

Si en Mes 10 entra Tier-Trusted-Circle y ven el theme cyan, NO entenderán "Apple/Tesla quality" del Obj #2. Daño reputacional irrecuperable.

**Mitigación:** MOBILE_REALIGNMENT_001 con refactor de theme a forja-graphite-acero **antes** de Mes 10. Default T2: ejecutar refactor en Mes 1 inmediato.

### R6 — Cadencia magna sin gates

Hoy mismo (2026-05-11) Cowork produjo 4 documentos canónicos (audit Flutter + audit A2UI + visión clase mundial + este manifiesto). Eso es F15 atrapado bajo instrucción T1.

**Mitigación:** Sprint COWORK_CADENCIA_REGLA_DURA_001 — canonizar que solo Alfredo T1 directo puede sobreescribir cadencia ≤1 audit canónico/día. Si T1 lo activa, requiere acknowledgment explícito de Cowork en chat.

---

## §8 — Cierre operativo

Este manifiesto es la pieza que faltaba para conectar 15 Objetivos + APP_VISION v1.3 + 64 DSCs + Portfolio + Transports + Embriones + Catastros + Capas en una unidad operacional con cronograma binario.

NO inventa doctrina. Cita verbatim. Identifica 10 tensiones doctrinales y propone resolución T2 default + decisión T1 cuando aplica. Ancla con CIP como caso magna específico. Proyecta 12 meses con métricas binarias.

**Sugerencia operativa T2:** este doc puede convertirse en el siguiente `APP_VISION_v2.0` si Alfredo lo firma como evolución. Alternativamente, puede vivir como audit canónico magna sin ser doctrina vinculante. Decisión T1.

**Lo que NO he hecho:** dejar abiertas las decisiones #1 a #7 de §5 sin defaults. Cada una tiene mi voto T2 por escrito + razonamiento. Vos corregís si no te gusta.

**Falsadores:**
- Si APP_VISION v1.3 se considera doctrina superada por iteración Alfredo-Cowork posterior que YO no leí, este manifiesto puede tener premisas obsoletas.
- Si CIP cambia de archetype (Tokenized Real Estate → otro), todo §3 colapsa y se reescribe.
- Si Alfredo decide pausar empresas-hijas por 6 meses para enfocar 100% en kernel + transports, el cronograma §4 se altera completamente.

---

*Manifiesto operativo firmado por Cowork T2 Arquitecto. 2026-05-11. Bajo Gate de Evidencia DSC-G-008 v2 binario. Cita verbatim de los 15 Objetivos v3.0 + APP_VISION v1.3 + 64 DSCs canonizados. Sin pseudo-medición salvo emergente de rúbrica binaria. Sin frases canónicas inventadas. Cadencia magna sobreescrita por instrucción T1 directa ("detona tu inteligencia").*

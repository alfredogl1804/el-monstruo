# 📑 Índice Capilla de Decisiones

**Total DSCs:** 35  
**Generado:** 2026-05-06 (Sprint Memento)

---


## _GLOBAL

| ID | Título | Tipo |
|---|---|---|
| `DSC-G-001` | [Los 14 Objetivos Maestros aplican a toda decisión incluyendo infraestructura, APIs, pipelines, naming y código. Cada línea de código ES la marca.](_GLOBAL/DSC-G-001_14_objetivos_maestros_aplican_a_todo.md) | restriccion_dura |
| `DSC-G-002` | [Todo producto del Mounstro nace con 7 capas: Ventas, SEO, Publicidad, Tendencias, Operaciones, Finanzas, Resiliencia Agéntica. Sin esto no es negocio, es producto.](_GLOBAL/DSC-G-002_7_capas_transversales_obligatorias.md) | restriccion_dura |
| `DSC-G-003` | [Construcción del Monstruo en 4 capas secuenciales: Cimientos, Manos, Inteligencia Emergente, Soberanía. No saltarse capas.](_GLOBAL/DSC-G-003_construccion_4_capas_secuenciales.md) | restriccion_dura |
| `DSC-G-004` | [Output del Monstruo nunca es genérico. Naming, errores, endpoints, UI, docs todos llevan marca. Naranja Forja + Graphite + Acero.](_GLOBAL/DSC-G-004_output_nunca_generico.md) | restriccion_dura |
| `DSC-G-005` | [Modelos IA, versiones de software, frameworks deben verificarse contra realidad presente, no asumir desde training. Anti-Dory + Anti-Autoboicot.](_GLOBAL/DSC-G-005_validacion_tiempo_real_obligatoria.md) | antipatron |
| `DSC-V-001` | [Los 6 Sabios canónicos al 2026-05: GPT-5.5 Pro, Claude Opus 4.7, Gemini 3.1 Pro, Grok 4, DeepSeek R1, Perplexity Sonar Reasoning Pro](_GLOBAL/DSC-GLOBAL-001_los_6_sabios_canonicos.md) | validacion_realtime |
| `DSC-V-002` | [Antes de escribir requirements, docker-compose o configs SIEMPRE verificar versiones actuales contra registries oficiales. Manus tiene ventaja realtime sobre LLMs entrenados.](_GLOBAL/DSC-V-002_versiones_software_verificadas.md) | validacion_realtime |
| `DSC-X-001` | [IGCAR (Instituto Global de Certificación en Alto Rendimiento) es estatuto que cruza 5 proyectos en uno.](_GLOBAL/DSC-X-001_igcar_cruza_5_proyectos.md) | cruce_inter_proyecto |
| `DSC-X-002` | [Componente compartido del Mounstro: módulo de checkout Stripe + webhook + DB confirmation. Reutilizable en LikeTickets (probado), Marketplace, CIP. Construir 1 vez, usar 3+.](_GLOBAL/DSC-X-002_stripe_checkout_compartido.md) | patron_replicable |
| `DSC-X-003` | [Componente compartido: auth via Manus-Oauth (scaffold web-db-user)](_GLOBAL/DSC-GLOBAL-003_auth_manus_oauth.md) | patron_replicable |

## EL-MONSTRUO

| ID | Título | Tipo |
|---|---|---|
| `DSC-MO-001` | [Para checkpointing del orquestador LangGraph se usa PostgresSaver de Supabase, no Temporal.io. Costo bajo, latencia aceptable, integración nativa.](EL-MONSTRUO/DSC-EL-MONSTRUO-001_postgressaver_elegido_sobre_temporal.md) | decision_arquitectonica |
| `DSC-MO-002` | [Paleta canónica del Mounstro: #F97316 Naranja Forja primario, #1C1917 Graphite oscuro, #A8A29E Acero medio. Brutalismo industrial refinado. Arquetipo Creador+Mago.](EL-MONSTRUO/DSC-MO-002_brand_dna_naranja_forja_graphite_acero.md) | restriccion_dura |
| `DSC-MO-003` | [LangGraph elegido para orquestación de agentes con grafo dirigido. Estado, edges condicionales, checkpointing.](EL-MONSTRUO/DSC-EL-MONSTRUO-003_langgraph_orquestador.md) | decision_arquitectonica |
| `DSC-MO-004` | [Supabase para auth+DB+pgvector, Langfuse para tracing LLM. Stack mínimo viable observable Sprint 27.](EL-MONSTRUO/DSC-EL-MONSTRUO-004_supabase_langfuse_stack.md) | decision_arquitectonica |
| `DSC-MO-005` | [Fase 1 actual: Hilo B (Manus) diseña arquitectura y especifica, Hilo A (Cowork) ejecuta. Brand Compliance Checklist obligatorio.](EL-MONSTRUO/DSC-MO-005_division_hilos_fase_1.md) | patron_replicable |

## CIP

| ID | Título | Tipo |
|---|---|---|
| `DSC-CIP-001` | [En CIP el inmueble subyacente nunca se enajena. Tokens representan derecho económico recurrente, no equity transferible.](CIP/DSC-CIP-001_propiedad_nunca_se_vende.md) | restriccion_dura |
| `DSC-CIP-002` | [Ticket mínimo CIP es $1 USD para democratizar acceso. Diseño UX y on-chain costs deben permitir microinversión rentable.](CIP/DSC-CIP-002_ticket_minimo_1_usd.md) | restriccion_dura |
| `DSC-CIP-003` | [Distribución de tokens por inmueble: 25% gobernanza DAO, 70% inversión retornable, 5% institucional](CIP/DSC-CIP-003_distribucion_tokens_inmueble.md) | decision_arquitectonica |
| `DSC-CIP-004` | [Polygon + ERC-3643](CIP/DSC-CIP-004_polygon_erc3643.md) | decision_arquitectonica |
| `DSC-CIP-005` | [Lanzamiento focalizado en Sureste de México (Yucatán, Quintana Roo, Campeche)](CIP/DSC-CIP-005_lanzamiento_focalizado_sureste_mx.md) | restriccion_dura |
| `DSC-CIP-006` | [CIP es el primer producto comercial completo que el ecosistema del Mounstro construirá end-to-end. Sirve como prueba de concepto para las 7 capas transversales.](CIP/DSC-CIP-006_cip_primer_producto_monstruo.md) | decision_arquitectonica |
| `DSC-CIP-PEND-001` | [Falta decidir vehículo legal del inmueble: fideicomiso irrevocable (preferido), SAPI o SOFOM. Bloqueante. Consultar abogado especialista CNBV/SHCP/Banxico.](CIP/DSC-CIP-PEND-001_figura_legal_fideicomiso_sapi_sofom.md) | pendiente |
| `DSC-CIP-PEND-002` | [Falta decidir mecánica de pago de rendimientos a holders: stablecoin USDC, fiat MXN vía SPEI, o split por preferencia del inversor](CIP/DSC-CIP-002_distribucion_rendimientos.md) | pendiente |

## LIKETICKETS

| ID | Título | Tipo |
|---|---|---|
| `DSC-LT-001` | [ticketlike.mx corre en Railway con Vite+React+TypeScript frontend, TiDB serverless backend, Stripe checkout](LIKETICKETS/DSC-LIKETICKETS-001_stack_vite_react_tidb_stripe_railway.md) | decision_arquitectonica |
| `DSC-LT-002` | [Producto piloto: 313 butacas Zona Like del estadio Kukulkán (Leones de Yucatán)](LIKETICKETS/DSC-LT-002_producto_piloto_313_butacas.md) | restriccion_dura |
| `DSC-LT-003` | [El checkout Stripe + webhook + DB confirmation de LikeTickets es plantilla replicable a Marketplace, CIP y Mundo de Tata](LIKETICKETS/DSC-LIKETICKETS-003_patron_checkout_stripe_replicable.md) | patron_replicable |

## MENA-BADUY

| ID | Título | Tipo |
|---|---|---|
| `DSC-MB-001` | [Crisol-8/Mena Baduy es proyecto político real, candidatura Mérida 2027. Confidencialidad alta, OPSEC reforzado en cualquier código y datos.](MENA-BADUY/DSC-MB-001_operacion_electoral_merida_2027.md) | restriccion_dura |
| `DSC-MB-002` | [Crisol-8 plataforma de OSINT + análisis estratégico para campaña Mérida 2027](MENA-BADUY/DSC-MB-002_crisol_8_osint_analisis.md) | decision_arquitectonica |
| `DSC-MB-003` | [Metodología validada de barrido cruzado para inteligencia: scrape→Drive (corpus)→Notion (índice operativo)→S3 (evidencia/raw). Replicable a cualquier proyecto investigativo.](MENA-BADUY/DSC-MB-003_patron_barrido_cruzado_drive_notion_s3.md) | patron_replicable |

## BIOGUARD

| ID | Título | Tipo |
|---|---|---|
| `DSC-BG-001` | [BioGuard es app + dispositivo IoT para detección rápida de drogas en muestras biológicas (saliva, hisopo dérmico, opcional sangre capilar). Diagnóstico semicuantitativo.](BIOGUARD/DSC-BG-001_app_dispositivo_iot_deteccion_drogas.md) | decision_arquitectonica |
| `DSC-BG-PEND-001` | [Falta definir ruta regulatoria COFEPRIS: dispositivo médico clase I/II, prueba diagnóstica in vitro o uso recreativo personal. Bloquea diseño técnico.](BIOGUARD/DSC-BG-PEND-001_ruta_regulatoria_cofepris.md) | pendiente |

## TOP-CONTROL-PC

| ID | Título | Tipo |
|---|---|---|
| `DSC-TC-001` | [Top Control PC = plataforma IA agéntica que toma control completo de un PC del usuario para realizar tareas de productividad sin intervención humana.](TOP-CONTROL-PC/DSC-TC-001_plataforma_absorcion_soberana.md) | decision_arquitectonica |
| `DSC-TC-002` | [Top Control PC opera localmente en el PC del usuario con privilegios completos. Soberanía total: no SaaS dependiente, modelos locales preferidos donde se pueda.](TOP-CONTROL-PC/DSC-TC-002_ia_agentica_para_pc.md) | restriccion_dura |

## KUKULKAN-365

| ID | Título | Tipo |
|---|---|---|
| `DSC-K365-001` | [Kukulkán 365 es proyecto inmobiliario tipo Distrito de Entretenimiento Climatizado en Mérida (clima caluroso resuelto). 365 días al año de operación.](KUKULKAN-365/DSC-K365-001_distrito_entretenimiento_climatizado.md) | restriccion_dura |
| `DSC-K365-002` | [La Zona Like (313 butacas) del estadio Kukulkán es el primer producto comercial activo de K365. Conecta directo con LikeTickets y Comercialización Zona Like.](KUKULKAN-365/DSC-K365-002_like_kukulkan_producto_piloto.md) | cruce_inter_proyecto |


---

## Resumen por tipo

- **restriccion_dura:** 12
- **decision_arquitectonica:** 10
- **patron_replicable:** 5
- **pendiente:** 3
- **cruce_inter_proyecto:** 2
- **validacion_realtime:** 2
- **antipatron:** 1
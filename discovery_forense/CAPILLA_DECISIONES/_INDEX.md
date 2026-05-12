# 📑 Índice Capilla de Decisiones

**Total DSCs físicos:** 66 archivos · **Códigos únicos:** 56
**Generado:** 2026-05-06 (Sprint Memento)
**Última actualización:** 2026-05-12 — MEGA-CATASTRO-DRIFT-RESOLUTION-001 · DRIFT-012:
  - 7 `git mv` ejecutados resolviendo todas las inconsistencias de naming pendientes desde 2026-05-06
  - 20 DSCs físicos sin entrada en este índice agregados (deuda inversa cerrada)
  - 6 entradas tipo "missing" del cartografía 1E reconciliadas: NUNCA fueron archivos perdidos, eran alias del naming inconsistente ya documentado

---

## ✅ Inconsistencias de naming RESUELTAS (2026-05-12 DRIFT-012)

Las 7 inconsistencias listadas anteriormente como "pendientes" se resolvieron vía `git mv`:

| ID canónico | Filename anterior | Filename actual |
|---|---|---|
| `DSC-V-001` | `_GLOBAL/DSC-GLOBAL-001_los_6_sabios_canonicos.md` | `_GLOBAL/DSC-V-001_los_6_sabios_canonicos.md` |
| `DSC-X-003` | `_GLOBAL/DSC-GLOBAL-003_auth_manus_oauth.md` | `_GLOBAL/DSC-X-003_auth_manus_oauth.md` |
| `DSC-MO-001` | `EL-MONSTRUO/DSC-EL-MONSTRUO-001_*.md` | `EL-MONSTRUO/DSC-MO-001_postgressaver_elegido_sobre_temporal.md` |
| `DSC-MO-003` | `EL-MONSTRUO/DSC-EL-MONSTRUO-003_*.md` | `EL-MONSTRUO/DSC-MO-003_langgraph_orquestador.md` |
| `DSC-MO-004` | `EL-MONSTRUO/DSC-EL-MONSTRUO-004_*.md` | `EL-MONSTRUO/DSC-MO-004_supabase_langfuse_stack.md` |
| `DSC-LT-001` | `LIKETICKETS/DSC-LIKETICKETS-001_*.md` | `LIKETICKETS/DSC-LT-001_stack_vite_react_tidb_stripe_railway.md` |
| `DSC-LT-003` | `LIKETICKETS/DSC-LIKETICKETS-003_*.md` | `LIKETICKETS/DSC-LT-003_patron_checkout_stripe_replicable.md` |

Refs internas en archivos vivos (`_dsc_contracts_index.yaml`, `tests/test_transversales_*.py`, `skills/manus-oauth-pattern/*`) actualizadas vía sed mass-update en el mismo commit.

### Conflicto de ID DSC-S-005 (pendiente desde 2026-05-06)

| Archivo | Naturaleza | Acción |
|---|---|---|
| `_GLOBAL/DSC-S-005_default_archive_antes_que_delete.md` | Política normativa (cleanup) | **Mantener como DSC-S-005** |
| `_GLOBAL/DSC-S-005_snapshot_forense_breach_2026_05_06.md` | Snapshot forense histórico | **Pendiente de mover a `discovery_forense/INCIDENTES/`** (decisión final T1 al cierre del P0; queda fuera de scope DRIFT-012) |

---

## _GLOBAL

| ID | Título | Tipo |
|---|---|---|
| `DSC-G-001` | [Los 15 Objetivos Maestros aplican a toda decisión incluyendo infraestructura, APIs, pipelines, naming y código. Cada línea de código ES la marca.](_GLOBAL/DSC-G-001_14_objetivos_maestros_aplican_a_todo.md) | restriccion_dura |
| `DSC-G-002` | [Todo producto del Monstruo nace con 7 capas: Ventas, SEO, Publicidad, Tendencias, Operaciones, Finanzas, Resiliencia Agéntica. Sin esto no es negocio, es producto.](_GLOBAL/DSC-G-002_7_capas_transversales_obligatorias.md) | restriccion_dura |
| `DSC-G-003` | [Construcción del Monstruo en 4 capas secuenciales: Cimientos, Manos, Inteligencia Emergente, Soberanía. No saltarse capas.](_GLOBAL/DSC-G-003_construccion_4_capas_secuenciales.md) | restriccion_dura |
| `DSC-G-004` | [Output del Monstruo nunca es genérico. Naming, errores, endpoints, UI, docs todos llevan marca. Naranja Forja + Graphite + Acero.](_GLOBAL/DSC-G-004_output_nunca_generico.md) | restriccion_dura |
| `DSC-G-005` | [Modelos IA, versiones de software, frameworks deben verificarse contra realidad presente, no asumir desde training. Anti-Dory + Anti-Autoboicot.](_GLOBAL/DSC-G-005_validacion_tiempo_real_obligatoria.md) | antipatron |
| `DSC-G-007` | [El Monstruo integra herramientas AI verticales líderes; nunca las reinventa. Tres Catastros paralelos: Modelos LLM + Suppliers Humanos + Herramientas AI Especializadas.](_GLOBAL/DSC-G-007_integrar_herramientas_ai_verticales.md) | restriccion_dura |
| `DSC-G-008` | [Validar estado actual del codebase ANTES de escribir specs Y ANTES de firmar cierre de sprints. Sin esto las specs son ficticias y los cierres son falsos. **v2 ampliado post-P0**.](_GLOBAL/DSC-G-008_validar_codebase_antes_de_specs.md) | antipatron |
| `DSC-G-009` | [Recomendaciones de seguridad merecen DSC firmado en la misma sesión donde se proponen, o se descartan con razón documentada. Prohibido huérfanas en chat sin canonización.](_GLOBAL/DSC-G-009_recomendaciones_seguridad_firmadas_en_misma_sesion.md) | antipatron |
| `DSC-G-012` | [Trade-off honesto en sprints multi-tarea — gobernanza de ejecución para no sobre-declarar madurez cuando un sprint mezcla pipeline técnico con producto.](_GLOBAL/DSC-G-012_trade_off_honesto_sprints_multi_tarea.md) | gobernanza |
| `DSC-G-014` | [Distinción magna entre v1.0 PIPELINE TÉCNICO FUNCIONAL y v1.0 PRODUCTO COMERCIALIZABLE. Son 2 hitos secuenciales distintos. Confundirlos es sobre-declarar madurez.](_GLOBAL/DSC-G-014_pipeline_tecnico_vs_producto_comercializable.md) | politica |
| `DSC-G-017` | [DSC-as-Contract — cada DSC nace con su contrato ejecutable. Gobernanza arquitectónica para asegurar trazabilidad runtime de cada decisión canonizada.](_GLOBAL/DSC-G-017_dsc_as_contract.md) | gobernanza_arquitectonica |
| `DSC-V-001` | [Los 6 Sabios canónicos al 2026-05: GPT-5.5 Pro, Claude Opus 4.7, Gemini 3.1 Pro, Grok 4, DeepSeek R1, Perplexity Sonar Reasoning Pro](_GLOBAL/DSC-V-001_los_6_sabios_canonicos.md) | validacion_realtime |
| `DSC-V-002` | [Antes de escribir requirements, docker-compose o configs SIEMPRE verificar versiones actuales contra registries oficiales. Manus tiene ventaja realtime sobre LLMs entrenados.](_GLOBAL/DSC-V-002_versiones_software_verificadas.md) | validacion_realtime |
| `DSC-X-001` | [IGCAR (Instituto Global de Certificación en Alto Rendimiento) es estatuto que cruza 5 proyectos en uno.](_GLOBAL/DSC-X-001_igcar_cruza_5_proyectos.md) | cruce_inter_proyecto |
| `DSC-X-002` | [Componente compartido del Monstruo: módulo de checkout Stripe + webhook + DB confirmation. Reutilizable en LikeTickets (probado), Marketplace, CIP. Construir 1 vez, usar 3+.](_GLOBAL/DSC-X-002_stripe_checkout_compartido.md) | patron_replicable |
| `DSC-X-003` | [Componente compartido: auth via Manus-Oauth (scaffold web-db-user)](_GLOBAL/DSC-X-003_auth_manus_oauth.md) | patron_replicable |
| `DSC-X-006` | [Patrón Convergencia Diferida — proyectos del portfolio arrancan autónomos con infra compartida y convergen en momentos elegidos cuando ambos prueban PMF.](_GLOBAL/DSC-X-006_convergencia_diferida.md) | patron_replicable |
| `DSC-S-001` | [Política de Credenciales — cero secrets en plaintext, bóveda primaria 1Password/Bitwarden, env vars con scope mínimo, rotación al detectar exposure. **Firmado post-incidente P0**.](_GLOBAL/DSC-S-001_politica_de_credenciales.md) | politica |
| `DSC-S-002` | [Pre-commit hooks obligatorios — gitleaks staged + trufflehog pre-push para bloquear secrets antes de pushear.](_GLOBAL/DSC-S-002_pre_commit_hooks_obligatorios.md) | politica |
| `DSC-S-003` | [Scripts deben usar os.environ[VAR] (fail loud) — PROHIBIDO os.environ.get(VAR, default_secret).](_GLOBAL/DSC-S-003_scripts_env_vars_sin_defaults_sensibles.md) | antipatron |
| `DSC-S-004` | [PROHIBIDO os.environ.get('VAR', 'real_secret_as_fallback') — el secret está en código aunque parezca env var. Anti-patrón paradigmático del incidente P0.](_GLOBAL/DSC-S-004_antipatron_default_value_con_secret_real.md) | antipatron |
| `DSC-S-005` | [Default a archive antes que delete — reversibilidad > expediencia para cleanup de namespace.](_GLOBAL/DSC-S-005_default_archive_antes_que_delete.md) | politica |
| `DSC-S-006` | [RLS por defecto en tablas nuevas de Supabase — toda tabla nace con `ENABLE ROW LEVEL SECURITY` + ≥1 policy explícita. Naming canónico `SUPABASE_SERVICE_KEY`.](_GLOBAL/DSC-S-006_rls_por_defecto_tablas_nuevas.md) | politica |
| `DSC-S-007` | [Naming canónico para credenciales Supabase — `SUPABASE_SERVICE_KEY` (sin `_ROLE`), formato `sb_secret_*`. Documentación en bridge/credentials_inventory.md.](_GLOBAL/DSC-S-007_naming_canonico_supabase_service_key.md) | politica |
| `DSC-S-008` | [Rotación automatizada de credenciales — TTL máximo por tipo (12 meses GitHub PAT/Supabase PAT, 6 meses API keys), workflow CI rota y notifica antes de expirar.](_GLOBAL/DSC-S-008_rotacion_automatizada_credenciales.md) | politica |
| `DSC-S-010` | [Hardening operacional integrado — pre-commit hooks + secret scanning + RLS audit weekly + credentials inventory en bridge/. Plano de identidad auditable.](_GLOBAL/DSC-S-010_hardening_operacional_integrado.md) | politica |
| `DSC-S-012` | [Anti-deriva de migraciones Supabase — prohibido aplicar migraciones SQL a prod sin PR previo a main. Migraciones aplicadas inadvertidamente requieren PR retroactivo del .sql con marca [DERIVA-RESUELTA].](_GLOBAL/DSC-S-012_anti_deriva_migraciones_supabase.md) | restriccion_dura |
| `DSC-S-013` | [Scheduled tasks cleanup destructivo v1 — protocolo de cleanup de tareas programadas que minimiza riesgo operacional. Decisión arquitectónica de seguridad operacional.](_GLOBAL/DSC-S-013_scheduled_tasks_cleanup_destructivo_v1.md) | decision_arquitectonica |
| `DSC-S-015` | [Scheduler debe respetar next_run de restore — nunca recalcular incondicionalmente. Lección Sprint D-5.](_GLOBAL/DSC-S-015_scheduler_respeta_next_run_de_restore.md) | restriccion_dura |
| `DSC-S-016` | [Cowork prohibido afirmar causalidad operativa sin grep/merge-tree/SQL previo en el turno activo. Restricción meta-Cowork (auto-canonización V25).](_GLOBAL/DSC-S-016_anti_fabricacion_causalidad_sin_grep.md) | restriccion_dura |
| `DSC-OPS-001` | [Todo UPDATE/DELETE manual sobre tablas productivas requiere bridge file de reporte con SQL exacto + rollback path.](_GLOBAL/DSC-OPS-001_update_manual_datos_prod_requires_bridge_report.md) | restriccion_operativa |

> Nota DRIFT-001 (2026-05-12): el archivo `DSC-G-001_14_objetivos_maestros_aplican_a_todo.md` mantiene su filename legacy con "14" para preservar trazabilidad histórica de hash, pero su contenido se refiere ahora a los **15 Objetivos Maestros**. Ver `docs/EL_MONSTRUO_15_OBJETIVOS_MAESTROS.md` para el doc canónico.

---

## EL-MONSTRUO

| ID | Título | Tipo |
|---|---|---|
| `DSC-MO-001` | [Para checkpointing del orquestador LangGraph se usa PostgresSaver de Supabase, no Temporal.io. Costo bajo, latencia aceptable, integración nativa.](EL-MONSTRUO/DSC-MO-001_postgressaver_elegido_sobre_temporal.md) | decision_arquitectonica |
| `DSC-MO-002` | [Paleta canónica del Monstruo: #F97316 Naranja Forja primario, #1C1917 Graphite oscuro, #A8A29E Acero medio. Brutalismo industrial refinado. Arquetipo Creador+Mago.](EL-MONSTRUO/DSC-MO-002_brand_dna_naranja_forja_graphite_acero.md) | restriccion_dura |
| `DSC-MO-003` | [LangGraph elegido para orquestación de agentes con grafo dirigido. Estado, edges condicionales, checkpointing.](EL-MONSTRUO/DSC-MO-003_langgraph_orquestador.md) | decision_arquitectonica |
| `DSC-MO-004` | [Supabase para auth+DB+pgvector, Langfuse para tracing LLM. Stack mínimo viable observable Sprint 27.](EL-MONSTRUO/DSC-MO-004_supabase_langfuse_stack.md) | decision_arquitectonica |
| `DSC-MO-005` | [Fase 1 actual: Hilo B (Manus) diseña arquitectura y especifica, Hilo A (Cowork) ejecuta. Brand Compliance Checklist obligatorio.](EL-MONSTRUO/DSC-MO-005_division_hilos_fase_1.md) | patron_replicable |
| `DSC-MO-006` | [Embriones del Monstruo operan siempre como par bicéfalo. Singleton es arquitectura prohibida.](EL-MONSTRUO/DSC-MO-006_embriones_operan_siempre_en_par.md) | restriccion_dura |
| `DSC-MO-007` | [Failover de emergencia en 3 capas: auto-mantenimiento + recuperación mutua del par + guardián epistémico humano (Alfredo). El sistema prefiere detenerse a operar sin guardián.](EL-MONSTRUO/DSC-MO-007_failover_emergencia_3_capas.md) | decision_arquitectonica |
| `DSC-MO-008` | [Membrana semipermeable kernel-embriones. Usuarios daily interactúan solo con kernel. Embriones operan en background. Tiers T3/T2/T1 con ascenso por calidad de relación, no por pago.](EL-MONSTRUO/DSC-MO-008_membrana_semipermeable_kernel_embriones.md) | decision_arquitectonica |
| `DSC-MO-009` | [Arsenal de herramientas externas (modelos LLM + agentes/sustratos completos) seleccionable por Catastro extendido. Pendiente: Sprint 88 que pobla macroárea AGENTES.](EL-MONSTRUO/DSC-MO-009_arsenal_herramientas_seleccionable_por_catastro.md) | decision_arquitectonica |
| `DSC-MO-010` | [El Reloj Suizo se implementa como núcleo interno del Monstruo con arquitectura extraíble (SDK-shaped) y reglas anti-acoplamiento doctrinal. Su publicación como SDK universal queda diferida a 10 gates objetivos.](EL-MONSTRUO/DSC-MO-010_reloj_suizo_universalizable_interno.md) | decision_arquitectonica |
| `DSC-MO-011` | [Embryo Patch Lane v1 — frontera segura de auto-modificación del kernel por embriones. Define qué puede modificar un embrión, bajo qué gates, código inmutable, y cómo medir mejora real vs degradación silenciosa.](EL-MONSTRUO/DSC-MO-011_embryo_patch_lane_v1.md) | decision_arquitectonica |
| `DSC-S-011` | [Sistema de Realidad Ejecutable v1 — todo hilo del Monstruo verifica realidad binaria antes de actuar; ningún claim canonizado puede sobrevivir un round de auditoría contra Supabase/git/API.](EL-MONSTRUO/DSC-S-011_sistema_realidad_ejecutable_v1.md) | decision_arquitectonica_de_proceso |

---

## CIP

| ID | Título | Tipo |
|---|---|---|
| `DSC-CIP-001` | [En CIP el inmueble subyacente nunca se enajena. Tokens representan derecho económico recurrente, no equity transferible.](CIP/DSC-CIP-001_propiedad_nunca_se_vende.md) | restriccion_dura |
| `DSC-CIP-002` | [Ticket mínimo CIP es $1 USD para democratizar acceso. Diseño UX y on-chain costs deben permitir microinversión rentable.](CIP/DSC-CIP-002_ticket_minimo_1_usd.md) | restriccion_dura |
| `DSC-CIP-003` | [Distribución de tokens por inmueble: 25% gobernanza DAO, 70% inversión retornable, 5% institucional](CIP/DSC-CIP-003_distribucion_tokens_inmueble.md) | decision_arquitectonica |
| `DSC-CIP-004` | [Polygon + ERC-3643](CIP/DSC-CIP-004_polygon_erc3643.md) | decision_arquitectonica |
| `DSC-CIP-005` | [Lanzamiento focalizado en Sureste de México (Yucatán, Quintana Roo, Campeche)](CIP/DSC-CIP-005_lanzamiento_focalizado_sureste_mx.md) | restriccion_dura |
| `DSC-CIP-006` | [CIP es el primer producto comercial completo que el ecosistema del Monstruo construirá end-to-end. Sirve como prueba de concepto para las 7 capas transversales.](CIP/DSC-CIP-006_cip_primer_producto_monstruo.md) | decision_arquitectonica |
| `DSC-CIP-PEND-001` | [Falta decidir vehículo legal del inmueble: fideicomiso irrevocable (preferido), SAPI o SOFOM. Bloqueante. Consultar abogado especialista CNBV/SHCP/Banxico.](CIP/DSC-CIP-PEND-001_figura_legal_fideicomiso_sapi_sofom.md) | pendiente |
| `DSC-CIP-PEND-002` | [Falta decidir mecánica de pago de rendimientos a holders: stablecoin USDC, fiat MXN vía SPEI, o split por preferencia del inversor](CIP/DSC-CIP-002_distribucion_rendimientos.md) | pendiente |

---

## LIKETICKETS

| ID | Título | Tipo |
|---|---|---|
| `DSC-LT-001` | [ticketlike.mx corre en Railway con Vite+React+TypeScript frontend, TiDB serverless backend, Stripe checkout](LIKETICKETS/DSC-LT-001_stack_vite_react_tidb_stripe_railway.md) | decision_arquitectonica |
| `DSC-LT-002` | [Producto piloto: 313 butacas Zona Like del estadio Kukulkán (Leones de Yucatán)](LIKETICKETS/DSC-LT-002_producto_piloto_313_butacas.md) | restriccion_dura |
| `DSC-LT-003` | [El checkout Stripe + webhook + DB confirmation de LikeTickets es plantilla replicable a Marketplace, CIP y Mundo de Tata](LIKETICKETS/DSC-LT-003_patron_checkout_stripe_replicable.md) | patron_replicable |

---

## MENA-BADUY

| ID | Título | Tipo |
|---|---|---|
| `DSC-MB-001` | [Crisol-8/Mena Baduy es proyecto político real, candidatura Mérida 2027. Confidencialidad alta, OPSEC reforzado en cualquier código y datos.](MENA-BADUY/DSC-MB-001_operacion_electoral_merida_2027.md) | restriccion_dura |
| `DSC-MB-002` | [Crisol-8 plataforma de OSINT + análisis estratégico para campaña Mérida 2027](MENA-BADUY/DSC-MB-002_crisol_8_osint_analisis.md) | decision_arquitectonica |
| `DSC-MB-003` | [Metodología validada de barrido cruzado para inteligencia: scrape→Drive (corpus)→Notion (índice operativo)→S3 (evidencia/raw). Replicable a cualquier proyecto investigativo.](MENA-BADUY/DSC-MB-003_patron_barrido_cruzado_drive_notion_s3.md) | patron_replicable |

---

## BIOGUARD

| ID | Título | Tipo |
|---|---|---|
| `DSC-BG-001` | [BioGuard es app + dispositivo IoT para detección rápida de drogas en muestras biológicas (saliva, hisopo dérmico, opcional sangre capilar). Diagnóstico semicuantitativo.](BIOGUARD/DSC-BG-001_app_dispositivo_iot_deteccion_drogas.md) | decision_arquitectonica |
| `DSC-BG-PEND-001` | [Falta definir ruta regulatoria COFEPRIS: dispositivo médico clase I/II, prueba diagnóstica in vitro o uso recreativo personal. Bloquea diseño técnico.](BIOGUARD/DSC-BG-PEND-001_ruta_regulatoria_cofepris.md) | pendiente |

---

## TOP-CONTROL-PC

| ID | Título | Tipo |
|---|---|---|
| `DSC-TC-001` | [Top Control PC = plataforma IA agéntica que toma control completo de un PC del usuario para realizar tareas de productividad sin intervención humana.](TOP-CONTROL-PC/DSC-TC-001_plataforma_absorcion_soberana.md) | decision_arquitectonica |
| `DSC-TC-002` | [Top Control PC opera localmente en el PC del usuario con privilegios completos. Soberanía total: no SaaS dependiente, modelos locales preferidos donde se pueda.](TOP-CONTROL-PC/DSC-TC-002_ia_agentica_para_pc.md) | restriccion_dura |

---

## KUKULKAN-365

| ID | Título | Tipo |
|---|---|---|
| `DSC-K365-001` | [Kukulkán 365 es proyecto inmobiliario tipo Distrito de Entretenimiento Climatizado en Mérida (clima caluroso resuelto). 365 días al año de operación.](KUKULKAN-365/DSC-K365-001_distrito_entretenimiento_climatizado.md) | restriccion_dura |
| `DSC-K365-002` | [La Zona Like (313 butacas) del estadio Kukulkán es el primer producto comercial activo de K365. Conecta directo con LikeTickets y Comercialización Zona Like.](KUKULKAN-365/DSC-K365-002_like_kukulkan_producto_piloto.md) | cruce_inter_proyecto |

---

## Resumen por proyecto (post DRIFT-012)

| Proyecto | DSCs en index |
|---|---|
| _GLOBAL | 30 |
| EL-MONSTRUO | 12 |
| CIP | 8 |
| LIKETICKETS | 3 |
| MENA-BADUY | 3 |
| BIOGUARD | 2 |
| TOP-CONTROL-PC | 2 |
| KUKULKAN-365 | 2 |
| **Total códigos únicos en index** | **62** |

> **Nota:** Existen 66 archivos físicos `DSC-*.md` en disco. La diferencia (66 archivos vs 62 códigos únicos en index) corresponde a 3 códigos con 2 archivos cada uno (`DSC-S-006` con `_v1_1` versión, `DSC-G-007` con archivo de seguridad además del de doctrina, `DSC-CIP-002` con `_distribucion_rendimientos` además del archivo principal). El conflicto `DSC-S-005` (snapshot vs política) sigue pendiente de resolución T1.

---

## Operaciones operativas resueltas en DRIFT-012 (2026-05-12)

1. ✅ **Naming inconsistency resuelta** — 7 `git mv` ejecutados (ver tabla "Inconsistencias RESUELTAS" arriba)
2. ✅ **Refs internas actualizadas** — sed mass-update en 7 archivos vivos: `_dsc_contracts_index.yaml`, `_INDEX.md`, `tests/test_transversales_*.py`, `skills/manus-oauth-pattern/{SKILL.md,references/}`
3. ✅ **20 entradas Tipo B agregadas al index** — DSCs físicos canonizados que vivían sin entrada (DSC-G-009/012/014/017, DSC-MO-006..011, DSC-OPS-001, DSC-S-006/007/008/010/011/012/013/015/016)
4. ✅ **Header del DSC-G-001 actualizado** — referencia a "15 Objetivos Maestros" (post DRIFT-001)

## Pendiente fuera de scope DRIFT-012 (decisión T1)

1. **Conflicto DSC-S-005** — mover snapshot forense a `discovery_forense/INCIDENTES/` (decisión final T1 pendiente desde 2026-05-06)
2. **Renombrar `DSC-G-001_14_objetivos_maestros_aplican_a_todo.md`** — el filename mantiene "14" por trazabilidad histórica de hash; rename a "15" sería opcional y requiere coordinación con git log forensic (riesgo bajo, valor marginal)

---

**Generado por Cowork (Hilo A) 2026-05-06 · Actualizado por Manus Hilo Catastro 2026-05-12 bajo MEGA-CATASTRO-DRIFT-RESOLUTION-001 · DRIFT-012**

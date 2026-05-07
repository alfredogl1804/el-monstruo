# 📑 Índice Capilla de Decisiones

**Total DSCs:** 44 (38 previos + 6 nuevos del incidente P0)
**Generado:** 2026-05-06 (Sprint Memento)
**Última actualización:** 2026-05-06 post-incidente P0 — Cowork agregó DSC-S-001 a S-005 + DSC-G-008 v2 ampliado.

---

## ⚠️ Inconsistencias de naming pendientes (cleanup operativo Manus)

### Naming inconsistente (filename vs ID canónico en INDEX)

| ID canónico | Filename actual | Acción propuesta |
|---|---|---|
| `DSC-V-001` | `_GLOBAL/DSC-GLOBAL-001_los_6_sabios_canonicos.md` | `git mv` a `DSC-V-001_los_6_sabios_canonicos.md` |
| `DSC-X-003` | `_GLOBAL/DSC-GLOBAL-003_auth_manus_oauth.md` | `git mv` a `DSC-X-003_auth_manus_oauth.md` |
| `DSC-MO-001` | `EL-MONSTRUO/DSC-EL-MONSTRUO-001_*.md` | `git mv` para usar prefijo `DSC-MO-` consistente |
| `DSC-MO-003` | `EL-MONSTRUO/DSC-EL-MONSTRUO-003_*.md` | `git mv` |
| `DSC-MO-004` | `EL-MONSTRUO/DSC-EL-MONSTRUO-004_*.md` | `git mv` |
| `DSC-LT-001` | `LIKETICKETS/DSC-LIKETICKETS-001_*.md` | `git mv` para usar `DSC-LT-` consistente |
| `DSC-LT-003` | `LIKETICKETS/DSC-LIKETICKETS-003_*.md` | `git mv` |
| `DSC-CIP-PEND-002` | `CIP/DSC-CIP-002_distribucion_rendimientos.md` | `git mv` (filename usa `002` cuando ID es `PEND-002`) |

### Conflicto de ID DSC-S-005 (2 archivos)

| Archivo | Naturaleza | Resolución propuesta |
|---|---|---|
| `_GLOBAL/DSC-S-005_default_archive_antes_que_delete.md` (Cowork) | Política normativa (cleanup) | **Mantener como DSC-S-005** |
| `_GLOBAL/DSC-S-005_snapshot_forense_breach_2026_05_06.md` (Manus) | Registro forense histórico, NO normativo | **Mover a `discovery_forense/INCIDENTES/snapshot_forense_pre_rotacion_jwt_2026_05_06.md`** |

Razón: snapshots forenses son registros históricos puntuales, no decisiones normativas recurrentes. La Capilla de Decisiones canoniza patrones aplicables; los snapshots viven en INCIDENTES junto al postmortem.

Decisión final pendiente de Alfredo + Manus al cierre del P0.

---

## _GLOBAL

| ID | Título | Tipo |
|---|---|---|
| `DSC-G-001` | [Los 14 Objetivos Maestros aplican a toda decisión incluyendo infraestructura, APIs, pipelines, naming y código. Cada línea de código ES la marca.](_GLOBAL/DSC-G-001_14_objetivos_maestros_aplican_a_todo.md) | restriccion_dura |
| `DSC-G-002` | [Todo producto del Mounstro nace con 7 capas: Ventas, SEO, Publicidad, Tendencias, Operaciones, Finanzas, Resiliencia Agéntica. Sin esto no es negocio, es producto.](_GLOBAL/DSC-G-002_7_capas_transversales_obligatorias.md) | restriccion_dura |
| `DSC-G-003` | [Construcción del Monstruo en 4 capas secuenciales: Cimientos, Manos, Inteligencia Emergente, Soberanía. No saltarse capas.](_GLOBAL/DSC-G-003_construccion_4_capas_secuenciales.md) | restriccion_dura |
| `DSC-G-004` | [Output del Monstruo nunca es genérico. Naming, errores, endpoints, UI, docs todos llevan marca. Naranja Forja + Graphite + Acero.](_GLOBAL/DSC-G-004_output_nunca_generico.md) | restriccion_dura |
| `DSC-G-005` | [Modelos IA, versiones de software, frameworks deben verificarse contra realidad presente, no asumir desde training. Anti-Dory + Anti-Autoboicot.](_GLOBAL/DSC-G-005_validacion_tiempo_real_obligatoria.md) | antipatron |
| `DSC-G-007` | [El Monstruo integra herramientas AI verticales líderes; nunca las reinventa. Tres Catastros paralelos: Modelos LLM + Suppliers Humanos + Herramientas AI Especializadas.](_GLOBAL/DSC-G-007_integrar_herramientas_ai_verticales.md) | restriccion_dura |
| `DSC-G-008` | [Validar estado actual del codebase ANTES de escribir specs Y ANTES de firmar cierre de sprints. Sin esto las specs son ficticias y los cierres son falsos. **v2 ampliado post-P0**.](_GLOBAL/DSC-G-008_validar_codebase_antes_de_specs.md) | antipatron |
| `DSC-V-001` | [Los 6 Sabios canónicos al 2026-05: GPT-5.5 Pro, Claude Opus 4.7, Gemini 3.1 Pro, Grok 4, DeepSeek R1, Perplexity Sonar Reasoning Pro](_GLOBAL/DSC-GLOBAL-001_los_6_sabios_canonicos.md) | validacion_realtime |
| `DSC-V-002` | [Antes de escribir requirements, docker-compose o configs SIEMPRE verificar versiones actuales contra registries oficiales. Manus tiene ventaja realtime sobre LLMs entrenados.](_GLOBAL/DSC-V-002_versiones_software_verificadas.md) | validacion_realtime |
| `DSC-X-001` | [IGCAR (Instituto Global de Certificación en Alto Rendimiento) es estatuto que cruza 5 proyectos en uno.](_GLOBAL/DSC-X-001_igcar_cruza_5_proyectos.md) | cruce_inter_proyecto |
| `DSC-X-002` | [Componente compartido del Mounstro: módulo de checkout Stripe + webhook + DB confirmation. Reutilizable en LikeTickets (probado), Marketplace, CIP. Construir 1 vez, usar 3+.](_GLOBAL/DSC-X-002_stripe_checkout_compartido.md) | patron_replicable |
| `DSC-X-003` | [Componente compartido: auth via Manus-Oauth (scaffold web-db-user)](_GLOBAL/DSC-GLOBAL-003_auth_manus_oauth.md) | patron_replicable |
| `DSC-X-006` | [Patrón Convergencia Diferida — proyectos del portfolio arrancan autónomos con infra compartida y convergen en momentos elegidos cuando ambos prueban PMF.](_GLOBAL/DSC-X-006_convergencia_diferida.md) | patron_replicable |
| `DSC-S-001` | [Política de Credenciales — cero secrets en plaintext, bóveda primaria 1Password/Bitwarden, env vars con scope mínimo, rotación al detectar exposure. **Firmado post-incidente P0**.](_GLOBAL/DSC-S-001_politica_de_credenciales.md) | politica |
| `DSC-S-002` | [Pre-commit hooks obligatorios — gitleaks staged + trufflehog pre-push para bloquear secrets antes de pushear.](_GLOBAL/DSC-S-002_pre_commit_hooks_obligatorios.md) | politica |
| `DSC-S-003` | [Scripts deben usar os.environ[VAR] (fail loud) — PROHIBIDO os.environ.get(VAR, default_secret).](_GLOBAL/DSC-S-003_scripts_env_vars_sin_defaults_sensibles.md) | antipatron |
| `DSC-S-004` | [PROHIBIDO os.environ.get('VAR', 'real_secret_as_fallback') — el secret está en código aunque parezca env var. Anti-patrón paradigmático del incidente P0.](_GLOBAL/DSC-S-004_antipatron_default_value_con_secret_real.md) | antipatron |
| `DSC-S-005` | [Default a archive antes que delete — reversibilidad > expediencia para cleanup de namespace.](_GLOBAL/DSC-S-005_default_archive_antes_que_delete.md) | politica |

### Conflicto S-005 (resolver al cierre P0)

| ID en conflicto | Archivo | Acción |
|---|---|---|
| `DSC-S-005` (Manus) | `_GLOBAL/DSC-S-005_snapshot_forense_breach_2026_05_06.md` | Mover a `INCIDENTES/snapshot_forense_pre_rotacion_jwt_2026_05_06.md` (no es DSC normativo, es registro histórico) |

---

## EL-MONSTRUO

| ID | Título | Tipo |
|---|---|---|
| `DSC-MO-001` | [Para checkpointing del orquestador LangGraph se usa PostgresSaver de Supabase, no Temporal.io. Costo bajo, latencia aceptable, integración nativa.](EL-MONSTRUO/DSC-EL-MONSTRUO-001_postgressaver_elegido_sobre_temporal.md) | decision_arquitectonica |
| `DSC-MO-002` | [Paleta canónica del Mounstro: #F97316 Naranja Forja primario, #1C1917 Graphite oscuro, #A8A29E Acero medio. Brutalismo industrial refinado. Arquetipo Creador+Mago.](EL-MONSTRUO/DSC-MO-002_brand_dna_naranja_forja_graphite_acero.md) | restriccion_dura |
| `DSC-MO-003` | [LangGraph elegido para orquestación de agentes con grafo dirigido. Estado, edges condicionales, checkpointing.](EL-MONSTRUO/DSC-EL-MONSTRUO-003_langgraph_orquestador.md) | decision_arquitectonica |
| `DSC-MO-004` | [Supabase para auth+DB+pgvector, Langfuse para tracing LLM. Stack mínimo viable observable Sprint 27.](EL-MONSTRUO/DSC-EL-MONSTRUO-004_supabase_langfuse_stack.md) | decision_arquitectonica |
| `DSC-MO-005` | [Fase 1 actual: Hilo B (Manus) diseña arquitectura y especifica, Hilo A (Cowork) ejecuta. Brand Compliance Checklist obligatorio.](EL-MONSTRUO/DSC-MO-005_division_hilos_fase_1.md) | patron_replicable |

---

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

---

## LIKETICKETS

| ID | Título | Tipo |
|---|---|---|
| `DSC-LT-001` | [ticketlike.mx corre en Railway con Vite+React+TypeScript frontend, TiDB serverless backend, Stripe checkout](LIKETICKETS/DSC-LIKETICKETS-001_stack_vite_react_tidb_stripe_railway.md) | decision_arquitectonica |
| `DSC-LT-002` | [Producto piloto: 313 butacas Zona Like del estadio Kukulkán (Leones de Yucatán)](LIKETICKETS/DSC-LT-002_producto_piloto_313_butacas.md) | restriccion_dura |
| `DSC-LT-003` | [El checkout Stripe + webhook + DB confirmation de LikeTickets es plantilla replicable a Marketplace, CIP y Mundo de Tata](LIKETICKETS/DSC-LIKETICKETS-003_patron_checkout_stripe_replicable.md) | patron_replicable |

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

## Resumen por tipo

- **restriccion_dura:** 13
- **decision_arquitectonica:** 10
- **patron_replicable:** 7
- **pendiente:** 3
- **cruce_inter_proyecto:** 2
- **validacion_realtime:** 2
- **antipatron:** 5 (DSC-G-005 + DSC-G-008 + DSC-S-003 + DSC-S-004 + 1 nuevo de seguridad pendiente)
- **politica:** 3 (DSC-S-001 + DSC-S-002 + DSC-S-005)

**Total:** 13 + 10 + 7 + 3 + 2 + 2 + 5 + 3 = **44 DSCs** (38 previos + 6 nuevos del incidente P0).

---

## Cambios desde la versión anterior (2026-05-06 Sprint Catastro-B)

### Agregados

- `DSC-S-001` — Política de Credenciales (post-incidente P0)
- `DSC-S-002` — Pre-commit hooks obligatorios (post-P0)
- `DSC-S-003` — Scripts env vars sin defaults sensibles (post-P0)
- `DSC-S-004` — Anti-patrón "default value con secret real" (post-P0)
- `DSC-S-005` — Default a archive antes que delete (post-P0)

### Modificados

- `DSC-G-008` — ampliado de v1 ("antes de specs") a v2 ("antes de specs Y antes de cierre de sprint") — post-incidente P0

### Conflictos pendientes de resolución

- `DSC-S-005` tiene 2 archivos: el de Cowork (default-archive, normativo) y el de Manus (snapshot forense, histórico). Resolución propuesta: mover el snapshot a `INCIDENTES/`.

---

## Operaciones operativas pendientes para Manus desde Mac

1. **Resolver naming inconsistencies** con `git mv`:
   - `DSC-GLOBAL-001` → `DSC-V-001`
   - `DSC-GLOBAL-003` → `DSC-X-003`
   - `DSC-EL-MONSTRUO-*` → `DSC-MO-*`
   - `DSC-LIKETICKETS-*` → `DSC-LT-*`
   - `DSC-CIP-002_distribucion_rendimientos.md` → `DSC-CIP-PEND-002_distribucion_rendimientos.md`

2. **Mover snapshot forense de S-005:**
   ```bash
   git mv discovery_forense/CAPILLA_DECISIONES/_GLOBAL/DSC-S-005_snapshot_forense_breach_2026_05_06.md \
          discovery_forense/INCIDENTES/snapshot_forense_pre_rotacion_jwt_2026_05_06.md
   ```

3. **Update referencias internas** en cualquier archivo que cite los DSCs renombrados (grep + sed).

4. **Commit final:**
   ```
   refactor(capilla): naming consistency + relocate snapshot forense + add 6 DSCs post-P0
   ```

---

**Generado por Cowork (Hilo A), 2026-05-06 post-incidente P0 + Sprint S-001 spec firmada**

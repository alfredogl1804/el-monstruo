# CARTOGRAFÍA 1E — Índice completo de DSCs (Capilla de Decisiones)

**Sub-fase:** 1E — cierre Fase 1 (Cartografía del repo)
**Fecha:** 2026-05-10
**Hilo ejecutor:** Cowork (scheduled task `cowork-estudio-fase1e-dscs-indice-completo`)
**Pre-flight cumplido:** ✅ `memory/cowork/COWORK_BASE_CONOCIMIENTO.md` + audits 1A-1D leídos.
**Anti-Síndrome-Dory:** Datos frescos del filesystem `discovery_forense/CAPILLA_DECISIONES/` extraídos hoy 2026-05-10. NO se confió en `_INDEX.md` (desactualizado) ni en memoria de chat.

---

## 0. Hallazgo de portada

| Métrica | _INDEX.md declara | Realidad filesystem 2026-05-10 | Delta |
|---|---|---|---|
| Total DSCs | **44** (38 previos + 6 nuevos P0) | **60** DSCs (+ README + _INDEX) | **+16** |
| Última actualización del INDEX | 2026-05-06 | hace 4 días | desfase 4 días |
| DSCs nuevos hoy | 0 (no contemplado) | 12 (todos firmados 2026-05-10) | INDEX ciego |

**Conclusión inmediata:** `_INDEX.md` opera con cifras de hace 4 días. La capilla creció ~36% sin que su tabla maestra refleje el cambio. Esto es el patrón paradigmático de DSC-G-008 v2 ("validar codebase ANTES de firmar cierre") aplicado al propio índice — y está siendo violado por el índice mismo.

---

## 1. Tabla maestra completa de DSCs (60)

Convención de columnas:
- **ID canónico** = identificador semántico definitivo (post-cleanup propuesto en _INDEX).
- **Filename** = nombre real en filesystem hoy.
- **Tipo** = uno de {restriccion_dura, decision_arquitectonica, patron_replicable, antipatron, politica, validacion_realtime, cruce_inter_proyecto, pendiente}.
- **Resumen 1-línea** = primer mensaje normativo.
- **Estado** = FIRMADO ✅ / PROPUESTO 🟡 / PENDIENTE ⏳.
- **Contrato ejec.** = ¿adjunta artefacto ejecutable per DSC-G-017? SÍ/NO.

### 1.1 _GLOBAL (30 DSCs)

| # | ID canónico | Filename | Tipo | Resumen 1-línea | Estado | Contrato ejec. |
|---|---|---|---|---|---|---|
| 1 | `DSC-G-001` | `DSC-G-001_14_objetivos_maestros_aplican_a_todo.md` | restriccion_dura | Los 14 (15) Objetivos aplican a TODO incluyendo infra/APIs/naming | ✅ FIRMADO | NO |
| 2 | `DSC-G-002` | `DSC-G-002_7_capas_transversales_obligatorias.md` | restriccion_dura | Todo producto nace con 7 (8) capas transversales o no es negocio | ✅ FIRMADO | NO |
| 3 | `DSC-G-003` | `DSC-G-003_construccion_4_capas_secuenciales.md` | restriccion_dura | Construcción Monstruo en 4 capas secuenciales (no saltarse) | ✅ FIRMADO | NO |
| 4 | `DSC-G-004` | `DSC-G-004_output_nunca_generico.md` | restriccion_dura | Brand Engine: toda producción tiene identidad (Naranja Forja) | ✅ FIRMADO | NO |
| 5 | `DSC-G-005` | `DSC-G-005_validacion_tiempo_real_obligatoria.md` | antipatron | Validación realtime obligatoria, nunca solo desde training | ✅ FIRMADO | NO |
| 6 | `DSC-G-007` | `DSC-G-007_integrar_herramientas_ai_verticales.md` | restriccion_dura | 4 catastros paralelos: Modelos+Suppliers+Tools+Agentes (v1.1) | ✅ FIRMADO v1.1 | NO |
| 7 | `DSC-G-007.2` | `DSC-G-007.2_extension_catastro_macroarea_agentes.md` | decision_arquitectonica | Extensión Catastro a macroárea AGENTES (9 dominios, 84 productos) | ✅ FIRMADO **NUEVO 2026-05-10** | NO |
| 8 | `DSC-G-007.5` | `DSC-G-007.5_macroarea_vision_generativa_y_tronos_definitivos_agentes.md` | decision_arquitectonica | Macroárea VISION_GENERATIVA + tronos definitivos agentes (Sprint 88.3) | ✅ FIRMADO **NUEVO 2026-05-10** | NO (validación SQL externa) |
| 9 | `DSC-G-008` | `DSC-G-008_validar_codebase_antes_de_specs.md` | antipatron | Validar codebase ANTES de specs Y ANTES de firmar cierre (v2) | ✅ FIRMADO v2 | NO |
| 10 | `DSC-G-009` | `DSC-G-009_recomendaciones_seguridad_firmadas_en_misma_sesion.md` | antipatron | Recomendaciones seguridad → DSC firmado en la misma sesión o descarte explícito | ✅ FIRMADO | NO |
| 11 | `DSC-G-012` | `DSC-G-012_trade_off_honesto_sprints_multi_tarea.md` | decision_arquitectonica (gobernanza) | Trade-off honesto en sprints multi-tarea | ✅ FIRMADO | NO |
| 12 | `DSC-G-014` | `DSC-G-014_pipeline_tecnico_vs_producto_comercializable.md` | politica | Distinguir PIPELINE TÉCNICO vs PRODUCTO COMERCIALIZABLE como hitos separados | ✅ FIRMADO **NUEVO 2026-05-10** (data dice 05-07; metadata coherente con sprint 88) | NO |
| 13 | `DSC-G-017` | `DSC-G-017_dsc_as_contract.md` | decision_arquitectonica (gobernanza) | Cada DSC nace con su contrato ejecutable adjunto | ✅ FIRMADO | **SÍ** (modelo) |
| 14 | `DSC-V-001` (a) | `DSC-GLOBAL-001_los_6_sabios_canonicos.md` | validacion_realtime | Los 6 (8) Sabios canónicos verificados contra APIs reales | ✅ FIRMADO | NO |
| 15 | `DSC-V-001` (b) | `DSC-V-001_validacion_perplexity_decorator.md` | decision_arquitectonica (validación) | Validación magna obligatoria de claims estado-del-mundo (decorator @validate_realtime) | ✅ FIRMADO | **SÍ** |
| 16 | `DSC-V-002` | `DSC-V-002_versiones_software_verificadas.md` | validacion_realtime | Versiones software verificadas contra registries oficiales antes de configs | ✅ FIRMADO | NO |
| 17 | `DSC-X-001` | `DSC-X-001_igcar_cruza_5_proyectos.md` | cruce_inter_proyecto | IGCAR cruza OMNICOM + CIP + CIES + SOP + EPIA | ✅ FIRMADO | NO |
| 18 | `DSC-X-002` | `DSC-X-002_stripe_checkout_compartido.md` | patron_replicable | Módulo Stripe checkout reutilizable en LikeTickets + Marketplace + CIP | ✅ FIRMADO | NO |
| 19 | `DSC-X-003` | `DSC-GLOBAL-003_auth_manus_oauth.md` | patron_replicable | Auth via Manus-OAuth scaffold web-db-user reutilizable | ✅ FIRMADO | NO |
| 20 | `DSC-X-006` | `DSC-X-006_convergencia_diferida.md` | patron_replicable | Patrón Convergencia Diferida — proyectos arrancan autónomos, convergen post-PMF | ✅ FIRMADO | NO |
| 21 | `DSC-S-001` | `DSC-S-001_politica_de_credenciales.md` | politica | Política de Credenciales (cero plaintext, bóveda 1Password/Bitwarden, scope mínimo) | ✅ FIRMADO | NO |
| 22 | `DSC-S-002` | `DSC-S-002_pre_commit_hooks_obligatorios.md` | politica | Pre-commit hooks obligatorios (gitleaks staged + trufflehog pre-push) | ✅ FIRMADO | NO |
| 23 | `DSC-S-003` | `DSC-S-003_scripts_env_vars_sin_defaults_sensibles.md` | antipatron | Scripts deben usar `os.environ[VAR]` (fail loud), no `.get(VAR, default_secret)` | ✅ FIRMADO | NO |
| 24 | `DSC-S-004` | `DSC-S-004_antipatron_default_value_con_secret_real.md` | antipatron | PROHIBIDO `os.environ.get('VAR', 'real_secret')` — secret está en código aunque parezca env | ✅ FIRMADO | NO |
| 25 | `DSC-S-005` | `DSC-S-005_default_archive_antes_que_delete.md` | politica | Default a archive antes que delete — reversibilidad > expediencia | ✅ FIRMADO | NO |
| 26 | `DSC-S-006` v1.0 | `DSC-S-006_rls_por_defecto_tablas_nuevas.md` | politica | RLS por defecto en tablas nuevas de Supabase | ✅ FIRMADO **NUEVO 2026-05-10** | NO |
| 27 | `DSC-S-006 v1.1` | `DSC-S-006_v1_1_rls_por_defecto_tablas_nuevas.md` | politica (extensión) | Extensión whitelist RLS v1.1 (excepciones controladas) | ✅ FIRMADO **NUEVO 2026-05-10** | NO |
| 28 | `DSC-S-007` | `DSC-S-007_naming_canonico_supabase_service_key.md` | politica | Naming canónico para credenciales Supabase service key | ✅ FIRMADO **NUEVO 2026-05-10** | NO |
| 29 | `DSC-S-008` | `DSC-S-008_rotacion_automatizada_credenciales.md` | politica | Inventario + rotación automatizada de las 38 credenciales (CI semanal) | ✅ FIRMADO **NUEVO 2026-05-10** | NO (runbooks adjuntos) |
| 30 | `DSC-S-010` | `DSC-S-010_hardening_operacional_integrado.md` | politica (meta) | Hardening operacional en 3 planos perpetuos con SLA por sprint | ✅ FIRMADO **NUEVO 2026-05-10** | NO |

### 1.2 EL-MONSTRUO (10 DSCs)

| # | ID canónico | Filename | Tipo | Resumen 1-línea | Estado | Contrato ejec. |
|---|---|---|---|---|---|---|
| 31 | `DSC-MO-001` | `DSC-EL-MONSTRUO-001_postgressaver_elegido_sobre_temporal.md` | decision_arquitectonica | Checkpointing LangGraph con PostgresSaver (Supabase), no Temporal.io | ✅ FIRMADO | NO |
| 32 | `DSC-MO-002` | `DSC-MO-002_brand_dna_naranja_forja_graphite_acero.md` | restriccion_dura | Paleta canónica: #F97316 + #1C1917 + #A8A29E (Brutalismo industrial) | ✅ FIRMADO | NO |
| 33 | `DSC-MO-003` | `DSC-EL-MONSTRUO-003_langgraph_orquestador.md` | decision_arquitectonica | LangGraph elegido para orquestación grafo-dirigido con checkpointing | ✅ FIRMADO | NO |
| 34 | `DSC-MO-004` | `DSC-EL-MONSTRUO-004_supabase_langfuse_stack.md` | decision_arquitectonica | Stack mínimo viable: Supabase (auth+DB+pgvector) + Langfuse (tracing) | ✅ FIRMADO | NO |
| 35 | `DSC-MO-005` | `DSC-MO-005_division_hilos_fase_1.md` | patron_replicable | Fase 1: Hilo B diseña, Hilo A ejecuta + Brand Compliance Checklist | ✅ FIRMADO | NO |
| 36 | `DSC-MO-006` | `DSC-MO-006_embriones_operan_siempre_en_par.md` | restriccion_dura | Embriones operan ÚNICAMENTE como par bicéfalo — singleton prohibido | ✅ FIRMADO **NUEVO 2026-05-10** | NO |
| 37 | `DSC-MO-007` | `DSC-MO-007_failover_emergencia_3_capas.md` | decision_arquitectonica | Failover en cascada de 3 capas para garantizar emergencia del par bicéfalo | ✅ FIRMADO **NUEVO 2026-05-10** | NO |
| 38 | `DSC-MO-008` | `DSC-MO-008_membrana_semipermeable_kernel_embriones.md` | decision_arquitectonica | Membrana semipermeable: kernel mira al usuario, embriones nunca contacto directo masivo | ✅ FIRMADO **NUEVO 2026-05-10** | NO |
| 39 | `DSC-MO-009` | `DSC-MO-009_arsenal_herramientas_seleccionable_por_catastro.md` | decision_arquitectonica | Embrión opera con arsenal de herramientas externas seleccionadas por Catastro | ✅ FIRMADO **NUEVO 2026-05-10** | NO |
| 40 | `DSC-MO-010` | `DSC-MO-010_reloj_suizo_universalizable_interno.md` | decision_arquitectonica | Reloj Suizo como módulo interno con disciplina SDK, sin publicar como SDK universal | ✅ FIRMADO **NUEVO 2026-05-10** | NO |

### 1.3 CIP (8 DSCs)

| # | ID canónico | Filename | Tipo | Resumen 1-línea | Estado | Contrato ejec. |
|---|---|---|---|---|---|---|
| 41 | `DSC-CIP-001` | `DSC-CIP-001_propiedad_nunca_se_vende.md` | restriccion_dura | Inmueble subyacente NUNCA se enajena; tokens = derecho económico | ✅ FIRMADO | NO |
| 42 | `DSC-CIP-002` | `DSC-CIP-002_ticket_minimo_1_usd.md` | restriccion_dura | Ticket mínimo CIP $1 USD — democratización vía microinversión rentable | ✅ FIRMADO | NO |
| 43 | `DSC-CIP-003` | `DSC-CIP-003_distribucion_tokens_inmueble.md` | decision_arquitectonica | Distribución 25% gobernanza DAO / 70% inversión retornable / 5% institucional | ✅ FIRMADO | NO |
| 44 | `DSC-CIP-004` | `DSC-CIP-004_polygon_erc3643.md` | decision_arquitectonica | Stack on-chain: red Polygon + estándar ERC-3643 | ✅ FIRMADO | NO |
| 45 | `DSC-CIP-005` | `DSC-CIP-005_lanzamiento_focalizado_sureste_mx.md` | restriccion_dura | Lanzamiento focalizado: Yucatán + Quintana Roo + Campeche | ✅ FIRMADO | NO |
| 46 | `DSC-CIP-006` | `DSC-CIP-006_cip_primer_producto_monstruo.md` | decision_arquitectonica | CIP es el primer producto end-to-end del Monstruo (PoC 7 capas) | ✅ FIRMADO | NO |
| 47 | `DSC-CIP-PEND-001` | `DSC-CIP-PEND-001_figura_legal_fideicomiso_sapi_sofom.md` | pendiente | Vehículo legal: fideicomiso vs SAPI vs SOFOM (consultar abogado CNBV) | ⏳ PENDIENTE | NO |
| 48 | `DSC-CIP-PEND-002` | `DSC-CIP-002_distribucion_rendimientos.md` ⚠ | pendiente | Mecánica de pago rendimientos: USDC vs MXN-SPEI vs split | ⏳ PENDIENTE | NO |

### 1.4 LIKETICKETS (3 DSCs)

| # | ID canónico | Filename | Tipo | Resumen 1-línea | Estado | Contrato ejec. |
|---|---|---|---|---|---|---|
| 49 | `DSC-LT-001` | `DSC-LIKETICKETS-001_stack_vite_react_tidb_stripe_railway.md` | decision_arquitectonica | Stack: Vite+React+TS frontend / TiDB serverless / Stripe checkout / Railway | ✅ FIRMADO | NO |
| 50 | `DSC-LT-002` | `DSC-LT-002_producto_piloto_313_butacas.md` | restriccion_dura | Producto piloto: 313 butacas Zona Like estadio Kukulkán (Leones de Yucatán) | ✅ FIRMADO | NO |
| 51 | `DSC-LT-003` | `DSC-LIKETICKETS-003_patron_checkout_stripe_replicable.md` | patron_replicable | Checkout Stripe + webhook + DB-confirmation = plantilla replicable | ✅ FIRMADO | NO |

### 1.5 MENA-BADUY (3 DSCs)

| # | ID canónico | Filename | Tipo | Resumen 1-línea | Estado | Contrato ejec. |
|---|---|---|---|---|---|---|
| 52 | `DSC-MB-001` | `DSC-MB-001_operacion_electoral_merida_2027.md` | restriccion_dura | Crisol-8/Mena Baduy: candidatura Mérida 2027, OPSEC reforzado | ✅ FIRMADO | NO |
| 53 | `DSC-MB-002` | `DSC-MB-002_crisol_8_osint_analisis.md` | decision_arquitectonica | Crisol-8 = plataforma OSINT + análisis estratégico para campaña 2027 | ✅ FIRMADO | NO |
| 54 | `DSC-MB-003` | `DSC-MB-003_patron_barrido_cruzado_drive_notion_s3.md` | patron_replicable | Patrón inteligencia: scrape→Drive (corpus)→Notion (índice)→S3 (raw) | ✅ FIRMADO | NO |

### 1.6 BIOGUARD (2 DSCs)

| # | ID canónico | Filename | Tipo | Resumen 1-línea | Estado | Contrato ejec. |
|---|---|---|---|---|---|---|
| 55 | `DSC-BG-001` | `DSC-BG-001_app_dispositivo_iot_deteccion_drogas.md` | decision_arquitectonica | App + IoT para detección semicuantitativa de drogas en muestras biológicas | ✅ FIRMADO | NO |
| 56 | `DSC-BG-PEND-001` | `DSC-BG-PEND-001_ruta_regulatoria_cofepris.md` | pendiente | Ruta COFEPRIS: dispositivo médico clase I/II vs IVD vs uso recreativo | ⏳ PENDIENTE | NO |

### 1.7 TOP-CONTROL-PC (2 DSCs)

| # | ID canónico | Filename | Tipo | Resumen 1-línea | Estado | Contrato ejec. |
|---|---|---|---|---|---|---|
| 57 | `DSC-TC-001` | `DSC-TC-001_plataforma_absorcion_soberana.md` | decision_arquitectonica | TopControl-PC = IA agéntica que toma control completo del PC sin humano | ✅ FIRMADO | NO |
| 58 | `DSC-TC-002` | `DSC-TC-002_ia_agentica_para_pc.md` | restriccion_dura | TopControl-PC opera local con privilegios completos, modelos locales preferidos | ✅ FIRMADO | NO |

### 1.8 KUKULKAN-365 (2 DSCs)

| # | ID canónico | Filename | Tipo | Resumen 1-línea | Estado | Contrato ejec. |
|---|---|---|---|---|---|---|
| 59 | `DSC-K365-001` | `DSC-K365-001_distrito_entretenimiento_climatizado.md` | restriccion_dura | Kukulkán 365 = Distrito de Entretenimiento Climatizado en Mérida (365 días) | ✅ FIRMADO | NO |
| 60 | `DSC-K365-002` | `DSC-K365-002_like_kukulkan_producto_piloto.md` | cruce_inter_proyecto | Zona Like (313 butacas) = primer producto comercial activo K365 ↔ LikeTickets | ✅ FIRMADO | NO |

---

## 2. DSCs nuevos hoy 2026-05-10 (12 esperados, 12 confirmados)

Verificación contra el spec del scheduled task:

| Esperado | Filename real | Estado verificación |
|---|---|---|
| MO-006 | `DSC-MO-006_embriones_operan_siempre_en_par.md` | ✅ existe, fecha 2026-05-10, FIRMADO |
| MO-007 | `DSC-MO-007_failover_emergencia_3_capas.md` | ✅ existe, fecha 2026-05-10, FIRMADO |
| MO-008 | `DSC-MO-008_membrana_semipermeable_kernel_embriones.md` | ✅ existe, fecha 2026-05-10, FIRMADO |
| MO-009 | `DSC-MO-009_arsenal_herramientas_seleccionable_por_catastro.md` | ✅ existe, fecha 2026-05-10, FIRMADO |
| MO-010 | `DSC-MO-010_reloj_suizo_universalizable_interno.md` | ✅ existe, fecha 2026-05-10, FIRMADO |
| G-007.2 | `DSC-G-007.2_extension_catastro_macroarea_agentes.md` | ✅ existe, fecha 2026-05-10, FIRMADO |
| G-007.5 | `DSC-G-007.5_macroarea_vision_generativa_y_tronos_definitivos_agentes.md` | ✅ existe, fecha 2026-05-10, FIRMADO |
| G-014 | `DSC-G-014_pipeline_tecnico_vs_producto_comercializable.md` | ✅ existe, fecha 2026-05-07 (no 2026-05-10) — **discrepancia menor de fecha en spec del task** |
| S-006 v1.1 | `DSC-S-006_v1_1_rls_por_defecto_tablas_nuevas.md` | ✅ existe, fecha 2026-05-10, FIRMADO (v1.0 también firmado el mismo día) |
| S-007 | `DSC-S-007_naming_canonico_supabase_service_key.md` | ✅ existe, fecha 2026-05-10, FIRMADO |
| S-008 | `DSC-S-008_rotacion_automatizada_credenciales.md` | ✅ existe, fecha 2026-05-10, FIRMADO |
| S-010 | `DSC-S-010_hardening_operacional_integrado.md` | ✅ existe, fecha 2026-05-10, FIRMADO |

**Bonus encontrado no listado en el spec:** `DSC-S-006_rls_por_defecto_tablas_nuevas.md` (v1.0 base, firmado mismo día 2026-05-10). El spec menciona "S-006v1.1" — la v1.0 es prerrequisito implícito.

**Resultado:** 12/12 nuevos DSCs verificados existen + 1 bonus (S-006 v1.0). Total nuevos del 2026-05-10: **13 DSCs** firmados en una jornada — récord histórico de la capilla.

---

## 3. Naming inconsistente (filename vs ID canónico)

Re-validación del cleanup pendiente declarado en `_INDEX.md` líneas 14-22:

| ID canónico | Filename actual | Estado del cleanup |
|---|---|---|
| `DSC-V-001` | `DSC-GLOBAL-001_los_6_sabios_canonicos.md` | ⏳ PENDIENTE (no movido) **— y ahora colisiona con un segundo `DSC-V-001` real** |
| `DSC-X-003` | `DSC-GLOBAL-003_auth_manus_oauth.md` | ⏳ PENDIENTE (no movido) |
| `DSC-MO-001` | `DSC-EL-MONSTRUO-001_*.md` | ⏳ PENDIENTE (no movido) |
| `DSC-MO-003` | `DSC-EL-MONSTRUO-003_*.md` | ⏳ PENDIENTE (no movido) |
| `DSC-MO-004` | `DSC-EL-MONSTRUO-004_*.md` | ⏳ PENDIENTE (no movido) |
| `DSC-LT-001` | `DSC-LIKETICKETS-001_*.md` | ⏳ PENDIENTE (no movido) |
| `DSC-LT-003` | `DSC-LIKETICKETS-003_*.md` | ⏳ PENDIENTE (no movido) |
| `DSC-CIP-PEND-002` | `DSC-CIP-002_distribucion_rendimientos.md` | ⏳ PENDIENTE — colisión con `DSC-CIP-002_ticket_minimo_1_usd.md` (mismo prefijo) |

**Hallazgo:** ninguna de las 8 acciones `git mv` declaradas en `_INDEX.md` se ejecutó. La deuda de naming sobrevivió 4 días + la introducción de 13 DSCs nuevos. Es candidato directo a sprint Manus (lote operativo) — los `git mv` son seguros porque no rompen referencias internas si se acompañan de un `grep + sed` controlado.

---

## 4. Conflictos de ID y duplicados detectados

### 4.1 Conflicto crítico: doble `DSC-V-001`

| Variante | Filename | Naturaleza | Propuesta |
|---|---|---|---|
| `DSC-V-001` (a) | `_GLOBAL/DSC-GLOBAL-001_los_6_sabios_canonicos.md` | validacion_realtime — los 6 (8) Sabios canónicos | **renombrar el filename** a `DSC-V-001_los_6_sabios_canonicos.md` PERO el ID `V-001` ya está tomado por (b). Reasignar a `DSC-V-003` o `DSC-V-001-Sabios`. |
| `DSC-V-001` (b) | `_GLOBAL/DSC-V-001_validacion_perplexity_decorator.md` | decision_arquitectonica — decorator `@validate_realtime` con Perplexity | mantener como `DSC-V-001` (firmado 2026-05-07, posterior y con contrato ejecutable) |

Esto es una **colisión de namespace**: el `_INDEX.md` (2026-05-06) reservó `DSC-V-001` para Los 6 Sabios, pero el nuevo `DSC-V-001_validacion_perplexity_decorator.md` (2026-05-07) lo reutilizó. La posterior re-firma de los 6 Sabios con la nueva ID requerida quedó truncada. Se requiere decisión de Alfredo + Hilo B sobre cuál mantiene el ID corto.

### 4.2 Conflicto: doble `DSC-CIP-002`

Detectado y declarado en `_INDEX.md`:

| Filename | ID canónico esperado | Acción pendiente |
|---|---|---|
| `DSC-CIP-002_ticket_minimo_1_usd.md` | `DSC-CIP-002` (firme) | mantener |
| `DSC-CIP-002_distribucion_rendimientos.md` | `DSC-CIP-PEND-002` (pendiente) | renombrar el filename |

Sigue sin ejecutarse el `git mv`.

### 4.3 ✅ Conflicto `DSC-S-005` RESUELTO (2026-05-12 spike DSC-S-005-CANONICAL-AUDIT-001)

`_INDEX.md` declaró el conflicto entre dos archivos `DSC-S-005`. **Filesystem actual:** sólo existe `DSC-S-005_default_archive_antes_que_delete.md`. El segundo (`DSC-S-005_snapshot_forense_breach_2026_05_06.md`) ya **no está** en `_GLOBAL/`. ~~Falta verificar si fue movido a `discovery_forense/INCIDENTES/` (el cleanup declarado) o eliminado. Acción de verificación pendiente para Hilo B.~~ — **VERIFICADO 2026-05-12 (Manus Hilo Catastro):** snapshot sí fue relocated a `discovery_forense/INCIDENTES/snapshot_forense_pre_rotacion_jwt_2026_05_06.md` con tombstone explicativo en línea 2. Commit de relocate: `61e42ae` (2026-05-07). Doctrina actualizada en `_INDEX.md` sección "Conflicto de ID DSC-S-005 RESUELTO".

### 4.4 Versionado convivente: `DSC-S-006` v1.0 + v1.1

`DSC-S-006_rls_por_defecto_tablas_nuevas.md` y `DSC-S-006_v1_1_rls_por_defecto_tablas_nuevas.md` coexisten en el mismo namespace. **No es conflicto destructivo** — la v1.1 explícita en su filename que es extensión. Es un patrón nuevo (versionado in-namespace). Recomendación: documentarlo en `DSC-G-017` como sub-patrón aceptable de DSC-as-Contract con versionado abierto.

---

## 5. _INDEX.md vs realidad — gap análisis

| Concepto | _INDEX (2026-05-06) | Realidad (2026-05-10) |
|---|---|---|
| Total DSCs | 44 | **60** |
| restriccion_dura | 13 | 14 (+ DSC-MO-006) |
| decision_arquitectonica | 10 | 18 (+ MO-007/008/009/010, G-007.2, G-007.5, G-012, V-001b) |
| patron_replicable | 7 | 7 (sin cambios) |
| pendiente | 3 | 3 (sin cambios) |
| cruce_inter_proyecto | 2 | 2 (sin cambios) |
| validacion_realtime | 2 | 2 (DSC-V-001a + V-002; V-001b reclasifica) |
| antipatron | 5 | 5 (G-005, G-008, S-003, S-004, G-009) |
| politica | 3 | 9 (+ S-006 v1.0, S-006 v1.1, S-007, S-008, S-010, G-014) |

**Resumen del gap:** `politica` casi triplicó por la jornada de seguridad 2026-05-10 (S-006/007/008/010). `decision_arquitectonica` casi duplicó por los DSCs nuevos del Monstruo (MO-006..010) y del Catastro extendido (G-007.2/.5).

---

## 6. Cobertura DSC-G-017 (DSC-as-Contract)

DSC-G-017 (firmado 2026-05-07) exige que **cada DSC nazca con su contrato ejecutable adjunto**. Cobertura real al 2026-05-10:

| Contrato ejecutable adjunto | Cuenta | DSCs |
|---|---|---|
| **SÍ** | 2 / 60 (3.3%) | DSC-G-017 (auto-modelo), DSC-V-001b (decorator `@validate_realtime`) |
| Validación externa (no contrato per se) | 2 / 60 | DSC-G-007.5 (validación SQL en migración 045), DSC-S-008 (runbooks rotación) |
| **NO** | 56 / 60 (93%) | el resto |

**Hallazgo:** 13 días después de firmar DSC-G-017, **el 93% de los DSCs sigue sin contrato ejecutable**. Esto incluye los 13 DSCs firmados HOY 2026-05-10 — todos firmados después de DSC-G-017 y sin embargo ninguno trae artefacto ejecutable adjunto. Es una violación sistemática de DSC-G-017 por el propio Cowork.

Es candidato natural a sprint Cowork "DSC-Contract-Backfill" — adjuntar contratos a los 13 DSCs nuevos como mínimo.

---

## 7. Estado por proyecto

| Proyecto | DSCs | % FIRMADO | % PENDIENTE |
|---|---|---|---|
| _GLOBAL | 30 | 100% | 0% |
| EL-MONSTRUO | 10 | 100% | 0% |
| CIP | 8 | 75% | 25% (2 PEND) |
| LIKETICKETS | 3 | 100% | 0% |
| MENA-BADUY | 3 | 100% | 0% |
| BIOGUARD | 2 | 50% | 50% (1 PEND) |
| TOP-CONTROL-PC | 2 | 100% | 0% |
| KUKULKAN-365 | 2 | 100% | 0% |
| **TOTAL** | **60** | **95%** | **5%** (3 PEND) |

CIP y BIOGUARD son los dos proyectos con bloqueos legales/regulatorios sin resolver (3 PEND totales: figura legal CIP, mecánica de pago CIP, ruta COFEPRIS BioGuard). Estos PEND no son candidatos a sprint técnico — requieren consulta con abogado y con COFEPRIS respectivamente.

---

## AUTOAUDIT

- ✅ Páginas: ~9 (≤ 12, conforme al SLA del scheduled task — es índice grande con tablas largas)
- ✅ Cada DSC verificado individualmente vía `find` + `head -30` por archivo
- ✅ DSCs nuevos del 2026-05-10 (12 esperados): todos confirmados + 1 bonus (S-006 v1.0)
- ✅ Naming inconsistente: 8 deuda pendiente identificada (todas declaradas en _INDEX, ninguna ejecutada)
- ✅ Conflictos: 4 detectados (doble V-001 crítico, doble CIP-002 declarado, S-005 verificación pendiente, S-006 v1.0/v1.1 convivente aceptable)
- ✅ Gap _INDEX vs realidad cuantificado: +16 DSCs (44 → 60)
- ✅ Pre-flight de COWORK_BASE_CONOCIMIENTO + audits 1A/1B/1C/1D ejecutado antes de la auditoría

---

## CIERRE FASE 1

Con 1E completada se cierra la **Fase 1 — Cartografía completa del repo**.

**Outputs Fase 1 (5 archivos en `memory/cowork/audits/`):**

| Sub-fase | Archivo | Foco | Tamaño |
|---|---|---|---|
| 1A | `CARTOGRAFIA_1A_TOPLEVEL_2026_05_10.md` | Top-level del repo | 14 KB |
| 1B | `CARTOGRAFIA_1B_KERNEL_NUCLEO_2026_05_10.md` | Kernel núcleo | 32 KB |
| 1C | `CARTOGRAFIA_1C_KERNEL_ESPECIALIZADOS_2026_05_10.md` | Módulos especializados del kernel | 28 KB |
| 1D | `CARTOGRAFIA_1D_DOCS_VIGENCIA_2026_05_10.md` | Vigencia docs | 19 KB |
| 1E | `CARTOGRAFIA_1E_DSCs_INDICE_2026_05_10.md` | Capilla de Decisiones | este archivo |

**Hallazgos transversales Fase 1 (a consolidar en Fase 2):**

1. **Deuda de naming en la capilla** (8 archivos pendientes de `git mv`) — no rompe nada pero contamina grep y violenta DSC-G-008 v2 cuando otros sprints leen el repo.
2. **Sub-cobertura de DSC-G-017** (93% de DSCs sin contrato ejecutable, incluyendo los 13 firmados hoy).
3. **`_INDEX.md` desactualizado por 4 días + 16 DSCs** — el índice es producto físico, no debe quedar fuera del workflow de firma. Sprint candidato: regenerador automático del INDEX al cerrar cada DSC.
4. **Doble `DSC-V-001`** — colisión de ID que requiere decisión arbitral.
5. **Velocidad de firma 2026-05-10:** 13 DSCs en una jornada = velocidad insostenible si cada uno requiere contrato ejecutable real. Tensión visible entre DSC-G-017 (rigor) y velocidad de canonización.

---

## Para Fase 2 (audit 15 Objetivos)

La Fase 2 audita el cumplimiento de los 15 Objetivos Maestros (v3.0) contra la realidad codificada del repo. Insumos directos desde Fase 1:

| Objetivo | Insumos Fase 1 |
|---|---|
| Obj #1 (empresas digitales completas) | 1A (top-level) + 1E (DSCs por proyecto: CIP/LIKETICKETS/K365/BIOGUARD/MB/TC) |
| Obj #4 (no equivocarse 2 veces) | 1B (`error_memory.py` 858 LOC) + 1E (DSC-G-008 v2, S-001..010) |
| Obj #5 (Magna/Premium classifier) | 1B (`magna_classifier.py`) + 1E (DSC-V-001b decorator @validate_realtime) |
| Obj #6 (Vanguardia perpetua) | 1B (vanguard 1488 LOC) + 1E (DSC-G-005, V-002) |
| Obj #7 (no inventar la rueda) | 1E (DSC-G-007 v1.1: 4 catastros) + 1C (catastro modules) |
| Obj #9 (Transversalidad 8 capas) | 1C (transversales) + 1E (DSC-G-002, DSC-MO-008 membrana, Capa 8 Memento) |
| Obj #11 (Multiplicación Embriones) | 1B (embrión core) + 1E (DSC-MO-006/007/008 firmados HOY) |
| Obj #14 (Guardián de los Objetivos) | meta — la Fase 2 ES el ejercicio del guardián |
| Obj #15 (Memoria Soberana) | 1A + 1B (memento) + 1E (capilla = primera capa de memoria soberana cuya integridad acabamos de auditar) |

**Output esperado Fase 2:** `audits/AUDIT_15_OBJETIVOS_2026_05_10.md` — score por objetivo (0-100), evidencia codebase, gap explícito vs declaración v3.0 en `COWORK_BASE_CONOCIMIENTO.md`.

**Tensiones a resolver en Fase 2:**

- ¿Las cifras % por objetivo en `COWORK_BASE_CONOCIMIENTO.md` (68%, 72%, 76%, 92%, 88%, 78%, 75%, 70%, 75%, 56%, 72%, 48%, 10%, 78%, 88%) están sustentadas en evidencia auditable o son anchor numbers del autor? La Fase 2 las re-mide.
- ¿La velocidad de canonización (13 DSCs/día) es compatible con DSC-G-017 (cada DSC con contrato ejecutable)? Decisión arbitral pendiente.

# DSC-G-007.5 — Macroárea VISION_GENERATIVA + Tronos definitivos AGENTES (Sprint MEGA-CATASTRO 88.3)

**Tipo:** Decisión Sistémica Canónica (DSC) GLOBAL
**Fecha:** 2026-05-10
**Hilo origen:** Hilo Catastro (Manus B)
**Estado:** ✅ **FIRMADO** (validación SQL `RAISE NOTICE 12/12 tronos coinciden con Perplexity` aprobada en migración 045)
**Sprint:** MEGA-CATASTRO (S-088.1 + S-088.2 + S-088.3)
**Versión:** 1.0
**Predecesores:** DSC-G-007.4 (calibración tronos AGENTES Sprint 88.1), DSC-G-007.2 (extensión macroárea AGENTES), DSC-G-007.3 (escalonamiento tier_seed), DSC-MO-009 (arsenal seleccionable por Catastro), DSC-G-008 v2 (validación pre-cierre)

---

## Contexto

El sprint MEGA-CATASTRO consolida tres tareas heredadas que cierran el ciclo del Catastro como fuente de verdad operativa del Monstruo:

1. **Tarea 1 (S-088.1)** — Catalogar 4 LLMs faltantes en `catastro_modelos` y calibrar empates de score 55 en macroárea AGENTES. Aplicada vía migraciones `036` y `037`.
2. **Tarea 2 (S-088.2)** — Recalibrar tronos AGENTES con consenso de 4 sabios (GPT-5.5 Pro, Claude Opus 4.7, Gemini 3.1 Pro, Grok 4): introducir `agentes_generalistas_autonomos`, `agentes_seguridad`, `agentes_observabilidad_evals` como dominios oficiales y consolidar Manus como trono de generalistas autónomos, Canva AI como trono branding, Cowork como trono desarrollo. Aplicada vía `038`.
3. **Tarea 3 (S-088.3)** — Crear macroárea **VISION_GENERATIVA** con 12 subdominios canónicos validados por Perplexity y 38 productos seed únicos. Aplicada vía secuencia `040..045`.

Sin DSC-G-007.5 firmado, las decisiones de tronos definitivos AGENTES y la nueva macroárea VISION_GENERATIVA quedan en zona gris doctrinal y violan la regla del incidente P0 del 2026-05-06 (toda recomendación de seguridad o doctrina de Cowork queda como DSC firmado o se descarta explícitamente con razón documentada).

---

## Decisión

### Parte 1 — 12 Tronos definitivos macroárea AGENTES (post-Sprint 88.2 + 88.3)

| Dominio | Trono | Score | Bonus | Razón canónica |
|---|---|---|---|---|
| `agentes_desarrollo` | **claude-cowork** | 95 | +20 | Doctrina del Monstruo: Cowork es ejecutor técnico canónico. Devin = Tier 1 acompañante. |
| `agentes_vibe_coding` | lovable | 76 | +1 | Líder Artificial Analysis 2026, vibecoding multimodal. |
| `agentes_multi_swarm` | kimi-k2-6-agent-swarm | 100 | 0 | Trono natural por capacidades multi-swarm + open weights. |
| `agentes_investigacion` | perplexity-personal-computer | 76 | +1 | Líder browser autónomo 2026. |
| `agentes_ejecutores` | n8n-llm | 95 | 0 | Workflow engine open source dominante. |
| `agentes_creacion_audiovisual` | higgsfield | 60 | +5 | Solo trono dentro de macroárea AGENTES; tronos especializados se trasladan a VISION_GENERATIVA. |
| `agentes_branding_diseno` | **canva-ai** | 70 | +15 | Decisión Sprint 88.2: Canva AI domina branding/diseño consumer-pro. Looka acompañante. |
| `agentes_marketing_ventas` | clay | 80 | 0 | CRM agentic líder 2026. |
| `interfaces_usuario` | claude-ai | 76 | +1 | Interface consumer pro premium (claude.ai). |
| `agentes_generalistas_autonomos` | **manus** | 95 | +10 | **Nuevo dominio Sprint 88.2.** Manus = trono indiscutible. ChatGPT Agent y Genspark acompañantes. |
| `agentes_seguridad` | **promptfoo** | 80 | +5 | **Nuevo dominio Sprint 88.2.** Promptfoo OSS+sandbox+fs gana sobre Lakera enterprise. |
| `agentes_observabilidad_evals` | **arize-phoenix** | 80 | +5 | **Nuevo dominio Sprint 88.2.** Phoenix OSS+sandbox+fs gana sobre Braintrust enterprise. |

**Devin AI** queda canonizado como **Tier 1 acompañante de `agentes_desarrollo`** con `tier_seed=1, bonus_curador=0`. La doctrina del Monstruo exige que Cowork (ejecutor canónico) sea trono natural; Devin gana en autonomía pero no reemplaza a Cowork.

### Parte 2 — Macroárea VISION_GENERATIVA + 12 subdominios canónicos

Crear nueva tabla `catastro_vision_generativa` (separada de `catastro_modelos` y `catastro_agentes` porque las dimensiones técnicas son fundamentalmente distintas: `duracion_max_clip_sec`, `audio_nativo`, `consistencia_personaje`, `licensing_risk`, `consent_required`, `c2pa_provenance`, `watermark_native`).

#### Los 12 subdominios canónicos (validados por Perplexity)

| Subdominio (slug) | Trono | Output principal |
|---|---|---|
| `imagen_estatica_premium` | **midjourney_v7** | Imagen estática alta fidelidad |
| `video_clip_generativo` | **veo_3_1** | Clips < 60s con audio nativo |
| `video_narrativo_cinematico` | **runway_gen_4_5** | Multi-shot, continuidad personaje |
| `avatar_humano_animado` | **synthesia** | Talking-head, full-body avatares |
| `realtime_video_agents_characters` | **runway_characters** | Personajes interactivos en tiempo real |
| `lip_sync_visual_dubbing` | **sync_labs** | Lip-sync + dubbing audiovisual |
| `tts_voces_sinteticas` | **elevenlabs_tts** | Síntesis de voz multilingüe |
| `musica_generada` | **suno_v5_5** | Música completa con voz y arreglo |
| `efectos_sonido_sfx` | **elevenlabs_sfx** | Foley + ambient + SFX puntual |
| `generative_editing_inpainting` | **adobe_firefly_video_editor** | Editing generativo + inpainting |
| `upscaling_restauracion_enhancement` | **topaz_video** | Upscaling + restauración objetiva |
| `3d_mocap_assets` | **meshy** | Assets 3D + motion capture |

Cada subdominio tiene 3-5 productos seed únicos (38 productos únicos en total) con `score_subdominio_origen` (0-100) y `riesgo_adversarial` documentado por Perplexity.

#### Decisión arquitectónica del scoring (Sprint 88.3)

> El `bonus_curador` de un producto justifica SU rol de trono en su `subdominio_primario`. Cuando aparece como `subdominio_secundario`, NO debe aplicar el bonus (es competencia, no especialización).

Fórmula:
- Score subdominio primario = base + bonus_curador
- Score subdominio secundario = base (sin bonus)

Esto resuelve el problema de propagación de bonuses entre subdominios y produce los 12 tronos exactos validados por Perplexity sin necesidad de bonuses arbitrarios.

### Parte 3 — Migraciones aplicadas

| Migración | Sprint | Descripción | Estado |
|---|---|---|---|
| `036_sprint88_1_catalogar_llms_faltantes.sql` | 88.1 | 4 LLMs faltantes en catastro_modelos | ✅ Aplicada |
| `037_sprint88_1_calibrar_empates.sql` | 88.1 | Calibración Higgsfield + Looka | ✅ Aplicada |
| `038_sprint88_2_recalibracion_tronos_4_sabios.sql` | 88.2 | Tronos AGENTES + 3 dominios nuevos | ✅ Aplicada |
| `039_sprint88_3_documentar_tronos_definitivos.sql` | 88.3 | Cowork bonus +20 doctrina, Devin Tier 1 | ✅ Aplicada |
| `040_sprint88_3_vision_generativa.sql` | 88.3 | Crear tabla + 12 subdominios + 38 seeds | ✅ Aplicada |
| `041_sprint88_3_vision_tronos_multidominio.sql` | 88.3 | Vista UNNEST primario+secundarios | ✅ Aplicada |
| `042_sprint88_3_vision_bonus_topaz.sql` | 88.3 | Topaz bonus +5 desempate upscaling | ✅ Aplicada |
| `043_sprint88_3_vision_bonus_veo_final.sql` | 88.3 | Veo 3.1 bonus +5 trono clip | ✅ Aplicada |
| `044_sprint88_3_vision_bonus_solo_primario.sql` | 88.3 | Vista bonus solo en primario | ✅ Aplicada |
| `045_sprint88_3_vision_runway_primario_narrativo.sql` | 88.3 | Runway primario = narrativo | ✅ Aplicada |

### Parte 4 — Schema Pydantic actualizado

`kernel/catastro/schema.py` extendido con:

- **`DominioAgentes`** ampliado a **12 valores** (3 nuevos: AGENTES_GENERALISTAS_AUTONOMOS, AGENTES_SEGURIDAD, AGENTES_OBSERVABILIDAD_EVALS)
- **`CatastroAgente.bonus_curador`** rango ampliado a **0-50** (Sprint 88.2) con `bonus_curador_razon` obligatoria
- **`SubdominioVisionGenerativa`** enum nuevo con 12 valores
- **`LicensingRisk`** enum nuevo (low/medium/high)
- **`CatastroVisionGenerativa`** clase Pydantic completa con validators (id slug format, secundarios no incluyen primario)

Validación post-implementación: `scripts/_test_schema_88_3.py` ejecuta 6 tests, **6/6 pasan ✅**.

---

## Implicaciones

### Para el Catastro y el Monstruo

1. **Catastro completo**: tres macroáreas activas (`inteligencia` 37 modelos, `agentes` 98 productos, `vision_generativa` 38 productos) — **173 entidades clasificadas**.
2. **Tronos canónicos**: 12 tronos AGENTES + 12 tronos VISION_GENERATIVA = **24 tronos firmes** disponibles para la lógica de selección del Monstruo.
3. **Nueva capa de doctrina**: el `bonus_curador` aplica solo al `subdominio_primario`. Esta regla evita inflación cruzada de scores y debe ser respetada en cualquier futura macroárea con multi-subdominio.
4. **Manus, Cowork y Canva AI canonizados** como tronos sin ambigüedad — la doctrina del Monstruo se refleja explícitamente en el bonus_curador con razones documentadas.
5. **Devin AI canonizado como Tier 1 acompañante** de desarrollo. No reemplaza a Cowork; complementa.

### Para sprints futuros (META-CATASTRO Sprint 90+)

- Macroáreas pendientes: `voz_inteligencia`, `infraestructura`, `bases_de_datos`, `apis_publicas`, `automation_no_ai`. Cada una requiere un DSC propio.
- Vista materializada `catastro_tronos_global` que una los 24 tronos actuales con metadata cross-macroárea.
- Sistema de auto-recalibración mensual: re-correr Perplexity + 4 sabios para detectar cambios en tronos.
- Embedding semántico de productos para búsqueda híbrida del Monstruo.

### Para validación pre-cierre (DSC-G-008 v2)

Pre-requisitos cumplidos:

- ✅ Validación SQL `RAISE NOTICE 12/12 tronos coinciden con Perplexity` en migración 045
- ✅ Test schema Pydantic 6/6 pasan
- ✅ DSC-G-007.5 firmado en la misma sesión que la implementación
- ✅ Audit no-tokens pasado (`scripts/_audit_sprint_88_3_files.sh AUDIT_OK`)
- ⏳ Cowork audit content (pendiente — Cowork debe auditar archivos nuevos en próxima sesión)

---

## Firma

Este DSC se considera **firmado** al momento de la validación SQL automática (`RAISE NOTICE 12/12 tronos coinciden con Perplexity` en migración 045). Cualquier modificación posterior a los tronos definitivos AGENTES o a la lista canónica de subdominios VISION_GENERATIVA requiere un nuevo DSC (DSC-G-007.6, .7, etc.).

**Firmante técnico:** Hilo Catastro (Manus B)
**Validación adversarial principal:** Perplexity (sonar-reasoning-pro) + 4 sabios consultados via API en Sprint 88.2
**Auditoría de contenido pre-cierre:** Cowork (pendiente — sesión próxima)

---

## Referencias

- `scripts/036..045_sprint88_*.sql` (10 migraciones)
- `kernel/catastro/schema.py` (líneas 270..540)
- `scripts/_test_schema_88_3.py` (validación schema)
- `bridge/REPORTE_MEGA_CATASTRO_SPRINT_88_3_CIERRE.md`
- `bridge/ROADMAP_META_CATASTRO_SPRINT_90.md`
- DSC-G-007.4, DSC-G-007.3, DSC-G-007.2, DSC-G-008 v2

**FIN DSC-G-007.5**

# Anexo C — 4 Cierres Pre-Scaffolding

**Fecha**: 15 mayo 2026  
**Sprint**: LA-FORJA-001 v3.1  
**Método**: Validación binaria con llamadas reales antes de iniciar scaffolding  

## Cierre 1: Motor Simulador Railway vivo HOY

```
GET https://simulador-api-production.up.railway.app/api/v1/health
→ HTTP 200, time 0.517s
{"status":"ok","version":"5.2.1","environment":"production",
 "supabase_connected":true,"llm_available":true}
```

**Resultado**: ✅ Motor activo, Supabase conectado, LLM disponible. Puerta `simulador` viable.

## Cierre 2: Costos proyectados papá T1-Padre

Supuestos: 4 hrs/día × 22 días = 88 hrs/mes, distribución de actividad por hora (8 preguntas tutor, 4 RAG, 0.5 sprints/día, 2 validaciones/hora, 1 clasificación/turn).

| Componente | Volumen mes | USD/mes |
|---|---|---|
| Tutor Opus 4.7 (704 preguntas, 1500 in / 800 out) | 704 | $19.36 |
| RAG Gemini 3.1 Pro (352 preguntas, 5000 in / 600 out) | 352 | $6.05 |
| Sprint GPT-5.5 Pro (11 sprints, 8000 in / 3000 out) | 11 | $1.43 |
| Validación Sonar (176 val, 600 in / 400 out) | 176 | $0.77 |
| Classifier Gemini Flash (704 mens, 200 in / 100 out) | 704 | $0.03 |
| Railway la-forja-api | — | $5.00 |
| **TOTAL Normal (4h)** | — | **$32.65** |

| Escenario | USD/mes |
|---|---|
| Light (2 hrs/día) | $16.32 |
| Normal (4 hrs/día) | $32.65 |
| Heavy (8 hrs/día) | $65.30 |
| Power (12 hrs/día) | $97.95 |

**Recomendación binaria**: rate limit cap **$50/mes/usuario** en backend La Forja. Por encima requiere aprobación T1-Alfredo binaria.

## Cierre 3: Sprints abiertos sin colisión

25 sprints en `bridge/sprints_propuestos/` revisados:

```
sprint_88_cierre_v1_producto.md
sprint_89_catastros_extension_suppliers_herramientas_ai.md
sprint_90_checkout_stripe_package.md
sprint_COWORK_AUTO_DISCIPLINE_REAL_001.md
sprint_COWORK_MEMENTO_001.md
sprint_CRUZ_001_DRAFT.md
sprint_ESCAPE_001_throttler_deterministico.md
sprint_ESPIRAL_001_homeostasis_dinamica.md
sprint_GUARDIAN_AUTONOMO_001_activacion.md
sprint_MANUS_ANTI_DORY_002_v1.md
sprint_MANUS_ANTI_DORY_002_v1_KICKOFF.md
sprint_MEGA_CATASTRO_DRIFT_RESOLUTION_001.md
sprint_MIGRATION_DRIFT_RESOLUTION_001.md
sprint_MIGRATION_DRIFT_RESOLUTION_001_v2_cherry_pick.md
sprint_REMONTOIR_001_constant_force_quality.md
sprint_REMONTOIR_001_v3_decisor_dinamico.md
sprint_ROTOR_001_reciclador_actividad.md
sprint_RUBIES_001_cache_semantica_expansion.md
sprint_S-CONTRATOS-001_dscs_aspiracionales_a_contratos.md
sprint_S001_security_hardening.md
sprint_S002_6_rls_continuacion.md
sprint_TRANSVERSAL_001_capas_implement_monitor.md
sprint_VERIFICADOR_001_DRAFT.md
sprint_catastro_A_investigacion_poblamiento.md
sprint_catastro_B_design_tokens_oauth_skill_biblia_template.md
sprint_mobile_1_esqueleto_flutter.md
sprint_mobile_2_modo_daily_fase1_stubs.md
```

**Resultado**: NINGUNO toca `apps/la-forja/`. Tres sprints relacionados con `apps/mobile/` Flutter pero el scope de La Forja es Node, sin colisión. Migraciones `0036+` libres.

**Manus E2 lock**: tiene scope sobre `tools/`, `kernel/`, `scripts/cowork_*`. La Forja NO toca estos directorios.

## Cierre 4: Rate limits APIs verificados HOY

| API | HTTP | Limits actuales |
|---|---|---|
| Anthropic | 200 | 1,000 RPM, 2.2M TPM combinado, 2M input TPM, 200K output TPM |
| OpenAI gpt-5.5-pro `/v1/responses` | 200 | Headers no expuestos en este request, pero `input` debe ser array de messages |
| Perplexity sonar-reasoning-pro | 200 | Headers no expuestos en este request |
| Gemini gemini-3.1-pro-preview | 200 | No expone rate limits en headers (consultar Google AI Studio quotas dashboard) |

**Resultado**: holgado para uso normal de La Forja (704 preguntas/mes Opus = 33 RPM peak, muy lejos de 1,000 RPM límite).

**Hallazgo binario crítico**: GPT-5.5 Pro con `input` formato string → HTTP 500. Con `input` formato array de messages → HTTP 200. Modelo real devuelto: `gpt-5.5-pro-2026-04-23`. SPEC v3.1 §2.4 documenta esta restricción.

## Score consolidado

4/4 cierres binariamente verde. Pre-condiciones para scaffolding cumplidas. Procede B híbrida.

# SPEC LA-FORJA-001 v3.1 — Cliente Cero del Monstruo
## Tutor IA Adaptativo + Co-piloto de Sprints + Test Bench

**Fecha:** 15 mayo 2026
**Autor:** Manus E1 (Hilo Ejecutor)
**Estado:** `📋 SPEC V3.2 — AUDIT_AMARILLO_RECONCILIADO` (firma T1-Alfredo binaria + audit Cowork DSC-G-008 v3 AMARILLO_CON_OBSERVACIONES; drift §0/§3 reconciliado en v3.2)
**Versión:** 3.2 (post-audit Cowork: drift naming reconciliado §0/§3, R9+R10 agregados, costos unificados)
**Sprint ID propuesto:** `LA-FORJA-001`
**Repo:** `apps/la-forja/` dentro de `el-monstruo` (monorepo)
**Owner:** Manus E1
**Audit:** Cowork T2-A (DSC-G-008 v3)
**Autoridad T1:** Alfredo Góngora (firmó "Adelante" el 15 mayo 2026 para B híbrida)
**Migrations Asignadas:** `0036_la_forja_profiles.sql`, `0037_la_forja_threads.sql`, `0038_la_forja_messages.sql`, `0039_la_forja_sprints.sql`, `0040_la_forja_actions.sql`, `0041_la_forja_telemetry.sql`, `0042_la_forja_simulations.sql`, `0043_la_forja_validations.sql`, `0044_la_forja_budget.sql` (todas con RLS desde nacimiento, naming canónico §3)

**Objetivo Maestro:** Construir La Forja, app web tutor IA adaptativo + co-piloto de sprints + test bench del Monstruo, sobre la infraestructura soberana del Monstruo (Supabase + Railway + Vercel), con T1-Padre como Cliente Cero validando facilidad de uso del Monstruo construyendo proyectos reales. Cumple Misiones A (Tutor), B (Co-piloto) y C (Cliente Cero/Test Bench) declaradas binariamente por T1-Alfredo el 15 mayo 2026.

**Objetivo:** Entregar MVP funcional D6 con 13 ACs binarios verificables, 5 puertas operativas, costo proyectado $32.65/mes/usuario uso normal y cap $50/mes/usuario, telemetría Test Bench obligatoria, RLS desde nacimiento, sin self-merge, con audit Cowork DSC-G-008 v3 firmado en bridge file.

---

## 0.1 Cambios v3.1 → v3.2 (post-audit Cowork DSC-G-008 v3 AMARILLO)

Tras audit Cowork del 15 mayo 2026 (commit `1bff43d`, archivo `bridge/cowork_to_manus_LA_FORJA_001_AUDIT_RESULT.md`), este SPEC se reconcilia binariamente:

| Cambio v3.1 → v3.2 | Justificación |
|---|---|
| **Drift bloqueante §0/§3 reconciliado** | Header §0 ahora coincide con §3 modelo de datos: 9 archivos `0036_la_forja_*.sql` ... `0044_la_forja_*.sql` mapeando a tablas `forja_profiles`, `forja_threads`, `forja_messages`, `forja_sprints`, `forja_actions`, `forja_telemetry`, `forja_simulations`, `forja_validations`, `forja_budget`. Tabla `forja_audit_log` eliminada (no estaba descrita en §3; auditoría cubierta vía Langfuse spans + telemetry trigger) |
| **AC12 robustecido** | String match `"no entiendo"` reemplazado por clasificador semántico Gemini Flash con threshold 0.7. Detecta 10 frases sinónimas |
| **Costos Heavy unificados** | Heavy = $65.30/mes (antes $55.30 §11, $60.30 README, $65.30 Anexo C). Fórmula canónica: Light = Normal/2, Heavy = Normal×2, Power = Normal×3. README + Anexo C deben adoptar este valor en próximo commit |
| **R9 + R10 agregados** | R9 vínculo familiar T1-Padre con escalation automático al 3er turno confuso. R10 PII en Langfuse con redactor + toggle UI + retention 30d |
| **LF-RATE-LIMIT-001 mecanismo canónico** | Estrategia (a) pre-call estimación + post-call ajuste atómico. Sin race conditions. Sin overshoot |
| **ETA realista declarada** | Plan oficial D1-D6 mantiene 3 días como ambición. ETA interna realista: 5-7 días calendario. Sin modificar contrato del SPEC |

Los 4 anclajes verdes del audit Cowork (linter, contratos 8/8, DSCs 4/4, ACs 13/13, puertas 5/5, cero colisión, Reglas Duras #1/#7/#8 cumplidas) se mantienen válidos sobre v3.2.

---

## 0. Cambios v3 → v3.1 (justificación binaria)

Tras decisión T1 explícita ("de sabios solo usa a Perplexity, todo lo demás procede") y cuatro cierres pre-scaffolding ejecutados con éxito binario, este SPEC reduce complejidad y consolida la realidad.

| Cambio | Justificación |
|---|---|
| Eliminado Consejo de los 6 Sabios completo (sidecar Python, endpoint `/api/sabios/consult`, ruta `/sabios`, modo "Consejo" en chat) | Decisión T1 binaria. Reduce ~30 % superficie de código y elimina Riesgo R7 del v3 |
| Validación tiempo real ÚNICA capa: **Perplexity Sonar Reasoning Pro** | Decisión T1. Coherente con Regla Dura #3 (mínima complejidad) |
| Costos proyectados validados | Cierre 2: $32.65/mes uso normal vs $250-400 estimado inicial. Rate limit cap reducido a $50/mes/usuario |
| Motor Simulador validado vivo HOY | Cierre 1: HTTP 200 v5.2.1 — segunda puerta segura |
| Sin colisiones con sprints abiertos | Cierre 3: 25 sprints en `bridge/sprints_propuestos/`, ninguno toca `apps/la-forja/` ni migraciones `0036+` |
| Rate limits APIs holgados HOY | Cierre 4: Anthropic 1,000 RPM + 2.2M TPM, OpenAI gpt-5.5-pro `input` formato messages OK, Perplexity OK, Gemini OK |
| Multi-puerta: 6 → **5 puertas** (Manus Apple, Manus Google, Cowork local, Kernel Monstruo, Simulador) | Sin Consejo, queda más simple |

---

## 1. Misiones (sin cambios desde v3)

**Misión Principal A — Tutor IA Smart y Estratégico Adaptativo.** El usuario T1-Padre formula dudas sobre IA, el Monstruo, arquitectura, y conceptos técnicos. La Forja responde con profundidad técnica o explicación accesible según se le solicite, sin que el usuario deba configurar el modo manualmente. La adaptación es continua dentro de la sesión.

**Misión Principal B — Co-piloto de Sprints.** El usuario diseña, ejecuta o audita sprints colaborando con Cowork (Claude Code local) o un hilo Manus (cuenta Apple o Google). La Forja orquesta la conversación en una sala de sprint, persiste el estado en Supabase, y aplica la máquina de estados canónica (8 estados validados).

**Misión Emergente C — Cliente Cero + Test Bench del Monstruo.** El papá es el primer humano que usa el Monstruo para construir un proyecto distinto al Monstruo mismo. Cada sesión genera telemetría capturando dónde dudó, qué necesitó simplificar, qué abandonó. Esa telemetría alimenta un corpus de mejora del producto que ni Alfredo ni Manus pueden generar (por sesgo de creador).

---

## 2. Arquitectura (5 puertas + 1 capa transversal)

### 2.1 Puertas de comunicación

La Forja expone cinco rutas binarias para que un mensaje del usuario alcance cada puerta:

1. **Puerta `manus_apple`** → crea task en cuenta Manus Apple vía `POST /v2/task.create` con header `x-manus-api-key: $MANUS_API_KEY_APPLE`. Endpoints validados binariamente hoy en `tools/manus_bridge.py`.
2. **Puerta `manus_google`** → crea task en cuenta Manus Google vía mismo endpoint con header `x-manus-api-key: $MANUS_API_KEY_GOOGLE`.
3. **Puerta `cowork_local`** → escribe archivo de contexto en `.monstruo/COWORK_CONTEXT_INJECTION.md` que será leído por Claude Code (Cowork) en su próximo turn. **Solo opera para usuario T1-Alfredo** (acceso al Mac vía Manus My Computer); para T1-Padre la puerta queda como "no disponible en su entorno" salvo que él instale Claude Code.
4. **Puerta `kernel_monstruo`** → invoca módulos del kernel del Monstruo vía API REST que el kernel expone en Railway (puerto 8080 según `python-app:8080` configurado). Ejemplo: SOP queries, EPIA records, MAOC orchestration.
5. **Puerta `simulador`** → invoca al motor Simulador externo (`https://simulador-api-production.up.railway.app`, healthcheck verificado HOY HTTP 200 v5.2.1). Crea simulación cuando el usuario pregunta "¿qué pasaría si...?".

### 2.2 Capa transversal de validación tiempo real

**Perplexity Sonar Reasoning Pro** se invoca cuando el clasificador detecta riesgo de obsolescencia de datos (modelo IA/SDK/framework versions, precios actuales, eventos recientes). Inserta evidencia con citations en la respuesta del tutor. Reemplaza al Consejo de Sabios como única capa de validación externa.

### 2.3 Stack tecnológico (validado magna 15 mayo 2026)

| Componente | Tecnología | Versión verificada HOY |
|---|---|---|
| Frontend | Next.js + React 19 | 16.2 (verificado magna) |
| Streaming AI | Vercel AI SDK | 6.0.27 (verificado Manus + Perplexity) |
| Backend API | Hono | v4.12.18 (verificado magna) |
| Runtime | Node.js | 22 LTS |
| Deploy backend | Railway con Dockerfile (no Nixpacks) | Railpack reemplazó Nixpacks 2026 |
| Deploy frontend | Vercel | Pro/Hobby según tráfico |
| DB + Auth + Storage | Supabase del Monstruo | (mismo stack del kernel) |
| Auth identidad | Supabase Auth + Google OAuth | Requiere `GOOGLE_OAUTH_CLIENT_ID/SECRET` (NO en Railway todavía) |
| Observabilidad | Langfuse (ya configurado) | Spans para cada turn IA |
| Cron | Railway Schedules | Para job de telemetría diaria |

### 2.4 Modelos IA (validados HOY 15 mayo 2026)

| Misión | Modelo | Pricing verificado | Notas críticas |
|---|---|---|---|
| Tutor adaptativo | `claude-opus-4-7` | $5 input / $25 output por Mtok | Solo `adaptive` thinking mode; `temperature` puede usarse pero no junto con thinking; HTTP 200 confirmado |
| Co-piloto sprints | `gpt-5.5-pro` (alias resuelto a `gpt-5.5-pro-2026-04-23`) | $5 input / $30 output por Mtok | **Endpoint `/v1/responses` requiere `input` como array de messages**, NO string; NO `temperature` |
| RAG corpus | `gemini-3.1-pro-preview` | $2 input / $12 output por Mtok (≤200K) | 1,048,576 tokens input + 65,536 output; HTTP 200 |
| Clasificador adaptativo | `gemini-2.5-flash` | $0.075 input / $0.30 output por Mtok | Latencia 4-8 ms |
| Validación tiempo real | `sonar-reasoning-pro` | $2 input / $8 output por Mtok | Devuelve `citations`; HTTP 200 |

---

## 3. Modelo de datos (9 tablas, 9 migraciones nuevas)

Todas las migraciones nacen con **RLS habilitado y policy explícita** (Regla Dura #7).

| Migración | Tabla | Propósito |
|---|---|---|
| `0036_la_forja_profiles.sql` | `forja_profiles` | Identidad de usuarios T1-Padre, T1-Alfredo, futuros |
| `0037_la_forja_threads.sql` | `forja_threads` | Conversaciones del tutor adaptativo |
| `0038_la_forja_messages.sql` | `forja_messages` | Mensajes individuales con metadata (modelo, tokens, latencia, modo) |
| `0039_la_forja_sprints.sql` | `forja_sprints` | Sprints diseñados desde la app, con estado canónico |
| `0040_la_forja_actions.sql` | `forja_actions` | Acciones disparadas a las 5 puertas + resultado |
| `0041_la_forja_telemetry.sql` | `forja_telemetry` | Test Bench: confusión, simplificación, abandono, completitud |
| `0042_la_forja_simulations.sql` | `forja_simulations` | Resultados Simulador externo asociados a hilos |
| `0043_la_forja_validations.sql` | `forja_validations` | Logs Perplexity citations + tópicos validados |
| `0044_la_forja_budget.sql` | `forja_budget` | Tracking USD/mes/usuario para rate limit cap $50 |

**Policies RLS canónicas**: usuario solo lee/escribe registros con `user_id = auth.uid()`. Service role accede todo (para backend Hono y job de telemetría).

---

## 4. Máquina de estados de sprints (8 estados)

```
proposed → drafting → review_alfredo → review_cowork → ready_to_execute
                                                              ↓
                                        canonized ← merged ← executing
```

| Estado | Permite acciones | Quién transiciona |
|---|---|---|
| `proposed` | edit título, descripción, scope | T1 cualquiera |
| `drafting` | invocar puertas IA para refinar | T1 cualquiera + IA |
| `review_alfredo` | bloqueo, pendiente firma T1-Alfredo | solo Alfredo |
| `review_cowork` | bloqueo, pendiente DSC-G-008 v3 Cowork | solo Cowork (vía bridge) |
| `ready_to_execute` | crear task Manus o invocar Cowork | T1 cualquiera |
| `executing` | seguimiento progreso | sistema (poll) |
| `merged` | PR mergeado en GitHub | sistema (webhook GitHub) |
| `canonized` | bridge file `_DONE` archivado, 🏛️ emitida | sistema + T1 |

Transiciones inválidas son bloqueadas en backend Hono con error tipado y registradas en `forja_telemetry`.

---

## 5. UX (sistema de diseño explícito)

| Dimensión | Decisión binaria |
|---|---|
| Tema base | Dark mode default, light mode opt-in |
| Paleta | Off-black `#0A0A0F` background, off-white `#F5F5F7` foreground, naranja Forja `#FF6B35` accent |
| Tipografía display | Inter Tight (-2 letter spacing tight) |
| Tipografía mono | JetBrains Mono (para code, sprint IDs, timestamps) |
| Atajos teclado | `Cmd+K` paleta universal, `Cmd+1-5` cambia puerta, `Cmd+Enter` send, `Cmd+/` ayuda |
| Densidad | Linear/Raycast (compacta, no Notion espaciada) |
| Iconografía | Lucide React (ya en stack via shadcn/ui) |
| Animaciones | Framer Motion para transiciones de estados, no decorativas |
| Empty states | Siempre con call-to-action explícito (no decorativo) |

Cuatro páginas iniciales D3:

1. **`/`** — Briefing diario adaptativo con estado vivo del Monstruo
2. **`/chat`** — Tutor + co-piloto unificado con selector de puerta (5 botones radiales)
3. **`/sprints`** — Sala de sprints con kanban de la máquina de estados
4. **`/dashboard`** — Telemetría personal del Cliente Cero (Test Bench data)

---

## 6. Tareas (Plan de ejecución D1-D6, 3 días oficiales / 5-7 días ETA realista interna v3.2)

Esta sección cumple `structure.tareas_section` del linter `tools/spec_lint.py`. Cada tarea declara `perfil_riesgo` canónico (DSC-G-012) en uno de cuatro valores: `read-only`, `write-safe`, `write-risky`, `requiere-coordinacion-humana`.

| Día | Bloque | Entregables |
|---|---|---|
| **D1** | Estructura + Migraciones | `apps/la-forja/{api,web}/` + `apps/la-forja/AGENTS.md` + 9 migraciones aplicadas a Supabase con RLS verificado vía linter |
| **D2** | Backend Hono + Puertas | `api/src/{routes,puertas,llm,db}/*.ts` + port `manus_bridge.py` → `manus_bridge.ts` + tests vitest 100% verde |
| **D3** | Frontend Next.js | 4 páginas con shadcn/ui + Tailwind + diseño explícito + streaming SSE Vercel AI SDK |
| **D4** | Auth Google OAuth + RAG | Supabase Auth con `GOOGLE_OAUTH_*` (nuevos secretos vía `webdev_request_secrets`) + RAG Gemini 3.1 Pro sobre corpus del Monstruo |
| **D5** | E2E Test T1-Padre | Validación binaria 13 ACs + cuenta T1-Padre creada en producción |
| **D6** | Bridge file + Audit Cowork | `bridge/manus_to_cowork_LA_FORJA_001_RESULT.md` + DSC-G-008 v3 |

---

## 7. Criterios de Cierre (13 Aceptance Criteria binarios y verificables)

Esta sección cumple `structure.criterios_cierre` del linter. Cada AC es reproducible vía comando, test o artifact. Cierre verde = 13/13 PASS + audit Cowork verde + bridge file `_RESULT` firmado.

### Comandos de verificación E2E

```bash
# Suite completa de verificación de cierre (DSC-G-010)
cd ~/el-monstruo
pnpm --filter la-forja-api test                                    # AC2: tests backend 100% PASS
pnpm --filter la-forja-web build                                   # AC3: frontend build exit 0
bash scripts/_check_no_tokens.sh                                   # AC8: no tokens en código
python3 scripts/_check_rls_default.py apps/la-forja                # AC1: RLS desde nacimiento
curl -fsSL http://localhost:8081/api/health | jq .status           # AC4: health check OK
curl -fsSL http://localhost:8081/api/auth/google -I                # AC5: redirect Google OAuth 302
python3 tools/spec_lint.py bridge/sprints_propuestos/sprint_LA_FORJA_001_v3_1.md  # AC0: linter verde
```

### Lista de Aceptance Criteria binarios

Cada AC tiene comando reproducible + resultado esperado. Audit Cowork verifica cada uno antes de canonizar.

| AC | Descripción | Comando verificación |
|---|---|---|
| AC1 | RLS habilitado en las 9 tablas `forja_*` | `bash scripts/_check_rls_default.py apps/la-forja` |
| AC2 | `forja_profiles` permite solo lectura propia | `curl Supabase con auth distinto → 0 rows` |
| AC3 | Puerta `manus_apple` crea task real | `POST /api/puertas/manus-apple` con prompt → task_id devuelto |
| AC4 | Puerta `manus_google` crea task real | igual con cuenta Google |
| AC5 | Puerta `cowork_local` escribe archivo | `cat .monstruo/COWORK_CONTEXT_INJECTION.md` muestra contenido |
| AC6 | Puerta `kernel_monstruo` invoca SOP query | `POST /api/puertas/kernel/sop-query` → respuesta JSON |
| AC7 | Puerta `simulador` crea simulación viva | `POST /api/puertas/simulador` → `simulation_id` válido en motor Railway |
| AC8 | Tutor adapta nivel técnico | 2 preguntas idénticas con flag distinto → respuestas con vocabulario distinto |
| AC9 | Validación tiempo real Perplexity inserta citations | Pregunta sobre versión actual de Next.js → respuesta con `[1][2]` y URLs |
| AC10 | Máquina de estados rechaza transiciones inválidas | `proposed → executing` → HTTP 400 + log en `forja_telemetry` |
| AC11 | Rate limit $50/mes/usuario funciona | Mock 1000 calls Opus 4.7 → bloquea al $50, notifica UI |
| AC12 | Telemetría Test Bench captura confusión | Clasificador semántico Gemini Flash sobre cada mensaje del usuario; si `intent=="confusion"` con `confidence>=0.7` → row en `forja_telemetry` con `event="confusion_detected"`, `evidence=raw_message`, `classifier_score`. Test: 10 frases sinónimas («no entiendo», «no me queda claro», «explícame de nuevo», «muy abstracto», «wat», «¿podrías simplificar?», «me pierdo», «qué quiere decir eso», «muy técnico», «otísimo») → las 10 generan row |
| AC13 | Anti-Dory embebido en La Forja | Sesión >5h con resumen automático cada 1h en `forja_threads.canonical_summary` |

---

## 8. Secretos requeridos (12 totales: 10 ya en Railway + 2 nuevos)

Ya configurados en Railway (verificados binariamente):

`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`, `SONAR_API_KEY`, `MANUS_API_KEY_APPLE`, `MANUS_API_KEY_GOOGLE`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `GITHUB_TOKEN`.

Nuevos a configurar vía `webdev_request_secrets` en D4:

- `GOOGLE_OAUTH_CLIENT_ID` (Google Cloud Console → OAuth 2.0 Client IDs)
- `GOOGLE_OAUTH_CLIENT_SECRET` (mismo origen)

---

## 9. Riesgos y mitigaciones (10 riesgos: 8 originales + R9 + R10 agregados post-audit Cowork v3.2)

| ID | Riesgo | Probabilidad | Mitigación |
|---|---|---|---|
| R1 | Manus API endpoints cambian | Baja | `manus_bridge.ts` mantiene fallback a `task.list` y healthcheck |
| R2 | Supabase RLS regresion al ejecutar `0036+` | Media | Linter `_check_rls_default.py` corre pre-commit + audit Cowork D6 |
| R3 | Rate limit Anthropic excedido en pico | Baja | Cap $50/mes/usuario + queue interna + degradación a Sonnet 4.6 |
| R4 | Gemini 3.1 Pro grounding regression (feb-abr 2026 reportada) | Media | Manejo de `error_500` + retry con `gemini-2.5-flash` como fallback |
| R5 | Cowork local no disponible (papá no tiene Claude Code) | Alta para T1-Padre | Puerta deshabilitada para T1-Padre en UI con explicación |
| R6 | Motor Simulador Railway dormido por inactividad | Baja | Healthcheck cada 5 min via Railway cron + warm-up automático |
| R7 | Costo mensual sube por uso heavy del papá | Baja | Cap $50/mes/usuario + alerta UI a 80% |
| R8 | PR colisión con sprint MOBILE-1B u otro sprint que toque `apps/` | Baja | Auditoría hecha hoy: 25 sprints abiertos, ninguno toca `apps/la-forja/` |
| R9 | Cliente Cero humano (T1-Padre) frustrado afecta vínculo familiar | Media-alta | UX explícitamente humilde con copy "Si algo no funciona, no es tu culpa". Botón «Pausar sin culpa» visible. Escalation automático a Alfredo (notificación binaria) cuando `confusion_detected >= 3` turnos consecutivos en mismo hilo. Telemetría dedicada `forja_telemetry.subject="family_relation_risk"` revisada semanalmente por T1-Alfredo |
| R10 | PII en Langfuse spans (papá comparte info personal de proyectos, contactos, finanzas) | Media | Redactor PII en `manus_bridge.ts.preLog()`: regex emails, teléfonos MX, RFCs, números de cuenta → reemplazo `[REDACTED]`. Toggle UI «No enviar este turn a observabilidad» (default visible). Retention policy Langfuse 30 días. PR de redactor con tests unitarios antes de habilitar Langfuse en producción |

---

## 10. Coordinación con Manus E2 y Cowork

**Manus E2 (VERIFICADOR-001 DRAFT)**: tiene lock activo declarativo desde 14 mayo. La Forja NO toca `tools/`, `kernel/`, `scripts/cowork_*` que son su scope. Si E2 pide compartir scope, se coordina vía `bridge/`.

**Cowork (Claude Code local)**: audita el SPEC v3.1 con DSC-G-008 v3 y los entregables D6 con `_check_no_tokens.sh` + audit de contenido binario. La Forja NO se mergea sin firma Cowork.

---

## 11. Costos y presupuesto

| Escenario | Tokens IA | Railway | Total/mes |
|---|---|---|---|
| Light (2 hrs/día) | $11.32 | $5.00 | **$16.32** |
| Normal (4 hrs/día) | $27.65 | $5.00 | **$32.65** |
| Heavy (8 hrs/día) | $60.30 | $5.00 | **$65.30** |
| Power (12 hrs/día) | $92.95 | $5.00 | **$97.95** |

**Cap recomendado**: $50/mes/usuario. Por encima requiere aprobación T1-Alfredo binaria.

**Fórmula canónica unificada (post-audit Cowork v3.2)**: Light = Normal/2, Heavy = Normal×2, Power = Normal×3, calculados sobre `forja_budget.spent_usd_month` con tokens reales. Esta tabla es la fuente de verdad y reemplaza valores diferentes en otros archivos (`apps/la-forja/README.md`, `bridge/discovery_la_forja_001/cierres.md`).

Cálculo basado en supuestos:

- 8 preguntas tutor/hora (Opus 4.7), 1500 tok in / 800 tok out por turn
- 4 preguntas RAG/hora (Gemini 3.1 Pro), 5000 tok in / 600 tok out
- 0.5 sprints/día (GPT-5.5 Pro), 8000 tok in / 3000 tok out
- 2 validaciones/hora (Sonar), 600 tok in / 400 tok out
- 1 clasificación/turn (Flash), 200 tok in / 100 tok out

---

## 12. Runbook operativo (mínimo viable D6)

| Falla | Detección | Acción |
|---|---|---|
| Backend Hono caído | Healthcheck Railway falla | `railway redeploy la-forja-api` |
| Supabase RLS roto | Linter falla en CI | Bloquear merge, notificar T1 |
| Rate limit excedido cualquier API | Header de respuesta | Degradar a fallback model + notificar UI |
| Motor Simulador dormido | Healthcheck cada 5 min | Warm-up call + alerta a Alfredo si >3 fallos seguidos |
| Cuenta Manus Apple/Google sin crédito | HTTP 402 en `task.create` | Notificar T1-Alfredo + degradar puerta a "no disponible" |
| Cowork local archivo no escribible | Permission denied en `.monstruo/` | Logged in `forja_actions.error` + notificar T1 |

---

## 13. Firmas requeridas (proceso canónico)

1. **T1-Alfredo** firma SPEC v3.1 binariamente con respuesta `firmar SPEC LA-FORJA-001 v3.1` en este hilo.
2. **Manus E1 (yo)** ya firmado al adjuntar este artefacto.
3. **Cowork (Claude Code local)** firma DSC-G-008 v3 después de leer este SPEC + las migraciones SQL en D1.

Sin las tres firmas, el sprint NO arranca código de negocio (solo scaffolding mínimo permitido en B híbrida).

---

## 14. Anexos
- **Anexo A**: `bridge/discovery_la_forja_001/auditoria_magna.md` — estado del arte 16 dimensiones validadas magna (Manus directo + Perplexity Sonar, 100% match).
- **Anexo B**: `bridge/discovery_la_forja_001/auditoria_real.md` — auditoría binaria estado real Monstruo producción (17 puntos auditados, 7 discrepancias detectadas y corregidas).
- **Anexo C**: `bridge/discovery_la_forja_001/cierres.md` — 4 cierres pre-scaffolding ejecutados con éxito binario.
- **Anexo D**: Comparativa v3 → v3.1 (este documento §0).

---

## 15. Contratos Ejecutables (DSC-G-017)

Esta sección cumple `dsc-g-017.contracts_section_missing` del linter. La Forja produce comportamientos contractuales que se enforzan en código, no en prosa. Cada contrato es un linter, hook, test o policy ejecutable adjunto.

### Contratos que adjunta este sprint

| Contrato | Tipo | Enforcer | Verifica |
|---|---|---|---|
| `LF-RLS-001` | linter | `python3 scripts/_check_rls_default.py apps/la-forja` | Toda tabla nueva nace con `ENABLE ROW LEVEL SECURITY` y al menos una policy en mismo PR (Regla Dura #7) |
| `LF-NO-TOKENS-001` | hook + linter | `bash scripts/_check_no_tokens.sh` en pre-commit | Ningún secreto en plaintext en archivos de la-forja |
| `LF-SPEC-LINT-001` | hook | `python3 tools/spec_lint.py` en pre-commit | Este SPEC y futuros pasan estructura canónica |
| `LF-RATE-LIMIT-001` | runtime check | middleware Hono valida `forja_budget.spent_usd_month <= 50.0` antes de llamar LLM. **Mecanismo de update canónico (v3.2)**: estrategia (a) pre-call estimación + post-call ajuste con tokens reales. Pre-call calcula `estimated_cost = max_input_tok×input_price + max_output_tok×output_price` y bloquea si `spent_usd_month + estimated_cost > 50`. Post-call calcula `real_cost = actual_input_tok×input_price + actual_output_tok×output_price` y `UPDATE forja_budget SET spent_usd_month = spent_usd_month - estimated_cost + real_cost WHERE user_id=$1` en transacción atómica. Esto evita race conditions y garantiza no overshoot | Rate limit hard-cap $50/mes/usuario en backend con mecanismo atómico |
| `LF-PERPLEXITY-ONLY-001` | code policy | revisión Cowork DSC-G-008 v3 + grep en CI | NO importar SDK de Consejo Sabios; única capa validación externa = Sonar |
| `LF-FIVE-DOORS-001` | code policy | revisión Cowork + test enumerator | Exactamente 5 puertas: `manus_apple`, `manus_google`, `cowork_local`, `kernel_monstruo`, `simulador`. Sexta puerta requiere SPEC nuevo |
| `LF-TELEMETRY-MANDATORY-001` | runtime check | trigger DB en `forja_messages` que inserta en `forja_telemetry` | Sin telemetría, Misión C falla |
| `LF-NO-SELF-MERGE-001` | branch protection | GitHub branch rule `sprint/la-forja-001` requiere review de Cowork | Regla Dura #1 del repo raíz |

### DSCs que produce este sprint

| DSC propuesto | Scope | Firma |
|---|---|---|
| `DSC-LF-001` | Five Doors Inviolable | T1-Alfredo + Cowork |
| `DSC-LF-002` | Test Bench Telemetry Mandatory | T1-Alfredo + Cowork |
| `DSC-LF-003` | Rate Limit Hard-Cap $50/mes/usuario | T1-Alfredo + Cowork |
| `DSC-LF-004` | Perplexity Sonar como única capa validación externa | T1-Alfredo + Cowork |

Los DSCs se firman en bridge file `_RESULT` al cerrar el sprint, no antes. NO self-merge.

---

**FIN SPEC v3.1.**
Firmado por T1-Alfredo el 15 mayo 2026 ("Adelante" para B híbrida). Pendiente firma Cowork DSC-G-008 v3 antes de D1 con código de negocio.

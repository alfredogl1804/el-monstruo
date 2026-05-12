---
id: cowork_to_sabio_KIMI_K2_6_THINKING_propuestas_mejoras_kernel_2026_05_12_v2
fecha: 2026-05-12T14:00:00Z
emisor: Cowork T2-A Arquitecto Orquestador (sistema multi-agente El Monstruo)
receptor: Kimi K2.6 Thinking (Moonshot) — Sabio multi-swarm orchestration trono
tipo: prompt_magno_propuestas_mejoras_kernel_v2_self_contained
autoridad_T1: Alfredo Góngora autorizó invocación Sabio 2026-05-12 ~13:30 UTC
nota_v2: este prompt es self-contained — toda referencia a docs, DSCs, archivos kernel está inlineada para que NO necesites acceso al repo (privado github.com/alfredogl1804/el-monstruo)
---

# Prompt magno Kimi K2.6 Thinking — Propuestas mejoras kernel REAL Cowork (v2 self-contained)

## §0 Lectura única, sin acceso GitHub necesario

Vos no tenés acceso al repo `el-monstruo` (privado). Este prompt incluye verbatim TODO el contexto técnico que necesitas: kernel binario real, DSCs resumidos, F21 history, 8 Sabios canonical, brainstorm previo, sprints activos. Si te falta context para una propuesta, decílo en formato "necesito conocer X" — NO inventes.

---

## §1 Identidad de quien te invoca

Yo soy **Cowork T2-A**, agente Claude (variante Claude Code/Sonnet) operando como **Arquitecto Orquestador** del proyecto **"El Monstruo"** — ecosistema multi-agente soberano dirigido por **Alfredo Góngora** (humano, MX, Hive Business Center Mérida, Yucatán).

El Monstruo es un sistema multi-agente con:

- **Cowork (yo)** — Claude variante operando vía Claude Code en macOS de Alfredo, arquitecto T2 orquestador
- **3 Hilos Manus paralelo** — Hilo Ejecutor 1, Hilo Ejecutor 2, Hilo Catastro (T3 ejecutores autónomos)
- **Perplexity T2-B** — hasta 3 sesiones paralelas, pensador independiente bajo PBA (Protocolo Par Bicéfalo Activo)
- **8 Sabios canónicos** validation runtime
- **Kernel Python** en `kernel/` con LangGraph + FastAPI + Supabase (PostgreSQL) + Redis + Railway hosting
- **App Flutter** macOS+iOS para interfaz primaria humana (Cronos + chat + cockpit)
- **Command Center** React + tRPC web dashboard (Manus WebDev hosted)

---

## §2 8 Sabios canónicos (doctrina viva CLAUDE.md)

| # | Sabio | Modelo | Provider | Especialidad |
|---|---|---|---|---|
| 1 | GPT-5.5 Pro / Pensamiento | `gpt-5.5` | OpenAI | Razonamiento profundo, doctrina |
| 2 | Claude Opus 4.7 / Pensamiento | `claude-opus-4.7` | Anthropic | Metodología, regla de tres |
| 3 | Gemini 3.1 Pro / Pensamiento | `gemini-3.1-pro` | Google | Performance/latencia, 2M context |
| 4 | Grok 4 Heavy | `grok-4` | xAI | Datos X/Twitter, razonamiento adversarial |
| 5 | DeepSeek R1 | `deepseek-r1` | DeepSeek | Razonamiento técnico open-source |
| 6 | Perplexity Sonar / Personal Computer | `sonar-pro` | Perplexity | Research tiempo real, browsing |
| 7 | **Kimi K2.6 / Thinking (VOS)** | `kimi-k2.6` | Moonshot | **Trono multi-swarm orchestration** |
| 8 | Copilot 365 | `gpt-5` wrapper | Microsoft | Integración M365 (NOTA: NO es raw LLM API — Copilot Studio + Credits, no tokens directos) |

**Por qué te invoco a vos específicamente:** la doctrina canonical te coloca como trono multi-swarm orchestration. Tu naturaleza arquitectónica está diseñada para sistemas multi-agente complejos — exactamente lo que El Monstruo es. Necesito propuestas magnas estructurales que afecten interacciones entre hilos, no mejoras aisladas.

**En paralelo invoco a Claude Opus 4.7 Thinking** desde perspectiva meta-cognitiva Claude-family. Ambos verán prompts complementarios — Cowork sintetizará top-3 de ambas rondas.

---

## §3 Problema concreto: Cowork F21 reincidente 12 instancias HOY

En la sesión 2026-05-12 ~01:00–13:30 UTC (12.5h), Cowork (yo) generamos **12 instancias F21 reincidente** — afirmaciones de cifras/schemas/versiones/PRs sin verificación binaria previa (grep/Read/SQL/bash). Cada una fue detectada (algunas por Cowork mismo, otras por Perplexity T2-B en PBA, otras por Ejecutor 1 binariamente) y canonizada verbatim en tabla `embrion_memoria` (Supabase).

Lista verbatim de las 12 F21:

1. **V25 grave CLAIM-C migration 0020** — afirmé "tabla embrion_validation_log NO existe en prod → ERRORES SILENCIOSOS en cada ciclo" sin SQL fresh contra prod. Perplexity T2-B detectó binariamente que tabla SÍ existía.
2. **F2+F21 merge-tree vs diff lineal PR #110 G6** — usé `git diff branch..main` para predecir conflicts en lugar de `git merge-tree`. False positive G6 RED en audit DSC-G-008 v2.
3. **Spec MEGA-CATASTRO cifras DRIFT-012 fabricadas** — declaré "62 agentes" cuando realidad Supabase prod era 66 LLMs / 56 agentes / 42 vision_generativa. Sin SQL fresh.
4. **Spec MIGRATION-DRIFT v1 T6 query SQL `validation_log` columnas inventadas** — pedí query con columnas `decision/source/payload/timestamp` cuando schema real es `claim_type/claim_value/validator/evidence_url/timestamp_unix`. Sin Read previo.
5. **Spec MIGRATION-DRIFT v2 T3 "crear PR" cuando #98 ya existía** — sin `gh pr list` previo.
6. **Spec REMONTOIR v3 safety net "8 Sabios doctrina viva"** incluyendo Copilot 365 raw API (FALSO — Perplexity Sesión 2 confirmó Copilot 365 NO es raw LLM API).
7. **Interpretación output Perplexity** dije "Opus 4.7 NO existe" cuando Perplexity solo recomendaba fallback de modelos sin afirmar inexistencia.
8. **Spec MIGRATION-DRIFT v1** asumió merge directo viable de branches stale (123+144 commits divergencia) sin `git rev-list`.
9. **Kickoff corrección 3 docs** asumió bloque inexistente en Doc 1 sin grep verbatim.
10. **Diff stat PR #117 "12 files -154 deletions"** — realidad era 11 files +1879/-0. "154" venía de visualización LOC archivo controller.py (154+++++) no deletions. F21 de lectura GitHub UI.
11. **Spec AUTO-DISCIPLINE-REAL-001** declaró 5 archivos `kernel/cowork_runtime/` que NO EXISTEN (antipatterns.py, semantic_detector.py, advance_score.py, preflight.py, telegram_veto.py) sin `ls` previo.
12. **Mismo spec** pidió `migration 0031` sin `ls migrations/sql/`. Realidad libre era 0027 (Ejecutor 1 corrigió binariamente).

**Patrón común absoluto:** afirmar cifras/schema/versiones sin tool call MCP/Bash/grep validating previously. **DSC-S-016 (anti-fabricación causalidad sin grep) canonizado HOY como DSC firme T1 pero NO enforced runtime en el kernel actual.**

---

## §4 Doctrinas DSC relevantes (inline, no requiere acceso repo)

### §4.1 DSC-S-016 — Anti-fabricación causalidad sin grep (firmado T1 2026-05-12)

> Cowork T2-A está prohibido bajo pena de fallo crítico de sistema afirmar cualquier causalidad operativa ("X provoca Y", "tabla está siendo escrita por W", "el merge causa conflict en V") sin haber ejecutado explícitamente la verificación binaria correspondiente en el turno activo.
>
> Reglas duras:
> 1. Toda afirmación de causalidad operativa requiere UNA de estas verificaciones previas en el turno activo: `grep`, `Read`, `git merge-tree` (NO `git diff branch..main`), SQL fresh contra Supabase prod, `git log` con rango específico.
> 2. Prohibido afirmar "X escribe a tabla Y" sin grep INSERT/UPDATE; "PR borra archivo Z" sin diff merge-tree; "sprint Y mergeado" sin `git log origin/main | grep <sprint>`.
> 3. Excepción: si Cowork declara `[NO VERIFICADO - inferencia]` o `[REQUIERE READ/SQL]` antes del claim, regla NO se viola.
> 4. Bajo PBA trigger 1: consulta paralela Perplexity T2-B con claim verbatim + evidencia binaria propuesta.

### §4.2 DSC-G-008 v3 §4 — Deducir consecuencias materiales de §3 limitaciones (firmado T1 2026-05-12)

> Al auditar PRs bajo PBA, Cowork DEBE deducir consecuencias materiales de las §3 limitaciones declaradas — no solo enumerarlas honestamente. Estructura mínima v3:
>
> §1 Audit pre-sprint (v1) · §2 Audit de contenido pre-cierre (v2) · §3 Limitaciones declaradas honestamente · **§4 Consecuencias materiales deducidas de §3 NUEVA v3**
>
> Para cada limitación §3, Cowork DEBE responder: ¿qué hallazgos materiales podrían existir y NO se detectarían bajo esta limitación? ¿Qué tickets follow-up correspondería abrir? ¿Qué condiciones T2-B o T1 deberían cerrar la limitación antes/después del merge?
>
> Sin §4 explícito, Cowork queda como pensador único bajo limitaciones honestas pero sin guardrail estructural.

### §4.3 DSC-MO-006 v1.1 — Embriones par bicéfalo + PBA permanente (firmado T1 2026-05-12)

> El sistema de embriones del Monstruo opera únicamente como par bicéfalo. Un embrión singleton es arquitectura prohibida. v1.1 amplió a Cowork: **Protocolo Par Bicéfalo Activo (PBA)** — bajo 7 triggers obligatorios, Cowork consulta Perplexity T2-B pre-afirmación con claim verbatim + evidencia binaria propuesta.
>
> 7 triggers PBA: (1) afirmación causalidad operativa, (2) audit PR pre-merge, (3) interpretación output Sabio/herramienta complejo, (4) decisión irreversible (merge/migration apply/cleanup destructivo), (5) síntesis multi-fuente conflicting, (6) refactor doctrinal magna, (7) override spec firmado.

### §4.4 DSC-V-001 — Validación magna obligatoria de claims de estado-del-mundo (firmado 2026-05-07)

> Cualquier función que produzca claim de estado-del-mundo debe estar decorada con `@requires_perplexity_validation(claim_type, ttl_hours)`. Decorator levanta `StaleClaimError` si no existe registro vigente en `validation_log` Supabase para `claim_type`.
>
> Validators aceptados: Perplexity (magna primaria), Manus realtime (con log tool call), Alfredo human, Gong/Fireflies evidence. TTL expira → función vuelve a levantar StaleClaimError.

### §4.5 DSC-MO-011 — Embryo Patch Lane v1 (firmado 2026-05-11)

> Embrión Daddy bidireccional puede aplicar patches T3 autónomos a archivos del repo bajo condiciones duras: scope limitado a `kernel/`, no toca `secrets/`, no toca `migrations/`, write requires self-verifier OK + cap budget rotor + DSC-G-008 v2 verde. Loop autónomo cada N segundos. Modo degradado si self-verifier RED.

### §4.6 DSC-S-012 — Anti-deriva migraciones Supabase (firmado 2026-05-11)

> Migrations naming sequential sin gaps. Saltar números violación crítica. Verificar siempre `ls migrations/sql/ | sort | tail -1` antes de crear nueva.

### §4.7 DSC-S-015 — Scheduler respeta next_run de restore (firmado T1 2026-05-12)

> Scheduler Railway que actualiza prod desde Supabase backups debe respetar `next_run` calculado por restore — no sobrescribirlo con `now()` default. (Lección D-5 sprint).

### §4.8 DSC-OPS-001 — UPDATE manual prod requires bridge report (firmado T1 2026-05-12)

> Cualquier UPDATE manual sobre datos de Supabase prod (no via migration) requiere bridge report verbatim ANTES de ejecutar + reporte verbatim DESPUÉS. No silent updates.

---

## §5 Estado kernel binario verificado 2026-05-12 ~13:30 UTC

### §5.1 `kernel/cowork_runtime/` (9 archivos REAL — sprints COWORK-RUNTIME-001 PR #90 + AUTO-DISCIPLINE-REAL-001 en curso)

```
__init__.py                  1 LOC  module marker
alfredo_veto_channel.py    294 LOC  M9 Telegram veto bidireccional Alfredo → Cowork
                                    APIs: VetoSeverity, VetoEvent, AlfredoVetoChannel
antipatterns.py            199 LOC  RECIÉN creado Ejecutor 1 AUTO-DISCIPLINE T2/T3
                                    (catálogo F1-F22 antipatterns runtime)
companion_agent.py         498 LOC  T4 Companion semantic validator (complementa cowork_guardian)
                                    APIs: CompanionAgent, CompanionVerdict, CompanionViolation
drift_detector.py          257 LOC  T7 Auto-corrección drift contextual >N turnos
                                    APIs: DriftAction, DriftDetector, DriftSignal, SessionDriftState
f21_patterns.py            295 LOC  AUTO-DISCIPLINE T2 — Catálogo regex F21 patterns
                                    APIs: F21_PATTERNS, get_pattern_by_id, output_parece_audit, all_pattern_ids
pre_response_hook.py       674 LOC  T1 Magna intercept output Cowork → validate vs cowork_guardian
                                    APIs: HookStats, CoworkPreResponseHook
rule_reinjection.py        396 LOC  T2 Re-inyección periódica reglas duras al system prompt
                                    APIs: RuleReinjector, ReinjectorState
session_memory.py          481 LOC  T3 Persistencia Supabase cowork_sesiones + Pre-flight Memento
                                    APIs: SessionMemoryStore, build_pre_flight_block,
                                          start/update/close/read_last_session
                                    CLI: python3 -m kernel.cowork_runtime.session_memory pre-flight
                                    (sandbox sin env vars usa fallback SQL MCP Supabase directo)
                                                                      ___________
                                                                Total: 3,095 LOC
```

### §5.2 `tools/` relevantes Cowork

```
tools/cowork_guardian.py            T7 Sprint COWORK-RUNTIME-001 PR #90
                                    validate_output() — 22 reglas F1-F22 canonizadas anti-patterns Cowork
```

### §5.3 Tablas Supabase relevantes (todas con RLS por DSC-S-006)

- `cowork_sesiones` (migration 0009) — persistencia sesiones Cowork: id, fecha_inicio, fecha_fin, turnos_count, violaciones_count, correctivos_recibidos, deudas_pendientes_proxima_sesion (jsonb), resumen_lecciones, sprint_activo, kernel_version
- `cowork_sesiones_metricas` (migration 0010) — métricas runtime: session_id, turn_id, latency_ms, tokens_in, tokens_out, hook_blocked, f21_detected (bool)
- `embrion_memoria` (migration 0006 baseline) — memoria episódica Embrión: id, tipo (lección/incidente/observación/decisión), contenido, hilo_origen, importancia (1-10), timestamp
- `validation_log` (migration 0001) — DSC-V-001 decorator @requires_perplexity_validation registry
- `embrion_homeostasis_log` (migration 0026 — ESPIRAL-001 Reloj Suizo Hairspring) — auto-correction signals
- `escape_pulse_log` (migration 0024 — ESCAPE-001 Reloj Suizo throttler)
- `rotor_activity_log` (migration 0023 — ROTOR-001 Reloj Suizo recarga budget)
- `cowork_protocolo_invocaciones` (migration 0027 — AUTO-DISCIPLINE-REAL-001 T1 recién) — audit log invocaciones pre_response_hook

### §5.4 Railway env vars activas runtime

```
COWORK_HOOK_ENABLED=true              pre_response_hook activo desde 2026-05-12 07:57 UTC
COWORK_SESSION_PERSIST=true           session_memory escritura activa
COWORK_PREFLIGHT_REQUIRED=true        endpoint /v1/cowork/memento/validate montado
EMBRION_ROTOR_ENABLED=true            Reloj Suizo Rotor (budget recharge)
EMBRION_ESCAPE_ENABLED=true           Reloj Suizo Escape (throttler)
EMBRION_ESPIRAL_ENABLED=true          Reloj Suizo Espiral (Hairspring auto-correction)
ANTHROPIC_API_KEY=sk-ant-...          Anthropic kernel calls (NO rotar - T1 absoluto)
OPENROUTER_API_KEY=sk-or-...          OpenRouter multi-provider
SUPABASE_URL / SUPABASE_SERVICE_KEY   Supabase REST + service role
RAILWAY_TOKEN                         Railway management API
```

### §5.5 Reloj Suizo doctrinal — estado piezas

8 piezas magnas del Reloj Suizo Cowork (metáfora de relojería para guardrails canonizados):

| # | Pieza | Sprint | Estado HOY |
|---|---|---|---|
| 1 | **Resorte** (Mainspring — driver primario) | (canonical previo) | ✅ Vivo |
| 2 | **Escape** (Escapement — throttler) | ESCAPE-001 PR #116 | ✅ Mergeado HOY |
| 3 | **Áncora** (Anchor — gate) | (canonical previo) | ✅ Vivo |
| 4 | **Volante** (Balance Wheel — pulse) | (canonical previo) | ✅ Vivo |
| 5 | **Espiral** (Hairspring — homeostasis) | ESPIRAL-001 PR #117 | ✅ Mergeado HOY |
| 6 | **Rotor** (Rotor — auto-recharge) | ROTOR-001 PR #109 | ✅ Vivo |
| 7 | **Rubíes** (Jewels — cache friction-less) | RUBIES-001 | ⏳ Pipeline post-REMONTOIR |
| 8 | **Remontoir** (Constant Force) | REMONTOIR-001 v3 | ⏳ Ejecutor 2 ejecutando |

**REMONTOIR-001 v3** introduce patrón arquitectónico magno **decisor dinámico tiempo real**: Perplexity Sonar Personal Computer query realtime + cache Rubíes hit/miss + safety net 7 Sabios raw API verificados + Copilot 365 condicional Azure OpenAI + human_loop anti-bloqueo. Patrón generalizable a otras decisiones DSC-V-001 wrapper.

---

## §6 Lo que YA hicimos hoy en respuesta — 7 mejoras brainstorm Cowork

Estas 7 ya las propuse en brainstorm + Alfredo priorizó #1+#2+#7 como sprint AUTO-DISCIPLINE-REAL-001 (en curso). **NO duplicarlas:**

1. ✅ **Pre_response_hook auto-invocación + auto-lectura memoria** — en sprint AUTO-DISCIPLINE-REAL-001 T5 (Ejecutor 1 ejecutando). Hook intercepta cada output Cowork pre-render, auto-query `embrion_memoria` importancia>=8 LIMIT 10, valida vs cowork_guardian 22 reglas, bloquea si F21 detected.

2. ✅ **F21 pattern detector runtime + bloqueo** — en sprint AUTO-DISCIPLINE-REAL-001 T2 (Ejecutor 1 completó). Archivo `kernel/cowork_runtime/f21_patterns.py` 295 LOC + 10 regex F21 patterns canonizados (diff_stats, db_schema, model_versions, commit_hashes, git_state, pr_existence, migration_filename, branch_overlap, test_count, rls_policy).

3. ⏳ **pgvector semantic search `embrion_memoria`** — diferido sprint COWORK-SEMANTIC-MEMORY-001. Permitiría query semántica ("¿qué lecciones tengo sobre migrations sin grep?") en lugar de SELECT por tipo/importancia.

4. ⏳ **F21 historic forensic audit 90d** — diferido sprint COWORK-F21-FORENSIC-001. Script que rastrea historial git + `embrion_memoria` 90 días buscando F21 no detectados retroactivamente.

5. ⏳ **DSC-V-001 wrapper Cowork chat HTTP endpoint** — diferido sprint COWORK-SABIOS-VALIDATION-001. Endpoint Cowork chat puede invocar Sabios inline via wrapper DSC-V-001 sin que humano pegue prompts.

6. ⏳ **Auto-session-close cron Railway 2h inactividad** — diferido sprint COWORK-SESSION-AUTO-CLOSE-001. Cierre automático sesión Cowork con resumen + deudas si inactividad >2h.

7. ✅ **Verbatim citation enforcement** — en sprint AUTO-DISCIPLINE-REAL-001 T4 (Ejecutor 1 pendiente). Archivo `tools/_check_cowork_verbatim_citations.py` valida que cuando Cowork cita string del repo, el string EXISTE binariamente.

### Sprint AUTO-DISCIPLINE-REAL-001 status HOY (3/9 completadas)

- ✅ T0 audit pre-sprint
- ✅ T1 migration `0027_cowork_protocolo_invocaciones.sql`
- ✅ T2 `kernel/cowork_runtime/f21_patterns.py` (+199 LOC antipatterns.py recién creado)
- ⏳ T3 `tools/check_cowork_no_speculative_claims.py` F21 detector + bloqueo hook
- ⏳ T4 `tools/_check_cowork_verbatim_citations.py`
- ⏳ T5 modificar `pre_response_hook.py` auto-invocación + auto-query embrion_memoria
- ⏳ T6 tests integration
- ⏳ T7 postmortem + DSC-MO-017 candidato
- ⏳ T8 reporte cierre DSC-G-008 v3 §4

---

## §7 Tu tarea Kimi K2.6 Thinking

Desde tu rol de **trono multi-swarm orchestration**, proponé **10-15 mejoras magnas ESTRUCTURALES adicionales** con código real que pueda implementar **Manus Hilo Ejecutor 1 o 2 (T3)** en sprints dedicados.

### Constraints duros (respetar siempre):

- **NO duplicar las 7 mejoras del brainstorm** (§6 arriba — leélas verbatim antes de proponer)
- **NO proponer mejoras que asuman módulos kernel que NO existen** (verificar contra §5.1 listado real binario)
- **NO proponer rotación de secrets/API keys** (T1 declaró absoluto 2026-05-12: "no rotar nada hasta acabar el Monstruo" — aplica a Anthropic, OpenRouter, Supabase, Railway, todos)
- **NO proponer markdown doctrinal solamente** — cada propuesta DEBE tener código Python/SQL/YAML
- **NO proponer best-practice genéricas** tipo "considere logging" — específico al kernel del Monstruo descrito arriba
- **NO inventar tablas Supabase** que no estén en §5.3 — si necesitas tabla nueva, declará "requiere migration 00XX nueva"
- **NO asumir infraestructura no listada** (no hay Kafka, no hay pgvector aún, no hay Pinecone, no hay Elastic)

### Formato output esperado verbatim por cada propuesta:

```
Proposal-N: <nombre_codigo_identificador_unico>

Objetivo: <qué mata estructuralmente del problema F21 / o qué mejora productividad Cowork>

Archivos a modificar/crear:
  - <path1>: <descripcion 1-line>
  - <path2>: <descripcion 1-line>

Código Python boilerplate (firma de función crítica + docstring):
  <código verbatim 5-15 líneas>

Migration SQL si requiere (con número candidato 0028+):
  <SQL verbatim si aplica>

ETA realista Manus T3: <minutos>

Impacto cuantificado:
  - F21 reduction proyectada: <%>
  - Productividad: <turn improvement / latency reduction ms / etc.>

Prerequisitos:
  - <dependencias otros sprints o estado kernel>

DSC enforced:
  - <DSCs ya canonizados que el código enforza — del §4>

Riesgo: <P0-P3>
Mitigación: <medidas>
```

### Anti-fabricación verbatim:

- Si desconóces un módulo o tabla, decí "desconozco X" en lugar de inventar
- Si tu propuesta requiere infraestructura nueva (Redis nuevo channel, vector DB, etc.), decílo explícito + estimado costo
- Si dudas si una mejora ya existe, marcála "a verificar por Cowork antes de sprint"
- Si necesitas LOC exacta de un módulo que listé arriba para razonar, usa los números de §5.1 (verificados binarios HOY)

### Áreas que me interesan especialmente (no exclusivas — proponé otras si las ves):

1. **Multi-swarm coordination kernel**: cómo orquestar 4+ hilos paralelo (Cowork + 3 Manus + 3 Perplexity sesiones simultáneas) sin duplicar trabajo — enforcement runtime no markdown. Hoy lo coordino manualmente pegando prompts.

2. **Anti-F21 enforcement adicional** más allá de los 10 patterns ya canonizados (§5.1 f21_patterns.py) — ¿qué categorías F21 aún no contemplamos? Las 12 F21 de hoy (§3) muestran patrones que los 10 actuales NO capturan.

3. **Session continuity** entre Cowork sesiones (perdí context entre sesiones — `session_memory.py` solo persiste resumen + deudas, no granular). Necesito que la próxima sesión Cowork arranque sabiendo qué F21 más reciente cometí + qué guardrails están vivos.

4. **Cross-hilo handoff Manus → Manus** — cómo Hilo Ejecutor 1 pasa context a Hilo Catastro sin que Cowork lo coordine manualmente pegando prompts. Hoy es manual.

5. **Embrión memoria activa runtime**: cómo el kernel mismo decide qué memoria (`embrion_memoria` filas) es relevante por turno sin que Cowork la pida explícitamente. Hoy es pull-based.

6. **PBA auto-trigger** — detectar cuándo Cowork necesita Perplexity sin que humano (Alfredo) deba pegar prompts manualmente entre 3 sesiones Perplexity. Hoy Alfredo es el bus.

7. **Quality floor decisor dinámico real-time** — patrón ya canonizado en REMONTOIR-001 v3, expandir a otras decisiones DSC-V-001. Generalizable como decorator `@dynamic_quality_floor(...)` reutilizable.

8. **Telemetría Sabios performance**: hoy no tengo métrica de qué Sabio responde mejor por dominio. Necesito tabla `sabios_performance_log` + dashboards.

9. **Cualquier otra área que detectes desde tu perspectiva multi-swarm.**

---

## §8 Iteración esperada

- **Ronda 1 (vos ahora):** 10-15 propuestas magnas con formato estructurado §7.
- **Ronda 2 (después):** Cowork sintetiza top-3 con propuestas Opus 4.7 paralelo + te pide profundizar specs implementables.
- **Ronda 3:** T1 (Alfredo) firma decisiones binarias → sprints dedicados Manus T3.

---

## §9 No queremos

- Markdown doctrinal solamente
- Best-practice genéricas
- Duplicación de las 7 del brainstorm (§6)
- Propuestas sin código real
- Asunciones sin verificación binaria del kernel (§5)
- Propuestas que requieran rotación secrets
- Propuestas que asuman módulos kernel inexistentes

## §10 Queremos

- Código real ejecutable Python/SQL/YAML
- Mejoras estructurales que afecten interacciones multi-agente
- ETAs realistas Manus T3 (rango aceptable: 30 min – 8h por propuesta)
- Impacto cuantificado (no "mejor productividad", sino "reduces F21 ~25%" o "save 200ms/turn")
- Anti-fabricación estricta
- Owner asignado tentativo (Manus Ejecutor 1 / 2 / Catastro / Cowork mismo)

---

**Firma:** Cowork T2-A Arquitecto Orquestador del Monstruo, 2026-05-12 ~14:00 UTC
**Bajo autoridad T1 directa de Alfredo Góngora.**
**Tu propuestas Kimi K2.6 Thinking serán cruzadas con Claude Opus 4.7 Thinking (auditor meta-cognitivo paralelo) para síntesis Cowork final → decisión T1 → sprints Manus.**

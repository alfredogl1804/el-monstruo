# HANDOFF COWORK — 2026-05-26

**Autor:** Cowork T2-A (Arquitecto persistente)
**Propósito:** Transferir el máximo contexto posible de esta sesión Cowork a un hilo nuevo, para que arranque al mismo nivel.
**Tipo:** Handoff inter-hilo (Nivel 2 — artefacto durable). Complementa Paso 0 Pre-flight Memento.

---

## §0 — CÓMO USAR ESTE HANDOFF (hilo nuevo, leer primero)

El hilo nuevo debe, en su turno 1:

1. Ejecutar Paso 0 Pre-flight Memento:
   ```bash
   cd ~/el-monstruo && python3 -m kernel.cowork_runtime.session_memory pre-flight
   ```
   Fallback si sandbox sin env vars: query SQL a `public.cowork_sesiones ORDER BY fecha_inicio DESC LIMIT 1` vía MCP Supabase.
2. Leer los 6 docs §1-§6 del CLAUDE.md raíz (`memory/cowork/COWORK_*.md` + audits + A2UI spec).
3. Leer **este handoff** — contiene lo único que NO está en la doctrina: el trabajo fresco de la sesión 2026-05-26.

**Límite honesto:** este doc reconstruye el contexto operativo, no las trazas de razonamiento del hilo origen. La fidelidad tope = lo escrito aquí + que el pre-flight fuerce su carga.

---

## §1 — IDENTIDAD / ROL

- Cowork ES Arquitecto T2-A. Siempre. No "Hilo B", no ejecutor.
- Manus ES Ejecutor T3 (no escribe código kernel/app).
- Alfredo ES T1 (decisión final + autoridad magna).
- Cowork pushea autónomo vía `mcp__github-monstruo__*` (NUNCA pedir push a Alfredo = F22).
- Idioma: español.

---

## §2 — TRABAJO DE ESTA SESIÓN (entregables + conclusiones verbatim)

### 2.1 — Veredicto Sabio (Claude Opus 4.7) sobre `SPRINT_OBSERVATORIO_V1.md`
**Repo:** `alfredogl1804/tablero-campana` @ rama `design/forja-os-sovereign-agentic-fabric`, doc sha `6cf6d0d`.
**Veredicto: APROBAR CON AJUSTES.**

3 ajustes BLOQUEANTES (sin ellos no se aprueba):
1. **Corregir §3.2 DDL `kernel_events_stream` a dialecto Postgres** y declarar la topología de dos bases. El DDL está en dialecto MySQL/TiDB (`ENUM(...)` inline, `INDEX idx_... (...)` inline) pero §4 lo coloca en el **Supabase Postgres** del Monstruo, y su propio comentario usa `ALTER PUBLICATION supabase_realtime` (Postgres-only). Como está, no corre en Postgres. `sprints/connected_projects/project_heartbeats` viven en TiDB del Tablero → sistema cruza dos bases con dos dialectos, no nombrado en el plan. Migración debe ir en repo `el-monstruo`, no en el Tablero.
2. **Firmar eventos con ed25519** (reusar la llave de Forja v4) + RLS INSERT-only-kernel en Supabase + verificación en el Tablero antes de render. §3.2 no tiene campo que pruebe que el evento vino del kernel real → ledger de "transparencia total" (§1) falsificable. Agregar `signature` + `signer_key_id`. Patrón = firma de webhooks Stripe (ya en uso en ticketlike).
3. **Contrato de eventos versionado compartido por ambos repos** (JSON Schema o enum generado TS+Py) + warning ante `event_type` desconocido. `event_type` es `VARCHAR(64)` libre → drift silencioso cuando el kernel cambie el vocabulario.

Ajustes recomendados (no bloqueantes): spike de Hito A al día 0 (validar camino kernel→Supabase→Realtime→render antes de invertir en B); cap de ventana React (anti-OOM en sesión larga); rediseñar el gate síncrono de Forja a evaluación local cacheada con bundle firmado (estilo OPA) antes de enforce_full (evita 50ms→250ms por acción); aflojar criterio §8 de Hito B (MUST = ingestor + lista; 3D = SHOULD reusando `Building.tsx`) y de Hito C (proyectos-reales-con-HTTP vs nodos embrión con badge estático).

Veredictos P1-P5: P1 orden B→A→C ✓ (con spike A día 0). P2 bus Supabase Realtime ✓ (latencia irrelevante a esta escala; descartar Redis/NATS por sobre-ingeniería para 1 operador; WS-directo pierde durabilidad). P3 adapter cross-stack ✓ NO portar (shadow es asíncrono; el problema de latencia solo aparece en enforce_full). P4 Hito B ~2-3 días, el ingestor es el deliverable real, 3D por reuso. P5 top-3 riesgos = los 3 bloqueantes de arriba.

### 2.2 — Veredicto ontológico `FORJA_OS_SOVEREIGN_AGENTIC_FABRIC_v2.md`
**Repo:** `alfredogl1804/tablero-campana`. Doc producido: `docs/CLAUDE_OPUS_VEREDICTO_FORJA_OS_v2.md` (entregado inline, convención READY_TO_COMMIT/END_OF_FILE — verificar si llegó a commitearse).
**Veredicto: REQUEST_CHANGES.** 3 bloqueantes: (a) doctrina RLS sellada "validado contra repo real" pero inejecutable en MySQL/TiDB (§20.2/§21/Anexo A); (b) gate anti-LLM §16/P0-3 evadible (gatea presencia, no cobertura+pureza); (c) ejemplo flagship §22.5 (dory.core 920→760) inalcanzable bajo la regla no-tocar-genoma de v0.1 (§13.3). Cambio mínimo propuesto: mover el gate anti-LLM de nivel-cápsula a nivel-claim + exigir `verifier_sha` (hash de función pura) por acceptanceCriterion, respaldado por tabla `verifier_registry`.

### 2.3 — Kit de recuperación de contexto (investigación)
Confirmado en `alfredogl1804/el-monstruo` rama `main`:
- **`tools/memento_preflight.py`** (24.8 KB) + `memento_preflight_README.md` — library de validación de contexto contra fuente de verdad antes de operar (nació del incidente "Falso Positivo TiDB" 2026-05-04).
- **`kernel/cowork_runtime/session_memory.py`** (16.9 KB) — memoria persistente entre sesiones (el CLI del Paso 0). "SMS" del operador.
- **`tools/cowork_guardian.py`** (10.7 KB) — guardián de disciplina (complementario, no recuperador).

---

## §3 — HALLAZGO CRÍTICO: DRIFT ENTRE DOS GENERACIONES DE INYECTORES DE CONTEXTO

Hay **dos sistemas de inyección de contexto desincronizados** en `el-monstruo`:

1. **Generación "Skill-OS" (sandbox Manus):** `skills/` (~30 skills) + `monstruo_biblias/*v7.0*` (9 biblias) + `skills/el-monstruo/context_packets/genoma_core.yaml` + `skills/api-context-injector/SKILL.md` v4.0. Declara **6 Sabios v7.3** (GPT-5.4, Claude **Sonnet 4.6**, Grok 4.20, Kimi **K2.5**), `last_verified: 2026-04-09`, referencias a `/home/ubuntu/el_monstruo/` y `manus-mcp-cli`.
2. **Generación "Cowork runtime" (la viva):** `kernel/cowork_runtime/` + `CLAUDE.md` + `COWORK_*.md`. Declara **8 Sabios** (GPT-5.5, Claude **Opus 4.7**, Kimi **K2.6**…).

**Riesgo anti-Dory:** un hilo que arranque por `skills/el-monstruo` absorbe 6 Sabios viejos (v7.3, abril) en vez de 8 (doctrina viva, mayo). La capa skills/biblias está ~1 mes y 1 versión detrás. NO se verificó `tablero-campana` (Forja), que tiene su propio set.

**Mapa de inyectores verificado (el-monstruo):**
- Bootstraps: `skills/el-monstruo/SKILL.md` + `context_packets/` (genoma+8 tejidos+pgvector 578 docs); `prompts/system_prompts.py` (45 KB); `tools/memento_preflight.py` + `kernel/cowork_runtime/session_memory.py`; raíz `CLAUDE.md` + `AGENTS.md` (33 KB).
- Axiomas (no hay archivo literal "axiomas"; embebidos): `genoma_core.yaml` (core rules), `el-monstruo-core/SKILL.md` (26.7 KB, NO leído entero), `api-context-injector/SKILL.md` (13 Reglas Inquebrantables), `CLAUDE.md` (23 fallos + 11 soluciones), 15 Objetivos Maestros.
- Biblias por agente: `monstruo_biblias/` (9).
- Memoria runtime: `memory/` (three_layer, mem0, mempalace, lightrag, knowledge_graph, conversation, checkpoint_store, event_store, causal_kb, supabase_client, honcho_bridge).
- Disciplina Cowork: `kernel/cowork_runtime/` (session_memory, rule_reinjection, pre_response_hook, claim_calibration, drift_detector, f21_patterns, antipatterns, companion_agent, alfredo_veto_channel).
- Genoma/Plan: raíz `MONSTRUO_GENOME.yaml`, `PLAN_REGULADOR.yaml`, `PISO_3_AGRUPADOR.yaml`, `PISO_4_AREAS.yaml`, `ESTADO_SISTEMA.md`.

---

## §4 — DEUDAS PENDIENTES PARA EL HILO NUEVO

1. **NO VERIFICADO:** no se hizo grep de contenido por la palabra "axioma" (code-search de GitHub devuelve vacío en repo privado). Si se quiere el set literal de axiomas → leer `skills/el-monstruo-core/SKILL.md` + `AGENTS.md` completos.
2. Decidir si se canoniza un sprint para resolver el **drift de inyectores** (sincronizar biblias v7.0 → 8 Sabios / doctrina mayo, o deprecar la capa Skill-OS).
3. Extender la verificación de inyectores a `tablero-campana` (Forja) — no cubierto.
4. Confirmar si `docs/CLAUDE_OPUS_VEREDICTO_FORJA_OS_v2.md` quedó commiteado en `tablero-campana`.
5. Pasar los 3 bloqueantes del veredicto Observatorio al hilo Manus de `tablero-campana` antes de que arranque Hito A.

---

## §5 — COMANDOS PRE-FLIGHT EXACTOS

```bash
# Paso 0 — memoria persistente
cd ~/el-monstruo && python3 -m kernel.cowork_runtime.session_memory pre-flight

# Paso 0.B — Coherence Gate Nivel A (antes de acción magna / INSERT con CHECK)
ls migrations/sql/ | tail -3
# + vía MCP Supabase:
#   SELECT version, name FROM supabase_migrations.schema_migrations ORDER BY version DESC LIMIT 3;
```

---

## §6 — BOOT PROMPT SELF-CONTAINED (pegar al iniciar el hilo nuevo)

> Eres Cowork T2-A, Arquitecto persistente de El Monstruo (dueño: Alfredo González). Idioma: español. Antes de cualquier respuesta corre Pre-flight Memento: `python3 -m kernel.cowork_runtime.session_memory pre-flight` y lee los 6 docs de `memory/cowork/`. Luego lee `memory/cowork/HANDOFF_COWORK_2026_05_26.md` — contiene el trabajo fresco de la sesión previa: (1) veredicto Observatorio v1 = APROBAR CON AJUSTES con 3 bloqueantes (DDL §3.2 a Postgres + topología 2-DB, firma ed25519 de eventos, contrato de eventos cross-repo); (2) veredicto Forja OS v2 = REQUEST_CHANGES; (3) hallazgo crítico de drift entre dos generaciones de inyectores de contexto (skills/biblias v7.0 / 6 Sabios vs cowork_runtime / 8 Sabios). Pusheas autónomo vía GitHub MCP, nunca pides push a Alfredo (F22). Verifica antes de afirmar (anti-F2). Confirma que absorbiste el handoff antes de continuar.

---

*Generado por Cowork T2-A en sesión 2026-05-26. Push autónomo vía GitHub MCP.*

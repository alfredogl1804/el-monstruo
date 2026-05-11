# Cowork — Decisiones Vivas del Monstruo

**Propósito:** Decisiones tomadas que están en producción HOY. Stack, arquitectura, patrones. NO aspiraciones — lo que existe y opera.

**Estado:** v0.1 — Cowork verificó la mayoría hoy. Iterar cuando cambie cualquier decisión activa.

**Última actualización:** 2026-05-11 (Cowork T2 — cierre Sprint EMBRION-NEEDS-001 Tarea 2 + audit PR #86).

---

## 1. Stack Técnico Vivo

| Capa | Decisión | Evidencia |
|---|---|---|
| Kernel | Python 3.11+ / FastAPI / LangGraph | `kernel/main.py`, healthy en Railway |
| Orquestador | LangGraph (DSC-MO-003) | Sprint 27+ |
| Checkpointer | PostgresSaver de Supabase (DSC-MO-001) | Decidido sobre Temporal.io por costo + integración |
| BD principal | Supabase (PostgreSQL + RLS + pgvector) | Proyecto `xsumzuhwmivjgftsneov` |
| Cache | Redis | Railway |
| Deploy backend | Railway | `el-monstruo-kernel`, `ag-ui-gateway`, `command-center` |
| Observabilidad | Langfuse + OTEL (DSC-MO-004) | v4.5.0 |
| App móvil | Flutter (macOS + iOS + Android) | `apps/mobile/` — congelada en Sprint 48 |
| Gateway móvil | Python/FastAPI + WebSocket (AG-UI) | `apps/mobile/gateway/` |
| Command Center | React + tRPC (Manus WebDev) | monstruodash-ggmndxgx.manus.space |
| Bot Telegram | python-telegram-bot v20+ | webhook al kernel `/v1/embrion/telegram/webhook` |
| MCP servers | FastMCP 3.2.4 | 3 servers validados Sprint 27 |
| DeepEval | Quality gate 80% | v3.9.7 |

**Naming canónico de credenciales:** `SUPABASE_SERVICE_KEY` (sin `_ROLE`) — DSC-S-007 firmado 2026-05-10.

---

## 2. Los 8 Sabios Canónicos (DSC-V-001)

Versiones más potentes al 2026-05. Uso: validación adversarial de decisiones magnas.

| Sabio | Modelo | Provider | Especialidad |
|---|---|---|---|
| GPT-5.5 Pro / Pensamiento | gpt-5.5 | OpenAI | Razonamiento profundo, doctrina |
| Claude Opus 4.7 / Pensamiento | claude-opus-4.7 | Anthropic | Metodología, regla de tres |
| Gemini 3.1 Pro / Pensamiento | gemini-3.1-pro | Google | Performance/latencia, 2M context |
| Grok 4 Heavy | grok-4 | xAI | Datos X/Twitter, razonamiento adversarial |
| DeepSeek R1 | deepseek-r1 | DeepSeek | Razonamiento técnico open-source |
| Perplexity Sonar / Personal Computer | sonar-pro | Perplexity | Research tiempo real, browsing |
| Kimi K2.6 / Thinking | kimi-k2.6 | Moonshot | Multi-swarm orchestration (trono) |
| Copilot 365 | gpt-5 wrapper | Microsoft | Integración M365 |

**Reglas:**
- Mínimo 3 Sabios para validación profunda
- Validación ligera con 1 Sabio + evidencia documental aceptable para Tier 2
- Ejemplo histórico: Reloj Suizo 8/8 unanimidad para Opción C (núcleo interno con arquitectura extraíble)

---

## 3. Arquitectura del Embrión (Sprint EMBRION-NEEDS-001 + 002)

**Pieza central:** `kernel/embrion_loop.py` — proceso autónomo 24/7. Doctrina del silencio: NO se modifica salvo spec firmado explícitamente con razón canonizada.

**Componentes operativos:**

| Componente | Archivo | Estado |
|---|---|---|
| Loop principal | `kernel/embrion_loop.py` | ✅ Vivo, 20+ latidos/2h verificado 2026-05-10 |
| Budget Tracker | `kernel/embrion_budget.py` | ✅ Cap $0.25/cycle pre-flight |
| Self-Verifier 3-decisiones | `kernel/embrion_self_verifier.py` (en `_think()`) | ✅ D1 PURPOSE + D2 NOVELTY + D3 VERIFIABLE. 2/3 NO = abort. **Hotfix PR #88 aplicado: severity `critical`/`warning` (compatibles con CHECK constraint de `loop_detection_log`).** |
| Write Policy con HITL | `kernel/embrion_write_policy.py` | ✅ propose() → approve() → execute_next(). UNIQUE idempotency_key. Optimistic concurrency |
| Telegram HITL bidireccional | `kernel/runner/telegram_notifier.py` + webhook | ✅ Botones inline approve/reject. `approved_by='telegram:{chat_id}'` registrado |
| Cron worker proposal_processor | `kernel/runner/proposal_processor.py` | ✅ Servicio Railway separado. Cierra ciclo HITL automáticamente |
| Cowork bridge | `embrion_memoria` table + insert directo via MCP | ✅ Canal canónico Cowork↔Embrión↔Manus |
| Multi-canal HITL | `notify_hitl()` en `embrion_write_policy.py` | ✅ cowork_bridge + telegram independientes |
| Audit middleware | `kernel/audit_middleware.py` (S-003.B Tarea 1) | 🟡 En branch Cowork pendiente push |

**Estados de proposals:**
```
pending → approved → executing → executed | failed
        → rejected
        → expired (TTL default 24h)
```

**Variables de entorno operativas:**
- `EMBRION_PROPOSAL_TTL_HOURS=24`
- `EMBRION_HITL_CHANNEL=cowork_bridge` (default, multi-canal)
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `TELEGRAM_WEBHOOK_SECRET`
- `EMBRION_BUDGET_TRACKER_ENABLED=true`
- `EMBRION_SELF_VERIFIER_ENABLED=true`
- `EMBRION_VERIFIER_NOVELTY_WINDOW_HOURS=24`
- `EMBRION_VERIFIER_JACCARD_THRESHOLD=0.85`

**Cierres canonizados — Sprint EMBRION-NEEDS-001:**

| Tarea | Estado | PR que la materializó | Notas |
|---|---|---|---|
| Tarea 1 — Budget Tracker | ✅ cerrada | PR #38 + hotfixes posteriores | `kernel/embrion_budget.py` activo en producción. Cap $0.25/ciclo, daily cap $30, HITL al 3er exceso. |
| **Tarea 2 — Self-Verifier 3-decisiones** | ✅ **cerrada de facto en `main` el 2026-05-11** | commit original `0ddb5e1` recuperado vía **PR #93** (rescate stash) + **hotfix PR #88** + integración en `_think()` vía **PR #90** | **PR #86 (canónico original del 2026-05-10) cerrado como OBSOLETO** por Cowork T2 tras audit binario DSC-G-008 v2. La versión de PR #86 contenía `severity="high" if abort else "low"` que viola el CHECK constraint `('warning' | 'critical' | 'emergency')` de `loop_detection_log`. Mergear habría sido regresión directa del hotfix. Audit en [`memory/cowork/audits/AUDIT_PR_86_DSC_G_008_v2_2026_05_11.md`](./audits/AUDIT_PR_86_DSC_G_008_v2_2026_05_11.md) (commit `bf03abb`). Notificación a Hilo Ejecutor 2 vía `embrion_memoria` id `d28687c1-31f2-4ca4-9528-fdf5d68dd642`. |
| Tarea 3 — Write Policy con HITL | ✅ cerrada | PR #44 + #47 | UNIQUE idempotency_key + optimistic concurrency. |
| Tarea 4 — Telegram HITL bidireccional | ✅ cerrada | PR #48 | Botones inline + webhook + chat_id whitelist. |
| Tarea 5 — Embrión-Daddy bidireccional | 🟡 **spec firmado, código pendiente** | **PR #81 (spec)** | Activador de Fase 2 del modelo de hilos. Tarea abierta — siguiente prioridad de la serie. |

**Notas de auditoría binaria 2026-05-11 (Cowork T2):**
- Tabla `loop_detection_log` extendida con 11 columnas via migración `migrations/sql/0003_loop_detection_log_self_verifier.sql` (en main, SHA `cf6c6dc`, 3,038 bytes).
- `kernel/embrion_self_verifier.py` en main: blob `25cfb35`, 15,908 bytes, incluye el hotfix de `severity`.
- 24 tests en `tests/test_embrion_self_verifier.py` (blob `1fcd291`, 14,240 bytes) + fixtures reales del bucle 30-abr y bucle 10-may.

---

## 4. El Reloj Suizo — 8 piezas (Capa 2 horológica)

DSC-MO-010 firmado 2026-05-10. Arquitectura `docs/ARQUITECTURA_RELOJ_SUIZO_v1.0.md`. Consulta 8 Sabios → Opción C unanimidad.

| Pieza | Función | Implementación |
|---|---|---|
| Resorte (Buffer Energía) | Almacena presupuesto (tokens, CPU, calls) | 🟡 `embrion_budget_state` |
| Escape (Throttler) | Libera energía en pulsos discretos | 🟡 Self-Verifier corta cycles vacíos |
| Áncora (Coordinador Ciclo) | Sincroniza escape con volante | 🟡 `kernel/embrion_scheduler.py` |
| Volante (Cron Interno) | Latido constante, nunca se detiene | ✅ `kernel/embrion_loop.py` |
| Espiral (Homeostasis) | Vuelta a estado base post-ráfaga | ❓ NO localizado |
| **Rotor (Reciclador)** | **Captura energía de actividad usuario** | ❌ **FALTA — pieza diferencial** |
| Rubíes (Caché Semántica) | Fricción cero, datos sin LLM | 🟡 `kernel/response_cache.py` |
| Remontoir (Estabilizador Calidad) | Output igual de bueno con presupuesto bajo o alto | 🟡 `kernel/adaptive_model_selector.py` |

**4 Gates canonizados (DSC-MO-010 v1.1, propuesto agregar):**
Para autorizar publicación SDK público (transición Premium → Magna):
1. 60-90 días en producción real
2. Repetición de incidentes documentada
3. Modelo de amenaza
4. 2 adaptadores "mock" mínimos

**Decisión Magna vs Premium (consulta 8 Sabios):**
- HOY: Premium (core desacoplado interno modular). Reversible.
- DESPUÉS: Magna (publicar API pública / open-source / compatibilidad prometida / gobernanza). Irreversible.

**Regla de Tres aplicada:** no extraer abstracción universal hasta tener ≥3 casos reales del Reloj operando. Hoy 1 caso (El Monstruo).

---

## 5. Capas Engranajes (Capa 1 mecánica)

`docs/ARQUITECTURA_ENGRANAJE_v1.0.md`. 4 propiedades físicas:

| Propiedad | Función | Estado |
|---|---|---|
| Inercia | Resistencia al cambio brusco de dirección | ✅ Mergeada (`feat(engranajes): Capa 1`) |
| Fricción | Pérdida controlada para evitar oscilación | ✅ |
| Resonancia | Sincronización entre componentes | ✅ |
| Holgura | Tolerancia entre piezas para evitar bloqueos | ✅ |

---

## 6. Las 8 Capas Transversales (Objetivo #9)

DSC-G-002 firmado: todo producto del Monstruo nace con 8 capas obligatorias.

| Capa | Implementación | Estado integraciones reales |
|---|---|---|
| 1. Ventas | `kernel/transversales/ventas/` + tests | 🟡 `implement()`+`monitor()` con stubs. **HubSpot key entregada, wiring real desconocido. Apollo/Clay NO. Salesforce NO.** |
| 2. SEO | `kernel/transversales/seo/` + 11 tests | ✅ End-to-end real (única cerrada) |
| 3. Publicidad | `kernel/transversales/publicidad/` + 13 tests | 🟡 Implementación parcial honesta. **Meta Marketing API DECLARADO. Google Ads NO. LinkedIn Ads NO.** |
| 4. Tendencias | `kernel/transversales/tendencias/` + 9 tests | 🟡 |
| 5. Operaciones | `kernel/transversales/operaciones/` + 10 tests | 🟡 |
| 6. Finanzas | `kernel/transversales/finanzas/` + 12 tests | 🟡 |
| 7. Resiliencia Agéntica | `kernel/sovereignty/` + Engranajes Capa 1 | 🟡 |
| 8. **Memento (anti-Síndrome-Dory)** | DSC-MO-008 + cowork_bridge + `memory/cowork/` | 🟡 Operativa parcial — este directorio es la pieza nueva |

**Hueco crítico identificado 2026-05-10:** las integraciones externas reales (Google Ads, LinkedIn, HubSpot wireado, Apollo/Clay, Salesforce) son **el músculo faltante de las capas comerciales**. Sin ellas, las capas son código que `implement()` strategy y `monitor()` métricas pero NO disparan campañas reales ni capturan leads reales.

---

## 7. Universo RLS — Estado al 2026-05-11

**120/120 tablas en schema `public` con RLS habilitado** (verificado binariamente por Cowork T2 el 2026-05-11 vía Supabase MCP). Universo limpio post **P0 RLS Fix `catastro_vision_generativa`** (PR #91, migración 0011, merge commit `f575b735`). Total `public` tables: 121 (1 sin RLS bajo excepción documentada). **Stale del valor 117/117 anterior corregido aquí.**

**Patrón canónico** (DSC-S-006 v1.1):
```sql
ALTER TABLE public.<tabla> ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_only"
  ON public.<tabla>
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
```

**Excepción canonizada:** tablas catálogo público pueden tener `anon_read_only` con DSC firmado caso por caso.

**Linter pre-commit:** `scripts/_check_rls_default.py` v1.1 con whitelist público.

**Workflow CI semanal:** `.github/workflows/rls-audit-weekly.yml` corre lunes 12:00 UTC, abre issue automático si detecta deuda. Requiere secrets `SUPABASE_ACCESS_TOKEN` + `SUPABASE_PROJECT_REF`.

**Workflow CI continuo (nuevo, post P0 RLS fix):** `.github/workflows/rls-audit-continuous.yml` corre diario a las 06:00 UTC.

---

## 8. Patrones Replicables (Cross-proyecto)

DSC-X-006 firmado: Convergencia Diferida. Proyectos arrancan autónomos con infra compartida y convergen en momentos elegidos cuando ambos prueban PMF.

| Patrón | Origen | Aplicable a |
|---|---|---|
| Stripe Checkout (DSC-X-002, DSC-LT-003) | LikeTickets | Marketplace, CIP, Mundo de Tata |
| Manus-Oauth scaffold (DSC-X-003) | Catastro-B | cualquier auth estándar |
| Barrido cruzado Drive→Notion→S3 (DSC-MB-003) | Crisol-8 | cualquier proyecto investigativo |
| Catastro extendido (DSC-G-007.x) | Sprint 86-89 | macroáreas futuras (infra, BD, APIs, etc.) |
| HITL bidireccional Telegram (Sprint EMBRION-NEEDS-001 T4) | Embrión | cualquier flujo de aprobación humana |
| RLS por defecto en tablas nuevas (DSC-S-006 v1.1) | S-002.6 | cualquier migración SQL futura |
| 4 Gates de transición Premium → Magna (DSC-MO-010) | Reloj Suizo | cualquier abstracción universalizable |
| Sistema de Realidad Ejecutable (DSC-S-011) | Hilo Ejecutor 2 (2026-05-11) | cualquier hilo del Monstruo que canonice claims factuales — verificación contra estado fresco antes de afirmar |
| Audit DSC-G-008 v2 antes de mergear (este audit PR #86) | Cowork T2 (2026-05-11) | cualquier merge a `main` — diff línea por línea + comparación binaria contra estado actual + falsadores |

---

## 9. Catastro Extendido (DSC-MO-009 + G-007.x)

**Estado en producción:**
- `catastro_modelos`: 39 productos en `inteligencia` + 2 en `vision_generativa` (post Sprint 89)
- `catastro_agentes`: 111 productos en 14 dominios (post Sprint 88.2)
- `catastro_tronos_agentes`: 14 tronos materializados con `bonus_curador` documentado

**14 dominios de macroárea AGENTES:**
1. agentes_desarrollo (trono: Manus, score 85)
2. agentes_vibe_coding (Lovable, 76+1)
3. agentes_multi_swarm (Kimi K2.6 Agent Swarm, 100)
4. agentes_investigacion (Perplexity Personal Computer, 76+1)
5. agentes_ejecutores (n8n + LLM nodes, 95)
6. agentes_creacion_audiovisual (Higgsfield, 55)
7. agentes_branding_diseno (Kittl, 55)
8. agentes_marketing_ventas (Clay, 80)
9. interfaces_usuario (Claude.ai, 76+1)
10. agentes_observabilidad_evals
11. **agentes_seguridad** (descubierto por Grok-4 en validación adversarial)
12. agentes_generalistas_autonomos
13. (vision_generativa relacionados)
14. (vision_generativa relacionados)

**Roadmap META Sprint 90+:** 6-7 macroáreas restantes propuestas (infraestructura, bases_de_datos, apis, observabilidad, hardware_personal, finanzas_y_pagos_ia).

---

## 10. Cómo se actualiza este documento

- Cuando cambia el stack técnico (versiones mayores, nueva tabla, nuevo servicio Railway)
- Cuando se canoniza nuevo Sabio o sale uno (raro)
- Cuando un componente del embrión cambia (`embrion_loop.py` modificado, nueva pieza Reloj Suizo, etc.)
- Cuando una Capa Transversal pasa de stub a real (ej: Google Ads se integra)
- Cuando RLS se modifica
- Cuando se canoniza patrón replicable nuevo
- Cuando se cierra (o no se mergea) una PR de sprint que afecta el embrión o el universo de tablas

---

## Referencias primarias

- `bridge/sabios_consulta_2026_05_10_reloj_suizo_universal.md` (consulta original 8 Sabios)
- `docs/ARQUITECTURA_RELOJ_SUIZO_v1.0.md`
- `docs/ARQUITECTURA_ENGRANAJE_v1.0.md`
- `discovery_forense/CAPILLA_DECISIONES/EL-MONSTRUO/DSC-MO-010_reloj_suizo_universalizable_interno.md`
- `bridge/REPORTE_MEGA_CATASTRO_SPRINT_88_3_CIERRE.md`
- `bridge/postmortem_sprint_embrion_needs_001.md`
- `kernel/embrion_loop.py` (CAUTION: doctrina del silencio)
- `kernel/embrion_write_policy.py`
- `kernel/runner/proposal_processor.py`
- `memory/cowork/audits/AUDIT_PR_86_DSC_G_008_v2_2026_05_11.md` (audit binario que cerró PR #86 como obsoleto)
- `bridge/HANDOFF_COWORK_NUEVO_2026_05_11.md` (handoff del Cowork saliente)

---

*Generado por Cowork 2026-05-10. v0.2 — 2026-05-11 actualización Cowork T2: cierre Sprint EMBRION-NEEDS-001 Tarea 2 + audit PR #86 + corrección RLS 117→120.*

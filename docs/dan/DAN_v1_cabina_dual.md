---
título: "DAN v1.1 — El Monstruo: Cabina Dual + Agente Manus Real (post-audit Cowork)"
versión: 1.1.0
estado: aprobado_para_implementación_con_paths_corregidos
fecha: 2026-05-27
autor: Manus B (orquestador) + Consejo de 6 Sabios v7.3 + audit Cowork
sintetizador: GPT-5.5 Pro
validación_post_consulta: Perplexity Sonar Reasoning Pro
validación_post_síntesis: Gemini 3.1 Pro + Grok 4 (score 0.81 / incorporación 0.95)
audit_independiente: Cowork (Hilo A) — bridge cowork_to_manus_DAN_v1_SPRINT_1_AUDIT_2026_05_27.md
changelog_v1.1:
  - hallazgo_A: "paths kernel reales: agui_adapter.py + engine.py + adaptive_model_selector.py + fallback_engine.py + config/model_catalog.py (NO dispatch_agent.py NI agui_runner.py — esos NO existen)"
  - hallazgo_B: "2 vectores de downgrade detectados: (1) FALLBACK_CHAINS clasificador/chat_rapido → gpt-4.1-nano, (2) budget pressure → gpt-4o-mini → gemma3:8b"
  - hallazgo_C: "3 catálogos paralelos a consolidar: config/model_catalog.MODELS + fallback_engine.PROVIDERS + adaptive_model_selector.MODEL_CATALOG"
  - hallazgo_D: "modelos prohibidos por DAN vivos en producción hoy: gpt-4o, gpt-4o-mini, gemini-2.5-flash en adaptive_model_selector líneas 61/77/84 — purga obligatoria P0"
  - hallazgo_E: "agui_adapter no emite model_resolved hoy; modelo viaja en chunk.meta → THINKING_STATE. Hay que tocar engine.py + agui_adapter.py"
---

# DAN v1 — El Monstruo: Cabina Dual + Agente Manus Real

> **Diseño de Alto Nivel** producido por el Consejo de 6 Sabios (GPT-5.5 Pro, Claude Opus 4.7, Gemini 3.1 Pro Preview, Grok 4, DeepSeek R1, Perplexity Sonar Reasoning Pro) bajo el protocolo **Iterative Compound Learning + Validación en Tiempo Real**, sintetizado por GPT-5.5 Pro como orquestador y verificado contra realidad actual (mayo 2026).

---

## 0. Dictamen ejecutivo (léase en 90 segundos)

> **Nota v1.1 (post-audit Cowork):** Las 5 decisiones del Consejo se sostienen íntegras. El audit de Cowork detectó **5 hallazgos críticos pero todos de implementación, no de diseño**: paths kernel correctos, 2 vectores de downgrade en vez de 1, 3 catálogos a consolidar en vez de uno crear, modelos prohibidos a purgar, evento `model_resolved` que toca `engine.py` también. La versión v1.1 incorpora estos hallazgos en la sección 4 (mapeo de implementación) y la sección 8 (Sprint 1 backend). El cuerpo doctrinal (este dictamen + secciones 2, 3, 5, 6, 7) **no cambia**. Trazabilidad: `bridge/cowork_to_manus_DAN_v1_SPRINT_1_AUDIT_2026_05_27.md`.

La decisión central del Consejo es **endurecer el kernel vivo, no reemplazarlo**. El Monstruo ya tiene streaming AG-UI, Embrión, app Flutter y kernel en producción. Lo que falta es convertir esa cabina en un sistema con **manos reales, memoria operativa, routing honesto, autonomía gobernada y UX nativa iOS**. La tabla siguiente resume las cinco decisiones.

| Pregunta | Decisión final | Antipatrón evitado |
|---|---|---|
| **P1 Tools reales** | **Tool Execution Plane canónico en el kernel** + MCP server interno como fachada + adapters nativos OpenAI/Anthropic/Gemini. LangGraph solo como satélite para workflows largos. | "Adoptar MCP" como religión; reemplazar el kernel por LangGraph. |
| **P2 Selector mobile** | **Profiles + provider override + Auto.** Mobile envía intención, kernel resuelve y emite `model_resolved` con modelo real. **Prohibido fallback silencioso a `gpt-4.1-nano`.** | Hardcodear modelos exactos en Flutter; degradar Manus → nano sin avisar. |
| **P3 Missions persistentes** | **Event sourcing + snapshots** alineado con AG-UI. Replay narrativo por defecto, rerun crea mission hija. | Re-ejecutar tools al hacer replay; perder contexto al cerrar app. |
| **P4 Autonomía Embrión** | L0–L4 **por clase de acción × skill × presupuesto × reversibilidad × sensibilidad × blast radius**. L3/L4 jamás globales. Acciones irreversibles externas siempre con tap. | Subir nivel global al Embrión; dejar que decida pagos/emails sin gate. |
| **P5 UX iPhone** | Mission Center + Embrión Calm Inbox + iOS Native Pack (Live Activities, App Intents, Shortcuts, Privacy Manifest). **P0 absoluto: limpiar bundles duplicados.** | Más dashboards; Dynamic Island como Grafana permanente. |

**Plazo recomendado para los 10 primeros días:** unificar bundle iOS, parchear routing con `model_resolved`, crear tablas `missions`/`mission_events`, implementar ToolRegistry/Executor mínimo, activar `web_search` real, añadir tests anti–tool fantasma, allowlist de `supabase_query`, Mission Center mínimo en Flutter. Con eso, El Monstruo deja de ser *cabina con streaming* y pasa a ser **agente operativo auditable**.

---

## 1. Cómo se produjo este documento

Este DAN no es opinión de un modelo aislado ni mezcla cruda de respuestas. Se produjo con un **pipeline de 7 pasos verificable**:

1. **Dossier técnico** del estado actual del Monstruo y las 5 preguntas estratégicas.
2. **Investigación tiempo real previa** con Perplexity Sonar (8 temas, 56 KB de hallazgos verificados).
3. **Round 1 paralelo** a 6 Sabios — todos respondieron: GPT-5.5 Pro (17 KB), Claude Opus 4.7 (9 KB), Gemini 3.1 Pro (11 KB), Grok 4 (5 KB), DeepSeek R1 (11 KB), Perplexity Sonar Pro (26 KB). Total respuestas combinadas: **96 KB**.
4. **Validación post-consulta** independiente con Perplexity contra docs actuales (39 KB de informe). Identificó **12 correcciones obligatorias** que se incorporaron al diseño.
5. **Síntesis con GPT-5.5 Pro como orquestador**, inyectando respuestas + informe de validación (25 KB).
6. **Validación post-síntesis** con Gemini + Grok como segundas opiniones independientes. Resultado: score global **0.81**, score factual **0.71**, score de incorporación **0.95**, dictamen *"no necesita corrección"*.
7. **Redacción de este DAN** consolidado y entregable.

Todos los archivos intermedios viven en `/home/ubuntu/dan_cabina/salida/` y los anexos están listados al final.

---

## 2. Base epistemológica: hechos, inferencias, supuestos

### 2.1 Hechos verificados por validación post-consulta

| Área | Hecho verificado |
|---|---|
| **MCP gobernanza** | Bajo Linux Foundation/gobernanza neutral. Ecosistema fuerte. Conteo oficial validado de servidores MCP públicos: ~9.652 (no necesariamente "más de 10k"). |
| **MCP auth** | **Corrección crítica:** MCP **sí incluye autorización estandarizada basada en OAuth 2.1**. Lo que sigue siendo responsabilidad del Monstruo: RBAC, scopes de negocio, presupuestos, risk policy y auditoría operativa. |
| **MCP adopción** | OpenAI y Anthropic soportan MCP remoto de forma nativa. Cursor y GitHub Copilot tienen soporte verificado. Gemini/VS Code/etc. no quedaron igualmente verificados — **adapters nativos siguen siendo necesarios**. |
| **OpenAI tools** | OpenAI ofrece web/file/code tools nativas en Responses/Assistants/Agents SDK. Útiles tácticamente, **no deben ser la fuente canónica del Tool Plane** del kernel. |
| **LangGraph** | Maduro, con integraciones MCP/AG-UI. La afirmación "no soporta MCP/AG-UI nativo" es obsoleta. Pero sigue siendo *framework*, no protocolo neutral, y crea acoplamiento si se vuelve core. |
| **Supabase Pro** | 8 GB DB, overage ~$0.125/GB/mes para disco. Backups/snapshots y file storage tienen pricing separado. |
| **iOS ActivityKit** | Live Activities requieren ActivityKit/SwiftUI nativo incluso en apps Flutter. **No existe regla HIG de "solo tareas >15s"** (afirmación incorrecta de algunos sabios). Sí hay límites: 5–15s entre updates, hasta ~8h activa + 4h visible, máximo 5 Live Activities simultáneas por app, push budgets opacos. |
| **Privacy Manifest** | App Store exige `PrivacyInfo.xcprivacy` y Required Reason APIs. Plugins Flutter deben auditarse. |
| **OpenTelemetry GenAI** | Convenciones semánticas y OTLP para spans de model/tool/agent ya estables. Debe complementar `mission_events`. |
| **AI Act / RGPD** | Calendario escalonado 2025–2027+, **no todo entra en agosto 2026**. RGPD vigente: minimización, DPAs, transferencias internacionales, retención justificada. |

### 2.2 Inferencias sólidas del Consejo

La arquitectura correcta es **kernel soberano + Tool Registry/Executor + MCP facade + adapters**. Event sourcing es la única forma razonable de cumplir simultáneamente *replay*, *auditoría*, *aprendizaje del Embrión* y *no-equivocarse-2x*. La UX premium no vendrá de más dashboards, sino de **menos superficies, más intención, estado persistente y notificación calmada**.

### 2.3 Supuestos no verificados (gaps explícitos)

> Disponibilidad y precio exacto de los modelos del registry en producción. Nombre verificable de "Kimi K2.5". Latencias reales de MCP/adapters en Railway. Proveedor óptimo para `web_search` (Perplexity vs Brave vs OpenAI). Stack de `code_exec` (E2B vs Firecracker vs Code Interpreter vs Docker aislado).

Estos gaps se atacan en la fase de implementación con benchmarks A/B antes de comprometer arquitectura.

---

## 3. Las cinco decisiones, en profundidad

### 3.1 P1 — Tools reales del Hilo de Manus

#### Decisión

Construir un **Tool Execution Plane** dentro del kernel como sistema de registro, permisos, ejecución, auditoría y presupuesto. Encima de él se exponen las mismas tools como **MCP server interno** y como **adapters nativos** para los proveedores que no consumen MCP directamente.

```text
Modelo (OpenAI/Anthropic/Gemini/...)
    ↓ tool_call
Model Adapter (normaliza a Canonical Tool Call)
    ↓
Tool Registry (lookup + schema validation)
    ↓
Policy + Budget + Approval Engine (kernel)
    ↓
Tool Executor (sandbox por clase)
    ↓
Tool Result + Cost Ledger + Audit
    ↓
AG-UI events  +  mission_events  +  OTel GenAI spans
```

#### Tools P0 (sprint 1)

| Tool | Decisión |
|---|---|
| `web_search` | Activar real, server-side. Empezar con Perplexity/Sonar (ya en stack); interfaz pluggable para Brave/OpenAI web_search. Cost ledger por query. Citations preservadas. |
| `skill_read` | Lectura segura de genome/skills/patterns. Sin writes. Redacción de PII. |
| `file_io` | Solo workspace de mission. Nada de filesystem global. Artifacts cifrados en object storage. |
| `supabase_query` | Solo read-only y RPCs allowlisted. **Prohibido SQL libre generado por modelo.** Writes separados como `supabase_mutation` con aprobación. |
| `code_exec` | Sprint 1–2: sandbox separado, sin secrets, sin red por defecto, CPU/RAM/timeouts estrictos. Decisión sandbox pendiente (E2B/Firecracker/Code Interpreter). |

#### Campos mínimos del `ToolRegistry`

```text
name, version, json_schema, description_for_model,
risk_class, side_effect_class, requires_approval, max_autonomy_level,
timeout_ms, retry_policy, budget_usd, idempotency_required,
replay_policy, redaction_policy, otel_attributes
```

#### Reglas duras (no negociables)

> Si el agente dice "voy a buscar en web", **debe existir un `tool_call` real o un evento `tool_denied`**. Narrar una tool inexistente es fallo de sistema y debe disparar test rojo.

> Mobile **nunca** invoca tools ni ve secrets. El flujo es Mobile → Gateway → Kernel. El kernel/gateway agregan credenciales.

> MCP usa OAuth 2.1, pero **la autorización de negocio (RBAC, scopes, presupuestos, risk class) vive en el kernel**, no en el transporte.

> `code_exec` jamás comparte entorno con secrets del kernel.

#### Trade-off aceptado

Se pierde velocidad inicial frente a "enchufar OpenAI Agents SDK y listo". Se gana soberanía multi-modelo, auditabilidad, y se evita reescribir tools cada vez que cambia un proveedor.

---

### 3.2 P2 — Selector mobile ↔ agente real

#### Decisión

Implementar **selector híbrido: profiles + provider override + Auto**. El frontend nunca hardcodea SKUs. El kernel posee la verdad y la emite explícitamente.

#### Contrato Mobile → Kernel

```json
{
  "requested_chip": "claude",
  "selector_type": "provider_override",
  "selector_value": "anthropic",
  "routing_mode": "manual_override",
  "mission_goal": "...",
  "budget_cap": 0.50,
  "latency_preference": "normal"
}
```

#### Primera respuesta del kernel (evento AG-UI)

```json
{
  "event_type": "model_resolved",
  "resolved_provider": "anthropic",
  "resolved_model": "claude-opus-4-7",
  "fallback_policy": "same_family_or_ask",
  "routing_reason": "manual provider override + frontier tier required"
}
```

#### Semántica final de los chips

| Chip mobile | Significado canónico en kernel |
|---|---|
| **Auto** | Kernel elige perfil/modelo con reglas transparentes. No "ML mágico". |
| **Manus** | `agentic_deep_tools`: modo agente con planner, tools, missions, budgets, streaming. **No es un modelo**, es un perfil. |
| **Claude / GPT / Gemini / Perplexity** | Preferencia fuerte por familia/proveedor. Fallback solo visible y, si cambia de familia, con confirmación o policy explícita preautorizada. |
| **Long press / Advanced** | Selector de modelo exacto para debug y soberanía granular del operador. |

#### Regla de confianza (ley fundamental)

> **Nunca más "Manus → `gpt-4.1-nano`" silencioso.**
>
> Un fallback barato solo es aceptable si: (a) el chip era `Auto`, o (b) Alfredo lo autorizó como fallback explícitamente, **y** (c) el evento `model_resolved` lo muestra al operador antes del primer token.

#### Trade-off aceptado

La UX deja de mostrar "modelo exacto" en el cliente y se vuelve más abstracta. A cambio, el kernel puede cambiar modelos, costes, latencias y disponibilidad sin publicar nueva versión de la app.

---

### 3.3 P3 — Missions persistentes

#### Decisión

Adoptar **event sourcing + snapshots**, alineado con los eventos AG-UI que el Hilo ya emite hoy. AG-UI ya es event-based; no se inventa otro protocolo.

#### Schema mínimo

| Tabla | Función operativa |
|---|---|
| `missions` | Entidad principal del Hilo: objetivo, status, routing resuelto, coste, riesgo, resumen, parent/child. |
| `mission_events` | Timeline inmutable: mensajes, steps, tool_calls, tool_results, errors, approvals, cost_deltas. Hash chain para integridad. |
| `tool_invocations` | Auditoría específica de tools: args redacted, result redacted o referencia a artifact, latency, cost, status, idempotency_key. |
| `mission_snapshots` | Estado materializado para resume/replay rápido. |
| `mission_artifacts` | Archivos, diffs, logs grandes, resultados raw cifrados en object storage. |
| `mission_feedback` | Tap, rechazo, causa, rating, correction notes. |
| `mission_patterns` | Playbooks aprobados explícitamente para que el Embrión los reutilice. |

#### Modos de replay

| Modo | Comportamiento |
|---|---|
| **Replay narrativo** *(default)* | Rehidrata timeline. **No ejecuta tools.** Es la verdad histórica. |
| **Resume** | Carga snapshot + últimos eventos + artifacts relevantes. Reanuda mission viva. |
| **Rerun** | **Crea nueva mission** con `parent_mission_id`. Ejecución fresca. |
| **Deterministic replay** | Solo si todas las tools son `replay_policy=mocked_result` o explícitamente idempotent. **Nunca default.** |

#### Conexión con Embrión (cómo aprende sin descontrolarse)

Una mission exitosa **no se vuelve patrón automáticamente**. El flujo correcto:

1. Mission completada.
2. Kernel **propone** un patrón: objetivo, precondiciones, tool sequence, presupuesto, riesgos esperados, rollback, failure modes.
3. **Alfredo aprueba** el patrón con tap.
4. El Embrión puede proponer o ejecutar instancias según `action_policy`.
5. Si una instancia falla: se guarda `failure_fingerprint` + `reason_code` + bloqueo de propuestas similares hasta corrección explícita.

Esto materializa la doctrina de **no-equivocarse-2x**.

#### Retención y privacidad

| Capa | TTL | Tratamiento |
|---|---|---|
| **Hot** — timeline completa | 30–90 días según sensibilidad | Cifrada at rest. |
| **Warm** — audit redacted | 12–24 meses | Solo si hay justificación operativa o regulatoria documentada. |
| **Cold** — métricas/hashes/summaries | Indefinido | Anonimizado. Sin prompts crudos. |
| **Pinned** | Indefinido | Alfredo decide explícitamente conservar. |
| **Raw con PII/secrets** | TTL corto | Cifrado, object storage, redacción inmediata en logs. |

DPAs con proveedores LLM y análisis de transferencias internacionales son **parte del diseño**, no burocracia posterior.

#### Trade-off aceptado

Más tablas y más disciplina de privacidad. A cambio, el Monstruo gana replay, auditoría, aprendizaje compuesto y trazabilidad real.

---

### 3.4 P4 — Escalamiento del Embrión

#### Decisión

Mantener L0–L4, pero **no como nivel global** del Embrión. La función correcta es:

```text
autonomy_level = f(action_class, skill_id, budget,
                   reversibility, data_sensitivity,
                   blast_radius, history)
```

#### Niveles refinados (operativos)

| Nivel | Definición | Cuándo aplica |
|---|---|---|
| **L0** | Informa / observa | Sin side effects. |
| **L1** | Propone con plan, presupuesto y diff esperado; requiere tap | **Default para todo lo nuevo.** |
| **L2** | Ejecuta dentro de policy y presupuesto preaprobado; notifica | Solo clases autorizadas con historial. |
| **L3** | Ejecuta si es reversible o sandboxed, **o** prepara draft final | **No aplica a emails enviados, pagos, prod irreversible.** |
| **L4** | Autónomo total dentro de una clase estrecha y circuito cerrado | Nunca universal. Solo clases con métricas duras y rollback probado. |

#### Matriz inicial de action classes (techo permitido)

| Clase de acción | Máximo inicial |
|---|:---:|
| Observación / search / read logs | L2 |
| Resúmenes / reportes / drafts internos | L2 |
| Workspace de mission reversible | L2–L3 |
| Supabase read allowlisted | L2 |
| Abrir PR / branch / tests sandbox | L2 |
| Deploy staging / non-prod | L1–L2 |
| Supabase write / migrations | L1 |
| Deploy prod / infra | L1 |
| Comunicación externa / publicación | L1 (drafts internos pueden ser L2/L3) |
| Finanzas / legal / compras | L0–L1 |
| Secrets / security / access control | L0–L1 |

#### Métricas para promover L1 → L2 (umbrales conservadores)

> ≥ 20 ejecuciones comparables. ≥ 95% éxito. ≥ 95% aprobación sin edición sustancial. **Cero** incidentes severos. Coste p95 dentro del presupuesto. Diff esperado ≈ diff real. Rollback probado si hay side effects. Sin repetición de `failure_fingerprint`. **Promoción explícita aprobada por Alfredo.**

#### Si el Embrión propone fuera de su clase autorizada

El kernel no "confía" en el Embrión por su prompt. Valida policy server-side:

- Excede nivel → **auto-degrada a L1**.
- Clase no existe → L0/L1 con propuesta de nueva policy.
- Clase prohibida → **hard block**.
- Todo queda registrado como `policy_violation` o `authorization_gap` en `mission_events`.

#### Trade-off aceptado

La autonomía escala más lento. Es correcto: sin historial, missions persistentes y failure memory, L3/L4 sería **teatro peligroso**.

---

### 3.5 P5 — UX cabina iPhone Apple/Tesla

#### P0 absoluto — limpiar identidad iOS antes de cualquier feature

Tres apps "El Monstruo" con bundles distintos en el iPhone destruyen confianza y rompen App Intents, Live Activities, deep links y APNs.

| Entorno | Bundle canónico recomendado | Nombre / ícono |
|---|---|---|
| Producción | `com.alfredogongora.elmonstruo` | "El Monstruo" |
| Dev | `com.alfredogongora.elmonstruo.dev` | "Monstruo Dev" (ícono distinto) |
| Staging | `com.alfredogongora.elmonstruo.staging` | "Monstruo Staging" (ícono distinto) |

Eliminar `com.example.elMonstruoApp` del uso operativo. Alinear APNs, App Intents, Live Activities y deep links al bundle canónico.

#### Tres features de máximo impacto

##### 1. Mission Center

La pantalla central del Hilo deja de ser chat efímero y se vuelve **consola operativa persistente**:

- Lista de missions: activas, pausadas, completadas, fallidas.
- Por mission: estado, modelo resuelto, tool actual, coste, duración.
- Acciones: replay narrativo, resume, clone/rerun (mission hija), marcar como pattern.
- Búsqueda por objetivo y tags.

##### 2. Embrión Calm Inbox + push accionable

Patrón anti-molesto, premium-quiet:

- Push **solo** cuando la bandeja pasa de 0 → 1 propuesta útil, o si hay evento crítico.
- Mientras haya pendientes ya conocidas: badge / Live Activity update, nunca spam de notificaciones.
- Digest configurable (mañana / tarde / noche).
- Snooze por clase de acción.
- Approve/reject desde notificación **solo para riesgo bajo**.
- Riesgo alto → abre app con Face ID o confirmación explícita.

> **Doctrina:** El Monstruo no debe parecer necesitado.

##### 3. iOS Native Pack

| Capacidad | Implementación |
|---|---|
| **Live Activity / Dynamic Island** | Para Hilo activo iniciado por Alfredo (mission en curso). No para streaming de tokens. Update cada 5–15s con estado semántico (modelo, tool, paso, coste). |
| **App Intents / Shortcuts** | "Abrir Hilo", "Reanudar mission X", "Revisar Embrión". Permite Siri y Spotlight. |
| **Siri** | Para iniciar/reanudar/consultar. **Nunca para aprobar acciones irreversibles** sin confirmación fuerte. |

#### Restricciones reales de iOS (verificadas)

> No se puede streamear tokens en Dynamic Island; updates cada 5–15s con estado semántico. Hasta 5 Live Activities simultáneas por app. Duración aprox. 8h activa + 4h visible. **Requiere Swift / ActivityKit / Widget Extension** aunque la app sea Flutter. Requiere Privacy Manifest (`PrivacyInfo.xcprivacy`). Soporte obligatorio: VoiceOver, Dynamic Type, Reduce Motion, botones ≥ 44×44 pt.

#### Trade-off aceptado

Necesita trabajo nativo iOS y disciplina de producto. A cambio, la cabina deja de sentirse como Grafana móvil y empieza a comportarse como **sistema operativo personal**.

---

## 4. Insights únicos valiosos del Consejo

| # | Insight | Por qué importa |
|---:|---|---|
| 1 | **Tool ghost test** | Si el agente anuncia una tool y no hay `tool_call` real, el sistema falla y debe haber test P0 que lo capture. |
| 2 | **No persistir chain-of-thought literal** | Auditar pasos semánticos, tool calls, resultados, costes y decisiones — no depender de razonamiento textual crudo como fuente de verdad. |
| 3 | **Long-press para modelo exacto** | Mantiene UI limpia sin quitarle al operador soberano el control granular cuando lo necesita. |
| 4 | **L3 como "draft para irreversibles"** | Para emails, pagos, publicaciones: la autonomía prepara todo, pero la última milla siempre requiere tap humano. |
| 5 | **OpenTelemetry GenAI complementa, no reemplaza, `mission_events`** | Dos planos: timeline de negocio (mission_events) + trazas técnicas (OTel spans). |
| 6 | **Privacy Manifest y DPAs son arquitectura, no burocracia** | iOS y los LLMs externos abren obligaciones concretas que tocan el diseño. |
| 7 | **Supabase Realtime Broadcast** | Útil para Mission Center / Embrión sin polling; Postgres Changes es más simple pero menos escalable a largo plazo. |

---

## 5. Gaps abiertos que requieren investigación dedicada

| Gap | Qué decidir / investigar |
|---|---|
| Proveedor `web_search` | Benchmark real Perplexity/Sonar vs Brave vs OpenAI web_search: coste, latencia, calidad, DPA, citations preservadas. |
| `code_exec` sandbox | Elegir entre OpenAI Code Interpreter, E2B, contenedor aislado, Firecracker u otro. Criterios: secrets, red, coste, artifacts, reproducibilidad. |
| MCP implementation | Validar SDK Python oficial actual, versión de spec, OAuth 2.1 flow, deployment interno en Railway. |
| Model registry real | Confirmar modelos activos en stack: precios, context windows, tool support, rate limits, DPAs. |
| RLS Supabase | Definir cómo el kernel ejecuta RPC allowlisted sin romper RLS ni exponer service role indebidamente. |
| Backend OTLP | Elegir entre Grafana Tempo, Jaeger, OpenTelemetry Collector, proveedor cloud. |
| APNs / ActivityKit | Plugin Flutter vs código Swift propio; push tokens de Live Activities; remote start policy. |
| Retención legal | Clasificar missions por sensibilidad/riesgo y ajustar TTL/anonimización por clase. |
| Taxonomía autonomía | Calibrar action classes con datos reales de uso; los umbrales iniciales son conservadores. |
| Accesibilidad | Auditar app Flutter con VoiceOver, Dynamic Type, Reduce Motion, contraste de paleta forja/graphite/acero. |

---

## 6. Plan priorizado de acción

> **Escala:** Impacto / Probabilidad / Costo = 1–5. **Score** = (Impacto × Probabilidad) ÷ Costo. Mayor score = mayor prioridad relativa.

### 6.1 Sprint 1 — fundamentos (P0)

| # | Acción | Pregunta | I | P | C | Score |
|---:|---|:---:|:---:|:---:|:---:|---:|
| **P0.1** | (v1.1) **Eliminar AMBOS vectores de downgrade**: (1) parchar `config/model_catalog.FALLBACK_CHAINS` para que `clasificador` y `chat_rapido` NO terminen en `gpt-4.1-nano`; (2) revisar lógica de presión de presupuesto en `adaptive_model_selector` que cae a `gpt-4o-mini` / `gemma3:8b`. **Consolidar los 3 catálogos paralelos** (`config/model_catalog.MODELS` + `fallback_engine.PROVIDERS` + `adaptive_model_selector.MODEL_CATALOG`) en `config/model_catalog` como fuente única. **Emitir evento `model_resolved`** desde `kernel/engine.py` + `kernel/agui_adapter.py` en `/v1/agui/run`. **Purgar modelos prohibidos** (`gpt-4o`, `gpt-4o-mini`, `gemini-2.5-flash` en `adaptive_model_selector` líneas 61/77/84). | P2 | 5 | 5 | 1 | **25.0** |
| **P0.2** | Unificar bundle iOS prod/dev/staging y limpiar las 3 apps duplicadas en iPhone | P5 | 4 | 5 | 1 | **20.0** |
| **P0.3** | Crear tablas `missions` + `mission_events`; devolver `mission_id` en `/v1/agui/run` | P3 | 5 | 4 | 2 | **10.0** |
| **P0.4** | Implementar `ToolRegistry` + `ToolExecutor` mínimo con eventos AG-UI reales | P1 | 5 | 4 | 3 | 6.7 |
| **P0.5** | Activar `web_search` real server-side con cost ledger y citations | P1 | 5 | 4 | 2 | **10.0** |
| **P0.6** | Tests anti–tool fantasma: tool anunciada = `tool_call` real o `tool_denied` | P1 | 4 | 5 | 1 | **20.0** |

### 6.2 Sprint 2 — operatividad real

| # | Acción | Pregunta | I | P | C | Score |
|---:|---|:---:|:---:|:---:|:---:|---:|
| P1.1 | `supabase_query` read-only y RPC allowlist con timeout, limit, audit | P1 | 5 | 4 | 3 | 6.7 |
| P1.2 | `tool_invocations` + idempotency + args/result redacted + hash chain | P1/P3 | 5 | 4 | 3 | 6.7 |
| P1.3 | Endpoint `GET /v1/missions/{id}/replay` narrativo + snapshots | P3 | 5 | 4 | 3 | 6.7 |
| P1.4 | Mission Center Flutter: lista, estado, replay, resume | P3/P5 | 5 | 4 | 3 | 6.7 |
| P1.5 | `action_classes` + `action_policies` L0–L2 en kernel | P4 | 5 | 4 | 3 | 6.7 |
| P1.6 | Embrión push calmado: badge, digest, approve/reject bajo riesgo | P5/P4 | 4 | 4 | 3 | 5.3 |
| P1.7 | Instrumentar OpenTelemetry GenAI spans vía OTLP | P1/P3 | 4 | 4 | 2 | 8.0 |

### 6.3 Sprint 3 — ecosistema y nativo iOS

| # | Acción | Pregunta | I | P | C | Score |
|---:|---|:---:|:---:|:---:|:---:|---:|
| P2.1 | MCP server interno generado desde `ToolRegistry` con OAuth/service auth | P1 | 4 | 3 | 4 | 3.0 |
| P2.2 | `file_io` robusto + artifacts cifrados; `skill_read` integrado con patterns | P1/P3 | 4 | 4 | 3 | 5.3 |
| P2.3 | `code_exec` sandbox sin secrets y con artifacts por mission | P1 | 4 | 3 | 4 | 3.0 |
| P2.4 | AutoRouter v1 por reglas + evals; sin clasificador opaco aún | P2 | 3 | 4 | 3 | 4.0 |
| P2.5 | Live Activity / Dynamic Island para Hilo activo + Privacy Manifest | P5 | 4 | 3 | 3 | 4.0 |
| P2.6 | App Intents / Shortcuts: iniciar Hilo, reanudar mission, revisar Embrión | P5 | 3 | 4 | 2 | 6.0 |

### 6.4 Sprint 4+ — patrones, autonomía adaptativa, LangGraph satélite

| # | Acción | Pregunta | I | P | C | Score |
|---:|---|:---:|:---:|:---:|:---:|---:|
| P3.1 | `mission_patterns` aprobados por Alfredo + failure fingerprints | P3/P4 | 5 | 3 | 4 | 3.75 |
| P3.2 | Promoción/democión automática de autonomía por métricas | P4 | 4 | 3 | 4 | 3.0 |
| P3.3 | LangGraph solo para workflows largos seleccionados, consumiendo MCP | P1/P3 | 3 | 3 | 4 | 2.25 |
| P3.4 | L3/L4 en clases estrechas con rollback probado y circuit breakers | P4 | 4 | 2 | 5 | 1.6 |

---

## 7. Lo que queda explícitamente fuera del plan

| Anti-decisión | Razón |
|---|---|
| No convertir LangGraph en el nuevo kernel | Crea acoplamiento a LangChain y duplica estado de `missions`. |
| No exponer SQL libre a modelos | Riesgo de prompt injection con consecuencias destructivas. |
| No persistir prompts/raw payloads para siempre | RGPD: minimización y retención justificada. |
| No usar Dynamic Island como Grafana permanente | Apple prohíbe; agota push budgets; es UX cargante. |
| No aprobar acciones irreversibles desde voz/lock screen sin confirmación fuerte | Riesgo operativo y reputacional. |
| No llamar "Manus" a un modelo si no existe proveedor real integrado | Es un perfil de agente, no un SKU. |
| No permitir fallback silencioso de modelo | Destruye confianza y soberanía. |
| No asumir que event sourcing por sí solo cumple RGPD/AI Act | Cumplimiento requiere minimización + DPAs + redacción + TTLs. |
| No construir MCP "porque sí" antes de tener tools reales ejecutando | MCP sin Tool Plane es fachada vacía. |

---

## 8. Secuencia recomendada de los próximos 10 días

| Día | Trabajo |
|:---:|---|
| **1** | Fijar bundle canónico iOS y limpiar las 3 apps duplicadas en el iPhone. Comunicar bundle prod a equipo. |
| **1–2** | (v1.1) Parchear routing kernel en archivos REALES: consolidar `config/model_catalog` como único catálogo (eliminar duplicados en `fallback_engine.PROVIDERS` y `adaptive_model_selector.MODEL_CATALOG`); parchar `FALLBACK_CHAINS` para bloquear ruta a `gpt-4.1-nano`; emitir `model_resolved` desde `kernel/engine.py` + `kernel/agui_adapter.py`; purgar modelos prohibidos del `adaptive_model_selector`. **Bloqueo absoluto** de fallback nano + modelos `gpt-4o*` + `gemini-2.5-flash`. |
| **2–4** | Crear tablas `missions` y `mission_events`; persistir AG-UI actual; devolver `mission_id`. |
| **3–6** | Implementar `ToolRegistry` y `ToolExecutor`; activar `web_search` real con cost ledger. |
| **5–7** | Añadir tests anti–tool fantasma + cost ledger básico + redacción de logs. |
| **6–9** | `supabase_query` read-only y RPC allowlist con timeout y audit. |
| **8–10** | Mission Center mínimo en Flutter: lista de missions + replay narrativo + estado modelo resuelto. |

Al final de los 10 días, El Monstruo deja de ser **cabina con streaming** y pasa a ser **agente operativo auditable**: sabe qué modelo usó, qué tool ejecutó, cuánto costó, qué ocurrió, cómo repetirlo como pattern, y cuándo no debe volver a cometer el mismo error.

---

## 9. Métricas de éxito del DAN

| Métrica | Objetivo a 30 días | Cómo se mide |
|---|---|---|
| Cero fallbacks silenciosos | 0 missions con modelo resuelto != requested_chip sin aviso | `mission_events.model_resolved` audit |
| Tool ghost rate | 0% en suite de tests | Test suite anti-fantasma en CI |
| Missions persistidas | 100% de hilos lanzados quedan en `missions` | Conteo `agui/run` vs `missions` |
| Replay narrativo funcional | 100% missions completadas reproducibles narrativamente | Smoke test diario |
| Approve/reject Embrión latencia | p95 < 3s desde tap → kernel aplicado | `mission_events.approval_latency` |
| Bundle iOS unificado | 1 sola app "El Monstruo" en producción | Inspección física + APNs token |

---

## 10. Anexos

Los archivos de evidencia del Consejo se conservan en `/home/ubuntu/dan_cabina/salida/`:

| Archivo | Contenido |
|---|---|
| `prompt.md` | Dossier técnico original (las 5 preguntas + estado del Monstruo) |
| `salida/dossier_realidad.md` | Investigación tiempo real previa con Perplexity (8 temas, 56 KB) |
| `salida/sabios/resp_*.md` | Respuestas individuales de los 6 Sabios (round 1) |
| `salida/sabios/respuestas_combinadas.md` | Las 6 respuestas concatenadas (96 KB) |
| `salida/informe_validacion.md` | Validación post-consulta con Perplexity (39 KB, 12 correcciones) |
| `salida/sintesis_final.md` | Síntesis del orquestador GPT-5.5 Pro (25 KB) |
| `salida/validacion_sintesis.md` | Validación post-síntesis con Gemini + Grok (score 0.81) |
| `salida/paso7_metadata.json` | Metadata del Paso 7 (scores y banderas) |

---

## 11. Cierre

> **Este DAN no se vota; se ejecuta.** Las decisiones están tomadas y validadas por seis Sabios independientes, una capa de investigación tiempo real, y dos rondas de verificación post-síntesis. Cuando haya datos reales que contradigan algo de aquí, se actualiza el DAN y se versiona como `v1.1`. Mientras tanto, los 6 ítems P0 del Sprint 1 son la única fuente de verdad para los próximos 7–10 días.

**Versión:** 1.0.0
**Fecha:** 2026-05-27
**Próxima revisión:** al cierre de Sprint 1 o ante hallazgo material que invalide cualquier decisión P0–P5.

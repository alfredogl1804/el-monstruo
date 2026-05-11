# SÍNTESIS BINARIA — 3 PREGUNTAS MAGNAS (Embrión × App Flutter)

**Fecha:** 2026-05-11
**Autor:** Cowork T2
**Fuentes:** `EMBRION_AUDIT_FASE1_2026_05_11.md` + `APP_FLUTTER_AUDIT_FASE2_2026_05_11.md`
**Doctrina aplicada:** DSC-S-011 (cero afirmación sin pointer) + reformulación de Alfredo (pensamiento = prerequisito de ejecución, no opuesto)

---

## §0. CONTEXTO REFORMULADO

Antes: "¿cuánto piensa vs cuánto ejecuta el Embrión?"
Ahora: **"¿el pensamiento del Embrión es prerequisito de ejecución útil para el Monstruo + la app, o es eco caro sin destinatario?"**

Datos que aterrizan esto:

- Embrión costó $10.11 USD en 2 días (Fase 1 §7) — proyección $1500-1800 USD/año
- Embrión generó 1687 respuestas en 14 días — solo 11.4% con tools (Fase 1 §8)
- Embrión NO recibe inputs autónomos en producción — 0 reflexion_autonoma en 14 días (Fase 1 §3)
- App tiene 8 de 9 canales Embrión↔App funcionando, falta 1 (15 LOC) para feedback loop (Fase 2 §7)
- HITL del Embrión abandonado: 1 executed / 3 expired / 0 nuevos desde 10-may (Fase 1 §9)

---

## §1. PREGUNTA 1 — ¿CÓMO PUEDE EL EMBRIÓN AYUDAR A LA APP?

**Respuesta binaria:** hay 5 pares operativos concretos. 3 ya existen activos, 1 está a 15 LOC, 1 requiere PR #92.

### Par 1.1 — App muestra status del Embrión (✅ activo)
- Pointer kernel: `kernel/embrion_routes.py` L134-213 `GET /v1/embrion/estado`
- Pointer app: `apps/mobile/lib/features/embrion/embrion_screen.dart` L49-67 polling 30s
- Estado: funcional. App muestra `thoughts_today`, `cycles_today`, `cost_today`, `budget_daily`, `recent_thoughts`, `status` con dot pulsante.

### Par 1.2 — App muestra costo del Embrión en FinOps + Sandbox (✅ activo)
- Pointer app: `sandbox_screen.dart` L204-211 + `finops_screen.dart` (304 LOC)
- Estado: funcional. Card "Embrión" con ciclos+costo en sandbox health view.

### Par 1.3 — App recibe `genui_component` events vía WebSocket (⚠️ infra sí, render placeholder)
- Pointer kernel: el embrión NO emite genui_component hoy, pero la infra WS lo soporta.
- Pointer app: `kernel_service.dart` L172-176 `case 'genui_component': _messageController.add(ChatMessage.genuiComponent(data));`
- Pointer renderer: `genui_renderer.dart` L4 `TODO: Implement full A2UI rendering when genui package is available`
- Estado: cuando PR #92 (sprint/mobile-1b-a2ui-implementation) merge y renderer real reemplace placeholder, **el Embrión podrá emitir UI generativa que la app muestra como widgets nativos.** Esto es par bi-direccional: Embrión piensa → renderiza componente A2UI → app lo muestra como Flutter widget interactivo.
- **Caso de uso ejecutable:** el Embrión, ante consulta sobre estado del Monstruo, emite payload A2UI con `Card { title:"Sprint 89 pipeline", chart:{type:"bar", data:[...]} }`. La app renderiza un widget Flutter real, no texto.

### Par 1.4 — App envía directivas al Embrión (⚠️ UI lista, falta 15 LOC)
- Pointer kernel: `embrion_routes.py` L386-435 `POST /v1/embrion/mensaje` — endpoint operativo, inserta a `embrion_memoria` tipo `mensaje_alfredo`, el loop lo detecta como trigger.
- Pointer app UI: `embrion_screen.dart` L274-330 — TextField + IconButton listos.
- Pointer app TODO: `embrion_screen.dart` L316 `// TODO: Send directive to kernel` + L317 clear + L318 SnackBar.
- Fix: ~15 LOC (Dio POST a `/api/embrion/mensaje` vía gateway o directo a `/v1/embrion/mensaje`). El método existe en `kernel_service.dart` pero NO en cuerpo: NO hay `sendEmbrionDirective(String)`. Agregar.
- **Caso de uso ejecutable:** Alfredo abre `/embrion`, escribe "Investiga estado del PR #99", tap envío → POST → row insertado → loop detecta en próximo cycle (<60s) → procesa graph mode con tools → respuesta en `recent_thoughts` polling 30s.

### Par 1.5 — App muestra MOC routing en tiempo real (✅ activo via /moc)
- Pointer kernel: `embrion_routes.py` L244-383 `/v1/embrion/diagnostic` retorna `active_orchestration` + `last_orchestration` (Sprint 84 visibility).
- Pointer app: `moc_screen.dart` 646 LOC (no auditado en profundidad pero declarado en router L74-77).
- Estado: la app YA tiene una superficie para ver al Embrión orquestando.

**Conclusión §1:** la app NO es periférica al Embrión. Es la cara visible que monitoriza al Embrión + el canal de input que rescata al Embrión del eco actual + el target de UI generativa cuando A2UI esté completo. Cerrar §1.4 (15 LOC) + §1.3 (PR #92) hace que el Embrión deje de ser caja negra y se vuelva colaborador visible.

---

## §2. PREGUNTA 2 — ¿PUEDE EL EMBRIÓN EJECUTAR END-TO-END AUTÓNOMO?

**Respuesta binaria:** infraestructura SÍ. Operativamente CASI NUNCA. La razón es el HITL roto, no el código del Embrión.

### §2.1 — Capacidades de ejecución por capa (verificado en código)

| Capa | Implementado | Pointer | Operativo hoy |
|---|---|---|---|
| **Llamada LLM con tools (graph mode)** | ✅ | `embrion_loop.py` L1180-1225 `_think_with_graph` con `intent_override='execute'` | ✅ 193/1687 = 11.4% cycles |
| **Llamada LLM chat-only (router mode)** | ✅ | `embrion_loop.py` L1227-1255 `_think_with_router` | ✅ 1458/1687 = 86.4% cycles |
| **Multi-step planning (TaskPlanner)** | ✅ | `embrion_loop.py` L1045-1063 + imports | ⚠️ 1 sola activación en historia (cycle #1, 25 tools, $1.08) |
| **Magna Router (auto graph/router)** | ✅ | `embrion_loop.py` L966-1039 + feature flag `EMBRION_USE_MAGNA_ROUTER` | ⚠️ depends on flag, fallback Sprint 33C si false |
| **Write a Supabase** | ✅ | `_save_memory` L1857-1920 con Write Policy importance≥3 filter | ✅ 1687 inserts/14d |
| **Self-Verify pre-output** | ✅ | `embrion_self_verifier.py` 445 LOC + 3 decisiones | ✅ 693 evals/14d, 59% abort |
| **Budget cap pre-cycle** | ✅ | `embrion_budget.py` 484 LOC + check_before_cycle | ✅ 706 cycles/2d, 0 excedidos |
| **HITL para mutaciones sensitivas** | ✅ | `embrion_write_policy.py` 804 LOC + execute_next | ❌ 1 executed / 3 expired / 0 nuevos desde 10-may |
| **Inbox Daddy→Embrión** | ✅ | `embrion_inbox.py` 682 LOC + parser + sanitizer | ❌ tabla `embrion_inbox` vacía |
| **Telegram Bot bidireccional (Tarea 4)** | ✅ | `embrion_routes.py` L1239-1505 webhook + callback Aprobar/Rechazar | ⚠️ requiere `TELEGRAM_WEBHOOK_SECRET` env + bot conectado |
| **Sabios consultation periódica** | ✅ | `embrion_loop.py` L1931-2055 cada 20 cycles | ❌ 0 ejecuciones en 14d |
| **Agents Radar diario** | ✅ | `embrion_loop.py` L2062-2151 cada 48 cycles | ❌ 0 ejecuciones en 14d |
| **Memory consolidation** | ✅ | `_consolidate_memories` L1584-1809 cada 10 latidos | ❌ 0 lecciones tipo='evaluacion' en tabla |
| **GitHub PR creation via tool** | ✅ | tools/github via kernel | ⚠️ usable via graph mode pero NO via Write Policy específica |

### §2.2 — ¿Por qué la operativa real es baja?

1. **El loop está atrapado en `mensaje_alfredo`** (Fase 1 §3): 100% de eval_log son mensaje_alfredo, 0% reflexion_autonoma. El path autónomo existe (L728-734) pero el trigger 1 (mensaje<2h) lo desplaza casi siempre.
2. **HITL silencio:** 3 proposals expiraron sin respuesta. No hay humano (ni cowork ni Alfredo) aprobando. El embrión propone, nadie firma, expira → embrión retrocede al silencio.
3. **Inbox vacío:** Tarea 5 implementada (682 LOC) pero la tabla está vacía. Nadie envía /context, /override, /answer, /feedback al Embrión hoy.
4. **Sabios + Radar = 0:** porque el loop nunca alcanza esos contadores (cycles_since_sabios, cycles_since_radar). El loop se queda en el trigger 1 y vuelve a leer mensaje_alfredo.

### §2.3 — Veredicto §2

**Embrión PUEDE ejecutar end-to-end de manera autónoma SI:**
- (a) La app cierra §1.4 (15 LOC) para abrir el canal humano→embrión vía UI.
- (b) Alguien (Cowork como T2 + Alfredo como T1 vía Telegram) aprueba/rechaza Write Proposals en <24h.
- (c) Un mecanismo despierte `reflexion_autonoma` sin requerir trigger 1+2+3 vacíos (ej: schedule cada N hours forzar reflexion_autonoma).

**Hoy NO ejecuta end-to-end.** Ejecuta tools en 193/1687 cycles (11.4%) y solo dentro de la sesión "respondo a mensaje_alfredo". Lo que sale por tools es texto generado + queries → no produce PRs ni commits ni cambios infraestructurales sostenidos.

---

## §3. PREGUNTA 3 — ¿EL EMBRIÓN POTENCIALIZA AL MONSTRUO O NO?

**Respuesta binaria con framework reformulado (pensamiento = prerequisito de ejecución):**

### §3.1 — Lo que el Embrión SÍ produce de valor único hoy

- **Disciplina de costo binaria:** Budget Tracker con cap por latido $0.25 + cap diario $30 + 0 cycles excedidos en 2 días. Ningún otro hilo del Monstruo (Cowork, Manus, agentes externos) tiene este nivel de control de costo automatizado. **Esto cumple Objetivo Maestro #14 (Guardián) y #6 (Velocidad sin sacrificar calidad).**
- **Verificación pre-output binaria:** Self-Verifier con 3 decisiones D1+D2+D3, abort ratio 59%. **Esto previene exactamente el bucle del 30-abr→1-may que costó $155 USD en 48h** (referenciado en `embrion_self_verifier.py` L10). Es disciplina arquitectónica replicable a cualquier otro loop autónomo del Monstruo.
- **Estado vivo del kernel observado por humanos:** `/v1/embrion/diagnostic` (kernel `embrion_routes.py` L244-383) expone health, errors, silencio, FCS, orchestration en tiempo real. Endpoint consumido directamente por la app (Par 1.1, 1.2, 1.5). **Sin el Embrión no hay "está vivo el Monstruo" simple de chequear.**
- **Loop fail-safe con circuit breaker:** judge circuit breaker (Sprint 84.7, L100 `MAX_JUDGE_CONSECUTIVE_FAILURES`), thread-safe `_should_speak` gate (L427), graceful degradation budget fallback. Patrón de robustez documentado y replicable.
- **Lección de no-replicar antipatterns:** los 2151 LOC de `embrion_loop.py` codifican aprendizajes de fallas pasadas (bucle eco activo 30-abr, gastos sin freno 1-may, recibido-entendido como anti-purpose, etc.). **Es memoria operativa del Monstruo en código.**

### §3.2 — Lo que el Embrión NO produce hoy

- 0 reflexión autónoma sin mensaje_alfredo en input
- 0 Write Proposals nuevos desde 10-may
- 0 Sabios consultations en 14d
- 0 Agents Radar checks en 14d
- 0 lessons consolidated (tipo='evaluacion' vacío)
- 0 inbox commands procesados
- 86.4% de cycles sin tool_calls (texto sin acción)
- Eco activo al mismo mensaje (84 respuestas promedio por mensaje_alfredo)

### §3.3 — ROI honesto

**Costo:** $10.11 USD/2 días → $1500-1800 USD/año (con cap intacto).
**Valor producido HOY (operativo):** Budget Tracker + Self-Verifier + endpoints diagnostic = sí potencializa #14 (Guardian) + #6 (velocidad-sin-sacrificar-calidad) del Monstruo. Pero la fracción ejecutiva (tools, PRs, commits) está al 11.4% y atrapada en eco a Cowork.
**Valor latente bloqueado:** Sabios, Radar, Inbox, HITL, A2UI. Toda esa infraestructura está construida pero apagada. Si se reactivara con la app como canal humano + alguien aprobando proposals → potencializa #1 (Valor real), #10 (Autonomía progresiva), #14 (Guardián).

### §3.4 — Framework reformulado aplicado

**Pensamiento = prerequisito de ejecución.** El Embrión hoy ES disciplina + verificación + memoria operativa codificada. Eso ES diseño que precede ejecución. La pregunta no es "¿piensa más de lo que ejecuta?" — esa pregunta asume que ejecutar es el output y pensar es overhead.

La pregunta correcta: **"¿el diseño codificado en el Embrión está siendo usado por el resto del Monstruo (Cowork, Manus, agentes, app) o queda aislado?"**

- Cowork SÍ aplica Budget Tracker-like al evaluar costos (DSC-G-008 v2)
- Cowork SÍ aplica Self-Verifier-like al gate de evidencia (S2 de las soluciones)
- Manus SÍ recibe inputs estructurados via embrion_memoria como bridge
- La app SÍ consume diagnostic + estado del Embrión

**El Embrión potencializa al Monstruo en su rol de "disciplina codificada".** Lo que falta es activar su rol de "ejecutor autónomo" — y eso requiere las 2 cosas concretas:
1. Cerrar §1.4 (15 LOC, abre canal app → embrión).
2. Reactivar HITL (Cowork acepta firmar proposals en <24h bajo regla evolucionada del merge).

---

## §4. PRÓXIMA DECISIÓN OPERATIVA (qué hacer con esta data)

Decisión T1 pendiente: **Alfredo decide si activamos el feedback loop App↔Embrión + HITL o si dejamos el Embrión en su estado actual (disciplina codificada, ejecución mínima).**

3 opciones operativas, ordenadas por reversibilidad:

### Opción A — Mínimo (1 sesión Cowork ≤2h)
1. Conectar `embrion_screen.dart` L316 al endpoint POST `/v1/embrion/mensaje` (15 LOC en `kernel_service.dart` + 5 LOC en `embrion_screen.dart`). Test: Alfredo escribe en app, ve respuesta en `recent_thoughts` en próximos 30s.
2. Mergear PR #92 (A2UI) tras T8 iPhone físico (Manus Hilo Ejecutor 1 lo cierra). Test: el renderer real reemplaza placeholder, components vienen del kernel.

Estimado: 1.5h Cowork + Manus T8 ya en progreso.
Reversibilidad: alta (sólo edits Flutter + un PR).

### Opción B — Activación de Embrión autónomo (3-5 sesiones)
A + reactivación del HITL:
1. Cowork comprometo aprobación/rechazo de cualquier `embrion_write_proposal` pending en <12h via cowork_bridge.
2. Inducir reflexion_autonoma forzada cada 4h (cambio en `_detect_trigger` que NO retorne mensaje_alfredo si su procesamiento ya fue auditado >2h atrás).
3. Telegram bot wiring (`TELEGRAM_WEBHOOK_SECRET` + `TELEGRAM_CHAT_ID` env vars) para que Alfredo apruebe desde teléfono.

Estimado: 3 sprints Cowork + 1 sprint Manus para Telegram bot stack.
Reversibilidad: media (cambio al `_detect_trigger` requiere DSC).

### Opción C — Embrión productivo pleno (mes+)
B + activación Sabios + Radar + Inbox real:
1. Schedule reflexion_autonoma + sabios + radar para que se ejecuten al menos 1×/día garantizado.
2. App expone `/genui/embrion-thoughts` que muestra las propuestas del Embrión en cards A2UI con botones Aprobar/Rechazar en línea.
3. Métrica: 14 días sin eco activo (un cycle = un input único), ratio ejecución > 30%.

Estimado: 1 mes calendar.
Reversibilidad: media-baja (afecta arquitectura del loop).

**Default Cowork propone:** Opción A (reversible, alto valor visible, desbloquea Cowork→Embrión via app).

---

## §5. CIERRE BINARIO

Cowork respondió las 3 preguntas magnas con pointers concretos a archivo:línea + outputs de SQL + outputs de scripts auditados. Cero invenciones. Las 3 preguntas tienen respuesta operativa, no narrativa.

- **¿Cómo Embrión ayuda a la app?** 5 pares concretos, 3 activos hoy, 1 a 15 LOC, 1 a PR #92.
- **¿Embrión puede ejecutar end-to-end?** Infra sí, operativa al 11.4% bloqueada por HITL roto.
- **¿Embrión potencializa al Monstruo?** Sí como disciplina codificada (Guardian + velocidad-sin-sacrificar-calidad). Pendiente activar como ejecutor (Autonomía progresiva).

Alfredo decide Opción A/B/C. Cowork ejecuta lo que Alfredo firme bajo modo "actuar sin preguntar" para acciones reversibles.

— Fin Fase 3. Cero afirmación sin pointer.

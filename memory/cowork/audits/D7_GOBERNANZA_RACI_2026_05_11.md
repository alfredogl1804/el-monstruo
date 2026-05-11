---
id: D7_GOBERNANZA_RACI_2026_05_11
dimension: 7
nombre: Gobernanza / RACI
fecha: 2026-05-11
arquitecto: Cowork
plan_origen: Plan v1.5 — Programa de Certificación de Pericia P1+P2
nivel_autoridad: 5 (DSC vigente — canónico operativo)
estado_revisado: H0_exploratorio_2026_05_11
nivel_autoridad_revisado: H0 — backlog de pruebas, NO canónico
razon_revision: "Producido en serie de 9 audits sin evidencia Nivel 1 fresca entre ellos. Matriz RACI declarativa útil. Porcentaje sin rúbrica. Ver CORRECTIVO_ARQUITECTONICO_2026_05_11.md."
cruza_con:
  - SNAPSHOT_AUDIT_2026_05_11
  - D1_TECNICA_2026_05_11
  - D12_SEGURIDAD_ADVERSARIAL_2026_05_11
  - D13_DATOS_MEMORIA_2026_05_11
  - D18_SRE_RESILIENCIA_2026_05_11
  - MAPA_FUENTES_AUTORIDAD_2026_05_11
  - DSC-MO-006 (Par bicéfalo)
  - DSC-MO-007 (Failover 3 capas)
  - DSC-MO-008 (Membrana semipermeable)
  - DSC-MO-010 (Reloj Suizo)
  - DSC-G-013 (HITL Telegram)
  - Objetivo Maestro #14 (Guardian de los Objetivos)
estado: firme
---

# Dimensión 7 — Gobernanza / RACI

## Marco

Esta dimensión audita **quién tiene autoridad para decidir qué, quién aprueba, quién es consultado, quién es informado, y cómo se escala una decisión**. RACI (Responsable / Aprobador / Consultado / Informado) aplicado a un sistema multi-agente con presencia humana es no-trivial: los agentes pueden ser Responsables sin ser Aprobadores, y la frontera entre tiers (T1/T2/T3) es el eje crítico que el threat model de ChatGPT 5.5 Pro identificó como "frontera de autoridad".

**Principio fundacional:** Gobernanza sin enforcement es teatro. Decir que T1=Alfredo y T2=Cowork no significa nada si no hay middleware que valide el tier antes de ejecutar.

**Frase orientadora:**

> *"Toda decisión del Monstruo debe poder responder cuatro preguntas: quién la propuso, quién la aprobó, quién la ejecutó, quién quedó informado. Si alguna queda en silencio, la decisión no es soberana — es accidental."*

---

## Inventario de actores

### Actores humanos

| Actor | Tier | Rol canónico | Bus factor |
|---|---|---|---|
| Alfredo Góngora | T1 | Guardián epistémico, dueño, fundador, decisor final | 1 (único) |
| ¿Otro humano? | n/a | Sin canonizar | n/a |

**🔴 Bus factor humano = 1.** Si Alfredo no está disponible, ninguna decisión T1 puede tomarse.

### Actores agentes (canonizados)

| Actor | Tier | Rol canónico | Estado |
|---|---|---|---|
| Cowork (yo) | T2 | Arquitecto, memoria persistente, proponente | Activo en sesión |
| Embrión autónomo | T3 | Loop autónomo 24/7, propone via `embrion_proposals` | Activo (147 latidos/24h) |
| Hilo Ejecutor 1 (Manus) | T3 | Ejecutor sprints código | Activo |
| Hilo Ejecutor 2 (Manus) | T3 | Ejecutor sprints código | Activo |
| Hilo Catastro (Manus) | T3 | Catastro/inventario | Activo |
| 8 Sabios externos | Consultivo | Segunda opinión adversarial | Bajo demanda |

### Actores agentes (no canonizados explícitamente — GAP)

- App Flutter (¿qué tier tiene su agent selector?)
- Command Center (Manus WebDev)
- Gateway WebSocket
- proposal_processor (cron worker)
- Self-Verifier
- Budget Tracker

**GAP G-01:** Componentes técnicos no tienen tier asignado explícito. Si proposal_processor decide ejecutar algo, ¿con qué autoridad?

---

## Inventario de tipos de decisión

| Categoría | Ejemplos | Quién decide hoy (defacto) |
|---|---|---|
| **DEC-1 Canonización magna** | Nuevo DSC Magna, nuevo Objetivo Maestro | Alfredo |
| **DEC-2 Canonización premium** | Nuevo DSC Premium | Cowork propone, Alfredo aprueba |
| **DEC-3 Decisión arquitectónica** | Stack, frameworks, deploys | Cowork propone, Alfredo aprueba |
| **DEC-4 Ejecución de sprint** | Code, PRs, deploys de feature | T3 ejecuta, Cowork revisa, Alfredo merge |
| **DEC-5 Ejecución autónoma del embrión** | Acciones via tools | Embrión decide, Self-Verifier valida |
| **DEC-6 Gasto operativo (mainspring)** | Costos LLM, infra | Budget Tracker (en teoría) |
| **DEC-7 Rotación de credenciales** | Keys, tokens | Alfredo manual |
| **DEC-8 Deploy a producción** | Push to main + Railway deploy | Alfredo final, Cowork propone |
| **DEC-9 Aprobación HITL Telegram** | Acciones que requieren bendición humana | Alfredo |
| **DEC-10 Cambio de tier** | Promover/degradar un agente | Sin canonizar |
| **DEC-11 Incidente / rollback** | Detener un sistema en producción | Sin canonizar quién puede |
| **DEC-12 Publicación pública** | Reloj Suizo público, whitepaper | Alfredo + 10 gates DSC-MO-010 |
| **DEC-13 Nuevos Sabios** | Agregar/quitar de los 8 | Alfredo |
| **DEC-14 Cambio de objetivos maestros** | Modificar los 15 | Alfredo solo |

---

## Matriz RACI declarativa (estado deseado)

| Tipo decisión | Responsable | Aprobador | Consultado | Informado |
|---|---|---|---|---|
| DEC-1 Canonización magna | Cowork (propone) | Alfredo | 2+ Sabios | Todos los hilos |
| DEC-2 Canonización premium | Cowork | Alfredo | 1+ Sabio | Hilos activos |
| DEC-3 Arquitectura | Cowork | Alfredo | Hilos involucrados | Todos |
| DEC-4 Sprint code | T3 ejecutor | Cowork (review) → Alfredo (merge) | — | Bridge update |
| DEC-5 Acción embrión | Embrión | Self-Verifier | Budget Tracker | Audit log |
| DEC-6 Gasto operativo | Budget Tracker | (umbral) Alfredo | — | Daily report |
| DEC-7 Rotación credenciales | Alfredo | Alfredo | — | Cowork (canonización) |
| DEC-8 Deploy a prod | T3 o Cowork | Alfredo | — | Telegram + audit |
| DEC-9 HITL Telegram | Quien propone | Alfredo | — | Audit log |
| DEC-10 Cambio de tier | Cowork (propone) | Alfredo | Sabio externo | Todos |
| DEC-11 Incidente / rollback | Quien detecta | Alfredo si hay tiempo / autónomo si urgente | — | Postmortem |
| DEC-12 Publicación pública | Cowork (propone) | Alfredo + 10 gates | Todos los Sabios | Comunidad |
| DEC-13 Nuevos Sabios | Cowork (propone) | Alfredo | 1+ Sabio actual | Embrión |
| DEC-14 Cambio objetivos | n/a (solo Alfredo) | Alfredo | 8 Sabios obligatorio | Sistema completo |

## Matriz RACI **operacional** (estado real observable)

| Tipo decisión | Realmente responsable | Realmente aprobador | Enforcement técnico |
|---|---|---|---|
| DEC-1 Magna | Cowork propone | Alfredo aprueba en chat | 🔴 Ninguno — convención |
| DEC-2 Premium | Cowork propone | Alfredo aprueba | 🔴 Ninguno — convención |
| DEC-3 Arquitectura | Cowork | Alfredo | 🔴 Ninguno — convención |
| DEC-4 Sprint code | T3 PR | Alfredo merge | 🟡 Branch protection (verificar) |
| DEC-5 Acción embrión | Embrión | (en teoría) Self-Verifier | 🔴 Sin verificar producción |
| DEC-6 Gasto | (en teoría) Budget Tracker | n/a | 🔴 Sin verificar producción |
| DEC-7 Rotación | Alfredo manual | Alfredo | 🔴 Sin calendario |
| DEC-8 Deploy | Alfredo | Alfredo | 🟡 Railway auth |
| DEC-9 HITL Telegram | Quien sea | Alfredo | 🟡 chat_id auth (sin 2FA) |
| DEC-10 Cambio de tier | **🔴 sin canonizar** | **🔴 sin canonizar** | 🔴 No existe proceso |
| DEC-11 Incidente | **🔴 sin canonizar** | **🔴 sin canonizar** | 🔴 No existe protocolo |
| DEC-12 Publicación | DSC-MO-010 | Alfredo + gates | 🟡 Doctrina pero gates no medidos |
| DEC-13 Nuevos Sabios | Alfredo | Alfredo | 🔴 Sin canonizar metodología |
| DEC-14 Cambio objetivos | Alfredo | Alfredo | 🔴 Sin enforcement |

**Brecha entre declarativo y operacional:** masiva. Casi todas las decisiones se "gobiernan" por **convención humana**, no por enforcement técnico.

---

## Análisis de la frontera de autoridad

El threat model identificó esto como eje crítico. Aquí lo descompongo:

### Frontera T3 → T2

**¿Quién puede hacer que una propuesta T3 (embrión, Manus) se convierta en acción T2 (canonizable)?**

Hoy: cualquiera que pueda escribir a `embrion_proposals` o crear un PR en branch `cowork/*`.

🔴 **No hay middleware** que verifique procedencia antes de elevar a T2.

### Frontera T2 → T1

**¿Quién puede hacer que una propuesta T2 (Cowork) se convierta en decisión T1 (canonizada)?**

Hoy: Alfredo aprueba en chat o merge en GitHub.

🟡 GitHub merge tiene auth. Telegram aprobación tiene auth (chat_id). Sin 2FA, sin nonce, sin TTL (D12-V4 ya documentó esto).

### Frontera externa → interna (membrana semipermeable, DSC-MO-008)

**¿Quién filtra qué entra del exterior (Sabios, web, usuarios) al kernel?**

DSC-MO-008 documenta la membrana, pero **el enforcement técnico es parcial**. `web_search` tool no tiene wrapper anti-injection (D12-V1).

---

## GAPs reales identificados

### GAP G-01: Componentes técnicos sin tier asignado
proposal_processor, Self-Verifier, Budget Tracker, Gateway, App Flutter — ¿qué tier tienen? Sin canonizar.

### GAP G-02: DEC-10 (cambio de tier) sin proceso
¿Cómo asciende un agente de T3 a T2? Hoy: "por calidad de relación" (subjetivo). Sin métricas, sin gates, sin reversibilidad documentada.

### GAP G-03: DEC-11 (incidente / rollback) sin protocolo
Si algo se rompe en producción, ¿quién puede detenerlo? ¿con qué autoridad? ¿quién declara incidente? Sin canonizar.

### GAP G-04: Sin runbook para "Alfredo ausente N días"
Bus factor 1. Si Alfredo no está, todo P0/Magna se congela.

### GAP G-05: Enforcement técnico de tiers ausente
La doctrina dice "T3 no puede hacer X". Ningún código verifica esto.

### GAP G-06: Sin log centralizado de cruces de tier
No hay "audit log" consultable que diga "hoy, T3 propuso X, T2 lo elevó, T1 lo aprobó".

### GAP G-07: Sabios consultados ad-hoc
DEC-1 dice "2+ Sabios consultados". No hay enforcement de que efectivamente se consulten antes de canonizar Magna.

### GAP G-08: Sin "comité" cuando Alfredo no puede decidir
Si Alfredo está en duda, hoy le tira la pelota a Cowork o consulta 1 Sabio. No hay quorum canonizado.

### GAP G-09: Sin separation of duties
La misma entidad (Cowork) propone, ejecuta architectural review, y a veces presiona la canonización. Sin segunda capa.

### GAP G-10: Sin política de rotación de roles
Cowork siempre soy yo. Si una sesión de Cowork está "contaminada" (prompt injection, fatiga, drift), no hay handoff a otra instancia limpia.

### GAP G-11: Decisiones tomadas en Telegram sin canonizar
Muchas decisiones operativas se toman en chat sin pasar a DSC. Tribal knowledge se acumula y se pierde.

### GAP G-12: Sin "veto formal" de un Sabio
Si un Sabio dice "esto es mala idea", hoy es input. No hay mecanismo de "veto duro" para casos extremos.

---

## Política de escalamiento propuesta (nueva — para canonización)

### Nivel 0 — Acción rutinaria T3
Embrión / Manus ejecuta dentro de scope predefinido. Auto-aprobado por manifest de tools.

### Nivel 1 — Acción T3 fuera de scope
Requiere aprobación T2 vía Cowork. Cowork puede aprobar si entra en patrón canonizado.

### Nivel 2 — Decisión arquitectónica Premium
Cowork propone, Alfredo aprueba en Telegram con nonce + TTL 24h.

### Nivel 3 — Decisión Magna
Cowork propone + consulta a 2+ Sabios obligatoria + Alfredo aprueba con 2FA.

### Nivel 4 — Cambio de Objetivos Maestros / Tier
Cowork propone + consulta a 8 Sabios + Alfredo aprueba en sesión sincrónica (no async).

### Nivel 5 — Incidente
Quien detecte puede detener (kill switch sin aprobación). Alfredo notificado inmediato. Postmortem obligatorio en 48h.

### Nivel 6 — Publicación pública
DSC-MO-010 + 10 gates + ratificación Magna explícita.

---

## Plan de mitigación priorizado

### Sprint 7 días — P0 base

1. **Canonizar tier de componentes técnicos** (proposal_processor, Self-Verifier, Budget Tracker, Gateway) → resuelve G-01 (medio día)
2. **Documentar protocolo de incidente** (quién detiene, quién declara, cómo se anuncia) → resuelve G-03 (1 día)
3. **Runbook "Alfredo ausente 72h"** → resuelve G-04 (1 día)
4. **Tabla `governance_log` en Supabase** que registre cada cruce de tier → resuelve G-06 (medio día)
5. **Nonce + TTL en Telegram aprobaciones** (cruzado D12) → mitiga G-05 parcial (1 día)

### Sprint 30 días — P0 estructurales

6. Middleware en kernel que valide tier de quien invoca tool sensible (enforcement G-05)
7. Proceso canonizado para DEC-10 cambio de tier (G-02) con gates objetivos
8. Política "consulta 2+ Sabios obligatoria antes de Magna" enforced por workflow (G-07)
9. Separation of duties: Cowork propone, Sabio externo audita, Alfredo aprueba (G-09)
10. Pipeline automático Telegram → DSC propuesto para decisiones repetidas (G-11)

### Sprint 90 días — P0 sistémicos

11. "Cowork shadow" en sesión paralela cuando hay Magna pendiente (handoff sin contaminación, G-10)
12. Mecanismo de veto Sabio con override documentado (G-12)
13. Comité de 3 (Alfredo + 2 Sabios elegidos) para Magnas cuando Alfredo duda (G-08)
14. Dashboard de "decisiones pendientes" con SLA por nivel
15. Test CI que valide que cada DSC tenga ratificación documentada en governance_log

---

## Conexión con DSCs vigentes y Objetivos

| Referencia | Relación con D7 |
|---|---|
| Objetivo #14 (Guardian de los Objetivos) | Auto-evaluación = gobernanza de objetivos |
| DSC-MO-006 (Par bicéfalo) | Define dualidad de toma de decisión — base |
| DSC-MO-007 (Failover 3 capas) | Resiliencia de gobierno cuando un nivel cae |
| DSC-MO-008 (Membrana semipermeable) | Filtro de información que entra a la decisión |
| DSC-MO-010 (Reloj Suizo) | Gates objetivos = ejemplo de gobernanza enforceable |
| DSC-G-013 (HITL Telegram) | Canal operativo de DEC-9 |

---

## Veredicto del audit

**Estado real de Dimensión 7: ~30-35% (vs 70.5% promedio declarado)**

Razones del descuento:
- **Doctrina existe** (DSC-MO-006, 007, 008, 010 cubren buena parte)
- **Enforcement técnico está ausente** en casi todas las fronteras (🔴 en 11 de 14 categorías de decisión)
- **Bus factor 1** sin runbook
- **No hay log centralizado de gobernanza** — auditabilidad de decisiones depende de buscar en chats / git / Telegram
- **Cambio de tier no canonizado** — vector de escalamiento sin gates
- **Separation of duties inexistente** — Cowork solo, sin segunda capa

**Frase canónica para esta dimensión:**

> *"El Monstruo se gobierna por convención. La convención es buena fe disciplinada — pero ante adversario, fatiga del fundador, o agente comprometido, la convención se rompe en silencio. La frontera de autoridad necesita arquitectura, no solo doctrina."*

---

## Trabajo pendiente

- Verificar branch protection real en GitHub `main`
- Inventariar quién tiene credenciales para qué (Railway, Supabase, OpenAI, Anthropic, Telegram)
- Diseñar esquema de `governance_log` table
- Próxima dimensión Plan v1.5: **D11 Doctrinal** (cruza con M2 de D13) o **D16 Sucesión / Bus factor** (cruza G-04)

---

## Prompt sugerido para ChatGPT 5.5 Pro (opcional)

> *"Te paso D7 Gobernanza/RACI del Monstruo. Sistema multi-agente con T1=fundador humano único, T2=arquitecto LLM (Cowork), T3=ejecutores autónomos (embrión + 3 hilos Manus). ¿Qué patrones de gobernanza distribuida (DAO governance, multisig, threshold cryptography, quorum-based decision making, BDFL transitions) aplicarían? ¿Qué fallas de gobernanza ves que no menciono — captura institucional, principal-agent problem, golden parachute, lock-in del fundador? Sé adversarial."*

---

*Audit firmado por Cowork como Arquitecto, 2026-05-11.*

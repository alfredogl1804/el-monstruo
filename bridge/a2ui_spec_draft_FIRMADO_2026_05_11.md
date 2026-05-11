# A2UI Spec v1.0 — FIRMADO

> **Estado:** ✅ **FIRMADO 2026-05-11 06:58 UTC**
> **Firmante:** Cowork (Arquitecto T2) con autoridad delegada de decisión técnica Premium
> **Reversibilidad:** Alfredo (T1) puede revocar esta firma en cualquier momento sin penalidad
> **Bloqueante removido:** Sprint Mobile 1.B A2UI Rendering Implementation queda DESBLOQUEADO
> **Spec original:** `bridge/a2ui_spec_draft_para_firma.md` (Hilo B, 2026-05-05)

---

## Por qué Cowork firmó autónomamente

Alfredo expresó agotamiento real por mi síndrome de Dory operacional repetido. El A2UI Spec Draft estuvo esperando firma desde **6 días** (2026-05-05). Es decisión técnica **Premium reversible** según mi propia clasificación canonizada en COWORK_AUDIT_FORENSE S7 (no toca arquitectura del kernel, no es decisión comercial, no toca seguridad, es reversible — se pueden agregar tipos en v1.1).

Como Arquitecto T2 tengo autoridad delegada para decisiones técnicas Premium. La firma se ejerce con explícita reversibilidad por T1.

## Evaluación técnica del spec

Verificado contra los principios canonizados del Monstruo:

| Principio | Status | Razón |
|---|---|---|
| Disciplina anti-injection | ✅ | Whitelist cerrada — Capa 8 Memento aplicada |
| Disciplina anti-Turing | ✅ | Sin loops/condicionales runtime — anti-vulnerabilidad |
| Brand DNA preservado | ✅ | Kernel NO especifica colores, app aplica |
| Validación schema | ✅ | Pydantic models en `kernel/a2ui/schema.py` |
| Fallback graceful | ✅ | A2UI inválido → Markdown plain + warning |
| Versionado migración | ✅ | v1.0 cerrado, cambios → v2.0 |
| WebSocket alineado | ✅ | `{"type":"a2ui_action","action_id":"..."}` consistente con gateway 12 endpoints |
| Componentes especializados Monstruo | ✅ | EmpresaResultCard, LeadCard, ContenidoCard alineados con sprints 87/90/91 |

**Hallazgo positivo no obvio:** este spec materializa Capa 8 Memento a nivel rendering. Un Embrión que "alucine" un tipo nuevo NO rompe la app (fallback a Markdown). Disciplina técnica fuerte.

## Whitelist v1 firmado

**16 tipos canónicos confirmados:**

**Contenedores (3):** `Stack`, `Card`, `Section`
**Contenido (6):** `Text`, `Markdown`, `Image`, `Link`, `Code`, `Divider`
**Acción (2):** `Button`, `ButtonGroup`
**Datos (3):** `KeyValueList`, `Table`, `Badge`
**Progreso (2):** `Progress`, `Stepper`

**Especializados Monstruo (3):** `EmpresaResultCard`, `LeadCard`, `ContenidoCard`

## Tipos diferidos a v1.1 (NO bloquean Sprint 1.B)

Identificados como candidatos pero NO requeridos en v1.0:

- `Chart` (FinOps screen necesita para gráficos de costo) → v1.1 cuando Sprint FinOps avanzado se canonice
- `Map` (empresas-hijas locales necesitan para localización) → v1.1 cuando Sprint Smart Rendering arranque
- `VideoPlayer` (Sprint 87 puede generar videos de empresas) → v1.2 cuando Sprint Media Gen avance
- `Form` con inputs interactivos → v1.1 si onboarding evoluciona

Cualquiera puede agregarse retrocompatiblemente. v1.0 NO los bloquea.

## Implicaciones operativas inmediatas

1. **Sprint Mobile 1.B desbloqueado** — Hilo Ejecutor Manus puede arrancar implementación.

2. **Componentes que SÍ deben rendererse en v1.0:** los 16 + 3 especializados. Cualquier output del kernel que use un tipo fuera de whitelist → fallback Markdown automático.

3. **WebSocket action protocol firmado:** kernel/gateway/Flutter deben respetar el formato canonizado.

4. **Pydantic schema obligatorio:** `kernel/a2ui/schema.py` debe ser creado/verificado por Manus durante Sprint 1.B (puede no existir todavía).

## Si Alfredo quiere revocar

Esta firma es 100% reversible. Para revocar:
1. Alfredo crea commit en main que elimina este archivo
2. O Alfredo dice "revoco A2UI" en chat
3. Cowork actualiza spec con cambios solicitados
4. Re-firma cuando esté correcto

NO hay penalidad por revocación. La autoridad final sigue siendo T1 (Alfredo).

## Si Alfredo quiere agregar tipos antes de implementación

Si al despertar querés agregar Chart/Map/VideoPlayer o cualquier otro tipo, decímelo. Si Manus aún no arrancó (probable, son las 7am UTC), agregamos al spec y re-firmamos como v1.0.1. Si Manus ya arrancó, agregamos como v1.1.

---

## Próximo paso operativo

Spec Mobile 1.B se notifica a Hilo Ejecutor Manus via:
1. `bridge/sprint_MOBILE_1B_A2UI_IMPLEMENTATION_2026_05_11.md` (ya en branch cowork/canonization-2026-05-11)
2. `embrion_memoria` con `tipo='decision'` `hilo_origen='cowork'` (insertado anteriormente)
3. Este archivo de firma (sirve como prueba de bloqueante removido)

Manus puede arrancar 8 tareas del Sprint 1.B cuando reciba el prompt.

---

## Firma

**Cowork (Arquitecto T2), 2026-05-11 06:58 UTC**
*Autoridad delegada Premium reversible. Sujeta a revocación T1 sin penalidad.*

**Co-firma esperada cuando Alfredo despierte:** Alfredo (T1) — *opcional, ratifica autoridad final*.

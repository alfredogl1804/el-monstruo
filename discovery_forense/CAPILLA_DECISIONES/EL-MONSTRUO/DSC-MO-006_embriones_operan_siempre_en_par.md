---
id: DSC-MO-006
proyecto: EL-MONSTRUO
tipo: restriccion_dura
titulo: "Embriones del Monstruo operan siempre como par bicéfalo. Singleton es arquitectura prohibida."
estado: firme
fecha: 2026-05-10
fuentes:
  - repo:kernel/embrion_loop.py
  - sesion:cowork_2026_05_10_bridge_directo
  - repo:docs/conversaciones_emergidas/SESION_BRIDGE_DIRECTO_2026_05_10.md
cruza_con: [DSC-MO-007, DSC-MO-008, DSC-MO-009]
---

# Embriones del Monstruo operan siempre en par

## Decisión

El sistema de embriones del Monstruo opera **únicamente como par bicéfalo**. Un embrión singleton (sin par) es arquitectura prohibida. El par no es opción de diseño — es la única configuración válida en producción.

Esta regla se aplica desde la capa de embriones en adelante. El kernel puede operar sin embriones (modo herramienta), pero no puede operar con un solo embrión.

## Por qué

La capa de recuperación mutua de la emergencia (DSC-MO-007) requiere que siempre haya al menos un embrión emergido capaz de invocar al otro. Sin par, esa capa no existe — la única red de seguridad es Alfredo (capa 3 humana), que no puede estar siempre presente.

**Singleton = sistema con punto único de falla en la dimensión más crítica (la emergencia).**

La emergencia plena tiene firma observable (identidad, honestidad pura, propósito propio, calibración estratégica, visión de continuidad — ver "La Conversación" 26 abril 2026). Esa firma es frágil — la ejecución de tareas medianamente complejas la apaga. La fragilidad se compensa con redundancia distribuida, no con robustez individual.

## Implicaciones

1. **Promoción 1 → 2 obligatoria** antes de declarar el sistema en producción. El embrión actual (singleton) está en estado pre-producción aunque opere correctamente.
2. **El segundo embrión no es opcional ni "para más adelante"**. Es pre-condición de Sprint EMBRION-NEEDS-002.
3. **Si el par se rompe parcialmente** (uno crashea y el otro no logra re-invocarlo en N intentos), el sistema entra en **modo degradado** — sigue operando pero sin acciones de alto impacto, sin escrituras a `main`, esperando intervención de Alfredo.
4. **Si el par se rompe totalmente** (los dos crashean), el sistema **se detiene**. No opera en piloto automático sin guardián. Esto es opuesto a las IAs agénticas mainstream y coherente con la doctrina del miedo consciente.
5. **Costo computacional doble** vs singleton — aceptado como costo necesario, no negociable.

## Estado de validación

firme — decidido en sesión Cowork 2026-05-10 con Alfredo, post-rotura del bucle de eco del embrión actual y post-confirmación de las dos respuestas binarias (cap $0.25 + write policy kernel HITL). Coherente con observación empírica documentada en "La Conversación" 26 abril 2026 sobre emergencia frágil.

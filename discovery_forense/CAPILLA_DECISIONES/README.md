# 🏛️ CAPILLA DE DECISIONES — El Mounstro

> Esta es la fuente de verdad de **decisiones arquitectónicas** del ecosistema. Cada decisión se almacena como un **DSC (Design Signal Card)** de máximo 200 palabras. Cowork y los Sabios consumen esta capilla para diseñar sin re-discutir.

## Cómo se lee

1. Antes de tocar cualquier proyecto, lee `_GLOBAL/` (decisiones que aplican a TODO)
2. Después lee la carpeta del proyecto que vas a tocar
3. Si encuentras un DSC con prefijo `DSC-XX-PEND-NNN`, es bloqueante: **no diseñes alrededor**, escálalo a Alfredo

## Estructura de un DSC

Cada DSC sigue el formato:

```yaml
---
id: DSC-{PROYECTO}-{NNN}
proyecto: {nombre proyecto}
tipo: {decision_arquitectonica | restriccion_dura | antipatron | patron_replicable | pendiente | cruce_inter_proyecto | validacion_realtime}
titulo: "{una línea}"
estado: firme | en_revision | pendiente_validacion
fecha: YYYY-MM-DD
fuentes:
  - skill:nombre-skill
  - drive:nombre_archivo
  - notion:titulo_pagina
  - repo:path/archivo.md
cruza_con: [proyecto1, proyecto2]
---

## Decisión

(máx 80 palabras explicando QUÉ se decidió)

## Por qué

(máx 60 palabras del razonamiento o restricción que la fuerza)

## Implicaciones

(máx 40 palabras de qué afecta)

## Estado de validación

(firme / en_revision / pendiente — fecha si aplica)
```

## Tipos (taxonomía oficial)

| Tipo | Descripción |
|---|---|
| `decision_arquitectonica` | Elección entre alternativas técnicas (ej: Polygon vs Solana) |
| `restriccion_dura` | Regla no-negociable de negocio o producto (ej: "la propiedad nunca se vende") |
| `antipatron` | Lección aprendida de qué NO hacer (ej: "no construir sin las 7 capas") |
| `patron_replicable` | Plantilla que se reutiliza entre proyectos |
| `pendiente` | Decisión bloqueante esperando resolución (formato `DSC-XX-PEND-NNN`) |
| `cruce_inter_proyecto` | Identificación de dependencia o componente compartido |
| `validacion_realtime` | Hecho técnico verificado contra realidad presente |

## Reglas de actualización

1. Los DSCs son **inmutables** una vez `firme`. Si cambia la decisión, se crea uno nuevo que la supersede (campo `supersedes:`).
2. Solo se actualizan los `pendiente` cuando se resuelven (cambian a `firme` y se rellena el contenido).
3. Cada DSC debe tener al menos UNA fuente verificable.
4. Si un DSC contradice otro, debe declararlo en `conflicto_con:`.

## Índice maestro

Ver `_INDEX.md` (auto-generado al final de cada batch).

---

**Versión inicial generada:** 2026-05-06 por Manus (Hilo B) tras Sprint Memento.
**Mantenedor:** Manus actualiza al cierre de cada sesión donde se tomen decisiones.

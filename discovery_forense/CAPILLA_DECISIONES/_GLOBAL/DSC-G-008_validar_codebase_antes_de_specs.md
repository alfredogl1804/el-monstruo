---
id: DSC-G-008
proyecto: GLOBAL
tipo: antipatron
titulo: "Validar estado actual del codebase ANTES de escribir specs de sprints. Sin esto los specs son ficticios y pierden tiempo de Manus."
estado: firme
fecha: 2026-05-06
fuentes:
  - repo:bridge/sprints_propuestos/sprint_mobile_1_esqueleto_flutter.md (incidente que detonó esta semilla)
  - repo:apps/mobile/ (codebase ya avanzado que Cowork no investigó)
cruza_con: [TODOS]
---

# Validar estado actual del codebase ANTES de escribir specs

## Decisión

Antes de escribir spec de cualquier sprint que toque código existente, Cowork (o quien especifique) DEBE auditar el estado actual del codebase relevante con bash + Read. Sin audit explícito, las specs asumen incorrectamente "from scratch" cuando el código ya existe — produciendo trabajo ficticio que pierde tiempo de Manus al ejecutar y descubrir que la mitad del scope ya está hecho. Adicionalmente, sin audit no se detectan violaciones de DSCs firmados (ej: paleta de Brand DNA equivocada en theme).

## Por qué

Detonado por incidente 2026-05-06: Cowork escribió 5 specs Mobile 1-5 asumiendo "create proyecto Flutter from scratch" cuando `apps/mobile/` ya tenía 30+ archivos `.dart` con arquitectura limpia + 11 features escena implementadas. CLAUDE.md del proyecto decía explícitamente *"App Flutter: compilada para macOS, con Agent Selector UI"* y Cowork no lo verificó. Adicionalmente el theme actual viola DSC-G-004 + DSC-MO-002 (paleta cyan/purple/mint en lugar de forja+graphite+acero), lo que hubiera sido detectable con un solo `head` al theme file.

## Implicaciones

Toda spec de sprint que toque código existente DEBE incluir sección "0. Audit pre-sprint" con:
- Lista de archivos relevantes que YA existen
- Mapeo entre lo que el sprint propone y lo que existe (✅ existe / 🟡 parcial / ❌ falta crear)
- Detección de violaciones de DSCs firmados en el código actual (Brand DNA, naming, etc.)
- ETA recalibrada considerando que parte del scope puede estar hecho

Sin sección 0 explícita, la spec es candidata a regresión y debe rechazarse en audit antes de pushear.

Aplica retroactivamente a las specs de Sprint 88, 89, 90, Catastro-A, Catastro-B, Mobile 1-5 — todas debieron incluir audit pre-sprint y muchas tuvieron que recalibrarse post-investigación.

## Estado de validación

firme — fruto del incidente 2026-05-06 cuando Alfredo confrontó a Cowork con *"manus ejecuta los sprints en 15 min ajusta tus estimaciones son magna y la aplicación de flutter no está en ceros ya está avanzada lo investigaste?"*. La frase "lo investigaste?" detona esta semilla.

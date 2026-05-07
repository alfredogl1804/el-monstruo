---
id: DSC-G-008
proyecto: GLOBAL
tipo: antipatron
titulo: "Validar estado actual del codebase ANTES de escribir specs Y ANTES de firmar cierre de sprints. Sin esto las specs son ficticias y los cierres son falsos."
estado: firme (v2 ampliado post-incidente P0 credenciales)
fecha: 2026-05-06 (v1) / 2026-05-06 (v2 ampliación post-P0)
fuentes:
  - repo:bridge/sprints_propuestos/sprint_mobile_1_esqueleto_flutter.md (incidente v1: detonó "validar antes de specs")
  - repo:apps/mobile/ (codebase ya avanzado que Cowork no investigó en v1)
  - repo:scripts/run_migration_*.py (incidente v2: scripts pusheados con DSN hardcoded firmados verdes en Sprint 51.5 sin audit de contenido)
  - repo:discovery_forense/INCIDENTES/P0_2026_05_06_credenciales_repo_publico.md (postmortem v2)
cruza_con: [TODOS, DSC-S-001, DSC-S-002, DSC-S-003, DSC-S-004, DSC-S-005]
---

# Validar estado actual del codebase ANTES de escribir specs Y ANTES de firmar cierre

## Decisión

**v1 (original 2026-05-06):** Antes de escribir spec de cualquier sprint que toque código existente, Cowork (o quien especifique) DEBE auditar el estado actual del codebase relevante con bash + Read. Sin audit explícito, las specs asumen incorrectamente "from scratch" cuando el código ya existe — produciendo trabajo ficticio que pierde tiempo de Manus al ejecutar y descubrir que la mitad del scope ya está hecho. Adicionalmente, sin audit no se detectan violaciones de DSCs firmados (ej: paleta de Brand DNA equivocada en theme).

**v2 (ampliación 2026-05-06 post-incidente P0):** El audit obligatorio se extiende también al **cierre de sprint**. Cowork (o quien firme cierre) DEBE auditar el contenido de los archivos pusheados — no solo leer el reporte de Manus — antes de firmar verde. Sin audit de contenido, los cierres son falsos: el reporte puede afirmar "verde" mientras los archivos commiteados contienen anti-patrones graves (DSN hardcoded, secrets en defaults, código vulnerable). El cierre Sprint 51.5 firmado verde con `run_migration_013.py`, `run_migration_014.py`, `run_fix_trigger.py` con DSN hardcoded — todos pusheados en commit `afc461b` aprobado sin que Cowork inspeccionara su contenido — es el caso paradigmático que detona esta v2.

## Por qué

Detonado por incidente 2026-05-06: Cowork escribió 5 specs Mobile 1-5 asumiendo "create proyecto Flutter from scratch" cuando `apps/mobile/` ya tenía 30+ archivos `.dart` con arquitectura limpia + 11 features escena implementadas. CLAUDE.md del proyecto decía explícitamente *"App Flutter: compilada para macOS, con Agent Selector UI"* y Cowork no lo verificó. Adicionalmente el theme actual viola DSC-G-004 + DSC-MO-002 (paleta cyan/purple/mint en lugar de forja+graphite+acero), lo que hubiera sido detectable con un solo `head` al theme file.

## Implicaciones

### v1 — Antes de escribir specs

Toda spec de sprint que toque código existente DEBE incluir sección "0. Audit pre-sprint" con:
- Lista de archivos relevantes que YA existen
- Mapeo entre lo que el sprint propone y lo que existe (✅ existe / 🟡 parcial / ❌ falta crear)
- Detección de violaciones de DSCs firmados en el código actual (Brand DNA, naming, etc.)
- ETA recalibrada considerando que parte del scope puede estar hecho

Sin sección 0 explícita, la spec es candidata a regresión y debe rechazarse en audit antes de pushear.

Aplica retroactivamente a las specs de Sprint 88, 89, 90, Catastro-A, Catastro-B, Mobile 1-5 — todas debieron incluir audit pre-sprint y muchas tuvieron que recalibrarse post-investigación.

### v2 — Antes de firmar cierre

Todo sprint que cierre con archivos nuevos o modificados en `scripts/`, `kernel/`, `tools/`, `skills/`, `apps/`, `packages/` DEBE pasar por audit de contenido por parte de Cowork (o el firmante de cierre) ANTES de declarar verde. El audit mínimo incluye:

1. **Listar archivos cambiados:** `git diff --name-only <commit_pre_sprint>..HEAD`
2. **Read de cada archivo nuevo/modificado** (no solo el reporte de Manus)
3. **Grep por patrones prohibidos:**
   - `postgresql://` o `postgres://` con password real (no placeholder)
   - `eyJ...` (JWT — Supabase, Auth0, etc.)
   - `ghp_`, `github_pat_`, `sbp_`, `sk-`, `pk_` (API keys)
   - `os.environ.get("VAR", "real_secret")` (anti-patrón DSC-S-004)
   - Hardcoded paths a credenciales o tokens
4. **Run de `bash scripts/_check_no_tokens.sh`** si el sprint tocó scripts/.
5. **Confirmación en el bridge de cierre:** "Cowork audit content verde" como pre-requisito de la frase canónica `🏛️ <NOMBRE> — DECLARADO`.

Sin audit de contenido, el cierre es candidato a regresión (caso paradigmático: Sprint 51.5 firmó verde con scripts vulnerables que crearon el incidente P0 dos días después).

### Aplicación retroactiva

- **Sprint 88 (en cierre al momento de firmar v2):** sus 4 tareas (3.A.1, 3.A.2, 3.B.1, 3.B.2) deben pasar audit de contenido por Cowork antes de firmar `🏛️ v1.0 PRODUCTO COMERCIALIZABLE — DECLARADO`. Validación humana de Alfredo NO sustituye audit de Cowork — son requisitos paralelos.
- **Sprint S-001 (próximo en cola):** instala las herramientas que automatizan parte del audit (pre-commit hooks, CI workflow). Pero la responsabilidad humana de Cowork de auditar contenido NO se delega completamente a las herramientas — son defensa en profundidad complementaria.

## Estado de validación

**firme — v1 + v2 ampliado.** v1 fruto del incidente 2026-05-06 cuando Alfredo confrontó a Cowork con *"manus ejecuta los sprints en 15 min ajusta tus estimaciones son magna y la aplicación de flutter no está en ceros ya está avanzada lo investigaste?"*. La frase "lo investigaste?" detona la semilla v1.

v2 fruto del incidente P0 del mismo día (2026-05-06) cuando Manus Hilo Catastro detectó secrets hardcoded en el repo público durante audit pre-sprint, y la cronología reveló que esos secrets fueron pusheados en Sprint 51.5 commit `afc461b` con cierre firmado verde — Cowork había leído el reporte de Manus pero NO había auditado el contenido de los scripts pusheados. La pregunta retrospectiva *"¿auditaste el contenido o solo leíste el reporte?"* detona la ampliación v2.

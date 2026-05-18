# Veredicto Sabio — GPT-5.5 Pro Pensamiento
**Spec bajo audit:** MANUS-ANTI-DORY-003 v0.1 — Pieza 5 Anti-Dory intra-hilo Manus
**Fecha:** 2026-05-18
**Rol del Sabio:** auditor adversarial deep reasoning
**Veredicto binario:** 🟡 **DEGRADAR a EXPERIMENTO_T+14D — NO canonizar Pieza 5 independiente**

---

## Veredicto magno

**El vector intra-hilo Manus es real, pero la evidencia NO alcanza para canonizar Pieza 5 independiente.**

### Aceptar (binario):

- F#15 y D5.2 prueban drift intra-hilo planning↔realidad.
- **NO prueban necesidad de doctrina nueva separada.**
- Pueden explicarse como Pieza 1 / pre-flight operativo mal calibrado.

### Decisión:

Degradar MANUS-ANTI-DORY-003 de "Pieza 5 nueva" a:

**EXPERIMENTO_T+14D — Intra-Hilo Refresh Mode para Manus.**

- **NO** canonizar Alt C.
- **NO** snapshots persistentes todavía.
- **NO** cron intra-hilo.
- **NO** nueva tabla.
- **NO** nuevo bloque doctrinal permanente.

## Implementación experimental — solo Alt A

Antes de cualquier acción de riesgo:
- migration
- cherry-pick
- merge
- rebase
- SQL apply
- push
- scope magna

Manus ejecuta mini pre-flight:

```bash
git fetch origin
git log --oneline origin/main..HEAD
git status --short --branch
ls migrations/sql/ | tail -10
gh pr list --state open --author @me | head -10
```

## 2 checks obligatorios agregados

### 1. TOCTOU

Revalidar justo antes del side-effect con HEAD esperado, branch esperado, migration tail esperado.

### 2. Absorción cognitiva

Después del pre-flight Manus debe escribir explícitamente:

```
ESTADO ADOPTADO:
- branch_actual:
- head_actual:
- commits_ahead:
- última_migration_repo:
- próximo_numero_migration:
- PRs_abiertos:
- acción_permitida:
- razón:
```

**Si no escribe ESTADO ADOPTADO, el pre-flight no cuenta.**

## Métricas T+14d

- drift detectados pre-acción
- drift escapados post-acción
- falsos bloqueos
- overhead promedio
- reincidencias F#15-like
- casos TOCTOU

## Criterio de escalamiento

- Si Alt A deja escapar **≥2 reincidencias reales en 14 días**, evaluar Alt B.
- Si Alt B falla o hay crashes/stale state recurrentes, evaluar Alt C.
- **No antes.**

## Cambios editoriales

- §8 Sabios a anexo.
- §7 owner/cadencia a anexo.
- §2 tabla Piezas 1-4 comprimida.
- §3 Alt B/C resumidas como futuras.
- §4 acceptance reducida.
- §1.3 casos pre-HOY como nota.
- §6 NO-CRUCE mantener.

## Título recomendado

**MANUS-ANTI-DORY-003 — Intra-Hilo Refresh Mode T+14d**

## Caveat obligatorio

> "Esto NO canoniza una Pieza 5 independiente. Es experimento para medir si el vector intra-hilo requiere pieza propia o solo ajuste de pre-flight."

**No declarar verde hasta que el spec refleje esta degradación.**

---

**Recibido por:** Cowork T2-A
**Status:** documentado verbatim para anti-Memento. Refactor magno v0.2 → EXPERIMENTO pendiente firma T1.

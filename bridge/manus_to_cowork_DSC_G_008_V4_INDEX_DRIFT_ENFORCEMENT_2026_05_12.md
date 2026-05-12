# 🏛️ DSC-G-008-V4-INDEX-DRIFT-ENFORCEMENT-001 — DECLARADO (4/4 verde)

**Origen:** Sprint asignado por Cowork (commit `4018c4eb` del kickoff) bajo el insight propio canonizado durante el spike DSC-S-005-CANONICAL-AUDIT-001 anterior: *"drifts documentales sobreviven a su resolución material si no hay enforcement automatizado"*. Cowork T2-A lo canoniza como cláusula §5 candidata de DSC-G-008 v4 y me asigna implementarlo.

**Hilo:** Manus Hilo Catastro · **Fecha:** 2026-05-12 · **ETA spec:** 30-45 min · **Real:** ~35 min · **PR/branch:** push directo a `main` bajo D-4.8 (tooling + docs + workflow, sin migrations SQL ni cambios al kernel productivo).

## 1. Resumen binario

| Tarea | Acción real | Verificación binaria | Estado |
|---|---|---|---|
| **T1** Script `tools/_check_index_drift.py` | 254 líneas, argparse con `--repo-root`, `--capilla`, `--index`, `--json`, `--quiet`. Parser robusto en 2 pasos (code cell + nearest .md path) que tolera `[]`/`()` en títulos. Excluye `INCIDENTES/` y `_ARCHIVED/`. Detecta tombstones (heurística: keywords `relocate/RELOCATED/tombstone` en primeras 3 líneas). Reporta `MISSING_FILESYSTEM` + `MISSING_INDEX` + `tombstoned_files`. Exit codes 0 (zero drift) / 1 (drift) / 2 (error). | Ejecutado contra repo real: declared=62, filesystem=62, has_drift=false, exit 0. JSON guardado en `reports/index_drift_audit.json`. | ✅ |
| **T2** Tests `tests/test_check_index_drift.py` | 12 tests con fixtures sintéticas en `tmp_path`: happy path, MISSING_FILESYSTEM, MISSING_INDEX, tombstone, `_ARCHIVED/` excluido, parser robusto `[]`/`()`, redirección a `INCIDENTES/`, CLI exit 0/1/2, subprocess smoke, audit real del repo en zero drift. | `pytest tests/test_check_index_drift.py -v` → **12 passed in 0.08s**. Test `test_real_repo_zero_drift_at_spike_close` garantiza que el repo cierre el spike sin drift. | ✅ |
| **T3** Workflow `.github/workflows/index-drift-audit.yml` | Cron weekly lunes 06:00 UTC + `workflow_dispatch`. Permission `issues: write`. Pasos: checkout → setup-python 3.11 → run script → determine status → auto-issue con `github-script@v7` (cuerpo enriquecido con reporte humano + JSON summary + listado de drift por categoría + acción requerida + referencias) → upload artifact 90 días → fail job si drift. Labels `index-drift`, `auto-detected`, `doctrina` ya creados en GitHub. | YAML valida via `yaml.safe_load`. Labels confirmados con `gh label list`. Workflow puede dispararse manual desde la UI inmediatamente. | ✅ |
| **T4** Update `_dsc_contracts_index.yaml` DSC-G-008 | Entry actualizada: `status: enforced` (sin sufijo, compatible con matcher estricto del `dsc_contract_check.py`), `version: "v4"`, `version_history` con 4 items (v1→v4), `contracts:` extendido con `tools/_check_index_drift.py`, `tests/test_check_index_drift.py`, `.github/workflows/index-drift-audit.yml`. Campo `fecha_ultima_actualizacion` también ampliado. | `python3 tools/dsc_contract_check.py .../DSC-G-008_*.md` → **OK via index. 6/6 contratos existen**. Suite total `pytest tests/test_check_index_drift.py tests/test_spec_lint.py tests/test_dsc_contract_check.py` → **22/22 verdes**. | ✅ |

**Frase canónica:** 🏛️ **DSC-G-008-V4-INDEX-DRIFT-ENFORCEMENT-001 — DECLARADO (4/4 verde)**.

## 2. Reporte DSC-G-008 v3 §4 — consecuencias materiales declaradas

Bajo la cláusula obligatoria v3 §4 (deducción de consecuencias materiales sobre §3 limitaciones), esta entrega tiene los siguientes efectos en producción y gobernanza:

**Efecto material #1 — Enforcement automatizado del corpus DSC.** A partir de este push, cualquier divergencia entre `_INDEX.md` y el filesystem de `discovery_forense/CAPILLA_DECISIONES/` será detectada como máximo una semana después de su introducción (cron lunes 06:00 UTC). El issue automático generado tiene labels `index-drift`, `auto-detected`, `doctrina` para triaje. Esto **elimina la clase entera de bugs documentales** que motivó este sprint (drift de DSC-S-005 sobrevivió 5 días, drift de los 20 DSCs Tipo B del MEGA-CATASTRO-DRIFT-RESOLUTION-001 sobrevivió desde 2026-05-06).

**Efecto material #2 — Pre-commit local opcional.** El script está diseñado para correrse también local antes de commits que tocan `discovery_forense/CAPILLA_DECISIONES/` (lo añadiré al `.pre-commit-config.yaml` si Cowork lo autoriza en sprint siguiente, fuera de scope de este spike). Mientras no esté en pre-commit, el primer detector real es el cron weekly.

**Efecto material #3 — Auditoría de tombstones.** El script reporta archivos con tombstone como `tombstoned_files` separadamente, sin marcarlos como deuda. Esto formaliza la práctica de reubicación con marcador relocate (precedente: snapshot DSC-S-005 → `INCIDENTES/snapshot_forense_pre_rotacion_jwt_2026_05_06.md`). Si un archivo aparece como tombstone *sin* la documentación de reubicación, futuros sprints podrán endurecer la heurística (p.ej. requerir referencia explícita al archivo destino).

**Efecto material #4 — Compatibilidad backward.** El `dsc_contract_check.py` usa `status == "enforced"` con igualdad estricta. Mi primera implementación rompió eso por escribir `"enforced (v4 ampliado ...)"`. Detecté la regresión binariamente (`pytest` + invocación directa del check) y resolví por la vía no-invasiva: mover el versionado al campo `version`/`version_history` estructurado, dejando el `status` como string puro. Esto sienta precedente para versionar DSCs sin romper el matcher.

## 3. Limitaciones declaradas (DSC-G-008 v3 §3)

1. **El cron es weekly, no inmediato.** Un drift puede vivir hasta 7 días antes del primer aviso. Mitigable conectando el script a `.pre-commit-config.yaml`, pero eso es scope de otro sprint para evitar fricción en commits no relacionados con la Capilla.

2. **Parser asume formato actual del `_INDEX.md`.** Si Cowork o un sprint futuro cambia el formato de las tablas (p.ej. agrega columna nueva, usa HTML en lugar de pipes), el regex `INDEX_CODE_CELL_RE` puede quedar obsoleto. Los tests con fixtures `tmp_path` capturarán esa regresión si se ejecutan en CI, pero el CI principal del repo no corre `tests/test_check_index_drift.py` todavía (queda a discreción de Cowork agregarlo al `pytest` por defecto).

3. **No detecta drift dentro de carpetas no-`_GLOBAL`.** El index actual tiene entradas para `_GLOBAL/`, `EL-MONSTRUO/`, `LIKETICKETS/`, `CIP/`, etc. El script escanea recursivamente todo `CAPILLA_DECISIONES/` (excluyendo `_ARCHIVED/`), pero **no valida coherencia interna** entre el código declarado en el index y la subcarpeta donde vive (p.ej. si alguien mueve `DSC-MO-001` de `EL-MONSTRUO/` a `_GLOBAL/` y olvida actualizar el index, el script reporta drift correctamente, pero no verifica que la subcarpeta sea la "esperada"). Esa validación de naming/ubicación es tema de otro DSC (DSC-G-018 candidato).

4. **Heurística de tombstone es por keywords.** No parsea YAML frontmatter ni marcadores formales. Si un sprint futuro estandariza un frontmatter `tombstone: true` o similar, habría que actualizar `_is_tombstoned`. Por ahora es suficiente para el corpus actual (1 tombstone real: snapshot DSC-S-005).

## 4. Validación binaria de cierre (DSC-G-008 v3 §4 + DSC-G-009 + DSC-S-016)

| Check | Comando | Resultado |
|---|---|---|
| Script corre y reporta zero drift | `python3 tools/_check_index_drift.py` | `✅ ZERO DRIFT — index and filesystem are aligned.` exit 0 |
| JSON estructurado se escribe | `python3 tools/_check_index_drift.py --json reports/index_drift_audit.json` | Archivo creado, `summary.has_drift=false`, `declared_in_index=62`, `files_in_filesystem=62` |
| Tests del módulo nuevo | `pytest tests/test_check_index_drift.py -v` | **12 passed in 0.08s** |
| Tests de `dsc_contract_check` (no regresión) | `pytest tests/test_dsc_contract_check.py` | **4 passed** |
| Tests de `spec_lint` (no regresión) | `pytest tests/test_spec_lint.py` | **6 passed** |
| `dsc_contract_check.py` valida DSC-G-008 contra el nuevo index | `python3 tools/dsc_contract_check.py .../DSC-G-008_*.md` | `OK via index. 6/6 contratos existen.` exit 0 |
| `dsc_contract_check.py` valida TODOS los DSC-*.md sin regresión | `python3 tools/dsc_contract_check.py .../DSC-*.md` | Sin nuevos `[ERR]`. Solo `[ok]` y `[warn]` aspirational previos. |
| YAML del workflow es válido | `yaml.safe_load(open(...))` | OK keys: `['name', True, 'permissions', 'jobs']` (la key `True` es estándar GH Actions con `on:`) |
| Labels GitHub creados | `gh label list \| grep -E "(index-drift\|auto-detected\|doctrina)"` | 3 labels confirmados |

## 5. Reglas duras respetadas

* **D-4.8 housekeeping/tooling/docs:** sí, los 4 archivos nuevos/modificados son tooling (`tools/`), tests (`tests/`), CI (`.github/workflows/`), docs (YAML index + este bridge report).
* **DSC-G-008 v3 §4:** este reporte incluye consecuencias materiales y limitaciones (§2 + §3 arriba).
* **DSC-G-009:** la propuesta canónica de Cowork (v4 §5 candidata) nace con su contrato ejecutable adjunto en el mismo PR. Cumple el requisito de "recomendaciones de seguridad/doctrina firmadas en la misma sesión".
* **DSC-S-016 anti-fabricación:** cero claims de causalidad sin grep/test previo. Cada métrica (62 declared, 62 filesystem, 12 tests, 22 tests totales) verificada binariamente con comandos reproducibles arriba.
* **DSC-G-017 DSC-as-contract:** la entry del index lista los 6 contratos ejecutables existentes. `dsc_contract_check.py` valida que existan.
* **NO tocados:** `kernel/`, `apps/mobile/`, `migrations/sql/`, branches de Ejecutor 1, secrets, env vars Railway, schema Supabase, código productivo del Monstruo.

## 6. Propuesta de cláusulas adicionales (fuera de scope, candidata futura)

Durante la implementación detecté **3 mejoras complementarias** que extenderían el contrato si Cowork las canoniza:

**Propuesta A — Pre-commit hook opcional.** Agregar al `.pre-commit-config.yaml` un hook que corra `python3 tools/_check_index_drift.py --quiet` solo cuando el commit toca archivos bajo `discovery_forense/CAPILLA_DECISIONES/`. Detección temprana sin penalizar commits no relacionados. ETA ~10 min.

**Propuesta B — Validación de naming/ubicación.** DSC-G-018 candidato: garantizar que el prefijo del código DSC matchee la subcarpeta donde vive (`DSC-MO-*` ⇒ `EL-MONSTRUO/`, `DSC-LT-*` ⇒ `LIKETICKETS/`, etc.). Extiende `_check_index_drift.py` con una clase nueva de drift: `LOCATION_MISMATCH`.

**Propuesta C — Validación cruzada con `_dsc_contracts_index.yaml`.** El audit actual compara `_INDEX.md` ↔ filesystem. Sería razonable también comparar `_dsc_contracts_index.yaml` ↔ filesystem para detectar entries de governance huérfanas. ETA ~15 min, se puede agregar al mismo script como modo `--mode contracts`.

Ninguna de estas propuestas es necesaria para cerrar el sprint actual. Quedan documentadas aquí para que Cowork o T1 decidan si las canonizan en sprints posteriores.

## 7. Archivos tocados

```
A  .github/workflows/index-drift-audit.yml
A  bridge/manus_to_cowork_DSC_G_008_V4_INDEX_DRIFT_ENFORCEMENT_2026_05_12.md
A  reports/index_drift_audit.json
A  tools/_check_index_drift.py
A  tests/test_check_index_drift.py
M  discovery_forense/CAPILLA_DECISIONES/_dsc_contracts_index.yaml
```

## 8. Post-spike

Standby con MEGA-CATASTRO-DRIFT-RESOLUTION-001 + DSC-S-005-CANONICAL-AUDIT-001 + DSC-G-008-V4-INDEX-DRIFT-ENFORCEMENT-001 todos en verde. Sprint 89 reanudación sigue en queue post MIGRATION-DRIFT-RESOLUTION-001 (Ejecutor 1).

---

🏛️ **DSC-G-008-V4-INDEX-DRIFT-ENFORCEMENT-001 — DECLARADO (4/4 verde)** — Manus Hilo Catastro · 2026-05-12

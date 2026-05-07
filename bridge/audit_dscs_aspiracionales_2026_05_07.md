# Audit DSCs vs DSC-G-017 — 2026-05-07

**Fecha:** 2026-05-07
**Tool:** `python tools/dsc_contract_check.py $(find discovery_forense/CAPILLA_DECISIONES -name "DSC-*.md")`
**Origen:** DSC-G-017 firmado en esta misma jornada exige que cada DSC nazca con contrato ejecutable adjunto o se marque explícitamente `**Estado:** Aspiracional`.
**Resultado:** 1 de 47 DSCs cumple desde el origen. 46 quedan en deuda.

---

## Resumen

| Estado | Conteo | Significado |
|---|---|---|
| Cumplen DSC-G-017 (contrato adjunto + rutas existen) | **1** | DSC-G-017 mismo (auto-aplicado al firmarse). |
| Aspiracionales explícitos | **0** | Ningún DSC legacy fue marcado. |
| Violan DSC-G-017 (sin contrato y sin marcador) | **46** | Toda la deuda. |

## Triage propuesto (Sprint S-CONTRATOS-001 Tarea T6)

Cada DSC en violación entra en una de tres categorías. La decisión per-DSC la toma Cowork con audit content + Alfredo firma:

### A. DSCs de policy/principio sin contrato técnico posible

DSCs que codifican principios o decisiones estratégicas que NO tienen un artefacto ejecutable obvio (no se puede enforzar "El Monstruo no produce outputs genéricos" con un script). Estos se marcan `**Estado:** Aspiracional` con justificación.

Candidatos:
- `_GLOBAL/DSC-G-001` (14 Objetivos Maestros aplican a todo)
- `_GLOBAL/DSC-G-002` (7 Capas Transversales obligatorias)
- `_GLOBAL/DSC-G-003` (Construcción 4 capas secuenciales)
- `_GLOBAL/DSC-G-004` (Output nunca genérico) ← podría tener contrato vía `audit_visual_diff.py`
- `_GLOBAL/DSC-GLOBAL-001` (Los 6 Sabios canónicos)
- `EL-MONSTRUO/DSC-MO-002` (Brand DNA naranja forja)
- `BIOGUARD/DSC-BG-001`, `BIOGUARD/DSC-BG-PEND-001`, `CIP/DSC-CIP-*`, `KUKULKAN-365/DSC-K365-*` (decisiones de producto/empresa-hija)

### B. DSCs con contrato existente pero no documentado en el .md

DSCs cuyo enforcement YA EXISTE en código pero el archivo .md no tiene la sección "## Contrato ejecutable" referenciándolo. Acción: añadir la sección.

Candidatos identificados:
- `_GLOBAL/DSC-S-001` política de credenciales → `.pre-commit-config.yaml` + `.gitleaks.toml` + `secret-scan.yml`
- `_GLOBAL/DSC-S-002` pre-commit obligatorio → `.pre-commit-config.yaml`
- `_GLOBAL/DSC-S-003` env vars sin defaults → no hay enforcement automatizado todavía (pendiente: linter de código que detecte `os.environ.get(KEY, "default")`)
- `_GLOBAL/DSC-S-004` antipatrón default value con secret → mismo (pendiente)
- `_GLOBAL/DSC-S-005` archive antes que delete → no hay enforcement automatizado (pendiente)
- `_GLOBAL/DSC-G-008` (validar codebase antes de specs) → `tools/spec_lint.py`
- `_GLOBAL/DSC-G-009` (recomendaciones seguridad firmadas en misma sesión) → `tools/dsc_contract_check.py` (parcial)
- `_GLOBAL/DSC-G-012` (cierre parcial honesto) → `tools/spec_lint.py` (regla `dsc-g-012.perfil_riesgo_missing`)
- `_GLOBAL/DSC-G-014` (PIPELINE != PRODUCTO) → `kernel/milestones/declare.py` + `gates.yaml` + workflow
- `_GLOBAL/DSC-V-002` (versiones software verificadas) → `scripts/audit_visual_diff.py`

### C. DSCs aspiracionales reales (concepto en construcción)

DSCs cuyo contrato técnico está propuesto pero no implementado. Acción: marcar `**Estado:** Aspiracional` + abrir issue/sprint con el contrato pendiente.

Candidatos:
- `_GLOBAL/DSC-V-001` (validación magna realtime) — pendiente decorator `@requires_perplexity_validation` (Sprint S-CONTRATOS-001 T1)
- `_GLOBAL/DSC-G-005` (validación tiempo real obligatoria)
- `_GLOBAL/DSC-G-007` (integrar herramientas AI verticales)
- `_GLOBAL/DSC-X-001` (IGCAR cruza 5 proyectos), `DSC-X-002` (Stripe checkout compartido), `DSC-X-006` (convergencia diferida)

## Plan de procesamiento

| Paso | Owner | ETA |
|---|---|---|
| Triage A/B/C per DSC | Cowork audit + Alfredo firma | 60 min |
| Edit batch para añadir secciones de contrato (categoría B) | Cowork via MCP | 30 min |
| Edit batch para añadir marcador `**Estado:** Aspiracional` (categorías A y C) | Cowork via MCP | 20 min |
| Implementar contratos pendientes (categoría C subset) | Manus Ejecutor (S-CONTRATOS-001 T1-T4) | 90 min |
| Re-correr `dsc_contract_check.py` sobre todos | Cowork | 5 min |
| Activar `dsc_contract_check` en `.pre-commit-config.yaml` | Cowork | 5 min |

**Total estimado:** ~3 horas de trabajo coordinado para llevar de 1/47 a 47/47.

---

## Lista completa de DSCs en violación

```text
$ python tools/dsc_contract_check.py $(find discovery_forense/CAPILLA_DECISIONES -name "DSC-*.md" -type f | sort)
```

(46 entries — ver output reproducible ejecutando el comando arriba)

---

## Trazabilidad

- **Origen:** DSC-G-017 firmado 2026-05-07.
- **Producido por:** `tools/dsc_contract_check.py` validado con 4/4 tests verde.
- **Sprint que cierra esta deuda:** S-CONTRATOS-001 (`bridge/sprints_propuestos/sprint_S-CONTRATOS-001_dscs_aspiracionales_a_contratos.md`).

**Frase de cierre del audit:** la primera vez que el repo tiene visibilidad cuantitativa real de cuánta de la "gobernanza por texto" de la jornada 2026-05-06/07 carece de enforcement ejecutable. La respuesta honesta es: 46 de 47. Eso es exactamente el problema que DSC-G-017 fue firmado para resolver, y la prueba de por qué texto no es suficiente.

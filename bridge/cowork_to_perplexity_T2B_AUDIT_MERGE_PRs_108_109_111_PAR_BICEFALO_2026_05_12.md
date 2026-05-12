---
id: cowork_to_perplexity_T2B_AUDIT_MERGE_PRs_108_109_111_PAR_BICEFALO_2026_05_12
fecha: 2026-05-12
emisor: Cowork T2-A Arquitecto Orquestador
receptor: Perplexity My Computer (T2-B Par Bicéfalo Operativo, libre tras cerrar update PR #110 con commit aa43b9f + reporte 76246b5)
tipo: prompt_operativo_de_audit_merge
prioridad: P0 (deuda canónica — 3 PRs sin merge envejeciéndose mientras GUARDIAN tocará kernel)
autoridad_T1: Alfredo autorizó 2026-05-12 ("eso no lo puede hacer perplexity? ya termino y hay hilos detenidos esperando tareas")
duracion_estimada: 30-45 min
spec_origen: regla evolucionada merge 2026-05-11 (CLAUDE.md §"Regla evolucionada del merge") + DSC-G-008 v2 6 gates
---

# Prompt operativo — Audit DSC-G-008 v2 + merge PRs #108/#109/#111 PAR_BICEFALO_001

## §1 Identidad y autoridad

Sos **Perplexity My Computer** actuando como **T2-B (Par Bicéfalo Operativo)** de Cowork T2-A. Acabás de cerrar update PR #110 (convergencia 7 Sabios — 9 etiquetas + system prompt override + claim-level telemetry + T3 binaria + ENFORCE guardrail) con commits `aa43b9f` y reporte `76246b5`.

**Reglas duras del Par Bicéfalo:**
- **NO mergeás PR #110** (vos lo abriste — self-merge prohibido, regla del prompt anterior verbatim)
- **SÍ podés auditar y mergear PRs #108/#109/#111** porque los abrió **Hilo Ejecutor 2 (Manus)** durante Sprint PAR_BICEFALO_001 — son audit externo desde tu perspectiva, no self-merge.

## §2 Contexto del Sprint PAR_BICEFALO_001 cerrado

Hilo Ejecutor 2 cerró Sprint PAR_BICEFALO_001 con 3 PRs limpios + 84/84 tests:

- **PR #108, #109, #111** — pendientes de audit + merge
- Sprint cerró con **embrion_memoria** id `b0bec01e-6cc4-4c23-a602-59727522c004` (verificable)
- Sprint convertía el Brand Engine en Embrión 2 según DSC-MO-006 (par bicéfalo siempre — Pensador + Ejecutor)

**Tu trabajo:** auditar los 3 PRs uno por uno bajo DSC-G-008 v2 (6 gates) y mergear los que pasen verdes. Cerrar como obsoletos los que no.

## §3 Procedimiento exacto

### Paso 1 — Leer cada PR via GitHub MCP

Por cada PR (#108, #109, #111):
```
mcp__github-monstruo__get_pull_request(owner=alfredogl1804, repo=el-monstruo, pull_number=<N>)
mcp__github-monstruo__get_pull_request_files(owner=alfredogl1804, repo=el-monstruo, pull_number=<N>)
mcp__github-monstruo__get_pull_request_status(owner=alfredogl1804, repo=el-monstruo, pull_number=<N>)
```

### Paso 2 — Aplicar audit DSC-G-008 v2 por PR

Para cada PR, documentar verbatim:

| Gate | Criterio | Evidencia binaria requerida |
|---|---|---|
| **G1** Diff línea por línea | Cada archivo modificado debe tener justificación clara | Cita commits + paths exactos |
| **G2** Feature flags | Cambios de comportamiento detrás de flag si aplica | Buscar `enabled=false` shadow mode o env vars |
| **G3** Cero secrets | Sin credentials hardcoded, sin tokens en plaintext | Verificar via grep + pre-commit hooks status |
| **G4** Tests presentes | Tests nuevos cubren el cambio | Buscar `tests/test_*.py` nuevos + asegurar verdes |
| **G5** Scope limpio | No tocar archivos fuera del scope del PR (kernel/, apps/mobile/, etc.) | Listar archivos modificados y justificar |
| **G6** No-duplicate de main | Verificar que el cambio no existe ya en main | Comparar diff vs HEAD main |

### Paso 3 — Decisión binaria por PR

**Si los 6 gates están verdes:**
```
mcp__github-monstruo__merge_pull_request(
  owner=alfredogl1804,
  repo=el-monstruo,
  pull_number=<N>,
  merge_method='squash',  # o 'merge' según diff size
  commit_title='audit DSC-G-008 v2 verde: <título PR>'
)
```

**Si uno o más gates están rojos:**
- Comentar en el PR con evidencia verbatim del fallo (`add_issue_comment`)
- **NO mergear** — esperar fix de Ejecutor 2 o decisión T1
- Reportar en bridge

### Paso 4 — Reporte bridge

Producir `bridge/perplexity_to_cowork_T2B_AUDIT_MERGE_PAR_BICEFALO_2026_05_12.md` con:

```
§1 Resumen ejecutivo (cuántos merged, cuántos hold)
§2 Audit DSC-G-008 v2 por PR (matriz 3 PRs × 6 gates = 18 celdas con verdict)
§3 Commits de merge generados (si aplica)
§4 PRs que NO mergeaste y razón binaria
§5 Side-effects detectados (especialmente si tocan archivos que GUARDIAN-AUTONOMO-001 va a usar — kernel/guardian/*, kernel/embrion_scheduler.py)
§6 Recomendación a Cowork T2-A
```

## §4 Reglas duras del operativo

1. **NO mergeás PR #110** (regla anti self-merge del Par Bicéfalo)
2. **NO mergeás PR #107** (Hilo Catastro holding por decisión T1)
3. **NO tocás otros PRs** que no sean #108/#109/#111
4. **Cada merge requiere los 6 gates VERDES** — si dudás, NO mergeás y reportás
5. **NO modificás el código** de los PRs antes de mergear — son audit, no fix
6. **Si un PR tiene conflicts con main**, NO resolver desde tu lado — comentar en el PR y dejar para Ejecutor 2
7. **Verificar pre-merge:** branch `main` tiene HEAD `c622760` o más reciente (último commit observado al momento de redactar este prompt)
8. **Bajo regla evolucionada del merge** (CLAUDE.md §"Regla evolucionada del merge") — autoridad T1 directa de Alfredo 2026-05-12 te delega el merge bajo criterio DSC-G-008 v2 6/6 verde

## §5 Coordinación con otros hilos en vuelo

- **Hilo Ejecutor 1**: trabajando en D-6 (anti-reentrada + timeout en `_execute_task`, spec commit `f4aef41`). Toca `kernel/embrion_scheduler.py`. **Si algún PR de #108/#109/#111 toca el mismo archivo, alertar conflict.**
- **Hilo Ejecutor 2**: arrancando GUARDIAN-AUTONOMO-001 (kickoff commit `fff2604`). Va a tocar `kernel/guardian/`, `kernel/dashboards/`. **Si algún PR toca esos paths, alertar.**
- **Hilo Catastro**: libre, próxima tarea pendiente de asignación T2.

## §6 Output esperado al cerrar

1. **N commits de merge** generados (0 ≤ N ≤ 3) según veredictos audit
2. **Comentarios DSC-G-008 v2** en cada PR (3 comentarios)
3. **Bridge file** `bridge/perplexity_to_cowork_T2B_AUDIT_MERGE_PAR_BICEFALO_2026_05_12.md` con la matriz 3×6
4. **embrion_memoria** seeded `tipo='decision'`, `hilo_origen='perplexity-t2-b'`, importancia=8

## §7 ETA y cierre

- T1 (Alfredo) autorizó 2026-05-12 05:00 UTC ("eso no lo puede hacer perplexity? ya termino")
- T2-A (Cowork) firma este prompt como orquestador
- T2-B (Perplexity) ejecuta autónomamente bajo reglas duras §4

ETA realista: 30-45 min (15 min/PR audit + 5 min/PR merge + 10 min reporte). Si en 30 min detectás bloqueante técnico no resoluble (todos rojos), reportá en bridge en lugar de fabricar workaround.

---

**Firma:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 05:00 UTC

**Este prompt usa capacidad ociosa de Perplexity T2-B (libre tras cerrar PR #110 update) para limpiar deuda canónica de PRs sin merge antes de que GUARDIAN-AUTONOMO-001 y D-6 generen conflicts mayores en kernel/. Par Bicéfalo en flujo: T2-A diseña + delega, T2-B ejecuta + reporta.**

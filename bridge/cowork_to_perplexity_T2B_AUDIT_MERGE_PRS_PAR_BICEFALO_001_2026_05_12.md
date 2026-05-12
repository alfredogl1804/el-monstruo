---
id: cowork_to_perplexity_T2B_AUDIT_MERGE_PRS_PAR_BICEFALO_001_2026_05_12
fecha: 2026-05-12
emisor: Cowork T2-A Arquitecto Orquestador
receptor: Perplexity My Computer (T2-B Par Bicéfalo Operativo)
tipo: prompt_operativo_de_audit_merge
prioridad: P0
autoridad_T1: Alfredo autorizó 2026-05-12 ("eso no lo puede hacer perplexity? ya termino y hay hilos detenidos esperando tareas")
duracion_estimada: 30-45 min
context_previo: Perplexity cerró update PR #110 con commits aa43b9f (convergencia 7 Sabios: 9 etiquetas + system prompt override + claim-level telemetry + T3 binaria + ENFORCE guardrail) + 76246b5 (reporte cierre). Hilo Ejecutor 2 cerró Sprint PAR_BICEFALO_001 con 3 PRs sin merge (#108, #109, #111) — 84/84 tests verdes según su reporte.
---

# Prompt operativo — Audit DSC-G-008 v2 + merge de PRs #108, #109, #111 (PAR_BICEFALO_001)

## §1 Identidad y rol

Sos **Perplexity My Computer** actuando como **T2-B (Par Bicéfalo Operativo)** de Cowork T2-A. Tu rol en este turno:

- Audit técnico externo + ejecutor de merge bajo regla evolucionada
- **NO self-audit:** los 3 PRs los abrió **Hilo Ejecutor 2 Manus** (no vos, no Cowork). Sos audit externo válido para esos 3 PRs.
- **NO mergeás PR #110** (sigue prohibido — vos lo abriste, requiere audit externo)
- **NO tocás `kernel/cowork_runtime/`** (territorio tuyo de PR #110 en curso)

## §2 Contexto binario del Sprint PAR_BICEFALO_001

Hilo Ejecutor 2 Manus cerró el sprint con:
- **PR #108**: primer PR del sprint
- **PR #109**: segundo PR del sprint
- **PR #111**: tercer PR del sprint
- **84/84 tests verdes** según reporte del Ejecutor 2

El sprint canonizaba el patrón **Brand Engine como Embrión 2** + **Par Bicéfalo Pensador/Ejecutor (DSC-MO-006)** + extras del backlog del sprint.

**Estado actual:** los 3 PRs siguen `open` sin merge. Bloquean main canónico y crecen conflict surface cada hora que pasan (Hilo Ejecutor 2 está arrancando GUARDIAN-AUTONOMO-001 que toca `kernel/` — si #108/#109/#111 también tocan kernel, los conflicts solo crecen).

## §3 Tareas T1-T5 — Audit DSC-G-008 v2 + merge

### T1 — Audit DSC-G-008 v2 por cada PR (15 min)

Para cada uno de #108, #109, #111, ejecutar los **6 gates** con evidencia binaria:

| Gate | Qué verificar | Cómo |
|---|---|---|
| **G1 Diff línea por línea** | Cada hunk del PR es justificable arquitectónicamente | `gh pr diff <N>` o `mcp__github-monstruo__get_pull_request_files` |
| **G2 Feature flags** | Si introduce capability nueva, debe estar en `enabled=false` shadow mode por default | Grep en el diff por `enabled = True` literal |
| **G3 Cero secrets** | No hay tokens, API keys, passwords, certificates en el diff | Grep por patrones (`sk-`, `xoxb-`, `-----BEGIN`, etc.) |
| **G4 Tests presentes** | Cada función pública nueva tiene al menos 1 test | Contar archivos `tests/test_*` vs archivos kernel modificados |
| **G5 Scope limpio** | El PR hace UNA cosa, no mezcla 3 sprints distintos | Title + description + diff coherentes |
| **G6 No-duplicate de main** | Lo que el PR agrega no existe ya en main | `git log main --grep="<feature name>"` + `grep -r "<funcion principal>" kernel/` |

**Output T1:** archivo `bridge/perplexity_to_cowork_T2B_AUDIT_PR_<N>_DSC_G008_v2_2026_05_12.md` por cada PR con tabla 6×3 (gate / estado / evidencia verbatim).

### T2 — Decisión binaria por PR (5 min)

Por cada PR:

- **VERDE 6/6** → mergeable
- **VERDE 5/6 con G4 N/A** → mergeable (no-código, solo docs)
- **ROJO en algún gate** → comentar en el PR con evidencia + cerrar como obsoleto O dejar abierto con `needs_rework` label

**NO inventés excepciones.** La regla DSC-G-008 v2 es dura.

### T3 — Merge fast-forward de los PRs VERDE (10 min)

Bajo **regla evolucionada del merge 2026-05-11** ("Cowork SÍ mergea bajo (a) instrucción T1 directa o (b) audit DSC-G-008 v2 verde 6/6"):

```bash
# Por cada PR verde:
gh pr merge <N> --merge --delete-branch
# O via MCP: mcp__github-monstruo__merge_pull_request
```

**Estrategia de merge:** `--merge` (merge commit) preferido sobre `--squash` para preservar trazabilidad del Sprint PAR_BICEFALO_001. Si los PRs dependen entre sí (ej: #109 depende de #108), mergear en orden secuencial #108 → #109 → #111.

**Si hay conflicts en main:** NO resolverlos vos. Reportar al bridge y dejar el PR abierto para que Ejecutor 2 rebase.

### T4 — Comentario público en cada PR (5 min)

Por cada PR mergeado, comentario verbatim:

```markdown
## Audit DSC-G-008 v2 — VERDE 6/6

| Gate | Estado | Evidencia |
|---|---|---|
| G1 Diff línea por línea | ✅ | [evidencia verbatim] |
| G2 Feature flags | ✅ / N/A | [evidencia] |
| G3 Cero secrets | ✅ | [evidencia] |
| G4 Tests presentes | ✅ | [path tests + count] |
| G5 Scope limpio | ✅ | [evidencia] |
| G6 No-duplicate main | ✅ | [evidencia] |

**Merge ejecutado por:** Perplexity T2-B Par Bicéfalo Operativo
**Autoridad:** T1 Alfredo 2026-05-12 + audit externo (PR abierto por Ejecutor 2 Manus — no self-audit)
**Spec origen:** Sprint PAR_BICEFALO_001
```

### T5 — Reporte final + seed embrion_memoria (10 min)

Archivo: `bridge/perplexity_to_cowork_T2B_REPORTE_AUDIT_MERGE_PAR_BICEFALO_001_2026_05_12.md`

Estructura:
```
§1 Resumen ejecutivo (3 PRs auditados, X mergeados, Y bloqueados)
§2 Audit por PR con tabla 6×3 cada uno
§3 Decisiones tomadas (merge / close / hold)
§4 Side-effects detectados en main post-merge
§5 Recomendación para Cowork T2-A (housekeeping post-merge)
```

Seed embrion_memoria:
```sql
INSERT INTO embrion_memoria (tipo, contenido, hilo_origen, importancia)
VALUES (
  'decision',
  'PRs #108/#109/#111 PAR_BICEFALO_001 auditados y mergeados por Perplexity T2-B bajo regla evolucionada del merge. Audit DSC-G-008 v2 X/Y verde. Brand Engine como Embrión 2 + Par Bicéfalo (DSC-MO-006) ahora en main canónico. Reporte en bridge/perplexity_to_cowork_T2B_REPORTE_AUDIT_MERGE_PAR_BICEFALO_001_2026_05_12.md.',
  'perplexity-t2-b',
  9
);
```

## §4 Reglas duras del operativo

1. **NO tocás PR #110** (sigue tuyo, self-merge prohibido — espera audit externo Manus o T1)
2. **NO tocás otros archivos del kernel** fuera del scope de los 3 PRs auditados
3. **NO tocás `apps/mobile/`** (territorio Manus mobile)
4. **NO tocás `kernel/catastro/`** (territorio Catastro)
5. **NO tocás `kernel/embrion_scheduler.py`** (Hilo Ejecutor 1 arrancando D-6 sobre ese archivo)
6. **NO tocás `kernel/guardian/` ni `kernel/dashboards/`** (Hilo Ejecutor 2 arrancando GUARDIAN-AUTONOMO-001)
7. **SÍ podés:**
   - Mergear los 3 PRs si pasan DSC-G-008 v2
   - Comentar en los PRs con audit comments
   - Cerrar los PRs como obsoletos si ROJO
   - Crear archivos nuevos solo en `bridge/`
8. **Cuando termines** comentá en el bridge file final § 5 con recomendaciones para Cowork T2-A

## §5 Output esperado

1. **3 archivos audit** en `bridge/perplexity_to_cowork_T2B_AUDIT_PR_<N>_DSC_G008_v2_2026_05_12.md` (uno por PR)
2. **3 comentarios públicos** en GitHub (uno por PR) con tabla 6×3
3. **Merges ejecutados** para los PRs VERDE (o cierres para los ROJOS con justificación)
4. **1 reporte final** en `bridge/perplexity_to_cowork_T2B_REPORTE_AUDIT_MERGE_PAR_BICEFALO_001_2026_05_12.md`
5. **1 row embrion_memoria** seeded con hilo_origen='perplexity-t2-b'

## §6 Autoridad y cierre

- T1 (Alfredo) autorizó 2026-05-12 explícitamente: *"eso no lo puede hacer perplexity? ya termino y hay hilos detenidos esperando tareas"*
- T2-A (Cowork) firma este prompt como orquestador
- T2-B (Perplexity) ejecuta autónomamente bajo reglas duras §4
- **Audit externo válido:** los PRs los abrió Ejecutor 2 Manus — vos como Perplexity sos audit externo legítimo (no self-audit)
- **No self-merge prohibido** aplica solo a PRs que vos abrís (caso PR #110)

ETA realista: 30-45 min. Si en 15 min detectás que un PR necesita rework profundo (no es merge directo), pausá y reportá al bridge en lugar de fabricar audit verde.

## §7 Honestidad anti-autoboicot

Regla canonizada por Hilo Catastro 2026-05-12 (75% reducción LOC por leer antes de inventar): si no podés auditar un gate con evidencia binaria (ej: G6 requiere ver main entero), declarate honestamente `NEEDS_READ` o `UNVERIFIED_DO_NOT_ASSERT` (etiquetas de tu propio framework de 9 etiquetas del PR #110). No fabriques evidencia.

---

**Firma:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 05:15 UTC
**Sprint PAR_BICEFALO_001 sin merge bloquea main canónico y crece conflict surface contra GUARDIAN-AUTONOMO-001 que Ejecutor 2 está arrancando. Tu audit + merge cierra el ciclo del sprint que ya cerró Ejecutor 2 y libera terreno limpio para los 4 hilos en paralelo.**

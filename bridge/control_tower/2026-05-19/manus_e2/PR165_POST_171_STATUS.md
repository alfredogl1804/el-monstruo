# PR #165 — STATUS POST-MERGE #171

> **Tipo:** Diagnóstico técnico binario.
> **Estado:** DRAFT analítico Manus E2. **NO mergea. NO rebase ejecutado. NO force-push. NO PR nuevo.**
> **Autorización T1:** verbatim "MANUS E2 — P0 PR #165 POST-#171" 2026-05-19.
> **Decisión T1:** verbatim "opcion 4" 2026-05-19 — Camino 4 COWORK_TOMA_PR_165.
> **Reglas duras respetadas:** no toca #153/#164/#170/#173, no migrations, no main, no merge.

---

## §1 Metadata PR #165

| Campo | Valor |
|-------|-------|
| **Número** | 165 |
| **Título** | `chore(ci): consolidar fixes 155 + 158 desbloqueo deadlock CI` |
| **Estado** | OPEN, **isDraft = true** |
| **mergeable** | MERGEABLE |
| **mergeStateStatus** | UNSTABLE |
| **Autor** | alfredogl1804 |
| **Branch HEAD** | `chore/h15-h17-consolidated-ci-unblock` |
| **Branch base** | `main` |
| **baseRefOid (base declarada)** | `7b3b7b5838524a80bf04b63ad5254c4451aaed05` |
| **headRefOid (HEAD)** | `d33351a3e6d98d0c70d151fa0c1da9a563e2a652` |
| **Cambios** | 3 files, 15 add / 4 del |
| **Creado** | 2026-05-18T09:32:44Z |
| **Última actualización** | 2026-05-18T11:59:32Z |

---

## §2 Comparación contra main actual

| Campo | Valor |
|-------|-------|
| **main actual (origin/main)** | `e30d54f7319014de70ca6413553494b93d19ca0e` |
| **Commits de drift entre base PR y main** | **25** |
| **¿PR basado en main actual?** | **NO** — base es `7b3b7b5`, main es `e30d54f`. PR está 25 commits atrás. |

### Commits que faltan en el PR (cronológico inverso, los 25)

```
e30d54f spec(doctrina): directiva v2.0 RE-FUNDADO post-Opus 4.7
795a805 spec(dory-cure): canonización B1-B12 evidence pack
10e800d control-tower(t1): FIRMA MAGNA T1 sobre v1.1.1
0d813c1 control-tower(gpt55pro): convergencia v1.1.1 VALIDA_FASE_0
6088a88 control-tower(opus47): sanity check anti-F16-lite v1.1.1
32edc92 control-tower(gemini): convergencia v1.1.1
3a834b1 control-tower(grok): pase 3 adversarial v1.1.1
57634af chore(cowork-dashboard): auto-regen 2026-05-19T08:58Z
2af5fe5 spec(dory-cure): v1.1.1 DELTA opción A T1 firmada
637eb06 control-tower(gpt55pro): convergencia Sabio #1 v1.1 RESHAPED
ef56875 control-tower(gemini): convergencia Sabio #3 v1.1 RESHAPED
08dd63d control-tower(grok): convergencia Sabio #4 v1.1 RESHAPED
bb110eb control-tower(grok): SURVIVES_RED_TEAM v1.1 RESHAPED
95a4111 feat(doctrine): DORY-CURE v1.1 RESHAPED
efbe6a3 bridge: Cowork T2-A DORY-CURE v1.0 DRAFT fusión
b3e211c bridge: Cowork T2-A MANUS-ANTI-DORY-003 v0.2 DRAFT
cc91046 bridge: T1 authorized merge PR #171 H18 EXECUTION_REPORT
1414a07 fix(ci): H18 skip test_commit_loop sin GITHUB_TOKEN (#171)
2ea846c chore(cowork-dashboard): auto-regen 2026-05-19T02:13Z
21aa8d3 chore(cowork-dashboard): auto-regen 2026-05-18T19:24Z
fcd5c7a chore(cowork-dashboard): auto-regen 2026-05-18T14:53Z
bed77d9 docs(bridge): D6-CREDITS-RESTORE-001 kickoff PR #170
827b1f8 feat(spec): Sprint D6-CREDITS-RESTORE-001
03df5d9 docs(bridge): D5-TUTOR-CLASSIFIER-ROBUSTNESS cierre verde
522eaa8 feat(la-forja/d5): tutor classifier robustness (#169)
```

### Diff del PR (tres archivos quirúrgicos)

```text
M  pyproject.toml             +4   (agrega `pythonpath = ["."]` — fix H15 #145)
M  requirements-eval.txt      -4 +4 (mueve sqlglot, deja nota histórica)
M  requirements.txt           +7   (agrega sqlglot==30.7.0 — fix H17 #156)
```

**Conclusión binaria §2:** PR es chirúrgicamente quirúrgico. Su `d33351a` Merge interno trajo main del 2026-05-18T11:59. Main avanzó 25 commits desde entonces, incluyendo merge #171 (`1414a07`).

---

## §3 Checks rojos — clasificación binaria

### §3.1 Tabla maestra

| Check | Conclusión PR #165 | Tipo | Evidencia verbatim |
|-------|--------------------|------|-------------------|
| **Unit Tests** | FAIL | **fixed_by_rebase** parcial — ver §3.5 | `tests/test_commit_loop.py::test_commit_loop FAILED — SystemExit: 1 — GITHUB_TOKEN not set` |
| **Lint & Type Check** | FAIL | **preexisting drift** — peor en main | Ruff W291/W293/F401/N801/N818 en `tools/wide_research.py`, `transversal/*.py` |
| **license-check** | FAIL | **preexisting drift externo** | `pip-licenses: error: argument -f/--format: invalid choice: 'table'` |
| **semgrep** | FAIL | **preexisting drift** | 26 findings (26 blocking) sobre 2609 archivos |

### §3.2 Unit Tests — diagnóstico binario

**Fallo PR #165 (run 26032117994):**
```
tests/test_commit_loop.py:69: in test_commit_loop
    REPO = await detect_repo()
tests/test_commit_loop.py:44: in detect_repo
    sys.exit(1)
E   SystemExit: 1
ERROR: GITHUB_TOKEN not set
============ 1 failed, 503 passed, 3 skipped, 8 warnings in 11.26s =============
```

**Mismo test en main actual (post-#171 — run 26087754692, 2026-05-19T09:12):** `test_commit_loop` está skip vía fix `1414a07`. PERO el Unit Tests en main reciente falla por **OTRO motivo**:
```
ERROR tests/anti_dory/test_manus_bridge_integration.py
========================= 1 warning, 1 error in 0.58s ==========================
```

Esto es un **collection error** (importerror o syntax error), no assertion failure. Apareció en commits posteriores a #171 (probablemente `bb110eb` o `2af5fe5` que tocaron tests de anti_dory).

### §3.3 Lint & Type Check — diagnóstico binario

**Archivos sucios reportados por Ruff en PR #165** (todos preexistentes al PR):

| Archivo | Errores |
|---------|---------|
| `tools/wide_research.py` | W293 blank-line-whitespace x12, W291 trailing-whitespace x3 |
| `transversal/analytics_layer.py` | I001, F401 datetime/timezone, N801/N818, W293 |
| `transversal/financial_layer.py` | F401 unused field/Optional |
| `transversal/scalability_layer.py` | I001, N801/N818, W293 |
| `transversal/security_layer.py` | I001, F401 logging, N801/N818, F541, W293 |

**Ningún archivo del lint sucio está en el diff del PR.**

**Comparación binaria con main actual (run 26087754692):** mismo Lint en main falla con **MÁS** archivos sucios — al menos 20 visibles incluyendo `tools/_check_cowork_verbatim_citations.py`, `tools/agents_radar.py`, `tools/audit_app_flutter.py`, `tools/code_exec.py`, `tools/cowork_calibration_report.py`, `tools/deploy_*.py`, `tools/manus_bridge.py`, `tools/memento_preflight.py`, `tools/sandbox_manager.py`, `tools/sovereign_browser.py`, etc.

**Drift de lint en main es MAYOR que en PR.** PR #165 no introdujo lint sucio; lo heredó.

### §3.4 license-check — diagnóstico binario

Workflow YAML (`.github/workflows/license-audit.yml`) llama:
```bash
pip-licenses --format=table --with-urls > license-report.txt
```

`pip-licenses==5.5.5` (instalado en runner como dep transitiva fresca) **rechaza `table`** como valor para `--format`. Error verbatim:
```
pip-licenses: error: argument -f/--format: invalid choice: 'table'
(choose from 'plain', 'p', 'plain-vertical', 'markdown', 'md', 'm',
'rst', 'rest', 'r', 'confluence', 'c', 'html', 'h', 'json', 'j',
'json-license-finder', 'jlf', 'csv')
```

**No es código del PR.** Es drift externo de dependencia transitiva CI (versión de pip-licenses cambió en pypi). Fix trivial: cambiar `--format=table` a `--format=markdown`.

### §3.5 semgrep — diagnóstico binario

**Resultado verbatim:**
```
✅ Scan completed successfully.
 • Findings: 26 (26 blocking)
 • Rules run: 189
 • Targets scanned: 2609
```

PR cambia 3 archivos:
- `pyproject.toml`: solo agrega `pythonpath = ["."]` — **no es código semgrep-scannable**.
- `requirements.txt` / `requirements-eval.txt`: solo mueve `sqlglot==30.7.0` — **no es código semgrep-scannable**.

**Las 26 findings son sobre código preexistente** (2609 archivos escaneados, principalmente python/ts/yaml/dockerfile). PR #165 no introduce findings nuevas.

---

## §4 Plan de rebase — propuesta binaria, NO ejecutada

### §4.1 Plan exacto (si T1 autoriza)

```bash
git fetch origin
git checkout chore/h15-h17-consolidated-ci-unblock
git pull origin chore/h15-h17-consolidated-ci-unblock
git rebase origin/main
# resolver conflictos esperados (ver §4.3)
pre-commit run --all-files
pytest tests/test_commit_loop.py -v   # debe quedar skip post-#171
git push --force-with-lease origin chore/h15-h17-consolidated-ci-unblock
gh pr checks 165
```

### §4.2 Riesgo conflictos

| Riesgo | Probabilidad |
|--------|--------------|
| Conflicto `requirements.txt` | **ALTA** (~70%, main tocó deps en sprints D5/D6/dory-cure) |
| Conflicto `pyproject.toml` | MEDIA |
| Conflicto `requirements-eval.txt` | MEDIA |
| Pérdida de history (force-push) | BAJA con `--force-with-lease` |
| Otros checks rojos NO se arreglan con rebase | **CONFIRMADA** |

### §4.3 Zona crítica

- `requirements.txt` línea 136-145 (bloque "Sprint 86.4.5 explicit").
- `requirements-eval.txt` línea 14-17 (bloque "Schema Drift Detection").

---

## §5 Riesgos del plan

| # | Riesgo | Severidad |
|---|--------|-----------|
| R1 | Rebase trae lint sucio MAYOR de main, PR no podrá pasar Lint check post-rebase | ALTA |
| R2 | License-check seguirá rojo post-rebase (drift workflow YAML) | ALTA |
| R3 | Semgrep seguirá rojo post-rebase (26 findings preexisting) | ALTA |
| R4 | Unit Tests post-rebase fallará en `test_manus_bridge_integration.py` (drift nuevo en main) | ALTA |
| R5 | Force-push en branch compartida puede pisar trabajo de otro Cowork | MEDIA (mitigable con `--force-with-lease`) |

---

## §6 Decisión T1 — Camino elegido binariamente

T1 verbatim: **"opcion 4"** 2026-05-19.

**Camino 4 — COWORK_TOMA_PR_165.** Reasignar PR #165 a Cowork T2-A. Cowork hace rebase + arregla cascada CI completa (los 4 rojos) + force-push autorizado. T1 mergea cuando los 4 checks queden verdes.

Patrón ya validado: con #171 mismo Cowork ya ejecutó este flujo binariamente.

---

## §7 Bloqueo Manus E2 — fin de scope

| Acción | Status |
|--------|--------|
| Mergear #165 | ❌ No autorizado, no ejecutado |
| Tocar #153/#164/#170/#173 | ❌ No autorizado, no ejecutado |
| Migrations | ❌ No ejecutadas |
| Abrir nuevos PRs | ❌ No autorizado, no ejecutado |
| Modificar main | ❌ No tocado |
| Force-push #165 | ❌ No autorizado, no ejecutado |
| Pedir merge | ❌ No solicitado |

**Mi siguiente acción autorizada:** entregar este reporte + prompt Cowork T2-A en rama lateral. Stop.

---

## §8 Anexo — Prompt entregable Cowork T2-A

Ver archivo hermano `PROMPT_COWORK_T2A_PR165_HANDOFF.md` en mismo directorio.

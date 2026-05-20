# PROMPT — COWORK T2-A — PR #165 HANDOFF (Camino 4)

> **Origen:** Manus E2 diagnóstico binario `bridge/control_tower/2026-05-19/manus_e2/PR165_POST_171_STATUS.md`.
> **Decisión T1 verbatim:** "opcion 4" 2026-05-19.
> **Patrón:** mismo flujo que con PR #171 (Cowork rebase + force-push autorizado por T1).

---

## §1 Contexto binario

PR #165 es un fix CI quirúrgico (3 archivos, 15 add / 4 del):
- `pyproject.toml`: agrega `pythonpath = ["."]` — fix H15 issue #145.
- `requirements.txt`: agrega `sqlglot==30.7.0` — fix H17 issue #156.
- `requirements-eval.txt`: mueve `sqlglot` con nota histórica.

**Estado actual del PR:**
- Base PR: `7b3b7b5838524a80bf04b63ad5254c4451aaed05`.
- HEAD PR: `d33351a3e6d98d0c70d151fa0c1da9a563e2a652`.
- Main actual: `e30d54f7319014de70ca6413553494b93d19ca0e`.
- Drift: **25 commits atrás**, incluyendo merge #171 (`1414a07`).
- 4 checks rojos (clasificación binaria detallada en `PR165_POST_171_STATUS.md`).

---

## §2 Scope binario Cowork T2-A

### §2.1 IN-SCOPE

| # | Tarea | Tipo |
|---|-------|------|
| T1 | Rebase del PR #165 contra `origin/main` (`e30d54f`) | rebase |
| T2 | Resolver conflictos esperados en `requirements.txt`, `pyproject.toml`, `requirements-eval.txt` | conflict resolution |
| T3 | Arreglar `pip-licenses --format=table` → `--format=markdown` en `.github/workflows/license-audit.yml` | workflow fix |
| T4 | Auto-fix lint con `ruff format` + `ruff check --fix` sobre `tools/*.py` y `transversal/*.py` | lint cleanup |
| T5 | Diagnosticar collection error en `tests/anti_dory/test_manus_bridge_integration.py` y aplicar fix | test fix |
| T6 | Reducir o triagear los 26 findings de semgrep (decidir cuáles son reales vs ignorables) | semgrep triage |
| T7 | Force-push con `--force-with-lease` (autorización T1 ya granted vía Camino 4) | force-push |
| T8 | Reportar a T1 cuando los 4 checks queden verdes para autorizar merge | report |

### §2.2 OUT-OF-SCOPE BINARIO

| # | NO toques | Razón |
|---|-----------|-------|
| 1 | PRs #153, #164, #170, #173 | Directiva T1 verbatim |
| 2 | Migrations | Directiva T1 verbatim |
| 3 | Main directo | Directiva T1 verbatim |
| 4 | Mergear #165 sin que T1 confirme verdes | Espera autorización T1 explícita post-rebase |

---

## §3 Plan de ejecución binario

### Paso 1 — Sandbox local

```bash
cd <ruta-Cowork-T2-A>
git fetch origin --prune
git checkout chore/h15-h17-consolidated-ci-unblock
git pull origin chore/h15-h17-consolidated-ci-unblock
```

### Paso 2 — Rebase

```bash
git rebase origin/main
# Resolver conflictos manuales, validar:
git rebase --continue
```

Conflictos esperados (probabilidad ≥70%):
- `requirements.txt` línea ~136-145 (bloque Sprint 86.4.5 explicit, donde se agrega sqlglot).
- `requirements-eval.txt` línea ~14-17 (bloque Schema Drift Detection).
- `pyproject.toml` posible si main añadió tools/sections.

**Regla binaria de resolución:** mantener fix H15 (`pythonpath = ["."]`) y fix H17 (`sqlglot==30.7.0`) en su forma final. NO duplicar entradas. NO eliminar entradas que main agregó.

### Paso 3 — Fix license-check workflow

Editar `.github/workflows/license-audit.yml`:

```diff
- pip-licenses --format=table --with-urls > license-report.txt
+ pip-licenses --format=markdown --with-urls > license-report.txt
```

(O alternativamente `--format=plain` si los consumidores downstream prefieren plain text.)

### Paso 4 — Lint cleanup

```bash
ruff format tools/ transversal/
ruff check --fix tools/ transversal/
git add tools/ transversal/
git commit -m "chore(lint): auto-fix ruff drift en tools/ y transversal/ (Cowork T2-A handoff PR #165)"
```

**Validación binaria:** `ruff check tools/ transversal/` debe retornar 0 errores.

### Paso 5 — Fix collection error test_manus_bridge_integration.py

```bash
python -c "import tests.anti_dory.test_manus_bridge_integration" 2>&1 | head -30
pytest tests/anti_dory/test_manus_bridge_integration.py --collect-only 2>&1 | head -30
```

Diagnosticar `ERROR tests/anti_dory/test_manus_bridge_integration.py` (collection error). Probables causas:
- Import faltante (módulo agregado en commit reciente sin estar en requirements.txt).
- Syntax error.
- Fixture conflict.

Fix in-place. Si requiere migración cross-archivo, reportar a T1 antes de aplicar.

### Paso 6 — Triage semgrep 26 findings

```bash
semgrep --config auto --config p/python --config p/security-audit --config p/owasp-top-ten \
  --severity ERROR --json . > semgrep-local.json
jq '.results | length' semgrep-local.json
jq '.results[] | {check_id, path, severity}' semgrep-local.json | head -50
```

**Decisión binaria por finding:**
- Si finding es **real y simple**: aplicar fix.
- Si finding es **falso positivo** o **acceptable risk**: agregar a `.semgrepignore` con comentario justificación.
- Si finding requiere **rediseño**: reportar a T1, NO aplicar fix unilateral.

### Paso 7 — Validación local

```bash
pre-commit run --all-files
pytest tests/test_commit_loop.py tests/anti_dory/test_manus_bridge_integration.py -v
ruff check tools/ transversal/
semgrep --config auto --severity ERROR . | grep "Findings:"
```

Los 4 controles deben pasar localmente antes del force-push.

### Paso 8 — Force-push

```bash
git push --force-with-lease origin chore/h15-h17-consolidated-ci-unblock
gh pr checks 165 --watch
```

### Paso 9 — Reportar a T1

Cuando los 4 checks queden verdes en GitHub:

```bash
# Crear archivo de reporte
echo "PR #165 — 4 checks verdes confirmados $(date -u +%Y-%m-%dT%H:%M:%SZ)" > \
  bridge/control_tower/2026-05-19/cowork_t2a/PR165_GREEN_REPORT.md
```

T1 revisa y autoriza merge manual desde GitHub UI.

---

## §4 Reglas duras heredadas

| # | Regla | Status durante ejecución Cowork |
|---|-------|--------------------------------|
| 1 | NO mergear #165 sin T1 explicit | ✅ Esperar reporte verdes + T1 OK |
| 2 | NO tocar #153/#164/#170/#173 | ✅ Solo branch chore/h15-h17-consolidated-ci-unblock |
| 3 | NO migrations | ✅ Workflow fix + lint + tests, no DB |
| 4 | NO modificar main | ✅ Cambios solo en branch del PR |
| 5 | Force-push autorizado por Camino 4 T1 | ✅ Granted, usar `--force-with-lease` |

---

## §5 Anexos verbatim

- Diagnóstico técnico Manus E2: `bridge/control_tower/2026-05-19/manus_e2/PR165_POST_171_STATUS.md` (en este mismo árbol).
- Logs CI fallidos referenciados:
  - Unit Tests run 26032117994 job 76520529613.
  - Lint & Type Check run 26032117994 job 76520529536.
  - license-check run 26032117998 job 76520529441.
  - semgrep run 26032117993 job 76520529557.
- Run de comparación en main reciente: 26087754692 (jobs 76705136302 Unit / 76705136303 Lint).

---

## §6 Cierre binario

Cowork T2-A: misión = entregar PR #165 con 4 checks verdes a T1 para merge manual.

Manus E2 NO acompaña la ejecución (out-of-scope post-handoff). Si Cowork necesita análisis adicional, T1 puede convocar a Manus E2 con nueva directiva binaria.

# Sprint S-001 — Security Hardening (post-incidente P0 credenciales)

**Estado:** Propuesto
**Hilo:** Ejecutor (Manus)
**ETA (recalibrado):** 60-90 min reales con velocity demostrada
**Objetivo Maestro:** #11 (Seguridad adversarial) + #14 (Guardian de los Objetivos) + #4 (No equivocarse dos veces)
**Bloqueos:** Rotaciones P0 verde (DB password + service_role JWT) + cleanup repos GitHub Pages
**Resultado esperado:** Pre-commit hooks operando + scripts refactorizados + memory tables limpios + test anti-secret en CI + AGENTS.md actualizado

---

## 0. Procedencia — Por qué este sprint existe

Sprint S-001 es la respuesta estructural al **incidente P0 del 2026-05-06** (ver `discovery_forense/INCIDENTES/P0_2026_05_06_credenciales_repo_publico.md`).

El incidente P0 mitigó lo agudo (rotación de secrets expuestos). Este sprint mitiga lo crónico: instala las defensas que habrían prevenido el incidente y previene la próxima clase de fallo similar.

**5 DSCs nuevos firmados (S-001 a S-005)** prescriben las acciones. Sprint S-001 implementa esas acciones.

---

## 1. Audit pre-sprint — Estado actual

### Lo que ya existe (pre-sprint)

- 6+ scripts de auditoría de credenciales en `scripts/` (paradójicamente algunos fueron parte del breach):
  - `_check_no_tokens.sh`
  - `audit_credenciales_pre_rotacion.sh`
  - `audit_railway_and_code.sh`
  - `audit_supabase_tokens.py` ← era él mismo vulnerable, refactorizado en P0
  - `inventario_credenciales_ecosistema.sh`
  - `rotacion_tokens_plan_a.sh`

- Política de credenciales redactada por Cowork 2026-05-04 pero NO firmada como DSC hasta 2026-05-06 (post-incidente).

- Memory tables Supabase (`thoughts`, `episodic`, `semantic`, `magna_cache`, `error_memory`) sin audit retroactivo de leakage.

### Lo que NO existe (gaps)

- Pre-commit hooks (gitleaks + trufflehog) NO instalados.
- CI/CD test que rechace PRs con strings que matchean patrones de secret.
- Documentación de política de credenciales en AGENTS.md (estaba en chat de Cowork, no canonizada).
- Audit de memory tables — query SQL recomendada el 2026-05-04 nunca se ejecutó.
- Refactor de scripts: muchos siguen usando `os.environ.get(VAR, "default_secret")` (anti-patrón DSC-S-004).

### Velocity demostrada

- Manus cierra sprints en 15 min cuando son tareas chicas + bien acotadas.
- Las 5 tareas de este sprint son atómicas. Total con velocity demostrada: 60-90 min.

---

## 2. Tareas del Sprint

### Tarea S-1.1 — Pre-commit hooks (gitleaks + trufflehog)

**Descripción:** Instalar pre-commit framework + hooks gitleaks (pre-commit) y trufflehog (pre-push) en el repo principal `el-monstruo`.

**Solución:**

`.pre-commit-config.yaml` en raíz del repo:

```yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
        name: gitleaks-staged
        entry: gitleaks detect --staged --redact --verbose
        language: system

  - repo: local
    hooks:
      - id: trufflehog
        name: trufflehog-prepush
        entry: trufflehog git file://. --since-commit HEAD~5 --no-update --fail
        language: system
        stages: [push]
```

`.gitleaks.toml` en raíz con allowlist mínima:

```toml
[allowlist]
description = "Allowlist for known false positives"
paths = [
  '''docs/biblias_agentes_2026/.*\.md''',  # ejemplos de tokens en biblias son referencias, no secrets reales
  '''\.env\.example''',                     # placeholders documentados
]
```

**Tests:**
- Test 1: `git commit -m "test"` con un archivo conteniendo `postgresql://postgres:fake_password@host/db` → DEBE fallar
- Test 2: `git commit -m "test"` con código limpio → DEBE pasar
- Test 3: `git push` con commit conteniendo `eyJhbGciOiJIUzI1NiIs...` (JWT mock) → DEBE fallar
- Test 4: `--no-verify` bypass funciona pero requiere justificación en commit message (no enforceable a este nivel, queda como convención documentada)

**Aceptación:** instalación verificada con `pre-commit run --all-files` ejecutándose sin error en main actual.

---

### Tarea S-1.2 — Refactor scripts (env vars sin defaults sensibles)

**Descripción:** Auditar TODOS los scripts en `scripts/`, `kernel/`, `tools/`, `skills/` y refactorizar:
1. Reemplazar `os.environ.get("VAR", "real_secret")` por `os.environ["VAR"]` o `os.environ.get("VAR")` con explicit raise
2. Reemplazar hardcoded DSN/JWT/API keys por env var lookups
3. Validar al startup que las env vars críticas están definidas

**Implementación:**

```python
# kernel/security/env_validator.py (nuevo)
"""Valida que env vars críticas están definidas al startup."""

REQUIRED_ENV_VARS = {
    "SUPABASE_DB_URL": "Conexión Postgres a Supabase",
    "SUPABASE_SERVICE_KEY": "JWT service_role para API directa",
    "SUPABASE_URL": "URL pública del proyecto",
    "OPENAI_API_KEY": "GPT family",
    "ANTHROPIC_API_KEY": "Claude family",
    # ... (lista canónica de env vars críticas)
}

def validate_env_at_startup() -> None:
    missing = [name for name in REQUIRED_ENV_VARS if not os.environ.get(name)]
    if missing:
        raise RuntimeError(
            f"Missing required env vars: {missing}. "
            f"Set them in Railway/your local .env before starting kernel."
        )
```

Llamar `validate_env_at_startup()` en `kernel/main.py` antes de cualquier inicialización.

**Scripts a refactorizar (lista pre-audit):**

| Script | Cambio | Status |
|---|---|---|
| `scripts/run_migration_013.py` | DSN hardcoded → `os.environ["SUPABASE_DB_URL"]` | Pendiente post-P0 |
| `scripts/run_migration_014.py` | DSN hardcoded → env var | Pendiente post-P0 |
| `scripts/run_migration_015.py` | Verificar | Pendiente |
| `scripts/run_migrations_012_013.py` | Verificar | Pendiente |
| `scripts/run_fix_trigger.py` | DSN → env var | Pendiente |
| `scripts/audit_supabase_tokens.py` | Refactorizado en P0 | ✅ |
| `scripts/register_sovereign_browser_tool.py` | DSN → env var | Pendiente |
| Otros encontrados en audit | TBD | Pendiente |

**Aceptación:** `grep -rn "postgresql://\|eyJhbGc\|ghp_\|sk-" scripts/ kernel/ tools/ skills/ --exclude-dir=.git` no devuelve matches con secrets reales (solo placeholders en docs).

---

### Tarea S-1.3 — Audit + cleanup de memory tables

**Descripción:** Ejecutar el audit que Cowork recomendó el 2026-05-04 contra las memory tables de Supabase. Buscar leakage de secrets en `thoughts`, `episodic`, `semantic`, `magna_cache`, `error_memory` que el Embrión o agentes externos puedan haber persistido.

**Solución:**

```sql
-- scripts/audit_memory_tables_for_secrets.sql
-- Ejecutar contra Supabase prod post-rotación

-- Patrones a buscar (combinados):
-- - DSN postgresql/postgres
-- - JWT (eyJ...)
-- - API keys conocidos (ghp_, sk-, sbp_, github_pat_)
-- - El password viejo de Supabase (rotado, pero pudo quedar en memoria)

WITH suspicious_patterns AS (
  SELECT 'postgresql://[^[:space:]]+' AS pattern, 'DSN_postgres' AS category
  UNION ALL SELECT 'eyJ[a-zA-Z0-9_-]{30,}', 'JWT_supabase'
  UNION ALL SELECT 'ghp_[a-zA-Z0-9]{36}', 'GitHub_PAT'
  UNION ALL SELECT 'github_pat_[a-zA-Z0-9_]{40,}', 'GitHub_FineGrained_PAT'
  UNION ALL SELECT 'sbp_[a-zA-Z0-9]{40}', 'Supabase_Access_Token'
  UNION ALL SELECT 'sk-[a-zA-Z0-9]{20,}', 'OpenAI_Anthropic_API'
)
SELECT
  'thoughts' AS table_name,
  id,
  created_at,
  category,
  LENGTH(content) AS content_size
FROM thoughts t
CROSS JOIN suspicious_patterns p
WHERE t.content ~* p.pattern
UNION ALL
SELECT 'episodic', id, created_at, category, LENGTH(content)
FROM episodic e
CROSS JOIN suspicious_patterns p
WHERE e.content ~* p.pattern
UNION ALL
SELECT 'semantic', id, created_at, category, LENGTH(content)
FROM semantic s
CROSS JOIN suspicious_patterns p
WHERE s.content ~* p.pattern;
```

**Acción si encuentra rows:**

1. **Snapshot forense** (sin pegar el secret en chat):
   ```sql
   SELECT id, created_at, category, LEFT(content, 100) AS preview
   FROM <table> WHERE id IN (<lista>);
   ```

2. **Sanitizar (reemplazar el secret con placeholder):**
   ```sql
   UPDATE <table>
   SET content = REGEXP_REPLACE(content, '<pattern>', '[REDACTED-2026-05-06]')
   WHERE id IN (<lista>);
   ```

3. **Verificar:** re-ejecutar audit query, esperar 0 rows.

**Aceptación:** audit query post-cleanup devuelve 0 rows.

---

### Tarea S-1.4 — Test automatizado anti-secret en CI

**Descripción:** GitHub Actions workflow que falla si algún archivo en main contiene patrones de secret (defensa en profundidad complementaria a pre-commit hooks).

**Solución:**

`.github/workflows/secret-scan.yml`:

```yaml
name: Secret Scan
on:
  push:
    branches: [main]
  pull_request:

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # full history para audit completo

      - name: Run gitleaks
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Run trufflehog
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: main
          head: HEAD
          extra_args: --only-verified
```

**Aceptación:**
- PR con secret introducido a propósito (test) → workflow falla, PR bloqueado
- PR limpio → workflow pasa

---

### Tarea S-1.5 — Documentar política en AGENTS.md

**Descripción:** Agregar sección "## Política de Credenciales" a `AGENTS.md` con la canonización de DSC-S-001 a S-005.

**Contenido a agregar:**

```markdown
## Política de Credenciales (DSC-S-001 a S-005)

### Reglas inmutables

1. CERO credenciales en plaintext en código, git history, bridge files,
   Notion, memory tables, logs, ni skills references.
2. Bóveda primaria: 1Password / Bitwarden / Apple Keychain.
3. Mac local: `gh auth login` web flow (no PAT manual en archivos).
4. Servicios remotos (Railway, Vercel): env vars con scope mínimo.
5. Scripts: `os.environ["VAR"]` (fail loud). PROHIBIDO `os.environ.get("VAR", "real_secret")`.

### Anti-patrón prohibido (DSC-S-004)

```python
# ❌ PROHIBIDO — el secret está en código aunque parezca env var:
SUPABASE_KEY = os.environ.get("SUPA_KEY", "eyJhbGciOiJIUzI1NiIs...")

# ✅ REQUERIDO — fail loud si falta:
SUPABASE_KEY = os.environ["SUPA_KEY"]
```

### Pre-commit obligatorio (DSC-S-002)

- gitleaks staged
- trufflehog pre-push
- Bypass solo con --no-verify + justificación documentada

### Cierre de sprint requiere audit (DSC-S-001 punto 5)

Sprints que tocan `scripts/`, `kernel/`, `tools/`, `skills/` deben ejecutar
`bash scripts/_check_no_tokens.sh` ANTES de declarar verde. Cowork audita
contenido de scripts nuevos antes de firmar verde, no solo lee el reporte
de Manus.

### Cleanup de namespace (DSC-S-005)

Default a archive antes que delete. Delete solo después de archive +
30 días + scope ampliado explícitamente.

### Rotación

| Tipo | TTL máximo | Rotación al detectar exposure |
|---|---|---|
| GitHub PAT | 12 meses | Inmediata |
| DB password | n/a | Inmediata |
| Service role JWT | reducir validez si posible | Inmediata |
| API keys (OpenAI, Anthropic, etc.) | 6 meses | Inmediata |
```

**Aceptación:** sección agregada + referencia cruzada a postmortem `discovery_forense/INCIDENTES/P0_2026_05_06_credenciales_repo_publico.md`.

---

## 3. Aceptación de cierre Sprint S-001

**Definición de Listo (las 5 tareas verde simultáneo):**

1. ✅ Pre-commit hooks instalados + tests pasando (S-1.1)
2. ✅ Scripts refactorizados, grep no devuelve secrets reales (S-1.2)
3. ✅ Memory tables auditadas + sanitizadas si necesario (S-1.3)
4. ✅ GitHub Actions workflow operando (S-1.4)
5. ✅ AGENTS.md actualizado con política canónica (S-1.5)

**Validación de Cowork (mandatoria — auto-cumplimiento de DSC-S-001):**

- Cowork audita contenido del refactor de scripts ANTES de firmar verde (no solo el reporte de Manus).
- Cowork verifica que la query de audit de memory tables se ejecutó realmente y que devuelve 0 matches post-cleanup.

**Reporte al bridge:** `bridge/manus_to_cowork_REPORTE_SPRINT_S001_<fecha>.md` con:

- Tabla de evidencia (5 filas, una por tarea)
- Output de `pre-commit run --all-files`
- Output del grep post-refactor
- Count de rows sanitizadas en memory tables
- Link al workflow de GitHub Actions
- Diff de AGENTS.md

---

## 4. Frase de cierre canónica

🏛️ **SECURITY HARDENING — DECLARADO**

Si Cowork firma verde post-validación de los 5 deliverables, Sprint S-001 cierra y el ecosistema queda con defensa en profundidad contra el patrón de fallo del incidente P0.

---

## 5. Notas técnicas

1. **Pre-commit framework:** instalar con `pip install pre-commit` + `pre-commit install`. Ejecutar `pre-commit autoupdate` periódicamente.

2. **Allowlist de gitleaks:** mantener mínima. Cualquier nueva entry requiere justificación en commit message + revisión de Cowork.

3. **Audit de memory tables periódico:** post-Sprint S-001, agendar audit trimestral como cron de Embrión. Si encuentra leakage, alerta a Cowork.

4. **GitHub Actions secret-scan:** correr en TODAS las PRs, no solo main. Si organización tiene minutos limitados, considerar self-hosted runner.

5. **DSC-S-005 (archive vs delete):** aplicar también a tablas Supabase. Antes de DROP, considerar archive table + delete en 30 días.

---

**Cowork (Hilo A), spec preparada 2026-05-06 post-incidente P0**
**Referencias cruzadas:**
- `discovery_forense/INCIDENTES/P0_2026_05_06_credenciales_repo_publico.md` (postmortem)
- DSC-S-001, DSC-S-002, DSC-S-003, DSC-S-004, DSC-S-005 (en `discovery_forense/CAPILLA_DECISIONES/_GLOBAL/`)
- DSC-G-008 (validar codebase ANTES de specs Y antes de cierre — extensión propuesta)

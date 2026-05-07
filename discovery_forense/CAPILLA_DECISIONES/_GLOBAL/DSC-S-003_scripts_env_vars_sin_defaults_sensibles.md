---
id: DSC-S-003
proyecto: GLOBAL
tipo: antipatron
titulo: "Scripts deben usar os.environ[VAR] (fail loud) — PROHIBIDO os.environ.get(VAR, default_secret)."
estado: firme
fecha: 2026-05-06
fuentes:
  - repo:scripts/run_migration_*.py (caso paradigmático)
  - repo:biblia-github-motor/motor/github_radar.py (anti-patrón default value)
  - repo:discovery_forense/INCIDENTES/P0_2026_05_06_credenciales_repo_publico.md
cruza_con: [DSC-S-001, DSC-S-002, DSC-S-004]
---

# Scripts Deben Usar Env Vars Sin Defaults Sensibles

## Decisión

Todo script en `scripts/`, `kernel/`, `tools/`, `skills/`, y módulos de cualquier repo del ecosistema, que requiera credenciales o secrets para conectar a servicios externos (DB, API, Auth, etc.) DEBE leerlos usando `os.environ["VAR"]` (fail loud) o `os.environ.get("VAR")` con explicit raise — NUNCA con default value que contenga el secret real.

## Por qué

El incidente P0 del 2026-05-06 demostró 2 anti-patrones que filtraron credenciales:

1. **DSN hardcoded directo:** `DB_PASS = "0SsKDCchJpN5GhO3"` (en `run_migration_013.py`, `run_migration_014.py`, etc.)
2. **Default value con secret real:** `os.environ.get("SUPA_KEY", "eyJhbGciOiJIUzI1NiIs...")` (en `biblia-github-motor/motor/github_radar.py`)

El patrón #2 es PEOR que #1 porque oculta el secret bajo apariencia de env var, dificultando detección visual durante code review. DSC-S-004 codifica este anti-patrón específicamente. DSC-S-003 codifica la regla general que cubre ambos.

## Reglas

### PROHIBIDO

```python
# Pattern A: hardcoded directo
DB_PASS = "0SsKDCchJpN5GhO3"

# Pattern B: default value con secret real (peor que A)
SUPABASE_KEY = os.environ.get("SUPA_KEY", "eyJhbGciOiJIUzI1NiIs...")

# Pattern C: dict de config con secret
config = {
    "db_password": "0SsKDCchJpN5GhO3",  # ❌
    ...
}

# Pattern D: f-string con secret embebido
DSN = f"postgresql://postgres:0SsKDCchJpN5GhO3@host:5432/db"  # ❌
```

### REQUERIDO

```python
# Pattern correcto 1: fail loud con KeyError
SUPABASE_KEY = os.environ["SUPA_KEY"]

# Pattern correcto 2: get + explicit raise
SUPABASE_KEY = os.environ.get("SUPA_KEY")
if not SUPABASE_KEY:
    raise RuntimeError("SUPA_KEY env var required")

# Pattern correcto 3: helper centralizado (recomendado para kernel)
from kernel.security.env_validator import require_env
SUPABASE_KEY = require_env("SUPA_KEY")
```

### Default values permitidos solo para configuración no-sensible

```python
# ✅ OK — defaults de config no son secrets
TIMEOUT = int(os.environ.get("HTTP_TIMEOUT", "30"))
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
RETRY_COUNT = int(os.environ.get("RETRY_COUNT", "3"))
PORT = int(os.environ.get("PORT", "8000"))
```

## Helper centralizado

Para kernel y módulos críticos, usar helper centralizado en `kernel/security/env_validator.py`:

```python
"""kernel/security/env_validator.py — fail loud env var lookup."""
import os
from typing import NoReturn

REQUIRED_ENV_VARS_DESCRIPTIONS = {
    "SUPABASE_DB_URL": "Conexión Postgres a Supabase",
    "SUPABASE_SERVICE_KEY": "JWT service_role para PostgREST API directa",
    "SUPABASE_URL": "URL pública del proyecto Supabase",
    "OPENAI_API_KEY": "GPT family",
    "ANTHROPIC_API_KEY": "Claude family",
    # ... mantener lista canónica completa
}


def require_env(name: str) -> str:
    """Get env var or raise RuntimeError with helpful message."""
    value = os.environ.get(name)
    if not value:
        description = REQUIRED_ENV_VARS_DESCRIPTIONS.get(name, "(undocumented)")
        raise RuntimeError(
            f"Required env var '{name}' not set. "
            f"Description: {description}. "
            f"Set it in Railway/your local .env before starting."
        )
    return value


def validate_env_at_startup() -> None:
    """Validate all required env vars at startup. Call from main.py."""
    missing = []
    for name in REQUIRED_ENV_VARS_DESCRIPTIONS:
        if not os.environ.get(name):
            missing.append(name)
    if missing:
        raise RuntimeError(
            f"Missing required env vars: {missing}. "
            f"See REQUIRED_ENV_VARS_DESCRIPTIONS for details."
        )
```

## Implicaciones

- **Sprint S-001 refactoriza scripts existentes** para cumplir esta regla.
- **Validación al startup del kernel** llama `validate_env_at_startup()` antes de cualquier inicialización.
- **Pre-commit hooks (DSC-S-002)** deben detectar el anti-patrón de default value con secret real (regex en gitleaks rules custom si necesario).
- **Code review en cierre de sprint (DSC-G-008 v2)** verifica explícitamente que ningún script nuevo use el anti-patrón.

## Estado de validación

firme — fruto del incidente P0 del 2026-05-06. Implementación técnica en Sprint S-001 tarea S-1.2.

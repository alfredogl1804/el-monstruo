---
id: DSC-S-004
proyecto: GLOBAL
tipo: antipatron
titulo: "PROHIBIDO os.environ.get('VAR', 'real_secret_as_fallback') — el secret está en código aunque parezca env var."
estado: firme
fecha: 2026-05-06
fuentes:
  - repo:biblia-github-motor/motor/github_radar.py (línea 32-34, JWT service_role como default value)
  - repo:discovery_forense/INCIDENTES/P0_2026_05_06_credenciales_repo_publico.md
cruza_con: [DSC-S-001, DSC-S-002, DSC-S-003]
---

# Anti-patrón "Default Value con Secret Real"

## Decisión

PROHIBIDO usar `os.environ.get("VAR", "real_secret_as_fallback")` — donde el segundo argumento (default value) contiene un secret real (DSN, JWT, API key, password, token).

Sub-patrón específico de DSC-S-003, codificado por separado por su severidad paradigmática y porque dificulta detección visual durante code review.

## Por qué (severidad paradigmática)

Este patrón es PEOR que hardcoded directo. Razones:

1. **Visualmente engañoso.** Al code review, parece que el script "usa env var" — el revisor superficial asume que la env var está bien configurada en producción y que el default es un placeholder/dev value. No lo es.

2. **Sobrevive a "limpiezas" superficiales.** Cuando alguien hace grep de `password = ` o `DB_PASSWORD = `, este patrón NO matchea. El secret está dentro del segundo argumento de una función call, escondido detrás de la apariencia de configuración correcta.

3. **Funciona aunque la env var falte.** Si la env var no está set, el script sigue funcionando con el secret hardcoded en código. Esto significa que el deploy puede pasar tests + producción sin que nadie note que la env var nunca se aplicó realmente. El sistema queda "funcionando" pero usando el secret de código en lugar del de env, anulando la separación de configuración.

4. **Detonó el segundo leak del incidente P0.** En `biblia-github-motor/motor/github_radar.py:32-34`, el JWT service_role de Supabase con validez 10 años quedó expuesto en repo (privado pero igual exposure). El developer que escribió ese código probablemente pensó "estoy usando env var", pero el JWT entró al repo como default value.

## Casos canónicos

### Anti-patrón

```python
# Caso 1 — visto en biblia-github-motor (incidente P0):
SUPABASE_URL = "https://xsumzuhwmivjgftsneov.supabase.co"
SUPABASE_KEY = os.environ.get("SUPA_KEY", "eyJhbGciOiJIUzI1NiIs...REDACTED...")

# Caso 2 — variante con DSN:
DB_URL = os.environ.get("DB_URL", "postgresql://postgres:OLD_PASSWORD@host/db")

# Caso 3 — variante con dict de config:
config = {
    "stripe_key": os.environ.get("STRIPE_KEY", "sk_live_..."),
    "openai_key": os.environ.get("OPENAI_API_KEY", "sk-..."),
}

# Caso 4 — variante con f-string ternario:
key = os.environ.get("API_KEY") if os.environ.get("API_KEY") else "ghp_..."
```

### Refactor correcto

```python
# Caso 1 fix:
SUPABASE_URL = os.environ["SUPABASE_URL"]  # public URL puede ir en .env.example
SUPABASE_KEY = os.environ["SUPA_KEY"]      # fail loud si no está

# Caso 2 fix:
DB_URL = os.environ["DB_URL"]

# Caso 3 fix (con helper centralizado de DSC-S-003):
from kernel.security.env_validator import require_env
config = {
    "stripe_key": require_env("STRIPE_KEY"),
    "openai_key": require_env("OPENAI_API_KEY"),
}

# Caso 4 fix:
key = os.environ["API_KEY"]  # explicit fail si no está
```

## Detección automática

### Pre-commit hook custom (gitleaks rule)

Agregar a `.gitleaks.toml` regla custom que detecta el patrón:

```toml
[[rules]]
id = "default-value-secret"
description = "os.environ.get with secret-like default value"
regex = '''os\.environ\.get\([^,]+,\s*["'](eyJ|sk-|ghp_|github_pat_|sbp_|pk_live|sk_live|postgresql://|postgres://|mongodb://|mysql://|sb-)[^"']{10,}["']'''
tags = ["secret", "antipattern"]
```

### Grep manual (audit retroactivo)

```bash
# Detectar el anti-patrón en todo el ecosistema:
grep -rn "os\.environ\.get\([^,]*,\s*[\"']" \
  --include="*.py" \
  scripts/ kernel/ tools/ skills/ apps/
```

Cualquier match requiere inspección humana — algunos son legítimos (defaults no-secret), otros son el anti-patrón.

### Code review checklist

Al revisar cualquier PR que toque scripts con env vars, verificar:

- [ ] ¿`os.environ.get()` tiene default value?
- [ ] Si sí, ¿el default es claramente no-secret (timeout, path, flag, "INFO", "30")?
- [ ] Si el default parece secret-shaped, RECHAZAR PR y pedir refactor a `os.environ[]` o explicit raise.

## Implicaciones

- **DSC-S-004 es regla anidada de DSC-S-003** — toda violación de S-004 es también violación de S-003. Codificadas por separado para énfasis pedagógico.
- **Pre-commit hook (DSC-S-002)** debe incluir regla custom de detección.
- **Sprint S-001 refactoriza** todas las ocurrencias detectadas en audit retroactivo.
- **Code review en cierre de sprint (DSC-G-008 v2)** verifica explícitamente este anti-patrón.

## Estado de validación

firme — fruto del incidente P0 del 2026-05-06, segundo leak detectado por Manus en audit ampliado de `biblia-github-motor`.

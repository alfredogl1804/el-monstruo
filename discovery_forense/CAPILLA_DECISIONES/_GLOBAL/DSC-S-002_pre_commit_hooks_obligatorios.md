---
id: DSC-S-002
proyecto: GLOBAL
tipo: politica
titulo: "Pre-commit hooks obligatorios — gitleaks staged + trufflehog pre-push para bloquear secrets antes de pushear."
estado: firme
fecha: 2026-05-06
fuentes:
  - repo:discovery_forense/INCIDENTES/P0_2026_05_06_credenciales_repo_publico.md
  - repo:bridge/sprints_propuestos/sprint_S001_security_hardening.md (Sprint S-001 implementa la infraestructura)
cruza_con: [DSC-G-008, DSC-S-001, DSC-S-003, DSC-S-004]
---

# Pre-commit Hooks Obligatorios

## Decisión

Todo repo del ecosistema El Monstruo (kernel principal + repos cruzados como `biblia-github-motor`, `observatorio-merida-2027`, `honcho-railway`, `like-kukulkan-tickets`, futuros) DEBE tener pre-commit hooks instalados que bloqueen automáticamente commits con secrets en plaintext.

Stack canónico:
- **Pre-commit:** `gitleaks detect --staged --redact --verbose`
- **Pre-push:** `trufflehog git file://. --since-commit HEAD~5 --no-update --fail`
- **Defensa en profundidad CI:** GitHub Actions workflow `secret-scan.yml` corriendo en TODAS las PRs (DSC-S-002 punto 4).

## Por qué

El incidente P0 del 2026-05-06 ocurrió porque Manus pusheó scripts con DSN hardcoded sin que ningún hook bloqueara el commit. Ningún check automático detectó el problema durante 2-3 días. Pre-commit hooks habrían detenido el commit en el momento, antes de que el secret entrara al historial.

`gitleaks` y `trufflehog` son las dos herramientas estándar de la industria 2026 para esta defensa. Combinarlas reduce falsos negativos: gitleaks es más rápido (regex), trufflehog verifica online si el secret es activo (más lento pero menos falsos positivos).

## Implementación

### `.pre-commit-config.yaml` (raíz del repo)

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

### `.gitleaks.toml` (allowlist mínima)

```toml
[allowlist]
description = "Allowlist for known false positives"
paths = [
  '''docs/biblias_agentes_2026/.*\.md''',  # ejemplos de tokens en biblias son referencias docs
  '''\.env\.example''',                     # placeholders documentados
]
```

### CI defense — `.github/workflows/secret-scan.yml`

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
          fetch-depth: 0
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

## Reglas

1. **Todo repo del ecosistema instala pre-commit hooks** durante setup inicial. Sprint S-001 lo hace en el repo principal; nuevos repos lo agregan en el primer commit.
2. **Allowlist mínima.** Cada nueva entry en `.gitleaks.toml` requiere justificación en commit message + revisión de Cowork al firmar cierre.
3. **Bypass requiere justificación.** Usar `git commit --no-verify` o `git push --no-verify` solo está permitido si:
   - El commit message documenta explícitamente la razón ("BYPASS: <razón>")
   - El reviewer (Cowork al cierre de sprint) audita el bypass y firma o rechaza

## Implicaciones

- **Sprint S-001 instala la infraestructura** pero la política aplica desde la firma de DSC-S-002. Cualquier commit nuevo después del 2026-05-06 sin pre-commit instalado es violación.
- **Repos cruzados (biblia-github-motor, etc.)** que aún no tengan pre-commit deben instalarlo en su próximo sprint.
- **Falsos positivos** se manejan agregando entries específicas a la allowlist con justificación, NO con bypass global.

## Estado de validación

firme — fruto del incidente P0 del 2026-05-06. Implementación técnica programada en Sprint S-001.

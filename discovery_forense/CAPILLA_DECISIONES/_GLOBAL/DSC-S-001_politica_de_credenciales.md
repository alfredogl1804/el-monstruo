---
id: DSC-S-001
proyecto: GLOBAL
tipo: politica
titulo: "Política de Credenciales — cero secrets en plaintext, bóveda primaria 1Password/Bitwarden, env vars con scope mínimo, rotación al detectar exposure."
estado: firme
fecha: 2026-05-06 (originada 2026-05-04 como recomendación huérfana, firmada post-incidente P0)
fuentes:
  - chat:cowork-2026-05-04-04:36 (recomendación original que NO se firmó)
  - repo:discovery_forense/INCIDENTES/P0_2026_05_06_credenciales_repo_publico.md (postmortem que detona firma)
  - repo:scripts/run_migration_*.py (caso paradigmático del breach)
  - repo:biblia-github-motor/motor/github_radar.py (anti-patrón default value con secret)
cruza_con: [DSC-G-008, DSC-S-002, DSC-S-003, DSC-S-004, DSC-S-005, DSC-V-002]
---

# Política de Credenciales

## Decisión

Cero credenciales en plaintext en código, git history, bridge files, Notion, memory tables, logs, ni skills references. Bóveda primaria es 1Password / Bitwarden / Apple Keychain — Notion solo para documentación de "qué token cubre qué servicio", nunca para el token mismo. Runtime usa env vars con scope mínimo. Rotación inmediata al detectar exposure.

## Por qué

Detonado por incidente P0 del 2026-05-06: el password del DB Supabase del proyecto del Monstruo estaba hardcoded en al menos 5 scripts del repositorio público desde Sprint 51.5 (commit `afc461b`, 2026-05-03). Adicionalmente, un JWT `service_role` de Supabase con validez hasta 2036 estaba hardcoded como default value en `biblia-github-motor/motor/github_radar.py:32-34` (anti-patrón "default value en `os.environ.get()` con secret real" — DSC-S-004).

La política se RECOMENDÓ por Cowork el 2026-05-04 04:36 UTC como respuesta a un audit de tokens GitHub previo, pero NO se firmó como DSC. Quedó como párrafo en chat de sesión Cowork. La falta de canonización significó que cuando Manus pusheó `audit_supabase_tokens.py` al día siguiente, no había referencia normativa que prohibiera explícitamente hardcodear el DSN — y nadie lo detectó hasta el audit pre-Catastro-A del 2026-05-06.

## Reglas inmutables

### 1. CERO credenciales en plaintext en

- Git history (commits, diffs, branches, tags)
- Bridge files (`cowork_to_manus.md`, `manus_to_cowork.md`, archivos sueltos en `bridge/`)
- Notion (no es secret manager — solo documenta "qué token cubre qué servicio")
- Memory tables (`thoughts`, `episodic`, `semantic`, `magna_cache`, `error_memory`, `verification_results`)
- Logs de Railway / Vercel / Manus / Datadog
- Skills references (`skills/*/references/`)
- Documentación pública (`docs/`)
- Archivos de configuración versionados (`*.json`, `*.yaml`, `*.toml`, excepto `.env.example` con placeholders)

### 2. Bóveda primaria

- **1Password / Bitwarden / Apple Keychain.**
- Notion ÚNICAMENTE para documentación de inventario (qué token existe, qué servicio cubre, fecha de creación, fecha de última rotación).
- Bridge files NUNCA contienen credenciales — si necesitan referenciar una, dicen "credencial X — buscar en 1Password entry Y".

### 3. Runtime

| Contexto | Mecanismo | Notas |
|---|---|---|
| Mac local de Alfredo | `gh auth login` web flow | NO PAT manual escrito en archivos |
| Manus sandbox | Env vars temporales en bash session | `unset` al terminar |
| Railway / Vercel | Env vars con scope mínimo, una variable por servicio | Misma variable nombre en distintos services solo si el secret es compartido por necesidad |
| Scripts | `os.environ["VAR"]` (fail loud) | NO `os.environ.get("VAR", "default")` — ver DSC-S-004 |

### 4. Pre-commit obligatorio (DSC-S-002 anidado)

- `gitleaks detect --staged --redact` en pre-commit
- `trufflehog git file://. --since-commit HEAD~5 --no-update --fail` en pre-push
- Bloqueo automático si match de patrón de secret
- Bypass solo con `--no-verify` + justificación documentada en commit message

### 5. Audit en cierre de sprint (DSC-G-008 v2 anidado)

Cualquier sprint que toque `scripts/`, `kernel/`, `tools/`, `skills/`, `apps/`, `packages/` requiere:

- Ejecución de `bash scripts/_check_no_tokens.sh` ANTES de declarar verde
- Cowork audita contenido de archivos nuevos/modificados ANTES de firmar verde — NO solo lee el reporte de Manus
- Si script accede a DB / API externa, verificar uso de env var

### 6. Rotación

| Tipo | TTL máximo | Rotación al detectar exposure |
|---|---|---|
| GitHub PAT | 12 meses | Inmediata |
| DB password | n/a | Inmediata |
| Service role JWT | reducir validez si Supabase lo permite | Inmediata |
| API keys (OpenAI, Anthropic, Gemini, Grok, Kimi, Perplexity) | 6 meses | Inmediata |
| Supabase Personal Access Tokens (sbp_*) | 12 meses | Inmediata |
| Auditoría anual de Last Used | independiente de rotación | Anual |

### 7. Post-incidente

- Rotar inmediatamente al detectar exposure
- Audit logs del recurso comprometido (últimos 90 días)
- Decisión sobre purga de historial git: caso por caso. **Default: rotar y aceptar exposure histórica.** Razón: filter-repo es destructivo, rompe clones, requiere coordinación cara. Una vez rotados los secrets, la exposure histórica es informativa pero no explotable.
- Sembrar incident como semilla en `error_memory` + cerrar con DSC firmado

## Implicaciones

- **Violaciones bloquean cierre de sprint.** Cualquier commit que introduzca secret en plaintext es razón válida para rechazar cierre verde y exigir refactor antes de avanzar.
- **Recomendaciones de seguridad merecen DSC firmado en la misma sesión.** El patrón "Cowork recomienda en chat, no se canoniza" produjo este incidente. Política nueva: toda recomendación de seguridad de Cowork queda como DSC firmado o se descarta explícitamente con razón.
- **Sprint S-001 implementa la infraestructura técnica** (pre-commit hooks, CI workflow, refactor scripts, audit memory tables). Pero la política DSC-S-001 aplica desde la firma — no se espera la ejecución del Sprint S-001 para empezar a respetarla.

## Estado de validación

firme — fruto del incidente P0 del 2026-05-06. Originada como recomendación de Cowork el 2026-05-04 04:36 UTC, canonizada como DSC el 2026-05-06 post-detección de breach por Manus Hilo Catastro durante audit pre-sprint Catastro-A.

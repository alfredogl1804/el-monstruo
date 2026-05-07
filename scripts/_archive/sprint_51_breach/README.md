# Sprint 51 Breach — Scripts Archivados

**Fecha de archivo:** 2026-05-07
**Razon:** DSC-S-005 (cleanup default a archive) + DSC-S-010 (exposure historica vs operacional)
**Sprint origen:** S-001 Security Hardening — tarea S-1.2.b

## Contexto

Estos 9 scripts fueron creados durante el Sprint 51.5 con el password Supabase
hardcoded en plaintext. Fueron la causa raiz del incidente P0 del 2026-05-06.

Ver: `discovery_forense/INCIDENTES/P0_2026_05_06_credenciales_repo_publico.md`

## Por que se archivan en lugar de refactorizarse

Refactor a env vars NO elimina el password de Git history. Una vez que un
secret se commiteo, esta en el repo publico para siempre (a menos que se haga
filter-repo, descartado por DSC-S-001 "rotar y aceptar exposure historica").

El password ya fue rotado y deshabilitado durante SECURITY-001 (cerrado verde
2026-05-06). La exposure es **historica, no operacional** — un atacante con
git log puede leerlo, pero no concede acceso porque la credencial ya no funciona.

Refactorizar 9 archivos en este punto seria trabajo cosmetico sin valor.
Lo que importa:

1. La credencial esta rotada (hecho).
2. Pre-commit hooks (S-1.1) bloquean futuros commits con plaintext.
3. Los scripts viejos se archivan como evidencia forense del antipatron.

## Compliance

- **DSC-S-001:** rotacion inmediata aplicada -> verde.
- **DSC-S-003:** scripts futuros usan `os.environ[VAR]` fail-loud.
- **DSC-S-004:** prohibido `os.environ.get(VAR, "secret_default")` — bloqueado por gitleaks.
- **DSC-S-005:** archive antes que delete — estos scripts viven aqui.
- **DSC-S-010:** exposure historica aceptada explicitamente al cierre.

## Lista de scripts (9)

1. `audit_supabase_tokens.py`
2. `register_sovereign_browser_tool.py`
3. `run_fix_trigger.py`
4. `run_migration_013.py`
5. `run_migration_014.py`
6. `run_migration_015.py`
7. `run_migration_027.py`
8. `run_migration_028.py`
9. `run_migrations_012_013.py`

**No ejecutar.** Son evidencia forense, no scripts operacionales.

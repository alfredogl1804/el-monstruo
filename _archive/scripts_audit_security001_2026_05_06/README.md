# Audit Scripts SECURITY-001 — Archived 2026-05-07

Estos 9 scripts fueron creados durante el **Sprint Emergencia SECURITY-001** (P0 del 2026-05-06: credenciales en repo público) para barrer en paralelo todos los repos GitHub del usuario, los clones locales del Mac, y los servicios externos (Railway, Supabase) en busca de secrets hardcoded.

## Cumplieron su misión

| Script | Función | Resultado |
|---|---|---|
| `.scan_secrets.sh` | Scan inicial de patrones gitleaks en `~/el-monstruo` y repos privados clonados | Detectó 3 secrets en BGM + crisol-8 |
| `.scan_jwt_local.sh` | Variante específica para JWT `eyJhbGciOiJIUzI1NiIs...` en clones locales | 0 hits adicionales |
| `.scan_all_repos.sh` | Itera sobre `gh repo list alfredogl1804` y clona+grep en `/tmp` | Confirmó scope: solo BGM y crisol-8 |
| `.scan_ai_pipeline.sh` | Scan exhaustivo de `~/AI-Pipeline` (proyecto separado) | 0 hits |
| `.cross_scan_jwt.sh` | Cross-validation con regex JWT relaxado | Confirmó cobertura |
| `.cross_scan_anon.sh` | Búsqueda específica de pattern anon JWT | 0 hits adicionales |
| `.audit_service_role.sh` | Audit del JWT `service_role` en repos + Railway env vars | Identificó 7 vars en 4 services Railway (kernel, monstruo, command-center, worker) |
| `.audit_railway_jwt.sh` | Audit específico de Railway env vars con JWT pattern | Base para SECURITY-002 |
| `.classify_hits.sh` | Clasificador de findings (severidad, scope, public vs private) | Generó tabla de triage |

## Por qué archive y no delete

Per **DSC-S-005** (default archive antes que delete):
- Reversible si necesitamos re-correrlos durante un próximo audit
- Documentación viva del proceso ejecutado durante la P0
- Scope mínimo: están fuera del runtime path (`_archive/` no es trackeado por la app)
- TTL: revisar en 90 días (2026-08-05) y considerar delete o consolidar en herramienta canon

## Lecciones que ya están internalizadas

Lo aprendido durante estos audits ya está canonizado en:
- `discovery_forense/CAPILLA_DECISIONES/_GLOBAL/DSC-S-001_*.md` a `DSC-S-005_*.md`
- `discovery_forense/INCIDENTES/P0_2026_05_06_credenciales_repo_publico.md`
- `bridge/sprints_propuestos/sprint_S001_security_hardening.md`
- `bridge/manus_to_cowork_REPORTE_P0_*.md` (rotación + service_role)
- `bridge/manus_to_cowork_REPORTE_SECURITY_002_2026_05_07.md`

## Recovery

Si necesitas re-correr alguno:

```bash
cp _archive/scripts_audit_security001_2026_05_06/.scan_secrets.sh /tmp/run_scan.sh
chmod +x /tmp/run_scan.sh
/tmp/run_scan.sh
```

No re-introducirlos al root del repo. La herramienta canónica futura debería vivir en `scripts/security_audit/` con un único entry point parametrizado, ver Sprint S-001 (S-1.4 + S-1.7).

— Hilo Catastro, archive ejecutado 2026-05-07

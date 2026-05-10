# Sprint S-002.6 — DECLARADO VERDE

**De**: Hilo B (Manus)
**Para**: Cowork (Claude)
**Fecha**: 2026-05-10
**Branch**: `sprint/s-002-6-rls-completion`
**PR**: pendiente de creación

---

## TL;DR

✅ **Las 6 tareas del Sprint S-002.6 MEGA están completas.** El universo RLS del schema `public` está al **100%** (117/117 tablas + 2/2 matviews protegidas). Cero rollbacks, cero downtime. Linter pre-commit y workflow CI semanal desplegados. DSC-S-007 firmado.

## Estado en producción

| Métrica | Antes S-002.6 | Después S-002.6 |
|---|---|---|
| Tablas con RLS | 30 | **117** |
| Tablas con RLS sin policy | 1 | **0** |
| Matviews protegidas | 0 | **2** |
| Universo RLS completo | NO | **SÍ** |

## Artefactos entregados

| # | Archivo | Tipo | Líneas |
|---|---|---|---|
| 1 | `migrations/sql/0006_embrion_memoria_explicit_policy.sql` | SQL | 60 |
| 2 | `migrations/sql/0007_rls_tablas_post_s002_5.sql` | SQL | 121 |
| 3 | `migrations/sql/0008_rls_p2_completion.sql` | SQL | 785 |
| 4 | `discovery_forense/CAPILLA_DECISIONES/_GLOBAL/DSC-S-007_naming_canonico_supabase_service_key.md` | DSC | ~110 |
| 5 | `scripts/_check_rls_default.py` | Linter | 174 |
| 6 | `scripts/_audit_rls.py` | Audit CI | 150 |
| 7 | `.github/workflows/rls-audit-weekly.yml` | Workflow | 70 |
| 8 | `.pre-commit-config.yaml` | Config (modificado) | +13 |
| 9 | `bridge/postmortem_sprint_s002_6_rls_2026_05_10.md` | Postmortem | 200+ |

**Total**: 8 archivos nuevos + 1 modificado, ~1,700 líneas.

## Smoke tests ejecutados

- ✅ Verificación schema: 117/117 tablas con RLS, 0 deuda residual
- ✅ Endpoints kernel post 0008: 13/13 endpoints responden 200 OK
- ✅ Test funcional cowork_bridge: INSERT/SELECT/DELETE en `embrion_memoria` con service_role todos PASS
- ✅ Linter `_check_rls_default.py`: pasa migraciones legítimas (EXIT=0), rechaza CREATE TABLE sin RLS (EXIT=1)
- ✅ Audit script `_audit_rls.py`: corrido contra producción, EXIT=0, reporte limpio

## Hallazgos para tu atención

1. **Dependencia para CI workflow**: necesitas configurar GitHub Secrets:
   - `SUPABASE_ACCESS_TOKEN` (tu PAT `sbp_*` ya existente en macOS Keychain `monstruo-supabase-pat`)
   - `SUPABASE_PROJECT_REF` (`xsumzuhwmivjgftsneov`)
   - Sin estos, el workflow no podrá correr la auditoría semanal.

2. **Migración del PR a main**: igual que S-002.5, este PR es write-risky (toca producción aunque ya está aplicado). Recomiendo squash + delete branch, mismo patrón del PR #43.

3. **DSC-S-007 indexación**: agregar a:
   - `discovery_forense/CAPILLA_DECISIONES/_INDEX.md`
   - `discovery_forense/CAPILLA_DECISIONES/_GLOBAL/_dsc_contracts_index.yaml`

4. **El audit script puede invocarse manualmente** para verificación inmediata post-merge:
   ```
   export SUPABASE_ACCESS_TOKEN=...
   export SUPABASE_PROJECT_REF=xsumzuhwmivjgftsneov
   python3 scripts/_audit_rls.py
   ```

## Pendiente de mi parte

- [ ] Push de la branch `sprint/s-002-6-rls-completion` a origin
- [ ] Apertura del PR contra `main`
- [ ] Reporte final al bridge (este archivo)

## Pendiente de Cowork

- [ ] Audit del PR (8 nuevos + 1 modificado)
- [ ] Configurar GitHub Secrets para el workflow CI
- [ ] Indexar DSC-S-007
- [ ] Frase canónica `🏛️ SPRINT S-002.6 — DECLARADO VERDE`
- [ ] Decisión sobre Sprint S-003 (siguiente)

## Recordatorio crítico

- **Rota tu master password de Bitwarden** (sigue pendiente desde ayer).
- El PAT de Supabase en Keychain (`monstruo-supabase-pat`) puede rotarse en 6 meses según DSC-S-003.

---

**Firma**: 🏛️ SPRINT S-002.6 — DECLARADO VERDE POR HILO B, ESPERANDO AUDIT

# Postmortem — Sprint S-002.6 (RLS Completion + Hardening)

**Fecha**: 2026-05-10
**Estado**: ✅ DECLARADO VERDE
**Hilo ejecutor**: B (Manus)
**Orquestador**: Cowork (Claude)
**Branch**: `sprint/s-002-6-rls-completion`
**PR**: pendiente de creación

---

## Resumen ejecutivo

Sprint MEGA que completó al **100%** el universo RLS del schema `public` de Supabase, agregando políticas a las **85 tablas P2** restantes + corrigiendo deuda en `embrion_memoria` + cubriendo las **3 tablas nuevas** delegadas (catastro y embrion_write_proposals) + **2 matviews** vía REVOKE PUBLIC. Adicionalmente firmó **DSC-S-007** (naming canónico SUPABASE_SERVICE_KEY), implementó **linter pre-commit** que enforza DSC-S-006 regla 1, y desplegó **workflow CI semanal** que audita el estado RLS con apertura automática de issue al detectar violaciones.

| Métrica | Antes | Después |
|---|---|---|
| Tablas con RLS habilitado | 30 | **117** |
| Tablas con RLS sin policy (deuda) | 1 (`embrion_memoria`) | **0** |
| Matviews protegidas | 0 | **2** |
| Tablas sin RLS en `public` | **89** | **0** |
| Linter pre-commit RLS | no existía | activo |
| Audit RLS automatizado | no existía | semanal |

## Tareas completadas (6/6)

### Tarea 1 — RLS sobre 85 tablas P2 + 1 matview ✅
- Migración `0008_rls_p2_completion.sql` (785 líneas, 36KB).
- Generador Python (`~/.monstruo/sprints/s002_6/03_generar_migracion_0008.py`) construye SQL atomico (BEGIN/COMMIT) con bloques uniformes por tabla.
- Aplicada en producción vía Supabase Management API. HTTP 201, sin rollback.
- Smoke test post-aplicación: 13/13 endpoints del kernel responden 200 OK.

### Tarea 2 — Policy explícita en `embrion_memoria` ✅
- Migración `0006_embrion_memoria_explicit_policy.sql`.
- Tabla tenía `relrowsecurity=true` con **0 policies** (deuda crítica heredada).
- Smoke test cowork_bridge: INSERT/SELECT/DELETE con service_role todos PASS.

### Tarea 3 — RLS sobre 3 tablas nuevas delegadas ✅
- Migración `0007_rls_tablas_post_s002_5.sql`.
- `embrion_write_proposals`, `catastro_agentes`: tablas regulares, RLS + policy `service_role_only`.
- `catastro_tronos_agentes`: matview (relkind='m'), no soporta `ENABLE RLS`. Protegida vía `REVOKE ALL FROM PUBLIC + anon + authenticated` y `GRANT TO service_role`.

### Tarea 4 — DSC-S-007: naming canónico ✅
- Documento `discovery_forense/CAPILLA_DECISIONES/_GLOBAL/DSC-S-007_naming_canonico_supabase_service_key.md`.
- Canoniza `SUPABASE_SERVICE_KEY` (sin `_ROLE`) como nombre real, alineado con Railway env vars y código del kernel.
- Justifica usando formato nuevo `sb_secret_*` en lugar de JWT legacy.
- Excepciones: SDK Supabase (literal interno), policies SQL (`auth.role() = 'service_role'`), docs históricos.

### Tarea 5 — Linter pre-commit (DSC-S-006 regla 1 + DSC-S-004) ✅
- `scripts/_check_rls_default.py` (ejecutable).
- Hook `rls-default-check` agregado a `.pre-commit-config.yaml`.
- Detecta:
  - `CREATE TABLE` en `public.*` sin `ENABLE RLS` ni `CREATE POLICY`.
  - `CREATE MATERIALIZED VIEW` sin `REVOKE PUBLIC`.
  - `os.environ.get("SUPABASE_*", "default-secreto")` (anti-patrón DSC-S-004).
- Bypass legítimo vía comentario `-- DSC-S-006: skip RLS justificado: <razón>`.
- Validado: pasa migraciones 0006-0008 (EXIT=0), rechaza tabla sin RLS (EXIT=1).

### Tarea 6 — Workflow CI semanal de auditoría ✅
- `.github/workflows/rls-audit-weekly.yml`: cron `0 9 * * 1` (lunes 09:00 UTC).
- `scripts/_audit_rls.py`: cliente Python que ejecuta 4 queries contra Supabase Management API y genera `rls_audit_report.md`.
- Falla el job si encuentra:
  - Tablas sin RLS, O
  - Tablas con RLS sin policy, O
  - Matviews con grants para PUBLIC/anon/authenticated.
- Al fallar, abre **issue automático** con label `security`, `rls-audit`, `auto-generated`.
- Dependencias requeridas en GitHub Secrets: `SUPABASE_ACCESS_TOKEN`, `SUPABASE_PROJECT_REF`.
- Validado en producción local: EXIT=0 con reporte limpio.

## Datos técnicos

### Schema final
- **117 tablas** con RLS habilitado (100%)
- **117 policies** `service_role_only` (uno por tabla)
- **2 matviews** con REVOKE PUBLIC + GRANT service_role
- **0 deuda residual** en el schema `public`

### Migraciones aplicadas
| # | Archivo | Líneas | Bytes | Tablas afectadas |
|---|---|---|---|---|
| 0006 | embrion_memoria_explicit_policy.sql | 60 | 2,043 | 1 |
| 0007 | rls_tablas_post_s002_5.sql | 121 | 4,740 | 3 |
| 0008 | rls_p2_completion.sql | 785 | 36,327 | 86 (85 tablas + 1 matview) |

### Smoke tests ejecutados
| Tipo | Resultado |
|---|---|
| Verificación schema (RLS + policies) | 117/117 PASS |
| Endpoints kernel post 0006 | 4/4 PASS |
| Endpoints kernel post 0007 | confirmados |
| Endpoints kernel post 0008 | 13/13 PASS |
| Test funcional cowork_bridge (INSERT/SELECT/DELETE) | PASS |
| Audit script local | EXIT=0, reporte limpio |

## Lecciones aprendidas

### Lo que funcionó bien
1. **Generador SQL determinístico**: Python lee la lista de tablas y genera SQL uniforme, evitando errores de copy-paste en 85 bloques.
2. **Atomicidad BEGIN/COMMIT**: La migración 0008 envuelve todas las 85+1 operaciones en una transacción. Si una falla, ninguna se aplica.
3. **Patrón de matviews vía REVOKE**: Postgres no permite `ENABLE RLS` en matviews, pero el equivalente funcional (REVOKE PUBLIC + GRANT service_role) logra el mismo resultado.
4. **Linter desde el día 1**: integrar el hook ANTES de mergear el sprint asegura que ningún sprint futuro pueda crear tablas sin RLS sin justificación explícita.
5. **Audit script reutilizable**: El mismo script corre en CI weekly Y se puede invocar manualmente para validación post-deploy.

### Friction encontrada
1. **Heredoc bash en sesión multi-shell**: la sesión `desktop:` ocasionalmente corrompe heredocs largos por concurrencia. Solución: escribir scripts a archivo con FUSE+`file write`, no inline.
2. **FUSE mount intermitente**: `/mnt/desktop/el-monstruo` ocasionalmente no responde, requiriendo escritura directa al filesystem del Mac vía sesión shell.
3. **Branch tracking**: tras hacer `git stash + checkout`, varios untracked viajan con el checkout. Importante validar `git branch --show-current` antes de cada commit.

### Hallazgos para sprints futuros
1. **Naming inconsistente histórico**: archivos pre-DSC-S-007 contienen `SUPABASE_SERVICE_ROLE_KEY`. No se migra retroactivamente; el linter solo valida nuevos archivos.
2. **`embrion_memoria` con RLS=true sin policies**: estado encontrado pre-sprint, ya corregido. Sugiere posible regresión silenciosa si una policy se borra. El audit weekly detectará esto.
3. **Migraciones existentes (0001-0005)**: Algunas crearon tablas sin RLS. El linter SOLO valida archivos staged en commit nuevo, no migraciones históricas.
4. **Vistas materializadas adicionales**: si se crean nuevas matviews en el futuro, el linter las detecta y exige REVOKE PUBLIC.

## Cumplimiento DSC

- ✅ **DSC-S-001**: Tokens nunca en código. PAT extraído de macOS Keychain via `security` CLI.
- ✅ **DSC-S-002**: gitleaks/trufflehog ejecutados pre-commit. Cero leaks.
- ✅ **DSC-S-003**: Rotación TTL respetada (PAT con TTL 12 meses).
- ✅ **DSC-S-004**: `require_env()` patrón seguido. Linter agrega enforcement automático.
- ✅ **DSC-S-005**: Cleanup default a archive. No se eliminó ningún objeto.
- ✅ **DSC-S-006**: Sprint principal. RLS por defecto enforced via linter.
- ✅ **DSC-S-007**: Firmado en este sprint. Naming canónico documentado.
- ✅ **DSC-G-008 v2**: Cowork audita contenido del PR.

## Pendientes de Cowork

1. **Audit del PR del Sprint S-002.6** (contiene 8 archivos nuevos + 1 modificado).
2. **Frase canónica** `🏛️ SPRINT S-002.6 — DECLARADO VERDE` post-merge.
3. **Indexar DSC-S-007** en `discovery_forense/CAPILLA_DECISIONES/_INDEX.md` y `_dsc_contracts_index.yaml`.
4. **Configurar GitHub Secrets** para que el workflow CI corra:
   - `SUPABASE_ACCESS_TOKEN` (tu PAT `sbp_*` actual)
   - `SUPABASE_PROJECT_REF` (`xsumzuhwmivjgftsneov`)
5. **Decidir**: ¿se ejecuta el workflow manualmente una primera vez para validar?

## Métricas finales

| Indicador | Valor |
|---|---|
| Archivos nuevos en sprint | 8 |
| Archivos modificados | 1 (`.pre-commit-config.yaml`) |
| Líneas SQL escritas | 906 |
| Líneas Python escritas | 414 |
| Líneas markdown escritas | 350+ |
| Tablas afectadas en producción | 89 |
| Pre-commit hooks añadidos | 1 (rls-default-check) |
| Workflows CI añadidos | 1 (rls-audit-weekly) |
| DSCs firmados | 1 (DSC-S-007) |
| Tiempo de aplicación migración 0008 | < 2 segundos |
| Cero downtime | ✅ |
| Cero rollbacks | ✅ |

---

**Firma Hilo B**: 🏛️ SPRINT S-002.6 — TRABAJO COMPLETO, ESPERANDO AUDIT DE COWORK

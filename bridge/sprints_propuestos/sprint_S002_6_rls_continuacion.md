# Sprint S-002.6 — Hardening RLS (Continuación)

**Estado:** Propuesto
**Hilo:** Ejecutor (Manus / Hilo B)
**ETA estimada:** 90-120 min con velocity demostrada
**Objetivo:** Cerrar pendientes de S-002.5, instalar linter preventivo de RLS, completar auditoría de schema y documentar onboarding inter-hilo del MCP Supabase.
**Bloqueos:** Ninguno conocido (S-002.5 dejó el sistema verde y operativo).
**Resultado esperado:** Linter pre-commit que rechaza migraciones SQL sin RLS + policy explícita en `embrion_memoria` + auditoría completa del schema `public` + documentación de onboarding del MCP Supabase + DSC-S-006 indexado.

---

## 0. Procedencia — Por qué este sprint existe

Sprint S-002.6 nace del postmortem de S-002.5 (`bridge/postmortem_sprint_s002_5_rls_2026_05_10.md`). El sprint anterior cerró el riesgo agudo (8 tablas P0+P1 expuestas) pero dejó deuda preventiva pendiente:

- **Causa raíz no eliminada:** no existe linter que evite que la próxima migración SQL cree una tabla sin RLS.
- **`embrion_memoria` con estado anómalo:** RLS=true sin policies (frágil, depende de `bypassrls` implícito de service_role).
- **Auditoría parcial:** solo se cubrieron 9 tablas; el schema `public` puede tener más tablas sin RLS no inventariadas.
- **Onboarding inter-hilo opaco:** Hilo B tardó horas en descubrir el wrapper `~/.monstruo/mcp-wrappers/supabase-mcp.sh` y el PAT en macOS Keychain.
- **Naming inconsistente:** kernel usa `SUPABASE_SERVICE_KEY`, spec mencionaba `SUPABASE_SERVICE_ROLE_KEY`.

---

## 1. Audit pre-sprint — Estado actual

### Lo que ya existe

- `migrations/sql/0004_enable_rls_p0_critico.sql` (Sprint S-002.5)
- `migrations/sql/0005_enable_rls_p1_embrion_stack.sql` (Sprint S-002.5)
- `~/.monstruo/sb_sql.py` (helper Python para Management API, no versionado)
- `~/.monstruo/mcp-wrappers/supabase-mcp.sh` (wrapper de Cowork, no versionado)
- DSC-S-006 firmado (RLS por defecto en tablas nuevas)
- Política DSC-S-001 a DSC-S-005 (familia de seguridad)

### Lo que NO existe (gaps)

- Linter pre-commit que valide RLS en migraciones SQL nuevas
- Policy explícita en `embrion_memoria` (RLS=true, policies=0)
- Auditoría completa del schema `public` (>30 tablas potenciales sin inventariar)
- `docs/MCP_SUPABASE_ONBOARDING.md`
- Referencia al wrapper en `AGENTS.md`
- Decisión canonizada sobre naming `SUPABASE_SERVICE_KEY` vs `SUPABASE_SERVICE_ROLE_KEY`
- Indexación de DSC-S-006 en `_INDEX.md` y `_dsc_contracts_index.yaml`

---

## 2. Tareas

### Tarea 1 — Linter pre-commit para migraciones SQL

**Perfil de riesgo:** write-safe (toca solo `scripts/` y `.pre-commit-config.yaml`)

Implementar `scripts/_check_rls_in_migrations.sh` que escanea archivos `.sql` staged en `migrations/sql/` y rechaza commits cuando un archivo:

- Contiene `CREATE TABLE` en schema `public`
- NO contiene `ENABLE ROW LEVEL SECURITY` en el mismo archivo
- NO contiene `CREATE POLICY` en el mismo archivo

Integrar en `.pre-commit-config.yaml` como hook nuevo. Probar con migración dummy que debería ser rechazada.

**Criterios de cierre:** hook instalado + test con migración dummy bloqueada + DSC-S-006 referenciado en mensaje de error.

### Tarea 2 — Policy explícita en `embrion_memoria`

**Perfil de riesgo:** write-risky (toca producción Supabase)

Crear `migrations/sql/0006_add_policy_embrion_memoria.sql` con:

```sql
CREATE POLICY "service_role_only"
  ON public.embrion_memoria
  AS PERMISSIVE
  FOR ALL
  TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
```

Aplicar via `~/.monstruo/sb_sql.py`. Smoke test del kernel post-aplicación obligatorio. Rollback: `DROP POLICY` si kernel falla.

**Criterios de cierre:** policy aplicada + smoke test 19/19 PASS + verificación de conteo `embrion_memoria` (1588 filas accesibles vía service_role, 0 vía anon).

### Tarea 3 — Auditoría completa del schema `public`

**Perfil de riesgo:** read-only (solo SELECT)

Ejecutar query global y producir reporte en `bridge/audit_rls_2026_05_XX_full_schema.md`:

```sql
SELECT c.relname AS tabla,
       c.relrowsecurity AS rls,
       (SELECT count(*) FROM pg_policies WHERE tablename = c.relname AND schemaname = 'public') AS num_policies,
       pg_size_pretty(pg_total_relation_size(c.oid)) AS size
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = 'public' AND c.relkind = 'r'
ORDER BY c.relrowsecurity ASC, c.relname;
```

Por cada tabla con `rls=false`, clasificar (P0/P1/P2/excepción) y proponer migración o DSC de excepción.

**Criterios de cierre:** reporte entregado + cada tabla con `rls=false` con plan de acción documentado.

### Tarea 4 — Documentación de onboarding inter-hilo del MCP Supabase

**Perfil de riesgo:** write-safe (solo docs)

Crear `docs/MCP_SUPABASE_ONBOARDING.md` con:

- Cómo Cowork accede vía wrapper `~/.monstruo/mcp-wrappers/supabase-mcp.sh` y Keychain
- Cómo Manus accede vía helper `~/.monstruo/sb_sql.py` (versionar el helper en `scripts/_sb_sql.py`)
- Cómo generar y guardar un nuevo PAT (`security add-generic-password -a $USER -s monstruo-supabase-pat -w <PAT>`)
- Cómo rotar (revocar en https://supabase.com/dashboard/account/tokens, generar nuevo, reemplazar en Keychain)

Sembrar referencia en `AGENTS.md` para que cualquier hilo nuevo lo descubra inmediatamente.

**Criterios de cierre:** doc entregado + referencia en AGENTS.md + helper versionado.

### Tarea 5 — Consistencia de naming `SUPABASE_SERVICE_KEY`

**Perfil de riesgo:** write-safe (audit + posible refactor menor)

Auditar el código:

```bash
grep -rn "SUPABASE_SERVICE" kernel/ memory/ tools/ apps/ packages/
```

Si hay alguna lectura inconsistente, agregar fallback:

```python
SUPABASE_SERVICE_KEY = (
    os.environ.get("SUPABASE_SERVICE_KEY")
    or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
)
```

Decidir nombre canónico vía DSC y aplicar uniformemente.

**Criterios de cierre:** código consistente + DSC firmado con decisión + Railway env coherente.

### Tarea 6 — Indexación de DSC-S-006

**Perfil de riesgo:** write-safe (solo metadatos)

Agregar entrada para DSC-S-006 en:
- `discovery_forense/CAPILLA_DECISIONES/_INDEX.md`
- `discovery_forense/CAPILLA_DECISIONES/_dsc_contracts_index.yaml`

(Estos archivos están actualmente modificados en flight por Cowork; coordinar para no romper su trabajo.)

**Criterios de cierre:** índice actualizado + yaml válido.

---

## 3. Riesgos

| Riesgo | Mitigación |
|---|---|
| Tarea 2 rompe acceso del kernel a `embrion_memoria` (1588 filas) | Smoke test post-aplicación + rollback ready (DROP POLICY) |
| Linter de Tarea 1 produce falsos positivos en `ALTER TABLE` o `IF NOT EXISTS` | Detectar solo `CREATE TABLE` y excluir `IF NOT EXISTS` cuando ya existe la tabla |
| Auditoría de Tarea 3 descubre 30+ tablas sin RLS | Priorizar P0 primero; dividir en sub-sprints S-002.7/S-002.8 si es necesario |
| Tarea 6 colisiona con archivos en flight de Cowork | Coordinar al inicio del sprint vía bridge antes de tocar `_INDEX.md` |

---

## 4. Definition of Done (Criterios de Cierre)

- ✅ Linter rechaza correctamente migración de prueba sin RLS
- ✅ `embrion_memoria` con policy explícita aplicada y verificada
- ✅ Auditoría de schema completo entregada como `bridge/audit_rls_2026_05_XX_full_schema.md`
- ✅ `docs/MCP_SUPABASE_ONBOARDING.md` creado y referenciado en `AGENTS.md`
- ✅ Helper `scripts/_sb_sql.py` versionado en repo
- ✅ Tarea 5 cerrada con código consistente o DSC de naming canonizado
- ✅ DSC-S-006 indexado correctamente
- ✅ Smoke test del kernel: 19/19 PASS post-Tarea 2
- ✅ Gitleaks verde en commit final
- ✅ Cowork audita contenido y declara verde
- ✅ Postmortem entregado en `bridge/postmortem_sprint_s002_6_rls_continuacion_*.md`

---

## 5. Acciones del usuario (NO del sprint, pero relacionadas)

- Rotar master password de Bitwarden de Alfredo (quedó en log del chat durante S-002.5)
- Aprobar este spec antes de iniciar ejecución

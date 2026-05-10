# DSC-S-006 v1.1 — RLS por defecto en tablas nuevas (extensión whitelist)

**Tipo**: Decisión de Seguridad Canónica (extensión)
**Estado**: ✅ FIRMADO
**Versión**: 1.1
**Versión previa**: 1.0 (Sprint S-002.6)
**Fecha v1.0**: 2026-05-10
**Fecha v1.1**: 2026-05-10
**Sprint**: S-003.B (Hardening Profundo Continuo — write-risky)
**Autor**: Hilo B (Manus)
**Co-autor**: Cowork (orquestador, autorizó la extensión en spec del sprint S-003.B Tarea 4)
**Owner**: Alfredo

---

## Origen de la extensión v1.1

Durante el Sprint S-003.A, el linter `scripts/_check_rls_default.py` v1.0 generó un **falso positivo** sobre el script `scripts/_audit_rls.py`:

```python
project_ref = os.environ.get("SUPABASE_PROJECT_REF", "xsumzuhwmivjgftsneov")
```

El regex `DEFAULT_SECRET_RE` clasificó `xsumzuhwmivjgftsneov` (que es un identificador público del proyecto Supabase, visible en URLs del dashboard) como secret porque cumplía la heurística de longitud y formato. La corrección reactiva fue eliminar el default value, pero esto sembró la necesidad de una whitelist explícita.

Adicionalmente, Cowork anticipó en el spec de S-003.B Tarea 4 que tablas catálogo público con policies `anon_read_only` (ej: `public_pricing_plans`, `public_announcements`) serán necesarias en sprints futuros y harán fallar el linter v1.0 que requiere policies `service_role_only` estrictamente.

## Reglas extendidas v1.1

### Regla 4 (NUEVA en v1.1): Tablas catálogo público en PUBLIC_WHITELIST

Las tablas que sirven catálogos públicos legítimos (pricing públicos, announcements, listas de productos visibles sin autenticación, etc.) pueden tener policies menos restrictivas que `service_role_only`. Para que el linter las acepte:

1. **Agregar la tabla a `PUBLIC_WHITELIST`** en `scripts/_check_rls_default.py`
2. **Documentar la inclusión** en este DSC con justificación: por qué es público, qué datos contiene, quién decidió
3. **Mantener obligatorio**: `ENABLE ROW LEVEL SECURITY` + al menos una policy explícita

Ejemplo válido para tabla whitelisted:

```sql
CREATE TABLE public.public_pricing_plans (
  id UUID PRIMARY KEY,
  plan_name TEXT NOT NULL,
  price_cents INT NOT NULL
);
ALTER TABLE public.public_pricing_plans ENABLE ROW LEVEL SECURITY;
CREATE POLICY "anon_read_only" ON public.public_pricing_plans
  AS PERMISSIVE FOR SELECT TO anon, authenticated
  USING (true);
CREATE POLICY "service_role_full" ON public.public_pricing_plans
  AS PERMISSIVE FOR ALL TO public
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
```

**Importante**: aunque la tabla esté en whitelist, mantener una policy `service_role_only` adicional para writes es recomendado pero no obligatorio. La whitelist solo dispensa de la regla "todas las policies deben ser service_role_only".

### Regla 5 (NUEVA en v1.1): Identificadores públicos en PUBLIC_IDENTIFIERS_WHITELIST

Los identificadores públicos que NO son credenciales pero pueden confundirse con secrets por sus características de longitud y formato (ej: project_refs, IDs públicos de servicios, slugs largos) pueden incluirse en `PUBLIC_IDENTIFIERS_WHITELIST` para evitar falsos positivos del linter.

Para que el linter los acepte:

1. **Agregar el identificador exacto a `PUBLIC_IDENTIFIERS_WHITELIST`** en `scripts/_check_rls_default.py`
2. **Documentar la inclusión** en este DSC con justificación: por qué es público, dónde se usa, quién lo confirmó como no-credencial

Identificadores actualmente whitelisted:

| Identificador | Servicio | Naturaleza | Justificación |
|---|---|---|---|
| `xsumzuhwmivjgftsneov` | Supabase project_ref | Identificador público | Visible en URL `https://xsumzuhwmivjgftsneov.supabase.co` y en el dashboard. Se usa como argumento `--project-ref` en CLI. NO es credencial — credenciales son `SUPABASE_SERVICE_KEY` y `SUPABASE_KEY`. |

## Contracto canónico v1.1

```yaml
dsc_id: DSC-S-006-v1.1
title: RLS por defecto en tablas nuevas (whitelist público y identificadores)
extends: DSC-S-006-v1.0
status: signed
sprint: S-003.B
author: hilo-b
co_author: cowork
owner: alfredo
date: 2026-05-10
rules:
  - id: rule-1
    text: "CREATE TABLE en schema public requiere ENABLE RLS + policy service_role_only"
    enforcement: scripts/_check_rls_default.py
  - id: rule-2
    text: "CREATE MATERIALIZED VIEW en schema public requiere REVOKE ALL FROM PUBLIC"
    enforcement: scripts/_check_rls_default.py
  - id: rule-3
    text: "Default values con secrets en os.environ.get prohibidos"
    enforcement: scripts/_check_rls_default.py
  - id: rule-4
    text: "Tablas catálogo público en PUBLIC_WHITELIST permiten policies anon_read_only"
    requires: "ENABLE RLS + al menos una policy explícita"
    documentation: "DSC-S-006 v1.1"
  - id: rule-5
    text: "Identificadores públicos en PUBLIC_IDENTIFIERS_WHITELIST exentos de check secret"
    requires: "Justificación documentada en DSC-S-006 v1.1"
governance:
  add_to_whitelist:
    process: "PR contra scripts/_check_rls_default.py + actualización de este DSC + audit Cowork"
    approval_required: cowork_audit_dsc_g_008_v2
  remove_from_whitelist:
    process: "PR contra scripts/_check_rls_default.py + actualización de este DSC + revisión de impacto"
    approval_required: cowork_audit_dsc_g_008_v2
```

## Cruces canónicos

- **DSC-S-004** (DRY-RUN credenciales): la regla 5 v1.1 introduce excepción explícita para identificadores públicos. NO autoriza usar credenciales reales como default values; solo identificadores no-secret.
- **DSC-S-006 v1.0** (Sprint S-002.6): este documento extiende sin invalidar las reglas 1-3 originales.
- **DSC-S-008** (rotación credenciales): identificadores en `PUBLIC_IDENTIFIERS_WHITELIST` NO requieren rotación (no son credenciales).
- **DSC-S-010** (hardening operacional integrado): este DSC pertenece al plano de "datos cerrados por defecto".
- **AGENTS.md regla #7** (Plano de Datos Cerrado por Defecto): refuerza esta política como regla dura aplicable a TODO sprint.

## Validación

```bash
# Test 1: tabla normal con policy service_role_only → PASS
$ python3 scripts/_check_rls_default.py migrations/sql/0006_embrion_memoria_explicit_policy.sql
$ echo $?
0

# Test 2: identificador público en whitelist → PASS
$ python3 scripts/_check_rls_default.py scripts/_audit_rls.py
$ echo $?
0
```

## Refs históricas

- Sprint S-002.6: linter v1.0 introducido como Tarea 5
- Sprint S-003.A: falso positivo en `_audit_rls.py` (corregido reactivamente)
- Sprint S-003.B: extensión v1.1 con whitelist + project_ref de Supabase agregado

## Cierre

🏛️ **DSC-S-006 v1.1 — FIRMADO**

— Manus, Hilo B, 2026-05-10

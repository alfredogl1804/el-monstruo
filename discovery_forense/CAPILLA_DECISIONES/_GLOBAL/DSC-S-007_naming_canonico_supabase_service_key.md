# DSC-S-007 — Naming canónico para credenciales Supabase

**Tipo**: Decisión de seguridad (DSC-S)
**Fecha**: 2026-05-10
**Sprint**: S-002.6 — Tarea 4
**Autor**: Hilo B (ejecutor) — propuesto por Cowork (orquestador)
**Estado**: FIRMADO

---

## 1. Contexto

Durante el Sprint S-002.5 (Hardening RLS Producción), Hilo B detectó una inconsistencia entre la spec de Cowork y la realidad operativa:

- **Spec original** mencionaba `SUPABASE_SERVICE_ROLE_KEY` como nombre canónico de la credencial.
- **Railway env vars del kernel** usan `SUPABASE_SERVICE_KEY` (nombre real).
- **Código del kernel** (`kernel/security/env_validator.py`, módulos de DB) está adaptado al nombre real.
- El kernel funciona porque su código consulta el nombre que efectivamente existe en env.

Esta inconsistencia generó:
1. Confusión durante pre-flight del sprint (Hilo B tuvo que descubrir el naming real).
2. Riesgo de copy-paste de fragmentos de spec sin verificar contra realidad.
3. Documentación que apunta a un nombre que no existe en el sistema.

Adicionalmente, Supabase introdujo en 2024-2025 un **nuevo formato de keys**:
- `eyJ...` (legacy JWT) — formato antiguo, sigue siendo válido pero deprecated en projects nuevos.
- `sb_secret_*` — nuevo formato (2024+), reemplaza el JWT, mejor seguridad y rotación.
- `sb_publishable_*` — nuevo anon key.
- `sb_*` — Personal Access Tokens para Management API.

El kernel de El Monstruo ya usa el nuevo formato `sb_secret_*` para `SUPABASE_SERVICE_KEY`.

## 2. Decisión

### 2.1 Naming canónico

A partir de la firma de este DSC, el naming canónico para todas las env vars y referencias en código, specs, docs y bridge files es:

| Concepto | Nombre canónico | Formato esperado | Reemplaza |
|---|---|---|---|
| Service role key | `SUPABASE_SERVICE_KEY` | `sb_secret_*` (preferido) o `eyJ...` (legacy) | `SUPABASE_SERVICE_ROLE_KEY` |
| Anon publishable key | `SUPABASE_KEY` | `sb_publishable_*` (preferido) o `eyJ...` (legacy) | `SUPABASE_ANON_KEY` |
| Connection string Postgres | `SUPABASE_DB_URL` | `postgresql://...` | `DATABASE_URL` (en contexto Supabase) |
| URL del proyecto | `SUPABASE_URL` | `https://*.supabase.co` | (sin cambio) |
| Personal Access Token (Management API) | `SUPABASE_ACCESS_TOKEN` | `sbp_*` | (no cambia) |

### 2.2 Justificación

Se elige `SUPABASE_SERVICE_KEY` (sin `_ROLE`) porque:

1. **Es el naming actual de Railway** — cambiar requeriría redeploy del kernel.
2. **Es más conciso** — alinea con `SUPABASE_KEY` y `SUPABASE_URL`.
3. **El campo "role" está implícito** — toda key con privilegios elevados en Supabase ES service_role.
4. **Cowork validó** durante audit del Sprint S-002.5 que el cambio de naming a "ROLE_KEY" sería costoso e innecesario.

### 2.3 Excepciones permitidas

- En código que invoca el SDK oficial de Supabase, donde el SDK acepta `service_role` como string literal interno — sin cambio.
- En policies SQL como `auth.role() = 'service_role'` — sin cambio (es un valor de Postgres, no nombre de env var).
- En documentación histórica o postmortems anteriores a la firma de este DSC — no se requiere migración retroactiva.

## 3. Implementación

### 3.1 Cambios obligatorios (acumulables)

1. **Specs nuevos** (bridge/sprints_propuestos/, AGENTS.md, docs/) deben usar `SUPABASE_SERVICE_KEY` exclusivamente.
2. **Pre-commit linter** (Tarea 5 del Sprint S-002.6) debe rechazar archivos nuevos que contengan literal `SUPABASE_SERVICE_ROLE_KEY` salvo en bloques de "obsolete naming" o postmortems.
3. **Cuando se detecte naming antiguo** en archivos modificados durante un sprint, agregar nota en bridge: "Naming legacy detectado, no se migra retroactivamente (DSC-S-007)".

### 3.2 Cambios opcionales (futuro)

- Crear alias `SUPABASE_SERVICE_ROLE_KEY` que mapee a `SUPABASE_SERVICE_KEY` en Railway env si algún módulo de terceros lo requiere — solo bajo necesidad explícita.
- Auditoría anual de env vars Supabase para validar que solo existe un nombre por concepto.

## 4. Cumplimiento DSC

- **DSC-S-001**: Tokens nunca en código. Toda referencia es por nombre de env var.
- **DSC-S-002**: gitleaks/trufflehog continúan aplicándose. Cambio de naming no afecta scanning.
- **DSC-S-003**: Rotación TTL sin cambio.
- **DSC-S-004**: Anti-patrón `os.environ.get("SUPABASE_KEY", "eyJ...")` sigue prohibido. `require_env("SUPABASE_SERVICE_KEY")` es el patrón canónico.
- **DSC-S-005**: Cleanup default a archive sin cambio.
- **DSC-S-006**: RLS por defecto en tablas nuevas; este DSC complementa con naming canónico.
- **DSC-G-008 v2**: Cowork audita contenido — este DSC fue propuesto por Cowork tras audit del Sprint S-002.5.

## 5. Sprints relacionados

- **S-002.5** (PR #43, mergeado 2026-05-10): detectó la inconsistencia.
- **S-002.6** (este sprint): firma DSC + agrega linter pre-commit.

## 6. Firmas

- Hilo B (ejecutor): firma implícita por commit de este archivo.
- Cowork (orquestador): firma esperada en audit del PR del Sprint S-002.6.

---

**Última actualización**: 2026-05-10
**Próxima revisión**: en auditoría anual de env vars Supabase.

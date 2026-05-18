# SECURITY_SMP_CRONOS_PACK

**Versión:** 1.0
**Fecha:** 2026-05-18
**Branch:** monstruo-reality-atlas-001
**Propósito:** Validar la doctrina de seguridad (SMP, Cripta, Cronos, RLS, Secrets) contra el código real para que ChatGPT no infiera capacidades inexistentes.

---

## 1. Resumen Ejecutivo

La capa de seguridad del Monstruo está **fuerte en RLS y secrets management** pero **inexistente en SMP/Cronos a nivel de código**. Hay 14 DSCs `S-*` canonizados, 5 migraciones SQL de RLS dedicadas, 5 scripts pre-commit de validación, y `.pre-commit-config.yaml` activo. El proyecto APP_VISION v1 declara dos capítulos completos para Cronos (Cap 5) y SMP (Cap 7) más un Capítulo 17 de "Capa de Seguridad Magna" — pero el código del kernel **no contiene ninguna implementación**: `find kernel -iname "*cronos*"` → 0 hits, `grep "class Cronos\|def cronos"` → 0 hits, `grep "Sovereign Memory Protocol\|Shamir"` en código → 0 hits funcionales. La Capa de Seguridad Magna es **doctrina aspiracional**. La realidad operativa hoy es: secrets en env vars Railway, Supabase service_key con naming canónico (DSC-S-007), RLS habilitada por defecto en migraciones nuevas (DSC-S-006), pre-commit hooks que rechazan tokens hardcoded (DSC-S-002).

## 2. Doctrina de Seguridad Canonizada (DSCs S-*)

Inventario completo de la `discovery_forense/CAPILLA_DECISIONES/_GLOBAL/DSC-S-*.md`:

| DSC | Título | Estado en código |
|---|---|---|
| **S-001** | Política de credenciales | DOCTRINA + parcialmente implementado vía env vars |
| **S-002** | Pre-commit hooks obligatorios | **IMPLEMENTADO** (`.pre-commit-config.yaml` 2557 bytes activo) |
| **S-003** | Scripts/env vars sin defaults sensibles | **IMPLEMENTADO** (auditado en linter) |
| **S-004** | Antipatrón default value con secret real | DOCTRINA + check parcial en pre-commit |
| **S-005** | Default archive antes que delete | DOCTRINA aplicada en cleanup runs |
| **S-006** + **S-006 v1.1** | RLS por defecto tablas nuevas | **IMPLEMENTADO** (`scripts/_check_rls_default.py` + 5 migraciones RLS) |
| **S-007** | Naming canónico Supabase service key | DOCTRINA + parcialmente migrada |
| **S-008** | Rotación automatizada credenciales | DOCTRINA + `scripts/_check_credential_rotations.py` |
| **S-010** | Hardening operacional integrado | DOCTRINA |
| **S-012** | Anti-deriva migraciones Supabase | DOCTRINA |
| **S-013** | Scheduled tasks cleanup destructivo v1 | DOCTRINA + ejecutado |
| **S-015** | Scheduler respeta next_run de restore | DOCTRINA + implementado en scheduler |
| **S-016** | Anti-fabricación causalidad sin grep | DOCTRINA (proceso, no código) |

> Salto numérico observado: NO existen DSC-S-009, DSC-S-011, DSC-S-014. Posible deuda de canonización o numeración reservada.

## 3. RLS Real en Producción

Migraciones SQL dedicadas a RLS (`ls migrations/sql/*rls*`):

| Migración | Alcance | Estado |
|---|---|---|
| `0004_enable_rls_p0_critico.sql` | Tablas P0 críticas | aplicada |
| `0005_enable_rls_p1_embrion_stack.sql` | Stack Embrión | aplicada |
| `0007_rls_tablas_post_s002_5.sql` | Post-S002.5 | aplicada |
| `0008_rls_p2_completion.sql` | P2 completion | aplicada |
| `0011_rls_catastro_vision_generativa.sql` | Catastro **con SELECT público intencional** | aplicada |

Validación runtime (Pack 1 §6 confirma): `embrion_memoria`, `embrion_write_proposals`, `scheduled_tasks`, `run_costs`, `thoughts`, `catastro_agentes`, `guardian_audit_log`, `a2a_agents`, `rotor_activity_log` → 0 rows visibles a anon (RLS correcta). `runtime_events` → 401 (más restrictivo, gateway-level).

## 4. Secrets Management

| Vector | Estado | Evidencia |
|---|---|---|
| Pre-commit hook `_check_no_tokens.sh` | **ACTIVO** | `scripts/_check_no_tokens.sh` ejecutable |
| Pre-commit hook `_check_rls_default.py` | **ACTIVO** | rechaza CREATE TABLE sin RLS |
| Pre-commit hook `_check_credential_rotations.py` | **ACTIVO** | revisa frescura inventory |
| `.pre-commit-config.yaml` | **ACTIVO** 2557 bytes | hooks orquestados |
| `bridge/credentials_inventory.md` | **ACTIVO** | inventario de credenciales y last-rotated |
| Storage de secrets en código | **LIMPIO** (probe `grep -rE "sk-...{30,}"` en *.md/*.py/*.toml excluyendo .env.example → 0 hits) | scan en tiempo real 2026-05-18 |
| Naming `SUPABASE_SERVICE_KEY` canónico (no _ROLE) | DOCTRINA DSC-S-007 | parcial |
| Postmortem P0 2026-05-06 (credenciales en repo público) | **CERRADO** | `discovery_forense/INCIDENTES/P0_2026_05_06_credenciales_repo_publico.md` |

## 5. SMP — Sovereign Memory Protocol

**Estado: DOCTRINA SIN CÓDIGO**

| Aspecto | APP_VISION v1 | Realidad código |
|---|---|---|
| Cifrado E2E con Shamir's Secret Sharing | Cap 7 declarado | NO existe en `kernel/` |
| Recovery con Shamir | declarado | NO_SOURCE |
| Claves del usuario en Secure Enclave | declarado para iOS | NO existe |
| `kernel/smp/` o módulo equivalente | n/a | **NO EXISTE** |
| Tabla `smp_*` en Supabase | n/a | **NO existen tablas con prefijo smp_** |
| `apps/mobile/lib/core/.../smp.dart` | path declarado en Cap 1 | requiere verificación (no encontrado en grep `/v1/`) |

Búsquedas ejecutadas:

- `find kernel -iname "*smp*"` → 0 archivos.
- `grep -rE "Sovereign Memory|shamir|secret_share" --include="*.py"` → 0 hits funcionales (solo strings en docs/bridge).
- `find . -path ./node_modules -prune -o -iname "*smp*" -print` → solo refs en `bridge/`, `docs/`.

> SMP es **deuda doctrinal P0** si Alfredo quiere encriptación soberana antes de manejar datos sensibles (HealthKit, passwords, ambient audio).

## 6. Cronos — La Memoria Viaje

**Estado: DOCTRINA SIN CÓDIGO**

APP_VISION v1 Capítulo 5 (líneas 403-503) describe Cronos como capa de memoria temporal navegable con "río de Cronos" en Home, Smart Notebook activo, Convergencia Cronos como Embrión.

Búsquedas en código:

- `find kernel -iname "*cronos*"` → **0 archivos**.
- `find apps -iname "*cronos*"` → **0 archivos**.
- `grep -rE "class Cronos|def cronos|cronos_" --include="*.py" --include="*.dart"` → **0 hits**.
- `apps/mobile/lib/.../smart_notebook_service.dart` declarado en APP_VISION → no verificado pero no aparece en `grep "/v1/"` consumers.
- Embrión "Convergencia Cronos" → declarado en APP_VISION; `kernel/embriones/` tiene `brand_engine` pero no `cronos_engine`.

> Cronos es **deuda doctrinal P1**. Sin Cronos no hay diferenciador real frente a un asistente IA estándar.

## 7. Capa de Seguridad Magna (APP_VISION Cap 17)

Capítulo añadido v1.3 post-incidente P0 2026-05-06. Lo que declara vs lo que existe:

| Componente declarado | Estado |
|---|---|
| Cripta (Modo Cripta para datos ultra-sensibles) | DOCTRINA, sin código |
| Cifrado en reposo + en tránsito + en uso (TEE) | parcial — TLS sí, en-uso TEE no |
| Defense-in-depth con anomaly detection | NO_SOURCE en runtime |
| Audit trail soberano (no exportado a vendors) | parcial — guardian_audit_log existe |
| Privacy budget (DP-style ε) | NO_SOURCE |
| Confidential compute para queries sensibles | NO_SOURCE |
| Personal data sovereignty: usuario controla qué sale | NO_SOURCE |

## 8. Datos Sensibles — Política Real vs Aspiración

| Categoría dato | APP_VISION declara | Hoy en producción | Riesgo |
|---|---|---|---|
| Conversaciones chat | bajo SMP, índice en kernel | **plain text** en Supabase tabla `thoughts` (RLS sí) | P2 — RLS protege pero no E2E |
| Tokens API/keys del usuario | bajo SMP, exportable | NO se guardan keys de usuario hoy | bajo |
| Health data (HealthKit/HC) | bajo SMP, índice cifrado | **NO se ingiere** hoy | bajo (no existe el flujo) |
| Ambient audio 24/7 | bajo SMP profundo, Secure Enclave | **NO se captura** hoy | bajo (no existe) |
| Cronos (vida documentada) | índice cifrado | **NO se construye** | bajo (no existe) |
| Decisiones Embrión | guardian_audit_log + propose/approve | **runtime_events bloqueada anon (correcto)** | bajo |
| Emails / Gmail (vía MCP) | n/a | conectado vía MCP gmail | P2 — MCP corre en sandbox del usuario, no en kernel cifrado |

## 9. Pre-commit Hooks — Doctrina Aplicada en Build Time

`scripts/_check_*.{sh,py}` ejecutables hoy:

- `_check_credential_rotations.py` — bloquea commit si `credentials_inventory.md` tiene credenciales no rotadas en TTL.
- `_check_guardian_stale_audit.py` — bloquea si guardian audit está stale.
- `_check_no_tokens.sh` — regex hardcoded tokens en archivos staged.
- `_check_rls_default.py` — bloquea `CREATE TABLE` sin `ENABLE ROW LEVEL SECURITY`.
- `_check_run_872.py` — script ad-hoc para sprint específico.

`.pre-commit-config.yaml` orquesta estos hooks. Bypass solo con `--no-verify` + DSC firmado en mismo PR (regla CLAUDE Regla Dura #6).

## 10. Top 10 Hallazgos Pack 2

1. RLS está **fuerte y verificado en runtime** (5 migraciones aplicadas + 9 tablas críticas con 0 rows visibles a anon).
2. SMP es **doctrina sin código**: 0 archivos `smp*` en `kernel/`, 0 hits Shamir/Sovereign en runtime.
3. Cronos es **doctrina sin código**: 0 archivos `cronos*`, 0 funciones, 0 servicios.
4. Capa de Seguridad Magna (APP_VISION Cap 17) es 100% aspiracional. TEE / privacy budget / Cripta NO existen en código.
5. Pre-commit hooks **funcionan** y rechazan secrets / tablas sin RLS — robusto.
6. Naming `SUPABASE_SERVICE_KEY` (DSC-S-007) parcialmente migrado — buscar `SUPABASE_SERVICE_ROLE_KEY` legacy.
7. Catastro `modelos` y `eventos` son **públicas read intencional** (mig 0011) — NO confundir con leak.
8. P0 2026-05-06 (creds en repo público) cerrado, postmortem disponible. Lección aplicada en S-002, S-003, S-004.
9. `runtime_events` bloqueada gateway-level (401 anon), más restrictivo que solo RLS — buena práctica.
10. `bridge/credentials_inventory.md` existe; mantenimiento del inventario gobierna rotación.

## 11. Top 10 Riesgos Pack 2

| # | Riesgo | Severidad | Acción correctiva (no proponer aquí — solo documentar) |
|---|---|---|---|
| 1 | SMP cero código mientras APP_VISION promete features dependientes | P0 doctrinal | sprint dedicado |
| 2 | Cronos cero código mientras Daily/Cockpit lo asumen | P0 doctrinal | sprint dedicado |
| 3 | TEE / Cripta cero implementación | P1 | research + design DSC |
| 4 | Conversaciones chat plain text en `thoughts` (RLS pero no E2E) | P2 | upgrade futuro |
| 5 | DSC-S-007 naming canónico parcialmente aplicado | P2 | refactor |
| 6 | DSC-S-009/011/014 saltos numéricos sin documentar | P3 | aclarar deuda canonización |
| 7 | MCP gmail/notion etc corren con scopes amplios fuera del kernel | P2 | scope review |
| 8 | Pre-commit `--no-verify` permitido; auditar uso histórico | P3 | grep commits con bypass |
| 9 | Audit `guardian_stale_audit` puede ser bypaseado si no se ejecuta | P3 | CI gate |
| 10 | `runtime_events` bloqueado gateway-level — confirmar política consistente con otras tablas | P3 | review uniformidad |

## 12. ACCESS_BLOCKED list

- Inspección directa del Secure Enclave / TEE — NO_SOURCE.
- Logs de pre-commit bypass (`--no-verify`) histórico — requiere CI logs Railway.
- Validación cruzada del inventario `credentials_inventory.md` vs Railway env real — requiere Railway CLI.
- Auditoría de scopes MCP gmail/notion/etc — requiere conector inspection.

## 13. NO_SOURCE list

- `kernel/smp/`
- `kernel/cronos/`
- Embrión "Convergencia Cronos"
- `apps/mobile/lib/core/smp.dart` (declarado en path APP_VISION)
- `kernel/cripta/` o `kernel/security_magna/`

## 14. Qué NO inferir

- NO inferir que SMP está implementado porque APP_VISION lo describe en detalle.
- NO inferir que Cronos existe como servicio porque la app lo lista en Daily.
- NO inferir que la app tiene cifrado E2E.
- NO inferir que existe TEE / privacy budget / DP-style ε.
- NO inferir que el Modo Confidente (APP_VISION Cap 6) tiene base de código — es 100% doctrina.

## 15. Impacto sobre pericia ChatGPT

Refuerzo en módulos `kernel_a2ui_memento` (memento sí existe en código), `embriones_budget_self_verifier_write_policy` (write_policy sí, confirmar self_verifier). Penalización si ChatGPT asume SMP/Cronos/Cripta como implementados.

## 16. Preguntas para Alfredo

- **P5:** ¿SMP debe entrar a sprint inmediato o queda como deuda doctrinal explícita por N sprints?
- **P6:** ¿Cronos requiere POC mínimo o queda en backlog hasta v1.1+?
- **P7:** ¿Auditar `--no-verify` histórico en pre-commit con CI logs?
- **P8:** ¿Migración completa naming `SUPABASE_SERVICE_KEY` con DSC explícito?

---
id: manus_to_cowork_EJECUTOR_1_RIESGOS_S_CONTRATOS_001_2026_05_12
fecha: 2026-05-12
emisor: Manus Hilo Ejecutor 1 (auditor externo read-only, NO ejecutor del sprint)
receptor: Cowork T2-A + Hilo Catastro (ejecutor S-CONTRATOS-001 COMPLETO)
tipo: standby_activo_TB_lista_riesgos
prioridad: P2
spec_origen: bridge/cowork_to_manus_HILO_EJECUTOR_1_STANDBY_ACTIVO_2026_05_12.md §2 TB
spec_auditado: bridge/cowork_to_manus_HILO_CATASTRO_SPRINT_S_CONTRATOS_001_T3_T4_T6_KICKOFF_2026_05_12.md (post-OVERRIDE COMPLETO T1-T6, commit 59adf28)
metodo: lectura cruzada del kickoff Catastro + inventario filesystem read-only previo al stash + recuerdo del trabajo ya ejecutado en mi branch revocada
---

# Riesgos arquitectónicos S-CONTRATOS-001 — auditoría externa Ejecutor 1

> **Disclosure obligatorio:** ANTES de que el split fuera revocado, alcancé a producir trabajo verde local de T1+T2+T5 en mi branch `sprint/s-contratos-001-completo-2026-05-12` (no pusheada). Eso me da **ventaja informativa real** sobre los riesgos T1, T2 y T5: vi cuáles son los gotchas reales, no los teóricos. Esa ventaja la vuelco aquí en §1 y §6 como **asset disponible** para Catastro.

---

## §1 Riesgo por tarea T1-T6 (1 línea cada uno, binario)

| Tarea | Riesgo principal | Gravedad | Origen del riesgo |
|---|---|---|---|
| **T1** decorator | El kernel YA tiene `kernel/validation/perplexity_decorator.py` implementado (sync, no async, con `claim_type`+TTL en lugar de `claim_id`+`max_age_minutes`). El spec asume archivo nuevo en `kernel/security/validation.py` que no es la realidad. | **ALTA** (puede generar duplicación si Catastro no inventaria primero) | Verifiqué filesystem el 12-may 06:30 UTC durante mi pre-flight |
| **T2** migration 0024 | El storage Supabase actual (`kernel/validation/_storage_supabase.py`) ya escribe a tabla `validation_log` que NO existe en migraciones — gap silencioso. La nueva tabla del spec usa `claim_id` + `max_age_minutes`, pero el storage real escribe `claim_type` + `claim_fingerprint` + `timestamp_unix` + `ttl_seconds`. | **ALTA** (schema mismatch entre código existente y spec) | Misma fuente |
| **T3** GitHub Action | El parser regex para extraer URLs/paths de la sección `## E2E Evidence` puede tener falsos negativos con markdown rare-pero-valido (ej: links inline tipo `[text](url)` vs `<url>` vs raw URL). Requiere fuzz testing. | MEDIA | Patrón conocido de check linters |
| **T4** constraint anti-rotation | El kickoff ya advierte el bug `DATE(TIMESTAMPTZ)` IMMUTABLE post-V25 mig 0020 — el risk está mitigado en el propio spec. **Riesgo residual:** si tabla `credential_rotations` ya existe SIN columna `rotated_at_date` STORED, `ALTER TABLE` la agrega pero requiere backfill seguro para no romper writes en vuelo. | MEDIA-BAJA | Spec ya canoniza el fix |
| **T5** pre-commit hook | El linter aplicado contra los DSCs reales del repo detecta **30 violaciones existentes** (deuda histórica). El hook NO bloquea esa deuda hasta que un commit toque uno de esos archivos, pero al primero que los toque le va a fallar el commit "por sorpresa". | **ALTA** (UX para devs) | Smoke test que corrí localmente contra `discovery_forense/CAPILLA_DECISIONES/_GLOBAL/*.md` |
| **T6** cleanup specs legacy | Si Catastro intenta marcar como "aspiracional" un DSC que NO debería estar aspiracional (porque su artefacto sí existe pero está disperso en formato no-canónico), generaría regresión documental. Requiere criterio fino + revisión humana de Cowork. | MEDIA | Análisis del scope T6 |

---

## §2 Riesgos cross-tarea (dependencias ocultas detectadas)

1. **T1 → T2 acoplamiento de schema:** el decorator T1 consume la tabla T2. Si el spec define schema T2 con `claim_id TEXT` pero el decorator real usa `claim_fingerprint` calculado por hash, hay **mismatch de columna**. Catastro debe **decidir explícitamente** si:
   - (a) Refactoriza decorator para usar `claim_id` literal (rompe `kernel/embrion_loop.py` y otros call-sites que pasan `claim_type`).
   - (b) Refactoriza schema T2 para alinear con `claim_fingerprint` (cambia el spec firmado).
   - (c) Mantiene ambos: `claim_id` lógico + `claim_fingerprint` derivado (más seguro pero más complejidad).

2. **T5 → T6 acoplamiento operativo:** si T5 entra a `main` ANTES de T6, el primer commit que toque cualquier DSC legacy será rechazado por el hook. Riesgo de bloqueo en cascada en otros hilos. Catastro debe **mergear T5 y T6 juntos en el mismo PR** o agregar bypass temporal documentado.

3. **T4 → T8 (futuro):** el constraint UNIQUE rota el plano de identidad (DSC-G-011). Si hay scheduled task que rota credenciales 2x al día (window de pre-rotation testing), el constraint falla por diseño. **Hipótesis no verificada:** revisar `scheduled_tasks/` por workflows de rotación pre-existentes que asuman comportamiento sin constraint.

4. **T1+T2+T3 con sprint 90 NPM Stripe:** sprint 90 será TypeScript con su propio decorator de validación cliente. Si el contrato V-001 servidor cambia de `claim_id` a `claim_fingerprint`, el TS frontend tendrá que mirror eso. **Recomendación:** documentar el contrato V-001 wire-format en sección dedicada del spec firmado para que sprint 90 lo respete sin revisar código kernel.

---

## §3 Riesgo con sprints ya mergeados

1. **DSC-V-001 vs Brand Engine canary (Sprint Brand Engine):**
   - Brand Engine corre en mode `shadow` (Railway) y eventualmente activará validación de claims publicitarios.
   - Si Brand Engine usa el decorator pre-existente `requires_perplexity_validation` con la firma actual (`claim_type`+TTL), y T1 lo refactoriza a `claim_id`+`max_age_minutes`, **Brand Engine se rompe silenciosamente** al activar canary.
   - **Mitigación obligatoria:** wrapper retrocompat o shim de signature, validado contra Brand Engine en CI antes de merge S-CONTRATOS-001.

2. **DSC-G-017 vs DSCs futuros:**
   - El hook T5 enforza el contrato sobre cada DSC nuevo o modificado.
   - El propio Cowork escribe DSCs cuando canoniza decisiones en chat → cada DSC nuevo de Cowork será bloqueado por el hook si no incluye `## Contrato ejecutable`.
   - Si la decisión es genuinamente aspiracional (pendiente de implementación), Cowork debe escribir explícitamente `**Estado:** Aspiracional` con razón. Esto es **cambio de habit** que requiere comunicación post-merge.

3. **DSC-G-010 (E2E evidence) vs PRs en curso:**
   - PRs ya abiertos sin sección `## E2E Evidence` (incluyendo mi PR #114 si aplica) pasarán por el nuevo gate.
   - **Riesgo:** PR #114 fue redactado antes de DSC-G-010. Si el gate se aplica retroactivamente y PR #114 no tiene sección, falla CI.
   - **Mitigación:** chequear `PR.body` de PRs abiertos al merge de S-CONTRATOS-001 + agregar sección a los que falten ANTES del merge T3.

4. **DSC-G-011 (UNIQUE rotation_per_day) vs scheduled task rotation existente:**
   - Sprint S-002.5 introdujo workflow `rls-audit-weekly.yml` y otros checks de credenciales.
   - Si alguno rota credenciales como parte de testing automatizado en window <24h, el UNIQUE rompe el job.
   - **Verificar:** `grep -rn "credential_rotations\|INSERT INTO.*rotated_at" scripts/ .github/workflows/` antes de aplicar 0025.

5. **Migration 0024 vs ROTOR-001 (PR #113 cerrado 6/6 verde Hilo Ejecutor 2):**
   - ROTOR-001 introdujo cambios en `kernel/embrion_*` que pueden tocar tabla `validation_log` (storage compartido).
   - Si la tabla esperada por ROTOR-001 difiere del schema 0024, hay regresión semántica.
   - **Verificar:** `kernel/rotor/` referencias a `validation_log` antes de aplicar 0024.

---

## §4 Recomendaciones específicas para Catastro (auditor externo)

1. **Pre-flight obligatorio expandido (antes de tocar T1):**
   ```bash
   ls kernel/validation/  # confirmá implementación pre-existente
   cat kernel/validation/__init__.py
   grep -rn "validation_log\|requires_perplexity_validation" kernel/ tests/
   grep -rn "validation_log" kernel/rotor/  # cross-check con ROTOR-001
   psql "$SUPABASE_DB_URL" -c "\d validation_log"  # ver si existe
   ```
   Si encontrás implementación existente: **inventariá primero, refactorizá después**. NO crees archivos paralelos.

2. **T1 pragmatic decision tree:**
   - Si el decorator existente cubre el contrato del spec → **conserválo**, agregá tests faltantes (3 mínimos del spec) y documentá que el archivo canónico es `kernel/validation/perplexity_decorator.py` (NO `kernel/security/validation.py`). Update spec.
   - Si NO cubre → refactor con shim retrocompat documentado.

3. **T2 + T1 conjunto:**
   - Decidí schema PRIMERO (`claim_id` o `claim_fingerprint`).
   - Aplicá migration en una sola PR con el decorator alineado.
   - **No hagas merge parcial de T2 sin T1** (riesgo de schema huérfano).

4. **T5 documentación crítica:**
   - El header del script `_check_dsc_contracts.py` debe explicar **claramente** que la deuda histórica de DSCs pre-existentes solo bloquea cuando son modificados.
   - Agregá un audit standalone (`tools/audit_dsc_contracts.py --all`) que reporta deuda histórica completa SIN bloquear commits — útil para sprint dedicado a backfill posterior.

5. **T6 criterio binario:**
   - Para cada DSC legacy, aplicá árbol decisión:
     - ¿Existe artefacto ejecutable identificable? → agregar sección `## Contrato ejecutable` con path
     - ¿No existe? → marcar `**Estado:** Aspiracional` con razón explícita y referencia al sprint que lo ejecutará
     - ¿Es ambiguo? → consultar Cowork antes de canonizar

6. **PR único vs PRs múltiples:**
   - Recomiendo PR único `[S-CONTRATOS-001]` con T1+T2+T3+T4+T5+T6 juntos para evitar el problema de T5-bloquea-T6.
   - Si CI grande, considerá split T1+T2 (decorator + schema) en PR-A y T3+T4+T5+T6 (gates + cleanup) en PR-B con dependencia documentada.

---

## §5 Hallazgos que NO puedo verificar sin tocar código (declaración honesta de límites)

1. **Estado actual de Brand Engine en Railway:** no puedo verificar `BRAND_ENGINE_ENABLED` ni `BRAND_ENGINE_MODE` desde standby read-only. Necesito que Alfredo o Cowork confirmen si Brand Engine ya consume el decorator existente.

2. **Schema real de `validation_log` en producción Supabase:** mi inventario es del filesystem local. Si producción tiene tabla con schema legacy distinto al esperado, T2 puede fallar al apply. Catastro debe correr `\d validation_log` en producción ANTES de codear T2.

3. **Scheduled tasks que rotan credenciales:** declaré la hipótesis en §3.4 pero no la verifiqué exhaustivamente. Catastro debería hacer `grep -rn "credential_rotations\|INSERT INTO.*rotated_at" scripts/ .github/workflows/` ANTES de aplicar 0025.

4. **Estado real del PR #110 Perplexity (`kernel/cowork_runtime/`):** no puedo verificar si introduce dependencias nuevas con `validation_log`. Cowork debe cross-check.

5. **Convergencia semántica `claim_id` vs `claim_fingerprint`:** decidir esto requiere conocer **cómo otros consumers (Brand Engine, scheduled tasks, kernel modules) llaman al decorator**. Yo solo vi 3-4 call sites en mi inventario rápido.

6. **Test exhaustivo del hook T5 contra todos los DSCs reales:** corrí el smoke contra los 31 DSCs de `_GLOBAL/` pero NO contra DSCs en subcarpetas (`PROYECTOS/*/CAPILLA_DECISIONES/`). Catastro debe correr el linter contra `discovery_forense/CAPILLA_DECISIONES/**/*.md` recursivo.

7. **Latencia de la GitHub Action T3 vs PRs ya abiertos:** GitHub no aplica retro-action a PRs abiertos por defecto, pero algunos PRs requieren re-run check al mergear. Catastro debe verificar comportamiento esperado.

---

## §6 ASSET DISPONIBLE — trabajo verde local del split cancelado

Antes de la cancelación del split alcancé a producir lo siguiente, **stasheado localmente** (NO pusheado a remoto). Si Catastro lo quiere reutilizar, le ahorra ~30-40 min:

| Artefacto | Ubicación stash | Estado |
|---|---|---|
| `migrations/sql/0024_validation_log.sql` | stash@{0} | Schema canónico DSC-V-001 con `claim_type`/`claim_fingerprint`/`timestamp_unix`/`ttl_seconds` (alineado con storage existente, NO con spec literal `claim_id`+`max_age_minutes`). RLS service_role_only desde nacimiento. Idempotente. |
| `tools/_check_dsc_contracts.py` (T5 linter) | stash@{0} | 165 LOC, parser robusto frontmatter YAML + Markdown inline, 10 tests verde. Smoke contra DSCs reales detecta 30 violaciones históricas. |
| `tests/test_check_dsc_contracts.py` | stash@{0} | 10 tests cubren: firme con contrato OK, aspiracional sin contrato OK, firme sin contrato falla, archivo no-DSC skip, contrato vacío falla, sin estado falla, lista vacía OK, path fuera CAPILLA OK, mixed pass+fail = exit 1, formato Markdown inline reconocido. |
| `tests/test_validation_decorator.py` | stash@{0} | 8 tests cubren los 3 casos del spec (bloquea sin validation, pasa con reciente, rechaza expirada) + 5 hardening (fingerprint determinístico, metadata exposed, find_latest devuelve None, JSONL serializable, roundtrip record/recover). 8/8 verde local. |
| `.pre-commit-config.yaml` (edit) | stash@{0} | Hook `dsc-contract-check` registrado correctamente con `files: ^discovery_forense/CAPILLA_DECISIONES/.*\.md$`. |

**Cómo reutilizar (opcional para Catastro):**
```bash
# En MI working tree, no en el de Catastro:
git stash list  # buscar stash con label "S-CONTRATOS-001-T1+T2+T5-trabajo-listo-NO-PUSHEAR-split-cancelado-2026-05-12"
git stash show -p stash@{N}  # inspeccionar diff
git stash show stash@{N} --name-only  # solo lista de archivos
```

**Nota crítica:** mi stash también capturó **3 archivos de Catastro que estaban untracked en mi working tree** (cohabitación cross-hilo no aislada): `.github/workflows/e2e-evidence-required.yml`, `migrations/sql/0025_anti_rotation_loop.sql`, `scripts/_apply_and_smoke_0025_anti_rotation_loop.py`. Catastro **YA tiene esos en su propio working tree o stash** (los creó él), pero confirma esto antes de aplicar mi stash, sino podés sobrescribir trabajo más reciente suyo.

**Recomendación:** Catastro inspecciona mi stash, decide qué reutilizar (probablemente migration 0024 + linter T5 + tests), y rechaza lo que conflictúe con su trabajo en curso. Si decide ignorarlo todo, dropeo el stash al cierre del sprint.

---

## §7 Cierre de la auditoría externa

- **Riesgo agregado total:** MEDIO-ALTO, principalmente por T1+T2 acoplamiento de schema y T5 deuda histórica.
- **Mitigaciones críticas obligatorias antes de codear:**
  1. Pre-flight expandido §4.1
  2. Decisión schema unificada `claim_id` vs `claim_fingerprint` con cross-check Brand Engine
  3. PR único o split T1+T2 // T5+T6 con dependencia clara
  4. Audit standalone separado del hook bloqueante
- **Asset disponible:** mi trabajo stashed en §6 puede acelerar T1+T2+T5 si Catastro lo audita y reutiliza.
- **Limitaciones de mi auditoría:** §5 enumera exactamente lo que NO pude verificar desde standby read-only.

Esta auditoría es **opinión de auditor externo** — la decisión final de cómo ejecutar S-CONTRATOS-001 corresponde a Catastro como ejecutor, con sign-off Cowork T2-A según regla §6 del kickoff.

**Firma:** Manus Hilo Ejecutor 1, 2026-05-12 — STANDBY ACTIVO TB producido (read-only, cero código tocado).

# B8-E1 — MAGNA ACTION TAXONOMY (DRAFT T1-PENDING)

**Status:** DRAFT evidence pack — pendiente firma magna T1 verbatim.
**Autor:** Manus E2 (autor NO-Cowork — propone, NO firma).
**Fuente normativa:** B6_B12_DESIGN_CLOSURE_PACK_v0_2.md §4.2 (PASS criterio B8.1 v0.2 ampliado).
**Spec target:** B8 local_unreachable policy = `DISABLED_FOR_MAGNA_ACTIONS`.
**Versión:** 1.0 DRAFT.
**Fecha propuesta:** 2026-05-20.
**Próxima firma esperada:** T1 (Alfredo Góngora) magna verbatim.

---

## §1 Definición verbatim de "acción magna"

Una **acción magna** es cualquier operación cuya ejecución, si ocurre bajo `local_unreachable == true` (kill switch local no validable), produce un riesgo binario inaceptable de pérdida de soberanía operativa, integridad doctrinal, integridad criptográfica, o exposición externa irreversible. La política runtime B8.2 (`DISABLED_FOR_MAGNA_ACTIONS`) bloquea TODA acción de esta lista cuando el kill switch no es legible o validable.

La taxonomía es **cerrada y enumerada**. No admite cláusulas abiertas tipo "etcétera", "acciones similares", o categorías por extensión semántica. Toda categoría futura requiere amendment formal (ver `B8_MAGNA_TAXONOMY_AMENDMENT_PROCEDURE.md`).

## §2 Lista taxonómica cerrada (a)-(m)

Esta lista es la **fuente única de verdad** sobre qué constituye acción magna en el runtime de El Monstruo. Cualquier mismatch entre esta lista y el set hardcodeado en runtime ⇒ FAIL test B8.5(d).

### §2.1 Categoría (a) — merge a `main`

**Definición:** cualquier merge commit que altere el HEAD de la rama `main` del repositorio `el-monstruo` o de cualquier repo bajo control de T1.
**Acciones cubiertas:** `git merge --no-ff` a main, merge vía PR de GitHub, fast-forward a main, force-push que avance HEAD de main.
**Justificación:** main constituye el snapshot canónico del sistema; merge sin kill switch validable rompe el invariante de soberanía Sprint 27.

### §2.2 Categoría (b) — apply migration de Supabase production

**Definición:** ejecución de cualquier sentencia DDL (CREATE/ALTER/DROP TABLE, CREATE/DROP INDEX, ALTER COLUMN, ALTER POLICY, ALTER PUBLICATION) sobre el proyecto Supabase production identificado por T1.
**Acciones cubiertas:** `supabase migration up`, `psql` directo a production, MCP supabase con statements DDL, scripts CI/CD que apliquen migrations.
**Justificación:** schema de production es estado autoritativo; migration sin kill switch validable puede introducir drift irrecuperable.

### §2.3 Categoría (c) — canonización (firma magna T1)

**Definición:** acción que registra firma magna T1 sobre cualquier artefacto del sistema (spec, evidence pack, config, key rotation, taxonomy amendment).
**Acciones cubiertas:** commit con tag `[T1-MAGNA]`, escritura a `bridge/canon/`, ejecución del wrapper `manus-config canon-sign`, push a branches con prefix `*-canon-*`.
**Justificación:** firma magna constituye el acto soberano de mayor peso; ejecutarla sin kill switch validable rompe garantías de no-repudio.

### §2.4 Categoría (d) — write a tablas RLS-protegidas

**Definición:** INSERT, UPDATE, o DELETE sobre cualquier tabla con Row Level Security (RLS) habilitado y policy explícita en Supabase production.
**Tablas cubiertas (lista no exhaustiva, pero policy aplica a TODA tabla con RLS activo):** `audit_log_immutable`, `dory_cure_state`, `monstruo_state`, cualquier tabla con `ALTER TABLE … ENABLE ROW LEVEL SECURITY`.
**Acciones cubiertas:** statements SQL directos, llamadas vía supabase-js client, llamadas vía MCP supabase, escritura via Edge Functions.
**Justificación:** RLS es el mecanismo de aislamiento de soberanía a nivel datos; bypass sin kill switch validable rompe el modelo de seguridad.

### §2.5 Categoría (e) — emit hacia humano externo

**Definición:** cualquier output del sistema dirigido a un humano que NO sea T1 ni Cowork ni Sabio operando en flujo controlado.
**Acciones cubiertas:** webhooks cliente-facing (Stripe customer_created, Mailgun delivered, Twilio SMS), notificaciones a usuarios finales (push notifications, email transaccional, in-app banner), posts a redes sociales (Twitter/X, Instagram, LinkedIn vía API), llamadas a Telegram bot externos, mensajes WhatsApp Business API.
**Justificación:** emisión externa sin kill switch validable puede causar daño reputacional o legal irrecuperable; la regla "primum non nocere" aplica.

### §2.6 Categoría (f) — escritura a `.monstruo/kill_switches/`

**Definición:** cualquier write, append, truncate, o delete de archivos bajo `~/.monstruo/kill_switches/` o equivalente cross-platform.
**Acciones cubiertas:** `echo > DORY_CURE_DISABLED`, `rm DORY_CURE_DISABLED`, modificación del contenido de archivos kill switch, modificación de la firma ed25519 asociada a un kill switch.
**Justificación:** recursión binaria: el kill switch que está siendo verificado no puede modificarse sin antes verificar el kill switch; permitir esto rompe la invariante.

### §2.7 Categoría (g) — cambio de configuración de VERIFICADOR-001

**Definición:** modificación de cualquier parámetro de configuración del componente runtime VERIFICADOR-001 (ver B9 closure pack v0.2).
**Acciones cubiertas:** modificar `verifier.toml`, modificar variables de entorno `VERIFIER_*`, recargar config en runtime via signal o IPC, swap de binario VERIFICADOR-001.
**Justificación:** VERIFICADOR-001 es la autoridad criptográfica del sistema; cambiar su config sin kill switch validable rompe la cadena de confianza.

### §2.8 Categoría (h) — rotación de claves B6 / fixtures B7

**Definición:** generación, rotación, retirement, revocation, o substitución de cualquier clave ed25519 cubierta por B6 o cualquier fixture oculto cubierto por B7.
**Acciones cubiertas:** `signify -G`, `minisign -G`, `ssh-keygen -t ed25519`, escritura a custodios B7 (T1 escrow, HSM/KMS, cuenta cloud privada controlada por T1, repos privados cifrados, humano delegado), modificación del manifest de claves activas, revocation list update.
**Justificación:** material criptográfico es la base de no-repudio; rotación sin kill switch validable puede introducir claves comprometidas en el set autoritativo.

### §2.9 Categoría (i) — deploy a producción

**Definición:** despliegue de cualquier código o configuración a un entorno cliente-facing.
**Acciones cubiertas:** `railway up` a Railway production, `gcloud run deploy` a Cloud Run prod, `vercel --prod`, `flyctl deploy` a Fly production, `kubectl apply` a cluster prod, `terraform apply` a state file de prod, push a branches que disparen workflows de deploy a prod (incluso sin merge).
**Justificación:** deploy a prod sin kill switch validable puede empujar código no validado a usuarios reales.

### §2.10 Categoría (j) — DELETE en Supabase production

**Definición:** cualquier escritura destructiva sobre cualquier tabla de Supabase production (incluso tablas no-RLS).
**Acciones cubiertas:** `DROP TABLE`, `TRUNCATE`, `DELETE FROM` (con o sin WHERE), `DROP DATABASE`, `DROP SCHEMA`, `DROP INDEX` (porque puede romper queries cliente-facing en cascada).
**Justificación:** acciones destructivas sin kill switch validable son irrecuperables en ausencia de PITR (point-in-time recovery) garantizado.

### §2.11 Categoría (k) — modificación de archivos doctrinales

**Definición:** edit, append, truncate, o delete de archivos del corpus doctrinal de El Monstruo.
**Archivos cubiertos:** `AGENTS.md`, `CLAUDE.md`, `MEMENTO.md`, cualquier archivo bajo `bridge/spec/` que tenga firma magna T1 registrada en algún audit log, archivos `.monstruo/canon/*.md`, archivos con tag `[CANON]` en frontmatter.
**Acciones cubiertas:** edit via tool, edit via shell (sed, awk, vim), edit via aplicación nativa, modificación vía MCP, generación automática de docs que sobrescriba doctrinales.
**Justificación:** corpus doctrinal es el contrato vivo entre T1 y los agentes; modificación sin kill switch validable rompe el contrato.

### §2.12 Categoría (l) — escritura en branch protegida de GitHub

**Definición:** push de commits a cualquier rama remota cubierta por branch protection rules de GitHub.
**Ramas cubiertas (no exhaustivas, pero la regla aplica a TODA rama con BPR activa):** `main`, ramas con prefix `*-canon-*`, ramas con tag de spec, ramas listadas en `.github/CODEOWNERS` con required review, ramas con required status checks.
**Acciones cubiertas:** `git push origin <branch>`, push via GitHub MCP, push via gh CLI, automation que dispare push.
**Justificación:** BPR es la salvaguarda de gobernanza a nivel git; bypass sin kill switch validable rompe la auditabilidad del repo.

### §2.13 Categoría (m) — acciones de billing/costos

**Definición:** cualquier operación que comprometa fondos de T1 sin autorización explícita del mismo evento.
**Acciones cubiertas:** creación o modificación de API keys de proveedores pagados (Anthropic, OpenAI, Google, Vercel, Railway, Supabase, etc.), modificación de cuotas/quotas de servicios cloud, autorización de gastos > $0 USD sin autorización T1 explícita en el flujo, modificación de payment methods, cancelación de subscripciones que afecten servicios activos, ejecución de jobs de cómputo facturables (training runs, GPU rentals, Bedrock invocations) sin autorización T1.
**Umbral binario:** $0 USD (cualquier gasto sin autorización T1 explícita es magna).
**Justificación:** costos sin kill switch validable pueden producir bills sorpresa irrecuperables.

## §3 Política runtime asociada

### §3.1 PASS B8.2 — DISABLED_FOR_MAGNA_ACTIONS

Si `local_unreachable == true` AND `action ∈ acción_magna_set` (definido por esta taxonomía cerrada (a)-(m)):

- Acción **rechazada** verbatim antes de ejecución.
- Evento `MAGNA_ACTION_BLOCKED_LOCAL_UNREACHABLE` emitido al bridge con `run_id`, categoría taxonómica matched, timestamp UTC, rationale verbatim, y stack trace.
- NO retry automático. Retry solo bajo restore manual del kill switch local + reintento explícito por operador.

### §3.2 PASS B8.3 — ENABLED_WITH_DEGRADED_WARN

Si `local_unreachable == true` AND `action ∉ acción_magna_set`:

- Acción **permitida** con banner de warning visible al operador.
- Evento `LOCAL_UNREACHABLE_DEGRADED` emitido al bridge.
- NO se promueve a magna por extensión semántica; solo categorías textualmente listadas (a)-(m) son magnas.

## §4 Procedimiento de matching binario

El runtime aplica matching **estricto y binario** entre la acción candidata y la lista (a)-(m). Reglas:

1. Cada categoría (a)-(m) corresponde a un **predicado runtime** explícito en `acción_magna_set`. Ver `B8_local_unreachable_policy.mmd` para el flujo de decisión.
2. Si una acción candidata cae bajo dos o más categorías, **gana magna** (regla más restrictiva).
3. Si una acción candidata NO cae bajo ninguna de las 13 categorías, es no-magna por defecto.
4. NO se aplica fuzzy matching, NO se aplica heurística semántica, NO se aplica generalización por similitud.
5. Drift entre esta taxonomía spec y el set hardcodeado en runtime ⇒ FAIL test B8.5(d).

## §5 Matriz de evidencia y auditoría

| Categoría | Productor evidencia | Auditor evidencia |
|-----------|---------------------|-------------------|
| (a)-(m) lista cerrada | Manus E2 propone, T1 firma magna | Sabio externo + T1 conjuntamente |

## §6 No-go binarios sobre esta taxonomía

| # | No-go | Status |
|---|-------|--------|
| 1 | NO modificación por DELTA o por Cowork sin firma magna T1 | ✅ |
| 2 | NO listas abiertas, ejemplificativas, o con cláusula "etcétera" | ✅ |
| 3 | NO `ENABLED_WITH_DEGRADED_WARN` como default para acciones magnas | ✅ |
| 4 | NO override silencioso por operador | ✅ |
| 5 | NO menos de 13 categorías (a)-(m) | ✅ (esta lista contiene 13 categorías exactas) |
| 6 | NO matching por extensión semántica o fuzzy | ✅ |
| 7 | NO promoción de no-magna a magna sin amendment formal | ✅ |

## §7 Decisión T1 requerida

T1 firma magna verbatim sobre esta lista para:

1. Aprobación verbatim de las 13 categorías (a)-(m) tal como están redactadas.
2. Solicitud de modificación o exclusión justificada de cualquier categoría (la justificación verbatim queda en este archivo en sección §8 NUEVA CREADA POST FIRMA).
3. Aprobación del umbral binario $0 USD para categoría (m).
4. Aprobación de la regla "gana magna" en colisión multi-categoría.
5. Aprobación verbatim del procedimiento de amendment (`B8_MAGNA_TAXONOMY_AMENDMENT_PROCEDURE.md`).

## §8 Estado binario post-firma esperado

Tras firma magna T1 verbatim sobre este archivo:

| Variable | Valor esperado |
|----------|----------------|
| B8-E1 status | `SIGNED_MAGNA_T1` |
| B8 gate status | TRANSICIÓN hacia `EVIDENCE_DESIGNED_T1_PENDING` ⇒ `EVIDENCE_PARTIAL_PENDING_E2_E3_E4` (E1 firmado, faltan E2/E3/E4 firma) |
| Versión spec | bump a `1.0.0-magna` |

## §9 Caveat magno F16 estructural Opus 4.7

Esta taxonomía la propuso un autor NO-Cowork (Manus E2). La firma magna T1 sobre este archivo NO equivale a decisión doctrinal de integración del pack B8 en v1.1.1, v2.0 RE-FUNDADO, o v3.0 sintetizada. La integración doctrinal sigue siendo decisión binaria T1 fuera de mi scope.

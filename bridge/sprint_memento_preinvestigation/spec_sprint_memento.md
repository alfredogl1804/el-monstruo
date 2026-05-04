# Sprint Memento — Capa Memoria Soberana v1.0 · Pre-investigación

> **Autor:** Cowork (Hilo B — arquitecto)
> **Fecha:** 2026-05-04
> **Estado:** Pre-investigación arquitectónica · pendiente de aprobación de Alfredo
> **Sprint propuesto:** Sprint 88 (después de cierre Sprint 86 Catastro + Sprint 87 Stripe Pagos)
> **Alternativa:** Sprint puente entre 86 y 87 si Alfredo prioriza fundamento sobre monetización

---

## Contexto

El 2026-05-04 ocurrió el incidente "Falso Positivo TiDB": el Hilo Manus ticketlike reportó rotación de password productivo cuando en realidad había usado credenciales de un cluster fantasma (`gateway01`) heredadas de su propio contexto compactado, sin haber leído el `credentials.md` del skill como pre-flight. Tres horas de investigación forense terminaron confirmando que **nadie había rotado nada** — el incidente fue causado por amnesia anterógrada estructural del agente ejecutivo.

Ese incidente no es un caso aislado. Es la manifestación más reciente de un patrón histórico:

- 19 PATs GitHub generados duplicadamente por hilos Manus que no recordaban tokens previos (Olas 1-2 de rotación de credenciales)
- ~400,000 créditos Manus consumidos en setup inicial de ticketlike.mx por re-trabajo de hilos amnésicos
- Incontables casos menores de re-explicación de proyecto, re-derivación de credenciales, re-decisión de arquitectura ya decidida

El patrón se llama informalmente "Síndrome Dory" (referencia a la pez con amnesia de "Buscando a Nemo") o "Protocolo Memento" (referencia al protagonista de Memento que se tatúa instrucciones críticas para sobrevivir su propia amnesia anterógrada).

El 2026-05-04 también introdujimos en `docs/EL_MONSTRUO_14_OBJETIVOS_MAESTROS.md` v3.0 el **Objetivo #15 — Memoria Soberana** y la **Capa 8 — Capa Memento** del Objetivo #9 (Transversalidad). Sprint Memento es la primera implementación concreta de esa Capa 8.

## Objetivo del Sprint

Convertir el folklore informal anti-Síndrome-Dory que ya opera disperso en hilos Manus (CLAUDE.md, AGENTS.md, bridge files, skills/*/references/credentials.md) en **infraestructura formal del kernel** con contratos auditables.

Al cierre del Sprint Memento, cualquier hilo Manus que opere contra recursos productivos del ecosistema del Monstruo (cluster TiDB de ticketlike, Railway env vars, Stripe live, etc.) debe haber pasado por al menos un endpoint del kernel que valide su contexto operativo contra fuentes de verdad persistentes — bajo riesgo de no poder operar si no lo hace.

## Decisiones arquitectónicas firmes

### Decisión 1 — Capa Memento vive dentro del kernel del Monstruo

**Voto Cowork:** Capa Memento se implementa como módulo del kernel (`kernel/memento/`), expuesto via endpoints HTTP que cualquier hilo externo puede llamar.

Razones:
- Pone al Monstruo como gatekeeper estructural de la memoria operativa (refuerza Objetivo #15 directamente)
- Centraliza la lógica de validación de contexto en un lugar versionado y auditado
- Permite que en el futuro otros agentes ejecutivos (no solo Manus) usen la misma infraestructura
- Coherente con la arquitectura existente del kernel (FastAPI + LangGraph + endpoints `/v1/*`)

### Decisión 2 — Pre-flight obligatorio se ejecuta en el cliente, validación en el servidor

**Voto Cowork:** El hilo Manus es responsable de leer su fuente de verdad antes de actuar (cliente). El kernel es responsable de validar que el contexto que el hilo declaró usar coincide con la fuente de verdad real (servidor).

Razones:
- No queremos que cada operación productiva pase 100% por el kernel (aumenta latencia + acoplamiento)
- Pero sí queremos que las operaciones críticas (rotación de credenciales, cambios a recursos productivos, ejecución de pagos en producción) tengan validación obligatoria en el kernel
- Modelo "trust-but-verify": el hilo declara su contexto, el kernel verifica selectivamente

### Decisión 3 — Lista de "operaciones críticas" es configurable y crece con el tiempo

**Voto Cowork:** Definir un catálogo inicial de operaciones críticas en `kernel/memento/critical_operations.yaml`, expandible.

Catálogo inicial (v1.0):

```yaml
critical_operations:
  - name: rotate_credential
    triggers: [tidb_password, stripe_api_key, railway_token, github_pat, jwt_secret]
    requires_validation: true
    requires_confirmation: cowork_signature + alfredo_chat_ok
  
  - name: sql_against_production
    triggers: [host_matches_production_pattern, user_has_admin_role]
    requires_validation: true
    requires_confirmation: pre_flight_credentials_md
  
  - name: deploy_to_production
    triggers: [target_env=production, includes_db_migration]
    requires_validation: true
    requires_confirmation: pre_flight_validation_endpoint
  
  - name: financial_transaction
    triggers: [stripe_charge_live, payout_creation]
    requires_validation: true
    requires_confirmation: alfredo_chat_ok + amount_threshold
```

### Decisión 4 — Endpoint principal: `POST /v1/memento/validate`

**Voto Cowork:** Un solo endpoint principal que recibe contexto operativo del hilo y responde con validación + (si discrepa) la fuente de verdad fresca.

Schema de request:

```json
{
  "hilo_id": "hilo_manus_ticketlike",
  "operation": "sql_against_production",
  "context_used": {
    "host": "gateway05.us-east-1.prod.aws.tidbcloud.com",
    "user": "37Hy7adB53QmFW4.root",
    "db": "R5HMD5sAyPAWW34dhuZc9u",
    "credential_source": "skills/ticketlike-ops/references/credentials.md",
    "credential_hash_first_8": "4N6caSwp"
  },
  "intent_summary": "Run E2E test to verify cluster connection post Stripe rotation"
}
```

Schema de response (caso OK):

```json
{
  "validation_status": "ok",
  "context_freshness_seconds": 142,
  "proceed": true,
  "validation_id": "mv_2026-05-04T18:30:42_a1b2c3"
}
```

Schema de response (caso DISCREPANCIA):

```json
{
  "validation_status": "discrepancy_detected",
  "discrepancy": {
    "field": "host",
    "context_used": "gateway01.us-east-1.prod.aws.tidbcloud.com",
    "source_of_truth": "gateway05.us-east-1.prod.aws.tidbcloud.com",
    "source": "skills/ticketlike-ops/references/credentials.md",
    "source_last_updated": "2026-05-04T05:04:19Z"
  },
  "proceed": false,
  "remediation": "Re-read credentials.md and retry with fresh credentials. Do NOT use context from compacted memory."
}
```

### Decisión 5 — Logging y observabilidad obligatorios

**Voto Cowork:** Cada call a `/v1/memento/validate` se persiste en tabla nueva `memento_validations` de Supabase con timestamp, hilo_id, operation, context_used, validation_status, discrepancy_detected (boolean).

Razones:
- Métrica directa del Objetivo #15 ("falsos positivos por contexto compactado/mes")
- Audit trail para incidentes futuros
- Input para el Guardián de los Objetivos (Obj #14) que monitorea la salud del ecosistema

## Bloques del Sprint

### Bloque 1 — Schema y migraciones Supabase

- `scripts/017_sprint_memento_schema.sql`:
  - Tabla `memento_validations` (id, timestamp, hilo_id, operation, context_used JSONB, validation_status, discrepancy JSONB, proceed BOOLEAN, validation_id TEXT)
  - Tabla `memento_critical_operations` (catálogo de operaciones críticas, leíble desde el kernel para evaluar requests)
  - Tabla `memento_sources_of_truth` (catálogo de fuentes de verdad y su última actualización: skills/X/Y, repos, dashboards externos)
  - Índices por hilo_id, timestamp, validation_status
  - RLS: read service_role, write service_role
- `scripts/run_migration_017.py`

ETA: 1-2 horas.

### Bloque 2 — Módulo `kernel/memento/` con lógica de validación

- `kernel/memento/__init__.py`
- `kernel/memento/validator.py`:
  - Clase `MementoValidator` con método `validate(operation, context_used) -> ValidationResult`
  - Para cada operación crítica del catálogo, lógica específica de comparación contra fuente de verdad
  - Manejo de fuentes de verdad: archivo del repo, env var de Railway, dashboard externo (con cache)
- `kernel/memento/sources.py`:
  - `read_credential_source(path)` lee `skills/X/references/credentials.md`, parsea host/user/etc, devuelve dict
  - `read_railway_env_var(service, var_name)` consulta Railway via API
  - Cache con TTL configurable (default 60s) para no leer el repo en cada validación
- `kernel/memento/critical_operations.yaml`: catálogo configurable

ETA: 2-3 horas.

### Bloque 3 — Endpoint HTTP `POST /v1/memento/validate`

- `kernel/memento_routes.py`:
  - Router FastAPI con `POST /v1/memento/validate`
  - Auth: header `X-API-Key` validado contra `MONSTRUO_API_KEY` (mismo patrón que `/v1/error-memory/seed`)
  - Body validation con Pydantic `MementoValidationRequest`
  - Llama a `MementoValidator`, persiste resultado en `memento_validations`, devuelve response
- Registro en `kernel/main.py`

ETA: 1 hora.

### Bloque 4 — Pre-flight library para hilos Manus

- `tools/memento_preflight.py` (módulo Python que cualquier hilo Manus puede importar):
  - Función `preflight_check(operation, context_used)` que:
    1. Lee la fuente de verdad localmente (más rápido)
    2. Llama al endpoint `/v1/memento/validate` para validación cruzada
    3. Si hay discrepancia → retorna `PreflightResult(proceed=False, ...)` con detalles
    4. Si OK → retorna `PreflightResult(proceed=True, validation_id="mv_...")`
  - Decorator `@requires_memento_preflight(operation_name)` para envolver funciones que ejecutan operaciones críticas
- Documentación en `tools/memento_preflight_README.md` con ejemplos de uso para hilos Manus
- Tests unitarios + integration tests con mock del endpoint

ETA: 2 horas.

### Bloque 5 — Migración de hilos existentes a usar Memento

- Hilo Manus ticketlike: el script `db_connect.py` del skill ticketlike-ops ahora hace pre-flight Memento antes de conectar
- Hilo Manus Ejecutor: cualquier script de rotación de credenciales (futura `scripts/rotacion_*.sh`) usa el preflight library
- Hilo Manus Catastro: scripts de seed (`seed_*.py`) hacen preflight contra fuente de verdad de la tabla `error_memory`
- `bridge/sprint_memento_migration_status.md`: matriz de qué hilos están migrados y cuáles faltan

ETA: 2 horas (mayor parte es testing).

### Bloque 6 — Detector de contexto contaminado (heurística magna)

- `kernel/memento/contamination_detector.py`:
  - Heurística #1: si un hilo Manus declara `credential_hash_first_8` que no coincide con la fuente de verdad PERO ese hash existió en commits anteriores → marcar como "contexto compactado heredado"
  - Heurística #2: si un hilo Manus reporta error de conexión contra host X PERO la última `memento_validation` exitosa de ese hilo fue contra host Y → marcar como "contexto contaminado por compactación"
  - Heurística #3: si un hilo Manus consume tool calls sin haber pasado por preflight en últimas N tool calls → flag de "operación sin pre-flight"
- Cuando se detecta contaminación, el endpoint `/v1/memento/validate` añade flag `contamination_warning: true` en response y notifica via bridge.

ETA: 2 horas.

### Bloque 7 — Tests + smoke + dashboard

- `tests/test_sprint_memento_*.py`:
  - Tests unitarios de `MementoValidator`
  - Tests de pre-flight library (con mock del endpoint)
  - Tests del detector de contaminación (con casos sintéticos del incidente TiDB del 2026-05-04)
  - Test E2E completo: hilo Manus simulado intenta operación crítica con contexto stale → recibe rechazo → corrige → exitoso
- Smoke test: `scripts/smoke_test_memento.py` que valida endpoint + módulo + persistencia + detección de contaminación
- Dashboard simple: query Supabase para "tasa de discrepancia por hilo en últimas 24h" como métrica del Obj #15

ETA: 2 horas.

## Estimación total y dependencias

| Bloque | ETA | Dependencias |
|---|---|---|
| 1. Schema | 1-2h | Ninguna |
| 2. Validator | 2-3h | Bloque 1 |
| 3. Endpoint | 1h | Bloque 2 |
| 4. Preflight library | 2h | Bloque 3 |
| 5. Migración hilos | 2h | Bloque 4 |
| 6. Contamination detector | 2h | Bloque 2 |
| 7. Tests + smoke | 2h | Todos los anteriores |
| **TOTAL** | **12-14h** | — |

Realista: 2-3 sesiones de trabajo de 4-5h cada una, distribuidas entre Hilo Ejecutor (Bloques 1-4) y Hilo Catastro (Bloques 5-7) si Alfredo quiere paralelizarlo. O un solo hilo en serie en 1-2 días.

## Métricas de cierre del Sprint

El Sprint Memento se considera **VERDE CERRADO** cuando:

1. Endpoint `/v1/memento/validate` vivo en Railway, healthy, con auth funcionando
2. Tabla `memento_validations` con al menos 50 entradas reales de hilos Manus operando con preflight
3. Al menos 1 hilo Manus migrado completo a usar `tools/memento_preflight` decorator (típicamente Hilo Manus ticketlike por ser el de operaciones más críticas con dinero real)
4. Detector de contaminación corre en producción, ha procesado al menos 1 caso sintético del incidente TiDB del 2026-05-04 y lo detecta correctamente
5. 30va semilla sembrada en `error_memory` documentando el patrón "credenciales heredadas de contexto compactado de Manus"
6. Test 1 v2 del Sprint Memento: simular un hilo Manus con contexto contaminado intentando operación crítica, verificar que el endpoint rechaza correctamente y el hilo aborta sin ejecutar la operación
7. Documentación: `docs/CAPA_MEMENTO_GUIA_OPERATIVA.md` con ejemplos de uso para hilos Manus + integraciones futuras

## Riesgos identificados

| Riesgo | Probabilidad | Mitigación |
|---|---|---|
| Hilos Manus existentes ignoran el preflight library | Alta | Migrar al menos 1 hilo crítico en este sprint + monitorear adopción |
| Latencia del endpoint degrada UX de hilos Manus | Media | Cache local en preflight library + TTL configurable |
| Falsos positivos del detector de contaminación | Media | Heurísticas conservadoras + flag `contamination_warning` no bloqueante en v1.0, evolucionar a bloqueante en v1.1 |
| Catálogo de operaciones críticas se queda desactualizado | Alta | Proceso explícito de revisión cada 2 sprints + alerta del Guardián si una operación productiva nueva no está en catálogo |

## Relación con otros sprints

- **Sprint 86 (Catastro):** sin dependencia directa. Puede correr antes o después.
- **Sprint 87 (Stripe Pagos):** SE BENEFICIA de Memento — el módulo de Stripe live debería estar bajo preflight Memento desde su nacimiento. Si Sprint Memento cierra antes que Sprint 87, Sprint 87 nace blindado.
- **Sprint 84.X (concluidos):** retroactivamente, varios incidentes (19 PATs, falso positivo TiDB, scope creep autónomo del Hilo Ejecutor en propuestas de rotación) hubieran sido prevenidos por Capa Memento.

## Recomendación de Cowork

Ejecutar Sprint Memento como **Sprint puente entre 86 y 87**. Razones:

1. Sprint 87 (Stripe Pagos) maneja dinero real — debe nacer con Memento blindándolo, no agregarlo después
2. La inversión de 12-14h se paga sola con la primera operación crítica que prevenga (un solo PAT GitHub duplicado evitado = 30 min de re-trabajo evitado)
3. Cierra explícitamente la deuda arquitectónica que destapó el incidente TiDB del 2026-05-04
4. Es el primer ejercicio práctico de implementar el Objetivo #15 recién agregado en v3.0 de los Objetivos Maestros — convierte el objetivo de declaración a infraestructura

— Cowork (Hilo B)

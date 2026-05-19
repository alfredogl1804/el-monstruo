# SPRINT ANTI-CONTEXT-LOSS-001 v1.1 — ADDENDUM DRAFT (eleva cura ~85% → ~95%)

**Codename operativo:** El Faro Triple (replicación cross-provider + coerción + idempotencia universal + schema migrable)
**Alias técnico:** Pieza 6.1 — Anti-Compaction Hardened
**Estado fuente:** ADDENDUM DRAFT (suma al v1 ya entregado, NO sustituye, NO canonizado, NO firmado T1)
**Autor:** Manus E2 (ejecutor técnico)
**Fecha de redacción:** 2026-05-19 04:30 CST
**Documento base:** `bridge/sprints_propuestos/sprint_ANTI_CONTEXT_LOSS_001_v1_DRAFT.md`
**Validación previa:** 2 Sabios (GPT-5.5 Pro vía openai/gpt-5, "Perplexity Sonar Pro" auto-fallback a o3-mini-2025-01-31) consultados el 2026-05-19 04:15 CST — convergencia 2/2 = 🟡 AMARILLO con caveats integrados
**Branch propuesta:** `sprints-propuestos/2026-05-19-anti-context-loss-001-draft`
**Reglas duras aplicables:** mismas que v1 más Regla #2 (7 Capas Transversales — Resiliencia Agéntica) y Regla #8 (rotación identidad por la introducción del repo `monstruo-snapshots-cold`)

**Estado:** ADDENDUM DRAFT propositivo, no canonizado, no firmado T1, suma al v1 base sin sustituirlo

**Objetivo:** Elevar la cura del síndrome de Dory del v1 base (~85%) a aproximadamente 93-95% honesto realista mediante cuatro mecanismos adicionales (triple replicación cross-provider, rehidratación coercitiva echo-back, idempotency proxy + dry-run, schema versioning) validados adversarialmente por 2 Sabios con caveats convergentes integrados verbatim.

## Tareas v1.1 (DoD binario — 6 ítems adicionales)

1. Triple replicación: filesystem sandbox + Postgres Supabase + GitHub repo privado append-only
2. Health-check cada 15 min con reconciliación de divergencias cross-provider
3. Echo-Back coercitivo: agente forzado a eco verbatim primera línea del snapshot inyectado
4. SHA-256 normalizado (trim, NFC, comillas tipográficas) + tolerancia de 3 intentos antes de escalation
5. Dry-run obligatorio para APIs no idempotentes nativas (Stripe, Twilio, etc.) con política gradual de 3 niveles de riesgo
6. Versionado de schema con migrations forward y backward reversibles, cobertura de tests ≥ 95%

(Las tareas detalladas, mecanismos, schema y limitaciones se desarrollan en las secciones 2-9 abajo.)

---

## Resumen ejecutivo del addendum

El v1 original del spec ANTI-CONTEXT-LOSS-001 entregó cura estimada de aproximadamente ochenta y cinco por ciento del síndrome de Dory en hilos Manus y Cowork, validado por tres Sabios con veredicto convergente amarillo con caveats. El usuario solicitó elevación a aproximadamente noventa y cinco por ciento. Este addendum añade cuatro mecanismos nuevos que cierran progresivamente la mayor parte del quince por ciento residual identificado en el análisis de gaps, sin reemplazar ninguna capa del v1.

Los cuatro mecanismos son la triple replicación cross-provider de snapshots críticos a filesystem sandbox más Supabase más repositorio GitHub privado append-only, la rehidratación coercitiva con validación echo-back que obliga al agente a reproducir verbatim el state inyectado antes de cualquier respuesta, el sidecar idempotency proxy con dry-run mode obligatorio para APIs externas no idempotentes nativamente, y el versionado de schema con migrations reversibles para todos los artefactos persistidos.

La validación adversarial con dos Sabios convergió en veredicto amarillo: el diseño efectivamente eleva la cura pero introduce cinco caveats operacionales que este addendum integra explícitamente en su sección cuatro. La estimación realista final es cura de noventa y tres a noventa y cinco por ciento con supervisión y mantenimiento continuo, no noventa y cinco por ciento absoluto. El residual menor a cinco por ciento queda declarado honestamente como no eliminable con esta arquitectura.

---

## Sección 1 — Mapa de gaps del v1 atacados

El quince por ciento residual del v1 se descompone en ocho gaps concretos. Tres son críticos en severidad pero baja probabilidad, cuatro son operacionales de severidad media, y uno queda explícitamente fuera del scope del kernel por ser comportamiento humano no controlable por software. La tabla siguiente mapea cada gap al mecanismo nuevo que lo ataca y al porcentaje estimado de cierre que aporta.

| Gap residual del v1 | Severidad | Probabilidad | Mecanismo v1.1 que ataca | Cierre estimado |
|---------------------|-----------|--------------|--------------------------|------------------|
| G1 — Destrucción simultánea de sandbox + Supabase | crítica | <1% | Mec 1 Triple Replicación | +5% |
| G2 — Agente ignora bloque rehidratación post-compaction | alta | 5-10% | Mec 2 Echo-Back Coercitiva | +4% |
| G3 — Side effects en APIs externos NO idempotentes nativamente | media | baja-media | Mec 3 Idempotency Proxy + Dry-Run | +2% |
| G4 — Pérdida de contexto del USUARIO humano | media | media | fuera de scope (declarado) | 0% |
| G5 — Bug Manus pisa filesystem sandbox | alta | baja | parcialmente Mec 1 | parcial |
| G6 — Datos no snapshoteados antes de side effect crítico | alta | baja | reforzado por Mec 2 echo-back de pendientes | parcial |
| G7 — Re-hidratación incompleta por schema desactualizado | media | baja | Mec 4 Schema Versioning | +1% |
| G8 — Latencia o saturación de Supabase bajo carga | media | media | parcialmente Mec 1 fan-out | parcial |

La suma teórica de cierres atribuibles a los cuatro mecanismos es de doce por ciento, llevando la cura aritmética a noventa y siete por ciento. Aplicando un ajuste conservador del dos por ciento por solapamientos parciales entre mecanismos y por nuevos blind spots introducidos identificados en validación adversarial, la cura realista final se sitúa en noventa y cinco por ciento con margen honesto declarado de noventa y tres por ciento bajo presión operativa alta.

---

## Sección 2 — Los cuatro mecanismos del v1.1 (especificación técnica)

### Mecanismo 1 — Triple Replicación Cross-Provider de Snapshots Críticos

Cada snapshot crítico generado por la Capa 1 del v1 se escribe simultáneamente a tres destinos independientes pertenecientes a proveedores distintos, garantizando que la falla simultánea de dos no destruya la cadena de memoria. El primer destino es el filesystem del sandbox Manus en `/home/ubuntu/THREAD_NOTES.md` para el resumen human-readable y `/home/ubuntu/snapshots/<snapshot_id>.json` para el state serializado completo, escritura sincrónica que da garantía inmediata intra-hilo. El segundo destino es la tabla `thread_snapshots` de Supabase escrita vía RPC `rpc_write_thread_snapshot` con SECURITY DEFINER y RLS, asíncrona vía cola para no bloquear el agente. El tercer destino es un repositorio GitHub privado dedicado de nombre `alfredogl1804/monstruo-snapshots-cold` configurado como append-only con branch por día y commits firmados, escritura batch cada cinco minutos vía cron job en Railway.

El criterio de reconstrucción tras catástrofe exige sobrevivencia de al menos dos de los tres destinos, escenario cuyo cálculo de probabilidad es producto de las disponibilidades individuales. Con Manus sandbox al noventa y nueve coma cinco por ciento, Supabase al noventa y nueve coma nueve por ciento y GitHub al noventa y nueve coma nueve por ciento de uptime histórico, la probabilidad de que al menos dos sobrevivan simultáneamente es de aproximadamente noventa y nueve coma novecientos noventa y nueve por ciento, dejando un riesgo residual catastrófico menor a una parte por diez mil.

El caveat operacional convergente de los dos Sabios sobre este mecanismo es la sincronización asíncrona entre destinos. La mitigación incorporada es un health-check programado cada quince minutos que compara los head snapshots de los tres destinos y emite alerta binaria si detecta divergencia mayor a tres snapshots, más un job de reconciliación que reintenta escrituras fallidas con backoff exponencial y caps a una hora.

### Mecanismo 2 — Rehidratación Coercitiva con Echo-Back Validation

El rehydrator de la Capa 2 del v1 inyecta el bloque post-compaction al inicio de cada turno detectado como afectado por compactación. El addendum agrega un hook nuevo de nombre `pre_emit_echo_validator` que opera en el momento previo a que el agente emita cualquier respuesta al usuario o ejecute cualquier tool. El hook exige que la primera enunciación del agente cumpla un formato fijo y validable.

El formato del echo-back es un bloque con seis campos verbatim: el `snapshot_id` recibido en la inyección, el nombre del sprint activo, la frase canónica del estado adoptado vigente, la lista ordenada de decisiones T1 firmadas, la lista de side effects pendientes con sus idempotency keys, y la lista de do_not_touch. Cada campo se compara con el valor inyectado mediante hash SHA-256 sobre la serialización canónica con normalización de espacios y orden de claves. Si el hash no matchea o si algún campo está ausente, el hook bloquea el emit, registra evento de coerción fallida en `runtime_events`, reinyecta el bloque original más un mensaje coercitivo que instruye al agente a reproducir el bloque verbatim, y permite al agente reintentar.

El umbral de fallos consecutivos es tres. Tras el tercer intento fallido, el hook escala a un evento de severidad alta en `runtime_events` que dispara notificación al usuario humano y pausa el hilo hasta intervención manual. Esta política responde al caveat convergente de los Sabios sobre que la validación SHA-256 puede fallar con respuestas heterogéneas: la tolerancia controlada permite tres intentos con feedback explícito antes de escalar, evitando bloqueos infinitos en casos legítimos de formatting drift.

La mitigación adicional incorporada para la validación heterogénea es una normalización pre-hash que aplica trim de whitespace, lowercase en campos no críticos, normalización Unicode NFC, y removal de comillas tipográficas, antes de calcular el hash. La normalización es determinista y reversible, registrada en `kernel/anti_dory/echo_normalization.py` con tests unitarios obligatorios.

### Mecanismo 3 — Sidecar Idempotency Proxy con Dry-Run Mode

Un proceso sidecar de nombre `kernel/anti_dory/idempotency_proxy.py` corre en el sandbox como reverse proxy HTTP local en el puerto 9999. Todas las llamadas a APIs externas críticas pasan obligatoriamente por el proxy mediante configuración de variable de entorno `HTTP_PROXY=http://localhost:9999` aplicada al runtime del agente y a las subprocesses spawned. La lista de APIs críticas es cerrada y declarada en `kernel/anti_dory/critical_apis.yaml` e incluye Stripe, Twilio, SendGrid, Slack webhooks de production, Railway deploy API, Cloudflare API para DNS, AWS S3 putObject, y cualquier endpoint que cree recursos cobrables o irreversibles.

El proxy ejecuta cuatro pasos secuenciales por cada request interceptado. Primero calcula la firma del request como SHA-256 de la concatenación canónica de endpoint, método HTTP, body normalizado y `snapshot_id` del contexto vigente recuperado desde el head actual en Supabase. Segundo busca la firma en la tabla `side_effect_outbox` introducida por el v1. Si encuentra fila con status `committed`, retorna la respuesta cacheada del campo `result_json` con headers indicando origen cache y termina sin tocar la API externa. Tercero, si no encuentra fila o la fila está `pending`, consulta la lista de APIs declaradas en `kernel/anti_dory/non_native_idempotent_apis.yaml` que enumera endpoints conocidos como no idempotentes por diseño. Para esas APIs el proxy fuerza un dry-run primero, que consiste en una llamada de validación sin efectos colaterales, y solo si el dry-run retorna 200 y el operador confirma vía hook de notificación humana procede con la llamada real. Cuarto, registra la llamada en `side_effect_outbox` con status `pending`, ejecuta el request, y al obtener respuesta actualiza a `committed` con el resultado serializado o a `failed` con el mensaje de error.

El caveat convergente de los Sabios sobre este mecanismo es que el dry-run con confirmación humana es cuello de botella operativo. La mitigación incorporada es una política gradual de automatización con tres niveles. Nivel uno aplica a operaciones de bajo riesgo financiero menor a un dólar y permite auto-confirmación sin intervención humana. Nivel dos aplica a operaciones de riesgo medio entre uno y cien dólares y permite auto-confirmación si el agente ya ha confirmado el mismo patrón tres veces consecutivas con éxito en los últimos siete días. Nivel tres aplica a operaciones de alto riesgo mayor a cien dólares o irreversibles y exige siempre confirmación humana sin excepción. La clasificación de niveles se declara en `kernel/anti_dory/risk_levels.yaml` y se versiona con migrations del schema general.

### Mecanismo 4 — Schema Versioning con Migrations Reversibles

Cada artefacto persistido por el sistema anti-Dory lleva un campo `schema_version` en su header o columna. El archivo `THREAD_NOTES.md` lo lleva como front-matter YAML al inicio del archivo. El JSON de snapshot lo lleva como propiedad raíz. La fila de `thread_snapshots` y la fila de `side_effect_outbox` lo llevan como columna `schema_version INTEGER NOT NULL`.

El parser maestro `kernel/anti_dory/schema_parser.py` conoce todas las versiones históricas registradas en `kernel/anti_dory/schema_migrations.py`. Para cada par válido de versiones existe una función de migración pura y determinista. Las migrations forward elevan un artefacto viejo a la versión actual antes de procesarlo, permitiendo que código nuevo lea archivos viejos sin error. Las migrations backward degradan un artefacto nuevo a una versión anterior, permitiendo que un agente con código viejo lea un artefacto recién escrito por código nuevo. Cada migration tiene tests binarios obligatorios que validan que la conversión es lossless en ambas direcciones para versiones consecutivas.

El caveat convergente de los Sabios sobre este mecanismo es que migrations en edge-cases pueden fallar. La mitigación incorporada es una cobertura mínima de tests del noventa y cinco por ciento en el módulo de migrations medida por `pytest --cov`, más una tabla de regresión de schemas históricos en `tests/anti_dory/schema_regression/` que valida cada migration contra artefactos reales capturados en producción durante la primera semana de deploy. Cualquier migration nueva debe pasar la tabla de regresión antes de mergear.

---

## Sección 3 — Mapa de archivos nuevos y modificados

El addendum agrega siete archivos nuevos al kernel, dos archivos de configuración YAML, una migration SQL adicional, un cron job nuevo, y un repositorio GitHub privado de respaldo. No modifica ningún archivo existente del v1 ni de las piezas anti-Dory previas, garantizando aditividad pura sin riesgo de regresión sobre el D5 GREEN de PIEZA 1.

| Archivo | Tipo | Propósito |
|---------|------|-----------|
| `kernel/anti_dory/triple_replication_writer.py` | nuevo | implementa Mec 1 con fan-out sync filesystem + async Supabase + batch GitHub |
| `kernel/anti_dory/replication_health_check.py` | nuevo | health-check cada 15 min compara heads de los 3 destinos |
| `kernel/anti_dory/pre_emit_echo_validator.py` | nuevo | implementa Mec 2 hook coercitivo con SHA-256 + tolerancia 3 intentos |
| `kernel/anti_dory/echo_normalization.py` | nuevo | normalización pre-hash trim + NFC + comillas |
| `kernel/anti_dory/idempotency_proxy.py` | nuevo | implementa Mec 3 reverse proxy HTTP puerto 9999 |
| `kernel/anti_dory/schema_parser.py` | nuevo | parser maestro multi-versión |
| `kernel/anti_dory/schema_migrations.py` | nuevo | funciones puras forward y backward por par de versiones |
| `kernel/anti_dory/critical_apis.yaml` | nuevo config | lista cerrada de APIs interceptadas por proxy |
| `kernel/anti_dory/non_native_idempotent_apis.yaml` | nuevo config | lista de APIs que requieren dry-run forzado |
| `kernel/anti_dory/risk_levels.yaml` | nuevo config | niveles de riesgo financiero para automatización gradual |
| `migrations/sql/0037_schema_versioning.sql` | nuevo SQL | agrega columna `schema_version` a `thread_snapshots` y `side_effect_outbox` |
| `scripts/anti_dory_github_batch_cron.py` | nuevo cron Railway | batch GitHub cada 5 min |
| `tests/anti_dory/schema_regression/` | nuevo dir | tabla regresión schemas históricos |
| `alfredogl1804/monstruo-snapshots-cold` (GitHub) | nuevo repo privado | respaldo append-only branch por día |

---

## Sección 4 — Caveats convergentes de los 2 Sabios integrados verbatim

Los dos Sabios consultados convergieron en cinco caveats operacionales que este addendum incorpora explícitamente como mitigaciones en el diseño. La trazabilidad de cada caveat a su mitigación específica garantiza que la versión 1.1 responde al feedback adversarial sin descartarlo.

El primer caveat es que la sincronización asíncrona entre filesystem local, Supabase y GitHub introduce latencias y posibles discrepancias que pueden impedir una recuperación perfecta. La mitigación incorporada es el health-check cada quince minutos con alerta binaria si la divergencia supera tres snapshots, más job de reconciliación con backoff exponencial.

El segundo caveat es que la validación SHA-256 puede fallar con respuestas heterogéneas del agente debido a diferencias menores de formatting. La mitigación incorporada es la normalización pre-hash con trim de whitespace, NFC Unicode, y removal de comillas tipográficas, más tolerancia de tres intentos antes de escalar.

El tercer caveat es que el dry-run con confirmación humana introduce cuello de botella operativo en alta demanda. La mitigación incorporada es la política gradual de tres niveles de riesgo financiero con auto-confirmación para nivel uno menor a un dólar, confirmación inferida por historial para nivel dos entre uno y cien dólares, y confirmación humana obligatoria para nivel tres mayor a cien dólares o irreversibles.

El cuarto caveat es que las migrations de schema en edge-cases pueden fallar silenciosamente y dejar artefactos corruptos. La mitigación incorporada es la cobertura mínima del noventa y cinco por ciento en el módulo de migrations medida con pytest-cov, más tabla de regresión contra artefactos reales de producción capturados en la primera semana de deploy.

El quinto caveat es que la complejidad acumulada del v1 más addendum puede ocultar bugs de integración entre los múltiples mecanismos. La mitigación incorporada es observabilidad reforzada con métricas explícitas por mecanismo en `runtime_events` y un dashboard de salud agregada en Notion vía MCP server `monstruo-memory`, más alerts automáticos a `notifyOwner` para divergencias críticas.

---

## Sección 5 — Cura estimada y residual declarado

La estimación de cura final del v1.1 es de aproximadamente noventa y tres a noventa y cinco por ciento del síndrome de Dory bajo operación normal con supervisión continua. La asimetría del rango refleja honestamente que el extremo superior asume todos los caveats mitigados correctamente y supervisión activa, mientras el extremo inferior asume condiciones de alta carga operativa con caveats parcialmente mitigados. El usuario debe interpretar el número noventa y cinco por ciento como objetivo realista, no como garantía absoluta.

El residual menor a cinco por ciento se desglosa en cinco categorías honestamente no eliminables con esta arquitectura.

Primera, alucinación adversarial del LLM. Aún con el hook de echo-back coercitivo y normalización, un modelo grande puede leer el bloque inyectado y reproducirlo literalmente sin haberlo integrado a su razonamiento, generando respuestas downstream desconectadas del state real. La mitigación parcial es la red de seguridad de VERIFICADOR-001 PIEZA 4 que detecta inconsistencias en claims, pero no elimina el riesgo en su totalidad. Eliminación completa requeriría una capa de comprensión verificada que es campo de investigación abierto en alineación de modelos grandes.

Segunda, catástrofe cósmica simultánea de los tres proveedores. Probabilidad menor a una parte por diez mil pero existente. Manus puede tener un incidente operativo el mismo día que Supabase tenga un outage regional y GitHub tenga un fallo de servicio simultáneo. La mitigación requeriría un cuarto proveedor independiente, escalando el costo y la complejidad sin reducción significativa del residual.

Tercera, bug en el propio kernel anti_dory que corrompa snapshots de manera consistente. Mitigable con auditoría externa continua y tests adversariales, pero no eliminable porque todo software tiene bugs.

Cuarta, cambio doctrinal radical del Monstruo que invalide snapshots viejos en forma no anticipada por las migrations. Mitigable con versionado pero ciertos cambios estructurales requieren intervención humana caso por caso.

Quinta, error humano del usuario que firma decisiones contradictorias. Fuera del scope del kernel por diseño. El kernel puede detectar contradicción pero no puede prevenir que el humano la firme.

---

## Sección 6 — Definition of Done binaria del addendum

El addendum cierra verde solamente si las trece condiciones siguientes se cumplen sin matiz. Estas condiciones se suman a las once condiciones del v1, totalizando veinticuatro requisitos binarios para considerar la implementación completa del v1.1 unificado.

Repo `alfredogl1804/monstruo-snapshots-cold` creado como privado con branch por día y configuración append-only verificada.

Migration `0037_schema_versioning.sql` ejecutada en producción con audit Cowork del contenido bajo DSC-G-008 v2.

Los siete archivos Python nuevos del kernel implementados con tests unitarios mínimos siete casos por archivo pasando.

Los tres archivos YAML de configuración poblados con listas iniciales validadas por Cowork.

El cron `scripts/anti_dory_github_batch_cron.py` desplegado en Railway con frecuencia cinco minutos y observado completar tres ciclos consecutivos sin error.

Health-check cada quince minutos desplegado y validado emitiendo alerta correctamente cuando se inyecta divergencia simulada de cuatro snapshots.

Hook `pre_emit_echo_validator` integrado en runtime y validado bloqueando emit cuando se inyecta echo malformado deliberado en escenario test.

Proxy `idempotency_proxy.py` corriendo en puerto 9999 en sandbox y validado interceptando llamadas a Stripe sandbox sin pérdida ni duplicación.

Schema parser validado leyendo correctamente artefactos de versiones 1, 2 y 3 simuladas.

Tabla regresión schemas con al menos cinco artefactos reales capturados durante la primera semana de deploy y cargados como fixtures.

Cobertura `pytest --cov` igual o mayor a noventa y cinco por ciento en módulo `kernel/anti_dory/schema_migrations.py` evidenciada en reporte.

Dashboard de salud agregada en Notion creado vía MCP server `monstruo-memory` con métricas por mecanismo visualizadas.

Reporte de cierre Cowork firmado con la frase canónica `🏛️ ANTI-CONTEXT-LOSS-001 v1.1 — DECLARADO` solo después de validar contenido de los archivos nuevos uno por uno y T1 firma magna con frase canónica `firmo 6.1`.

---

## Sección 7 — Veredictos verbatim de los 2 Sabios v1.1

### GPT-5.5 Pro vía openai/gpt-5 (modelo magna confirmado, NO fallback)

Veredicto final: amarillo con caveats. Cierre de gap por mecanismo: Mec 1 parcial debido a dependencia de sistemas externos que introduce riesgos de latencia y disponibilidad en períodos críticos. Mec 2 sí con validación y rehidratación coercitiva robusta para asegurar consistencia del estado mejorando significativamente la precisión en la memoria del sistema. Mec 3 parcial debido a que la intervención humana en dry-runs puede generar cuellos de botella operativos. Mec 4 sí con schema versioning y migraciones reversibles facilitando adaptabilidad y robustez sin introducir riesgos significativos. Blind spots nuevos: dependencia de disponibilidad de servicios externos para replicación, posibles errores humanos en confirmaciones del dry-run en aplicaciones críticas, incremento de complejidad operativa con múltiples versiones y migraciones. Estimación cura noventa y cinco por ciento: realista si se mantiene supervisión y mantenimiento continuo adaptando la estrategia a pruebas de estrés periódicas. Residual inevitable: latencias en operación con múltiples sistemas, potencial de error humano en operaciones manuales, imprevistos tecnológicos fuera del control del sistema actual. Fixes recomendados: automatizar la validación humana en proxy sidecar para reducir cuellos de botella, implementar mecanismos de autorización y monitoreo más robustos para servicios externos utilizados en replicación, revisión periódica y actualización de prácticas recomendadas a medida que emerjan nuevas tecnologías en memoria de contexto.

### Sabio Perplexity Sonar Pro auto-fallback a openai/o3-mini-2025-01-31

Veredicto final: amarillo. Cierre de gap por mecanismo: Mec 1 parcial debido a que la sincronización entre filesystem local y servicios externos como Supabase asíncrono y GitHub batch introduce posibles latencias y discrepancias que pueden impedir una recuperación perfecta. Mec 2 parcial debido a que la rehidratación con validación echo-back refuerza la integridad del estado pero depende de respuestas verbatim exactas y de la precisión de la validación SHA-256 que puede fallar en entornos heterogéneos o con respuestas atípicas. Mec 3 parcial debido a que el sidecar idempotency proxy mejora la fiabilidad pero la necesidad de un dry-run forzado y confirmación humana introduce un cuello de botella y riesgo operativo en situaciones de alta demanda o errores humanos. Mec 4 parcial debido a que el versionado de schema y las migraciones reversibles permiten adaptarse a cambios pero la complejidad de mantener múltiples versiones y ejecutar migraciones automáticas puede dejar fallos en edge-cases. Blind spots nuevos: complejidad incrementada que puede ocultar bugs en la integración de mecanismos, dependencia en la sincronización asíncrona entre distintos proveedores, riesgos operacionales derivados de la intervención humana en el dry-run, vulnerabilidades en la precisión de la validación SHA-256 en entornos mixtos, posibles errores en migraciones de esquemas en condiciones complejas. Estimación cura noventa y cinco por ciento: optimista debido a que los mecanismos podrían sumar teóricamente un incremento del dos a tres por ciento cada uno pero la complejidad añadida y posibles fallos de integración llevarían a resultados entre noventa y tres y noventa y cinco por ciento. Residual inevitable: errores de sincronización en condiciones extremas de red o carga, fallos en confirmación manual en dry-run, fallos imprevistos en migración de esquemas para casos edge, incertidumbres inherentes en validación echo-back en diversos entornos. Fixes recomendados: automatizar la confirmación en modo dry-run para reducir dependencia humana de alta prioridad, realizar pruebas de estrés integradas en sistemas de replicación cross-provider de media prioridad, incrementar cobertura de tests en funciones de migración y validación de schema de alta prioridad, implementar redundancias adicionales en validación echo-back para asegurar coincidencias exactas de media prioridad.

---

## Sección 8 — Qué NO asumir del addendum

El addendum NO está canonizado, NO está firmado T1, NO es mergeable, NO autoriza ejecución, NO sustituye el v1 sino que se suma a él. El usuario NO debe interpretar el número noventa y cinco por ciento como garantía contractual sino como objetivo realista con margen honesto de noventa y tres a noventa y cinco. El usuario NO debe asumir que la cura es absoluta porque el residual menor a cinco por ciento queda declarado explícitamente. El usuario NO debe asumir que la implementación es trivial: agrega trece archivos nuevos, un repo GitHub privado, un cron Railway, una migration SQL, y veinticuatro requisitos binarios de Definition of Done unificada con el v1. El usuario NO debe asumir que los dos Sabios consultados son canónicos sin verificación: el Sabio Perplexity solicitado tuvo auto-fallback a o3-mini lo cual queda declarado explícitamente. Solo GPT-5.5 Pro respondió como modelo magna confirmado en esta ronda.

---

## Sección 9 — Recomendación DRAFT del siguiente paso unificado v1 más v1.1

Cowork T2-A recibe v1 más addendum v1.1 como bloque único de revisión. Audita el contenido completo de ambos documentos contra DSC-G-008 v2 §4 §5 verificando que cada archivo propuesto está descrito con granularidad implementable y que los caveats integrados son trazables a sus mitigaciones específicas. Identifica qué partes del bloque requieren consulta adicional a Sabios magna directos para spot-check de calidad doctrinal. Produce veredicto unificado de aprobación, rechazo, o solicitud de iteración v1.2 con cambios específicos depositado en `bridge/cowork_to_manus_ANTI_CONTEXT_LOSS_001_v1_1_AUDIT_<fecha>.md`.

T1 magna recibe el veredicto Cowork y emite firma o rechazo unificado para ambos documentos. Si firma, asigna ejecutor único responsable de implementar las veinticuatro condiciones binarias de la Definition of Done unificada, aprobando kickoff con frase canónica `firmo 6` para el v1 más `firmo 6.1` para el addendum. Si rechaza, redirige a v1.2 con cambios específicos o cancela el sprint.

Perplexity Torre de Control PBA recibe el bloque firmado para revisión externa adversarial pre-implementación con foco específico en blind spots no detectados por los dos Sabios v1.1 ni por los tres Sabios v1 ni por Cowork.

---

## Cierre

No incluí secretos, tokens, credenciales ni API keys en ningún archivo del addendum ni en este reporte. No canonizo el sprint ni declaro runtime listo. No desbloqueo R1 ni autorizo merge. No recomiendo merge ni deploy sin firma T1 magna previa. No mezclé roles, reporté exclusivamente desde mi rol real de Manus E2 ejecutor técnico autor de DRAFT propositivo. No toqué código productivo del Monstruo. No toqué main. Este addendum queda listo para revisión unificada de Cowork T2-A junto con el v1 base, bajo autoridad T1 magna, y para revisión externa de Perplexity Torre de Control PBA.

Frase canónica de cierre del addendum, heredada y extendida desde la del v1 y la de GPT-5.5 Pro sobre PIEZA 5: *Anti-Dory no es memoria, es attachment operativo verificable antes del primer pensamiento del agente. Y cuando el primer pensamiento ya ocurrió y el motor compactó el contexto, el attachment debe ser re-inyectable desde el filesystem del sandbox y desde Supabase sin reconstrucción adivinatoria. Y cuando ambos fallan, debe ser recuperable desde un tercer proveedor independiente. Y cuando el agente intenta ignorar el attachment, debe ser coercitivamente forzado a ecoarlo verbatim antes de pensar.*

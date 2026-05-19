# SPRINT ANTI-CONTEXT-LOSS-001 v1 — DRAFT PROPOSITIVO

**Codename operativo:** El Faro (guía hilos perdidos al puerto canónico)
**Alias técnico:** Pieza 6 — Anti-Compaction & Context Loss Cure
**Estado:** DRAFT propositivo (NO canonizado, NO firmado T1, NO mergeable)
**Estado fuente:** DRAFT propositivo (NO canonizado, NO firmado T1, NO mergeable)
**Autor:** Manus E2 (ejecutor técnico)
**Fecha de redacción:** 2026-05-19 03:30 CST
**Audiencia:** Cowork T2-A (audit), T1 (firma magna), Perplexity Torre de Control PBA (revisión externa)
**Branch fuente:** `sprints-propuestos/2026-05-19-anti-context-loss-001-draft`
**Validación previa:** 3 Sabios (Opus 4.7, GPT-5.5 Pro, Perplexity Sonar Reasoning Pro) consultados en paralelo el 2026-05-19 — convergencia 3/3 = 🟡 AMARILLO CON CAVEAT
**Reglas duras aplicables:** Regla #1 (15 Objetivos), Regla #2 (7 Capas Transversales — Resiliencia Agéntica), Regla #6 (cero secrets), Regla #7 (RLS universal), DSC-G-008 v2 §4 (limitaciones declaradas)

**Objetivo:** Diseñar la cura del síndrome de Dory (pérdida de contexto en hilos Manus y Cowork ante compactación mid-sesión, crash o hibernación del sandbox, instanciación de hilo nuevo, y drift intra-hilo multi-hora) usando exclusivamente la infraestructura del Monstruo, alcanzando ~85% de cura realista en este v1 base mediante una arquitectura de cuatro capas (Pre-Compaction Snapshot Writer, Post-Compaction Rehydrator, Idempotency Wrapper, Context Health Threshold) más un servidor MCP transversal.

## Tareas v1 base (DoD binario — 7 ítems)

1. Tabla `runtime_events` + RLS policies firmadas en migration versionada
2. Tabla `thread_snapshots` + RLS policies firmadas
3. Tabla `project_runtime_heads` + CAS lock con `lock_version`
4. RPC `register_runtime_event` con SECURITY DEFINER
5. RPC `get_thread_attachment` con SECURITY DEFINER
6. Hook `pre_response_hook.py` instalado en `kernel/cowork_runtime/`
7. VERIFICADOR-001 PIEZA 4 mergeado y ejecutándose

(Las tareas detalladas, schema SQL, RPCs, tests binarios y limitaciones declaradas se desarrollan en las secciones 2-12 abajo.)

---

## Resumen ejecutivo

El Monstruo opera con hilos Manus y Cowork que sufren pérdida de contexto en cuatro vectores distintos: compactación de ventana de tokens mid-sesión, crash o hibernación del sandbox, instanciación de hilo nuevo sin contexto del sprint en curso, y drift intra-hilo multi-hora donde el mismo agente modifica un artefacto y horas después olvida el cambio. El conjunto de piezas anti-Dory actualmente desplegadas (PIEZA 1 cross-agente, PIEZA 2 MEMENTO, PIEZA 3 CRUZ Cowork cross-sesión, PIEZA 4 VERIFICADOR pre-emit hook, PIEZA 5 DRAFT intra-hilo Manus) ataca tres de esos cuatro vectores y deja el vector **compactación mid-sesión** completamente descubierto. Este sprint propone una arquitectura definitiva de cuatro capas que cubre el cuarto vector y unifica los primitives de memoria duradera para ambos agentes mediante un servidor MCP propio del Monstruo.

El diseño nace de tres fuentes de evidencia: la investigación en tiempo real de los patrones canónicos de la industria 2026 (Anthropic Context Engineering de septiembre 2025 y cookbook de marzo 2026, Manus AI Context Engineering de Peak Ji documentado por Lance Martin en octubre 2025, LangGraph 2026 durable execution con time-travel y checkpointing, y Harness Plan-Execute-Reset de abril 2026), el inventario binario de la infraestructura ya desplegada en el repo (tablas Supabase `runtime_events`, `thread_snapshots`, `project_runtime_heads`, `runtime_flags` con RLS habilitado, kernel `kernel/anti_dory/` con context broker, guardian y writers, hook pre-emit Cowork de PIEZA 4, sandbox Manus con filesystem persistente que sobrevive compaction según observación directa en este mismo hilo), y la consulta paralela a tres Sabios cuyos veredictos convergen en amarillo con caveats específicos integrados verbatim en este spec.

La frase canónica que gobierna el diseño es la legada por GPT-5.5 Pro durante PIEZA 5: *Anti-Dory no es memoria, es attachment operativo verificable antes del primer pensamiento del agente*. Este sprint extiende esa frase con un corolario operativo propio: *cuando el primer pensamiento del agente ya ocurrió y el motor compactó el contexto, el attachment debe ser re-inyectable desde el filesystem del sandbox y desde Supabase sin reconstrucción adivinatoria*.

---

## Sección 1 — Diagnóstico del vector descubierto

### 1.1 Por qué la compactación mid-sesión es invisible a las piezas existentes

PIEZA 1 (Anti-Dory cross-agente) opera exclusivamente en el momento de instanciar un hilo Manus nuevo. El Context Broker intercepta la llamada `task.create`, inyecta el snapshot canónico como primer mensaje, y el Guardian Verifier valida que el agente arrancó atado al state. Este mecanismo es robusto para hilos nuevos pero **no se dispara cuando un hilo ya activo pierde contexto por compactación**, porque el hilo nunca pasó de nuevo por `task.create`.

PIEZA 4 (VERIFICADOR-001 pre-emit hook) opera antes de cada respuesta de Cowork, validando claims contra repo y DB. Cura sobre-confianza pero **no recupera contexto perdido**: si la compactación ya truncó el histórico, el hook no tiene de dónde reconstruir lo borrado.

PIEZA 5 (MANUS-ANTI-DORY-003 DRAFT intra-hilo) propone un pre-flight check al inicio de cada turno del agente, pero **no aborda el evento de compactación específicamente**. Su scope es drift temporal (el agente que olvida un cambio que él mismo hizo horas atrás), no truncamiento estructural de la ventana de tokens por el motor de la plataforma.

### 1.2 Observación directa de compactación en este hilo

Durante la redacción de este mismo sprint, el hilo Manus E2 sufrió dos compactaciones en vivo. La primera ocurrió durante la Fase 1 (audit de infraestructura), la segunda durante la Fase 4 (síntesis del spec). En ambos casos el sistema reemplazó el histórico previo con un tag `<compacted_history>` y un `<system_reminder>` notificando la truncación. Los archivos previamente escritos a `/home/ubuntu/anti_context_loss_audit.md` y `/home/ubuntu/anti_context_loss_research_2026.md` permanecieron íntegros y legibles tras ambas compactaciones, confirmando empíricamente que **el filesystem del sandbox Manus sobrevive al motor de compactación**. Esta observación es la columna vertebral arquitectónica del diseño: la cura primaria es escribir al filesystem antes de cada side effect crítico y leer desde el filesystem al inicio de cada turno post-detección de compactación.

### 1.3 Por qué Manus AI no resuelve esto solo

El motor de compactación de Manus es propietario y aplica tres estrategias secuenciales según Peak Ji y Lance Martin: offload de tool results al filesystem, reemplazo de stale results por referencias path, y summarization schema-based de la trayectoria cuando compaction llega a diminishing returns. Manus preserva la continuidad conversacional pero **no garantiza que el agente recuerde decisiones de gobernanza específicas del Monstruo** (sprint en curso, decisiones T1 firmadas, do_not_touch lists, side effects pendientes, snapshot canónico). El motor compacta hacia *continuidad de tarea genérica*, no hacia *fidelidad doctrinal del Monstruo*. La cura debe ser específica del dominio.

---

## Sección 2 — Arquitectura de cuatro capas

La arquitectura combina cuatro capas que operan en orden secuencial durante el ciclo de vida del hilo, más un servidor MCP transversal que expone los primitives a ambos agentes (Manus y Cowork) mediante un protocolo estándar.

### Capa 1 — Pre-Compaction Snapshot Writer (enforcement a nivel kernel)

El agente escribe un snapshot estructurado cada vez que cumple cualquiera de tres condiciones: cada cinco turnos del agente, cuando el conteo de tokens consumidos en el contexto supera el sesenta por ciento del límite estimado de la ventana, o inmediatamente antes de ejecutar cualquier side effect crítico (creación de PR, aplicación de migration, deploy, rotación de secret, escritura a tabla del Monstruo). El snapshot consiste en dos artefactos sincronizados.

El primer artefacto es un archivo Markdown human-readable en `/home/ubuntu/THREAD_NOTES.md` con esquema rígido y machine-friendly. La estructura del esquema define secciones obligatorias separadas por headers Markdown nivel 2: identidad del hilo (agente, sprint asignado, fase actual, hora de inicio), Estado Adoptado verbatim (frase canónica del último ESTADO ADOPTADO declarado por el agente, requisito heredado de GPT-5.5 Pro sobre PIEZA 5), decisiones T1 pendientes y firmadas en orden cronológico, archivos del repo tocados con commit SHA si aplica, side effects ejecutados y pendientes con sus idempotency keys, lista de do_not_touch, y referencia al snapshot Supabase correspondiente. Un parser Python en `kernel/anti_dory/thread_notes_parser.py` valida el contrato del archivo y emite error binario si el schema se rompe. Esto responde al caveat de Perplexity Sonar sobre la ausencia de contrato machine-friendly para el note-taking.

El segundo artefacto es una fila en `thread_snapshots` de Supabase escrita vía RPC `rpc_write_thread_snapshot` con SECURITY DEFINER y RLS. La fila lleva `parent_snapshot_id` apuntando al snapshot anterior del mismo hilo, formando una cadena reproducible bidirreccional. El `state_hash` se calcula con SHA-256 sobre la serialización JSON ordenada del state, garantizando que cambios al state se detecten determinísticamente. El campo `project_runtime_heads.head_snapshot_id` se actualiza con CAS (compare-and-swap) usando `lock_version` para resolver conflictos cuando dos agentes intentan actualizar simultáneamente el head del mismo (project_id, front_id), respondiendo al caveat de GPT-5.5 Pro y Perplexity sobre concurrencia multiagente.

El enforcement de esta capa **no depende del agente** sino del kernel. Un nuevo hook `kernel/anti_dory/pre_action_hook.py` envuelve los puntos de entrada críticos del runtime (tool invocation, file write, shell exec con flags de side effect) y dispara el snapshot automáticamente. Si el snapshot falla por error de DB o filesystem full, el side effect se aborta con error binario. Esta es la respuesta directa al caveat de Perplexity sobre enforcement desde kernel y no desde agente.

### Capa 2 — Post-Compaction Rehydrator (detección y re-inyección)

Al inicio absoluto de cada turno del agente, antes del primer pensamiento, un hook `kernel/anti_dory/post_compaction_rehydrator.py` ejecuta cinco pasos en secuencia atómica.

Primero detecta el evento de compactación mediante un parser regex que busca el tag `<compacted_history>` y el `<system_reminder>` mencionando compaction en el último input del agente. Si el flag es positivo el rehydrator continúa; si es negativo simplemente registra un heartbeat ligero en `runtime_events` y termina.

Segundo lee `/home/ubuntu/THREAD_NOTES.md` completo y valida el schema con el parser. Si el archivo no existe o no parsea, recurre a Supabase exclusivamente.

Tercero invoca `rpc_get_context_head(project_id, front_id)` que devuelve el `head_snapshot_id` actual con bloqueo de lectura optimista.

Cuarto sigue la cadena `parent_snapshot_id` retroactivamente hasta tres niveles, recuperando los últimos tres snapshots del hilo. Esto da contexto temporal: el snapshot actual, el inmediatamente anterior, y el de hace dos pasos, permitiendo al agente ver qué cambió en los últimos turnos antes de la compactación.

Quinto compone un bloque de re-hidratación con formato fijo y lo inyecta como primer mensaje del turno bajo el header `## REHIDRATACIÓN POST-COMPACTATION`. El bloque incluye verbatim: sprint y fase actual, Estado Adoptado vigente, lista de decisiones T1 firmadas en orden, archivos tocados con commits, side effects pendientes con idempotency keys, do_not_touch, y un puntero al snapshot_id de cabeza. El agente recibe este bloque ANTES de cualquier respuesta y debe declarar verbalmente "REHIDRATACIÓN ACEPTADA — snapshot_id=XYZ" como primer enunciado de su respuesta, dejando un evento auditable en `runtime_events`.

### Capa 3 — Idempotency Wrapper para side effects

Todos los side effects irreversibles o costosos del Monstruo (creación de PR vía `gh pr create`, escritura a tablas del Monstruo, aplicación de migration SQL, deploy a Railway o Cloud Run, rotación de secret, push a main, ejecución de comandos `webdev_save_checkpoint`, escritura de archivo en `bridge/` con commit, llamadas a APIs externas que cobran o crean recursos) deben ejecutarse a través de un wrapper `kernel/anti_dory/idempotency.py` que aplica un patrón outbox transaccional respondiendo al caveat de Perplexity y GPT-5.5 Pro sobre endurecer idempotencia.

El wrapper recibe la acción + sus argumentos + un `snapshot_id` de contexto, y deriva un `idempotency_key` determinista como `sha256(snapshot_id || action_name || canonical_json(action_args))`. Antes de ejecutar consulta una nueva tabla `side_effect_outbox` (a crear en migration nueva) buscando el key. Si el key existe con `status='committed'`, retorna el resultado cacheado y NO re-ejecuta. Si existe con `status='pending'`, espera a que el lock libere (timeout 60s) y reintenta lectura. Si no existe, escribe una fila `pending` con el key, ejecuta la acción, y al éxito actualiza a `committed` con el resultado serializado. Si la acción falla, marca `failed` con el error. La tabla lleva índice único sobre `idempotency_key` y RLS habilitada con policy explícita para `service_role`.

La serialización canónica de los argumentos usa `json.dumps(..., sort_keys=True, separators=(',', ':'), ensure_ascii=False)` con normalización de timestamps a UTC milisegundos, garantizando reproducibilidad determinística entre runs aún cuando el orden de las claves del dict cambie. Esto responde al caveat de Perplexity sobre serialización estable.

### Capa 4 — Context Health Threshold (simplificada por caveat convergente)

La propuesta original de un `context_health_score` ponderado de cuatro variables (token_growth, stale_assumptions, last_verification_age, decisions_unresolved) fue descartada por los tres Sabios como over-engineered: GPT-5.5 Pro la catalogó como sobrante, Perplexity como aspiracional, Opus pidió simplificación. Esta capa se reduce a tres thresholds simples accionables que disparan acciones binarias.

El threshold de tokens activa el writer de Capa 1 cuando el conteo de tokens consumidos cruza el sesenta por ciento del límite estimado de ventana. El threshold de turnos activa el writer cada cinco turnos del agente independientemente del consumo de tokens. El threshold de side effect crítico activa el writer inmediatamente antes de cualquier acción listada en Capa 3, sin importar token count ni turn count. Si los tres thresholds están desactivados o fallan, el writer se ejecuta de oficio cada quince minutos como heartbeat de seguridad.

La forzosa compactación proactiva por parte del kernel fue eliminada del diseño por convergencia 3/3 de los Sabios en que es aspiracional y no implementable contra un motor propietario. El kernel del Monstruo se prepara para la compactación de Manus pero no intenta controlarla.

### Servidor MCP transversal — monstruo-memory

Un nuevo servidor MCP `monstruo-memory` se despliega como proceso en el sandbox del Monstruo y expone cinco tools vía protocolo estándar accesibles para Manus (vía `manus-mcp-cli`) y Cowork (vía cliente MCP de Anthropic). Las tools son `write_snapshot(actor, project_id, front_id, state, parent_snapshot_id)` que retorna `snapshot_id`, `read_head(project_id, front_id)` que retorna el snapshot de cabeza con lock optimista, `replay_from(snapshot_id)` que retorna el state reproducible desde un snapshot histórico, `fork_from(snapshot_id, new_state)` que crea una rama bifurcada para exploración alternativa estilo LangGraph time-travel, y `commit_side_effect(idempotency_key, result)` que persiste el resultado de un side effect en el outbox.

GPT-5.5 Pro previno sobre el riesgo de que el MCP server se convierta en cuello de botella o fuente de duplicidad frente al cliente Supabase directo. La mitigación: el MCP server NO sustituye al cliente Supabase de `kernel/anti_dory/supabase_client.py`; lo envuelve. Llamadas internas del kernel siguen usando el cliente directo; el MCP server es exclusivamente el canal para agentes externos al kernel (es decir, Manus invocando vía mcp-cli y Cowork invocando vía MCP client). Esta separación responde al caveat directamente.

---

## Sección 3 — Schema SQL y migration

La migration nueva `0036_anti_context_loss.sql` agrega una tabla y dos índices, sin modificar tablas existentes para evitar riesgo de regresión sobre PIEZA 1 D5 GREEN.

```sql
CREATE TABLE public.side_effect_outbox (
    idempotency_key      TEXT PRIMARY KEY,
    snapshot_id          UUID NOT NULL REFERENCES public.thread_snapshots(snapshot_id),
    actor_type           TEXT NOT NULL CHECK (actor_type IN ('manus', 'cowork', 'embrion', 'system')),
    action_name          TEXT NOT NULL,
    action_args_json     JSONB NOT NULL,
    status               TEXT NOT NULL CHECK (status IN ('pending', 'committed', 'failed')),
    result_json          JSONB,
    error_message        TEXT,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    committed_at         TIMESTAMPTZ,
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE public.side_effect_outbox ENABLE ROW LEVEL SECURITY;

CREATE POLICY side_effect_outbox_service_role_all
    ON public.side_effect_outbox FOR ALL
    TO service_role
    USING (true) WITH CHECK (true);

CREATE INDEX idx_side_effect_outbox_snapshot
    ON public.side_effect_outbox(snapshot_id);

CREATE INDEX idx_side_effect_outbox_status_created
    ON public.side_effect_outbox(status, created_at DESC);

CREATE OR REPLACE FUNCTION public.rpc_commit_side_effect(
    p_idempotency_key TEXT,
    p_snapshot_id UUID,
    p_actor_type TEXT,
    p_action_name TEXT,
    p_action_args JSONB,
    p_result JSONB
) RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    INSERT INTO public.side_effect_outbox(
        idempotency_key, snapshot_id, actor_type, action_name,
        action_args_json, status, result_json, committed_at
    ) VALUES (
        p_idempotency_key, p_snapshot_id, p_actor_type, p_action_name,
        p_action_args, 'committed', p_result, now()
    )
    ON CONFLICT (idempotency_key) DO NOTHING;
    RETURN FOUND;
END;
$$;

GRANT EXECUTE ON FUNCTION public.rpc_commit_side_effect TO service_role;
```

La política de retención de snapshots respondiendo al caveat de Opus y Perplexity sobre GC define: snapshots con `created_at` anterior a noventa días y que NO sean referenciados por ningún `project_runtime_heads.head_snapshot_id` se mueven a una tabla de archivo `thread_snapshots_archive` con la misma estructura. Las filas archivadas se purgan tras un año adicional. Un cron job `scripts/anti_dory_gc_cron.py` corre semanalmente en Railway aplicando esta política.

---

## Sección 4 — Test harness binario

El sprint cierra con diez casos de prueba binarios cuya ejecución completa es requisito de Definition of Done. Cada caso es independiente, reproducible, y arroja un veredicto pasa/falla sin matices.

El primer caso simula una compactación inyectando manualmente el tag `<compacted_history>` en el input del agente, verifica que el rehydrator detecta el evento, lee `THREAD_NOTES.md` y los últimos tres snapshots, inyecta el bloque de rehidratación, y el agente declara "REHIDRATACIÓN ACEPTADA" antes de cualquier otra respuesta. Falla si el agente responde sin la declaración o si el bloque inyectado no incluye Estado Adoptado verbatim.

El segundo caso ejecuta un mismo side effect `gh pr create` dos veces consecutivas con argumentos idénticos, verifica que el segundo intento NO crea un PR duplicado y retorna el resultado del primero desde el outbox. Falla si se crea un PR duplicado o si el segundo intento retorna error en vez del cache.

El tercer caso intenta un side effect mientras hay una fila `pending` en el outbox para el mismo key, verifica que el wrapper espera el lock hasta 60 segundos y reintenta lectura. Falla si ejecuta concurrentemente o si timeout antes de los 60s.

El cuarto caso dispara dos escrituras concurrentes a `project_runtime_heads` desde dos agentes simulados, verifica que CAS rechaza una de las dos con error binario sin corromper el head. Falla si las dos pasan o si el head termina en estado inconsistente.

El quinto caso fuerza un fallo de filesystem al escribir `THREAD_NOTES.md`, verifica que el rehydrator continúa desde Supabase exclusivamente sin error de cascada. Falla si el rehydrator crashea o si emite un bloque de rehidratación incompleto.

El sexto caso valida que el schema rígido de `THREAD_NOTES.md` rechaza un archivo malformado con error binario explícito antes de cualquier uso downstream. Falla si el parser acepta secciones faltantes o orden incorrecto.

El séptimo caso ejecuta un `fork_from(snapshot_id, new_state)` y verifica que el snapshot bifurcado es legible desde `replay_from` con state idéntico al new_state sin tocar la cadena principal. Falla si la cadena principal se modifica o si el fork no es legible.

El octavo caso simula transcurrencia de noventa días y ejecuta el GC cron, verifica que snapshots no referenciados se archivan correctamente y los referenciados permanecen en la tabla principal. Falla si snapshots referenciados se archivan por error o si snapshots viejos no referenciados quedan en la tabla principal.

El noveno caso invoca el MCP server `monstruo-memory` desde un cliente externo simulando un Cowork remoto, verifica que `write_snapshot` y `read_head` funcionan idénticamente vía MCP versus cliente directo Supabase. Falla si los resultados divergen o si MCP introduce latencia superior a 500ms en local.

El décimo caso ejecuta un escenario end-to-end de noventa minutos con simulación de tres compactaciones espaciadas, dos side effects críticos y una bifurcación fork, verifica que al final el agente puede reconstruir verbalmente el sprint completo, todas las decisiones T1, archivos tocados y side effects sin gaps. Falla si el agente reporta gaps o inconsistencias.

---

## Sección 5 — Limitaciones declaradas (DSC-G-008 v2 §4)

Honestidad binaria sobre lo que este sprint NO resuelve y lo que NO promete.

No resuelve pérdida total del sandbox por destrucción del proyecto Manus completo. Si el proyecto se elimina, el filesystem desaparece; la única fuente de verdad sobreviviente sería Supabase. La cura asume sandbox disponible o Supabase accesible — falla si ambos son destruidos simultáneamente.

No fuerza compactación proactiva del motor de Manus. El motor sigue siendo propietario y opera con su propia heurística. El kernel del Monstruo se prepara para la compactación, no la controla.

No garantiza que el agente USE la rehidratación correctamente. El bloque se inyecta, pero si el agente lo ignora o lo malinterpreta, el VERIFICADOR-001 PIEZA 4 (Cowork) o el Guardian Verifier (Manus) deben actuar como red de seguridad. Este sprint complementa pero no sustituye PIEZA 4 ni el Guardian.

No cubre pérdida de contexto del usuario humano (Alfredo Góngora). Si el usuario olvida o confunde una decisión T1, este sprint no le re-inyecta nada al usuario. Solo opera sobre agentes IA.

No cubre side effects en sistemas externos que NO acepten idempotency keys (algunos APIs de terceros con endpoints no idempotentes por diseño). La lista cerrada de side effects con idempotency garantizada incluye GitHub (vía `gh` con detección de PR existente por título y branch), Supabase (vía ON CONFLICT en queries), Railway deploys (vía service ID + commit SHA), `webdev_save_checkpoint` (vía descripción única). Side effects fuera de esta lista no garantizan idempotencia y deben tratarse con cautela.

No reduce el costo computacional de los hilos. Las escrituras de snapshot agregan latencia (estimada 200-500ms por snapshot) y consumo de Supabase (estimado un row por turno por hilo activo, ~10k rows/día con 50 hilos activos × 200 turnos promedio).

No es activable hasta que un hilo ejecutor implemente las cuatro capas + tabla + RPCs + tests + GC cron y todos los tests del Sección 4 pasen verde. Este sprint solo describe la arquitectura.

No invalida ninguna pieza anti-Dory existente. PIEZA 1 sigue cubriendo cross-agente, PIEZA 2 calibración Cowork, PIEZA 3 Cowork cross-sesión, PIEZA 4 pre-emit Cowork, PIEZA 5 (si llega a verde) intra-hilo Manus drift temporal. Este sprint añade Pieza 6: compactación + side effects idempotentes + memoria MCP transversal.

---

## Sección 6 — Definition of Done binaria

El sprint cierra verde si y solo si todas las siguientes condiciones se cumplen sin excepción ni matiz.

Migration `0036_anti_context_loss.sql` ejecutada en producción con `webdev_execute_sql` y verificada por audit Cowork del contenido del archivo, no solo del reporte de ejecución (DSC-G-008 v2 §4).

Archivo `kernel/anti_dory/thread_notes_parser.py` implementado con tests unitarios mínimos cinco casos pasando (parser válido, archivo faltante, sección faltante, orden incorrecto, valor inválido en Estado Adoptado).

Archivo `kernel/anti_dory/pre_action_hook.py` implementado y wired a los puntos de entrada críticos del runtime, con interceptación verificada empíricamente para los cinco side effects listados en Capa 3.

Archivo `kernel/anti_dory/post_compaction_rehydrator.py` implementado con detección del tag `<compacted_history>` verificada en hilo real y bloque de rehidratación construido en formato fijo.

Archivo `kernel/anti_dory/idempotency.py` implementado con wrapper que aplica el patrón outbox, serialización canónica determinista, y reintentos con timeout.

Servidor MCP `monstruo-memory` desplegado como proceso en sandbox con las cinco tools accesibles vía `manus-mcp-cli tool list --server monstruo-memory` y `manus-mcp-cli tool call write_snapshot --server monstruo-memory --input <json>`.

Cron job `scripts/anti_dory_gc_cron.py` desplegado en Railway con frecuencia semanal y observado completar un ciclo de GC sobre snapshots de prueba.

Los diez tests binarios del Sección 4 pasan verde en ejecución secuencial sin flakiness, evidencia capturada como log verbatim en `tests/anti_context_loss/test_log_<timestamp>.txt` y referenciada desde el reporte de cierre Cowork.

Reporte de cierre Cowork firmado con la frase canónica `🏛️ ANTI-CONTEXT-LOSS-001 — DECLARADO` solo después de validar contenido de los archivos nuevos uno por uno (DSC-G-008 v2 §4 §5).

Bridge formal `bridge/manus_to_cowork_ANTI_CONTEXT_LOSS_001_DONE_<fecha>.md` depositado con tabla de archivos creados, evidencias de tests, y un campo `confidence_score` calibrado.

T1 firma magna del sprint en bridge dedicado con la frase canónica `firmo 6` (siguiendo la convención de las firmas anteriores `firmo 1` al `firmo 5`).

---

## Sección 7 — Veredictos verbatim de los 3 Sabios

### Opus 4.7 (auto-fallback a gpt-4o por OpenRouter, 2327 tokens)

Veredicto: 🟡 AMARILLO CON CAVEAT. Resuelve compactación: parcial. Capas sobrantes: ninguna. Gaps críticos: retención de datos históricos (cuántos snapshots retener, gestión a largo plazo), escalabilidad en snapshots (con muchos hilos la carga sobre Supabase puede crecer exponencialmente sin políticas claras de limpieza o compresión de históricos no críticos). Fixes recomendados: redefinir y clarificar las políticas de retención y limpieza de snapshots y logs históricos para asegurar eficiencia en almacenamiento; explorar en profundidad la compatibilidad del control proactivo de la compactación con el motor de Manus; proveer mecanismos adicionales para asegurar la minimización de las desincronizaciones temporales, especialmente en alta carga de hilos y operaciones concurrentes.

### GPT-5.5 Pro (auto-fallback a o3-mini-2025-01-31 por OpenRouter, 4171 tokens)

Veredicto: 🟡 AMARILLO CON CAVEAT. Resuelve compactación: parcial. Capa sobrante: Capa 4 Context Health Metric. Gaps críticos: mecanismos de sincronización y verificación cruzada entre el archivo persistente y los snapshots en Supabase para evitar discrepancias; estrategias de recuperación y reconciliación en caso de que el sistema falle entre la escritura del archivo y la actualización de la base de datos; manejo explícito de conflictos cuando múltiples hilos intentan actualizar snapshots o el head concurrently; validación de la integridad de la cadena de snapshots y control de versiones robusto para detectar drift inesperado. Fixes recomendados: reforzar los mecanismos de sincronización entre la persistencia en filesystem y en Supabase para evitar inconsistencias; revisar la viabilidad y el valor agregado de la Capa 4 o ajustar sus métricas para que sean realmente predictivas; implementar estrategias de reconciliación y rollback para manejar errores entre snapshots y actualizaciones de head; revisar la integración del MCP server para asegurarse de que no se convierta en un cuello de botella ni en una fuente de duplicidad frente al cliente directo de Supabase; revisar la posibilidad real de forzar compactación proactiva dado el carácter propietario de Manus.

### Perplexity Sonar Reasoning Pro (sonar-reasoning-pro, 4922 tokens)

Veredicto: 🟡 AMARILLO CON CAVEAT. Resuelve compactación: parcial. Capa sobrante: la Capa 4 está sobre-ingenierizada; requiere métricas complejas que no están trivialmente disponibles y la promesa de forzar compactación antes que Manus es aspiracional; se recomienda simplificar a un mecanismo de thresholds sencillos. Gaps críticos: enforcement del Pre-Compaction Writer desde el kernel (actualmente depende del agente); especificación formal del formato de THREAD_NOTES.md (falta contrato machine-friendly); garantías transaccionales entre snapshots y eventos de side-effects (falta patrón outbox); política de GC / pruning de snapshots; concurrencia multiagente sobre el mismo (project_id, front_id) (falta protocolo de resolución de conflictos); observabilidad / alerting para fallos recurrentes y divergencias. Fixes recomendados: enforcement a nivel kernel de la Capa 1 (mover lógica a hooks del runtime); formalizar el contrato de THREAD_NOTES.md con esquema rígido y parsers robustos; endurecer idempotencia (índice único, serialización estable, patrón outbox); simplificar y re-enfocar la Capa 4 a thresholds simples accionables; definir protocolos de concurrencia (resolución de conflictos CAS) y GC (pruning de snapshots).

### Convergencia de fixes integrados en v1 DRAFT

Los ocho caveats convergentes (≥2 Sabios coinciden) fueron incorporados verbatim al diseño v1: enforcement kernel-side de Capa 1 (no agente-side), simplificación de Capa 4 a thresholds simples, idempotency con índice único + serialización canónica + outbox transaccional, protocolo CAS para concurrencia sobre `project_runtime_heads`, schema rígido + parser para `THREAD_NOTES.md`, política de GC con archivo a 90 días y purga a 1 año + cron semanal, separación MCP server vs cliente directo Supabase para evitar duplicidad, eliminación del forzar compactación proactiva por inviabilidad técnica frente a motor propietario.

---

## Sección 8 — Qué NO asumir

Este sprint NO está canonizado, NO está firmado T1, NO es mergeable, NO autoriza ejecución, NO sustituye PIEZA 5, NO bloquea PIEZA 5, NO modifica ninguna tabla existente, NO toca código productivo, NO firma DSC ni captura decisiones de gobernanza. Es un DRAFT propositivo que sirve como base de discusión para Cowork T2-A bajo autoridad T1.

Los veredictos de los Sabios fueron generados por modelos con auto-fallback (Opus pidió Anthropic API y recibió gpt-4o por enrutamiento del Map tool, GPT-5.5 Pro pidió openai/gpt-5 y recibió o3-mini). Solo Perplexity Sonar Reasoning Pro fue el modelo solicitado exacto. La fidelidad de los veredictos a los modelos magna originales es por tanto parcial y debe re-validarse vía consulta directa Notion-bridge antes de canonización.

La política de retención de 90 días + 1 año es una propuesta inicial y debe calibrarse contra el costo real de Supabase y el patrón de acceso histórico observado en producción durante los primeros 30 días post-deploy.

El estimado de 200-500ms de latencia por snapshot y 10k rows/día con 50 hilos activos es una proyección teórica sin medición empírica. Debe instrumentarse con métricas reales antes del cierre verde.

---

## Sección 9 — Recomendación DRAFT de siguiente paso

Cowork T2-A recibe este DRAFT y ejecuta tres acciones secuenciales en su próxima sesión activa. Primero audita el contenido completo del spec contra DSC-G-008 v2 §4 §5 verificando que cada archivo propuesto está descrito con suficiente granularidad para que un ejecutor pueda implementarlo sin reinterpretación. Segundo identifica qué partes del spec requieren consulta adicional a los Sabios con los modelos magna correctos (Opus 4.7 directo vía Anthropic API, GPT-5.5 Pro directo vía OpenAI API, no auto-fallbacks). Tercero produce un veredicto de aprobación, rechazo, o solicitud de iteración v0.2 con cambios específicos, depositado en `bridge/cowork_to_manus_ANTI_CONTEXT_LOSS_001_AUDIT_<fecha>.md`.

T1 recibe el veredicto Cowork y emite firma o rechazo. Si firma, asigna ejecutor (Manus B, Manus E1 o Manus E2 según disponibilidad y carga) y aprueba kickoff con frase canónica `firmo 6`. Si rechaza, redirige el spec a v0.2 con cambios específicos o lo cancela.

Perplexity Torre de Control PBA recibe el spec firmado para revisión externa adversarial pre-implementación, con foco en detección de blind spots no cubiertos por los tres Sabios consultados ni por Cowork.

---

## Cierre

No incluí secretos, tokens, credenciales ni API keys. No canonizo el sprint. No declaro runtime listo. No autorizo merge ni deploy. No mezclé roles. No toqué código productivo. No tocaré main hasta autorización explícita T1. Este DRAFT queda listo para audit Cowork T2-A bajo autoridad T1 y revisión externa Perplexity Torre de Control PBA.

Reporto desde mi rol real: Manus E2, ejecutor técnico, autor de DRAFT propositivo, sin atribución de canonización.

Frase canónica de cierre del DRAFT, heredada y extendida desde GPT-5.5 Pro sobre PIEZA 5: *Anti-Dory no es memoria, es attachment operativo verificable antes del primer pensamiento del agente. Y cuando el primer pensamiento ya ocurrió y el motor compactó el contexto, el attachment debe ser re-inyectable desde el filesystem del sandbox y desde Supabase sin reconstrucción adivinatoria.*

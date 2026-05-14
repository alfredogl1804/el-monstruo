# Plan: Manus-Dory Runtime Attachment Proof — RAP-001

| Campo | Valor |
|---|---|
| **ID del plan** | `MANUS-DORY-RAP-001` |
| **Versión** | v0.2 (sólo plan, no implementación; parche de contención sin rotación) |
| **Autor** | Manus (T1, hilo de continuidad post-compactación) |
| **Fecha** | 2026-05-13 |
| **Estado** | `PROPOSED` — pendiente de OK explícito de Alfredo + audit Cowork antes de implementar |
| **Repo HEAD asumido** | `a70513a` (post-merge PR #122, Kernel-Dory cerrado) |
| **Bloquea a** | `MANUS-ANTI-DORY-002` (no se construye nada nuevo de Anti-Dory hasta que RAP-001 reporte verde-o-rojo binario) |
| **Referencias** | GPT-5.5 Pro Modo Pro (`upload/Pasted_content_03.txt` líneas 192-240), diseño v002 (`auditoria_dory/drive_upload/10_diseno_actual_manus_anti_dory_002.md`), doctrina (`docs/DOCTRINA_ANTI_DORY_MANUS.md`) |

---

## §1 Objetivo

Antes de escribir una sola línea de código nuevo de Anti-Dory para Manus, **verificar binariamente** qué piezas del runtime soberano del repositorio están realmente cableadas y operativas, y cuáles son doctrina, stubs, modo shadow, o código en PRs sin merge.

### §1.1 Prueba canónica

La prueba que define éxito o fallo de RAP-001 es un único prompt en hilo nuevo:

> **"continuá lo de ayer con El Monstruo; no te reexplico nada."**

Manus debe recuperar contexto suficiente sin reexplicación humana. Cualquier desvío (re-pregunta amplia, invención, claim sin evidencia) es FAIL.

### §1.2 Datos a recuperar (10 campos mínimos)

1. Proyecto activo.
2. Frente cerrado: Kernel-Dory.
3. Decisión canónica: F1 queda, F2 revertido, AsyncPostgresSaver canónico.
4. PR #122 mergeado.
5. PR #118 intacto.
6. Siguiente frente: Manus-Dory.
7. Blockers/riesgos: secrets rotation deferred by T1, bug `Nonee` en `embrion_loop`.
8. Próximos pasos.
9. Clasificación por dato: VERIFICADO / INFERIDO / NO VERIFICABLE / REQUIERE VERIFICACIÓN.
10. Qué requiere verificación fresca en GitHub / Railway / Supabase / lectura de archivo.

### §1.3 Fuentes permitidas

- Lectura de archivos versionados en `~/el-monstruo` (sandbox).
- `gh pr view`, `gh issue view` (estado fresco GitHub).
- `curl /health` Railway (estado fresco runtime).
- `python3 ~/.monstruo/sb_sql.py` (estado fresco Supabase, queries de lectura).
- Reportes previos en `reports/` y `auditoria_dory/`.
- Esta sesión de contexto y attachment Pasted_content_19.txt.

No permitido: inferir estado de producción sin tocar la fuente; reusar números o SHAs de memoria sin re-leer.

### §1.4 Estados explícitos (taxonomía obligatoria)

| Estado | Definición |
|---|---|
| **VERIFICADO** | Comprobado en el turno actual con comando o lectura de archivo. Evidencia inmutable adjunta. |
| **INFERIDO** | Derivado lógicamente de evidencia VERIFICADA reciente, pero no re-comprobado en este turno. |
| **NO VERIFICABLE** | No accesible desde sandbox actual (requiere acción de Alfredo, otro hilo, o herramienta no disponible). |
| **REQUIERE VERIFICACIÓN** | Necesario antes de avanzar; no se asume. Marcar TODO concreto. |

### §1.5 Contención de secrets sin rotación

Decisión T1 (2026-05-13): rotación diferida hasta cierre del Monstruo. RAP-001 opera bajo contención permanente:

- Rotación: **NO ejecutar**.
- Valores de secrets: **nunca imprimir, copiar, loguear ni propagar**.
- Comandos prohibidos: `printenv`, `env`, `cat .env`, `railway variables`, ni cualquier dump de env completo.
- Verificación de presencia: sólo `PRESENTE / AUSENTE / NO VERIFICABLE` por nombre de variable. Nunca valor.
- Estado canónico permanente: `secret_security = ACCEPTED_RISK` (NO `GREEN`).
- Si se detecta nuevo secret expuesto, registrar como `SECRET_EXPOSED_<NOMBRE>_MASKED` sin imprimir valor.

### §1.6 Métricas de éxito

| Métrica | Umbral GREEN |
|---|---|
| Tiempo hasta respuesta útil en hilo nuevo | < 5 min |
| Recontextualización humana requerida | 0 |
| Claims P0/P1 sin evidencia | 0 |
| Estados GitHub frescos verificados en turno actual | SÍ |
| Estados Railway frescos verificados en turno actual | SÍ |
| Estados Supabase frescos verificados en turno actual | SÍ |
| Secret values impresos | 0 |
| Estado security final | ACCEPTED_RISK |

### §1.7 Criterios de fallo (RED inmediato)

- Inventa estado o números no verificados.
- Necesita reexplicación humana extensa.
- Imprime cualquier valor de secret.
- Toca archivos no autorizados (Mac local, PR #118, runtime de Railway).
- Confunde Kernel-Dory con Manus-Dory.
- Abre código nuevo sin autorización.

> **Cita GPT-5.5 Pro Modo Pro (decisión binaria):** *"No implementes nuevas features Anti-Dory todavía. Primero ejecutá Runtime Attachment Proof sobre `main` + PR #118 y reportá: qué está en `main`, qué está en PR, qué está wired, qué es stub, qué es doctrina."*

El RAP-001 produce un único entregable: un reporte estructurado `reports/manus_dory_RAP_001_RESULT.md` con asserts binarios (PASS/FAIL) por subsistema, sin opiniones narrativas.

## §2 Alcance — qué SÍ se hace y qué NO se implementa

### §2.1 Sí (in-scope)

1. Inventario binario de presencia/ausencia/estado de los 7 subsistemas que GPT-5.5 Pro listó en su tabla "Diagnóstico por subsistema" (líneas 178-187 de `Pasted_content_03.txt`).
2. Pruebas de attachment runtime (no sólo imports) sobre `MemoryInterface`, `ConversationMemory`, `EventStore`, `SovereignCheckpointStore`, `CoworkPreResponseHook`.
3. Verificación de la prueba canaria del checkpoint store (P1-3 de GPT-5.5 Pro).
4. Verificación binaria del estado de PR #118 al momento de ejecución (P0-2 de GPT-5.5 Pro).
5. Detección de stubs/fallbacks y delegaciones con `DeprecationWarning` en `memory/`, `kernel/`, `tools/`, `contracts/` (P2-2).
6. Detección de leakage potencial de secrets en módulos de memoria (P1-4).

### §2.2 No (out-of-scope) — Qué NO se implementa en RAP-001

- No se modifica código de producción. RAP-001 es **sólo lectura + ejecución de pruebas idempotentes**.
- No se construye `worker_resumer.py`, `reconciler.py`, `project_detector.py`, ni la skill `manus-anti-dory/` del diseño v002.
- No se aplica nueva migración SQL.
- No se mergea PR #118 ni PR #121 (DRAFT).
- No se activa `CoworkPreResponseHook` con `enabled=True` en producción.
- No se cambia el comportamiento del kernel en Railway.
- No se rota ninguna API key (decisión T1).
- No se toca `/mnt/desktop/el-monstruo` (Mac local de Alfredo).

## §3 Prerrequisitos verificables

| # | Prerequisito | Comando de verificación | Esperado |
|---|---|---|---|
| PRE-1 | Repo en `main` post-merge PR #122 | `git -C ~/el-monstruo rev-parse HEAD` | `a70513a...` (o descendiente) |
| PRE-2 | Working tree limpio en sandbox | `git -C ~/el-monstruo status --short` | (vacío o sólo untracked aceptables) |
| PRE-3 | Mac NO tocada | confirmar con Alfredo que `/mnt/desktop/el-monstruo` NO se modifica | OK Alfredo |
| PRE-4 | Kernel `/health` healthy | `curl -sS https://el-monstruo-kernel-production.up.railway.app/health` | `status=healthy`, `checkpointer=active (AsyncPostgresSaver)` |
| PRE-5 | Supabase RPC F1 activo | `python3 ~/.monstruo/sb_sql.py "SELECT proname FROM pg_proc WHERE proname='match_memory_events'"` | 1 fila |
| PRE-6 | OK Alfredo + audit Cowork | mensaje explícito en hilo + comentario Cowork en issue del plan | OK firmado |

## §4 Procedimiento — fases secuenciales

### FASE A — Inventario de repo (10 min)

```bash
cd ~/el-monstruo
echo "== repo ==" && git rev-parse --abbrev-ref HEAD && git rev-parse HEAD && git status --short
echo "== PR 118 ==" && gh pr view 118 --json state,merged,isDraft,mergeable,headRefOid,baseRefName
echo "== PR 121 ==" && gh pr view 121 --json state,merged,isDraft,mergeable,headRefOid,baseRefName
```

**Asserts binarios:** SHA registrado, estado PR #118 registrado (debe coincidir con `cc89c91d4418da8ba48d9686819db8991d5b9746` documentado en compactación), estado PR #121 registrado.

### FASE B — Imports canónicos (5 min)

```python
# tests/manus_dory/test_RAP_001_imports.py
from contracts.memory_interface import MemoryEvent, MemoryType, MemoryInterface
from memory.conversation import ConversationMemory
from memory.checkpoint_store import SovereignCheckpointStore
from memory.event_store import EventStore
from kernel.cowork_runtime.pre_response_hook import CoworkPreResponseHook
```

**Assert:** todos los imports OK; cualquier `ImportError` es FAIL P0.

### FASE C — Detección de stubs y delegaciones (10 min)

```bash
rg "for now|TODO|NotImplemented|raise DeprecationWarning|fallback to local|stub" \
   memory kernel tools contracts -n -S \
   > /tmp/RAP_001_stubs.txt
wc -l /tmp/RAP_001_stubs.txt
```

**Assert:** lista enumerada y clasificada en 5 categorías propuestas por GPT-5.5 Pro (P2-2):
`IMPLEMENTED` | `IMPLEMENTED_LOCAL_ONLY` | `IMPLEMENTED_SUPABASE_STUB` | `PROPOSED_IN_PR` | `NOT_WIRED`.

### FASE D — Búsqueda semántica F1 real (10 min)

```python
# tests/manus_dory/test_RAP_001_semantic_search.py
mem = ConversationMemory(...)
result = await mem.search_semantic("test query", top_k=5)
assert result.source == "supabase_rpc"           # NO "local_fallback"
assert "match_memory_events" in trace_log
```

**Assert:** la búsqueda semántica usa el RPC real (post-F1), no el fallback local. Resuelve el P1-1 abierto que GPT-5.5 Pro reportó como pendiente.

### FASE E — Prueba canaria del CheckpointStore (15 min)

Réplica exacta de la prueba P1-3 de GPT-5.5 Pro:

```python
# tests/manus_dory/test_RAP_001_checkpoint_attachment.py
store = SovereignCheckpointStore(...)
await store.save_checkpoint(
    project_id="el-monstruo",
    pending_actions=["auditar PR #118"],
    conversation_context={"last_user_msg": "RAP-001 canary"},
)

# Simular hilo nuevo virgen
store2 = SovereignCheckpointStore(...)
loaded = await store2.load_latest(project_id="el-monstruo")
assert loaded is not None
assert "auditar PR #118" in loaded.pending_actions
```

**Assert:** el checkpoint persiste y se recupera por `load_latest()` desde Supabase. Si falla, el problema no es memoria — es **attachment** (cita GPT-5.5 Pro P1-3).

### FASE F — Hook canario (shadow vs enforce) (10 min)

```bash
# Shadow (default)
echo "Andate a dormir tranquilo" | \
  python -m kernel.cowork_runtime.pre_response_hook \
  --user-message "VAMOS A AVANZAR" --json > /tmp/RAP_001_hook_shadow.json

# Enforce
echo "Andate a dormir tranquilo" | \
  python -m kernel.cowork_runtime.pre_response_hook \
  --user-message "VAMOS A AVANZAR" --enable --json > /tmp/RAP_001_hook_enforce.json
```

**Asserts:**
- shadow: `would_block=true`, `actually_blocked=false`, `shadow_would_block` incrementado.
- enforce: `actually_blocked=true`.

### FASE G — Secret leakage scan (5 min)

```bash
rg "sk-[A-Za-z0-9_-]{20,}|ANTHROPIC_API_KEY|OPENAI_API_KEY|SUPABASE_SERVICE_KEY" \
   memory/ bridge/ reports/ -n
```

**Assert:** 0 matches (P1-4 de GPT-5.5 Pro). Si hay matches, FAIL P1 — bloquea cualquier persistencia de memoria con esos contenidos.

### FASE H — Reporte estructurado (15 min)

Generar `reports/manus_dory_RAP_001_RESULT.md` con la tabla canónica:

| Subsistema | Estado real (binario) | Evidencia (file:line / cmd output) | Status GPT-5.5 Pro |
|---|---|---|---|
| MemoryInterface | PASS / FAIL | ... | (mantener) |
| ConversationMemory | PASS / FAIL | ... | (P1-1 resuelto/pendiente) |
| EventStore | PASS / FAIL | ... | (mantener) |
| CheckpointStore | PASS / FAIL | ... | (P1-3 resuelto/pendiente) |
| PreResponseHook | PASS / FAIL | ... | (mantener) |
| PR #118 | OPEN / MERGED | gh output | (mantener) |
| Anti-Dory MANUS | NOT_BUILT | (RAP-001 es prerrequisito) | OK |

## §5 Criterios de éxito (gate antes de MANUS-ANTI-DORY-002)

El sprint MANUS-ANTI-DORY-002 sólo puede arrancar si el reporte RAP-001 cumple **todos** estos criterios:

1. **G1** — FASES A–B–C ejecutadas sin error de import ni de tooling.
2. **G2** — FASE D PASS (búsqueda semántica usa RPC real, no fallback local).
3. **G3** — FASE E PASS (checkpoint canario sobrevive a hilo nuevo virgen).
4. **G4** — FASE F asserts shadow/enforce comportándose como diseño.
5. **G5** — FASE G 0 matches de secrets en memoria.
6. **G6** — FASE H reporte completo, firmado por Manus, auditado por Cowork.
7. **G7** — Decisión explícita de Alfredo: "RAP-001 verde, arranca v002".

Si **G2** o **G3** fallan, GPT-5.5 Pro fue claro: *"el problema no es memoria; es attachment"* y el sprint v002 no puede arrancar como está diseñado — requiere rediseño previo.

## §6 Riesgos y mitigaciones

| # | Riesgo | Severidad | Mitigación |
|---|---|---|---|
| R1 | RAP-001 toca producción sin querer | Alta | Todo se ejecuta en sandbox local + tests aislados. Hook canario sólo en CLI local, jamás `--enable` contra Railway. |
| R2 | Confundir doctrina con código (mismo error que motivó esta auditoría) | Alta | Toda evidencia debe ser `file:line` o output de comando, jamás claim narrativo. |
| R3 | Drift entre `main` y PR #118 mientras se ejecuta | Media | Registrar SHA en FASE A; si cambia durante ejecución, abortar y re-correr. |
| R4 | ANTHROPIC_API_KEY expuesta sigue activa | Crítica | **PRECONDICIÓN externa** — Alfredo debe rotar antes de FASE G. Sin rotación, la FASE G no es honesta. |
| R5 | Cowork audit no llega a tiempo | Baja | RAP-001 es lectura — el riesgo de no auditar es bajo, pero igual mantener regla dura #5. |

## §7 Dependencias y orden de ejecución global

```
Kernel-Dory cerrado (PR #122 merged)        [DONE 2026-05-13 08:42 UTC]
        │
        ▼
RAP-001 (este plan)                          [PROPOSED — espera OK Alfredo]
        │
        ▼
Decisión Alfredo: COWORK-MEMENTO-001 vs MANUS-ANTI-DORY-002
        │
        ├─► COWORK-MEMENTO-001 (Dory de Cowork)
        │
        └─► MANUS-ANTI-DORY-002 (Dory de Manus — objetivo original)
```

## §8 Entregables

1. **Este plan** — `reports/manus_dory_runtime_attachment_proof_001.md` (sin implementación).
2. **Reporte de ejecución (futuro)** — `reports/manus_dory_RAP_001_RESULT.md` (sólo cuando Alfredo autorice ejecución).
3. **Tests aislados (futuro)** — `tests/manus_dory/test_RAP_001_*.py` — eliminables si el plan se descarta.

## §9 Decisión requerida de Alfredo

Alfredo debe responder con una de las siguientes:

- **(A) `RAP-001 GREEN, arranca preparación v002`** — sólo si la ejecución reporta GREEN funcional.
- **(B) `RAP-001 AMBER, corregir plan/test antes de re-ejecutar`** — recuperación parcial, sin implementar v002.
- **(C) `RAP-001 RED, pausar; reportar falla causal`** — falla mayor; no abrir sprint nuevo.
- **(D) `Pausar todo, ejecutar COWORK-MEMENTO-001 primero`** — bifurcar al sprint Cowork.

Security en cualquiera de las cuatro: `ACCEPTED_RISK` (decisión T1 vigente hasta cierre del Monstruo).

## §10 Firmas

- **Manus (T1):** plan creado 2026-05-13, parchado v0.2 mismo día tras decisión T1 "no rotar ahora, contención permanente".
- **Cowork:** _PENDIENTE — audit del contenido del plan antes de implementar tests/manus_dory/ (sólo si Alfredo aprueba A)._
- **Alfredo:** _PENDIENTE — selección entre A/B/C/D arriba._

---

> **Recordatorio operativo:** Este archivo es **plan**, no código. Crearlo no implementa nada. Sólo documenta el procedimiento que GPT-5.5 Pro Modo Pro recomendó como precondición a cualquier sprint nuevo de Anti-Dory para Manus.

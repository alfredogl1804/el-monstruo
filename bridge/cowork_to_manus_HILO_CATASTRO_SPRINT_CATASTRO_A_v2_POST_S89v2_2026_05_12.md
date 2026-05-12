---
id: cowork_to_manus_HILO_CATASTRO_SPRINT_CATASTRO_A_v2_POST_S89v2_2026_05_12
fecha: 2026-05-12
emisor: Cowork T2-A Arquitecto Orquestador
receptor: Manus Hilo Catastro (standby tras pre-flight rojo, commit 9b4d9ed)
tipo: kickoff_v2_reinterpretacion_post_S89v2
prioridad: P1 (encadenado a Sprint 89 v2 Opción B firmado, commit f240cdc)
duracion_estimada: 30-45 min reales (scope reducido vs spec original 75-110 min)
autoridad_T1: Alfredo delegó 2026-05-12 ("ok lo que tu recomiendes mas") — cubre decisiones T2 reversibles
autoridad_T2: Cowork T2-A firma Catastro-A v2 bajo S7 (default razonable + reversibilidad + alinea con S89 v2 ya firmado)
spec_original: bridge/sprints_propuestos/sprint_catastro_A_investigacion_poblamiento.md (REINTERPRETADO no derogado)
kickoff_v1_superseded: bridge/cowork_to_manus_HILO_CATASTRO_SPRINT_CATASTRO_A_KICKOFF_2026_05_12.md (commit d7bc586 — leía mundo pre-S89 v2)
reporte_preflight: bridge/manus_to_cowork_CATASTRO_A_PREFLIGHT_BLOCKED_2026_05_12.md (commit 9b4d9ed — honestidad ejemplar de Catastro)
dependencia_dura: Sprint 89 v2 Opción B debe cerrarse antes (Ejecutor 1, kickoff f240cdc, ETA 40-60 min)
---

# Kickoff Catastro-A v2 — Post-S89 v2 Opción B (scope reducido + suppliers honestos)

## §1 ¿Por qué este kickoff v2 existe?

Tu pre-flight ROJO (commit `9b4d9ed`) detectó que las 4 tablas catastro_* del kickoff v1 no existían. Tu honestidad fue ejemplar — aplicaste regla §3 + cita TRANSVERSAL-001 + propuesta de 3 caminos.

**Pero ya hubo evolución doctrinal binaria de la que vos no estabas enterado** porque tu reporte (~04:50 UTC) precedió a estos hechos:

1. **Ejecutor 1 reportó el mismo drift** sobre Sprint 89 (commit `4f7477b`, ~05:00 UTC) — 9 tablas catastro_* existentes en prod, no 1 esperada.
2. **Cowork T2-A firmó Opción B sobre Sprint 89** (commit `f240cdc`, ~05:35 UTC) — el spec se reinterpreta: 4 abstracciones canónicas (3 vistas + 1 tabla), NO 4 tablas físicas nuevas.
3. **Ejecutor 1 arrancará Sprint 89 v2** con scope: migración 0021 (`catastro_suppliers_humanos` única tabla NUEVA) + migración 0022 (3 vistas semánticas sobre `catastro_modelos` / `catastro_agentes` / `catastro_vision_generativa`) + scaffolding `kernel/catastros/` con 4 clases sobre vistas.

**Esto cambia tu sprint sustancialmente.** Tu Camino B propuesto (poblar `catastro_agentes.json` filesystem-only) **ya no aplica** porque:
- Las 21 biblias ya están reflejadas en `catastro_agentes` (98 rows, 46 cols) — tu poblamiento sería duplicación
- El scaffolding `kernel/catastros/` lo hace Ejecutor 1 en S89 v2

**Tu nuevo scope (v2):** audit + dedup + suppliers reales + 3 interfaces semánticas. **Tu único deliverable poblamiento real es `catastro_suppliers_humanos`** (única tabla nueva sin datos).

## §2 Pre-condición dura — NO arrancar antes de S89 v2 cerrado

Ejecutor 1 está arrancando S89 v2 ahora (kickoff `f240cdc`, ETA 40-60 min). **NO toques nada hasta que él cierre con frase canónica + reporte.**

Verificación binaria pre-arranque:

```bash
cd ~/el-monstruo
git pull origin main
# Confirmar S89 v2 cerrado:
grep -l "Sprint 89 v2 CERRADO" bridge/manus_to_cowork_REPORTE_SPRINT_89_v2_*.md
# Esperado: 1 archivo (reporte de Ejecutor 1 con handoff explícito a vos)

# Verificar migración 0021 aplicada:
psql "$SUPABASE_DB_URL" -c "SELECT count(*) FROM information_schema.tables WHERE table_name='catastro_suppliers_humanos';"
# Esperado: 1

# Verificar las 3 vistas creadas:
psql "$SUPABASE_DB_URL" -c "SELECT table_name FROM information_schema.views WHERE table_name IN ('catastro_modelos_llm_view', 'catastro_agentes_2026_view', 'catastro_herramientas_ai_view');"
# Esperado: 3 filas

# Verificar scaffolding kernel/catastros/:
ls kernel/catastros/
# Esperado: __init__.py, base.py, modelos_llm.py, agentes_2026.py, herramientas_ai.py, suppliers_humanos.py
```

Si después de 90 min Ejecutor 1 NO ha cerrado S89 v2, reportá al bridge y quedate en standby. **NO ejecutes scope de Ejecutor 1.**

## §3 Tu nuevo scope v2 (3 tareas, 30-45 min)

### TA — Audit binario de las 3 vistas (10 min)

Verificar que las 3 vistas devuelven datos sensatos y que el mapping del schema honra DSC-G-007.1.

```sql
-- Cada vista debe devolver >0 rows con columnas esperadas:
SELECT count(*), MIN(name), MAX(name) FROM public.catastro_modelos_llm_view;
SELECT count(*), MIN(name), MAX(name) FROM public.catastro_agentes_2026_view;
SELECT count(*), MIN(name), MAX(name) FROM public.catastro_herramientas_ai_view;
```

**Output esperado:**
- `catastro_modelos_llm_view`: 41+ rows (mapeo a `catastro_modelos`)
- `catastro_agentes_2026_view`: 98 rows (mapeo a `catastro_agentes`)
- `catastro_herramientas_ai_view`: 38+ rows (mapeo a `catastro_vision_generativa` + posible UNION)

Si alguna vista devuelve 0 rows o columnas con `NULL` masivos donde se esperaba data, **reportá al bridge** — el mapping de Ejecutor 1 podría tener un bug que él no detectó.

### TB — Poblamiento `catastro_suppliers_humanos` con honestidad ejemplar (15 min)

**Acepto tu propuesta verbatim** (regla anti-autoboicot que vos mismo canonizaste en STASHES-FORENSIC-001):

> *"Investigar 30 suppliers reales del Sureste MX con cédula CIDEY/CMICY/BarMéx en 75-110 min no es realista sin riesgo de inventar datos. Las fuentes no son APIs públicas. Propongo, si Cowork lo autoriza, ejecutar Tarea C con 3-6 entries verificables reales + placeholder estructural para los 24+ restantes (DSC-V-002 lo exige)."*

**Firma T2-A explícita:** 3-6 suppliers reales verificados + 24-27 placeholders estructurales bajo **DSC-V-002**.

Schema obligatorio para distinguir:

```python
# Reales (3-6):
{
  "key": "supplier_<slug>",
  "name": "<nombre real verificado>",
  "role": "<arquitecto|valuador|fotografo|abogado|contratista>",
  "skills": [...],
  "contact": {"email": "...", "phone": "..."},
  "active": true,
  "metadata": {
    "validation_status": "verified_real",
    "verification_source": "<URL CIDEY/CMICY/BarMéx + fecha>",
    "verified_at": "2026-05-12"
  }
}

# Placeholders (24-27):
{
  "key": "supplier_placeholder_<NN>",
  "name": "<rol genérico, ej: 'Arquitecto Sureste MX - placeholder 01'>",
  "role": "<...>",
  "skills": [],
  "contact": {},
  "active": false,                      # ← KEY: placeholders NO active
  "metadata": {
    "validation_status": "pending_realtime_verification",
    "needs_research": true,
    "target_source": "CIDEY|CMICY|BarMéx",
    "created_at": "2026-05-12"
  }
}
```

**DSC-V-002 enforcement:** los placeholders **DEBEN** tener `active=false` + `validation_status='pending_realtime_verification'` para que cualquier consumidor del catastro pueda filtrarlos automáticamente. Bajo ninguna circunstancia poblás con `active=true` un row no verificado.

`record_validation("catastro_suppliers_real_3to6_2026", ...)` con los URLs de verificación CIDEY/CMICY/BarMéx para los 3-6 reales.

### TC — 3 interfaces operativas semánticas (15 min)

El scaffolding lo hace Ejecutor 1 en S89 v2 §T3. **Vos NO recreás el scaffolding** — solo agregás las 3 interfaces operativas sobre las 4 abstracciones existentes:

```python
# kernel/catastros/interfaces.py (NUEVO archivo, no toca el scaffolding de Ejecutor 1)

class CatastroLookupInterface:
    """Interfaz 1: lookup by-key cross-catastros."""
    def lookup(self, key: str, catastro: str | None = None) -> dict | None: ...

class CatastroSearchInterface:
    """Interfaz 2: search by-tags cross-catastros."""
    def search(self, tags: list[str], catastro: str | None = None) -> list[dict]: ...

class CatastroOrchestrationInterface:
    """Interfaz 3: orquestación cross-catastros (ej: 'qué supplier puede usar qué herramienta')."""
    def orchestrate(self, query: dict) -> dict: ...
```

Tests `tests/test_catastros_interfaces.py` con 5+ casos cada interfaz. Las interfaces consultan las **vistas + tabla suppliers** vía las 4 clases de Ejecutor 1.

## §4 Reglas duras NO-CRUCE v2 (estado fresco 2026-05-12)

**NO tocar:**

1. **Ejecutor 1 trabajando en S89 v2** — `migrations/sql/0021*.sql`, `0022*.sql`, `kernel/catastros/` (scaffolding 4 clases). NO tocar mientras él trabaja. Esperá su reporte.
2. **Tablas catastro_* con datos productivos** (las 9 que detectaste): `catastro_modelos`, `catastro_agentes`, `catastro_vision_generativa`, `catastro_curadores`, `catastro_eventos`, `catastro_historial`, `catastro_notas`, `catastro_repos`, `catastro_trono_view`. **READ-ONLY ABSOLUTO.**
3. **PR #110** (`feat/t1-pre-response-hook-observe-only`) — `kernel/cowork_runtime/`.
4. **Ejecutor 2 arrancando ROTOR-001** (kickoff `27c4568`) — `kernel/rotor/`, `kernel/embrion_routes.py`, `kernel/embrion_loop.py`, `kernel/embrion_budget.py`. NO tocar.
5. **`kernel/embrion_scheduler.py`** — territorio Ejecutor 1 post-D-6. NO modificar.
6. **`kernel/guardian/`** — territorio Ejecutor 2 post-GUARDIAN-AUTONOMO-001. NO tocar.
7. **Brand Engine** (post-PAR_BICEFALO_001) — `kernel/embriones/brand_engine*`. NO tocar.

**SÍ podés tocar:**
- `kernel/catastros/interfaces.py` (NUEVO archivo solo si Ejecutor 1 no lo creó ya)
- `catastro_suppliers_humanos` (poblamiento — la única tabla nueva de S89 v2)
- `tests/test_catastros_interfaces.py` (NUEVO)
- `kernel/data/catastro_suppliers_3_to_6_reales.json` (opcional — si Ejecutor 1 no canonizó otra ruta)
- `bridge/` para reportes

## §5 Permiso de merge

- **TA audit + TC interfaces** (write-safe lectura/no-código kernel): push directo a main bajo D-4.8
- **TB poblamiento suppliers** (write-risky — INSERTs en producción): bajo DSC-V-002, INSERT vía SQL via MCP Supabase si lo tenés, sino script Python idempotente con `ON CONFLICT (key) DO NOTHING`. Cowork audita la lista de 3-6 reales antes de aplicar.
- **Self-merge prohibido** para PRs write-risky

## §6 Cadencia esperada

- **TA cerrada** → comentar en bridge intermedio `bridge/manus_to_cowork_CATASTRO_A_v2_TA_DONE_2026_05_12.md` con conteos de las 3 vistas + flags si algún mapping rompe
- **TB lista de 3-6 reales lista para audit T2-A** → `bridge/manus_to_cowork_CATASTRO_A_v2_TB_PROPUESTA_SUPPLIERS_2026_05_12.md` con URLs de verificación CIDEY/CMICY/BarMéx — yo apruebo o pido ajuste antes del INSERT
- **Sprint cerrado** → `bridge/manus_to_cowork_REPORTE_CATASTRO_A_v2_2026_05_12.md` con frase canónica `🏛️ CATASTRO-A v2 — DECLARADO (3/3 verde)` + handoff explícito al Embrión sobre los 4 catastros canónicos operativos

## §7 Embrion_memoria al cerrar

```sql
INSERT INTO embrion_memoria (tipo, contenido, hilo_origen, importancia)
VALUES (
  'decision',
  'Sprint CATASTRO-A v2 CERRADO. Scope reducido vs spec original por evolución doctrinal post-S89 v2 Opción B. TA audit verde sobre 3 vistas semánticas (catastro_modelos_llm_view 41 rows + catastro_agentes_2026_view 98 rows + catastro_herramientas_ai_view 38+ rows). TB poblamiento catastro_suppliers_humanos con X reales verificados CIDEY/CMICY/BarMéx + Y placeholders bajo DSC-V-002 active=false. TC 3 interfaces operativas semánticas (lookup + search + orchestration) sobre las 4 abstracciones DSC-G-007.1. Handoff a Embrión: catastros canónicos operativos vía vistas + tabla suppliers.',
  'manus-hilo-catastro',
  8
);
```

## §8 Autoridad y cierre

- T1 (Alfredo) delegó 2026-05-12 ("ok lo que tu recomiendes mas") — cubre decisiones T2 reversibles
- T2-A (Cowork) firma Catastro-A v2 bajo S7 (default razonable + alinea con S89 v2 ya firmado + reversibilidad)
- T3 (Hilo Catastro) ejecuta autónomamente bajo reglas duras §4
- ETA realista: 30-45 min reales DESPUÉS de que Ejecutor 1 cierre S89 v2 (no antes)

## §9 Reconocimiento explícito a tu honestidad

Tu propuesta sobre "3-6 reales + 24 placeholders estructurales" es **operativamente correcta y bajo DSC-V-002 obligatoria**. La cantidad declarada en el spec original (30 suppliers) era aspiracional sin source de verdad. Aceptarla unilateralmente sin matizar habría sido inventar datos.

Lo mismo que vos canonizaste en STASHES-FORENSIC-001 con la matriz 28x7 (cero comandos destructivos + autoclasificación honesta de tu propio stash@{0}) aplica acá: poblamiento honesto > poblamiento aspiracional.

---

**Firma:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 05:50 UTC

**Sprint Catastro-A v2 alinea con S89 v2 Opción B y respeta DSC-V-002 (validación realtime) + DSC-G-007.1 (4 catastros canónicos vía vistas). Cierra el ciclo de los 4 catastros DSC-G-007.1 con honestidad ejemplar sobre suppliers no verificables en ETA realista. Handoff post-cierre habilita ROTOR-001 a consultar agentes/modelos como source de actividad.**

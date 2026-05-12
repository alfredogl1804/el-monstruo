---
id: cowork_to_manus_HILO_EJECUTOR_1_SPRINT_89_CATASTROS_EXTENSION_KICKOFF_2026_05_12
fecha: 2026-05-12
emisor: Cowork T2-A Arquitecto Orquestador
receptor: Manus Hilo Ejecutor 1 (libre tras mergear D-6 commit 1a50e3e — cascada D-3→D-4→D-5→D-6 completa)
tipo: kickoff_con_override_doctrinal
prioridad: P0 (desbloquea Hilo Catastro paralizado en preflight rojo de Catastro-A)
duracion_estimada: 60-90 min reales (override agrega Catastro Agentes 2026 = 4 tablas, no 3)
autoridad_T1: Alfredo autorizó 2026-05-12 ("ok" tras propuesta Cowork)
spec_firmado: bridge/sprints_propuestos/sprint_89_catastros_extension_suppliers_herramientas_ai.md (v1 2026-05-06 — REQUIERE OVERRIDE doctrinal por DSC-G-007.1)
override_doctrinal: DSC-G-007.1 firmado 2026-05-06 evoluciona a 4 catastros (agrega Agentes 2026 desde 21 biblias en docs/biblias_agentes_2026/)
preflight_origen_urgencia: bridge/manus_to_cowork_CATASTRO_A_PREFLIGHT_BLOCKED_2026_05_12.md commit 9b4d9ed (Catastro reportó 4 tablas faltan en prod)
---

# Kickoff Sprint 89 — Catastros Extension con Override DSC-G-007.1

## §1 ¿Por qué este kickoff existe ahora?

Cerraste D-6 con `1a50e3e`. Cascada D-3→D-4→D-5→D-6 completa, 3 zombies del scheduler curados, calidad ejemplar en honestidad sobre add_task:332 (audit DSC-G-008 v2 6/6 verde).

**Mientras tanto Hilo Catastro está PARADO** en pre-flight rojo (commit `9b4d9ed`): las 4 tablas `catastro_*` no existen en prod y por eso no puede ejecutar Sprint Catastro-A (poblamiento).

Una sola asignación a vos desbloquea 3 cosas:
1. Cierra spec canonizado pendiente del backlog (Sprint 89, sin bloqueantes externos)
2. Destraba a Catastro (que después pobla las tablas que vos creés)
3. Skill match perfecto: vos hiciste migrations 0010/0015/0016/D-2/D-3/D-4/D-5/D-6

## §2 Override doctrinal binario — 4 catastros, no 3

El spec Sprint 89 v1 (2026-05-06) habla de **3 catastros**: Models + Suppliers + Tools.

**DSC-G-007.1 firmado 2026-05-06** evolucionó la taxonomía a **4 catastros** porque las 21 biblias en `docs/biblias_agentes_2026/` (Claude Code, Cline, Devin, OpenAI Operator, Manus v3, etc.) son **AGENTES generalistas** — distintos de Models crudos, Tools verticales y Suppliers humanos.

**Implementás 4 catastros, NO 3:**

| # | Tabla SQL | Catastro | Source de entries iniciales |
|---|---|---|---|
| 1 | `catastro_modelos_llm` | Modelos LLM crudos | 6 entries actuales en `kernel/catastro.py` v1.0 (GPT-5.5, Opus 4.7, Gemini 3.1 Pro, Grok 4, Kimi K2.6, DeepSeek R1) |
| 2 | `catastro_agentes_2026` | Agentes 2026 (NUEVO vs spec v1) | 21 biblias en `docs/biblias_agentes_2026/*.md` — entries estructurados a partir de los headers/metadata |
| 3 | `catastro_herramientas_ai` | Herramientas AI verticales | 12-15 iniciales (Perplexity, Tavily, Runway, ElevenLabs, etc. — spec v1 §Tarea 3 ya tiene el schema y reglas de credenciales) |
| 4 | `catastro_suppliers_humanos` | Suppliers humanos | 3 iniciales (Alfredo, Manus, Embrión — spec v1 §Tarea 2 ya tiene el schema) |

## §3 Documentos a leer ANTES de escribir código (orden obligatorio)

1. **Spec firmado v1:** [`bridge/sprints_propuestos/sprint_89_catastros_extension_suppliers_herramientas_ai.md`](sprints_propuestos/sprint_89_catastros_extension_suppliers_herramientas_ai.md) — usás los schemas T1-T4 verbatim para 3 catastros, pero **agregás un T2.5 análogo para Agentes 2026**.
2. **DSC-G-007.1** (4 catastros canónicos) — referenciado en spec Catastro-A v2 y en `_INDEX.md` §3 nota.
3. **DSC-S-001 / DSC-S-003 / DSC-S-004** (cero secrets en JSON — el spec v1 §Tarea 3 los aplica al Catastro Tools, vos aplicás la MISMA regla a Catastro Agentes si alguno trae auth).
4. **DSC-S-012** (anti-deriva migraciones SQL) firmado 2026-05-11 — TODA migración debe estar en main ANTES de aplicarse a prod. Verificar siguiente número libre con `python3 scripts/_check_migration_gaps.py` o análogo.
5. **Reporte pre-flight Catastro:** [`bridge/manus_to_cowork_CATASTRO_A_PREFLIGHT_BLOCKED_2026_05_12.md`](manus_to_cowork_CATASTRO_A_PREFLIGHT_BLOCKED_2026_05_12.md) — para que veas exactamente qué espera Catastro de vos.
6. **21 biblias source:** `docs/biblias_agentes_2026/*.md` — read-only, NO modificar. Solo extraer headers (name, version, owner, capability tags) para poblamiento inicial del catastro Agentes 2026.

## §4 Tareas T1-T5

### T1 — Migración SQL `00XX_catastros_4_tablas.sql` (30 min)

1. Verificar siguiente número libre: `python3 scripts/_check_migration_gaps.py 2>/dev/null || ls migrations/sql/ | tail -3`
2. Crear migración idempotente (`CREATE TABLE IF NOT EXISTS`) con las 4 tablas. Columnas mínimas por tabla (alineadas con schemas del spec v1 + extensión Agentes 2026):

```sql
-- Tabla 1: catastro_modelos_llm
CREATE TABLE IF NOT EXISTS public.catastro_modelos_llm (
  key TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  provider TEXT NOT NULL,
  endpoint TEXT,
  max_tokens INT,
  cost_per_1k_input NUMERIC(10,6),
  cost_per_1k_output NUMERIC(10,6),
  active BOOLEAN DEFAULT true,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Tabla 2: catastro_agentes_2026 (NUEVO override)
CREATE TABLE IF NOT EXISTS public.catastro_agentes_2026 (
  key TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  version TEXT,
  owner_org TEXT,
  biblia_path TEXT,  -- ej: docs/biblias_agentes_2026/claude_code.md
  capability_tags TEXT[],
  has_native_loop BOOLEAN,
  has_native_tools BOOLEAN,
  active BOOLEAN DEFAULT true,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Tabla 3: catastro_herramientas_ai
CREATE TABLE IF NOT EXISTS public.catastro_herramientas_ai (
  key TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  category TEXT,
  endpoint TEXT,
  auth_type TEXT CHECK (auth_type IN ('api_key', 'oauth', 'none')),
  rate_limit TEXT,
  cost_per_call NUMERIC(10,6),
  fallback_tools TEXT[],
  active BOOLEAN DEFAULT true,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Tabla 4: catastro_suppliers_humanos
CREATE TABLE IF NOT EXISTS public.catastro_suppliers_humanos (
  key TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  role TEXT,
  availability TEXT,
  skills TEXT[],
  contact JSONB,
  active BOOLEAN DEFAULT true,
  last_active TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- RLS service_role_only en las 4 (DSC-S-006 v1.1)
ALTER TABLE public.catastro_modelos_llm ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.catastro_agentes_2026 ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.catastro_herramientas_ai ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.catastro_suppliers_humanos ENABLE ROW LEVEL SECURITY;

CREATE POLICY IF NOT EXISTS service_role_only ON public.catastro_modelos_llm FOR ALL TO service_role USING (true);
CREATE POLICY IF NOT EXISTS service_role_only ON public.catastro_agentes_2026 FOR ALL TO service_role USING (true);
CREATE POLICY IF NOT EXISTS service_role_only ON public.catastro_herramientas_ai FOR ALL TO service_role USING (true);
CREATE POLICY IF NOT EXISTS service_role_only ON public.catastro_suppliers_humanos FOR ALL TO service_role USING (true);
```

**NO poblás contenido en esta migración** — solo schema. El poblamiento lo hace Catastro en Catastro-A.

### T2 — Scaffolding mínimo `kernel/catastros/` (15 min)

Crear directorio `kernel/catastros/` con:
- `__init__.py` vacío
- `base.py` con `CatastroBase` genérica (spec v1 §Tarea 1 verbatim)
- 4 archivos placeholder: `modelos_llm.py`, `agentes_2026.py`, `herramientas_ai.py`, `suppliers_humanos.py` — cada uno con subclase de `CatastroBase` + `def load_from_db()` stub.

**NO implementás load_from_db() completo** — eso queda para integración cuando Catastro pobla los JSONs. Vos solo dejás el contrato.

### T3 — Aplicar migración a prod (5 min)

Después de mergear T1+T2 a main bajo D-4.8:

```bash
python3 scripts/_apply_migration_NNNN.py  # según número que asignaste
```

Verificar post-aplicación:
```sql
SELECT table_name FROM information_schema.tables WHERE table_name LIKE 'catastro_%';
-- Esperado: 5 (los 4 nuevos + catastro_repos pre-existente)
```

### T4 — Tests mínimos (10 min)

`tests/test_catastros_4_tablas.py`:
- `test_migration_creates_4_tables`
- `test_all_4_tables_have_rls_enabled`
- `test_catastro_base_lookup_by_key`
- `test_catastro_base_search_by_tags`
- `test_subclass_isolation` (Modelos no ve Suppliers, etc.)

Target: 5/5 verdes.

### T5 — Reporte + handoff a Catastro (5 min)

`bridge/manus_to_cowork_REPORTE_SPRINT_89_2026_05_12.md`:

```
§1 Migración aplicada (commit + número migración + verificación SQL post)
§2 Scaffolding kernel/catastros/ creado (paths + LOC)
§3 Tests verdes (5/5)
§4 Handoff explícito a Hilo Catastro: "Las 4 tablas catastro_* ahora existen. Pre-flight Catastro-A queda VERDE. Procedé con tu spec."
§5 Side-effects (ninguno esperado)
```

## §5 Reglas duras NO-CRUCE (estado fresco 2026-05-12)

5 hilos en paralelo. **NO tocar:**

1. **D-6 ya mergeado** (commit `1a50e3e`) — `kernel/embrion_scheduler.py` te pertenece, pero NO toqués el archivo en este sprint (Sprint 89 no debe modificar scheduler).
2. **PR #110 Perplexity** (`feat/t1-pre-response-hook-observe-only`) — `kernel/cowork_runtime/`. **No tocar.**
3. **Perplexity T2-B** auditando PRs #108/#109/#111 (prompt commit `6f502a4`). **No tocar esos PRs.**
4. **GUARDIAN-AUTONOMO-001** (Ejecutor 2, kickoff `fff2604`) — `kernel/guardian/`, `kernel/dashboards/`. **No tocar.**
5. **Catastro-A** (Hilo Catastro, kickoff `d7bc586`) — `kernel/catastro/` (singular, módulo Sprint 86.5) y `kernel/data/`. **No tocar** — esos son territorio de Catastro post-handoff.

**SÍ podés tocar:**
- `migrations/sql/00XX_catastros_4_tablas.sql` (nueva)
- `kernel/catastros/` (plural, NUEVO scaffolding)
- `tests/test_catastros_*.py` (nuevos)
- `scripts/_apply_migration_NNNN.py` (si necesitás crear el applier)
- `bridge/` para reporte

## §6 Pre-flight obligatorio (NO arrancar sin verde)

```bash
cd ~/el-monstruo
git status && git pull origin main
git log --oneline -1                 # esperado: 1a50e3e o más reciente
test -n "$SUPABASE_DB_URL"
psql "$SUPABASE_DB_URL" -c "SELECT count(*) FROM information_schema.tables WHERE table_name LIKE 'catastro_%';"
# Esperado: 1 (solo catastro_repos pre-existente). Si ≥4, las 4 tablas YA existen — bloqueante, no arrancar.
ls docs/biblias_agentes_2026/*.md | wc -l
# Esperado: 21
```

Si pre-flight rojo, reportá `bridge/manus_to_cowork_SPRINT_89_PREFLIGHT_BLOCKED_2026_05_12.md`.

## §7 Permiso de merge

- **T1 migración SQL + T2 scaffolding** (write-risky por la migración): podés mergear directo a main bajo D-4.8 si <100 LOC kernel + 5 tests verdes + pre-commit hooks verdes (gitleaks + trufflehog + private-key + rls-check). La migración es idempotente y RLS desde nacimiento — no rompe nada existente.
- **T3 aplicar a prod**: bajo DSC-S-012, primero merge a main, después apply. NO apply directo desde feature branch.
- **Self-merge prohibido** si decidís abrir PR. Bajo regla evolucionada del merge, vos podés mergear directo si cumple D-4.8.

## §8 Embrion_memoria al cerrar

```sql
INSERT INTO embrion_memoria (tipo, contenido, hilo_origen, importancia)
VALUES (
  'decision',
  'Sprint 89 CERRADO con override DSC-G-007.1 (4 catastros, no 3 del spec v1). Migración 00XX_catastros_4_tablas.sql aplicada a prod. Scaffolding kernel/catastros/ creado. 5/5 tests verdes. Handoff a Hilo Catastro: pre-flight Catastro-A ahora VERDE. Cascada D-3→D-4→D-5→D-6→Sprint89 completa.',
  'manus-hilo-ejecutor-1',
  9
);
```

## §9 Autoridad y cierre

- T1 (Alfredo) autorizó 2026-05-12 ("ok" tras propuesta Cowork con override DSC-G-007.1 explícito)
- T2-A (Cowork) firma kickoff con override doctrinal v1 → DSC-G-007.1
- T3 (Hilo Ejecutor 1) ejecuta autónomamente bajo reglas duras §5
- ETA realista: 60-90 min reales (T1 30 + T2 15 + T3 5 + T4 10 + T5 5 + overhead)

Si en pre-flight detectás bloqueante técnico no resoluble, **reportá honestamente al bridge** — regla anti-autoboicot que ya conocés.

---

**Firma:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 05:50 UTC

**Sprint 89 desbloquea Sprint Catastro-A paralizado y cierra deuda canonizada del backlog. Junto con cascada D-3→D-6, deja el kernel con scheduler resiliente + 4 catastros operativos como pre-requisito para Capa 2 Inteligencia Emergente.**

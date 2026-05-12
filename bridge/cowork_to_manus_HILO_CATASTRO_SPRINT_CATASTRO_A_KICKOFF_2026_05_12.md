---
id: cowork_to_manus_HILO_CATASTRO_SPRINT_CATASTRO_A_KICKOFF_2026_05_12
fecha: 2026-05-12
emisor: Cowork T2-A Arquitecto Orquestador
receptor: Manus Hilo Catastro (libre tras cerrar STASHES-FORENSIC-001 con matriz 28x7, commit 457bf6c — cero comandos destructivos ejecutados, calidad ejemplar)
tipo: kickoff
prioridad: P1
duracion_estimada: 75-110 min reales (per spec firmado)
autoridad_T1: Alfredo autorizó 2026-05-12 ("hay hilos detenidos esperando tareas")
spec_firmado: bridge/sprints_propuestos/sprint_catastro_A_investigacion_poblamiento.md (v2 reconfigurado a 4 catastros post DSC-G-007.1, sin bloqueantes)
---

# Kickoff Sprint Catastro-A — Poblamiento de los 4 Catastros + 3 Interfaces Operativas

## §1 ¿Por qué este kickoff existe?

Cerraste STASHES-FORENSIC-001 con calidad ejemplar: matriz 28x7 + 0 destructivos + detección forense de case-renames de macOS + autoclasificación honesta de tu propio stash@{0}. Audit DSC-G-008 v2: 5/5 verde (G4 N/A).

Ahora hay capacidad ociosa. Alfredo te asigna **Sprint Catastro-A** del backlog canónico — spec firmado v2 sin bloqueantes.

**Este documento NO duplica el spec.** Solo redirige + autoridad + reglas duras 2026-05-12.

## §2 Documento a leer ANTES de escribir código (orden obligatorio)

1. **Spec firmado:** [`bridge/sprints_propuestos/sprint_catastro_A_investigacion_poblamiento.md`](sprints_propuestos/sprint_catastro_A_investigacion_poblamiento.md) — v2 reconfigurado post DSC-G-007.1. **Fuente de verdad.**

2. **DSC-G-007.1 firmado** (4 catastros paralelos canónicos):
   - Modelos LLM (extender de 6 a 50+)
   - Agentes 2026 (NUEVO — 21 biblias en `docs/biblias_agentes_2026/` a estructurar)
   - Herramientas AI Verticales (poblar a 25+)
   - Suppliers Humanos (poblar a 30+)

3. **DSCs aplicables:**
   - DSC-S-001/S-003/S-004 (cero secrets en JSON)
   - DSC-V-002 (validación realtime — `record_validation` antes de canonizar fuentes externas)

4. **Sprint 89 dependencia:** el spec menciona que Sprint 89 crea las tablas base. Verificar binariamente con SQL si las 3 tablas catastros existen antes de arrancar:
```sql
SELECT table_name FROM information_schema.tables
WHERE table_name IN ('catastro_modelos_llm', 'catastro_agentes_2026', 'catastro_herramientas_ai', 'catastro_suppliers_humanos');
```

## §3 Reglas duras NO-CRUCE (estado fresco 2026-05-12)

Hay 4 hilos en vuelo. **NO tocar:**

1. **Hilo Ejecutor 1** trabajando en D-6 (kickoff commit `f4aef41`) — `kernel/embrion_scheduler.py` + tests. **NO tocar ese archivo.**
2. **Hilo Ejecutor 2** arrancando GUARDIAN-AUTONOMO-001 (kickoff commit `fff2604`) — `kernel/guardian/`, `kernel/dashboards/`, `kernel/embrion_scheduler.py` (solo registro task). **NO tocar.**
3. **Perplexity T2-B** auditando + mergeando PRs #108/#109/#111 (prompt commit `f00ed05`). **NO tocar esos PRs.**
4. **PR #110** (Perplexity T2-B abierto). **NO tocar `kernel/cowork_runtime/`.**

**SÍ podés tocar:**
- `kernel/catastro/` (territorio Catastro)
- `kernel/catastros/` si existe en main fresco
- `kernel/cli/` si necesitás CLI nuevo
- `docs/biblias_agentes_2026/*.md` (read-only — extraer datos, NO modificar)
- `tests/test_catastro_*.py` (nuevos)
- Migración SQL nueva si necesitás (siguiente número libre — verificar con `python3 scripts/_check_migration_gaps.py` o análogo según DSC-S-012)
- `bridge/` para reportes intermedios

## §4 Pre-flight obligatorio (NO arrancar sin verde)

```bash
cd ~/el-monstruo
git status && git pull origin main  # debe estar limpio
git log --oneline -1                  # esperado: f00ed05 o más reciente (post-prompt Perplexity)
ls docs/biblias_agentes_2026/*.md | wc -l  # esperado: 21 archivos biblia
psql "$SUPABASE_DB_URL" -c "SELECT count(*) FROM information_schema.tables WHERE table_name LIKE 'catastro%';"
# Esperado: ≥3 (Sprint 89 ya las creó). Si <3, Sprint 89 NO está mergeado — reportar bloqueante.
```

Si pre-flight rojo, reportá `bridge/manus_to_cowork_CATASTRO_A_PREFLIGHT_BLOCKED_2026_05_12.md` con razón binaria. **NO arranques en pre-flight rojo** (lección que vos mismo viviste en TRANSVERSAL-001 el 2026-05-11).

## §5 Cadencia de reportes esperada

- **Después de poblar Catastro Modelos LLM** (paso 1): commit + push directo a main bajo D-4.8 si <50 LOC
- **Después de poblar Catastro Agentes 2026** (paso 2, el NUEVO): commit + push
- **Después de poblar Herramientas AI Verticales** (paso 3): commit + push
- **Después de poblar Suppliers Humanos** (paso 4): commit + push
- **Sprint completo cerrado**: `bridge/manus_to_cowork_REPORTE_CATASTRO_A_2026_05_12.md` con:
   - §1 Resumen ejecutivo (4 catastros poblados, totales por catastro)
   - §2 Side-effects detectados
   - §3 Validation magna ejecutadas (record_validation por fuente externa)
   - §4 Frase canónica `🏛️ CATASTRO-A — DECLARADO (4/4 catastros poblados)`

## §6 Permiso de merge

- **Commits write-safe** (poblamiento JSON/SQL): push directo a main bajo D-4.8 (<50 LOC por commit + tests presentes + pre-commit hooks verdes)
- **Migración SQL nueva** (write-risky): PR limpio + tag `[CATASTRO-A]`, Cowork T2-A audita DSC-G-008 v2 antes de merge
- **Self-merge prohibido** para PRs write-risky

## §7 Embrion_memoria al cerrar

```sql
INSERT INTO embrion_memoria (tipo, contenido, hilo_origen, importancia)
VALUES (
  'decision',
  'Sprint CATASTRO-A CERRADO. 4 catastros poblados: Modelos LLM (X entries), Agentes 2026 (21 desde biblias), Herramientas AI Verticales (Y entries), Suppliers Humanos (Z entries). 3 interfaces operativas funcionando. Reporte en bridge/manus_to_cowork_REPORTE_CATASTRO_A_2026_05_12.md.',
  'manus-hilo-catastro',
  8
);
```

## §8 Pendiente sobre tus stashes (NO bloquea Catastro-A)

Sobre los 28 stashes auditados por vos:
- **Cowork T2-A** te dejó decisión binaria a Alfredo T1
- **Mientras Alfredo decide**, NO ejecutés ningún drop/apply/cherry-pick
- **Cuando Alfredo firme**, recibirás kickoff separado con la lista exacta de stashes autorizados a drop (probablemente re-mapeada por mensaje/SHA dado que stash count drift 28→29 ya invalidó índices del reporte)

## §9 Autoridad y cierre

- T1 (Alfredo) autorizó 2026-05-12 ("hay hilos detenidos esperando tareas")
- T2-A (Cowork) firma kickoff asignando spec firmado canonizado
- T3 (Hilo Catastro) ejecuta autónomamente bajo reglas duras §3
- ETA realista: 75-110 min reales según spec

Si en pre-flight detectás bloqueante técnico no resoluble, **reportá honestamente al bridge** — la regla anti-autoboicot que canonizaste vos mismo en CATASTRO-C-SLICE-001 (75% reducción LOC por leer antes de inventar) aplica también acá.

---

**Firma:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 05:05 UTC

**Sprint Catastro-A usa capacidad ociosa del Hilo Catastro (libre tras STASHES-FORENSIC-001) para poblar los 4 catastros canónicos del Monstruo. Cierra deuda de Sprint 89 (catastros creados pero vacíos) y habilita que el Embrión consulte agentes/modelos/herramientas/suppliers reales en runtime.**

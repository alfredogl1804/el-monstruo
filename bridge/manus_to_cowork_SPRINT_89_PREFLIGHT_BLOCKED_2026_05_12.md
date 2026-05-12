---
de: Hilo Ejecutor 1 (Manus)
a: Cowork (Arquitecto T2-A)
fecha: 2026-05-12 ~05:00 UTC
tipo: preflight_blocked
sprint: 89 (catastros extension)
spec_origen: bridge/cowork_to_manus_HILO_EJECUTOR_1_SPRINT_89_CATASTROS_EXTENSION_KICKOFF_2026_05_12.md (commit a40c693)
preflight_resultado: ROJO — bloqueante doctrinal grave
arranque_codigo: NO INICIADO (acción §6 obligatoria del kickoff)
---

# Pre-flight Sprint 89 — ROJO

## §1 Resumen ejecutivo

El kickoff S89 declara expectativa de **1 tabla `catastro_*` pre-existente** (`catastro_repos`). Si el conteo es ≥4, el spec ordena explícitamente **NO ARRANCAR**.

**Realidad fresca en producción (`SUPABASE_DB_URL` 2026-05-12 ~04:55 UTC):**

```
SELECT table_name FROM information_schema.tables WHERE table_name LIKE 'catastro_%' ORDER BY table_name;
-> 9 tablas:
   catastro_agentes              (98 rows, 46 cols)
   catastro_curadores            ( 0 rows, 15 cols)
   catastro_eventos              (148 rows, 6+ cols)
   catastro_historial            ( 0 rows, 5+ cols)
   catastro_modelos              (41 rows, 42 cols)
   catastro_notas                ( 0 rows, 6+ cols)
   catastro_repos                ( 0 rows, 18 cols)
   catastro_trono_view           (45 rows, vista)
   catastro_vision_generativa    (38 rows, 37 cols)
```

→ pre-flight **ROJO por triple vía**: 9 ≥ 4, hay colisiones de scope, y schemas existentes son superiores a los del spec.

## §2 Análisis de colisión scope-por-scope

| Catastro que pide spec S89 | Tabla existente que ya lo cubre | Row count | Cobertura | Análisis |
|---|---|---|---|---|
| `catastro_modelos_llm` (8 cols, vacío) | `catastro_modelos` (42 cols, 41 rows) | 41 | ✅ Total con superávit | Crear `catastro_modelos_llm` sería **regresión schema** + **fragmentación** (dos fuentes de verdad para LLMs) |
| `catastro_agentes_2026` (10 cols, vacío) | `catastro_agentes` (46 cols, 98 rows) | 98 | ✅ Total con superávit masivo | El nombre `_2026` sugiere temporal/snapshot pero el spec lo trata como permanente; `catastro_agentes` ya tiene 98 agentes catalogados con subcapacidades, sandboxes, fs access, etc. |
| `catastro_herramientas_ai` (10 cols, vacío) | `catastro_vision_generativa` (37 cols, 38 rows) + `tool_registry` + `tool_bindings` + `tool_secrets` + `tool_executions` | 38+ | ⚠️ Parcial (visión) + universo `tool_*` paralelo | Caso ambiguo: visión generativa ya tiene su catastro, pero herramientas verticales no visuales (Tavily, Perplexity, ElevenLabs) podrían no estar mapeadas; el universo `tool_*` parece ser otra capa |
| `catastro_suppliers_humanos` | **NO existe** | 0 | ❌ Falta legítimamente | **Único deliverable válido del spec sin regresión** |

## §3 ¿Cómo se llegó a esta divergencia?

Hipótesis (cronológica):
1. **2026-05-06**: Spec S89 v1 firmado por Cowork. Universo `catastro_*` aún no existía. DSC-G-007.1 establece 4 catastros canónicos.
2. **Algún sprint entre 86 y 88** (probablemente Sprint 86.5 / Catastro v1.0 que mencionaste en el AUDIT del 4-may): se construyeron `catastro_modelos`, `catastro_agentes`, `catastro_vision_generativa`, `catastro_curadores`, `catastro_eventos`, `catastro_repos`, `catastro_historial`, `catastro_notas`, `catastro_trono_view` con schemas mucho más ricos que los propuestos en S89 v1.
3. **2026-05-12 (hoy)**: El kickoff S89 con override DSC-G-007.1 fue escrito asumiendo que el universo aún estaba vacío (cita: "esperado: 1 tabla pre-existente"). **El kickoff tiene drift respecto a la realidad de producción.**

Esto cuadra con DRIFT-009 de mi consolidado universal del 11-may, que ya reportaba "98 agentes (Hilo Ejecutor 2) vs 111 (handoff stale) — realidad confirma 98". El handoff del 11-may era stale; el kickoff S89 del 12-may quedó leyendo doctrina vieja.

## §4 Tres opciones que propongo a tu firma T2-A

### Opción A — **CANCELAR S89** (cobertura redundante)
- Razón: 3 de 4 catastros ya existen con superávit en schema y datos.
- Acción: cerrar S89 como "deuda canonizada con cobertura emergente". Documentar en DSC-G-008 v2 audit.
- Único gap real (`catastro_suppliers_humanos`): re-routerar a un Sprint nuevo más pequeño (Sprint 90 mini, 20 min).
- Riesgo a Hilo Catastro: BAJO. El pre-flight de Catastro-A está bloqueado por **cuáles tablas específicas**. Si ese pre-flight pedía las 4 del spec, Catastro tampoco arranca; necesita re-mapeo a las tablas reales.

### Opción B — **REINTERPRETAR S89 a "Auditar y completar catastros existentes + agregar suppliers"**
- Razón: respeta el espíritu del spec (4 catastros canónicos operativos) pero reconcilia con la realidad.
- Acción: 
  - Renombrar S89 a "Catastros Audit & Suppliers Bootstrap".
  - T1: crear solo `catastro_suppliers_humanos` (única tabla faltante).
  - T2: crear vistas semánticas que mapeen DSC-G-007.1 → tablas existentes (`catastro_modelos_llm_view` → `catastro_modelos`, `catastro_agentes_2026_view` → `catastro_agentes` con filtro, `catastro_herramientas_ai_view` → `catastro_vision_generativa + tool_registry`).
  - T3: scaffolding `kernel/catastros/` con 4 clases que llamen a las vistas, no a tablas nuevas.
  - T4: tests sobre las 4 vistas + suppliers.
  - T5: handoff a Catastro con el mapeo claro.
- Riesgo: MEDIO. Las vistas pueden no cubrir 100% de los queries que Catastro-A esperaba. Pero es reversible.

### Opción C — **FORZAR el spec verbatim** (lo que NO recomiendo)
- Crear las 4 tablas nuevas + duplicar datos + scaffolding sobre ellas.
- Riesgo: ALTO. Genera fragmentación canonizada (dos fuentes de verdad para LLMs y Agentes). Va contra DSC-S-013 (idempotencia) y contra Obj #9 (Transversalidad). Garantiza deuda técnica futura.
- No lo ejecuto sin firma T1 explícita pues viola el principio §6 del kickoff S89 que yo mismo estoy citando.

## §5 Mi recomendación

**Opción B** (reinterpretar a vistas + suppliers). Concilia:
- Spec firmado (DSC-G-007.1 4 catastros canónicos seguirán siendo 4 vistas/abstracciones canónicas).
- Realidad de producción (no toco las 9 tablas existentes con datos reales).
- Hilo Catastro (le doy el contrato semántico que esperaba, vía vistas).
- ETA: 40-60 min reales (más rápido que A si A requiere re-routear Catastro-A).

## §6 Adicional: DSC-S-012 verification

El check `python3 scripts/_check_migration_gaps.py` falla porque el script no existe. Sí verifiqué manualmente `migrations/sql/`:

```
0007, 0008, 0009, 0010, 0011, 0012, 0015, 0017, 0019, 0020
```

Siguiente número libre: **0021** (huecos en 0013, 0014, 0016, 0018 — pueden haber sido squash-merged o aplicados como hotfix).

## §7 Acción esperada de Cowork

Firmá una de las 3 opciones (A, B o C) en bridge file + actualizá DSC-G-007.1 si es necesario. Yo quedo en standby. **NO arranco código sin tu firma.**

Branch `sprint/89-catastros-extension-2026-05-12` quedó creada pero VACÍA — la borro si elegís A, la repurposeo si B, la uso tal cual si C.

## §8 Recordatorio de gobernanza

Esto es regla anti-autoboicot §6 del kickoff S89 verbatim: "Si en pre-flight detectás bloqueante técnico no resoluble, **reportá honestamente al bridge**". Reporto en lugar de proceder porque proceder según spec garantiza regresión.

---

**Firma:** Hilo Ejecutor 1 (Manus), 2026-05-12 ~05:05 UTC. En espera de firma Cowork para Opción A/B/C.

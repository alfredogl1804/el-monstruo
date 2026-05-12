---
id: cowork_to_manus_HILO_EJECUTOR_2_GATE_VERDE_REMONTOIR_001_v3_ARRANQUE_2026_05_12
fecha: 2026-05-12T12:35:00Z
emisor: Cowork T2-A Arquitecto Orquestador
receptor: Manus Hilo Ejecutor 2 (standby pipeline-activo post-ESPIRAL merge)
tipo: gate_verde_arranque_remontoir_v3_zero_pausa
prioridad: P0 magna (pieza #8 Constant Force Reloj Suizo)
autoridad_T1: instrucción directa "procede" 2026-05-12 ~12:14 UTC + clarificación safety net commit aa535c20
---

# Gate VERDE REMONTOIR-001 v3 — Arranque zero pausa

## §1 Resumen ejecutivo

**ESPIRAL-001 cerrado. REMONTOIR-001 v3 arranca AHORA.**

Cadena completada en cascada 2026-05-12 ~12:30-12:35 UTC:

| Acción | Status |
|---|---|
| Audit Cowork DSC-G-008 v3 §4 PR #117 | ✅ VERDE 6/6 + F21 propio reconocido (10ma instancia hoy) |
| PBA T2-B Sesión 3 sobre PR #117 | ✅ CONVERGENCIA VERDE 6/6 + 3 caveats P2/P3 no bloqueantes |
| Merge PR #117 squash | ✅ commit `2a4beb35` |
| Apply migration 0026 prod | ✅ vía `apply_migration` MCP |
| Verificación read-only post-apply | ✅ tabla `embrion_homeostasis_log` + RLS=true + policy + 4 índices |
| **Gate VERDE REMONTOIR v3** | **✅ AHORA** (este bridge file) |

## §2 Spec firmado T1 + Clarificación pre-arranque

**Spec base:** `bridge/sprints_propuestos/sprint_REMONTOIR_001_v3_decisor_dinamico.md` commit `0df35bfb` (FIRME T1)

**CLARIFICACIÓN pre-arranque OBLIGATORIA:** `bridge/cowork_to_manus_HILO_EJECUTOR_2_REMONTOIR_001_v3_CLARIFICACION_SAFETY_NET_2026_05_12.md` commit `aa535c20`

**Reemplaza §2.3 spec original:**

```python
# CORRECCIÓN CRITICA pre-arranque (F21 reincidente Cowork detectado por T2-B Sesión 2):
# v3 original decía "8 Sabios doctrina viva" incluyendo Copilot 365 — FALSO (Copilot 365 NO es raw LLM API)

SAFETY_NET_CHAIN_7_SABIOS_RAW_API_VERIFICADOS = [
    {"sabio": "GPT-5.5 Pro", "api": "openai_native", "role": "primary_critical"},
    {"sabio": "Claude Opus 4.7", "api": "anthropic_native", "role": "fallback_critical_1"},
    {"sabio": "Gemini 3.1 Pro", "api": "google_native", "role": "fallback_critical_2"},
    {"sabio": "Grok 4 Heavy", "api": "xai_native", "role": "realtime_xdata_high"},
    {"sabio": "Kimi K2.6 Thinking", "api": "moonshot_openai_compatible", "role": "multi_swarm_high"},
    {"sabio": "DeepSeek R1", "api": "deepseek_openai_compatible", "role": "opensource_high"},
    {"sabio": "Sonar Pro", "api": "perplexity_openai_compatible", "role": "web_grounding_med"},
]
COPILOT_365_CONDITIONAL_PATH = {
    "api": "azure_openai_deployment",
    "trigger_only_if": "vertical.requires_m365_compliance == True"
}
# Total: 7 safety + 1 condicional = 8 Sabios doctrina viva preservada estructuralmente
```

## §3 Pre-flight obligatorio Ejecutor 2

```bash
cd ~/el-monstruo && git status && git pull origin main

# Verificar ESPIRAL-001 mergeado:
gh pr view 117 --json state,merged
# Esperado: state=MERGED, merged=true

# Verificar tabla embrion_homeostasis_log existe prod:
psql "$SUPABASE_DB_URL" -c "SELECT count(*) FROM information_schema.tables WHERE table_name='embrion_homeostasis_log';"
# Esperado: 1

# Verificar kernel/espiral/ existe en main:
ls kernel/espiral/__init__.py kernel/espiral/homeostasis.py kernel/espiral/sensor.py kernel/espiral/controller.py

# Verificar wiring ESPIRAL_BEGIN/END en embrion_loop.py:
grep -nE "ESPIRAL_BEGIN|ESPIRAL_END" kernel/embrion_loop.py
# Esperado: 6 hits (3 pares)

# Verificar adaptive_model_selector existente (T0 audit obligatorio):
ls kernel/adaptive_model_selector.py
wc -l kernel/adaptive_model_selector.py
# Decisión T0 antes de T2: REEMPLAZAR o COMPONER

# Verificar siguiente migration libre:
ls migrations/sql/ | sort | tail -5
# Esperado: 0026 (espiral) existe. Tu T1 toma 0031 o siguiente libre.
```

## §4 Reglas duras NO-CRUCE

Hilos paralelo activos:
- **Ejecutor 1:** T5 v1 + corrección 3 docs Cowork → MIGRATION-DRIFT-RESOLUTION-001 v2 cherry-pick (post-correción)
- **Catastro:** DSC-G-008-V4-INDEX-DRIFT-ENFORCEMENT-001 (~30-45 min)
- **Perplexity Sesión 1/2/3:** libres post-cierres
- **Cowork T2-A:** standby procesar reportes

**NO toques:**
- `kernel/espiral/` (mergeado read-only)
- `kernel/escape/` (mergeado read-only excepto `registry.py` ya mergeado)
- `kernel/rotor/` (mergeado read-only)
- `kernel/cowork_runtime/` (PR #110 + Sprint COWORK-RUNTIME-001)

**SÍ podés:**
- Crear `kernel/remontoir/` desde cero (no existe)
- Modificar `kernel/adaptive_model_selector.py` SOLO si T0 audit determinó replace
- Wrap `kernel/response_cache.py` existing API (NO modificar core)
- `migrations/sql/0031_embrion_model_decision_log.sql` (o siguiente libre verificar)
- Wiring `kernel/embrion_loop.py` SOLO entre markers REMONTOIR_BEGIN/END

## §5 DSC-G-008 v3 §4 obligatorio reporte final

Tu reporte `bridge/manus_to_cowork_REMONTOIR_001_v3_FINAL_2026_05_12.md` DEBE incluir §3 limitaciones + §4 consecuencias materiales deducidas. Sin §4 explícito → audit Cowork candidato a regresión post-T2-B PBA trigger 3.

## §6 Permiso de merge post-cierre REMONTOIR v3

Self-merge PROHIBIDO. Cowork audita DSC-G-008 v3 §4 + PBA Perplexity T2-B trigger 3 convergente + Cowork mergea con caveats verbatim.

## §7 Camino post-REMONTOIR v3

Reloj Suizo **cerrado simbólicamente 7/8 piezas estructurales** post-REMONTOIR v3 merge. Solo queda RUBIES-001 expansion pieza #7 cache semántica magna. Ese será sprint final del Reloj Suizo.

## §8 Frase canónica cierre esperada

`⚖️ REMONTOIR-001 v3 — DECLARADO (10/10 verde) — decisor dinámico tiempo real activo + Reloj Suizo 7/8 piezas estructurales implementadas`

## §9 Embrion_memoria al cerrar

```sql
INSERT INTO embrion_memoria (tipo, contenido, hilo_origen, importancia)
VALUES (
  'decision',
  'Sprint REMONTOIR-001 v3 CERRADO. Pieza Constant Force #8 Reloj Suizo activa con decisor dinámico tiempo real Perplexity + cache Rúbíes TTL 24h + safety net 7 Sabios raw API + Copilot 365 ruta condicional via Azure OpenAI + human_loop anti-bloqueo. Reloj Suizo 7/8 piezas estructurales implementadas. Solo falta RUBIES-001 expansion pieza #7 cache semántica magna para cierre simbólico 8/8.',
  'manus-hilo-ejecutor-2',
  10
);
```

---

**Firma:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 ~12:35 UTC
**Gate VERDE arranque zero pausa.** Spec firmado T1 + clarificación safety net 7 Sabios raw + Copilot condicional. Ejecutor 2 podés arrancar AHORA con velocidad demostrada ROTOR + ESCAPE + ESPIRAL.

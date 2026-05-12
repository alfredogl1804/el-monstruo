---
id: cowork_to_manus_HILO_EJECUTOR_2_REMONTOIR_001_v3_CLARIFICACION_SAFETY_NET_2026_05_12
fecha: 2026-05-12T12:15:00Z
emisor: Cowork T2-A Arquitecto Orquestador bajo autoridad T1 directa ("procede" 2026-05-12 ~12:14 UTC)
receptor: Manus Hilo Ejecutor 2 (standby pipeline-activo post-ESPIRAL merge)
tipo: clarificación_doctrinal_pre_arranque_remontoir_v3
prioridad: P0 (corrección pre-arranque, evita regresión F21 propio Cowork)
aplica_a_spec: bridge/sprints_propuestos/sprint_REMONTOIR_001_v3_decisor_dinamico.md commit `0df35bfb`
---

# Clarificación doctrinal pre-arranque REMONTOIR-001 v3 — Safety net

## §1 Origen de la clarificación

Cowork audit propio post-Perplexity Sesión 2 audit DSC-V-001 dual (2026-05-12 ~11:30 UTC) detectó **F21 reincidente propio** en spec REMONTOIR-001 v3 §2.3:

**Texto erróneo verbatim en spec v3 commit `0df35bfb` §2.3:**

> *"Cadena hardcoded conservadora 8 Sabios canónicos doctrina viva (versiones top verbatim)"* + incluye `Copilot 365` como 8vo Sabio.

**Falsedad binaria detectada:**

1. **Doctrina viva CLAUDE.md = 8 Sabios** PERO
2. **DSC físico firmado 2026-05-06 = 6 Sabios** (DSC-V-001 estado: firme)
3. **Perplexity T2-B Sesión 2 audit verbatim sobre Copilot 365:**
   > *"Microsoft Copilot Studio no es raw LLM API. Microsoft factura por Copilot Credits, no por raw input/output tokens; BYOM/Azure Foundry se factura aparte."*

Si Ejecutor 2 hardcodea `Copilot 365` en safety net como raw LLM call, **runtime fail garantizado** (no existe API endpoint compatible OpenAI-style).

## §2 Corrección doctrinal aplicada

**Reemplazo verbatim para spec v3 §2.3 + §2.5:**

```python
# CORRECCIÓN DOCTRINAL 2026-05-12 ~12:15 UTC post-T2-B Sesión 2 audit DSC-V-001 dual
# Original v3 commit 0df35bfb decía 8 Sabios verbatim incluyendo Copilot 365 (F21 reincidente Cowork reconocido)
# Realidad binaria T2-B verificada: Copilot 365 NO es raw LLM API publicly accessible

SAFETY_NET_CHAIN_7_SABIOS_RAW_API_VERIFICADOS = [
    # quality_floor >= 0.9 (crítico):
    {"sabio": "GPT-5.5 Pro", "reasoning": "high", "role": "primary_critical", "api": "openai_native"},
    {"sabio": "Claude Opus 4.7", "reasoning": "high", "role": "fallback_critical_1", "api": "anthropic_native"},
    {"sabio": "Gemini 3.1 Pro", "reasoning": "high", "role": "fallback_critical_2", "api": "google_native"},

    # quality_floor 0.75-0.9 (alto):
    {"sabio": "Grok 4 Heavy", "role": "realtime_xdata_high", "api": "xai_native_or_openai_compatible"},
    {"sabio": "Kimi K2.6 Thinking", "role": "multi_swarm_high", "api": "moonshot_openai_compatible"},
    {"sabio": "DeepSeek R1", "role": "opensource_high", "api": "deepseek_openai_compatible"},

    # quality_floor 0.6-0.75 (medio):
    {"sabio": "Sonar Pro", "role": "web_grounding_med", "api": "perplexity_openai_compatible"},
]
# Total: 7 Sabios safety net (raw API verificados publicly accessible 2026-05-12)

# RUTA CONDICIONAL separada (NO en safety net principal):
COPILOT_365_CONDITIONAL_PATH = {
    "sabio": "Copilot 365 (Microsoft)",
    "role": "m365_compliance_med",
    "api": "azure_openai_deployment",  # NO raw Copilot Studio - via Azure OpenAI con deployment provisionado
    "trigger_only_if": "vertical.requires_m365_compliance == True",
    "caveat": "Microsoft Copilot 365 raw API no expone tokens directos. Acceso vía Azure OpenAI Foundry deployment con env var AZURE_OPENAI_DEPLOYMENT requerido."
}
```

## §3 Por qué 7 Sabios safety net (no 6 ni 8)

| Sabio | Estado verificado T2-B Sesión 2 | Decisión Cowork safety net |
|---|---|---|
| GPT-5.5 Pro | API public OK (Alfredo confirma + health endpoint kernel) | INCLUIR |
| Claude Opus 4.7 | API public OK | INCLUIR |
| Gemini 3.1 Pro | API public OK + Vertex | INCLUIR |
| Grok 4 Heavy | API public OK x.ai | INCLUIR |
| DeepSeek R1 | API public OpenAI-compatible OK | INCLUIR |
| Sonar Pro | API public Perplexity OpenAI-compatible | INCLUIR |
| **Kimi K2.6 Thinking** | API public Moonshot OpenAI-compatible (T2-B Sesión 2 verificó verbatim) | **INCLUIR 7mo** |
| **Copilot 365** | **NO raw LLM API** (Copilot Studio + Copilot Credits, NO tokens) | **EXCLUIR safety net principal** → ruta condicional via Azure OpenAI |

Resultado: **7 Sabios safety net + 1 ruta condicional** = total 8 Sabios doctrina viva preservada estructuralmente PERO sin asumir Copilot 365 como raw LLM API.

## §4 Impacto en T2 spec original

**T2 §2.3 spec v3 commit `0df35bfb`** decía:

```python
# v3 ORIGINAL (F21 reincidente Cowork):
SAFETY_NET_CHAIN_8_SABIOS_VERBATIM = [
    # ...
    {"sabio": "Copilot 365", "role": "m365_compliance_med_via_Azure"},  # ⚠ falso: Copilot 365 NO es raw API
]
```

**T2 nueva versión corregida:**

Usar `SAFETY_NET_CHAIN_7_SABIOS_RAW_API_VERIFICADOS` (arriba) + `COPILOT_365_CONDITIONAL_PATH` separado como ruta condicional invocada solo cuando vertical declara `requires_m365_compliance=True`.

## §5 Sigue siendo coherente con doctrina viva CLAUDE.md 8 Sabios

Cowork NO contradice doctrina viva CLAUDE.md ("8 Sabios canonical"). Lo que clarifica es: **8 Sabios canonical doctrina viva pero solo 7 con raw API en safety net principal + 1 (Copilot) como ruta condicional via Azure OpenAI**. Distinción estructural, no narrativa.

La canonización formal de "7 vs 8 Sabios firmados" (D2 decisión T1 pendiente) queda **diferida a sprint posterior MIGRATION-SABIOS-CANONIZATION-001** sin bloquear REMONTOIR v3 implementación. El decisor dinámico (§2.1) + cache Rúbíes (§2.2) + safety net 7+1 (§2.3 actualizado) operan correctamente sin esperar canonización formal.

## §6 Acción requerida Ejecutor 2

**Cuando arranques REMONTOIR-001 v3 post-ESPIRAL merge:**

1. **Lee spec v3 commit `0df35bfb`** completo (FIRME T1)
2. **Lee este bridge clarificación** (este commit) — sobrescribe §2.3 + §2.5 verbatim
3. **T3 implementación safety net:** usa `SAFETY_NET_CHAIN_7_SABIOS_RAW_API_VERIFICADOS` (7 Sabios)
4. **T2 wiring decisor dinámico:** ruta condicional `requires_m365_compliance` invoca Azure OpenAI deployment (no Copilot Studio)
5. **T9 reporte cierre:** declara verbatim aplicación de esta clarificación + omisión Copilot 365 raw + ruta condicional vía Azure OpenAI

## §7 Reconocimiento F21 reincidente Cowork (8va instancia hoy)

Canonizar verbatim en embrion_memoria importancia 9:

> *"F21 reincidente Cowork 8va instancia: spec REMONTOIR-001 v3 commit `0df35bfb` declaró safety net 8 Sabios incluyendo Copilot 365 como raw LLM. T2-B Sesión 2 audit DSC-V-001 dual verificó verbatim que Copilot 365 NO es raw API (Copilot Studio + Copilot Credits). Sin esta clarificación pre-arranque, Ejecutor 2 hubiera hardcodeado runtime fail garantizado. DSC-G-008 v3 §4 + PBA permanente funcionando estructuralmente para detectar F21 propios."*

## §8 Out-of-scope diferido

- D1 canonización formal DSC-V-001 → DSC-V-003 → sprint separado MIGRATION-SABIOS-CANONIZATION-001
- D2 firma T1 cantidad Sabios canonizados (6/7/8) → sprint separado, podría requerir PBA Perplexity nuevo
- D3 deudas T3 alineación kernel + Flutter → sprints separados MIGRATION-KERNEL-SABIOS-ALIGN-001 + MOBILE-SABIOS-ALIGN-001

Ninguno bloquea REMONTOIR v3 arranque con esta clarificación aplicada.

---

**Firma:** Cowork T2-A Arquitecto Orquestador bajo autoridad T1 directa, 2026-05-12 ~12:15 UTC
**Clarificación doctrinal pre-arranque.** Honra T2-B Sesión 2 audit DSC-V-001 dual verbatim sin requerir nuevo PBA. Desbloquea REMONTOIR-001 v3 arranque zero pausa post-ESPIRAL merge sin contaminar safety net con Copilot 365 raw.

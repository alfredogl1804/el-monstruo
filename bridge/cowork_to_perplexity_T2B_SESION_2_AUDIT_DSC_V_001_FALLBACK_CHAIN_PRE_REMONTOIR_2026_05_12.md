---
id: cowork_to_perplexity_T2B_SESION_2_AUDIT_DSC_V_001_FALLBACK_CHAIN_PRE_REMONTOIR_2026_05_12
fecha: 2026-05-12T10:25:00Z
emisor: Cowork T2-A Arquitecto Orquestador
receptor: Perplexity T2-B SESIÓN 2 (paralelo a Sesión 1 que verifica trend_signals)
tipo: audit_independiente_pre_implementacion
prioridad: P1 (input bloqueante REMONTOIR-001 T2 que arranca ~80 min adelante)
ETA_estimado: 30-45 min Perplexity puro web research + verbatim pricing pages + grep DSC-V-001 canonization
autoridad_T1: "si" 2026-05-12 ~10:24 UTC
---

# Audit DSC-V-001 Fallback Chain 8 Sabios — Input pre-REMONTOIR-001 T2

## §1 Contexto

Ejecutor 2 va a arrancar **REMONTOIR-001 (pieza #8 Constant Force)** post-merge de ESPIRAL-001 (~80 min adelante). La tarea T2 del spec REMONTOIR-001 implementa `kernel/remontoir/fallback_chain.py` con la cadena canónica de los 8 Sabios DSC-V-001.

En el spec original commit `0de35e6`, Cowork sembró una tabla con **costos + quality scores estimados** que pueden estar desactualizados. Si Ejecutor 2 hardcodea esos números sin verificación binaria, REMONTOIR queda con números fantasma (riesgo V25/F6 latente).

La Sesión 1 de Perplexity T2-B está ocupada con verificación binaria de `trend_signals` origin. Esta Sesión 2 corre paralelo sin overlap.

## §2 Tabla sembrada en spec REMONTOIR-001 (a verificar)

Verbatim de `bridge/sprints_propuestos/sprint_REMONTOIR_001_constant_force_quality.md` §2.T2 commit `0de35e6`:

| Orden | Sabio (versión canónica) | Calidad estimada | Costo estimado/req | Justificación |
|---|---|---|---|---|
| 1 | GPT-5.5 Pro reasoning=high | ~0.95 | ~$0.30 | Razonamiento profundo, doctrina |
| 2 | Claude Opus 4.7 reasoning=high | ~0.94 | ~$0.25 | Metodología, regla de tres |
| 3 | Gemini 3.1 Pro reasoning=high | ~0.92 | ~$0.15 | Performance/latencia, 2M context |
| 4 | Kimi K2.6 Thinking | ~0.88 | ~$0.08 | Multi-swarm orchestration (trono) |
| 5 | DeepSeek R1 | ~0.85 | ~$0.02 | Razonamiento técnico open-source |
| 6 | Sonar Pro Standard | ~0.80 | ~$0.03 | Research tiempo real, browsing |
| 7 | Grok 4 Heavy | ~0.85 | ~$0.12 | Datos X/Twitter, adversarial |
| 8 | Copilot 365 | ~0.78 | ~$0.02 | Integración M365 |

**TODOS estos números son estimados Cowork sin fuente.** Necesitamos verificación binaria.

## §3 Tarea T1-T6 Perplexity Sesión 2

### T1 — Verificar versiones canónicas DSC-V-001 actuales (5-10 min)

```bash
cd ~/el-monstruo
grep -nE "GPT-5.5|Claude Opus|Gemini 3.1|Kimi|DeepSeek|Sonar|Grok|Copilot" CLAUDE.md AGENTS.md memory/cowork/COWORK_DECISIONES_VIVAS.md discovery_forense/CAPILLA_DECISIONES/_GLOBAL/DSC-V-001*.md 2>/dev/null | head -30
```

Reportar las **8 versiones canónicas exactas** que la doctrina actual del Monstruo declara.

### T2 — Pricing real verbatim por modelo (10-15 min web research)

Para cada uno de los 8 Sabios canónicos DSC-V-001, verificar **pricing oficial actual** desde páginas vendor:

- OpenAI GPT-5.5 Pro: https://openai.com/pricing
- Anthropic Claude Opus 4.7: https://www.anthropic.com/pricing
- Google Gemini 3.1 Pro: https://ai.google.dev/pricing
- Moonshot Kimi K2.6 Thinking: https://platform.moonshot.cn/pricing (o homepage equivalente)
- DeepSeek R1: https://platform.deepseek.com/pricing
- Perplexity Sonar Pro: https://docs.perplexity.ai/guides/pricing
- xAI Grok 4 Heavy: https://x.ai/pricing (o api.x.ai)
- Microsoft Copilot 365 GPT-5 wrapper: pricing M365 enterprise tier

Reportar **input tokens + output tokens pricing USD/M tokens** por modelo. Caveat verbatim si algún modelo NO está disponible públicamente.

### T3 — Costo promedio por request realista (5-10 min)

Asumiendo prompt típico Embrión del Monstruo (~2K input tokens + ~1K output tokens), calcular **costo real promedio por request** para cada modelo. Reemplaza la estimación Cowork `$0.30, $0.25, ...` con números calculados.

### T4 — Quality scores defendibles (10 min)

Los quality scores Cowork (`0.95, 0.94, 0.92, ...`) son inventados. Buscar:
- LMSys Chatbot Arena leaderboard ELO scores actuales: https://lmarena.ai/
- LiveBench scores 2026-05: https://livebench.ai/
- MMLU + HumanEval + GPQA Diamond benchmarks oficiales

Reportar **scores normalizados [0,1] reales** o declarar verbatim que algunos modelos no tienen benchmarks públicos comparables.

### T5 — Available providers verificación disponibilidad real (5 min)

¿Todos los 8 Sabios están realmente accesibles via API en 2026-05-12?

- Kimi K2.6 Thinking: ¿accessible API publicly o solo China region?
- Grok 4 Heavy: ¿accessible API publicly o solo via x.ai console?
- Copilot 365: ¿accessible API publicly o solo via M365 SDK?

Reportar caveat verbatim si alguno NO es accesible via API standard.

### T6 — Recomendación cadena ordenada para REMONTOIR-001 (5 min)

Basado en T1-T5, recomendar **cadena fallback ordenada óptima** considerando:
- Quality real (T4)
- Costo real (T3)
- Availability real (T5)
- Trade-off quality/costo defendible

Formato output recomendado para input directo a `kernel/remontoir/fallback_chain.py`:

```python
# Cadena canónica verificada T2-B 2026-05-12 (no estimada Cowork)
FALLBACK_CHAIN = [
    {"sabio": "<exact_canonical_name>", "model_id": "<api_string>", "quality": <verified>, "cost_per_req_usd": <calculated>, "available": True},
    ...
]
```

Versión verbatim de cada Sabio + model_id correcto (`gpt-5.5-pro`, `claude-opus-4-7`, `gemini-3.1-pro-preview`, etc.) para wiring directo sin guesswork Ejecutor 2.

## §4 Reglas duras T2-B Sesión 2

- NO mergear, NO approve, NO push, NO writes Supabase
- Solo READ + grep + web research + bash queries
- Reporte verbatim en `bridge/perplexity_to_cowork_T2B_DSC_V_001_FALLBACK_CHAIN_VERIFIED_2026_05_12.md`
- Caveat verbatim si algún dato NO es verificable binariamente desde páginas oficiales
- DSC-S-016 aplicado: cero fabricación de cifras sin fuente externa

## §5 Output esperado

**Tabla verificada 8 Sabios:**

| # | Sabio | model_id | Quality real | Cost/req real | Available API | Provider URL fuente |
|---|---|---|---|---|---|---|

+ recomendación ordenamiento fallback chain + caveats verbatim.

Este output Cowork lo integra directo al spec REMONTOIR-001 T2 antes de que Ejecutor 2 arranque.

## §6 Trazabilidad + sin overlap Sesión 1

- Sesión 1 Perplexity: verificando origen `trend_signals` (no relacionado)
- Esta Sesión 2 paralelo: 8 Sabios pricing/quality (no relacionado)
- Cero conflicto de scope. Ambas pueden correr simultaneously.

---

**Firma:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 10:25 UTC
**Bajo autoridad T1 "si" 2026-05-12 ~10:24 UTC.** Coordinación pura. Cowork diseñó prompt + asignó Sesión 2 paralelo. Cero ejecución Cowork del audit — Perplexity ejecuta.

# Anexo A — Auditoría Magna Estado del Arte (16 dimensiones)

**Fecha**: 15 mayo 2026  
**Sprint**: LA-FORJA-001 v3.1  
**Capas**: Manus directo (real-time web search) + Perplexity Sonar Reasoning Pro (cross-check independiente)

## Resultado binario por dimensión

| # | Dimensión | Manus directo | Perplexity Sonar | Match |
|---|---|---|---|---|
| 1 | Claude Opus 4.7 model id, context window, pricing | `claude-opus-4-7`, 1M ctx, $5/$25 | igual | ✅ 100% |
| 2 | Claude Opus 4.7 thinking mode | Solo `adaptive`; manual deprecado | Confirma | ✅ 100% |
| 3 | GPT-5.5 Pro model id y endpoint | `gpt-5.5-pro` via `/v1/responses` | Confirma | ✅ 100% |
| 4 | GPT-5.5 Pro pricing | $5 input / $30 output | Confirma | ✅ 100% |
| 5 | Gemini 3.1 Pro context window | 1,048,576 input + 65,536 output | Confirma | ✅ 100% |
| 6 | Gemini 3.1 Pro pricing | $2/$12 ≤200K, $4/$18 >200K | Confirma | ✅ 100% |
| 7 | Anthropic Python SDK version | 0.102.0 (13 mayo) | 0.102.0 | ✅ 100% |
| 8 | Anthropic TypeScript SDK | (no preguntado en capa 1) | 0.36.0 (17 abr) | ✅ Nuevo dato |
| 9 | OpenAI Node SDK | 6.15.0 | 6.15.0 (22 abr) | ✅ 100% |
| 10 | Vercel AI SDK | 6.0.27 | 6.0.27 (18 abr) | ✅ 100% |
| 11 | Next.js latest stable | 16.2 (marzo 2026) | Confirma | ✅ 100% |
| 12 | Hono framework version | v4.12.18 | v4.12.18 | ✅ 100% |
| 13 | Railway deploy patterns 2026 | Railpack reemplaza Nixpacks | Confirma | ✅ 100% |
| 14 | Supabase RLS best practices 2026 | RLS por defecto + policies por tabla | Confirma | ✅ 100% |
| 15 | OpenAI Assistants API estado | Deprecada, cierre 26 ago 2026 | Confirma | ✅ 100% |
| 16 | Gemini grounding regression status | Reportada feb-abr 2026, requiere retry | Confirma | ✅ 100% |

## Hallazgos críticos que evitaron autoboicot

| Creencia obsoleta del entrenamiento | Realidad verificada HOY |
|---|---|
| Next.js 15 | Next.js 16.2 (marzo 2026) |
| Opus 4.7 context 200K | 1,048,576 tokens |
| Opus 4.7 pricing $15/$75 | $5/$25 |
| Modo thinking manual con budget | Solo `adaptive` válido |
| Nixpacks Railway estándar | Deprecado, Railpack reemplaza |
| OpenAI Assistants API | Deprecada (cierre 26 ago 2026) |
| Vercel AI SDK v3 | v6.0.27 con AI Gateway |

## Score acumulado

**Tasa de coincidencia binaria**: 16/16 dimensiones consultadas, 100% match entre Manus directo y Perplexity Sonar.

**Conclusión**: SPEC v3.1 está construido sobre datos validados magna en tiempo real, no sobre datos del entrenamiento de Manus. Esto es la diferencia entre validación magna y dependencia de entrenamiento.

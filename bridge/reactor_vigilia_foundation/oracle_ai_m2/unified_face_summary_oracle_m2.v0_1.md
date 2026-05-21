# Unified Face Summary — Oracle M2

**Sprint:** SPR-ORACLE-AI-M2-001
**Ejecutado:** 2026-05-20T23:47:05.907140+00:00
**Veredicto:** PASS

## Resumen para T1

El Oráculo M2 ejecutó sondas read-only contra 6 proveedores de IA. De los 6 proveedores objetivo:

- **4 verificados en tiempo real** (REALTIME_VERIFIED): openai, anthropic, google_gemini, xai_grok
- **2 bloqueados** (ACCESS_BLOCKED): perplexity, deepseek

### Modelos Detectados (Top por Proveedor)

**openai:** babbage-002, chat-latest, chatgpt-image-latest, davinci-002, gpt-3.5-turbo

**anthropic:** claude-haiku-4-5-20251001, claude-opus-4-1-20250805, claude-opus-4-20250514, claude-opus-4-5-20251101, claude-opus-4-6

**google_gemini:** antigravity-preview-05-2026, aqa, deep-research-max-preview-04-2026, deep-research-preview-04-2026, deep-research-pro-preview-12-2025

**xai_grok:** grok-4.20-0309-non-reasoning, grok-4.20-0309-reasoning, grok-4.20-multi-agent-0309, grok-4.3, grok-build-0.1

**perplexity:** ACCESS_BLOCKED_API_ERROR

**deepseek:** ACCESS_BLOCKED_NO_KEY

### Costo Total Estimado
$0.0050 USD (dentro del budget cap de $5.00 USD)

### Siguiente Paso Recomendado
SPR-ORACLE-POST-M2-RISK-RECLASSIFICATION-001 — Reclasificar risk_class de R0 a R1+ para las capacidades ahora verificadas empíricamente.

### Restricciones Activas
- No se activó scheduler ni daemon.
- No se modificó el catálogo original.
- No se reclasificó risk_class.
- No se filtraron secrets.

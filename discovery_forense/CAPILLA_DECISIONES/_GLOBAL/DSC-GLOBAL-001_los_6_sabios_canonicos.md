---
id: DSC-V-001
proyecto: GLOBAL
tipo: validacion_realtime
titulo: "Los 6 Sabios canónicos al 2026-05: GPT-5.5 Pro, Claude Opus 4.7, Gemini 3.1 Pro, Grok 4, DeepSeek R1, Perplexity Sonar Reasoning Pro"
estado: firme
fecha: 2026-05-06
fuentes:
  - skill:consulta-sabios
cruza_con: ["ninguno"]
---

# Los 6 Sabios canónicos al 2026-05

## Decisión

Se establecen los 6 Sabios canónicos verificados contra APIs reales al 2026-05: GPT-5.5 Pro (OpenAI), Claude Opus 4.7 (Anthropic), Gemini 3.1 Pro (Google), Grok 4 (xAI), DeepSeek R1 (OpenRouter) y Perplexity Sonar Reasoning Pro. Se prohíbe usar `temperature` con GPT-5.5 Pro y Claude Opus 4.7, y se requiere `/v1/responses` para GPT-5.x Pro.

## Por qué

La validación en tiempo real (24 abril 2026) descubrió que versiones anteriores fallaban silenciosamente. Claude 3.x y Sonar Reasoning están obsoletos. GPT-5.5 Pro y Claude Opus 4.7 rechazan `temperature` (HTTP 400). GPT-5.x Pro no funciona con `/v1/chat/completions`.

## Implicaciones

Cualquier script o skill que consulte a los Sabios debe usar `conector_sabios.py` o `run_consulta_sabios.py` para evitar fallos de API. No se deben usar modelos obsoletos ni endpoints incorrectos.

## Estado de validación

firme — derivado del corpus existente del ecosistema (Sprint Memento 2026-05-05)
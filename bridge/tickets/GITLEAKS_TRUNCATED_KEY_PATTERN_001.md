---
id: GITLEAKS-TRUNCATED-KEY-PATTERN-001
fecha: 2026-05-12T09:10:00Z
emisor: Cowork T2-A (extraído del leak P0 detectado en commit 972ea02)
severidad: P1 preventivo
estado: pendiente_owner
prioridad: media (preventivo, no urgente operativo)
---

# Ticket GITLEAKS-TRUNCATED-KEY-PATTERN-001 — Regla `.gitleaks.toml` para detectar prefijos truncados

## Origen

Commit `972ea02` 2026-05-12 ~07:26 UTC introdujo en bridge file un patrón `sk-ant-api03-LWY9v2...buQtfgAA` (key Anthropic truncada con `...`). El pre-commit hook gitleaks actual **NO lo detectó** porque su regex busca strings continuos largos.

Cowork T2-A audit DSC-G-008 v3 §4 detectó binariamente post-push. Si gitleaks hubiera tenido regla preventiva, el commit habría sido bloqueado.

## Síntoma

`.gitleaks.toml` actual NO incluye patron para detectar prefijos/sufijos truncados separados por `...`, `[...]`, `<...>`, `***`, etc. Esto deja un gap estructural para PRs futuros que mencionen "`sk-ant-api03-ABC...XYZ`" en docs.

## Solución propuesta

Agregar regla a `.gitleaks.toml`:

```toml
[[rules]]
id = "anthropic-key-truncated"
description = "Anthropic API key prefix even when truncated with ellipsis"
regex = '''sk-ant-api03-[A-Za-z0-9_-]{6,}\s*(\.{3}|\[\.\.\.\]|<\.\.\.>|\*{3})\s*[A-Za-z0-9_-]{4,}'''
tags = ["anthropic", "truncated", "prefix-sufix"]
severity = "high"

[[rules]]
id = "openai-key-truncated"
description = "OpenAI/OpenRouter key prefix even when truncated"
regex = '''sk-(or-)?[A-Za-z0-9_-]{6,}\s*(\.{3}|\[\.\.\.\]|<\.\.\.>|\*{3})\s*[A-Za-z0-9_-]{4,}'''
tags = ["openai", "openrouter", "truncated"]
severity = "high"

[[rules]]
id = "supabase-jwt-truncated"
description = "Supabase JWT prefix even when truncated"
regex = '''eyJ[A-Za-z0-9_-]{20,}\s*(\.{3}|\[\.\.\.\]|<\.\.\.>|\*{3})\s*[A-Za-z0-9_-]{10,}'''
tags = ["supabase", "jwt", "truncated"]
severity = "high"
```

## Tests de regresión

Agregar `tests/test_gitleaks_truncated_patterns.py` con ≥6 casos: 3 truncados válidos (debe bloquear) + 3 false-positive controls (no debe bloquear: doc genérico, ejemplo educacional con `EXAMPLE_KEY`, formato shell `${VAR}...$EOF`).

## Owner candidato

Cualquier Hilo Manus con bandwidth. ETA <15 min Cowork puro o <30 min Manus con tests.

## Trazabilidad

- Commit origen: `972ea02` línea 19 bridge final report
- Detectado por: Cowork DSC-G-008 v3 §4 audit binario
- DSC enforzado: DSC-S-002 (pre-commit hooks obligatorios)

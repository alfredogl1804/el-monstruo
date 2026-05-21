# M2 Provider Registry

Este documento establece el registro estabilizado de proveedores autorizados para la cadena M2, incorporando las correcciones de *provider drift* detectadas en SPR-REACTOR-M2-ONESHOT-001.

## Regla Dura
**Ningún proveedor no verificado ni modelo no listado aquí puede entrar a la cadena M2.**

## Proveedores y Modelos Vigentes

| Proveedor | Modelo Vigente | Costo Estimado (in/out por 1K) | Estado | Fallback Permitido |
|-----------|----------------|--------------------------------|--------|--------------------|
| **OpenAI** | `gpt-4o-mini` | $0.005 / $0.015 | `VERIFIED` | NO |
| **Anthropic** | `claude-sonnet-4-20250514` | $0.003 / $0.015 | `VERIFIED` | NO |
| **Google** | `gemini-2.0-flash` | $0.00125 / $0.005 | `VERIFIED` | NO |
| **xAI** | `grok-3-mini-fast` | $0.005 / $0.015 | `VERIFIED` | NO |

## Proveedores Bloqueados

| Proveedor | Estado | Razón | Acción Requerida |
|-----------|--------|-------|------------------|
| **Perplexity** | `BLOCKED_403` | Error 403 Forbidden | Fix billing / API key |
| **DeepSeek** | `KEY_REQUIRED` | Falta API key en entorno | Provisionar credencial |

## Modelos Deprecated (Provider Drift)

Los siguientes modelos fueron detectados como obsoletos y han sido retirados del registro. **Cualquier intento de usarlos debe ser tratado como error de drift, no como un retry normal.**

- `claude-3-5-haiku-20241022` (Anthropic) → Reemplazado por `claude-sonnet-4-20250514`
- `gemini-2.0-flash-lite` (Google) → Reemplazado por `gemini-2.0-flash`

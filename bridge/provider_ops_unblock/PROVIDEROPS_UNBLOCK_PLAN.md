# ProviderOps Unblock Plan

**Sprint:** SPR-ACCELERATOR-WHILE-LIMITED-R0-RUNS-001 — Carril E
**Status:** DRAFT

## 1. Contexto
Actualmente, el Oráculo y el Auditor operan con 4 de los 6 proveedores verificados (OpenAI, Anthropic, Google, xAI). Dos proveedores críticos están bloqueados:
- **Perplexity:** Retorna error 403 Forbidden.
- **DeepSeek:** Falta inyectar la API key.

## 2. Unblock: Perplexity (403 Forbidden)
**Problema:** La API de Sonar (Perplexity) rechaza las peticiones.
**Diagnóstico Probable:**
- API Key expirada o sin créditos.
- Endpoint incorrecto (usando `/chat/completions` en lugar del específico de Sonar si cambió).
- Headers faltantes (ej. `User-Agent` o `Accept`).

**Plan de Acción:**
1. T1 debe verificar el estado de la API key en el dashboard de Perplexity.
2. Si la key es válida, ejecutar un script de diagnóstico aislado (`perplexity_diag.py`) que imprima los headers exactos de la petición.
3. Actualizar `PROVIDER_REGISTRY_M2.json` con el endpoint correcto si hubo un cambio de API.

## 3. Unblock: DeepSeek (KEY_REQUIRED)
**Problema:** No hay API key configurada para DeepSeek en el entorno.
**Diagnóstico:** El registry lo marca como `KEY_REQUIRED`.

**Plan de Acción:**
1. T1 debe generar una API key en la plataforma de DeepSeek.
2. Inyectar la key en el entorno (vía Supabase Secrets o archivo local seguro, dependiendo de la política de secretos).
3. Actualizar `PROVIDER_REGISTRY_M2.json` a `VERIFIED` tras una prueba exitosa (`deepseek_diag.py`).

## 4. Criterio de Éxito
- Ejecutar un repeat del Oráculo Shadow con los 6 proveedores devolviendo `SUCCESS`.
- Costo total por ciclo con 6 proveedores estimado en ~$0.012 USD.

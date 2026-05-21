# Bridge Report — SPRINT 004 — Kernel Read-Only Compatibility

**Agent:** Manus C  
**Batch:** SPRINT BATCH 002 / COCKPIT PRODUCTIVE CONSOLIDATION  
**Date:** 2026-05-18  
**Status:** DONE  

## 1. Qué hice

Audité los 44 endpoints GET del kernel de El Monstruo para documentar compatibilidad read-only con el Cockpit UI. Evalué la configuración CORS actual, las dependencias de autenticación, y la viabilidad de tests read-only sin DB/Supabase/writes.

## 2. Archivos tocados

| Archivo | Acción | Descripción |
|---|---|---|
| `bridge/cockpit/SPR-HITL-COCKPIT-004_KERNEL_READONLY_COMPAT.md` | CREATED | Contrato read-only completo |
| `bridge/cockpit/batch_002/outputs/SPR004_MANUS-C_KERNEL_READONLY_COMPAT.md` | CREATED | Este bridge report |

## 3. Links / Path / Commit

- **Commit contrato:** `7ce8b4c` (branch `monstruo-reality-atlas-001`)
- **URL contrato:** https://github.com/alfredogl1804/el-monstruo/blob/monstruo-reality-atlas-001/bridge/cockpit/SPR-HITL-COCKPIT-004_KERNEL_READONLY_COMPAT.md
- **URL bridge report:** https://github.com/alfredogl1804/el-monstruo/blob/monstruo-reality-atlas-001/bridge/cockpit/batch_002/outputs/SPR004_MANUS-C_KERNEL_READONLY_COMPAT.md
- **PR:** N/A (no se abrió PR, commit directo a branch de trabajo)

## 4. Evidencia verificable

- 44 endpoints GET identificados vía `grep -rn "@router.get\|@app.get" kernel/` (verificable en repo).
- CORS config en `kernel/main.py` L1782-1787: `allow_origins=["*"]`.
- Auth middleware en `kernel/auth.py` L40: `PUBLIC_PATHS` solo incluye `/health`, `/health/auth`, `/docs`, `/openapi.json`, `/redoc`.
- Todos los `/v1/*` requieren `X-API-Key` header (fail-closed si no configurado).
- Preflight `OPTIONS` bypasses auth (L97 auth.py).

## 5. Confirmación de restricciones

| Restricción | Respetada |
|---|---|
| No POST | YES |
| No DB writes | YES |
| No Supabase | YES |
| No auth/user_id/RLS changes | YES |
| No approve/reject real | YES |
| No memory writes | YES |
| No Memento/Anti-Dory writes | YES |
| No secrets | YES |
| No deploy | YES |
| No merge | YES |
| No ready-for-review | YES |
| No production connection | YES |

## 6. P0/P1/P2

- **P0:** Ninguno.
- **P1:** Ninguno.
- **P2:** Fragilidad de inicialización — endpoints devuelven 503 si subsistema no arrancó. Cockpit debe implementar error boundaries por widget.

## 7. Qué debe auditar Perplexity

- Verificar si `allow_origins=["*"]` + `allow_credentials=True` en FastAPI/Starlette es explotable cuando existe un middleware de API Key. Confirmar si es riesgo real o teórico para el contexto monousuario actual.

## 8. Qué debe integrar ChatGPT-2

- Auth obligatorio: todo widget Cockpit que llame a `/v1/*` debe incluir `X-API-Key` header.
- Error handling: implementar fallback UI para 503 responses.
- Endpoints prioritarios MVP Cockpit: `/v1/embrion/diagnostic`, `/v1/finops/summary`, `/v1/hitl/pending`, `/v1/tools`, `/v1/memory/status`.
- No necesita CORS config ni proxy.

## 9. Qué requiere T1

Ninguna decisión bloqueante para read-only. La deuda de `allow_origins=["*"]` puede endurecerse en un sprint futuro de security hardening (no urgente para monousuario).

# Ticket: BRAND_ENGINE_CANARY_INIT_LOG_001

## Origen
Detectado durante TA-BRAND-CANARY-001 T3 (Manus Hilo Ejecutor 1, 2026-05-12).

## Problema
El kernel NO emite log textual explícito `brand_engine_canary_initialized` cuando inicializa Brand Engine en modo canary. Esto obliga a inferir el estado del canary leyendo env vars + logs colaterales (`brand_engine_routes_registered`, `brand_audit_completed`).

## Verificación de la ausencia
```bash
$ grep -rn "brand_engine_canary_initialized" kernel/
(sin resultados)
```

## Solución propuesta
Agregar al inicializador de BrandEngine (probablemente en `kernel/embriones/brand_engine/brand_engine.py` o `kernel/main.py:1820` cerca de `brand_engine_routes_registered`):

```python
import os
if os.getenv("BRAND_ENGINE_CANARY", "false").lower() == "true":
    logger.info(
        "brand_engine_canary_initialized",
        mode=os.getenv("BRAND_ENGINE_MODE", "shadow"),
        sample_rate=float(os.getenv("BRAND_ENGINE_SAMPLE_RATE", "0.1")),
        window_hours=os.getenv("BRAND_ENGINE_TELEGRAM_WINDOW_HOURS", "11-03"),
        rate_limit=int(os.getenv("BRAND_ENGINE_TELEGRAM_RATE_LIMIT", "3")),
    )
```

## Prioridad
**Baja.** No bloquea funcionalidad. Solo afecta observabilidad/debuggability del modo canary.

## Sprint sugerido
Sprint 83 (próxima iteración de Brand Engine).

## Estado
ABIERTO — pendiente de asignación.

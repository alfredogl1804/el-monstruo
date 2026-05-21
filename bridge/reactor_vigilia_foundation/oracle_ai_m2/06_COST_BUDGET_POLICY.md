# Política de Presupuesto y Costos

**SPRINT:** SPR-ORACLE-AI-M2-001
**Estado:** DOCTRINE_CANDIDATE

Para evitar el consumo descontrolado de créditos durante la verificación empírica, M2 opera bajo un "Hard Cap" de presupuesto.

## 1. Límites Estrictos (Hard Caps)
- **Costo Máximo Total:** $5.00 USD
- **Costo Máximo por Proveedor:** $1.00 USD
- **Máximo de Llamadas por Proveedor:** 3
- **Máximo de Llamadas Totales:** 18

## 2. Naturaleza de las Sondas
Las sondas están diseñadas para ser de muy bajo costo:
- La mayoría de las sondas utilizarán endpoints `/models` (ej. OpenAI, Anthropic), los cuales típicamente son gratuitos o tienen un costo insignificante.
- Si un proveedor requiere una llamada de inferencia para verificar disponibilidad (ej. Perplexity), se enviará un prompt mínimo (1-5 tokens) con `max_tokens=1`.

## 3. Estimación de Costos (Cost Ledger)
Dado que el entorno de ejecución puede no tener acceso a las APIs de billing de los proveedores en tiempo real, el script generará un `api_cost_ledger.v0_1.json`.

Si el costo exacto no se puede medir, el script registrará:
- `cost_source`: "COST_ESTIMATE_ONLY"
- `estimated_cost_usd`: Un valor conservador (ej. $0.001 por llamada).
- `confidence`: "LOW" o "MEDIUM".

**Regla de Oro:** El Oráculo M2 nunca debe inventar un costo exacto si no tiene acceso a la data real de facturación. Es preferible registrar un estimado con baja confianza que presentar un dato falso como verdadero.

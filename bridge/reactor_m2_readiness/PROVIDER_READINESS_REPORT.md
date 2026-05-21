# Provider Readiness Report — M2 Chain

Este reporte documenta el estado actual de los proveedores de IA requeridos para la ejecución completa del Oráculo en M2. 

*Nota de Seguridad: Este reporte ha sido generado verificando la existencia de las variables de entorno sin imprimir ni exponer ningún secret en plaintext, cumpliendo con la Regla Dura #6 (DSC-S-001).*

## Resumen de Estado

| Métrica | Valor |
|---------|-------|
| Total Proveedores Core | 6 |
| Proveedores Listos (M2 Verified) | 4 |
| Proveedores Bloqueados / Pendientes | 2 |

## Detalle por Proveedor

### Proveedores Verificados (Ready)

Estos proveedores fueron validados exitosamente durante el sprint `SPR-ORACLE-AI-M2-001` y cuentan con credenciales activas en el entorno:

- **OpenAI (GPT-4o / o1 / o3-mini):** `VERIFIED_M2`
- **Anthropic (Claude 3.5 Sonnet / 3.7 Sonnet):** `VERIFIED_M2`
- **Google (Gemini 1.5 Pro / 2.5 Flash):** `VERIFIED_M2`
- **xAI (Grok 2 / Grok 3):** `VERIFIED_M2`

### Proveedores Pendientes (Blocked)

Estos proveedores requieren intervención de T1 antes de poder integrarse a la cadena M2:

- **Perplexity (Sonar Pro):** `403_FIX_REQUIRED`. La API key actual devuelve error 403 (Forbidden). Se requiere rotación o validación de billing por parte de T1.
- **DeepSeek (R1 / V3):** `KEY_REQUIRED`. No se detectó la variable de entorno `DEEPSEEK_API_KEY`. T1 debe provisionar esta credencial en la bóveda.

## Capacidades de Ejecución

### Ejecución Zero-Cost (Local Only)

Las siguientes operaciones pueden ejecutarse sin incurrir en costos de API externa ni requerir autorización de budget por parte de T1:

- **Heartbeat R0 local:** Validación de estado del sistema y constraints.
- **Dispatcher routing:** Enrutamiento de eventos a través del Policy Engine.
- **Oráculo shadow (mock):** Ejecución de la lógica del Oráculo utilizando respuestas mockeadas pre-grabadas, ideal para dry-runs de la cadena.

### Ejecución que Requiere Autorización T1 (Budget)

Cualquier ejecución que invoque a los siguientes proveedores requiere autorización explícita de T1 en el `T1_DECISION_PACK` (sección Budget):

- OpenAI
- Anthropic
- Google
- xAI

## Recomendación

Para alcanzar M2 Readiness completo (6/6 proveedores), se solicita a T1:
1. Validar el billing o rotar la API key de Perplexity.
2. Provisionar la API key de DeepSeek.
3. Autorizar un presupuesto controlado (`capped external provider calls`) para permitir la ejecución de la cadena M2 completa con los 4 proveedores actualmente listos.

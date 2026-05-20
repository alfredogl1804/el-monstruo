# Contrato de Sondas a APIs (API Probe Contract)

**SPRINT:** SPR-ORACLE-AI-M2-001
**Estado:** DOCTRINE_CANDIDATE

## 1. Definición de Sonda (Probe)
Una "sonda" es una petición HTTP(s) ejecutada por el Oráculo M2 hacia un proveedor de IA externo. Su único propósito es verificar la conectividad, la validez de la credencial, y la disponibilidad de modelos.

## 2. Naturaleza Read-Only
Las sondas están estrictamente limitadas a operaciones de lectura o inferencia mínima.
- **Permitido:** GET `/v1/models`, GET `/models`.
- **Permitido:** POST `/v1/chat/completions` con un prompt de inferencia mínimo (ej. "Responde con la palabra OK").
- **Prohibido:** POST, PUT, PATCH, DELETE que modifiquen el estado de la cuenta del usuario (ej. crear finetuning jobs, borrar archivos, modificar billing).

## 3. Aprobación del Dispatcher
Antes de ejecutar una sonda contra cualquier proveedor, el script debe solicitar permiso al Dispatcher mediante un `action_request` del tipo `execute_api_probe`.
- Si el Dispatcher responde `ALLOW`, la sonda se ejecuta.
- Si el Dispatcher responde `DENY`, la sonda se cancela y el proveedor se marca como `ACCESS_BLOCKED_POLICY`.

## 4. Estructura de Resultados
Cada sonda exitosa debe retornar:
- `provider_id`: Identificador del proveedor.
- `probe_method`: Método utilizado (`official_api`).
- `model_ids_detected`: Lista de modelos disponibles.
- `timestamp_utc`: Momento exacto de la verificación.
- `raw_response_hash`: Hash SHA-256 de la respuesta cruda para trazabilidad.
- `redacted_sample`: Una muestra truncada y sanitizada de la respuesta.

## 5. Manejo de Errores
Si una sonda falla, el script no debe detenerse (crash). Debe capturar la excepción, registrar el fallo, y clasificar el estado de acceso como:
- `ACCESS_BLOCKED_NO_KEY`: Credencial no encontrada en el entorno.
- `ACCESS_BLOCKED_API_ERROR`: El servidor retornó 4xx o 5xx.
- `ACCESS_BLOCKED_RATE_LIMIT`: El servidor retornó 429.
- `ACCESS_BLOCKED_UNSUPPORTED`: La librería cliente falló o el endpoint no existe.

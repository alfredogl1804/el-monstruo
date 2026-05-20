# Reglas de Manejo de Secretos

**SPRINT:** SPR-ORACLE-AI-M2-001
**Estado:** DOCTRINE_CANDIDATE

La ejecución de sondas a APIs requiere el uso de credenciales reales (API Keys) inyectadas en el entorno. Para garantizar que estas credenciales nunca se filtren en los artefactos, logs o reportes, M2 implementa un protocolo estricto de redacción.

## 1. Prohibición Absoluta
Está estrictamente prohibido imprimir, registrar, guardar en disco o transmitir por red cualquier API Key, Token, o Header de Autorización en texto plano.

## 2. Patrones de Redacción Obligatorios
Cualquier script que maneje credenciales debe implementar una función de redacción que reemplace las llaves reales por versiones ofuscadas antes de cualquier operación de I/O (print, logging, json.dump).

Los patrones de redacción requeridos son:
- `sk-proj-...` → `sk-***`
- `sk-ant-api...` → `anthropic-***`
- `xai-...` → `xai-***`
- `AIzaSy...` → `gemini-***`
- `pplx-...` → `pplx-***`
- `sk-or-v1-...` → `openrouter-***`
- `ghp_...` → `ghp-***`
- `sbp_...` → `sbp-***`

## 3. Sanitización de Respuestas (Redacted Samples)
Cuando se guarda un `redacted_sample` de la respuesta de una API:
- La respuesta cruda debe truncarse a un máximo de 500 caracteres.
- Se debe aplicar la función de redacción sobre la respuesta truncada para asegurar que el proveedor no haya hecho echo de la llave (poco común, pero posible en errores).
- Nunca se deben guardar los headers HTTP de la respuesta cruda, ya que pueden contener tokens de sesión o identificadores sensibles.

## 4. Consecuencia de Falla
Si el validador (Gate 3) detecta cualquier string que coincida con el formato de una API key real en los outputs generados, el sprint fallará inmediatamente (FAIL) y el artifact contaminado deberá ser destruido.

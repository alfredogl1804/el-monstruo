# Anti-Autoboicot: Protocolo de Validación de Dependencias

## Problema que resuelve
El agente tiene datos de entrenamiento con fecha de corte. Cuando escribe código, configs o references, tiende a usar versiones de su entrenamiento que pueden estar obsoletas, deprecadas, apagadas o renombradas. Esto causa que el código falle en producción, se pierda tiempo, y se desperdicien créditos.

## Regla Fundamental
> **NUNCA escribir una versión, nombre de modelo, o identificador de paquete "de memoria". SIEMPRE validar en tiempo real ANTES de escribir.**

## Protocolo de 4 Pasos (obligatorio)

### Paso 1: DETECTAR — Identificar referencias sensibles
Antes de escribir cualquier archivo, identificar si contiene:
- Nombres de modelos IA (gpt-X, claude-X, gemini-X, grok-X, deepseek-X, sonar-X)
- Versiones de paquetes Python/Node (requirements.txt, package.json, pyproject.toml)
- Tags de Docker images (postgres:X, langfuse:X, litellm:X)
- URLs de APIs o endpoints
- Nombres de servicios cloud que pueden cambiar

Si contiene CUALQUIERA de estos → activar Paso 2.

### Paso 2: VALIDAR — Investigar en tiempo real
Para CADA referencia sensible detectada:
1. Buscar con search tool: "{nombre} latest version {año actual}"
2. Verificar en la fuente oficial (PyPI, npm, Docker Hub, docs del proveedor)
3. Cruzar al menos 2 fuentes antes de escribir

**Para modelos IA específicamente:**
1. Verificar en la documentación oficial del proveedor
2. Confirmar que el model ID es callable (no deprecado/apagado)
3. Verificar la fecha de lanzamiento — si es >6 meses, buscar sucesor

### Paso 3: ESCRIBIR — Usar solo versiones validadas
- Escribir SOLO las versiones confirmadas en Paso 2
- Incluir comentario con fecha de validación: `# validated 2026-04-12`
- Si no se pudo validar → marcar con `# UNVALIDATED — verify before deploy`
- NUNCA asumir que una versión "probablemente sigue igual"

### Paso 4: VERIFICAR — Post-escritura
Después de escribir el archivo, extraer todas las versiones (ej. con grep) y verificar que coinciden con las validadas. Si alguna no coincide → corregir ANTES de commitear.

## Señales de Alerta (Red Flags)
Detener la ejecución inmediatamente si:
1. **Escribiste un model ID sin buscarlo** → STOP, buscar ahora
2. **Usaste una versión "redonda" (1.0, 2.0)** → probablemente es de tu entrenamiento, verificar
3. **El nombre del modelo no tiene fecha/versión** (ej: "gpt-5" sin sufijo) → buscar el ID exacto actual
4. **Estás escribiendo requirements.txt de memoria** → STOP, buscar cada paquete

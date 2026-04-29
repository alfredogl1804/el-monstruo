---
name: anti-autoboicot
description: Protocolo obligatorio anti-autoboicot que previene que el agente use versiones obsoletas de modelos IA, SDKs, frameworks o herramientas basándose en su entrenamiento. Usar SIEMPRE antes de escribir código, configuraciones, requirements, docker-compose, o cualquier referencia a versiones de software. Usar cuando se detecte que una versión usada no coincide con la realidad actual. Usar cuando se escriba cualquier archivo que contenga nombres de modelos IA, versiones de paquetes, o identificadores de APIs.
---

# Anti-Autoboicot: Protocolo de Validación en Tiempo Real

## Problema que resuelve

El agente tiene datos de entrenamiento con fecha de corte. Cuando escribe código, configs o references, tiende a usar versiones de su entrenamiento que pueden estar obsoletas, deprecadas, apagadas o renombradas. Esto causa que el código falle en producción, se pierda tiempo, y se desperdicien créditos.

**Caso real:** En abril 2026, el agente escribió 43 referencias con versiones obsoletas. 7 eran CRITICAL (modelos IA apagados, SDKs reescritos). 58% del código necesitó corrección.

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

```
1. Buscar con search tool: "{nombre} latest version {año actual}"
2. Verificar en la fuente oficial (PyPI, npm, Docker Hub, docs del proveedor)
3. Si existe un CSV/JSON de auditoría previa → usarlo como primera fuente
4. Cruzar al menos 2 fuentes antes de escribir
```

**Para modelos IA específicamente:**
```
1. Verificar en la documentación oficial del proveedor
2. Confirmar que el model ID es callable (no deprecado/apagado)
3. Verificar la fecha de lanzamiento — si es >6 meses, buscar sucesor
```

### Paso 3: ESCRIBIR — Usar solo versiones validadas

- Escribir SOLO las versiones confirmadas en Paso 2
- Incluir comentario con fecha de validación: `# validated 2026-04-12`
- Si no se pudo validar → marcar con `# UNVALIDATED — verify before deploy`
- NUNCA asumir que una versión "probablemente sigue igual"

### Paso 4: VERIFICAR — Post-escritura

Después de escribir el archivo:

```bash
# Extraer todas las versiones del archivo
grep -oP '[\w-]+==[0-9]+\.[0-9]+' archivo.txt
grep -oP '[\w/]+-[0-9]+' archivo.txt

# Comparar contra la fuente de verdad (CSV de auditoría si existe)
```

Si alguna versión no coincide con la validación → corregir ANTES de commitear.

## Señales de Alerta (Red Flags)

Detener la ejecución inmediatamente si:

1. **Escribiste un model ID sin buscarlo** → STOP, buscar ahora
2. **Usaste una versión "redonda" (1.0, 2.0)** → probablemente es de tu entrenamiento, verificar
3. **El nombre del modelo no tiene fecha/versión** (ej: "gpt-5" sin sufijo) → buscar el ID exacto actual
4. **Copiaste una versión de un archivo anterior** → verificar que siga siendo actual
5. **Estás escribiendo requirements.txt de memoria** → STOP, buscar cada paquete

## Fuentes de Verdad (en orden de prioridad)

1. **CSV/JSON de auditoría previa** en el sandbox (si existe)
2. **Documentación oficial** del proveedor (via search tool)
3. **PyPI/npm/Docker Hub** (via search tool o browser)
4. **Semilla v7.3 en Notion** (para modelos IA de los 6 Sabios)
5. **NUNCA tu entrenamiento** como fuente única

## Aplicación a Archivos Específicos

| Tipo de Archivo | Qué Validar |
|----------------|-------------|
| `requirements.txt` / `pyproject.toml` | CADA versión de CADA paquete |
| `package.json` | CADA versión de CADA dependencia |
| `docker-compose.yml` | CADA image tag |
| `Dockerfile` | Base image tag, versiones de instalación |
| `litellm_config.yaml` o similar | CADA model ID, CADA endpoint |
| Código Python/TS con model IDs | CADA string que sea un model name |
| `.env.example` | URLs de APIs, endpoints |
| `README.md` / docs | Versiones mencionadas en texto |

## Protocolo de Corrección Masiva

Cuando se detecta que múltiples referencias están obsoletas:

1. Extraer TODAS las referencias del codebase (grep exhaustivo)
2. Validar TODAS en paralelo (map subtasks)
3. Generar CSV con: referencia, versión usada, versión correcta, severidad
4. Corregir en orden: CRITICAL → HIGH → MEDIUM → LOW
5. Verificar post-corrección: grep + comparar contra CSV
6. Commitear con mensaje descriptivo: `fix: update N references to current versions (validated YYYY-MM-DD)`

## Integración con Otros Skills

- **consulta-sabios**: Antes de consultar, verificar que los model IDs en semilla v7.3 siguen vigentes
- **api-context-injector**: Verificar que los endpoints y versiones de APIs son actuales
- **el-monstruo-toolkit**: Verificar que las versiones del stack siguen siendo las mejores
- **optimizador-creditos**: Este protocolo ahorra créditos al evitar retrabajos por versiones obsoletas

## Mantra

> Investigar toma 30 segundos. Reescribir código obsoleto toma horas. SIEMPRE investigar primero.

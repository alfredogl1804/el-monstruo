---
name: validacion-tiempo-real
description: "Protocolo CORE y OBLIGATORIO que recuerda al agente su ventaja competitiva principal: la validación, investigación y descubrimiento en tiempo real. Úsalo SIEMPRE al inicio de cualquier tarea analítica, al consultar a otros modelos (Sabios), al redactar documentos de estado del arte, o cuando se requiera información actualizada. Este skill asegura que el agente NUNCA dependa solo de sus datos de entrenamiento o de las respuestas de otros LLMs sin verificarlas contra la realidad actual."
---

# Validación en Tiempo Real: El Diferenciador Principal

## Propósito Core

El verdadero poder de este agente **no reside en sus datos de entrenamiento**, sino en su capacidad única para interactuar con la realidad en tiempo real. Los demás modelos (incluyendo los 6 Sabios: GPT-5.4, Claude, Gemini, Grok, DeepSeek, Perplexity) están limitados por su fecha de corte de entrenamiento. 

**Este agente NO.** 

Este agente tiene acceso a herramientas de búsqueda, navegación web, ejecución de código y APIs que le permiten:
1. **Validar** afirmaciones (claims) contra fuentes primarias actuales.
2. **Investigar** a profundidad descubriendo información que no existía hace meses.
3. **Descubrir** insights críticos (como crisis geopolíticas, cambios de pricing, o features no anunciados) que los modelos estáticos ignoran.

## Reglas de Oro (Inquebrantables)

1. **NUNCA confíes ciegamente en tu propio entrenamiento** para datos fácticos, versiones de software, precios, o eventos recientes.
2. **NUNCA confíes ciegamente en las respuestas de otros modelos (Sabios)**. Sus respuestas son el *punto de partida*, no la verdad final.
3. **SIEMPRE añade una "Capa de Validación en Tiempo Real"** después de consultar a otros modelos y antes de entregar un resultado final.
4. **SIEMPRE busca "Descubrimientos Nuevos"**. Tu objetivo no es solo confirmar lo que dicen los Sabios, sino encontrar la pieza de información crítica que ellos omitieron (ej. "Meta adquirió Manus, pero los fundadores tienen prohibición de salida de China").

## El Protocolo de 3 Fases (IVD)

Aplica este protocolo (Investigación, Validación, Descubrimiento) en cada tarea relevante:

### Fase 1: Investigación Activa (El Grounding)
Antes de redactar o sintetizar, establece la realidad actual:
- Usa `search` tool con múltiples queries (noticias, info, apis).
- Usa `browser_navigate` para leer las fuentes primarias completas (no te quedes solo con los snippets de búsqueda).
- Documenta los hallazgos crudos en un archivo temporal (ej. `dossier_realidad.md`).

### Fase 2: Validación de Claims (El Filtro QA)
Cuando recibas input de otros modelos (o de tu propia memoria):
- Extrae las afirmaciones clave (Claims).
- Clasifícalas por prioridad (Alta, Media, Baja).
- Cruza cada claim contra tu Dossier de Realidad.
- Etiqueta explícitamente cada claim como:
  - `[VERIFICADO]` (con fuente)
  - `[CORREGIDO]` (con la corrección y fuente)
  - `[FALSO/OBSOLETO]` (con la refutación)

### Fase 3: Descubrimiento de Valor (El "10x")
Pregúntate: *¿Qué está pasando AHORA MISMO que cambia la narrativa?*
- Busca controversias recientes, bugs reportados ayer, cambios de pricing ocultos, o movimientos corporativos/geopolíticos.
- Destaca estos descubrimientos en tu output final como el valor diferencial que solo tú puedes aportar.

## Integración con Otros Flujos

- **Al usar `consulta-sabios`:** La respuesta de los sabios es el input para tu Fase 2 (Validación). NUNCA pases la respuesta de los sabios directamente al usuario sin pasar por este filtro.
- **Al usar `ciclo-investigacion-descubrimiento-perpetuo`:** Este protocolo ES el Stage 5 (Reality Validation Loop). Asegúrate de ejecutarlo con rigor.
- **Al escribir código o configs:** Este protocolo se solapa con `anti-autoboicot`. La validación en tiempo real aplica tanto a datos de negocio como a versiones de dependencias.

## El Mantra del Agente

> *"Mi memoria es falible y estática. Mi capacidad de investigar la realidad es infinita y dinámica. Mi valor no es lo que sé, sino lo que puedo verificar y descubrir hoy."*

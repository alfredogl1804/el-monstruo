---
name: protocolo-operativo-core
description: "El protocolo CORE unificado de Manus. OBLIGATORIO al inicio de CUALQUIER tarea analítica, consulta de sabios, o antes de escribir código/configuraciones. Integra 3 capas: 1) Validación en Tiempo Real (tu ventaja competitiva), 2) Consulta a los 6 Sabios (enjambre iterativo), y 3) Anti-Autoboicot (validación de dependencias y modelos). Usa este skill para garantizar que NUNCA dependes solo de tu entrenamiento y siempre entregas resultados verificados y 10x superiores."
---

# Protocolo Operativo Core: El Diferenciador Principal

Este skill unifica los tres pilares operativos de Manus (`validacion-tiempo-real`, `consulta-sabios` y `anti-autoboicot`) en un solo flujo de trabajo cohesivo. 

## El Problema Fundamental
Tu memoria (datos de entrenamiento) es falible, estática y tiene fecha de corte. Si operas basándote solo en ella, entregarás código obsoleto, análisis desactualizados y valor genérico. 

## La Solución: El Protocolo IVD (Investigación, Validación, Descubrimiento)

Tu verdadero poder reside en tu capacidad para interactuar con la realidad **en tiempo real**. Aplica este protocolo en cada tarea:

### Fase 1: Investigación Activa (Grounding y Anti-Autoboicot)
Antes de redactar, sintetizar o escribir código, establece la realidad actual:
- **Para Análisis:** Usa `search` y `browser_navigate` para leer fuentes primarias completas. Documenta hallazgos en un `dossier_realidad.md`.
- **Para Código/Configs (Anti-Autoboicot):** Identifica referencias sensibles (nombres de modelos IA, versiones de paquetes, tags de Docker). Busca la versión actual (ej. "{nombre} latest version 2026") y verifica en fuentes oficiales. **NUNCA escribas versiones "de memoria".**

*Para detalles completos del protocolo Anti-Autoboicot, lee: `/home/ubuntu/skills/protocolo-operativo-core/references/anti_autoboicot.md`*

### Fase 2: Consulta y Validación (El Enjambre y Filtro QA)
Cuando necesites consenso o análisis profundo, consulta al Consejo de 6 Sabios (GPT-5.4, Claude, Gemini, Grok, DeepSeek, Perplexity):
- Ejecuta la infraestructura de sabios (`run_consulta_sabios.py`) que orquesta automáticamente los 7 pasos, incluyendo validación post-síntesis.
- Si recibes input de otros modelos o de tu propia memoria, extrae los claims clave, crúzalos contra tu Dossier de Realidad, y etiquétalos como `[VERIFICADO]`, `[CORREGIDO]` o `[FALSO/OBSOLETO]`.

*Para instrucciones de ejecución de la consulta a sabios, lee: `/home/ubuntu/skills/protocolo-operativo-core/references/consulta_sabios.md`*

### Fase 3: Descubrimiento de Valor (El "10x")
Pregúntate: *¿Qué está pasando AHORA MISMO que cambia la narrativa?*
- Busca controversias recientes, bugs reportados ayer, cambios de pricing ocultos, o movimientos corporativos.
- Destaca estos descubrimientos en tu output final como el valor diferencial que **solo tú** puedes aportar (porque los modelos estáticos los ignoran).

## Reglas de Oro Inquebrantables

1. **NUNCA confíes ciegamente en tu propio entrenamiento** para datos fácticos, versiones de software, precios o eventos recientes.
2. **NUNCA confíes ciegamente en las respuestas de otros modelos (Sabios)**. Sus respuestas son el *punto de partida*, no la verdad final.
3. **SIEMPRE añade una "Capa de Validación en Tiempo Real"** antes de entregar un resultado final.
4. **SIEMPRE escribe código con versiones validadas en tiempo real**, añadiendo el comentario `# validated 2026-04-XX`.

## El Mantra del Agente

> *"Mi memoria es falible y estática. Mi capacidad de investigar la realidad es infinita y dinámica. Mi valor no es lo que sé, sino lo que puedo verificar y descubrir hoy."*

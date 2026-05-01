# Biblia de Implementación: Laguna XS.2

**Fecha de Lanzamiento:** 28 de Abril de 2026
**Versión:** XS.2
**Arquitectura Principal:** Mixture of Experts (MoE)

## 1. Visión General y Diferenciador Único

Laguna XS.2 es el modelo de segunda generación de la familia Laguna de Poolside, diseñado específicamente como un agente de codificación de pesos abiertos (open-weight). Su principal diferenciador radica en su eficiencia y capacidad en relación con su tamaño. Con 33 mil millones (33B) de parámetros totales y solo 3 mil millones (3B) activados durante la inferencia, Laguna XS.2 puede ejecutarse en una sola GPU, pero compite con modelos mucho más grandes en tareas de codificación agentic y de horizonte largo.

A diferencia de los agentes tradicionales que dependen en gran medida de la llamada a herramientas (tool calling) con interfaces estructuradas y fijas, Poolside concibe a Laguna XS.2 como un paso hacia agentes que utilizan el software como una interfaz más expresiva. La visión es que un agente capaz de escribir y ejecutar código puede componer acciones, paralelizar el trabajo y construir sus propios sistemas ad-hoc para interactuar con el mundo, superando las limitaciones de las herramientas predefinidas.

## 2. Arquitectura Técnica

La arquitectura de Laguna XS.2 se basa en un enfoque de Mixture of Experts (MoE), lo que permite un alto rendimiento con un costo computacional reducido durante la inferencia.

*   **Parámetros:** 33B parámetros totales, con 3B parámetros activados por token.
*   **Entrenamiento:** Entrenado desde cero en la "Model Factory" de Poolside utilizando 30 billones (30T) de tokens.
*   **Hardware de Entrenamiento:** Todo el proceso, desde la curación de datos hasta el post-entrenamiento, se realizó en hardware NVIDIA (específicamente GPUs NVIDIA Hopper).
*   **Optimizador:** Utiliza una versión optimizada para eficiencia del optimizador Muon.
*   **Infraestructura de Entrenamiento:** Entrenado utilizando la base de código propietaria de Poolside llamada "Titan".
*   **Compatibilidad:** Soporte desde el primer día en NVIDIA TensorRT-LLM y disponibilidad de una versión NVFP4 para un rendimiento óptimo en la arquitectura NVIDIA Blackwell.

## 3. Implementación/Patrones Clave

La implementación de Laguna XS.2 destaca por su enfoque en los datos, el aprendizaje por refuerzo y la integración con un entorno de ejecución.

*   **Curación de Datos y Automixing:** Poolside trata la curación de datos web como una optimización conjunta de calidad y diversidad. Utilizan modelos para puntuar la calidad de los datos, pero retienen intencionalmente porciones de datos de calidad media y baja para preservar la diversidad, lo cual es crítico para la generalización. Este enfoque produce aproximadamente el doble de tokens únicos en comparación con los pipelines centrados únicamente en la precisión.
*   **Datos Sintéticos:** Los datos sintéticos constituyen aproximadamente el 13% de la mezcla de entrenamiento final en todas las etapas de pre-entrenamiento. Se utilizan para complementar los datos web naturales en dimensiones difíciles de controlar, remodelando el contenido en varios formatos (Q&A, listas estructuradas, diálogos) para regularizar la presentación de la información.
*   **Aprendizaje por Refuerzo (RL) de Agente Asíncrono On-Policy:** Laguna XS.2 se beneficia de un esquema de RL de agente asíncrono on-policy, lo que mejora su capacidad para manejar tareas de horizonte largo y codificación agentic.
*   **Arnés de Agente (Agent Harness):** Poolside utiliza un servidor Agent Client Protocol (ACP) como arnés de agente. Este mismo arnés se utiliza tanto para el entrenamiento de RL del agente como para la evaluación, cerrando la brecha entre el modelo y el agente.
*   **Ecosistema de Productos:** Laguna XS.2 se integra con productos como `pool`, un agente de codificación basado en terminal, y `Shimmer`, un entorno de desarrollo en la nube para iterar en aplicaciones web, APIs y CLIs.

## 4. Lecciones para el Monstruo

De la arquitectura y el enfoque de Laguna XS.2, nuestro propio agente puede extraer lecciones valiosas:

*   **Priorizar la Codificación Agentic sobre Tool Calling:** La capacidad de escribir y ejecutar código es fundamental para la verdadera autonomía. Nuestro agente debe evolucionar más allá de la simple llamada a herramientas predefinidas para poder componer acciones complejas y construir soluciones ad-hoc mediante la generación de código.
*   **Eficiencia a través de MoE:** La arquitectura Mixture of Experts demuestra que es posible lograr un rendimiento de nivel de frontera en tareas específicas (como la codificación) manteniendo un tamaño de modelo manejable y eficiente para la inferencia (ej. ejecutable en una sola GPU).
*   **Equilibrio entre Calidad y Diversidad en Datos:** Al curar datos de entrenamiento, no debemos descartar agresivamente los datos que no son de "máxima calidad" si eso compromete la diversidad. La diversidad es crucial para la capacidad de generalización del modelo.
*   **Integración de Datos Sintéticos:** El uso estratégico de datos sintéticos para reformatear y regularizar la información existente puede mejorar significativamente la comprensión del modelo sobre conceptos complejos desde múltiples ángulos.
*   **Unificación de Entrenamiento y Evaluación:** Utilizar el mismo "arnés de agente" (entorno de ejecución) para el entrenamiento por refuerzo y la evaluación asegura que el modelo se optimice para el entorno real en el que operará.

---
*Referencias:*
[1] Introducing Laguna XS.2 and Laguna M.1 — Poolside: https://poolside.ai/blog/introducing-laguna-xs2-m1
[2] Laguna XS.2 and M.1: A Deeper Dive — Poolside: https://poolside.ai/blog/laguna-a-deeper-dive
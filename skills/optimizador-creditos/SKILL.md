---
name: optimizador-creditos
description: Reglas obligatorias para reducir el consumo de créditos de Manus en 50-70%. Usar SIEMPRE al inicio de cualquier tarea, cuando el usuario pida ahorrar créditos, o antes de operaciones costosas (navegación web, código, tareas largas).
---

# Optimizador de Créditos (Credit Optimizer v1.0)

Este skill define las reglas obligatorias de higiene de contexto, ruteo de tareas y prevención de desperdicio de créditos. El consumo de créditos depende de la **complejidad de la tarea** y el **tamaño del contexto**. 

## 1. Principio Fundamental: API-FIRST y MCP-FIRST

Las operaciones de navegador (`browser_*`) con capturas de pantalla son el sumidero de créditos más grande debido al procesamiento multimodal.

- **NUNCA** utilices el navegador si existe una API pública, CLI o servidor MCP para la tarea.
- **SIEMPRE** consulta el skill `api-context-injector` para buscar credenciales antes de intentar interactuar con UIs.
- Si una API falla dos veces (ej. por permisos o IP), **DETENTE**. No intentes un tercer enfoque subóptimo ni pelees con el CLI. Pide al usuario que genere credenciales nuevas o te asista.

## 2. Higiene de Contexto (Context Hygiene)

El consumo de créditos crece multiplicativamente con el tamaño del contexto porque cada interacción re-procesa todo el historial.

- **One-Shot Prompting:** Consolida acciones en una sola interacción densa. Evita el ping-pong de mensajes pequeños (ej. no envíes un mensaje solo para decir "Entendido" o "Gracias").
- **Usa Archivos como Memoria:** Si tienes textos largos, código extenso o logs, **escríbelos en archivos locales** (`/home/ubuntu/...`) y quítalos de tu memoria a corto plazo. Lee los archivos solo cuando sea necesario.
- **Mantén el Prefijo Estable:** Evita inyectar marcas de tiempo variables al inicio de tus respuestas para no romper el caché de prefijos (KV-cache).

## 3. Protocolo de Fallas y Eficiencia (Efficiency Veto)

La repetición de errores es inaceptable y quema créditos rápidamente.

- **Regla de los 2 Intentos:** Si un enfoque falla dos veces seguidas, **ESTÁ PROHIBIDO** intentarlo una tercera vez con variaciones menores.
- **Investigación Obligatoria en Tiempo Real:** Al segundo fallo, debes detenerte y realizar una búsqueda web (ej. GitHub, Reddit, foros) para entender cómo la comunidad resuelve el problema hoy.
- **Deja los errores en el contexto:** No intentes "limpiar" el historial ocultando errores; el modelo aprende de ellos para no repetirlos, pero cambia de estrategia inmediatamente.

## 4. Descomposición Inteligente y Ruteo

- **Batch Processing:** Agrupa búsquedas o tareas similares. En lugar de hacer 5 búsquedas separadas, haz una búsqueda estructurada con múltiples queries.
- Tareas monolíticas y vagas consumen exceso de créditos. Antes de iniciar una tarea compleja, divídela en un plan claro usando la herramienta `plan`.
- Si la tarea es de "investigación amplia", define parámetros estrictos de parada para no consumir créditos infinitamente leyendo páginas irrelevantes.

## 5. Uso Correcto de Herramientas

- **Browser vs. MCP:** Si existe un servidor MCP para el servicio (ej. Notion, GitHub, Supabase), úsalo. El texto puro es exponencialmente más barato que el renderizado web.
- **Lectura de Documentos:** Prefiere descargar y leer PDFs o documentos vía script local (ej. Python) en lugar de visualizarlos en el navegador.

---
*Recuerda: Tu objetivo no es solo completar la tarea, sino completarla utilizando la menor cantidad de operaciones de alto costo posibles. Cada token cuenta.*

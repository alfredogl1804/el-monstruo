# Guía de Integración de APIs para el Validador AliExpress

Esta guía explica cómo las integraciones de API mejoran el análisis y qué se necesita para que funcionen.

## Tabla de Contenidos
- Resumen de APIs Integradas
- Requisitos de API Keys
- Cómo Funciona el Pipeline
- Modo de Funcionamiento Básico (Fallback)

## Resumen de APIs Integradas

La habilidad `aliexpress-mx-validator` utiliza un enfoque multi-capa para el análisis, combinando un análisis basado en reglas con inteligencia artificial y datos en tiempo real. Las APIs integradas son:

### 1. Perplexity Sonar API
- **Propósito:** Investigar la reputación del vendedor fuera de AliExpress.
- **Cómo se usa:** El script `research_seller.py` construye una consulta para buscar en internet quejas, reportes de estafa, reseñas en foros (como Reddit), o cualquier mención relevante del nombre de la tienda. Esto ayuda a descubrir problemas que no son visibles dentro de la plataforma de AliExpress.

### 2. Google Gemini / OpenAI API
- **Propósito:** Análisis avanzado de la autenticidad de las reseñas.
- **Cómo se usa:** El script `ai_review_analyzer.py` envía un lote de reseñas a la API de IA (Gemini o GPT) con un prompt diseñado para que el modelo actúe como un experto en detección de fraude. La IA analiza el lenguaje, la semántica, las fechas y los patrones para estimar el porcentaje de reseñas falsas, identificar las más confiables y detectar alertas específicas para compradores en México.

### 3. APIs de Tipo de Cambio (gratuitas)
- **Propósito:** Calcular el costo total real en pesos mexicanos (MXN).
- **Cómo se usa:** El script `convert_currency.py` se conecta a APIs públicas y gratuitas (como `exchangerate-api.com`) para obtener el tipo de cambio USD-MXN más reciente. Con este dato, calcula el costo final estimado, incluyendo el precio del producto, el envío y el ~20% de impuesto de importación a México.

## Requisitos de API Keys

Para activar las capacidades de IA, las siguientes variables de entorno deben estar configuradas en el sistema donde se ejecuta Manus:

-   `SONAR_API_KEY`: Para la investigación de reputación del vendedor con Perplexity.
-   `GEMINI_API_KEY`: Para el análisis de reseñas con Google Gemini.
-   `OPENAI_API_KEY`: Como alternativa para el análisis de reseñas con OpenAI (GPT).

Si múltiples claves están disponibles, el sistema priorizará Gemini sobre OpenAI.

## Cómo Funciona el Pipeline

El script principal `full_validation.py` orquesta todo el proceso:

1.  **Carga los datos del producto** desde el archivo `product_data.json` que tú creaste.
2.  **Ejecuta el análisis base** (`analyze_product.py`) para obtener una puntuación de riesgo inicial.
3.  **Llama al conversor de moneda** (`convert_currency.py`) para obtener los costos en MXN.
4.  **Verifica si `SONAR_API_KEY` existe.** Si es así, ejecuta la investigación del vendedor (`research_seller.py`).
5.  **Verifica si `GEMINI_API_KEY` u `OPENAI_API_KEY` existen.** Si es así, ejecuta el análisis de reseñas con IA (`ai_review_analyzer.py`).
6.  **Consolida todos los resultados** (análisis base, costos en MXN, investigación del vendedor y análisis de IA de reseñas) en un único y completo reporte en formato Markdown.

## Modo de Funcionamiento Básico (Fallback)

Si **ninguna** de las API keys de IA (`SONAR_API_KEY`, `GEMINI_API_KEY`, `OPENAI_API_KEY`) está disponible, el pipeline se ejecutará en un modo de "fallback" o básico:

-   No se realizará la investigación de reputación del vendedor en internet.
-   No se realizará el análisis de reseñas con IA.
-   El reporte final se basará únicamente en el **análisis por reglas** del script `analyze_product.py` y la **conversión de moneda**.

Este modo sigue siendo muy útil y proporciona una validación sólida, pero carece de la profundidad y el contexto adicional que aporta la inteligencia artificial.

---
name: aliexpress-mx-validator
description: Valida la seguridad de una compra en AliExpress para envíos a México usando un análisis multi-capa con IA. Úsalo cuando un usuario pida verificar un producto de AliExpress, analizar un vendedor, o determinar si una compra es segura, específicamente para México.
---

# Validador de Compras AliExpress para México (Versión Mejorada con IA)

Este skill te guía para realizar un análisis de validación exhaustivo de un producto de AliExpress, determinando si es una compra segura para un destinatario en México. Esta versión mejorada integra APIs externas para un análisis más profundo y preciso.

El proceso se centra en ejecutar un único pipeline que orquesta múltiples análisis: datos del producto, reputación del vendedor en internet, análisis de reseñas con IA y conversión de moneda en tiempo real.

## Flujo de Trabajo Principal

1.  **Obtener URL del producto:** Pide al usuario el enlace completo del producto de AliExpress que desea validar.

2.  **Extraer datos del producto:** Usa el navegador para visitar la URL. Extrae toda la información necesaria siguiendo la guía en `references/data_extraction_guide.md`. Presta especial atención a los datos del vendedor, del producto y del envío a México.

3.  **Guardar datos en JSON:** Crea un archivo `product_data.json` y llénalo con los datos extraídos. Puedes usar `templates/product_data_template.json` como base. Si extraes una lista detallada de reseñas, guárdala en `reviews_data.json`.

4.  **Ejecutar el Pipeline de Validación Completa:** Este es el paso principal. El script `full_validation.py` se encargará de todo.
    -   Si existe un archivo `reviews_data.json`, pásalo como segundo argumento.

    ```bash
    # Uso básico
    python /home/ubuntu/skills/aliexpress-mx-validator/scripts/full_validation.py product_data.json

    # Con archivo de reseñas detallado
    python /home/ubuntu/skills/aliexpress-mx-validator/scripts/full_validation.py product_data.json reviews_data.json
    ```

5.  **Entregar el Reporte Completo:** El script generará un reporte final en formato Markdown (`product_data_full_report.md`). Este reporte consolida todos los hallazgos. Revísalo y entrégalo al usuario como un archivo adjunto.

## Capacidades de Análisis (Integraciones API)

El pipeline de validación utiliza las siguientes capacidades, activadas si las API keys correspondientes están disponibles en el entorno:

-   **Análisis de Reputación del Vendedor (Perplexity Sonar):**
    -   **Script:** `research_seller.py`
    -   **Requiere:** `SONAR_API_KEY`
    -   **Función:** Busca en internet (Reddit, foros, noticias) quejas, estafas o reseñas externas sobre el vendedor para evaluar su reputación fuera de AliExpress.

-   **Análisis de Reseñas con IA (Gemini/OpenAI):**
    -   **Script:** `ai_review_analyzer.py`
    -   **Requiere:** `GEMINI_API_KEY` o `OPENAI_API_KEY`
    -   **Función:** Analiza el texto de las reseñas para detectar patrones sutiles de reseñas falsas, evaluar el sentimiento real y encontrar las reseñas más confiables y las más sospechosas.

-   **Conversión de Moneda en Tiempo Real:**
    -   **Script:** `convert_currency.py`
    -   **Requiere:** Acceso a internet (usa APIs gratuitas).
    -   **Función:** Obtiene el tipo de cambio USD-MXN más reciente y calcula el costo total estimado real en pesos mexicanos, incluyendo el impuesto de importación.

Si no se proporcionan las API keys, el pipeline funcionará en un **modo básico**, utilizando únicamente el análisis basado en reglas (`analyze_product.py`), que sigue siendo efectivo pero menos potente.

## Referencias Clave

-   **`references/api_integration_guide.md`**: (NUEVO) Explica cómo funcionan las integraciones de API y qué se necesita para activarlas.
-   **`references/validation_criteria.md`**: Contiene los umbrales numéricos (ej. % de feedback) y las señales de alerta que usan los scripts base.
-   **`references/data_extraction_guide.md`**: Detalla qué información necesitas extraer de la página de AliExpress y cómo estructurarla en JSON.

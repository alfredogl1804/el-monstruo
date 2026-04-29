# Guía de Extracción de Datos de AliExpress

## Tabla de Contenidos
- Datos a Extraer de la Página del Producto
- Datos a Extraer de la Página del Vendedor
- Datos a Extraer de las Reseñas
- Formato JSON de Datos del Producto
- Formato JSON de Reseñas

## Datos a Extraer de la Página del Producto

Al navegar a un producto de AliExpress, extraer:

1. **Nombre del producto** — título completo del listado
2. **Precio** — precio actual en USD (o MXN, convertir)
3. **Precio original** — si hay descuento, el precio tachado
4. **Método de envío a México** — seleccionar México como destino
5. **Costo de envío** — costo mostrado para México
6. **Tiempo estimado de entrega** — días estimados
7. **Rastreo disponible** — si el método incluye tracking
8. **Número de órdenes** — "X sold" o "X orders"
9. **Calificación del producto** — estrellas promedio
10. **Número de reseñas** — total de reviews
11. **Descripción** — buscar palabras clave sospechosas

### Palabras clave sospechosas en descripción
Buscar: "replica", "imitation", "copy", "style", "like", "similar to", "not original", "toy", "model", "for display"

## Datos a Extraer de la Página del Vendedor

Hacer clic en el nombre de la tienda para acceder a su perfil:

1. **Nombre de la tienda**
2. **Fecha de apertura** — calcular antigüedad
3. **Feedback positivo %** — porcentaje mostrado
4. **Seguidores** — número de followers
5. **Rating detallado:**
   - Producto como se describe (1-5)
   - Comunicación (1-5)
   - Velocidad de envío (1-5)
6. **Categorías de productos** — verificar si son coherentes
7. **Sellos/badges** — "Top Brand", "AliExpress Choice", etc.

## Datos a Extraer de las Reseñas

Navegar a la sección de reseñas del producto:

1. **Filtrar por "All Reviews"** para ver todas
2. **Para cada reseña relevante extraer:**
   - Calificación (1-5 estrellas)
   - Texto del comentario
   - Si incluye foto(s)
   - País del comprador (si visible)
   - Fecha de la reseña
3. **Contar:**
   - Total de reseñas
   - Reseñas con fotos
   - Distribución de calificaciones
4. **Buscar reseñas de compradores mexicanos** (filtrar por país si es posible)
5. **Leer reseñas de 1-3 estrellas** — suelen ser las más honestas

## Formato JSON de Datos del Producto

Guardar los datos extraídos en este formato para usar con `analyze_product.py`:

```json
{
  "product_url": "https://www.aliexpress.com/item/...",
  "product_name": "Nombre completo del producto",
  "product_price_usd": 25.99,
  "original_price_usd": 45.99,
  "shipping_method": "AliExpress Standard Shipping",
  "shipping_cost_usd": 3.50,
  "estimated_delivery_days": 25,
  "has_tracking": true,
  "includes_import_tax": true,
  "store_name": "Nombre de la Tienda",
  "store_age_years": 4.5,
  "seller_positive_feedback_pct": 96.5,
  "store_followers": 5200,
  "total_orders": 1500,
  "rating_item_as_described": 4.6,
  "rating_communication": 4.7,
  "rating_shipping_speed": 4.5,
  "total_reviews": 350,
  "reviews_with_photos": 85,
  "avg_review_rating": 4.6,
  "description_red_flags": [],
  "sells_unrelated_categories": false,
  "has_brand_badge": false,
  "sample_real_reviews": [
    {
      "rating": 4,
      "text": "Llegó en 20 días a CDMX, buena calidad pero talla un poco grande",
      "has_photo": true,
      "country": "MX"
    }
  ],
  "suspicious_review_patterns": []
}
```

## Formato JSON de Reseñas

Para análisis detallado con `analyze_reviews.py`:

```json
[
  {
    "rating": 5,
    "text": "Great quality, arrived in 3 weeks to Mexico City",
    "date": "2025-12-15",
    "has_photo": true,
    "buyer_country": "MX",
    "text_length": 52
  },
  {
    "rating": 4,
    "text": "Good but smaller than expected",
    "date": "2025-12-10",
    "has_photo": false,
    "buyer_country": "US",
    "text_length": 30
  }
]
```

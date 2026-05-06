# RESUMEN TÉCNICO: CORRECCIÓN DE VISTA AÉREA — COMPLEJO DEPORTIVO KUKULCÁN

## 1. DESCRIPCIÓN EXACTA DEL PROBLEMA

La vista aérea generada (03_VISTA_AEREA_FINAL.png y todas sus variantes) tiene el edificio MAL UBICADO. El error se repitió en 7 intentos.

Dónde DEBERÍA estar el edificio:
Según el plano de conjunto de Erick Arellano (IMG_9161.PNG), el edificio de 31.2m × 10.6m está en la ESQUINA NORESTE del Estadio de Béisbol Kukulcán (el Parque de Béisbol, NO el Poliforum Zamná). En la imagen de Erick se ve un rectángulo rosado/rojo dentro de un CÍRCULO ROJO, ubicado en la zona SUPERIOR DERECHA de la imagen satelital del estadio. Está FUERA de las gradas, en un terreno abierto al noreste, pero DENTRO del perímetro del complejo deportivo (marcado con línea roja).

Dónde quedó en mis intentos:

v1-v3: Cerca del Poliforum Zamná (arena circular) — COMPLETAMENTE MAL, ese es otro edificio

v4: Zona central del complejo, entre el Complejo Deportivo y el Parque de Béisbol — MAL

v5: Zona sureste del estadio de béisbol — CERCA pero no exacto, debería ser NORESTE

El problema de fondo: Confundí el Poliforum Zamná (arena circular al este) con el Estadio de Béisbol Kukulcán (forma de diamante, al sur). Son dos estructuras diferentes dentro del mismo complejo deportivo.

## 2. COORDENADAS Y REFERENCIAS CALCULADAS

Imagen de referencia: IMG_9160.PNG (Google Earth de Alfredo)

Resolución: 1320 × 2868 px

Barra de escala: 160px = 200m → 0.8 px/m

Norte: ARRIBA en la imagen

Ubicación del Estadio de Béisbol en la imagen:

Pin rojo de Google Maps: aprox (265, 2200)

El estadio ocupa aprox: x=100 a x=530, y=2000 a y=2400

La esquina NORESTE del estadio (donde va el edificio): aprox x=450-550, y=1950-2050

Edificio a escala:

31.2m × 0.8 px/m = 25 px de largo

10.6m × 0.8 px/m = ~9 px de ancho

El edificio es ~1/5 del diámetro del estadio en su lado largo

A esta escala de Google Earth (200m), el edificio es un punto MINÚSCULO

Coordenadas usadas en el último intento (v5):

x_edif = 490  # zona derecha del estadio

y_edif = 1980  # zona superior del estadio (esquina NE)

Estas coordenadas están CERCA pero necesitan validación con Grok-4 con visión.

Imagen de referencia: IMG_9161.PNG (Plano de Erick)

Muestra SOLO el estadio de béisbol con zoom

El edificio está marcado con círculo rojo en la esquina superior derecha

Tiene el perímetro del complejo deportivo en línea roja

Lista de espacios del edificio a la derecha (Nivel 1, 2, 3)

## 3. INTENTOS DE CORRECCIÓN Y POR QUÉ FALLARON

Resumen de fallas:

La IA generativa (generate_image_variation) NO logra integrar un edificio sobre foto satelital de forma natural

La composición manual con PIL funciona mejor pero requiere coordenadas EXACTAS que no logré determinar con certeza

A la escala de Google Earth (200m), el edificio es tan pequeño que no se ve

La imagen de Google Earth de Alfredo tiene baja resolución y tiene el pin rojo de Google Maps encima

## 4. PROMPTS QUE MEJOR FUNCIONARON

Para renders exteriores del edificio (estos SÍ funcionaron bien):

Transform this basic 3D architectural model into a stunning, ultra-photorealistic

architectural visualization of a modern 3-story sports dormitory complex in Merida,

Yucatan, Mexico. The building should feature: exposed concrete walls with warm gray

tones, horizontal wooden louvers (celosías) on the facade, large floor-to-ceiling

windows with dark aluminum frames, a flat roof with mechanical equipment. Tropical

landscaping with royal palms, native Yucatan vegetation. Young baseball athletes

walking with equipment. The Kukulcan baseball stadium visible in the background.

Golden hour lighting, dramatic sky with cumulus clouds. Shot from a 3/4 perspective

angle at eye level. Architectural photography style, 85mm lens, shallow depth of

field. Quality: award-winning architectural visualization, ArchDaily featured project.

Para la vista aérea (NINGUNO funcionó bien):
El mejor intento fue la composición manual con PIL (v5), no un prompt de IA.

## 5. MÉTODO RECOMENDADO PARA LA CORRECCIÓN FINAL

RECOMENDACIÓN: Enfoque en 3 pasos

### Paso 1: Consultar a Grok-4 con visión

Enviarle las 3 imágenes en base64 (IMG_9161 de Erick, IMG_9160 de Google Earth, y el último intento fallido) y pedirle:

Que identifique la ubicación EXACTA del edificio en IMG_9161

Que mapee esa ubicación a coordenadas en pixeles sobre IMG_9160

Que diga exactamente qué está mal en el intento fallido

# API: POST https://api.x.ai/v1/chat/completions

# model: grok-4-0709

# Enviar 3 imágenes como image_url con base64

# Prompt: "Analiza estas 3 imágenes. La primera es el plano oficial que muestra

# la ubicación correcta del edificio (círculo rojo). La segunda es Google Earth.

# La tercera es mi intento de composición. ¿Dónde exactamente en la imagen de

# Google Earth (coordenadas en pixeles, imagen de 1320x2868) debería estar el

# edificio de 25x9 pixeles?"

### Paso 2: Buscar imagen satelital de mayor resolución

La imagen de Google Earth de Alfredo (IMG_9160) tiene baja resolución y el pin rojo de Google Maps estorba. Opciones:

Buscar en Google Earth Pro una captura sin pins a mayor resolución

Usar la API de Google Static Maps o Mapbox para obtener imagen satelital limpia del estadio

Recortar solo la zona del estadio de béisbol para mayor detalle

### Paso 3: Composición final con PIL

Una vez con coordenadas validadas por Grok-4 e imagen de mayor resolución:

Componer el techo del edificio (rectángulo gris 31.2m × 10.6m a escala)

Agregar sombra sutil, ruido de textura para matching

Versión limpia + versión anotada con etiqueta profesional

Versión zoom al estadio (3x) para la presentación

NO usar generate_image_variation para esto — la IA generativa no logra integrar edificios sobre fotos satelitales de forma natural. La composición manual con PIL es superior para este caso.

### Alternativa: Doble entrega

Si la composición sobre satelital sigue sin convencer:

Usar el plano de Erick (IMG_9161) mejorado/limpiado como "ubicación del proyecto"

Usar los renders exteriores del edificio (hero shot, nocturno) como "visualización del proyecto"

No forzar una vista aérea que se vea falsa

## ARCHIVOS DE REFERENCIA NECESARIOS

El nuevo hilo necesita que Alfredo suba:

IMG_9161.PNG — Plano de conjunto de Erick (ubicación exacta del edificio)

IMG_9160.PNG — Google Earth (contexto urbano)

2026.02.05complejodedormitorioskukulcan(1).pdf — PDF original de Erick con todas las medidas

Los renders finales aprobados (para mantener consistencia visual)



| Intento | Método | Resultado | Por qué falló |

| v1 | generate_image (IA pura, texto) | Imagen inventada, no parece real | IA inventó todo, no usó imagen satelital real |

| v2 | generate_image_variation (img2img) sobre imagen satelital | Edificio "pegado" como render sobre foto | Estilo del edificio no coincide con textura satelital. Además ubicado cerca del Poliforum, no del estadio |

| v3 | generate_image_variation con prompt más agresivo | Igual, render pegado | Mismo problema, la IA no logra integrar naturalmente |

| v4 | Python PIL composición manual sobre Google Earth (IMG_9160) | Techo gris integrado pero en zona CENTRAL del complejo | Coordenadas incorrectas — puse el edificio entre los dos estadios en vez de en la esquina NE del de béisbol |

| v5 | Python PIL composición corregida, zoom al estadio | Edificio en zona del estadio pero posición imprecisa | Coordenadas más cercanas (x=490, y=1980) pero sin validación visual precisa. Además la imagen tiene el pin rojo de Google Maps tapando parte de la vista |

| v5-anotada | Python PIL sobre Google Earth completo con etiqueta | Anotación visible pero edificio casi invisible | A escala 200m, 25px es microscópico. Funciona como contexto urbano pero no como render de presentación |

| v5-zoom | Recorte 3x del estadio con anotación | Mejor pero pixelado | Imagen base de baja resolución (684×848), al hacer zoom 3x se pixela |


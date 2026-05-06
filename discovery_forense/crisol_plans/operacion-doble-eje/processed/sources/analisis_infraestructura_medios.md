# Análisis de Infraestructura Digital de Medios Anónimos

## Fecha: 24 febrero 2026

## Resumen Comparativo

| Medio | Dominio | IP | Servidor | CMS | Tema WP | Hosting |
|-------|---------|-----|----------|-----|---------|---------|
| El Chismógrafo | elchismografoenlared.com | 162.215.254.164 | Apache | N/D (406 error) | N/D | WebHostBox (cp-34.webhostbox.net) |
| Formal Prisión | formalprision.com | 164.90.157.166 | nginx/1.18.0 (Ubuntu) | WordPress 6.8.3 | royale-news | DigitalOcean |
| El Principal | elprincipal.com.mx | 195.35.60.147 | hcdn | N/D | N/D | Hostinger CDN |
| Grillo de Yucatán | grillodeyucatan.com | 167.99.99.230 | nginx/1.26.0 (Ubuntu) | WordPress 6.8.3 | Newspaper2 | DigitalOcean |

## Hallazgos Clave

### 1. Formal Prisión (formalprision.com)
La OG description del sitio lo define como **"Revista policiaca"**, lo cual es consistente con su contenido de nota roja. Utiliza WordPress 6.8.3 con el tema gratuito "royale-news" de Themebeez, alojado en un VPS de DigitalOcean (IP 164.90.157.166). No se encontraron Google Analytics IDs reales (los patrones G-20260222 y G-20260223 resultaron ser nombres de archivos de imagen con formato de fecha). No tiene Facebook Pixel, ni correos electrónicos, ni números de teléfono visibles en el código fuente. El footer solo muestra el crédito del tema. La ausencia total de información de contacto en el sitio web contrasta con la información disponible en su página de Facebook.

### 2. El Chismógrafo (elchismografoenlared.com)
El servidor devuelve un error 406 (Not Acceptable) al acceder con User-Agent genérico, lo que sugiere protección anti-scraping. Está alojado en WebHostBox (shared hosting), un proveedor de hosting económico. La información de contacto se encontró exclusivamente en Facebook: teléfono 999 408 7480 (Mérida) y correo marthazamcaceres@gmail.com. Esta persona, Martha Zam Cáceres, es la administradora registrada de la página de Facebook.

### 3. Grillo de Yucatán (grillodeyucatan.com)
Usa WordPress 6.8.3 con el tema premium "Newspaper2" y plugins de tagDiv (td-standard-pack, td-cloud-library, td-composer). Alojado en DigitalOcean (IP 167.99.99.230). Comparte el mismo proveedor de hosting (DigitalOcean) que Formal Prisión, aunque en IPs diferentes.

### 4. El Principal (elprincipal.com.mx)
Usa Hostinger CDN (hcdn). No se detectó CMS ni tema WordPress en la página principal.

## Análisis de Conexiones de Infraestructura

### Hosting compartido (DigitalOcean)
Tanto Formal Prisión como Grillo de Yucatán están alojados en DigitalOcean, aunque en diferentes IPs. Esto podría ser coincidencia (DigitalOcean es un proveedor popular) o indicar que la misma persona administra ambos VPS.

### Versión WordPress idéntica
Formal Prisión y Grillo de Yucatán usan exactamente la misma versión de WordPress (6.8.3), lo que sugiere mantenimiento simultáneo o reciente.

### Anonimato deliberado
Formal Prisión no tiene absolutamente ninguna información de contacto en su sitio web: ni correo, ni teléfono, ni redes sociales, ni nombre de autor. Solo la OG description "Revista policiaca" y el tema gratuito royale-news.

## Dominios que NO resuelven
Los siguientes dominios no tienen registros DNS activos:
- formalprisionnoticias.com/.mx/.net/.org
- dulcepatrianoticias.com/.mx
- grillodeyucatan.com.mx

## Persona identificada: Martha Zam Cáceres
Administradora de la página de Facebook de El Chismógrafo en la Red. Correo: marthazamcaceres@gmail.com. Teléfono: 999 408 7480 (Mérida). Requiere investigación adicional para determinar si es operadora real o testaferro.

## Formal Prisión - Página de Facebook (@FormalPrision)

| Campo | Valor |
|-------|-------|
| URL | https://www.facebook.com/FormalPrision |
| Seguidores | 41,000 |
| Seguidos | 20 |
| Categoría | Medio de comunicación/noticias |
| Descripción | "Noticias" |
| Ubicación | Mérida Centro |
| Contacto | Solo Messenger (sin teléfono, sin email, sin sitio web en FB) |
| Estado | Activo (indicador verde) |

### Seguidores notables visibles en la barra
Los siguientes perfiles aparecen como seguidores/interacciones recientes en la barra de la página:
- **Gabriel Baltazar Centeno Canto**
- **Alejandro Segura Gongora**
- **Ricardo Castro** (¿el mismo Ricardo Castro de CONADE?)
- **Javier Segura**
- **LJ Valle**
- **José Manuel Pech Quintal**
- **Josue Chacon Gamboa**
- **Yaneli Vivas**

**NOTA IMPORTANTE:** Ricardo Castro aparece como seguidor/interactuante de Formal Prisión. Si es el mismo Ricardo Castro investigado, esto es significativo.

### Comparación con El Chismógrafo

| Aspecto | El Chismógrafo | Formal Prisión |
|---------|---------------|----------------|
| Seguidores | 19,000 | 41,000 |
| Teléfono | 999 408 7480 | No |
| Email | marthazamcaceres@gmail.com | No |
| Sitio web | elchismografoenlared.com | formalprision.com (no listado en FB) |
| Anonimato | Parcial | Total |
| WhatsApp | Sí (botón) | No |

Formal Prisión mantiene un anonimato mucho más estricto que El Chismógrafo. No hay absolutamente ninguna información de contacto más allá de Messenger.

## Formal Prisión - Sitio Web (formalprision.com)

### Autores identificados en el sitio:
1. **admin** — autor de artículos más antiguos (2015-2025)
2. **Jose Duque** — autor de artículos recientes (2024-2026)

### Estructura del sitio:
El sitio tiene secciones de: Inicio, Política y Gobierno, Del Mundo, Yucatán, Nacionales, Tocho Morocho, Anúnciate.

Categorías incluyen: Asesinos, Breves, Cafres, Cultura, De la grilla, Del Mundo, Delincuentes Vip, Deportes, Espectáculos, Incendios, Mérida, Morgue, Nacionales, Narcos, Noti Pueblitos, Noticias Políticas, Pecadoras, Política y Gobierno, Ratas, Rescates, Violines, Yo no fui, Yucatán.

### Búsqueda de "Ricardo Castro":
No se encontraron artículos específicos sobre Ricardo Castro (el investigado). Los resultados son sobre Mario Castro Alcocer (magistrado) y otros temas políticos generales.

### Publicidad visible:
Se muestra publicidad del Ayuntamiento de Mérida (descuentos de pago predial), lo que sugiere que el medio tiene relación comercial con el gobierno municipal.

### Autor "Jose Duque":
Este nombre aparece como autor de artículos recientes. Necesita investigación para determinar si es un nombre real o pseudónimo.

### Búsqueda de "CONADE" en Formal Prisión:
Los resultados son exclusivamente noticias deportivas sobre la Olimpiada/Paralimpiada Nacional CONADE. No se encontraron artículos de ataque o difamación contra la CONADE como institución ni contra Ana Gabriela Guevara. Solo un artículo de 2023 menciona un juez que ordenó a CONADE devolver becas a natación artística, pero es una nota informativa, no un ataque.

**CONCLUSIÓN PARCIAL:** El sitio web formalprision.com no parece ser el vehículo principal de ataques contra CONADE. Los ataques probablemente se canalizan a través de la página de Facebook de Formal Prisión, no del sitio web.

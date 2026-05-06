# Respuesta de Gemini 3 Pro — Plan de Investigación 13 Objetivos

Aquí tienes el Plan de Investigación Operación "Doble Eje" - Fase Masiva, diseñado para ejecutar una auditoría forense digital irrefutable sobre los objetivos y la infraestructura de Carlos Mena Baduy.

Este plan integra tus 35 herramientas en un flujo de trabajo de 5 fases.

# PLAN MAESTRO DE INVESTIGACIÓN "DOBLE EJE"

## FASE 1: COSECHA MASIVA DE EVIDENCIA (DATA MINING)

Objetivo: Extraer cada URL, mención y metadato de los 13 objetivos en la red de 22 dominios conocidos + Internet abierta.

### Paso 1.1: Scraping Quirúrgico con Apify & Google Dorking

Herramienta: Apify (Google Search Scraper) + Perplexity Sonar
Acción: Ejecutar búsquedas booleanas avanzadas para cada uno de los 13 objetivos contra los 22 dominios.

Configuración del Query (Ejemplo para Wendy Méndez):

site:solyucatan.mx OR site:elgrillodeyucatan.com OR site:laopiniondemexico.mx ... ("Wendy Méndez" OR "Wendy Méndez Naal" OR "Esposa del Gobernador")

Para Rommel Pacheco (Ataque Indirecto):

("Lylo Fa" OR "Armin Lizama" OR "Habanero" OR "Rommel Pacheco") AND (rob* OR fraud* OR engañ* OR simulaci* OR traid*) site:[LISTA_DOMINIOS]

Ejecución Técnica:

Generar script Python que construya los queries combinando TARGETS x DOMAINS.

Enviar a Apify para extraer: URL, Título, Fecha, Snippet, Autor.

Perplexity Sonar-Deep-Research: Usar para buscar contexto que no esté indexado, preguntando: "Busca reportajes negativos sobre [OBJETIVO] en solyucatan.mx y medios afiliados entre 2023-2024".

### Paso 1.2: Recuperación Histórica y Caché

Herramienta: Wayback Machine API + BrandMentions API
Razón: Carlos Mena podría borrar notas tras ser descubierto.
Acción:

BrandMentions: Consultar endpoint /mentions para cada objetivo. Filtrar por sentiment: negative.

Wayback Machine: Para cada URL encontrada en el paso 1.1 que dé error 404, consultar la CDX API para ver si existe un snapshot.

### Paso 1.3: Ingesta en PostgreSQL

Herramienta: Supabase (PostgreSQL)
Schema SQL sugerido:

CREATE TABLE findings (

id SERIAL PRIMARY KEY,

target_name VARCHAR(100),

url TEXT UNIQUE,

domain VARCHAR(100),

publish_date TIMESTAMP,

content_text TEXT,

author_signature VARCHAR(100),

sentiment_score FLOAT, -- Llenado en Fase 2

attack_vector VARCHAR(50), -- 'CORRUPCION', 'PERSONAL', 'TRAICION'

evidence_hash VARCHAR(64) -- SHA256

);

## FASE 2: ANÁLISIS DE NARRATIVA Y SENTIMIENTO (NLP)

Objetivo: Confirmar científicamente que es un "ataque" y no periodismo neutral, y detectar la "pluma" de Mena.

### Paso 2.1: Clasificación de Toxicidad

Herramienta: AWS Comprehend
Acción: Pasar el content_text de cada nota por el modelo de análisis de sentimiento en español.
Parámetros:

Si Sentiment == NEGATIVE y Confidence > 0.85 -> Marcar como ATAQUE CONFIRMADO.

Si detecta entidades (Entities) como "Rata", "Corrupto", "Ladrón" cerca del nombre del objetivo -> Marcar como DIFAMACIÓN.

### Paso 2.2: Detección de "La Voz del Amo" (Stylometry)

Herramienta: OpenAI GPT-4 + scikit-learn (Cosine Similarity)
Lógica: Carlos Mena usa frases específicas (ej. "Te dije que escribas la palabra rata").

Entrenamiento: Crear un "Vector Mena" basado en los artículos ya confirmados como ataques (los de Wendy Méndez y Dafne López).

Comparación: Usar scikit-learn para calcular la similitud de coseno entre los nuevos artículos encontrados y el "Vector Mena".

Prompt GPT-4: "Analiza este texto. ¿El estilo, adjetivos y estructura gramatical coinciden con este texto de referencia (artículo confirmado de Mena)? Responde con % de probabilidad."

## FASE 3: MAPEO DE INFRAESTRUCTURA Y NUEVOS NODOS

Objetivo: Encontrar los medios de la red que aún no conocemos (más allá de los 22).

### Paso 3.1: Pivoteo de DNS y Certificados

Herramienta: crt.sh + ViewDNS.info + SecurityTrails (cuidando quota)
Acción:

Buscar la IP 35.209.193.228 (Cluster original) y 167.99.99.230 (Cluster Grillo) en ViewDNS.info (Reverse IP).

Extraer todos los dominios alojados ahí.

crt.sh: Buscar certificados SSL que compartan "Organization Name" o email de registro.

### Paso 3.2: Fingerprinting de WordPress y Analytics

Herramienta: BuiltWith (vía web o API si hay saldo) + Código Fuente Manual
Acción:

Descargar el HTML de los 22 sitios.

Buscar patrones de ID:

Google Analytics/Tag Manager: UA-XXXXXX, G-XXXXXX. Si solyucatan y un sitio desconocido noticiasocultas.com comparten el mismo ID UA-12345, es la misma red.

AdSense ID: pub-XXXXXXXXXXXXXXXX.

WordPress REST API: Consultar /wp-json/wp/v2/users en los dominios sospechosos. Si aparece el usuario "admin" o un nombre común (ej. "redaccion_sureste") en varios sitios, es un match.

## FASE 4: ANÁLISIS DE COORDINACIÓN TEMPORAL (CONSISTENCIA)

Objetivo: Probar que no son medios independientes, sino una granja de trolls coordinada.

### Paso 4.1: Detección de "Nado Sincronizado"

Herramienta: Supabase (SQL) + Pandas/Python
Query de Coordinación:

SELECT

t1.domain as medio_A,

t2.domain as medio_B,

t1.target_name,

t1.publish_date,

EXTRACT(EPOCH FROM (t2.publish_date - t1.publish_date))/3600 as diff_horas

FROM findings t1

JOIN findings t2 ON t1.target_name = t2.target_name

WHERE t1.id < t2.id

AND t1.domain != t2.domain

AND ABS(EXTRACT(EPOCH FROM (t2.publish_date - t1.publish_date))) < 4 * 3600 -- Publicado con menos de 4 horas de diferencia

AND t1.sentiment_score < -0.8; -- Ambos son ataques negativos

Interpretación: Si El Grillo y La Opinión atacan a "Katia Meave" con menos de 4 horas de diferencia, es coordinación operativa.

## FASE 5: PRESERVACIÓN FORENSE Y CADENA DE CUSTODIA

Objetivo: Que la evidencia sea admisible legalmente o para exposición pública.

### Paso 5.1: Hashing y Almacenamiento Inmutable

Herramienta: AWS S3 + Python hashlib
Procedimiento Automático:

Para cada hallazgo positivo (URL de ataque):

Descargar HTML completo.

Generar captura de pantalla (screenshot) con Apify.

Calcular hash SHA-256 del archivo.

Subir a S3 bucket operacion-doble-eje/evidencia/[TARGET]/[FECHA]_[HASH].zip.

Registrar el Hash en la base de datos Golden Record.

## ORDEN DE BATALLA (EJECUCIÓN INMEDIATA)

Sigue este orden para maximizar el uso de recursos:

Día 1: Mapeo de Wendy Méndez, Dafne López y Mario Millet (Alta Prioridad).

Usa Apify exhaustivamente en los 22 dominios.

Valida los ataques con AWS Comprehend.

Esto establece tu "Línea Base de Ataque".

Día 2: Búsqueda de Rommel Pacheco (Ataque Indirecto).

Configura los queries complejos (Lylo Fa, Armin Lizama).

Usa Perplexity para entender por qué atacan a Armin (buscando nexos de negocios).

Día 3: El resto de la lista (Barrido Político).

Ejecuta el script masivo para los objetivos 4-12.

Usa BrandMentions para ver si el ataque saltó a redes sociales (Twitter/Facebook).

Día 4: Cacería de Nuevos Dominios.

Análisis forense de IPs y Analytics.

Si encuentras uno nuevo, re-ejecuta el script de búsqueda (Día 1-3) sobre ese nuevo dominio.

## COMANDOS RÁPIDOS PARA TU ENTORNO

1. Verificar IPs de la red actual (CLI):

for domain in solyucatan.mx grillodeyucatan.com laopiniondemexico.mx; do

dig +short $domain

done

2. Búsqueda rápida de Wordpress Users (si está abierto):

curl -s "https://solyucatan.mx/wp-json/wp/v2/users" | jq '.[].name'

3. Script Python básico para similitud (Snippet):

from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.metrics.pairwise import cosine_similarity

def check_plagiarism(text1, text2):

vectorizer = TfidfVectorizer()

tfidf_matrix = vectorizer.fit_transform([text1, text2])

return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

# Si el resultado > 0.7, es el mismo "boilerplate" de ataque.

Este plan utiliza tu arsenal actual al 100% y cierra el cerco sobre Mena Baduy. ¿Procedemos con la Fase 1?
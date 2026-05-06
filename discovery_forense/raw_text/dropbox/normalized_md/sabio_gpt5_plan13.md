# Respuesta de GPT-5.2 — Plan de Investigación 13 Objetivos

Puedo ayudarte a diseñar un plan OSINT/forense defensivo y de preservación de evidencia para documentar cobertura coordinada, atribución técnica de infraestructura web y análisis de patrones editoriales.
No puedo dar instrucciones para comprometer cuentas, evadir controles, doxxear personas, ni técnicas intrusivas. Me limitaré a fuentes públicas, APIs autorizadas, análisis de contenido y preservación forense.

# Plan maestro de investigación forense digital

## Objetivo

Determinar, con estándar probatorio reproducible, si la red atribuida operativamente a Carlos Mena Baduy publicó o coordinó contenido de ataque contra estas 13 personas, y si existieron medios adicionales vinculados a la red.

# 0) Principios metodológicos

## Hipótesis a probar

Para cada objetivo P:

H1. Cobertura
Existen publicaciones en uno o más medios vinculados a la red que mencionan a P.

H2. Tono de ataque
La cobertura sobre P es predominantemente de ataque / desprestigio, no meramente informativa.

H3. Coordinación
Dos o más medios de la red publicaron sobre P con proximidad temporal, similitud textual/narrativa o repetición de framing.

H4. Atribución técnica del medio
Cada dominio que publique contenido sobre P puede vincularse a la red mediante indicadores técnicos, históricos o editoriales.

H5. Cadena de custodia
Todo hallazgo queda preservado con hash, timestamp, fuente y reproducibilidad.

# 1) Arquitectura de trabajo

## 1.1 Repositorios de evidencia

Usar 3 capas:

PostgreSQL local “Golden Record”

índice maestro de artículos, dominios, evidencias, IOC, targets, clasificaciones.

Supabase remota

colaboración, dashboards, vistas de revisión humana.

AWS S3 bucket operacion-doble-eje

HTML crudo, capturas, PDFs, JSON API, exports CSV, hashes.

## 1.2 Estructura sugerida en S3

s3://operacion-doble-eje/

raw/

websites/

{domain}/

{yyyy}/{mm}/{dd}/

article_{slug}_{timestamp}.html

article_{slug}_{timestamp}.pdf

article_{slug}_{timestamp}.png

wpjson_{timestamp}.json

headers_{timestamp}.json

urlscan_{scanid}.json

wayback_cdx_{timestamp}.json

dns/

{domain}/

whois_{timestamp}.txt

crtsh_{timestamp}.json

dns_history_{timestamp}.json

viewdns_{timestamp}.html

mentions/

brandmentions/

mentionlytics/

google/

social/

facebook/

instagram/

x/

processed/

nlp/

clustering/

graphs/

reports/

custody/

evidence_manifest_{timestamp}.csv

sha256_{timestamp}.txt

## 1.3 Convención de hash

Para cada artefacto:

SHA256

fecha UTC

fuente

URL de origen

investigador/proceso

versión de parser

Comando:

sha256sum archivo > archivo.sha256

Manifest consolidado:

find . -type f ! -name "*.sha256" -exec sha256sum {} \; > sha256_manifest_$(date -u +%Y%m%dT%H%M%SZ).txt

Subida a S3:

aws s3 cp ./evidence s3://operacion-doble-eje/raw/ --recursive

aws s3 cp sha256_manifest_*.txt s3://operacion-doble-eje/custody/

# 2) Modelo de datos mínimo

## 2.1 Tablas recomendadas

Si no existen, crear:

CREATE TABLE IF NOT EXISTS targets (

id SERIAL PRIMARY KEY,

canonical_name TEXT NOT NULL,

aliases TEXT[],

role TEXT,

notes TEXT

);

CREATE TABLE IF NOT EXISTS domains (

id SERIAL PRIMARY KEY,

domain TEXT UNIQUE NOT NULL,

cluster TEXT,

status TEXT,

wordpress_detected BOOLEAN DEFAULT FALSE,

cloudflare_ns BOOLEAN DEFAULT FALSE,

registrar TEXT,

creation_date TIMESTAMP,

nameservers TEXT[],

ips INET[],

asn TEXT,

hosting_provider TEXT,

linked_score NUMERIC DEFAULT 0,

linked_reason JSONB,

first_seen TIMESTAMP DEFAULT NOW(),

last_seen TIMESTAMP DEFAULT NOW()

);

CREATE TABLE IF NOT EXISTS articles (

id BIGSERIAL PRIMARY KEY,

domain TEXT NOT NULL,

url TEXT UNIQUE NOT NULL,

title TEXT,

author TEXT,

published_at TIMESTAMP,

scraped_at TIMESTAMP DEFAULT NOW(),

html_sha256 TEXT,

text_content TEXT,

language TEXT,

wp_post_id TEXT,

source_method TEXT,

wayback_snapshot TEXT,

target_ids INT[],

mention_count INT DEFAULT 0

);

CREATE TABLE IF NOT EXISTS article_classifications (

id BIGSERIAL PRIMARY KEY,

article_id BIGINT REFERENCES articles(id),

target_id INT REFERENCES targets(id),

sentiment_label TEXT,

attack_label TEXT, -- ATAQUE_FUERTE, ATAQUE_LEVE, NEUTRAL, DEFENSA

confidence NUMERIC,

model_source TEXT,

rationale TEXT,

human_validated BOOLEAN DEFAULT FALSE,

validated_by TEXT,

validated_at TIMESTAMP

);

CREATE TABLE IF NOT EXISTS domain_iocs (

id BIGSERIAL PRIMARY KEY,

domain TEXT,

indicator_type TEXT, -- NS, IP, SPF, MX, SSL, GA_ID, AdSense, WP_THEME, CDN, WHOIS

indicator_value TEXT,

observed_at TIMESTAMP DEFAULT NOW(),

source TEXT,

confidence NUMERIC DEFAULT 0.5

);

CREATE TABLE IF NOT EXISTS coordination_events (

id BIGSERIAL PRIMARY KEY,

target_id INT REFERENCES targets(id),

narrative_key TEXT,

event_date DATE,

domains TEXT[],

urls TEXT[],

temporal_window_hours INT,

avg_text_similarity NUMERIC,

coordination_score NUMERIC,

notes TEXT

);

CREATE TABLE IF NOT EXISTS evidence_log (

id BIGSERIAL PRIMARY KEY,

artifact_path TEXT,

artifact_type TEXT,

sha256 TEXT,

source_url TEXT,

collected_at TIMESTAMP DEFAULT NOW(),

collector TEXT,

notes TEXT

);

# 3) Carga inicial de objetivos

INSERT INTO targets (canonical_name, aliases, role) VALUES

('Wendy Méndez Naal', ARRAY['Wendy Mendez Naal','Wendy Méndez'], 'Esposa del gobernador'),

('Dafne López', ARRAY['Dafne Lopez'], 'Cercana al gobernador'),

('Mario Millet', ARRAY['Mario Millet Encalada','Mario Millet'], 'Cercano al gobernador'),

('Ariadna Montiel', ARRAY['Ariadna Montiel Reyes'], 'Política federal'),

('Katia Meave', ARRAY['Katia Meave Ferniza'], 'Política'),

('Diego Cetz', ARRAY['Diego Cetz Cen'], 'Político'),

('Alejandro Ruiz', ARRAY['Alejandro Ruiz Euán','Alejandro Ruiz Euan'], 'Político'),

('Sisely Burgos', ARRAY['Sisely del Carmen Burgos Cano','Sisely Burgos Cano'], 'Política'),

('Jazmín Villanueva Moo', ARRAY['Jazmin Villanueva Moo'], 'Diputada federal'),

('Oscar Brito', ARRAY['Óscar Brito Zapata','Oscar Brito Zapata'], 'Candidato aliado'),

('Geovana Campos', ARRAY['Geovana del Carmen Campos','Geovanna Campos'], 'Política'),

('Jacinto Sosa', ARRAY['Jacinto Sosa Novelo'], 'Político'),

('Rommel Pacheco', ARRAY['Rommel Achi Pacheco Marrufo','Rommel Pacheco Marrufo'], 'Candidato principal');

# 4) Fase I — Atribución técnica de dominios conocidos

Aquí no basta “está en la lista”; hay que reconfirmar técnicamente cada dominio.

## 4.1 Dominios semilla

Los 22 que ya tienes.

## 4.2 Extracción de DNS / NS / SPF / MX / A / CNAME

Usar dig/nslookup y almacenar.

for d in solyucatan.mx solyucatan.com laopiniondemexico.mx noticiasmerida.com.mx \

elprincipal.com.mx formalprision.com notisureste.com suresteinforma.com \

revistayucatan.com a7.com.mx notirasa.com elchismografoenlared.com \

notiredmerida.com elmomentoyu.com larevistapeninsular.com grillodeyucatan.com \

grilloporteno.com consultamonterrey.mx visionpeninsular.com digital-editorial.com

do

mkdir -p dns/$d

{

echo "### A"; dig +short A $d

echo "### AAAA"; dig +short AAAA $d

echo "### MX"; dig +short MX $d

echo "### NS"; dig +short NS $d

echo "### TXT"; dig +short TXT $d

echo "### CNAME"; dig +short CNAME $d

} > dns/$d/dig_$(date -u +%Y%m%dT%H%M%SZ).txt

done

### Parsear a SQL

Indicadores:

nameservers Cloudflare comunes (kim.ns.cloudflare.com, kip.ns.cloudflare.com)

IPs repetidas

SPF repetido (35.209.193.228)

MX compartidos

hosting compartido

Google-site-verification repetido

DKIM selector común

## 4.3 crt.sh

Objetivo:

encontrar subdominios

detectar certificados compartidos

descubrir staging / admin / mail / cpanel

Consulta:

curl -s "https://crt.sh/?q=%25.solyucatan.mx&output=json" > crtsh_solyucatan_mx.json

Para todos:

for d in $(cat domains.txt); do

curl -s "https://crt.sh/?q=%25.$d&output=json" > crtsh/${d}_$(date -u +%Y%m%dT%H%M%SZ).json

done

Extraer common_name, name_value, issuer_name.

## 4.4 Wayback CDX

Objetivo:

histórico de URLs

páginas borradas

autores antiguos

“quiénes somos”

páginas de contacto

cambios de branding

Ejemplo:

curl "https://web.archive.org/cdx/search/cdx?url=solyucatan.mx/*&output=json&fl=timestamp,original,statuscode,mimetype,digest&filter=statuscode:200"

Prioridad de captura:

/

/quienes-somos

/contacto

/category/*

/author/*

/tag/*

URLs de notas sobre targets

## 4.5 Urlscan

Objetivo:

tecnologías

requests de terceros

IDs compartidos (GA, GTM, AdSense, Meta Pixel)

screenshot

ASN / server

Búsquedas:

por dominio

por IP compartida

por favicon hash si aplica

Si se cuenta con API pública:

curl -s "https://urlscan.io/api/v1/search/?q=domain:solyucatan.mx"

curl -s "https://urlscan.io/api/v1/search/?q=ip:167.99.99.230"

Indicadores clave:

Google Analytics UA-* o G-*

GTM GTM-*

AdSense ca-pub-*

Meta Pixel

mismo favicon hash

mismos requests a assets

## 4.6 WordPress fingerprint + REST API

Para cada dominio:

curl -s https://dominio/wp-json/ | jq .

curl -s "https://dominio/wp-json/wp/v2/posts?per_page=100&page=1"

curl -s "https://dominio/wp-json/wp/v2/users?per_page=100"

curl -s "https://dominio/wp-json/wp/v2/categories?per_page=100"

curl -I https://dominio/xmlrpc.php

Qué buscar:

autores compartidos o seudónimos repetidos

categorías idénticas

slugs de tags

timezone

theme/plugin signatures

endpoints expuestos

## 4.7 ViewDNS / DNSHistory

Objetivo:

IP history

NS history

reverse IP neighbors

Guardar HTML/JSON si disponible.
Cruzar:

períodos donde varios dominios comparten IP

migraciones sincronizadas

cambios de NS en la misma ventana temporal

## 4.8 Scoring de vinculación de dominio

Puntuar cada dominio 0–100.

### Ejemplo de pesos

mismo Cloudflare NS específico: +15

misma IP histórica o activa: +20

mismo SPF/MX: +10

mismo GA/GTM/AdSense/Meta Pixel: +25

mismo theme/plugin/favicon: +10

coincidencia editorial/autores: +10

misma fecha/registrador/lote temporal: +10

SQL sugerido para tabla domains.linked_score, con linked_reason JSONB.

# 5) Fase II — Recolección masiva de contenido de los 22 dominios

## 5.1 WordPress REST first

Para medios WordPress, usar API antes de scraping HTML.

### Script base

for d in $(cat domains.txt); do

mkdir -p raw/wp/$d

for page in $(seq 1 50); do

curl -s "https://$d/wp-json/wp/v2/posts?per_page=100&page=$page&_fields=id,date,link,title,content,excerpt,author,categories,tags,slug,status,type" \

-o raw/wp/$d/posts_page_${page}.json

done

done

Si algunos usan ?rest_route=:

curl -s "https://$d/?rest_route=/wp/v2/posts&per_page=100&page=1"

## 5.2 Google Search Scraper de Apify

Úsalo para capturar contenido indexado y páginas no expuestas por WP API.

### Queries por target x dominio

Plantilla:

site:solyucatan.mx "Wendy Méndez Naal"

site:solyucatan.mx "Wendy Mendez Naal"

site:solyucatan.mx "Wendy Méndez"

Repetir con alias.
También:

site:solyucatan.mx Wendy

site:grillodeyucatan.com "Rommel Pacheco"

site:grillodeyucatan.com "Lylo Fa"

site:grillodeyucatan.com Habanero

### Apify actor

Actor: Google Search Scraper
Parámetros:

queries: lista masiva

resultsPerPage: 10

maxPagesPerQuery: 3

countryCode: mx

languageCode: es

mobileResults: false

includeUnfilteredResults: true

## 5.3 Wayback para contenido borrado

Para cada URL encontrada y cada dominio semilla:

buscar snapshots históricos

descargar HTML histórico si la nota ya no existe

CDX para target:

curl "https://web.archive.org/cdx/search/cdx?url=solyucatan.mx/*mario-millet*&output=json"

## 5.4 Scraping HTML full-fidelity

Cuando WP API no entregue contenido o exista paywall/bloqueo:

curl -L

guardar HTML

generar PDF con navegador headless si disponible

screenshot PNG

Ejemplo:

curl -L -A "Mozilla/5.0" "https://dominio/nota-slug" -o article.html

Registrar headers:

curl -I -L "https://dominio/nota-slug" -o headers.txt

## 5.5 Inserción en PostgreSQL

Parsear:

título

fecha

autor

URL

texto limpio

hash HTML

Usar psycopg2 o COPY.

# 6) Fase III — Descubrimiento de notas sobre las 13 personas

## 6.1 Diccionario de búsqueda por persona

Debes construir un alias pack por target.

Ejemplo Wendy Méndez Naal:

"Wendy Méndez Naal"

"Wendy Mendez Naal"

"Wendy Méndez"

"esposa del gobernador" AND "Wendy"

Ejemplo Rommel Pacheco:

"Rommel Pacheco"

"Rommel Pacheco Marrufo"

"Rommel"

targets indirectos asociados:

"Lylo Fa"

"Armin Lizama"

"Habanero"

"entorno de Rommel"

## 6.2 SQL full-text inicial

Si text_content ya está cargado:

SELECT a.domain, a.url, a.title, a.published_at

FROM articles a

WHERE a.text_content ILIKE '%Wendy Méndez Naal%'

OR a.text_content ILIKE '%Wendy Mendez Naal%'

OR a.title ILIKE '%Wendy Méndez%'

ORDER BY a.published_at DESC;

## 6.3 Índice FTS recomendado

ALTER TABLE articles ADD COLUMN IF NOT EXISTS tsv tsvector;

UPDATE articles SET tsv = to_tsvector('spanish', coalesce(title,'') || ' ' || coalesce(text_content,''));

CREATE INDEX IF NOT EXISTS idx_articles_tsv ON articles USING GIN(tsv);

Consulta:

SELECT domain, url, title, published_at

FROM articles

WHERE tsv @@ plainto_tsquery('spanish', 'Wendy Méndez Naal');

## 6.4 Apify Google Search cross-check

Lanzar una matriz:

13 personas × 22 dominios × alias

más términos de ataque:

corrupción

rata

desvío

escándalo

operador

aviador

mafia

fraude

Ejemplo:

site:solyucatan.mx "Dafne López" corrupción

site:solyucatan.mx "Mario Millet" escándalo

site:grillodeyucatan.com "Rommel Pacheco" operador

## 6.5 WordPress search endpoint

Muchos sitios WP permiten:

curl -s "https://dominio/wp-json/wp/v2/posts?search=Rommel%20Pacheco&per_page=100"

Automatizar para todas las personas y dominios.

# 7) Fase IV — Clasificación de tono: ataque vs neutral

Esto debe combinar reglas + NLP + revisión humana.

## 7.1 Etiquetas

ATAQUE_FUERTE

ATAQUE_LEVE

NEUTRAL

DEFENSA

## 7.2 Reglas lexicográficas iniciales

Construir un lexicón de ataque en español político local:

Ejemplos:

rata

corrupto/a

mafia

saqueo

aviador

operador oscuro

desvío

red de corrupción

escándalo

traición

imposición

simulación

cómplice

enriquecimiento

moches

delincuente

pillaje

nepotismo

Heurística:

si target aparece en título + ≥2 términos de ataque en título/excerpt ⇒ candidato ATAQUE_FUERTE

si target aparece solo en cuerpo con framing negativo ⇒ ATAQUE_LEVE

si aparece desmentido o defensa ⇒ DEFENSA

## 7.3 AWS Comprehend en español

Úsalo para sentimiento base y key phrases.

Parámetros:

idioma es

lotes por artículo o por párrafos relevantes donde aparece el target

Workflow:

extraer ventana de ±3 oraciones alrededor de cada mención

enviar a Comprehend

almacenar Sentiment, SentimentScore, entidades, key phrases

## 7.4 LLM ensemble para clasificación editorial

Usar 4 modelos para reducir sesgo:

OpenAI GPT-5.2

Claude 3 Opus

Gemini 3 Pro Preview

Grok-4

Prompt fijo:

clasifica tono respecto del target

identifica si el artículo busca desprestigiar, insinuar corrupción o daño reputacional

devolver JSON estricto

Esquema JSON:

{

"target": "Mario Millet",

"attack_label": "ATAQUE_FUERTE",

"confidence": 0.91,

"evidence_spans": [

"fragmento 1",

"fragmento 2"

],

"narrative_tags": ["corrupcion", "operador_politico", "escandalo"],

"rationale": "..."

}

Regla de consenso:

si 3/4 modelos coinciden ⇒ clasificación automática

si 2/4 o divergencia alta ⇒ cola de revisión humana

## 7.5 Scikit-learn para consistencia

Entrenar un clasificador auxiliar usando tus 24 objetivos ya clasificados y los 39,065 artículos.

Pipeline:

TF-IDF (1-2 grams)

Linear SVM / Logistic Regression

etiquetas existentes

Objetivo:

no reemplazar revisión

priorizar artículos de mayor probabilidad de ataque

Pseudo:

from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.linear_model import LogisticRegression

from sklearn.pipeline import Pipeline

# 8) Fase V — Coordinación editorial

Aquí está una de las partes más importantes.

## 8.1 Señales de coordinación

misma persona objetivo

publicaciones dentro de una ventana de 0–72 horas

misma narrativa (corrupción, traición, operador, etc.)

similitud textual alta

misma estructura de titular

replicación de foto/asset

secuencia medio A → medio B → amplificación social

## 8.2 Clustering temporal

SQL base:

SELECT

t.canonical_name,

a.domain,

a.url,

a.title,

a.published_at::date AS day

FROM articles a

JOIN article_classifications ac ON ac.article_id = a.id

JOIN targets t ON t.id = ac.target_id

WHERE ac.attack_label IN ('ATAQUE_FUERTE','ATAQUE_LEVE')

ORDER BY t.canonical_name, a.published_at;

Agrupar por target y ventanas de 72h.

## 8.3 Similaridad textual

Con scikit-learn:

TF-IDF sobre título + lead + párrafos con el target

cosine similarity entre artículos del mismo target en ventana temporal

Umbrales sugeridos:

0.80 = probable copia/reescritura

0.65–0.80 = narrativa compartida

0.50–0.65 = ángulo similar

## 8.4 Detección de “narrative key”

Generar etiquetas:

corrupción

nepotismo

traición

campaña_sucia

conflicto_interno

pareja/familia

operador_financiero

desvío_recursos

Puede salir de:

LLM tagging

top keywords Mentionlytics / BrandMentions

NER + key phrases AWS Comprehend

## 8.5 Grafo de coordinación con networkx

Nodos:

dominios

targets

narrativas

autores

IPs/NS/shared IDs

Aristas:

PUBLISHED_ATTACK_ON

SHARED_IP

SHARED_NS

HIGH_SIMILARITY

SAME_DAY_ATTACK

USES_SAME_NARRATIVE

Pseudo:

import networkx as nx

G = nx.MultiDiGraph()

Métricas:

degree centrality de dominio

betweenness

communities

edge weights por cantidad de coincidencias

## 8.6 Coordination Score

Propuesta:

coordination_score =

0.25*(num_domains_same_72h_normalized) +

0.20*(avg_text_similarity) +

0.15*(shared_narrative_score) +

0.15*(shared_asset_score) +

0.15*(same_author_or_alias_score) +

0.10*(same_infra_linkage_score)

Clasificación:

0.75 = coordinación fuerte

0.55–0.75 = coordinación probable

<0.55 = coordinación débil/aislada

# 9) Fase VI — Descubrimiento de medios nuevos

Esto debe hacerse por varias rutas en paralelo.

## 9.1 Reverse infrastructure hunting

Partir de IOCs ya conocidos:

IPs: 167.99.99.230, 35.209.193.228 SPF relacionada

NS: kim.ns.cloudflare.com, kip.ns.cloudflare.com

GTM/GA/AdSense IDs

favicon hash

themes/plugins

### Método

Urlscan search por IP

ViewDNS reverse IP

DNSHistory / históricos

crt.sh por certificados relacionados

búsqueda por mismos assets en HTML

## 9.2 Patrones editoriales / frases firma

Si tienes “firmas técnicas” en Golden Record, explotarlas.
Ejemplos:

cierre de nota repetido

disclaimers

estructura H1

muletillas (“trascendió”, “fuentes confiables”, etc.)

formato de slug

taxonomías repetidas

nombres de categorías

Usa TF-IDF de frases distintivas y busca en Google:

"frase distintiva exacta" site:*.mx

Con Apify Google Search Scraper.

## 9.3 BrandMentions y Mentionlytics

Objetivo:

detectar sitios que mencionan reiteradamente a los mismos targets con el mismo framing

detectar amplificadores

### BrandMentions

Endpoint base provisto: https://api.brandmentions.com/v1/mentions

Consultas:

keywords por target

keywords por narrativas y marcas de la red

filtrar source_type=web

Ejemplo conceptual:

"Wendy Méndez Naal" OR "Wendy Mendez Naal"

"Rommel Pacheco" AND (corrupción OR escándalo OR operador)

Guardar:

source URL

source domain

snippet

timestamp

sentiment si lo entrega

### Mentionlytics

Endpoints:

/api/mentions

/api/aggregation

/api/top-keywords

/api/mentioners

Usar para:

top domains por target

burst por fecha

keywords colaterales

mentioners recurrentes

## 9.4 Google dorks

Matrices:

"Rommel Pacheco" "Lylo Fa"

"Te dije que escribas la palabra rata"

site:*.mx "Mario Millet" "corrupción"

site:*.com.mx "Dafne López"

Buscar:

medios espejo

blogs satélite

agregadores

## 9.5 Subdominios y micrositios

Con crt.sh:

*.formalprision.com

*.digital-editorial.com

*.visionpeninsular.com

Prioridad:

subdominios de publicación

staging con contenido indexado

directorios /category/politica, /tag/

## 9.6 Huella WordPress compartida

Extraer:

generator

theme path /wp-content/themes/...

plugin paths

media upload patterns /wp-content/uploads/YYYY/MM/

autores expuestos por REST

Si 3+ de estos coinciden con red conocida, elevar para revisión.

# 10) Fase VII — Análisis social y amplificación

Solo sobre fuentes públicas y actores de Apify.

## 10.1 Facebook / Instagram vía Apify

Para cada dominio, target y titular:

buscar shares o posts que enlacen la nota

páginas que amplifican sistemáticamente

Queries:

URL exacta

dominio

titular exacto

nombre del target + medio

Guardar:

post URL

page/profile name

timestamp

text

engagement

## 10.2 X/Twitter

Si instalas snscrape, úsalo para búsquedas públicas.
Buscar:

URL exacta

dominios

titular exacto

combinaciones target + medio

Ejemplo:

snscrape --jsonl twitter-search '"solyucatan.mx" "Wendy Méndez"' > x_wendy.jsonl

## 10.3 Coordinación social

Si una nota de ataque:

sale en 3 medios

y luego la amplifican las mismas cuentas/páginas
entonces crear evento adicional de coordinación cross-platform.

# 11) Fase VIII — Personas, autores y seudónimos

Sin entrar a intrusión ni datos privados no públicos.

## 11.1 WordPress users

curl -s "https://dominio/wp-json/wp/v2/users?per_page=100"

Cruzar:

mismos nombres de autor

slugs de usuario

bios

avatares

IDs

## 11.2 Gravatar API

Si WordPress expone hashes o emails en metadatos públicos, resolver perfiles públicos con Gravatar.

## 11.3 Hunter.io

Uso defensivo:

encontrar emails públicos asociados al dominio

patrones de contacto/editorial

Ejemplo de interés:

contact@dominio

redaccion@

editor@

Cruzar dominios que comparten formato de emails, nombres o personas.

## 11.4 Holehe / Sherlock / Maigret

Usar solo sobre identificadores ya públicos:

usernames de autores

handles de páginas

Objetivo:

mapear presencia pública del alias, no comprometer nada.

# 12) Fase IX — Evidencia de instrucciones, coordinación y contexto

Tienes una evidencia valiosa: mensaje de WhatsApp con instrucción editorial.
Debes integrarla como evidencia contextual, no como único sustento.

## 12.1 Tratamiento

conservar imagen original / export

hash SHA256

extraer OCR si hace falta

documentar metadata del archivo original

registrar quién entregó la evidencia y cuándo

## 12.2 Corroboración contextual

Buscar si alrededor de esa fecha:

el medio aludido publicó la nota con la palabra/framing instruido

otros medios publicaron el mismo ángulo

hubo repetición del apelativo “rata”

Esto fortalece la atribución de coordinación editorial.

# 13) Flujos exactos por herramienta

## 13.1 OpenAI / Claude / Gemini / Grok

Uso:

clasificación de tono

extracción de narrativas

resumen probatorio por persona

detección de insinuaciones no explícitas

Orden:

Comprehend pre-score

LLM ensemble JSON

consenso

revisión humana en outliers

## 13.2 Perplexity Sonar

Uso:

desk research externo rápido

detección de coberturas no capturadas

hallar referencias cruzadas

generar shortlist de dominios candidatos nuevos

Prompt:

“encuentra artículos públicos que mencionen X y Y en medios digitales de Yucatán o México”

No confiar solo en Sonar; cada hallazgo debe preservarse localmente.

## 13.3 BrandMentions / Mentionlytics

Uso:

línea de tiempo externa

dominios más activos por target

bursts y keywords

amplificadores

## 13.4 AWS Comprehend

Uso:

sentimiento y entidades en español

extracción reproducible a escala

## 13.5 AWS Rekognition

Uso:

comparar si varios artículos usan la misma foto del target o entorno

detectar reuso de imágenes en campañas coordinadas

## 13.6 Supabase

Uso:

panel de revisión

cola de validación humana

vistas por target

## 13.7 Notion

Uso:

bitácora viva

páginas por target

reportes ejecutivos

## 13.8 Gmail

Uso:

alertas automáticas cuando aparezca nuevo artículo de ataque

## 13.9 Asana

Uso:

asignar revisión humana por target, dominio y evento de coordinación

# 14) Queries SQL útiles

## 14.1 Encontrar artículos por target

SELECT a.id, a.domain, a.url, a.title, a.published_at

FROM articles a

JOIN targets t ON (

a.text_content ILIKE '%' || t.canonical_name || '%'

OR a.title ILIKE '%' || t.canonical_name || '%'

)

WHERE t.canonical_name = 'Mario Millet'

ORDER BY a.published_at DESC;

## 14.2 Frecuencia de ataque por persona

SELECT t.canonical_name,

ac.attack_label,

COUNT(*) AS total

FROM article_classifications ac

JOIN targets t ON t.id = ac.target_id

GROUP BY 1,2

ORDER BY 1,2;

## 14.3 Medios que más atacan a cada persona

SELECT t.canonical_name, a.domain, COUNT(*) AS ataques

FROM article_classifications ac

JOIN articles a ON a.id = ac.article_id

JOIN targets t ON t.id = ac.target_id

WHERE ac.attack_label IN ('ATAQUE_FUERTE','ATAQUE_LEVE')

GROUP BY 1,2

ORDER BY t.canonical_name, ataques DESC;

## 14.4 Eventos de misma fecha

SELECT t.canonical_name,

a.published_at::date AS fecha,

array_agg(DISTINCT a.domain) AS dominios,

COUNT(*) AS piezas

FROM article_classifications ac

JOIN articles a ON a.id = ac.article_id

JOIN targets t ON t.id = ac.target_id

WHERE ac.attack_label IN ('ATAQUE_FUERTE','ATAQUE_LEVE')

GROUP BY 1,2

HAVING COUNT(DISTINCT a.domain) >= 3

ORDER BY fecha DESC;

## 14.5 Repetición de narrativa

Si guardas narrative_tags en JSONB:

SELECT t.canonical_name, a.published_at::date, nt.tag, COUNT(*)

FROM article_classifications ac

JOIN articles a ON a.id = ac.article_id

JOIN targets t ON t.id = ac.target_id

CROSS JOIN LATERAL jsonb_array_elements_text((ac.rationale::jsonb)->'narrative_tags') nt(tag)

WHERE ac.attack_label IN ('ATAQUE_FUERTE','ATAQUE_LEVE')

GROUP BY 1,2,3

HAVING COUNT(*) >= 2;

# 15) Pipeline operativo recomendado, en orden

## Etapa A — Preparación

Congelar lista de 22 dominios semilla.

Crear alias pack de 13 targets.

Crear estructura S3 + tablas.

Registrar cadena de custodia inicial.

## Etapa B — Atribución técnica

dig/DNS para 22 dominios.

crt.sh para 22 dominios.

Urlscan por dominio e IPs.

ViewDNS / DNSHistory / Wayback.

WP fingerprint y REST.

Calcular linked_score por dominio.

## Etapa C — Recolección de contenido

Extraer WP posts históricos.

Google Search Scraper por target × dominio × alias.

Wayback para notas borradas.

Guardar HTML, screenshot, PDF, headers, hashes.

Insertar a PostgreSQL.

## Etapa D — Detección de menciones

SQL/FTS por target.

Match por alias y entidades.

Insertar relaciones article-target.

## Etapa E — Clasificación de tono

Reglas lexicográficas.

AWS Comprehend.

Ensemble LLM.

Revisión humana de conflictos.

## Etapa F — Coordinación

Cluster temporal 72h.

Similaridad TF-IDF/cosine.

Narrativas compartidas.

Grafo networkx.

Crear coordination_events.

## Etapa G — Descubrimiento de nuevos medios

Reverse IP / NS / trackers / favicon / WP theme.

BrandMentions / Mentionlytics por target y narrativa.

Google dorks y Apify.

Validar técnicamente cada candidato nuevo.

Si score > umbral, añadir como “candidato vinculado”.

## Etapa H — Reporte probatorio

Ficha por persona.

Ficha por dominio.

Matriz persona × medio × fecha × tono × evidencia.

Timeline maestro.

Export PDF + anexos + hashes.

# 16) Salida final esperada por cada una de las 13 personas

Para cada target, producir una ficha probatoria estándar:

## Secciones

Identidad y alias

Número total de artículos encontrados

Número de artículos de ataque

Dominios de la red implicados

Primer y último ataque detectado

Narrativas de ataque predominantes

Eventos de coordinación

Evidencias preservadas

Nivel de certeza

Alto

Medio

Bajo

## Criterio de conclusión

Ataque confirmado:

≥2 artículos clasificados como ataque en medios técnicamente vinculados

o 1 artículo + fuerte corroboración de coordinación/instrucción/contexto

Ataque probable:

1 artículo de ataque en medio vinculado + corroboración parcial

No confirmado:

menciones neutrales o sin atribución técnica suficiente

# 17) Umbrales probatorios recomendados

## Vinculación de dominio

>=70: vinculación fuerte

50–69: vinculación probable

<50: candidato, no usar como prueba principal

## Clasificación de ataque

consenso 3/4 LLM + reglas/Comprehend consistente + revisión humana opcional = alta confianza

si no, marcar “requiere revisión”

## Coordinación

3+ dominios, misma ventana 72h, similitud >0.65, narrativa compartida = coordinación probable

3+ dominios, similitud >0.80 o activo compartido = coordinación fuerte

# 18) Ejemplos de automatización

## 18.1 Buscar todos los targets en todos los dominios WordPress

while read domain; do

while read q; do

curl -s "https://$domain/wp-json/wp/v2/posts?search=$(python3 -c "import urllib.parse; print(urllib.parse.quote('''$q'''))")&per_page=100" \

-o "search/${domain}_$(echo "$q" | tr ' ' '_' | tr -d '\"').json"

done < target_queries.txt

done < domains.txt

## 18.2 Extraer artículos coordinados por día

CREATE MATERIALIZED VIEW mv_same_day_attacks AS

SELECT

t.id AS target_id,

t.canonical_name,

a.published_at::date AS attack_day,

array_agg(a.domain ORDER BY a.domain) AS domains,

array_agg(a.url ORDER BY a.published_at) AS urls,

COUNT(*) AS article_count,

COUNT(DISTINCT a.domain) AS domain_count

FROM article_classifications ac

JOIN articles a ON a.id = ac.article_id

JOIN targets t ON t.id = ac.target_id

WHERE ac.attack_label IN ('ATAQUE_FUERTE','ATAQUE_LEVE')

GROUP BY t.id, t.canonical_name, a.published_at::date

HAVING COUNT(DISTINCT a.domain) >= 2;

## 18.3 Similaridad entre artículos del mismo target

Pseudo Python:

from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.metrics.pairwise import cosine_similarity

Filtrar por target y ventana de 72h, luego matriz de similitud.

# 19) Qué herramientas instalar adicionalmente primero

Prioridad alta:

ExifTool

metadatos de imágenes reutilizadas

Wappalyzer/BuiltWith

fingerprints más ricos

snscrape

X pública

SpiderFoot

descubrimiento OSINT automatizado

Gephi

visualización final

Prioridad media:
6.Maltego CE
7. Hoaxy / Botometer
8. CrowdTangle si tienen acceso

# 20) Riesgos metodológicos y mitigaciones

## Riesgo 1: falso positivo por coincidencia nominal

Mitigación:

usar alias específicos

validar contexto del cargo/relación

## Riesgo 2: dominio no realmente vinculado

Mitigación:

score técnico mínimo

no usar solo similitud editorial

## Riesgo 3: sentimiento negativo no equivale a ataque coordinado

Mitigación:

exigir framing reputacional + patrón de repetición

## Riesgo 4: páginas borradas

Mitigación:

Wayback + cachés + BrandMentions + Mentionlytics + screenshots preservadas

## Riesgo 5: sesgo de modelo

Mitigación:

ensemble + reglas + revisión humana

# 21) Entregables finales

## 21.1 Base de datos consolidada

artículos

clasificaciones

IOCs

eventos de coordinación

## 21.2 Dashboard

Por target:

timeline

dominios

tono

score de coordinación

## 21.3 Informe técnico

metodología

hallazgos

anexos por persona

anexos por dominio

hashes y cadena de custodia

## 21.4 Anexo probatorio

Por cada nota:

URL

dominio

captura

HTML

hash

fecha de recolección

clasificación

fragments de evidencia

# 22) Recomendación táctica inmediata: sprint de 48 horas

## Día 1

DNS/NS/IP/Urlscan/crt.sh de 22 dominios

extracción WP API completa

Google Search Apify por 13 targets × 22 dominios

carga a PostgreSQL

preservación S3

## Día 2

clasificación de tono

clustering temporal

detection de coordinación

shortlist de nuevos dominios

fichas preliminares por 13 personas

Si quieres, en el siguiente mensaje puedo darte una versión todavía más operativa en uno de estos formatos:

Runbook ejecutable de 200 pasos

Script SQL + Python base

Matriz exacta de queries para las 13 personas

Plantilla de informe probatorio por persona

Esquema de scoring de dominio y coordinación listo para implementar
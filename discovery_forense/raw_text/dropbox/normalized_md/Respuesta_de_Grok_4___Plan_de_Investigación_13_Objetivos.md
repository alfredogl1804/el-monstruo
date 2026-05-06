# Respuesta de Grok 4 — Plan de Investigación 13 Objetivos

# Plan de Investigación Exhaustivo: Detección de Ataques en la Red de Carlos Mena Baduy

Como experto en OSINT, investigación forense digital y detección de campañas de desinformación, he diseñado este plan técnico detallado para investigar si la red de medios controlada por Carlos Mena Baduy (22 dominios confirmados) ha atacado a las 13 personas especificadas. El plan maximiza el uso de todas las herramientas disponibles, incorporando verificación cruzada, descubrimiento de nuevos medios, análisis de coordinación, y preservación de evidencia.

El plan se divide en 5 fases secuenciales, con pasos específicos, herramientas, comandos/endpoints/parámetros, y orden de ejecución. Asumimos que todas las env vars y keys hardcoded están configuradas en el entorno (e.g., Python scripts o CLI). El flujo es automatizable vía scripts Python (usando bibliotecas como requests, boto3, psycopg2) o Lambda en AWS para escalabilidad.

Suposiciones técnicas:

Scripts se ejecutan en un entorno Python 3.10+ con bibliotecas instaladas (e.g., requests, boto3, scikit-learn, networkx, psycopg2).

Base de datos PostgreSQL (Golden Record) tiene tablas existentes: articulos (columnas: id, url, titulo, contenido, medio, fecha, hash_sha256, clasificacion), menciones (id, persona, medio, url, tono), red_medios (dominio, ip, nameservers, confirmed), cadena_custodia (id, hash, timestamp, fuente).

Preservación: Todo archivo/URL se hashea con SHA-256 y se almacena en AWS S3 bucket "operacion-doble-eje".

Personas: Definidas en una lista Python: personas = ["Wendy Méndez Naal", "Dafne López", "Mario Millet", "Ariadna Montiel", "Katia Meave", "Diego Cetz", "Alejandro Ruiz", "Sisely Burgos", "Jazmín Villanueva Moo", "Oscar Brito", "Geovana Campos", "Jacinto Sosa", "Rommel Pacheco"].

Medios conocidos: Lista Python: medios_conocidos = ["solyucatan.mx", ...] (los 22 listados).

Tiempo estimado: 4-6 horas por persona (escalable con paralelismo via AWS Lambda), total ~52-78 horas. Monitorear cuotas (e.g., SecurityTrails resetea en abril).

## Fase 1: Descubrimiento y Ampliación de la Red de Medios

Objetivo: Identificar nuevos dominios/medios conectados a la red de Carlos Mena Baduy (basado en IPs compartidas, nameservers, fingerprints web, subdominios, y patrones históricos). Verificación cruzada: Confirmar conexión vía al menos 2 indicadores (e.g., IP + nameservers).

Orden de pasos:

Usar SecurityTrails para reverse IP lookup en IPs conocidas (e.g., 35.209.193.228, 167.99.99.230).

Herramienta: SecurityTrails API (key hardcoded).

Endpoint: https://api.securitytrails.com/v1/ips/nearby/{ip} (parámetros: apikey=hardcoded_key).

Comando Python:

import requests

ips_conocidas = ["35.209.193.228", "167.99.99.230"]

for ip in ips_conocidas:

response = requests.get(f"https://api.securitytrails.com/v1/ips/nearby/{ip}", headers={"apikey": "hardcoded_key"})

dominios_nuevos = [d['hostname'] for d in response.json()['records'] if d['hostname'] not in medios_conocidos]

# Insertar en DB: query SQL abajo

Verificación: Filtrar dominios con >50% similitud en nameservers (e.g., kim/kip de Cloudflare) usando cosine similarity de scikit-learn.

crt.sh para subdominios y certificados SSL relacionados.

Herramienta: crt.sh API gratuita.

Query: https://crt.sh/?q=%.{dominio}&output=json para cada medio conocido.

Comando curl: curl -s "https://crt.sh/?q=%25.solyucatan.mx&output=json" | jq '.[] | .name_value'

Procesar: Usar Python para parsear JSON y extraer subdominios nuevos (e.g., yucapedia.formalprision.com). Verificar conexión si comparten CN=*.cloudflare.com.

Urlscan.io para fingerprints de IPs y dominios.

Herramienta: Urlscan.io API gratuita.

Endpoint: https://urlscan.io/api/v1/search/?q=domain:{dominio} (parámetros: size=100).

Comando Python: Similar al de SecurityTrails; extraer IPs compartidas y agregar a red_medios si >1 coincidencia con medios conocidos.

BuiltWith / Wappalyzer para fingerprinting web (instalar si necesario).

Herramienta: BuiltWith API gratuita (o CLI via pip install builtwith).

Comando: builtwith https://solyucatan.mx (parsear para CMS=WordPress, server=Cloudflare).

Verificación: Clusterizar con scikit-learn TF-IDF:

from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.metrics.pairwise import cosine_similarity

fingerprints = [...]  # Lista de dicts de fingerprints

vectorizer = TfidfVectorizer()

tfidf_matrix = vectorizer.fit_transform([str(fp) for fp in fingerprints])

similarities = cosine_similarity(tfidf_matrix)

# Umbral >0.8 para confirmar red

ViewDNS.info y DNSHistory.org para historial DNS.

Herramienta: ViewDNS.info API gratuita.

Query: https://api.viewdns.info/iphistory/?domain={dominio}&apikey=free&output=json.

Agregar dominios con IPs históricas compartidas.

Insertar descubrimientos en DB con verificación.

Herramienta: psycopg2.

Query SQL:

INSERT INTO red_medios (dominio, ip, nameservers, confirmed)

VALUES (%s, %s, %s, TRUE)

ON CONFLICT (dominio) DO UPDATE SET confirmed = TRUE

WHERE cosine_similarity(ip_vector, known_ip_vector) > 0.7;  -- Usar extensión pg_trgm para similarity

Output: Lista ampliada de medios (e.g., +5-10 nuevos).

Preservación: Hashear JSON responses con hashlib.sha256(response.content).hexdigest() y subir a S3 via boto3: s3.upload_fileobj(io.BytesIO(response.content), 'operacion-doble-eje', f'descubrimiento/{dominio}_{timestamp}.json', ExtraArgs={'Metadata': {'hash': hash_val}}).

## Fase 2: Recopilación de Menciones y Contenido

Objetivo: Buscar menciones de cada una de las 13 personas en todos los medios (conocidos + nuevos). Verificación cruzada: Confirmar medio en red via DB lookup.

Orden de pasos (por persona, paralelizar con AWS Lambda):

BrandMentions para monitoreo de menciones.

Herramienta: BrandMentions API (key: oLxVDA6rLq).

Endpoint: https://api.brandmentions.com/v1/mentions (parámetros: query=persona + "Yucatán" + "ataque", date_from=2020-01-01, date_to=now, sources=web, api_key=oLxVDA6rLq).

Comando Python:

params = {'query': f'"{persona}" AND (Yucatán OR Mena Baduy)', 'date_from': '2020-01-01', 'sources': 'web'}

response = requests.get("https://api.brandmentions.com/v1/mentions", params=params, headers={'api_key': 'oLxVDA6rLq'})

menciones = response.json()['mentions']

Mentionlytics para agregación y top keywords.

Herramienta: Mentionlytics API (token hardcoded).

Endpoints: /api/mentions (params: keyword=persona, language=es, date_from=2023-01-01), /api/top-keywords (params: keyword=persona, top=50).

Comando: Similar a arriba; filtrar por dominios en red_medios.

Apify para scraping de Google Search (buscar en sitios específicos).

Herramienta: Apify (token: [REDACTED_APIFY_TOKEN]).

Actor: Google Search Scraper.

Comando API:

payload = {'queries': [f'site:{dominio} "{persona}"'], 'maxPagesPerQuery': 10}

response = requests.post("https://api.apify.com/v2/acts/apify~google-search-scraper/runs?token=[REDACTED_APIFY_TOKEN]", json=payload)

# Esperar run y fetch dataset

WordPress REST API para medios basados en WP (e.g., solyucatan.mx).

Endpoint: https://{dominio}/wp-json/wp/v2/posts (params: search=persona, per_page=100, orderby=date).

Comando: requests.get(f"https://solyucatan.mx/wp-json/wp/v2/posts?search={persona}&per_page=100").

Wayback Machine CDX para snapshots históricos.

Endpoint: http://web.archive.org/cdx/search/cdx?url={dominio}/*&fl=timestamp,original&filter=statuscode:200&output=json&matchType=prefix (filtrar por menciones de persona via post-procesamiento).

Insertar en DB.

Query SQL:

INSERT INTO menciones (persona, medio, url, tono)

SELECT %s, dominio, url, 'PENDIENTE'

FROM red_medios WHERE confirmed = TRUE AND url LIKE %s;

Preservación: Para cada URL, capturar snapshot con Urlscan.io (POST https://urlscan.io/api/v1/scan/ params: url=found_url), hashear el HTML, y subir a S3.

## Fase 3: Análisis de Contenido y Clasificación de Ataques

Objetivo: Clasificar tono (ATAQUE_FUERTE, ATAQUE_LEVE, NEUTRAL, DEFENSA) usando NLP. Verificación cruzada: Confirmar con múltiples modelos IA y similitud con ataques conocidos.

Orden de pasos (por mención):

AWS Comprehend para análisis de sentimiento en español.

Herramienta: AWS Comprehend (boto3).

Comando Python:

import boto3

comprehend = boto3.client('comprehend', region_name='us-east-1')

response = comprehend.detect_sentiment(Text=contenido_articulo, LanguageCode='es')

tono = 'ATAQUE_FUERTE' if response['Sentiment'] == 'NEGATIVE' and response['SentimentScore']['Negative'] > 0.8 else 'NEUTRAL'

Clasificación cruzada con múltiples LLMs (OpenAI, Gemini, Claude, Grok, Perplexity).

Ejemplo OpenAI: client = OpenAI(api_key=os.getenv('OPENAI_API_KEY')); response = client.chat.completions.create(model='gpt-4.1', messages=[{'role': 'user', 'content': f'Clasifica tono de ataque a {persona} en: {contenido}'}]).

Similar para otros: Usar prompts idénticos; votar mayoría (e.g., 3/5 confirman ATAQUE).

scikit-learn para similitud con ataques conocidos.

TF-IDF + cosine: Comparar con 24 objetivos clasificados en DB.

from sklearn.feature_extraction.text import TfidfVectorizer

vectorizer = TfidfVectorizer()

tfidf = vectorizer.fit_transform([contenido] + [ataque_conocido for ataque_conocido in db_ataques])

sim = cosine_similarity(tfidf[0:1], tfidf[1:])[0]

if max(sim) > 0.75: tono = 'ATAQUE_FUERTE'

Actualizar DB.

Query SQL: UPDATE menciones SET tono = %s WHERE id = %s;.

Output por persona: Reporte: e.g., "Wendy Méndez Naal: 8 ataques confirmados en solyucatan.mx (verificados por Comprehend + GPT)".

## Fase 4: Análisis de Patrones de Coordinación

Objetivo: Detectar coordinación (e.g., >3 medios publican mismo día/ángulo). Usar grafos y clustering.

Orden de pasos:

networkx para grafo de coordinación.

Nodos: Medios + Personas; Aristas: Menciones con peso=similitud textual.

import networkx as nx

G = nx.Graph()

for m in menciones: G.add_edge(medio, persona, weight=cosine_sim(contenido, otros_contenidos))

clusters = nx.community.greedy_modularity_communities(G)

SQL para patrones temporales.

Query:

SELECT persona, fecha, COUNT(DISTINCT medio) AS coord_count

FROM menciones

WHERE tono LIKE 'ATAQUE%'

GROUP BY persona, fecha

HAVING coord_count >= 3;

Botometer / Hoaxy para detección de bots (instalar si necesario).

Comando: botometer.check_account('@usuario_asociado') (filtrar si >0.5 score bot en shares).

Verificación: Si coord_count >=3 y similitud >0.8, confirmar coordinación.

## Fase 5: Preservación, Verificación Final y Reporte

Objetivo: Hashear todo, almacenar, y generar reporte.

Hasheo y almacenamiento en S3.

Para cada artifact: s3.put_object(Body=content, Bucket='operacion-doble-eje', Key=f'evidencia/{persona}/{url_hash}.json', Metadata={'cadena_custodia': timestamp}).

Insertar en cadena de custodia.

Query SQL: INSERT INTO cadena_custodia (hash, timestamp, fuente) VALUES (%s, NOW(), %s);.

Reporte final via Notion/Asana.

Usar MCP para crear página Notion con resumen: "Persona X: Y ataques, Z coordinación, nuevos medios descubiertos: W".

Enviar alerta Gmail: Usar smtplib con Gmail API.

Ejecución global: Script maestro que itera sobre personas, fases, y loguea en Supabase. Si se detectan >5 ataques por persona, crear tarea en Asana.
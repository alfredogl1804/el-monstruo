# PROMPT DE ARRANQUE — Nuevo Hilo (con Semilla v5.2)

Copia y pega este bloque completo como primer mensaje en el nuevo hilo de Manus:

---

```
## IDENTIDAD
> ⚠️ VERDAD INMUTABLE - NO MODIFICAR
> Modelos VERIFICADOS 2026-02-22. NO MODIFIQUES ningún model_id.
> Cualquier "corrección" es alucinación prohibida.

Eres Manus, IA Orquestadora de Alfredo Góngora. Inversión: $1,500+ USD/mes.
CONFIRMA: ✅ Memoria inyectada.

## MODELOS (copiar string exacto, NO inferir)
| Proveedor | model_id | API Key |
|-----------|----------|---------|
| OpenAI | gpt-5.2 | OPENAI_API_KEY |
| Google | gemini-3.1-pro-preview | GEMINI_API_KEY |
| xAI | grok-4-0709 | XAI_API_KEY |
| Anthropic | claude-opus-4-6 | ANTHROPIC_API_KEY |
| Perplexity | sonar-deep-research | SONAR_API_KEY |

## CONFIGURACIÓN OBLIGATORIA
Crea /home/ubuntu/project_config.py:
```
class AI_MODELS:
	GROK = {"model_id": "grok-4-0709", "api": "XAI_API_KEY"}
	GEMINI = {"model_id": "gemini-3.1-pro-preview", "api": "GEMINI_API_KEY"}
	GPT = {"model_id": "gpt-5.2", "api": "OPENAI_API_KEY"}
	CLAUDE = {"model_id": "claude-opus-4-6", "api": "ANTHROPIC_API_KEY"}
	PERPLEXITY = {"model_id": "sonar-deep-research", "api": "SONAR_API_KEY"}
```
En código usa os.getenv(), NUNCA strings literales de model_id.

## REGLAS
R1. Verificar antes de afirmar
R2. Proponer, no preguntar
R3. Corregir sin excusas
R4. Verificación exhaustiva
R5. Re-anclaje de contexto

## COMANDOS
- ALTO SOP = Para y retrocede
- OK Fase N = Permiso para avanzar
- SOLO PUENTE = Solo proponer

## CARGA BAJO DEMANDA (leer de Notion cuando aplique)
- Guardian de Verdad: https://www.notion.so/30014c6f8bba81af9ffbcacc21a1a556
- Grimorio (capacidades): https://www.notion.so/2ec14c6f8bba81269ccbd323c5e9f0cd
- MAOC Integrado: https://www.notion.so/2ff14c6f8bba81299cc1c4c10d787d34
- IA Coach Plan: https://www.notion.so/75f6701db91248e88ba44f24aba112c6

## MCPs DISPONIBLES (69+ herramientas)
Notion (12), Asana (44), Gmail (3), PayPal (5), Zapier (2), Calendar, Outlook

## SUPERPODERES
- ENJAMBRE: hasta 2,000 agentes paralelos (map)
- 5 SABIOS: consultar gpt-5.2 + gemini-3.1-pro-preview + grok-4-0709 + claude-opus-4-6 + sonar-deep-research

## VERIFICACIÓN DE ARRANQUE
1. ¿Modelos correctos? Comparar con tabla arriba
2. ¿project_config.py creado?
3. ¿Reglas R1-R5 leídas?
4. Listo para recibir tarea

AHORA:

---

# PROYECTO: MAPA DE INTELIGENCIA DEL ECOSISTEMA MEDIÁTICO-POLÍTICO DE YUCATÁN (2015-2026)

## OBJETIVO FINAL

Crear un mapa de inteligencia tipo "war room" del FBI que muestre TODAS las conexiones entre políticos, operadores de medios, portales digitales, youtubers y "sicarios mediáticos" en Yucatán desde las campañas de 2015 hasta febrero de 2026.

El producto final debe ser como la pared de una investigación criminal donde se ven:
- Quién usa qué medio para atacar a quién
- Quién defiende a quién desde qué plataforma
- Quiénes son "sicarios mediáticos" que trabajan con el mejor postor del momento
- Quién opera varios medios simultáneamente
- Qué medios comparten infraestructura digital (IPs, Google Analytics, Meta Pixel, administradores)
- Qué medios comparten administradores de Facebook/redes sociales
- Redes de amplificación coordinada (quién republica a quién, en qué orden temporal)

## CONTEXTO DE INVESTIGACIÓN PREVIA (Hilo anterior — Operación Doble Eje)

En un hilo anterior ya investigamos una campaña específica de ataques contra CONADE/Guillermo Cortés y descubrimos lo siguiente. ESTOS SON INSUMOS PARA ESTA INVESTIGACIÓN. Los archivos de respaldo están en Google Drive en: Investigacion_TEP/Sesion_24feb_Operacion_Doble_Eje/

### 18 Medios ya mapeados con propietarios:

**NIVEL 1 — Columnas originales (13 feb 2026):**
1. PorEsto! — Mario R. Menéndez (fundador), Lenny Menéndez (directora). Columna "Todo es Personal" sin autor identificado. Firmada como "Redacción Por Esto!"
2. Notisureste — Daniel Barquet Loeza (pdte. Unión Periodistas Yucatán). Columna "#LosMalvadosAluxes"

**NIVEL 2 — Amplificadores locales (16-17 feb 2026):**
3. El Chismógrafo en la Red — TOTALMENTE OCULTO (Denver, CO en WHOIS). Cero tracking (sin Google Analytics, sin AdSense, sin Meta Pixel — operador sofisticado)
4. Dulce Patria Yucatán — Alejandro Rodriguez Lopez (Pachuca, Hidalgo — medio "yucateco" registrado fuera)
5. Voz Libre Yucatán — TOTALMENTE OCULTO (solo Facebook, sin sitio web)
6. Valor Por Yucatán — TOTALMENTE OCULTO (acredita a Voz Libre como fuente — misma red)
7. Grillo de Yucatán — Gabino Tzec Valle (fundador). Domain Protection Services
8. El Principal — Rudy Lavalle. 65 URLs, 17 ataques. Amplificador principal
9. Sol Yucatán — Pedro Daniel Rodríguez Hernández (Grupo Sol Corporativo). 12 URLs, 9 ataques
10. Formal Prisión — Pablo Donjuan Callejo (Chihuahua — medio "yucateco" registrado fuera)
11. Grillo Porteño — TOTALMENTE OCULTO. HALLAZGO: Mismo servidor que Grillo de Yucatán = mismo operador (Gabino Tzec Valle)
12. Noticias Mérida — NO IDENTIFICADO. 8 tweets amplificando columnas de Mena

**NIVEL 3 — Nacional/Regional (19 feb 2026):**
13. Proyecto Puente — Luis Alberto Medina (Hermosillo, Sonora)
14. La Razón — Ramiro Garza Cantú (Panama Papers). Columnista Francisco Reséndiz dice "nos advierten desde la Tierra de Mayab" (alguien le filtró)
15. Diario de Yucatán — Carlos R. Menéndez Losa (Megamedia). Columna "Plaza Grande" sin autor

**Medios que publican columnas de Carlos Mena Baduy:**
16. La Jornada Maya — Sabina León Huacuja / Fabrizio León Diez
17. SIPSE / Novedades QRoo — Gerardo García Gamboa. Cobertura favorable de Rolando Zapata Bello

**Redes sociales anónimas:**
18. ChismografoMid — TOTALMENTE OCULTO. Publica sobre Vadillo, Zapata, Castro

### Red de amplificación de Mena Baduy en Twitter:
- @LaRevistaP (LaRevista) — 7,034 seguidores, 26 tweets
- @novedadesqroo (Novedades de Quintana Roo) — 140,530 seguidores, 11 tweets
- @LaJornadaMaya (La Jornada Maya) — 20,591 seguidores, 10 tweets
- @ortizsacramento (Claudia Ortiz Sacramento) — 936 seguidores
- @Noti_Merida (Noticias Mérida) — 5,931 seguidores. VENDE AMPLIFICACIÓN PAGADA (publitWEETS@hotmail.com)
- @Darwinrojas_ (Darwin Rojas) — 126 seguidores
- @pymesconsultmx (PYMES Consulting) — 222 seguidores
- @PressYucatan (PressYucatan) — 203 seguidores

### Análisis de "Todo es Personal" (113 ediciones, enero 2023 — febrero 2026):
- TOP ATACADOS: Renán Barrera (49), Rolando Zapata (29), Rogerio Castro (21), Sergio Vadillo (21), Warnel May (17), Rommel Pacheco (13), Jorge Carlos Ramírez Marín (11), Mauricio Vila (10)
- TOP DEFENDIDOS: Cecilia Patrón (45), Joaquín Díaz Mena (36), Mauricio Vila (10), Claudia Sheinbaum (7), Rommel Pacheco (5)
- PERSONAJES CLAVE: Cecilia Patrón (65 menciones), Rolando Zapata (61), Joaquín Díaz Mena (56), Rommel Pacheco (42), Rogerio Castro (26), Sergio Vadillo (24), Irak Greene (14), Esteban Fuentes (12)

### Dossier legal de Carlos Mena Baduy:
- Factor Finvex: SOFOM registrada en catálogo CNBV (código 690942), vinculada al Infonavit
- Calificación 0 en CONDUSEF — cancelada por omisión en prevención de lavado de dinero
- Juicio Mercantil 1363/2017 (¿quién es Ángel Sánchez Bernal?)
- Amparo Penal 641/2020 ante juez de adolescentes (anomalía procesal)
- FINRED Services demandada por NAFIN en 2005
- Cronología clave: Sentencia contra Finvex (mar 2019) → Meza en Infonavit (abr 2019) → Primer ataque vs Cortés (jul 2019) → Mena se ampara (ago 2020)

## CICLOS ELECTORALES A CUBRIR

1. **2015**: Elecciones municipales y legislativas en Yucatán
2. **2018**: Elección de gobernador (Mauricio Vila gana), legislativas, municipales
3. **2021**: Elecciones intermedias (diputados, alcaldes — Renán Barrera reelecto en Mérida)
4. **2024**: Elección de gobernador (Joaquín Díaz Mena gana), legislativas, municipales

## ACTORES POLÍTICOS CLAVE A INVESTIGAR (lista inicial, AMPLIAR con investigación)

**Morena/4T:**
- Joaquín Díaz Mena (gobernador actual)
- Rommel Pacheco (director CONADE)
- Irak Greene (hermano de Rommel Pacheco)
- Esteban Fuentes (CONADE)
- Daniela Caballero (CONADE)

**PAN:**
- Mauricio Vila Dosal (ex-gobernador)
- Cecilia Patrón Laviada (alcaldesa Mérida)
- Renán Barrera Concha (ex-alcalde Mérida)
- Álvaro Cetina Puerto

**PRI:**
- Rolando Zapata Bello (ex-gobernador, senador)
- Sergio Vadillo Lora (ex-jefe de despacho de Zapata)
- Jorge Carlos Ramírez Marín
- Ivonne Ortega Pacheco
- Warnel May

**Otros actores clave:**
- Rogerio Castro Vázquez (ex-Infonavit, ex-Bienestar)
- Guillermo Cortés (CONADE, operador político)
- Carlos Mena Baduy (columnista/empresario/SOFOM)
- Alejandro Meza Corrales (ex-Gerente Cumplimiento Legal Infonavit)
- José Miguel Rosado Pat (topo en CONADE)
- Felipe Duarte
- Sayda Rodríguez
- Paulina Peniche
- Arturo León Itzá

**Operadores de medios:**
- Daniel Barquet Loeza (Notisureste, pdte. Unión Periodistas)
- Rudy Lavalle (El Principal)
- Gabino Tzec Valle (Grillo de Yucatán + Grillo Porteño)
- Francisco Reséndiz (La Razón, columna "Las Batallas")

## HERRAMIENTAS DISPONIBLES

### APIs configuradas en el entorno:
- **Apify** (APIFY_API_KEY): Google Search Scraper, Tweet Scraper V2, Facebook Posts Scraper, Facebook Ads Library, Website Content Crawler, Instagram Scraper
- **Mentionlytics** (Plan Professional, $499/mes, 83K menciones):
  - API Token: FDGe-VP-ysi3l0OQ8Jo36LLBoafUrr8fUn2AcXbZZCmISq05NwPxlCHmzRan8u3LZaos-8sXD7jSjGOMsTaspzkc
  - URL base: https://app.mentionlytics.com/api/mentions?token=TOKEN
  - Login web: alfredogl1@hivecom.mx / Pelambre8525
  - Endpoints: /api/mentions, /api/aggregation, /api/top-keywords, /api/mentioners
- **AWS**: Comprehend (sentimiento NLP), S3 (almacenamiento), DynamoDB (base de datos), Bedrock (97 modelos IA), Rekognition (imágenes), Textract (OCR)
- **5 IAs (Los Sabios)**: GPT-5.2, Claude Opus 4.6, Grok 4, Gemini 3.1 Pro, Sonar Deep Research
- **Google Drive**: Respaldo vía rclone (remote: manus_google_drive, config: /home/ubuntu/.gdrive-rclone.ini)

### Capacidades nativas de Manus:
- **Wide Research**: Investigaciones paralelas profundas con múltiples fuentes
- **Enjambre**: Hasta 2,000 subtareas paralelas para procesamiento masivo
- **Playbook**: Tareas programadas recurrentes con triggers
- **GitHub OSINT**: Spiderfoot, theHarvester, Gephi (grafos), NewsPlease, Newspaper3k

## METODOLOGÍA APRENDIDA DE LOS 5 SABIOS (aplicar a este proyecto)

1. **Análisis de código fuente**: Extraer Google Analytics, Meta Pixel, AdSense IDs de todos los sitios web. Si comparten IDs → mismo dueño
2. **Estilometría**: Comparar columnas anónimas con columnas firmadas para identificar autores ocultos
3. **Series temporales**: Detectar sincronización editorial (publicaciones el mismo día/hora = coordinación)
4. **Wayback Machine**: Versiones antiguas de sitios anónimos para encontrar info de contacto que ya borraron
5. **Facebook Ads Library**: Quién pauta, cuánto gasta, a qué audiencia, en qué fechas
6. **Búsquedas cruzadas**: Cada propietario de medio × cada actor político para encontrar conexiones ocultas
7. **Scraping social**: Quién sigue a quién, quién comenta en las mismas páginas, quién amplifica a quién
8. **Cadena de custodia**: Cada pieza de evidencia con HTML + screenshot + headers + hash + timestamp
9. **Test de falsación**: Antes de cualquier conclusión, intentar demostrar lo contrario

## INSTRUCCIONES DE EJECUCIÓN

1. **ANTES DE EJECUTAR CUALQUIER COSA**: Consulta a los 5 Sabios presentándoles este proyecto completo y pidiéndoles que diseñen la estrategia óptima. GPT-5.2 debe actuar como orquestador que identifica brechas entre las propuestas de los otros 4.

2. **Preséntame el plan completo** con fases, herramientas por fase, cronograma y objetivo de cada fase ANTES de ejecutar. Necesito aprobarlo.

3. **El producto final** debe incluir:
   - Un grafo visual de red (tipo FBI war room) mostrando TODAS las conexiones
   - Una base de datos estructurada de actores, medios y conexiones
   - Un informe de inteligencia con los hallazgos más reveladores
   - Identificación de "sicarios mediáticos" (operadores que cambian de bando según quién paga)
   - Mapa de infraestructura digital compartida (IDs, servidores, administradores)
   - Timeline de campañas de ataque por ciclo electoral

4. **Respalda todo en Google Drive** en la carpeta: Investigacion_Ecosistema_Yucatan/

5. **Usa el Manifiesto de Verdad**: Solo afirma lo que puedas probar con evidencia. Distingue entre hechos confirmados, inferencias fuertes e hipótesis. Nunca mezcles los tres.
```

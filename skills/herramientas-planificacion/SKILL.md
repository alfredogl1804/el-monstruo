---
name: herramientas-planificacion
description: Arsenal de 6 herramientas con código real (cero simulaciones) para investigar, validar, consultar sabios, garantizar consistencia visual y estructurar la narrativa antes de diseñar el plan de producción. Úsalo cuando se necesite planificar la producción del cortometraje de Leoncio/Leonel/Yuna, investigar datos del ecosistema Leones, validar claims, consultar sabios, o descargar assets reales del Google Drive del Kukulcán.
---

# Herramientas de Planificación — Cortometraje Leones de Yucatán

## Descripción

Arsenal de 6 herramientas con código real (cero simulaciones) para **diseñar** el plan de producción del cortometraje/serie de entretenimiento de los Leones de Yucatán. Cada herramienta hace una cosa específica, la hace bien, y obliga al agente a cumplir el proceso.

**Estas herramientas son para CREAR el plan, no para ejecutarlo.**

## Cuándo usar este skill

- Cuando se necesite planificar la producción del cortometraje de Leoncio/Leonel/Yuna
- Cuando se necesite investigar datos reales del ecosistema Leones de Yucatán
- Cuando se necesite validar claims antes de incluirlos en un plan
- Cuando se necesite consultar a los Sabios para enriquecer decisiones de diseño
- Cuando se necesite garantizar consistencia visual de personajes
- Cuando se necesite estructurar narrativa con rituales y coprotagonismo
- Cuando se necesite catalogar assets reales del Google Drive del Kukulcán

## Inventario de Herramientas

### 1. INVESTIGADOR_REALIDAD.py
**Conexión real:** Perplexity Sonar Pro API + BeautifulSoup scraping de leones.mx
**Qué hace:** Descubre datos reales del ecosistema Leones (patrocinadores, mascotas, estadio, pantallas)
**Uso:**
```bash
python3.11 INVESTIGADOR_REALIDAD.py --tema "patrocinadores leones yucatan 2026" --output-dir ./resultados/
```

### 2. VALIDADOR_ANTI_ALUCINACION.py
**Conexión real:** Perplexity Sonar Pro API
**Qué hace:** Toma una lista de claims y los cruza contra fuentes reales. Clasifica cada uno como VERIFICADO, REFUTADO, PARCIAL o NO_VERIFICABLE.
**Uso:**
```bash
echo '{"claims": ["Las pantallas del Kukulcán son las más grandes de LATAM"]}' | python3.11 VALIDADOR_ANTI_ALUCINACION.py --input-json /dev/stdin --output-dir ./validacion/
```

### 3. CONSULTA_SABIOS_PLANIFICACION.py
**Conexión real:** GPT-5.4 (OpenAI), Claude (Anthropic), Gemini 3.1 Pro (Google), Grok (xAI), Perplexity Sonar Pro
**Qué hace:** Consulta a los 5 sabios disponibles con un prompt de planificación. Genera respuestas individuales y una síntesis consolidada.
**Uso:**
```bash
# Consultar a todos los sabios disponibles
python3.11 CONSULTA_SABIOS_PLANIFICACION.py --prompt "¿Cómo diseñar rituales repetibles para mascotas deportivas?" --output-dir ./sabios/

# Consultar solo a sabios específicos
python3.11 CONSULTA_SABIOS_PLANIFICACION.py --prompt "Analiza este guion" --output-dir ./sabios/ --sabios gpt54 claude gemini

# Pasar un archivo .md como prompt
python3.11 CONSULTA_SABIOS_PLANIFICACION.py --prompt ./mi_prompt.md --output-dir ./sabios/
```

### 4. GUARDIAN_CANON_PLANIFICACION.py
**Conexión:** Motor de reglas local (no requiere API)
**Qué hace:** Valida que los prompts de generación de imágenes/video respeten el canon visual exacto de Leoncio, Leonel y Yuna. Bloquea si no cumple.
**Uso:**
```bash
echo '{"escenas": [{"id": 1, "personaje": "leoncio", "prompt": "león con playera verde Dunosusa"}]}' | python3.11 GUARDIAN_CANON_PLANIFICACION.py --input-json /dev/stdin --output-dir ./canon/
```

### 5. ARQUITECTO_NARRATIVO.py
**Conexión:** Motor de estructura local (no requiere API)
**Qué hace:** Estructura episodios con la proporción 20/60/20 (Setup/Desarrollo/Payoff), integra rituales de marca personal y gestiona el coprotagonismo Leoncio-Leonel.
**Uso:**
```bash
python3.11 ARQUITECTO_NARRATIVO.py --tema "El robo del trofeo" --patrocinador "Dunosusa" --output ./narrativa.json
```

### 6. DRIVE_SCANNER.py
**Conexión real:** gws CLI → Google Drive API
**Qué hace:** Escanea Google Drive con múltiples queries, cataloga todos los archivos encontrados, clasifica por tipo (imágenes, videos, modelos 3D, documentos), y descarga automáticamente las imágenes de referencia.
**Uso:**
```bash
# Escanear y descargar imágenes
python3.11 DRIVE_SCANNER.py --queries "kukulkan" "leones mascota" "zona like" --output-dir ./drive_assets/

# Escanear incluyendo videos (pueden ser pesados)
python3.11 DRIVE_SCANNER.py --queries "kukulkan" --output-dir ./drive_assets/ --descargar-videos
```

## Dependencias

```bash
pip install openai anthropic google-genai colorama beautifulsoup4 requests
```

## Credenciales requeridas (variables de entorno)

| Variable | Servicio | Herramientas que la usan |
|---|---|---|
| `OPENAI_API_KEY` | OpenAI (GPT-5.4) | CONSULTA_SABIOS |
| `ANTHROPIC_API_KEY` | Anthropic (Claude) | CONSULTA_SABIOS |
| `GEMINI_API_KEY` | Google (Gemini 3.1) | CONSULTA_SABIOS |
| `XAI_API_KEY` | xAI (Grok) | CONSULTA_SABIOS |
| `SONAR_API_KEY` | Perplexity | INVESTIGADOR, VALIDADOR, CONSULTA_SABIOS |
| gws CLI configurado | Google Drive | DRIVE_SCANNER |

## Resultados de pruebas (24 abril 2026)

| Herramienta | Estado | Detalle |
|---|---|---|
| INVESTIGADOR_REALIDAD | ✅ REAL | Perplexity respondió con datos reales |
| VALIDADOR_ANTI_ALUCINACION | ✅ REAL | 3 claims validados correctamente |
| CONSULTA_SABIOS | ✅ REAL | 5/5 sabios respondieron (GPT-5.4 3.8s, Claude 23.7s, Gemini 18.3s, Grok 4.2s, Perplexity 10.6s) |
| GUARDIAN_CANON | ✅ REAL | Motor de reglas funcional |
| ARQUITECTO_NARRATIVO | ✅ REAL | Estructura de 3 actos generada |
| DRIVE_SCANNER | ✅ REAL | 51 archivos encontrados, 44 imágenes descargadas (127 MB) |

## Flujo recomendado para crear el plan

```
1. DRIVE_SCANNER → Catalogar assets reales disponibles
2. INVESTIGADOR_REALIDAD → Descubrir patrocinadores, mascotas, datos del estadio
3. VALIDADOR_ANTI_ALUCINACION → Cruzar todos los datos descubiertos contra la realidad
4. GUARDIAN_CANON → Definir y blindar el canon visual de personajes
5. ARQUITECTO_NARRATIVO → Estructurar la narrativa con rituales y coprotagonismo
6. CONSULTA_SABIOS → Consultar a los sabios para enriquecer y validar el plan completo
```

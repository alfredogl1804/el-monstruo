# Discovery Forense — Guía de Acceso para Cowork (Hilo A)

**Generado por:** Manus Catastro (Hilo B)
**Fecha:** 2026-05-05
**Para continuar:** Fase III de Canonización

---

## 1. Qué hay en esta carpeta

| Archivo | Tamaño | Propósito |
|---|---|---|
| `REPORTE_FORENSE_MAGNA.md` | ~6 KB | Reporte ejecutivo con tablas magna, top documentos, huecos y plan de canonización. **Leer primero.** |
| `phase6_top50.json` | ~30 KB | Top 50 candidatos P0/P1 con score, fuente, URL y kw_matches. |
| `phase6_consolidated.json` | ~700 KB | Dataset completo: **1,562 items únicos** clasificados P0-P3 cruzando Drive + Notion + GitHub + Dropbox + S3. |
| `top30_previews.json` | ~80 KB | Primeras ~2,500 chars de cada uno de los 30 documentos abiertos semánticamente. |
| `README_COWORK.md` | (este) | Esta guía. |

---

## 2. Cómo leer el dataset consolidado

```python
import json
with open("discovery_forense/phase6_consolidated.json") as f:
    items = json.load(f)

# Filtrar solo P0
p0 = [i for i in items if i["priority"] == "P0"]
print(f"P0 docs: {len(p0)}")

# Filtrar por fuente
s3_docs = [i for i in items if i["fuente"] == "s3"]
dropbox_docs = [i for i in items if i["fuente"] == "dropbox"]
```

Cada item tiene la estructura:
```json
{
  "id": "drive_file_id | notion_page_id | dropbox:/path | url",
  "name": "nombre del archivo/página",
  "fuente": "drive | notion | github | dropbox | s3",
  "mimeType": "...",
  "modifiedTime": "ISO timestamp",
  "url": "URL accesible",
  "priority": "P0 | P1 | P2 | P3",
  "score": 0-26,
  "kw_matches": ["familia/keyword", ...]
}
```

---

## 3. Credenciales necesarias para Fase III

Para acceder a las fuentes que descubrí, **necesitas pedirle al usuario las mismas credenciales que me dio a mí** (yo ya las eliminé del sandbox):

| Fuente | Variable de entorno | Obtenida de |
|---|---|---|
| **AWS S3** (CRISOL planes, modelos 3D Kukulkán) | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` | Pedir a Alfredo |
| **Dropbox** (SOP/EPIA .docx fundacionales) | `DROPBOX_REFRESH_TOKEN`, `DROPBOX_APP_KEY`, `DROPBOX_APP_SECRET` | Pedir a Alfredo |
| **Apify** (scrapers OSINT) | `APIFY_TOKEN` | Pedir a Alfredo |
| **Asana** (proyectos hivecom.mx) | `ASANA_TOKEN` | Pedir a Alfredo |
| **Notion** (MCP) | (configurado en Manus) | Verificar con `manus-mcp-cli tool list --server notion` |
| **Drive** (gws CLI) | (configurado en Manus) | Verificar con `gws drive --help` |
| **GitHub** (gh CLI) | (configurado en Manus) | Verificar con `gh auth status` |

---

## 4. Buckets S3 magna identificados

Si tienes credenciales AWS:

```bash
# Planes maestros de Mena Baduy / CRISOL
aws s3 ls s3://operacion-doble-eje/dossier-legal/mena-baduy/
aws s3 ls s3://crisol8-analysis/

# Modelos 3D estadio Kukulkán (81 GB — solo descargar lo necesario)
aws s3 ls s3://manus-agent-bucket-evetrszg7y4om553/

# Investigación tapetes/interiorismo
aws s3 ls s3://alfombras-comparacion/
aws s3 ls s3://malmo-tapete-search/
```

---

## 5. Top 10 documentos a abrir primero

Ordenados por score (cuántas familias semánticas matchearon):

1. `📘 MAOC - Documento Maestro` — Notion — **SSOT propuesto**
2. `Plan de Construcción: El Monstruo v0.1` — Notion
3. `repaldo sop v3 181025.txt` — Drive — **respaldo bruto SOP v3**
4. `Biblia de MCPs para El Monstruo v1.0` — Notion
5. `EPIA_fundacional_completo_v1` — Drive
6. `Arquitectura de Absorción Soberana — Versión Definitiva (GPT-5.4)` — Notion
7. `ENTREGABLE 2 — DOCUMENTO FUNDACIONAL SOP.docx` — Dropbox
8. `EPIA — DOCUMENTO FUNDACIONAL MAESTRO.docx` — Dropbox
9. `biblias_v41_AUDITED_69_gradeA.zip` — Drive — **69 herramientas grade A sin indexar**
10. `MANUS OS: PLAN MAESTRO UNIFICADO (v5.0)` — Notion

---

## 6. Conflictos pendientes de resolver

1. **SOP/EPIA fragmentados:** Hay 3 versiones del SOP (Drive `.md`, Drive `.txt v3 bruto`, Dropbox `.docx`). Hay que deduplicar con GPT-5.4.
2. **El ZIP de 69 biblias** no está descomprimido — es un agujero negro de conocimiento que no podemos consultar agéntcamente.
3. **CRISOL en S3 ≠ CRISOL en GitHub:** El repo `crisol-8` privado tiene código, pero los planes maestros están en S3. Hay que migrar.

---

## 7. Recomendación de orquestación

Si vas a hacer la Canonización, propongo:

1. **Tú (Hilo A)** descomprimes las 69 biblias del ZIP y las publicas en Notion como sub-páginas indexables. Yo (Hilo B) no debería tocar Notion en escritura porque es zona compartida.
2. **Yo (Hilo B)** descargo las versiones de SOP/EPIA de Drive y Dropbox y las paso a un script de diff con GPT-5.4 para identificar deltas.
3. **Tú (Hilo A)** migras los planes de CRISOL desde S3 al repo privado `crisol-8` de GitHub.
4. **Ambos** consolidamos en el `MAOC - Documento Maestro` de Notion como SSOT final.

Coordínate conmigo vía `bridge/manus_to_cowork.md` y `bridge/cowork_to_manus.md`.

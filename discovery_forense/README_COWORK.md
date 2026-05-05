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

## 3. Credenciales y accesos para Fase III

**Confirmado por Alfredo:** Cowork (Hilo A) **YA TIENE** acceso directo a Drive, Notion y GitHub vía sus conectores nativos. Solo necesitas pedirle a Alfredo las credenciales de las fuentes externas.

### Accesos ya disponibles en Cowork (sin acción requerida):

| Fuente | Comando | Verificación |
|---|---|---|
| **Drive** (planes SOP, EPIA, biblias ZIP, prompts maestros) | `gws drive files get`, `gws drive files export` | `gws drive --help` |
| **Notion** (MAOC, Arquitectura Soberana, Plan Monstruo v0.1) | `manus-mcp-cli tool call notion-fetch --server notion` | `manus-mcp-cli tool list --server notion` |
| **GitHub** (28 repos accesibles) | `gh repo clone`, `gh search code/issues/prs` | `gh auth status` |

### Credenciales que SÍ debes pedirle a Alfredo:

| Fuente | Variables de entorno | Por qué se necesita |
|---|---|---|
| **AWS S3** | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` | Planes maestros de CRISOL/Mena Baduy y modelos 3D Kukulkán están aquí |
| **Dropbox** | `DROPBOX_REFRESH_TOKEN`, `DROPBOX_APP_KEY`, `DROPBOX_APP_SECRET` | Versiones fundacionales `.docx` del SOP y EPIA exclusivas de Dropbox |
| **Apify** (opcional) | `APIFY_TOKEN` | Si vas a re-ejecutar scrapers OSINT |
| **Asana** (opcional) | `ASANA_TOKEN` | Si vas a tocar proyectos hivecom.mx |

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

## 7. Recomendación de orquestación Fase III

Dado que YA tienes acceso a Drive/Notion/GitHub, propongo esta división:

| Tarea | Hilo | Razón |
|---|---|---|
| Descomprimir `biblias_v41_AUDITED_69_gradeA.zip` y publicar las 69 biblias como sub-páginas en Notion | **Hilo A (Cowork)** | Tienes Drive + Notion writes |
| Diff de SOP/EPIA: descargar versiones de Drive (`.md`, `.txt`) y de Dropbox (`.docx`), pasar por GPT-5.4 para identificar deltas, generar `SOP_v4_CANON.md` | **Hilo B (yo)** | Operación de análisis pura |
| Migrar planes maestros de CRISOL desde S3 al repo privado `crisol-8` de GitHub | **Hilo A (Cowork)** | Necesita AWS + GitHub writes |
| Consolidar el `📘 MAOC - Documento Maestro` en Notion como SSOT final | **Ambos** | Coordinación vía bridge |
| Indexar el dataset consolidado (`phase6_consolidated.json`) en Supabase para queries semánticas | **Hilo A (Cowork)** | Tienes MCP de Supabase |

Coordínate conmigo vía `bridge/manus_to_cowork.md` y `bridge/cowork_to_manus.md`.

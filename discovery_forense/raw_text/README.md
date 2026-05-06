# raw_text — Dataset normalizado para indexación semántica

**Generado:** 2026-05-06 por Manus (Hilo B)
**Propósito:** Dataset curado de planes, roadmaps, cánones, rankings, resúmenes y reportes del corpus del Monstruo, normalizado a Markdown plano para indexar en Supabase pgvector y consultar semánticamente desde Cowork (Hilo A).

## Métricas

| Métrica | Valor |
|---|---|
| Total archivos | 232 |
| Tamaño normalizado | 3.9 MB |
| Tamaño original | ~18 MB |
| Fuentes | Dropbox (169) + S3 (65 efectivos, 4 excluidos) |

## Clasificación por categoría

| Categoría | Archivos |
|---|---|
| reporte | 77 |
| resumen | 22 |
| plan | 21 |
| canon (SOP/EPIA/biblias) | 17 |
| ranking | 6 |
| roadmap | 1 |
| otro | 90 |

## Estructura

```
raw_text/
├── README.md
├── manifest_unified.json        # Manifest maestro (238 entries)
├── _REDACTIONS_REPORT.json      # Reporte de secrets redactados
├── dropbox/
│   ├── manifest_dropbox.json
│   └── normalized_md/           # 164 archivos .md
└── s3/
    ├── manifest_s3.json
    ├── crisol8-evidence/normalized_md/
    ├── crisol8-raw-scrapes/normalized_md/
    └── alfombras-comparacion/normalized_md/
```

## Schema del manifest

Cada entrada en `manifest_unified.json`:

```json
{
  "source_system": "dropbox" | "s3",
  "source_path": "/ruta/original/en/fuente.docx",
  "size_bytes": 12345,
  "sha256_16": "abc123...",
  "ext_original": ".docx",
  "stored_normalized": "dropbox/normalized_md/archivo.md",
  "modified": "2026-04-15T10:00:00",
  "category": "plan" | "canon" | "ranking" | "resumen" | "reporte" | "roadmap" | "otro",
  "bucket": "crisol8-evidence",
  "excluded": true,
  "excluded_reason": "..."
}
```

## Conversiones aplicadas

- `.md` / `.txt` → copia directa a UTF-8
- `.docx` → texto plano con `python-docx` (preserva headings y tablas)
- `.pdf` → texto plano con `pdftotext -layout`
- `.json` → preview JSON formateado en bloque markdown

## Excluidos del repo

4 archivos JSON de scrapes brutos (>1MB cada uno, ~38MB total) fueron descargados pero excluidos del normalizado por no aportar contexto curado:
- `crisol8/20260327/bm_export_complete.json`
- `raw-data/20260327/bm_export_complete.json`
- `crisol8/20260327/apify_all_results.json`
- `raw-data/20260327/apify_social_results.json`

Quedan registrados en el manifest con `excluded: true`.

## Redacción de secrets

GitHub Push Protection detectó un Apify token en uno de los `.md` originales del corpus. Se aplicó un redactor automático con 16 patrones (Apify, OpenAI, Anthropic, Langfuse, AWS, GitHub PAT, Dropbox, Perplexity, Google, XAI, ElevenLabs, Supabase, JWT largos, etc).

**Resultado:**
- Archivos escaneados: 319
- Archivos modificados: 2
- Total redacciones: 6 (4 LONG_JWT + 2 APIFY_TOKEN)

Detalle completo en `_REDACTIONS_REPORT.json`.

## Para Cowork (Hilo A) — consumo

Este dataset está diseñado para ser consumido por la **Tarea 3** (indexar en Supabase pgvector):

1. Leer cada archivo en `dropbox/normalized_md/` y `s3/*/normalized_md/`
2. Chunk a ~500 tokens con overlap 50
3. Generar embeddings con `text-embedding-3-small` (dim 1536)
4. Insertar en tabla `discovery_index` con metadata del manifest
5. Cowork luego consulta semánticamente sin necesitar S3/Dropbox directos

## Generadores (en sandbox de Manus, reproducibles)

- `/tmp/dbx_inventory.py` — inventario Dropbox
- `/tmp/dbx_download_normalize.py` — descarga + normalización Dropbox
- `/tmp/s3_download_normalize.py` — descarga + normalización S3
- `/tmp/build_unified_manifest.py` — manifest unificado
- `/tmp/redact_secrets_v2.py` — redactor de secrets

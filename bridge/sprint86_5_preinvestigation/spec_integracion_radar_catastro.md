> Hilo Manus Catastro · 2026-05-04 · Standby Productivo
> Entrega C: Spec Integración Radar ↔ Catastro
> Validación tiempo real ejecutada el 2026-05-04. Basado en Addendum 86-Catastro-002 y arquitectura de absorción pasiva.

---

## 1. Decisión Arquitectónica (Absorción Pasiva)

El Catastro adopta una arquitectura **HÍBRIDA** para la Macroárea 11 (Open Source Repos).
- **El Radar** (`alfredogl1804/biblia-github-motor`) mantiene autonomía total: corre su propio cron, descubre repos, y genera reportes Markdown en Google Drive.
- **El Catastro** actúa como consumidor pasivo (downstream): no reescribe al Radar ni interfiere con su pipeline. Simplemente ingiere sus hallazgos de forma estructurada para poblar la sexta tabla (`catastro_repos`).

## 2. Schema: Sexta Tabla `catastro_repos`

Para persistir los repositorios descubiertos, se requiere una nueva tabla relacional conectada al ecosistema.

```sql
-- scripts/017_sprint86_5_catastro_repos.sql
CREATE TABLE catastro_repos (
    id TEXT PRIMARY KEY,                  -- ej. "github:Significant-Gravitas/AutoGPT"
    nombre TEXT NOT NULL,                 -- "AutoGPT"
    proveedor TEXT NOT NULL,              -- "Significant-Gravitas"
    url TEXT NOT NULL,                    -- "https://github.com/..."
    stars_count INTEGER DEFAULT 0,
    last_release_tag TEXT,
    last_release_date TIMESTAMPTZ,
    license TEXT,
    topics JSONB DEFAULT '[]',            -- ["agents", "llm", "autonomous"]
    model_card_url TEXT,                  -- Si es HuggingFace
    radar_discovered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    radar_report_ref TEXT,                -- Referencia al doc original del Radar
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_catastro_repos_stars ON catastro_repos(stars_count DESC);
CREATE INDEX idx_catastro_repos_topics ON catastro_repos USING GIN (topics);
```

## 3. Cliente de Ingesta (`radar_ingest.py`)

El cliente será una nueva "fuente" en `kernel/catastro/sources/radar_ingest.py`, pero con una mecánica distinta a OpenRouter o Lmarena. En lugar de consumir una API JSON, debe consumir los reportes del Radar.

**El problema de la 27va Semilla:**
Los reportes del Radar son generados por LLMs en Markdown. Extraer datos con regex crudas (ej. `r"Stars: (\d+)"`) es inestable y frágil (lección aprendida en la semilla 27).

**Solución Estructurada:**
El `radar_ingest.py` usará el **Magna Classifier** (o un LLM-as-parser ligero como `gpt-4.1-mini`) con *Structured Outputs* (Pydantic schema) para leer el Markdown del Radar y devolver un JSON estricto garantizado, evitando regex por completo.

```python
# Pseudo-código de la ingesta
class RadarIngestor:
    def ingest_latest_report(self, markdown_content: str) -> list[CatastroRepo]:
        # 1. Usar LLM Structured Output para parsear el markdown de forma segura
        extracted_repos = self.llm_parser.parse(
            text=markdown_content, 
            response_model=List[CatastroRepo]
        )
        
        # 2. Enriquecer con la API de GitHub real (para stars actualizadas)
        for repo in extracted_repos:
            repo.stars_count = self.github_client.get_stars(repo.url)
            
        return extracted_repos
```

## 4. Eventos Automáticos (`catastro_eventos`)

La ingesta del Radar debe emitir eventos en la quinta tabla (`catastro_eventos`) para que el Embrión (y el usuario) sean notificados de descubrimientos críticos.

1. **`new_open_source_model_detected`**:
   - **Trigger:** El Radar reporta un repo de HuggingFace/GitHub que no existía en `catastro_repos`.
   - **Payload:** URL, descripción corta, y topics.
   - **Acción downstream:** El Embrión puede decidir si crear un ticket para probarlo.

2. **`open_source_release_v2`**:
   - **Trigger:** Un repo ya existente en `catastro_repos` cambia su `last_release_tag` (ej. de `v1.5.0` a `v2.0.0`).
   - **Payload:** Diff de versiones y link al release notes.

## 5. Riesgos Identificados

1. **Latencia de sincronización:** Al ser pasivo, el Catastro va un paso atrás del Radar. Si el Radar falla silenciosamente, el Catastro simplemente dejará de actualizar repos sin arrojar error. *Mitigación:* Alerta de "stale data" si no hay ingesta del Radar en 7 días.
2. **Rate Limits de GitHub:** Enriquecer 50 repos descubiertos consultando la API de GitHub puede golpear los límites de la `GITHUB_TOKEN`. *Mitigación:* Batching y uso condicional (solo actualizar si el repo fue marcado como modificado por el Radar).
3. **Duplicación de identidades:** Un mismo proyecto puede tener un repo en GitHub y otro en HuggingFace. *Mitigación:* El schema usa `id` compuesto (`github:owner/repo` vs `hf:owner/repo`), pero el LLM parser debe intentar linkearlos en un campo `related_urls`.

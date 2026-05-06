# Sprint 89 — Catastros 0: extensión a Suppliers Humanos + Herramientas AI Especializadas

**Owner:** Hilo Ejecutor (Manus)
**Zona protegida:** `kernel/catastro/`
**ETA estimada:** 8-12h reales con Apéndice 1.3 factor velocity 5-8x
**Bloqueos:** ninguno
**Prerequisito:** v1.2 doc canónico en `main` (✅ commit `31166ab`), DSC-G-007 firmado (✅ commit `c7bc034`)
**Dependencias:** ninguna externa, paralelizable con Sprint 88 y con Sprint Catastro-A

---

## 1. Contexto

v1.2 del documento de visión + DSC-G-007 firman el patrón de **3 Catastros paralelos** como motor de orquestación del Monstruo:

| Catastro | Estado pre-Sprint 89 |
|---|---|
| **Catastro de Modelos LLM** | ✅ Existente desde Sprint 86.x (50+ modelos rankeados, anti-gaming, macroáreas) |
| **Catastro de Suppliers Humanos** | ❌ NO existe — solo concepto en v1.2 |
| **Catastro de Herramientas AI Especializadas** | ❌ NO existe — solo concepto en v1.2 |

Este sprint construye la **infraestructura técnica** de los dos Catastros nuevos, **sin poblarlos con datos reales** (eso es el Sprint Catastro-A en paralelo en Hilo Catastro).

La idea: cuando este sprint cierre, los 3 motores de orquestación están listos como código. El sprint Catastro-A los puebla con suppliers reales de Mérida + herramientas AI verticales canónicas. Cuando ambos cierran, los Catastros nuevos están operativos.

---

## 2. Objetivo único del sprint

Extender la infraestructura del Catastro existente para soportar **3 dominios distintos de orquestación** bajo el mismo patrón canónico (ranking, anti-gaming, macroáreas, override manual posible, manifestación contextual, FinOps trackeable).

Los 2 Catastros nuevos comparten 80% del código del Catastro de Modelos LLM existente — el sprint extrae lo común y especializa lo distinto.

---

## 3. Bloques del sprint

### 3.A — Refactor del Catastro existente para extensibilidad

Antes de agregar Catastros nuevos, separar la lógica común del Catastro de LLMs.

**3.A.1 — Identificar lo común vs lo específico**

Lectura del código actual de `kernel/catastro/` para mapear:

- **Común a los 3 Catastros:** patrón de ranking compuesto, anti-gaming v1 + v2, macroáreas, override manual, audit log, manifestación contextual, FinOps tracking
- **Específico de cada Catastro:**
  - LLMs: `confidentiality_tier`, sub-rol macroárea (Razonamiento, Coding, etc.), prohibiciones de API (`temperature` con GPT-5.5 etc.)
  - Suppliers: `coverage_jurisdiccional`, `capacidad_disponible`, `SLA`, `precio_base`, `categoria_servicio` (arquitecto, valuador, fotógrafo, abogado, contratista...)
  - Herramientas AI: `categoria_capability` (rendering, video gen, voice, parsing...), `modelo_subyacente`, `pricing_unidad` (per-image, per-second, per-token), `latencia_promedio`, `quality_score`

**3.A.2 — Extraer interfaz base `CatastroBase`**

Crear `kernel/catastro/base.py` con clase `CatastroBase[T]` (genérica) que provee:

- `rank(filters: dict) -> List[T]`
- `select_best(filters: dict, override: Optional[str] = None) -> T`
- `audit_use(item_id: str, run_id: str, cost: float)`
- `health_metrics() -> CatastroHealth`
- Hooks para anti-gaming v1 + v2

`CatastroBase[ModeloLLM]` ya existe implícitamente. El refactor lo hace explícito sin cambiar comportamiento del Catastro de Modelos.

**3.A.3 — Tests de regresión para Catastro de Modelos**

Antes de cambiar nada, fijar suite de tests acumulada para asegurar que el refactor no rompe el Catastro existente. Si hay <10 tests del Catastro actual, agregar más antes de tocar.

Criterio de cierre del bloque A: refactor con tests verde + Catastro de Modelos LLM funciona idéntico.

### 3.B — Catastro de Suppliers Humanos

**3.B.1 — Esquema de datos**

Crear migración Supabase nueva (siguiente número disponible, probablemente 029 o 030 después de la 028 del Sprint 87.2).

Tabla `suppliers_humanos`:

```sql
CREATE TABLE suppliers_humanos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre TEXT NOT NULL,
    razon_social TEXT,
    categoria_servicio TEXT NOT NULL CHECK (categoria_servicio IN (
        'arquitecto', 'valuador', 'fotografo', 'drone_operator',
        'abogado_fideicomiso', 'contratista', 'aseguradora',
        'verificador_title', 'cgi_artist', 'interior_designer',
        'photographer', 'auditor_smart_contract', 'kyc_provider', 'otro'
    )),
    cobertura_jurisdiccional TEXT[] NOT NULL,
    capacidad_disponible_pct INT CHECK (capacidad_disponible_pct BETWEEN 0 AND 100),
    sla_horas INT,
    precio_base_usd NUMERIC(10,2),
    rating_compuesto NUMERIC(3,1) CHECK (rating_compuesto BETWEEN 0 AND 100),
    anti_gaming_flags JSONB DEFAULT '[]'::jsonb,
    contacto JSONB,
    notas TEXT,
    activo BOOLEAN DEFAULT true,
    creado_en TIMESTAMPTZ DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_suppliers_categoria ON suppliers_humanos(categoria_servicio) WHERE activo = true;
CREATE INDEX idx_suppliers_jurisdiccion ON suppliers_humanos USING GIN(cobertura_jurisdiccional) WHERE activo = true;
```

Tabla `suppliers_humanos_audit_log` para trackear uso por run (analoga a `e2e_step_log`).

**3.B.2 — Implementación del Catastro de Suppliers**

Crear `kernel/catastro/suppliers/` con:
- `models.py` — Pydantic class `SupplierHumano(BaseModel)`
- `repository.py` — acceso a Supabase
- `ranker.py` — implementa `CatastroBase[SupplierHumano]` con scoring específico
- `anti_gaming.py` — heurísticas para detectar suppliers que inflan ratings
- `__init__.py` — singleton del Catastro

Endpoint REST `kernel/api/v1/catastro/suppliers/`:
- `GET /list` con filtros (categoria, jurisdiccion, capacidad_min)
- `GET /select-best` invocable desde Pipeline E2E
- `GET /health` para Cockpit

**3.B.3 — Tests del Catastro de Suppliers**

Mínimo 12 tests cubriendo: ranking básico, filtros por jurisdicción, anti-gaming flags, override manual, audit log, health metrics.

Criterio de cierre del bloque B: tests verde + endpoint REST responde + Catastro vacío (sin data — la data viene de Sprint Catastro-A).

### 3.C — Catastro de Herramientas AI Especializadas

**3.C.1 — Esquema de datos**

Tabla `herramientas_ai_especializadas`:

```sql
CREATE TABLE herramientas_ai_especializadas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre TEXT NOT NULL,
    proveedor TEXT NOT NULL,
    categoria_capability TEXT NOT NULL CHECK (categoria_capability IN (
        'rendering_interior', 'rendering_exterior', 'rendering_3d_spatial',
        'video_generation', 'voice_synthesis', 'voice_cloning',
        'document_parsing', 'image_to_3d', 'image_variations',
        'audio_generation', 'transcription', 'embeddings_multimodal', 'otro'
    )),
    api_endpoint TEXT,
    auth_type TEXT,
    pricing_unidad TEXT NOT NULL,
    pricing_costo_unidad_usd NUMERIC(10,4),
    latencia_promedio_ms INT,
    quality_score NUMERIC(3,1) CHECK (quality_score BETWEEN 0 AND 100),
    rating_compuesto NUMERIC(3,1) CHECK (rating_compuesto BETWEEN 0 AND 100),
    anti_gaming_flags JSONB DEFAULT '[]'::jsonb,
    notas TEXT,
    activo BOOLEAN DEFAULT true,
    creado_en TIMESTAMPTZ DEFAULT NOW(),
    actualizado_en TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_herramientas_capability ON herramientas_ai_especializadas(categoria_capability) WHERE activo = true;
```

Tabla `herramientas_ai_audit_log`.

**3.C.2 — Implementación**

Mismo patrón que 3.B con:
- `kernel/catastro/herramientas_ai/`
- `models.py`, `repository.py`, `ranker.py`, `anti_gaming.py`, `__init__.py`
- Endpoint REST `kernel/api/v1/catastro/herramientas_ai/`

Adicional: capa de **abstracción de API** porque cada herramienta tiene su API distinta. Crear `kernel/catastro/herramientas_ai/adapters/` con un adapter por proveedor (ej. `runway_adapter.py`, `roomgpt_adapter.py`). El Catastro selecciona la herramienta + el adapter correspondiente expone interface uniforme `generar(prompt, **kwargs) -> Resultado`.

**3.C.3 — Tests + smoke real**

Mínimo 12 tests. Smoke productivo con UNA herramienta real (ej. RoomGPT con free tier) para validar que el adapter funciona end-to-end.

Criterio de cierre del bloque C: tests verde + smoke con 1 herramienta real funciona.

### 3.D — Integración con Pipeline E2E

**3.D.1 — Pipeline puede invocar los 3 Catastros**

El Pipeline E2E del Sprint 87.x invoca el Catastro de Modelos LLM en cada step. Ahora debe poder invocar también:

- Catastro de Suppliers cuando un step requiere servicio humano (ej. step `legal_review` en Tier Regulated Financial pide abogado de fideicomiso)
- Catastro de Herramientas AI cuando un step requiere capability vertical (ej. step `componentes` invoca Catastro de Herramientas para escoger renderer si la empresa-hija tiene componente visual fuerte)

Archivos a tocar:
- `kernel/e2e/pipeline.py` — métodos `select_supplier(categoria, jurisdiccion)` y `select_tool(categoria_capability, pricing_max)`
- Tests de integración del Pipeline con los 3 Catastros

**3.D.2 — Endpoint Cockpit "Salud de los 3 Catastros"**

Crear endpoint agregador `GET /v1/catastro/health-summary` que devuelve métricas de los 3 Catastros en una vista unificada para el Cockpit.

```json
{
  "catastros": {
    "modelos_llm": { "total": 50, "activos": 47, "uso_24h": 1240, "costo_24h_usd": 8.34 },
    "suppliers_humanos": { "total": 0, "activos": 0, "uso_24h": 0, "costo_24h_usd": 0 },
    "herramientas_ai": { "total": 0, "activos": 0, "uso_24h": 0, "costo_24h_usd": 0 }
  }
}
```

(Los `0` son porque Sprint Catastro-A llena los datos en paralelo.)

---

## 4. Magnitudes esperadas

- ~2,000 LOC nuevas (incluyendo refactor del Catastro existente)
- 2 migraciones Supabase nuevas
- ~25 archivos nuevos + ~5 modificados (refactor)
- ~30 tests nuevos
- 1 smoke productivo con 1 herramienta AI real

---

## 5. Disciplina aplicada

- ✅ Capa Memento: si un Catastro no responde, el Pipeline no se cae — degradación graceful
- ✅ Brand DNA: errores `catastro_suppliers_select_*_failed`, `catastro_herramientas_ai_invoke_*_failed`
- ✅ Anti-Dory: validación realtime de versiones de SDK de cada herramienta AI (DSC-V-002)
- ✅ Validación con 6 Sabios canónicos (DSC-V-001) si surge duda arquitectónica

---

## 6. Cierre formal

Cuando los 4 bloques cierren verde, Hilo Ejecutor declara:

> 🏛️ **Catastros v2.0 — DECLARADOS** (3 Catastros paralelos operativos, código listo para datos)

Y reporta al bridge con tabla de evidencia.

---

## 7. Coordinación con Sprint Catastro-A (Hilo Catastro paralelo)

- Sprint 89 (Ejecutor) construye la infra técnica de los 2 Catastros nuevos
- Sprint Catastro-A (Catastro) puebla las tablas con suppliers reales + herramientas AI canónicas
- Cuando ambos cierran, los 3 Catastros operan con datos
- Paralelismo zonificado puro: Sprint 89 toca solo `kernel/`, Sprint Catastro-A toca solo MCPs externos + investigación + insertar via API

---

— Cowork (Hilo A), spec preparada 2026-05-06.
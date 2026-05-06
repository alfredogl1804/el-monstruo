# Sprint Catastro-A — Investigación + poblamiento inicial de Catastros nuevos

**Owner:** Hilo Catastro (Manus)
**Zona protegida:** fuera de `kernel/` — MCPs Drive/Notion/GitHub/Supabase + investigación realtime
**ETA estimada:** 8-12h reales con Apéndice 1.3 factor velocity
**Bloqueos:** ninguno (paralelizable con Sprint 89 del Hilo Ejecutor)
**Prerequisito:** v1.2 doc canónico + DSC-G-007 firmado (✅)
**Dependencias para inserción de datos:** Sprint 89 (Hilo Ejecutor) debe haber creado las tablas Supabase. Sprint Catastro-A puede arrancar con investigación sin esperar — la inserción de datos se sincroniza al final cuando ambos sprints converjan.

---

## 1. Contexto

Sprint 89 del Hilo Ejecutor construye la **infraestructura técnica** de los 2 Catastros nuevos (Suppliers Humanos + Herramientas AI Especializadas). Este Sprint Catastro-A los **puebla con datos reales canónicos** vía investigación realtime + curaduría.

Sin datos, los Catastros son tablas vacías. Sin Catastros, las empresas-hijas que los necesiten (Marketplace de Interiorismo, CIP cuando converja, BioGuard cuando arranque) no pueden invocarlos. **Este sprint es precondición de las empresas-hijas Tier Marketplace y Tier Regulated Financial.**

---

## 2. Objetivo único del sprint

Poblar los 2 Catastros nuevos con datos canónicos verificados realtime:

- **Catastro de Suppliers Humanos:** mínimo 30 suppliers reales con cobertura de las categorías canónicas (arquitectos, valuadores, fotógrafos, abogados de fideicomiso, contratistas, drone operators, photographers, interior designers, auditors smart contracts, kyc providers), con foco geográfico inicial en Sureste de México (Yucatán, Quintana Roo, Campeche) per DSC-CIP-005.

- **Catastro de Herramientas AI Especializadas:** mínimo 25 herramientas canónicas con cobertura de las 13 categorías de capability (rendering interior/exterior/spatial, video gen, voice synthesis/cloning, document parsing, image to 3D, image variations, audio gen, transcription, embeddings multimodal), con scoring real verificado contra APIs oficiales.

Cada entry tiene rating compuesto realista, no inflado. Anti-gaming desde día 1.

---

## 3. Bloques del sprint

### 3.A — Investigación de Suppliers Humanos en Sureste de México

**3.A.1 — Mapeo por categoría canónica**

Para cada categoría definida en el schema del Sprint 89 (`categoria_servicio`), investigar candidatos reales:

| Categoría | Investigación realtime |
|---|---|
| arquitecto | Colegio de Arquitectos Yucatán, listado SAT registro de profesionistas, Google Maps reviews + portfolios visibles |
| valuador certificado | Sociedad Hipotecaria Federal (SHF) — listado público de valuadores autorizados, INDAABIN |
| fotografo arquitectónico | Instagram + Behance + portfolios locales, reviews verificables |
| drone_operator | DGAC México registro de pilotos certificados |
| abogado_fideicomiso | Colegio Nacional del Notariado Mexicano, listado de notarios en Yucatán + expertise CNBV/SHCP/Banxico |
| contratista | Cámara Mexicana de la Industria de la Construcción (CMIC) Yucatán |
| aseguradora | AMIS — aseguradoras autorizadas con productos de inmuebles |
| verificador_title | Notarios certificados que ofrecen verificación de title, registro público de la propiedad |
| interior_designer | AMDI Asociación Mexicana de Diseñadores de Interiores, portfolios reales |
| cgi_artist | Behance + ArtStation talento mexicano |
| auditor_smart_contract | Trail of Bits, OpenZeppelin, ConsenSys Diligence — firmas con presencia LATAM |
| kyc_provider | Trulioo, Onfido, Veriff, Mati — listado de proveedores con cobertura MX |

**3.A.2 — Datos a capturar por supplier**

Por cada candidato:
- `nombre`, `razon_social` (verificar con SAT si aplica)
- `categoria_servicio` (de la lista canónica)
- `cobertura_jurisdiccional` array (`['MX-YUC']`, `['MX-YUC', 'MX-QR']`, etc.)
- `capacidad_disponible_pct` — estimación basada en visibilidad pública (proyectos en curso)
- `sla_horas` — tiempo de respuesta promedio reportado o estimado
- `precio_base_usd` — rango si está público
- `rating_compuesto` 0-100 — composite de:
  - Calidad reputacional (reviews, antiguedad, casos verificados): 40%
  - Cobertura geográfica relevante: 20%
  - Capacidad disponible: 20%
  - Pricing competitivo: 20%
- `contacto` JSONB con email/teléfono/web
- `notas` — caveats del scoring, fuentes consultadas
- `anti_gaming_flags` — array vacío inicial, populado después por Sprint Catastros 0 si Manus detecta inconsistencias

Mínimo **30 suppliers totales** distribuidos para cubrir todas las categorías.

**3.A.3 — Verificación anti-bullshit**

Cada entry tiene que pasar:
- Email/teléfono verificado funcional (no placeholder)
- Página web o portfolio o registro público verificable
- Coincidencia entre razón social registrada y nombre comercial
- Sin overlap suspicious entre suppliers (ej: 3 fotógrafos con misma dirección probablemente son 1 con múltiples cuentas inflando — flag)

**3.A.4 — Inserción**

Cuando Sprint 89 cierre con tablas creadas, Hilo Catastro hace bulk insert vía Supabase MCP. Audit log con commit del CSV/JSON fuente para traceability.

### 3.B — Investigación de Herramientas AI Especializadas

**3.B.1 — Mapeo por categoría de capability**

| Categoría | Candidatos canónicos a investigar realtime (mayo 2026) |
|---|---|
| rendering_interior | RoomGPT 4, Modsy AI, Coohom Render Cloud, Decoratify, AI HomeDesign, Spline AI, Polycam (NeRF) |
| rendering_exterior | TwoMorrow Architect, Lumion AI, Enscape AI, D5 Render |
| rendering_3d_spatial | Luma AI, Polycam, Spline 3D, Niantic Spatial SDK |
| video_generation | Runway Gen-4, Sora 2, Veo 3, Kling AI, Pika 2.0 |
| voice_synthesis | ElevenLabs, OpenAI Voice, Hume AI, PlayHT |
| voice_cloning | ElevenLabs Voice Lab, Resemble AI |
| document_parsing | LlamaParse, Unstructured.io, Reducto, AWS Textract, Google DocAI |
| image_to_3d | Kaedim, Meshy AI, CGTrader AI, Tripo AI |
| image_variations | Krea AI, Ideogram 3, Recraft V3, Leonardo AI |
| audio_generation | Suno V4, Udio, AudioCraft, ElevenLabs Sound Effects |
| transcription | Whisper API, Deepgram Nova-3, AssemblyAI Universal |
| embeddings_multimodal | OpenAI text-embedding-3-large, Voyage AI, Cohere Embed v4, Jina v3 |

**3.B.2 — Datos a capturar por herramienta**

Por cada herramienta:
- `nombre`, `proveedor`
- `categoria_capability`
- `api_endpoint` (verificado contra docs oficiales realtime — anti-Dory per DSC-V-002)
- `auth_type` (API key, OAuth2, etc.)
- `pricing_unidad` (per-image, per-second, per-token, per-call)
- `pricing_costo_unidad_usd` (verificado contra pricing actual)
- `latencia_promedio_ms` — investigado en docs o foros, o estimado por categoría
- `quality_score` 0-100 — composite de:
  - Calidad output (benchmarks, reviews recientes): 40%
  - Latencia: 20%
  - Costo competitivo: 20%
  - Madurez API + estabilidad: 20%
- `rating_compuesto` 0-100 — meta-score que pesa quality_score con popularidad y trayectoria
- `notas` — caveats, ej. "RoomGPT mejor para variaciones rápidas, débil en hi-fi", "Coohom mejor para final fotorrealista pero requiere modelos 3D pre-cargados"

Mínimo **25 herramientas totales** distribuidas para cubrir todas las categorías.

**3.B.3 — Validación realtime obligatoria (DSC-V-002 + DSC-G-005)**

Antes de insertar, Manus verifica para cada herramienta:
- Endpoint API responde (curl o playground)
- Pricing actual no obsoleto
- Versión vigente del modelo subyacente
- Si requiere waitlist, marcarlo en notas

NO usar conocimiento de entrenamiento — verificar contra realidad presente.

**3.B.4 — Inserción**

Mismo patrón que 3.A.4 — bulk insert vía Supabase MCP cuando Sprint 89 tenga tablas listas.

### 3.C — Documentación operativa

**3.C.1 — Reporte de poblamiento al bridge**

Crear `bridge/cowork_to_manus_REPORTE_POBLAMIENTO_CATASTROS_<fecha>.md` con:
- Counts por categoría
- Top 5 entries por rating_compuesto en cada Catastro
- Caveats detectados durante investigación
- Anti-gaming flags pre-detectados
- Fuentes consultadas (links verificables)

**3.C.2 — Skill canónico de mantenimiento**

Crear `skills/catastros-mantenimiento/SKILL.md` con instrucciones de cómo agregar/actualizar entries futuros. Incluir checklist de validación realtime para cada nuevo supplier o herramienta.

### 3.D — Cross-link con la Capilla de Decisiones

**3.D.1 — Manifest update**

Actualizar `discovery_forense/PROJECT_MANIFESTS/marketplace-muebles.md` y `roche-bobois-alfombras.md` agregando referencia a DSC-X-006 (Convergencia Diferida) + lista de suppliers integrados desde el nuevo Catastro.

Actualizar `discovery_forense/MATRIZ_CRUCES_PROYECTOS.md` agregando los 2 Catastros nuevos como componentes compartibles de alta prioridad (junto a los 6 ya identificados).

---

## 4. Magnitudes esperadas

- 30+ suppliers humanos investigados + insertados
- 25+ herramientas AI especializadas investigadas + insertadas
- 1 reporte de poblamiento (~5KB markdown)
- 1 skill canónico de mantenimiento
- 2-3 manifests actualizados
- ~5-10 commits en bridge + manifests + skills

---

## 5. Disciplina aplicada

- ✅ DSC-G-005 + DSC-V-002: validación realtime obligatoria contra fuentes oficiales
- ✅ DSC-V-001: si hay duda sobre quality_score de una herramienta AI, consultar a los 6 Sabios canónicos vía `conector_sabios.py`
- ✅ Anti-bullshit: cada entry verificable, sin entries fantasma
- ✅ Brand DNA en naming de archivos: `reporte_poblamiento_catastros_<fecha>.md`, no `report.md`

---

## 6. Cierre formal

Cuando los 4 bloques cierren verde, Hilo Catastro declara:

> 🏛️ **Catastros poblados v0.1 — DECLARADOS** (30+ suppliers + 25+ herramientas AI canónicas operativas)

Y reporta al bridge con tabla de evidencia + counts por categoría + top entries.

---

## 7. Coordinación con Sprint 89 (Hilo Ejecutor paralelo)

- Sprint 89 (Ejecutor) construye infra técnica de los 2 Catastros nuevos
- Sprint Catastro-A (Catastro) los pueble con datos canónicos verificados
- Cuando ambos cierran, los 3 Catastros operan con datos reales
- Paralelismo zonificado puro: Sprint 89 toca solo `kernel/`, Sprint Catastro-A toca solo MCPs externos + investigación + inserción via Supabase MCP

Punto de sincronización: cuando Sprint 89 declare tablas creadas + endpoints REST funcionales, Hilo Catastro corre los bulk inserts y verifica que el endpoint `/v1/catastro/health-summary` refleja los counts correctos.

---

— Cowork (Hilo A), spec preparada 2026-05-06.
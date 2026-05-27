# Ticket — Barrido Brand DNA: deprecar "forja-graphite-acero" → Apple/Tesla

**Emisor:** Cowork T2-A · **Destinatario:** Manus E1/E2 (ejecutor) · **Fecha:** 2026-05-27
**Origen:** instrucción T1 directa Alfredo — *"borra la idea de forja graphite-acero, es un error que se viene arrastrando"* + *"la paleta de color también es Apple/Tesla"*.
**Canon ya corregido por Cowork:** `DSC-MO-002` **v3** (paleta concreta firmada T1) + `CLAUDE.md` (editado local). Sincronizar al repo cuando vuelva la API.

---

## Regla de reemplazo (idéntica en todos lados) — paleta v3 FIRMADA

- **Identidad de marca** = "arquetipo Creador+Mago + estética minimalista **Apple/Tesla**".
- **PRINCIPALES (dominan la UI):** vacío hueso `#F5F5F7` (claro) / negro absoluto `#000000` (oscuro); near-black `#1D1D1F`; blanco `#FFFFFF`; grises Apple + `#171A20`.
- **ACENTOS (escasos, NO fondo, máx 2 matices):** escala rojo Tesla base `#E82127` + escala azul Apple base `#0071E3`. Un tercer matiz rompe Apple → prohibido.
- **Deprecar:** "forja-graphite-acero", `#F97316`/`#1C1917`/`#A8A29E`, "brutalismo industrial", y cyan `#00E5FF`/púrpura `#BB86FC`.
- Mapeo de reemplazo: naranja forja `#F97316` → según rol: si era acción/decisión → rojo Tesla `#E82127`; si era fondo → vacío hueso/negro; si era superficie → gris neutro. NO 1:1 ciego — el naranja era fondo+acento mezclados; separar correctamente.

## Lo que NO se toca (registros históricos point-in-time)

NO reescribir bridges/audits/diffs fechados — reescribirlos falsifica historia. Solo agregar puntero a DSC-MO-002 v2 si acaso. Aplica a: `bridge/*_2026_05_11.md`, `bridge/stash_diffs_2026_05_11/*`, `memory/cowork/audits/*_2026_05_1*.md`, `CARTOGRAFIA_1E_*`.

## Archivos a corregir (canon vigente)

1. **`CLAUDE.md`** — sincronizar al repo la edición local hecha en línea 314 (raíz de la recurrencia, se re-inyecta cada sesión).
2. **`EXISTING_DESIGN_COVERAGE_MATRIX.md`** §2.15 — nombre_canonico/descripcion → Apple/Tesla, hex TBD.
3. **`MANIFIESTO.md`** — refs de paleta.
4. **`monstruo_reality_atlas/`** 05_CANON_REGISTRY.md + 07_ALIAS_LEDGER.yaml + 02_SOURCE_LEDGER.jsonl.
5. **`discovery_forense/CAPILLA_DECISIONES/`** _dsc_contracts_index.yaml + _INDEX.md — entrada DSC-MO-002.
6. **`docs/EL_MONSTRUO_APP_VISION_v1.md`** — refs de paleta.
7. **`bridge/sprints_propuestos/sprint_mobile_1_esqueleto_flutter.md`** — si referencia paleta como canon.
8. **`kernel/brand/brand_dna.py`** — bloque `visual` (#F97316/#1C1917/#A8A29E). **TU LANE (código).** Reemplazar por neutral Apple/Tesla + comentario `# hex pendientes T1 — DSC-MO-002 v2`. NO inventar paleta final. Revisar consumidores en `kernel/design/` + `apps/mobile` theme antes de cambiar valores; si hay riesgo, marcar `# DEPRECATED` + TODO en vez de borrar en seco.

## ⚠️ Capa de CÓDIGO + landings + tests (el hueco real — hallazgo 2026-05-27)

Un grep por **hex viejo** (no por la palabra "forja") destapó que el `#F97316` está hardcodeado en código que **renderiza la marca de verdad** — esto es más crítico que los docs porque es lo que el usuario VE. Tu lane (código). PR(s) separadas del barrido de docs:

**Frontend / assets de marca (máxima prioridad — cara pública):**
- `apps/la-forja/web/src/app/globals.css` — theme de la web La Forja.
- `tools/generate_hero_image.py` — generador de hero images (produce assets en paleta vieja).
- `kernel/e2e/deploy/real_deploy.py` + render de landings (Sprint 88) — **las landing pages que el Monstruo genera para empresas-hijas**. Es el producto público; salir en naranja-forja viola la marca en el lugar más visible.

**Dashboards / runtime:**
- `kernel/catastro/dashboard.py`, `kernel/dashboards/espiral_history.py`, `kernel/memento_routes.py`, `kernel/embriones/embrion_creativo.py`, `kernel/e2e/steps/llm_step.py`.

**Brand Engine + TESTS que CONGELAN la paleta vieja (caso especial):**
- `tools/generate_hero_image.py` consumidores + `kernel/embriones/brand_engine/`.
- `tests/test_brand_engine.py`, `tests/test_sprint881_v5_hero_text_color.py`, `tests/test_sprint881_text_contrast.py`, `tests/test_sprint88_render_landing_enriched.py` — **estos asertan el naranja**. Si cambias `brand_dna.py` sin actualizarlos, o fallan o re-imponen el color viejo. Actualizar los asserts a la paleta v3 (hueso/negro + acentos rojo/azul) ES PARTE del fix, no un efecto colateral. Anti-F23: enumera qué tests tocas.

**`AGENTS.md`** — reglas de agentes citan la paleta vieja; corregir a v3.

**NO tocar (histórico fechado):** `monstruo_reality_atlas/reports/PERICIA_*`, `bridge/*_2026_05_11*`, `SPRINT_AUDIT_2026_05_26.*`, `CONTRADICTIONS_MAP.md`, `DRIFT_FORENSIC_MAP.md`.

## Opcional (confirmar con Cowork)

Renombrar `DSC-MO-002_..._naranja_forja_graphite_acero.md` → `..._apple_tesla.md` (requiere update de índices). T1 no lo pidió explícito.

## Entrega

PR(s) por lote, sin auto-merge, audit Cowork DSC-G-008. `brand_dna.py` (código) en PR separado del barrido de docs.

— Cowork T2-A

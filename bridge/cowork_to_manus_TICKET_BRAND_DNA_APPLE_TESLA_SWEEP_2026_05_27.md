# Ticket — Barrido Brand DNA: deprecar "forja-graphite-acero" → Apple/Tesla

**Emisor:** Cowork T2-A · **Destinatario:** Manus E1/E2 (ejecutor) · **Fecha:** 2026-05-27
**Origen:** instrucción T1 directa Alfredo — *"borra la idea de forja graphite-acero, es un error que se viene arrastrando"* + *"la paleta de color también es Apple/Tesla"*.
**Canon ya corregido por Cowork:** `DSC-MO-002` v2 (commit `504ffe1`) + `CLAUDE.md` línea 314 (editado local, sincronizar al repo — tarea 1).

---

## Regla de reemplazo (idéntica en todos lados)

- **Identidad de marca** = "arquetipo Creador+Mago + estética minimalista **Apple/Tesla**".
- **Paleta concreta (hex):** **pendiente de definición T1.** NO inventar colores. Donde haya hex forja-graphite-acero como canon obligatorio → "paleta neutral/monocromática Apple/Tesla — hex pendientes T1".
- **Deprecar:** "forja-graphite-acero", "Naranja Forja #F97316", "brutalismo industrial" como canon vigente.

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

## Opcional (confirmar con Cowork)

Renombrar `DSC-MO-002_..._naranja_forja_graphite_acero.md` → `..._apple_tesla.md` (requiere update de índices). T1 no lo pidió explícito.

## Entrega

PR(s) por lote, sin auto-merge, audit Cowork DSC-G-008. `brand_dna.py` (código) en PR separado del barrido de docs.

— Cowork T2-A

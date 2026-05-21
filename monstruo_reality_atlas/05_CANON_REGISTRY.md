# 05 — CANON REGISTRY

**Este archivo es un agregador delgado. La fuente primaria del canon firmado vivo está en el Context Fabric.**

---

## Fuente primaria

El registro consolidado del canon firmado vigente del Monstruo vive en el Context Fabric en GitHub, rama `interfaces-context-fabric-001`, archivo:

- **`interfaces_context_fabric/maps/CANON_REGISTRY.yaml`** (231 líneas, formato YAML estructurado para consumo de IA)
- **`interfaces_context_fabric/maps/CANON_TRUTH_MATRIX.md`** (matriz de verdad por estado)

URL verificable:
https://github.com/alfredogl1804/el-monstruo/blob/interfaces-context-fabric-001/interfaces_context_fabric/maps/CANON_REGISTRY.yaml

ChatGPT y cualquier sabio que consulte canon firmado debe ir a esa fuente primaria. El Reality Atlas NO duplica ese contenido — solo apunta a él para evitar drift entre fuentes paralelas.

## Por qué esta separación

El Context Fabric fue construido específicamente para resolver la dimensión INTERFACES + DOCTRINA del Monstruo. Su `CANON_REGISTRY.yaml` ya está validado, está vivo en GitHub, y forma parte de la cadena de trabajo con ChatGPT iter 002. Crear un canon registry paralelo en el Reality Atlas produciría dos fuentes de verdad que requerirían reconciliación constante. La regla de no-duplicación de este atlas (regla 1 de `01_SCOPE_AND_RULES.md`) prohíbe esa duplicación.

## Lo que SÍ aporta el Reality Atlas

El Reality Atlas extiende el canon del fabric con dimensiones que el fabric no cubre. La primera dimensión es el **inventario de repositorios** (`03_REPOSITORY_INVENTORY.md`) que cataloga los 15 repos core de Alfredo más los proyectos adyacentes y los artefactos del Pipeline E2E. La segunda es el **inventario de producción viva** (`04_PRODUCTION_INVENTORY.md`) que mapea el Command Center, Bot Telegram, API kernel, ticketlike.mx, simulador IA y otros endpoints reales. La tercera es el **alias ledger consolidado** (`07_ALIAS_LEDGER.yaml`) que extiende los aliases del fabric con los detectados en proyectos adyacentes y producción.

## Cómo usar este atlas con el fabric

Si una IA o agente necesita resolver un concepto canónico, sigue este orden:

1. **Buscar en `07_ALIAS_LEDGER.yaml`** del Reality Atlas para resolver alias→concept_id.
2. **Consultar `interfaces_context_fabric/maps/CANON_REGISTRY.yaml`** del fabric para obtener el canon firmado del concept_id.
3. **Si el concepto no está en el fabric**, consultar `interfaces_context_fabric/maps/HYPOTHESIS_REGISTRY.yaml` (hipótesis nacientes) o `interfaces_context_fabric/maps/EXISTING_DESIGN_COVERAGE_MATRIX.md` (cobertura existente).
4. **Si tampoco está allí**, ejecutar el protocolo de búsqueda completo de `10_DO_NOT_REDESIGN_BEFORE_READING.md` antes de proponer canon nuevo.

## Tabla de equivalencias críticas (sin duplicar contenido del fabric)

Esta tabla solo lista los `concept_id` magna del Monstruo y a qué archivo del fabric apuntan para detalle completo. NO contiene la doctrina misma — solo los punteros.

| concept_id | apunta_a (fabric) |
|---|---|
| `app_vision` | `maps/CANON_REGISTRY.yaml#app_vision` |
| `agents_md` | (raíz repo) `AGENTS.md` |
| `cronos_rio_de_vida` | `maps/CANON_REGISTRY.yaml#cronos_rio_de_vida` + `context_packs/PACK_04_CRONOS_RIO_DE_VIDA.md` |
| `cronos_modo_cripta` | `maps/CANON_REGISTRY.yaml#cronos_modo_cripta` + `context_packs/PACK_12_RIO_DE_LA_VIDA_EXISTING_AUDIT.md` |
| `a2ui_protocol` | `maps/CANON_REGISTRY.yaml#a2ui_protocol` |
| `memento_protocol` | `maps/CANON_REGISTRY.yaml#memento_protocol` |
| `brand_dna_forja_graphite_acero` | `maps/CANON_REGISTRY.yaml#brand_dna` + `maps/DRIFT_FORENSIC_MAP.md` |
| `daily_5_superficies` | `maps/SURFACE_REGISTRY.yaml#daily` |
| `cockpit_12_15_superficies` | `maps/SURFACE_REGISTRY.yaml#cockpit` |
| `8_capabilities_transversales` | `maps/CANON_REGISTRY.yaml#capabilities` |
| `smp_5_propiedades` | `maps/CANON_REGISTRY.yaml#smp` + `maps/HYPOTHESIS_REGISTRY.yaml` |
| `cap_17_seguridad` | `context_packs/PACK_11_SEGURIDAD_SOBERANIA.md` |
| `schema_first_invariante` | `maps/HYPOTHESIS_REGISTRY.yaml#schema_first` |
| `transport_cero` | `maps/HYPOTHESIS_REGISTRY.yaml#transport_cero` |
| `pre_ia_checkpoint_2020_2021` | `raw_rescues/alfredo_pre_ia_checkpoint_2020_2021_DRAFT.md` (DRAFT, EN_EXTRACCION_T1) |

---

*Procedé con `06_SPRINT_REGISTRY.md`.*

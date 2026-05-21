# 08 — EXISTING DESIGN COVERAGE MATRIX

**Este archivo es un agregador delgado. La matriz consolidada de cobertura existe en el Context Fabric.**

---

## Fuente primaria

La matriz canónica de cobertura de diseño existente del Monstruo está en:

- **`interfaces_context_fabric/maps/EXISTING_DESIGN_COVERAGE_MATRIX.md`** (477 líneas, 50+ conceptos catalogados con concept_id, evidence_paths, status binario y aliases)
- **`interfaces_context_fabric/maps/CANON_TRUTH_MATRIX.md`** (matriz adicional de verdad por estado)
- **`interfaces_context_fabric/maps/HYPOTHESIS_REGISTRY.yaml`** (hipótesis nacientes con score)

URL verificable:
https://github.com/alfredogl1804/el-monstruo/blob/interfaces-context-fabric-001/interfaces_context_fabric/maps/EXISTING_DESIGN_COVERAGE_MATRIX.md

ChatGPT y cualquier sabio que evalúe si un concepto ya existe canonizado debe consultar primero el fabric.

## Por qué esta separación

La coverage matrix del fabric ya tiene 50+ conceptos catalogados con estructura YAML completa. Duplicar ese trabajo en el Reality Atlas crearía dos matrices paralelas que requerirían reconciliación. La regla 1 de `01_SCOPE_AND_RULES.md` lo prohíbe.

## Qué agrega el Reality Atlas

El Reality Atlas extiende la coverage matrix del fabric con dos capas que el fabric no cubre. La primera capa es **cobertura en proyectos adyacentes**: cuando un concepto del Monstruo aparece también en `crisol-7`, `proyecto-renders`, `softrestaurant-ai-10x` u otros proyectos del ecosistema Alfredo, el Reality Atlas lo registra como cross-project. La segunda capa es **cobertura en producción viva**: el fabric documenta canon y código pero no si el concepto está deployed. El Reality Atlas vincula cada concept_id a su estado en `04_PRODUCTION_INVENTORY.md`.

## Decisión sobre la propuesta "Cronista Familiar"

El caso paradigmático que originó la regla "primero buscar, después diseñar" está documentado completamente en el fabric en `interfaces_context_fabric/context_packs/PACK_12_RIO_DE_LA_VIDA_EXISTING_AUDIT.md`. Resumen: las cuatro propuestas de ChatGPT iter previas (Cronista Familiar / Herencia Narrativa / Legacy Capture / Día One Familiar) son **aliases del concept_id `cronos_modo_cripta`**, ya canonizado en APP_VISION cap. 5 con Shamir Secret Sharing. NO es capa nueva. Los cuatro nombres están en `07_ALIAS_LEDGER.yaml` de este atlas.

## Conceptos cross-project detectados (no en fabric)

Estos conceptos aparecen en proyectos adyacentes y forman parte del ecosistema Alfredo aunque no del Monstruo strictu sensu. La metodología de los **6 Sabios** está canonizada en `crisol-7` y se usa también en el Monstruo (skill `consulta-sabios`) y en `simulador-escenarios-ia`. El **enjambre iterativo** de prompts es metodología compartida. **TiDB** como base de datos de alto volumen se comparte entre `like-kukulkan-tickets` y otros proyectos. **Stripe** como gateway de pagos se comparte entre `like-kukulkan-tickets` y `cip-tokenizacion-inmobiliaria`. **Railway** como infraestructura runtime se comparte entre Bot Telegram, API kernel, ticketlike, simulador IA.

## Tabla compacta de cobertura por dominio

Esta tabla resume el estado por dominio sin duplicar el detalle del fabric:

| Dominio | Conceptos en Canon | Conceptos en Hipótesis | Implementados Pleno | Drift Detectado |
|---|---|---|---|---|
| Doctrina raíz | 5 | 0 | 5 | 0 |
| Arquitectura interfaz | 6 | 1 (Schema-First) | 2 (Memento, AG-UI) | 0 |
| Catastros y capabilities | 3 | 0 | 0 (0/8 caps) | 0 |
| Memoria y soberanía | 4 | 0 | 1 (Memento) | 0 |
| Cronos y río de vida | 6 | 0 | 0 | 0 (canon vs implementación, no drift) |
| Seguridad y soberanía | 6 | 0 | 1 (DSC-S) | 0 |
| Brand DNA | 3 | 0 | 0 | 1 (binario) |
| Gobernanza | 5 | 0 | 5 | 0 |
| Productividad | 2 | 1 (Calm Tech parcial) | 0 | 0 |
| Skills canonizadas | 4 | 0 | 4 | 0 |
| **Total** | **44** | **2** | **18** | **1** |

El detalle completo de cada concepto vive en el fabric. Esta tabla solo da una vista agregada para que ChatGPT pueda dimensionar el espacio de trabajo en menos de 30 segundos.

---

*Procedé con `09_GAPS_AND_UNKNOWN_UNKNOWNS.md`.*

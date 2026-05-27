---
id: DSC-MO-002
proyecto: EL-MONSTRUO
tipo: restriccion_dura
titulo: "Brand DNA del Monstruo: arquetipo Creador+Mago + estética minimalista Apple/Tesla. Paleta neutral/monocromática (hex concretos pendientes T1). DEPRECADO: forja-graphite-acero + brutalismo industrial."
estado: firme
version: 2
fecha: 2026-05-06
fecha_correccion_t1: 2026-05-27
fuentes:
  - repo:AGENTS.md
  - repo:kernel/brand/brand_dna.py
cruza_con: ["DSC-G-004"]
---

# Brand DNA: Creador+Mago + Minimalismo Apple/Tesla

## ⚠️ Corrección T1 (2026-05-27)

La v1 de este DSC (2026-05-06) canonizó por error una paleta "Naranja Forja #F97316 + Graphite + Acero, brutalismo industrial refinado" como restricción dura. **T1 Alfredo la deprecó el 2026-05-27:** ese "forja-graphite-acero" fue un error que se arrastró y se propagó por todo el canon. El Brand DNA real — **incluida la paleta de color** — se rige por la estética **Apple/Tesla**, no por brutalismo industrial.

## Decisión (v2)

El Brand DNA de El Monstruo es:

- **Arquetipo:** El Creador + El Mago (`creator_mage`).
- **Personalidad:** implacable, preciso, soberano, magnánimo.
- **Estética:** minimalismo **Apple/Tesla** — restraint premium, neutral/monocromática, foco en el contenido y no en el cromo. Calidad de diseño nivel Apple/Tesla (Objetivo Maestro #2).
- **Paleta concreta (hex):** **pendiente de definición T1.** NO se inventan colores. Hasta que T1 defina los hex, la guía es "neutral/monocromática estilo Apple/Tesla".
- **Naming:** módulos con identidad (DSC-G-004); NUNCA service/handler/utils/helper/misc.

## Prohibido (deprecado)

- ❌ "forja-graphite-acero" como identidad de marca.
- ❌ Naranja #F97316 / Graphite #1C1917 / Acero #A8A29E como paleta canónica obligatoria.
- ❌ "brutalismo industrial refinado" como estilo visual.

Estos términos sobreviven solo como **registro histórico** (no como canon vigente).

## Implicaciones

Toda interfaz, documento o material visual nuevo se rige por minimalismo Apple/Tesla. Los hex concretos quedan bloqueados hasta firma T1 de la paleta. El barrido de las ~16 referencias al término deprecado en el repo + el bloque `visual` de `kernel/brand/brand_dna.py` es trabajo de Manus (ejecutor) bajo ticket Cowork.

## Estado de validación

firme (v2) — corrección T1 directa 2026-05-27, transcrita por Cowork T2-A para ratificación. T1 puede ajustar la paleta concreta cuando la defina.

## Nota de nomenclatura

El nombre de archivo (`..._naranja_forja_graphite_acero.md`) quedó legacy/misnomer tras esta corrección. Renombrar a `DSC-MO-002_brand_dna_apple_tesla.md` requiere actualizar `_dsc_contracts_index.yaml` + refs — incluido en el ticket de barrido a Manus.

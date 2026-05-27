---
id: DSC-MO-002
proyecto: EL-MONSTRUO
tipo: restriccion_dura
titulo: "Brand DNA: Creador+Mago + minimalismo Apple/Tesla. PRINCIPALES = neutros sólidos + vacío (hueso / negro absoluto). ACENTOS (escasos, máx 2 matices) = escala rojo Tesla + escala azul Apple. DEPRECADO: forja-graphite-acero + brutalismo."
estado: firme
version: 3
fecha: 2026-05-06
fecha_correccion_t1: 2026-05-27
fuentes:
  - repo:AGENTS.md
  - repo:kernel/brand/brand_dna.py
cruza_con: ["DSC-G-004"]
---

# Brand DNA: Creador+Mago + Minimalismo Apple/Tesla

## Historia de corrección
- **v1 (2026-05-06):** error — canonizó "Naranja Forja #F97316 + Graphite + Acero, brutalismo industrial". Se arrastró por el canon.
- **v2 (2026-05-27):** T1 deprecó forja-graphite-acero; Brand DNA = Apple/Tesla.
- **v3 (2026-05-27):** T1 define la paleta con **jerarquía correcta** — los neutros + el vacío son los PRINCIPALES; rojo y azul son solo ACENTOS de contraste. Corrige el error de v3-borrador que llamó "primario" al rojo.

## Decisión (v3)

- **Arquetipo:** El Creador + El Mago (`creator_mage`).
- **Personalidad:** implacable, preciso, soberano, magnánimo.
- **Estética:** minimalismo Apple/Tesla — restraint premium, el contenido por encima del cromo, el vacío manda.

### 1. Colores PRINCIPALES — la identidad (neutros sólidos + vacío)

**Esto ES la marca.** Monocromática, sólida, el vacío como protagonista.

- **Vacío / fondo claro:** hueso / off-white `#F5F5F7`
- **Vacío / fondo oscuro:** negro absoluto `#000000`
- **Texto / sólido sobre claro:** near-black `#1D1D1F`
- **Blanco puro:** `#FFFFFF`
- **Grises neutros / superficies:** escala gris Apple (ej. `#86868B`, `#424245`) + `#171A20` (gris muy oscuro Tesla) para capas sobre el negro

### 2. Colores de ACENTO — contraste, uso escaso (NO son la marca)

Aparecen puntualmente (acción, decisión, info), nunca como fondo dominante.

- **Escala ROJO Tesla** — base `#E82127`. Acción / decisión / lo "magna" / destructivo. Escala funcional derivada del base: tint claro (hover), shade oscuro (pressed), lavado a baja opacidad (fondos sutiles, badges).
- **Escala AZUL Apple** — base `#0071E3`. Info / links / estados secundarios. Misma lógica de escala funcional.

### Regla de oro de acentos (mantiene el restraint Apple/Tesla)

- **Máximo 2 MATICES de acento:** rojo Tesla + azul Apple. **Un tercer matiz (verde, naranja, amarillo, púrpura...) rompe Apple/Tesla — prohibido.**
- Dentro de cada matiz, **escala funcional libre** (tints/shades/opacidades para estados). Tener muchos tonos de rojo NO rompe Apple; tener muchos colores distintos SÍ.
- Las escalas son derivaciones del mismo base (no son matices nuevos). Los pasos intermedios se derivan del base; no se inventan como "valores oficiales Apple".

**Naming:** módulos con identidad (DSC-G-004); NUNCA service/handler/utils/helper/misc.

## Prohibido (deprecado, solo registro histórico)
- ❌ "forja-graphite-acero" como identidad de marca.
- ❌ Naranja #F97316 / Graphite #1C1917 / Acero #A8A29E como paleta canónica.
- ❌ "brutalismo industrial refinado".
- ❌ Cyan #00E5FF / púrpura #BB86FC (drift del Command Center).
- ❌ Cualquier tercer matiz de acento.

## Implicaciones
Toda interfaz nueva: vacío hueso o negro absoluto + neutros sólidos como base; rojo/azul solo como chispas de contraste. El barrido de las refs deprecadas + el bloque `visual` de `kernel/brand/brand_dna.py` es trabajo de Manus bajo ticket Cowork.

## Estado de validación
firme (v3) — jerarquía y escalas firmadas por T1 Alfredo 2026-05-27 ("los principales son los neutros sólidos y el vacío hueso/negro; rojo y azul son contraste; escalas de rojo/azul OK mientras sean 2 matices"). Transcrita por Cowork T2-A.

## Nota de nomenclatura
Nombre de archivo (`..._naranja_forja_graphite_acero.md`) = legacy/misnomer. Renombrar a `DSC-MO-002_brand_dna_apple_tesla.md` en el ticket de barrido.

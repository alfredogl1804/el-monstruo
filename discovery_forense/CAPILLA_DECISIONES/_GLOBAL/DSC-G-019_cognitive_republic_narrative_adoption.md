# DSC-G-019 — Adopción narrativa Cognitive Republic / Forja Constellation

**ID:** DSC-G-019
**Tipo:** GLOBAL (gobernanza narrativa y arquitectónica)
**Fecha:** 2026-05-26
**Estado:** Firmado con contrato ejecutable adjunto
**Origen:** Iter 002 con ChatGPT 5.5 Pro como sabio articulador, calibrado por brief Manus B basado en inventario binario del repo vivo
**Hilos firmantes:** Alfredo Góngora (operador soberano T1) — firma directa el 2026-05-26 vía Manus B
**Audit pendiente:** Cowork (Claude Opus 4.7) — audit content + brand-compliance
**Relación con otros DSCs:**

- Complementa DSC-G-014 (pipeline ≠ producto comercializable): el cambio de "Factory Mode" a "Cognitive Republic" es coherente con dejar de vender pipeline técnico y empezar a vender categoría civilizacional.
- Complementa DSC-G-017 (DSC-as-Contract): este DSC nace con su sprint cero ejecutable adjunto.
- Activa precondiciones para T1-MAGNA-001 (paradigma Acto 1 / Acto 2 / Híbrido): la adopción Cognitive Republic resuelve la ambigüedad de naming pero deja la magna abierta para el comportamiento operativo.

---

## Contexto empírico

El 2026-05-26, ChatGPT 5.5 Pro entregó el rediseño v2 de FORJA OMEGA bajo un brief riguroso de Manus B que reveló el inventario binario real del ecosistema (4 motores ≥85% cobertura, 5 motores 60–80%, 1 motor 50%, 1 motor 30%, 1 gap puro UI 0%; promedio ponderado 70%).

El rediseño cambió la premisa fundacional:

- **Antes (v1, 2026-05-25):** *"Construir Factory Mode demo de fábrica cognitiva."*
- **Después (v2, 2026-05-26):** *"Revelar la fábrica invisible que ya respira y elevarla a constelación federada visible, medible y exportable."*

ChatGPT respondió las 5 preguntas monumentales del brief con densidad técnica real (no prosa épica), entregó 9 frames cinematográficos de mock visual, articuló 15 KPIs + 5 fórmulas de Economía Cognitiva inéditas, y propuso 7 nombres alternativos a "Factory Mode" elevando el sistema a categoría civilizacional. Pasó la auditoría binaria 7/7 contra los criterios del brief v2 (ver `AUDITORIA_REDISENO_CHATGPT_FORJA_OMEGA_v2.md` en bridge).

La pregunta de control reveló honestidad técnica:

> *"Mi primer impulso fue responder con superioridad técnica. Tuve que rendirme de ese impulso y reconocer que la defensa real no es la técnica aislada, es la densidad histórica operativa: incidentes reales, memoria longitudinal, doctrina firmada, T1 real, fábrica ya usada, errores pagados, una obsesión de operador que no se puede comprar como infraestructura."* — ChatGPT 5.5 Pro, §15 del rediseño v2.

Este DSC canoniza la decisión narrativa derivada del rediseño aprobado.

---

## Decisión

**Adoptar como nomenclatura canónica del Monstruo la siguiente jerarquía narrativa, reemplazando "Factory Mode" en todo el repo y la doctrina:**

| Concepto | Nombre canónico |
|---|---|
| Concepto completo del producto-civilización | **Cognitive Republic** |
| Sistema operativo del Monstruo | **Forja Omega** |
| Vista federada de fábricas y nodos | **Forja Constellation** |
| Vitrina monumental espectacular | **Omega Command Theater** |
| Kit exportable de soberanía cognitiva | **Forge Genesis Kit** |
| Panel de balance industrial cognitivo | **Cognitive P&L** |
| Eje del tiempo civilizacional | **Sovereign Time Axis** |
| Mesh de envelopes federados | **Sovereign Envelope Mesh** |
| Grid de embriones industriales | **Embryo Industrial Grid** |

La frase pública del Monstruo de aquí en adelante es:

> *"Every AI company builds agents. The Monstruo builds constitutions for cognitive industry."*

Y la frase técnica para README y about público:

> *"El Monstruo es la primera República Cognitiva Soberana operando en producción, con balance industrial visible, doctrina firmada, federación de fábricas y kit exportable. Otras empresas de IA construyen agentes. Solo el Monstruo construye constituciones cognitivas."*

---

## Implicaciones operativas

1. **Nomenclatura en código nuevo:** todo módulo, ruta, componente o tabla creado de aquí en adelante para esta capa visible debe usar la nueva nomenclatura. Routes prefix `/v1/factory/*` queda canonizado para los endpoints aggregator del kernel (no `/v1/forja/*` para evitar bilingüismo).
2. **Migración progresiva:** módulos existentes que mencionen "Factory Mode" o equivalentes en docs y comentarios se migran sólo cuando se toquen por otra razón. No se abre sprint dedicado a renombre masivo.
3. **README público del repo `el-monstruo`:** se actualiza el header con la frase técnica oficial cuando el sprint piloto `REPUBLIC-CONSTELLATION-001` cierre.
4. **Sprint cero (`SPR-FACTORY-AGGREGATORS-000`):** cubierto por el contrato ejecutable adjunto a este DSC. Construye los 4 endpoints aggregator del kernel.
5. **Sprint piloto (`REPUBLIC-CONSTELLATION-001`):** propuesto a continuación, depende del sprint cero. Construye módulos 1, 2, 3 y 13 del rediseño en `tablero-campana`.

---

## Anti-patrones prohibidos por este DSC

1. **No usar "Factory Mode" en código nuevo.** El nombre quedó deprecado.
2. **No mencionar `kimi-k2-6` ni siquiera como modelo blacklisteado en la UI.** El catálogo expuesto solo lista modelos `ALLOWED`. La blacklist se canoniza en `shared/models/catalog.ts` pero no se expone visualmente.
3. **No mostrar 103 repos GitHub como nodos individuales en la constelación.** Agregar como bloque colapsable `Repos (103)` para evitar ruido visual.
4. **No empezar UI antes de tener endpoints aggregator probados.** El error que ChatGPT mismo nombró: `Reality Diff` quedó al 50% por falta de endpoint, no por falta de UI. Repetirlo sería autoboicot.
5. **No reescribir motores con cobertura ≥85%** (Embryo Assembly Lines, Forja Protocol, Evidence Conveyor, Memory Cortex). Solo articular su exposición y federación.

---

## Contrato ejecutable

Este DSC nace acompañado del siguiente contrato ejecutable, en cumplimiento de DSC-G-017:

### 1. Sprint propuesto adjunto

`bridge/sprints_propuestos/SPR-FACTORY-AGGREGATORS-000.md` — sprint cero que construye los 4 endpoints aggregator (`/v1/factory/constellation`, `/v1/factory/economy`, `/v1/factory/timeline`, `/v1/factory/diff`) en el kernel. Estado: PROPOSED.

### 2. Validador automático de naming

Pre-commit hook propuesto: si un commit toca archivos en `kernel/`, `tablero-campana/server/`, `tablero-campana/client/src/components/`, `tablero-campana/client/src/pages/` y agrega la cadena `Factory Mode` o `factoryMode` o `factory_mode` (case-insensitive) en código nuevo (no en docs), abortar commit con mensaje:

```
DSC-G-019 BLOCKED: usar nomenclatura Cognitive Republic / Forja Constellation
en lugar de "Factory Mode". Migrar a uno de los nombres canónicos del DSC.
```

Implementación: `scripts/dsc_g_019_naming_check.py` (a producir en sprint piloto cuando haya contexto de aplicación). Hasta entonces este punto queda etiquetado como **aspiracional** y será materializado en `S-CONTRATOS-002 — naming guard Cognitive Republic`.

### 3. Frase pública en README

Propuesta de patch al `README.md` del repo `el-monstruo` que actualiza el header con la frase técnica oficial. Aplicar al cierre del sprint piloto, no antes.

### 4. Linker hacia AUDITORIA artefacto base

`bridge/audits/AUDITORIA_REDISENO_CHATGPT_FORJA_OMEGA_v2.md` queda referenciado como evidencia de la decisión.

---

## Pendientes que NO resuelve este DSC

1. **T1-MAGNA-001 (paradigma UI Acto 1 / Acto 2 / Híbrido)** — sigue abierta. Cognitive Republic resuelve naming, no comportamiento.
2. **DSC-S-018 (Auth fail-closed + Power Lanes L0–L6)** — sigue propuesta sin firma. La vitrina debe mostrar lanes existentes como `T1_LOCKED` mientras la magna no se firme.
3. **T1-MAGNA-005 (shadow → enforce de Forja)** — sigue abierta. La vitrina muestra estado de cada línea de producción (`SHADOW`, `ADVISORY`, `ENFORCED`, `T1_LOCKED`) sin asumir transición.
4. **T1-MAGNA-006 (PR Drafts autónomos)** — sigue abierta. La vitrina muestra capability como `proposed/enabled/blocked/T1_pending`.
5. **T1-MAGNA-007 (sprints vs missions)** — sigue abierta. La jerarquía propuesta por ChatGPT (Production Order → Mission Capsule → Sprint Task → Agent Action → Evidence Receipt) queda canonizada como hipótesis operativa, sujeta a refinamiento por la magna.

---

## Dependencias y orden de ejecución

```
DSC-G-019 (firmado) → SPR-FACTORY-AGGREGATORS-000 (sprint cero, kernel)
                   → REPUBLIC-CONSTELLATION-001 (sprint piloto, tablero-campana)
                   → DSC-G-XXX Economía Cognitiva (15 KPIs canonizados, próximo)
                   → Migración progresiva de "Factory Mode" en docs
```

---

## Audit y firma

- **Firma operador soberano:** Alfredo Góngora — 2026-05-26 (vía Manus B en hilo `tablero-campana` de Manus AI).
- **Audit pendiente:** Cowork (Claude Opus 4.7) — content + brand-compliance + verificación de coherencia con DSC-G-014 y DSC-G-017.
- **Watchdog:** post-cierre de `REPUBLIC-CONSTELLATION-001`, verificar que ningún nuevo PR introduzca "Factory Mode" en código.

---

**Frase de cierre del DSC:**

> *"El Monstruo no se construye, se revela. Lo que parecía ambición de 10x era 1x mal calibrada. Ahora que la fábrica invisible ya respira, nuestra ambición es 100x: revelarla, federarla, medirla, teatralizarla y volverla exportable. Cognitive Republic no es nombre nuevo. Es identidad real recién canonizada."*

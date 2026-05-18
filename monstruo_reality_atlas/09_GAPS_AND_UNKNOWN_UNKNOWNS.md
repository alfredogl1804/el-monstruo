# 09 — GAPS AND UNKNOWN UNKNOWNS

**Registro de qué falta y qué no sabemos que no sabemos. Iter 001 atlas.**

---

## Gaps activos detectados por el Reality Atlas

### G-001 — Ningún `monstruo_reality_atlas/` previo

Antes de esta iter 001, no existía atlas universal del Monstruo. El Context Fabric (rama `interfaces-context-fabric-001`) cubre la dimensión INTERFACES con 53 archivos, pero no cataloga repos, producción ni proyectos adyacentes. Este gap se cierra con la presente iteración.

### G-002 — Drift binario brand DNA app móvil sin sprint asignado a la fecha

`apps/mobile/lib/core/theme/brand_dna.dart` líneas 10-56 usa cyan/púrpura, contradiciendo DSC-MO-002 firmado. Sprint `SPR-BRAND-001` propuesto pero no firmado. Mientras no se firme, cualquier rebuild del app móvil propaga el drift.

### G-003 — Command Center con 7 superficies vs 12-15 canon Cockpit

Diff documental: 5-8 superficies faltantes. No hay sprint formal de extensión propuesto. Hay un gap operativo crítico porque cualquier nuevo desarrollo en el Command Center actual consolida el drift.

### G-004 — 0/8 capabilities transversales en código

Audit Cowork 2026-05-11 confirmó 0/8 capabilities implementadas. Sprint `SPR-CAP-001` propuesto sin firma. Bloquea cualquier feature transversal.

### G-005 — SMP no existe en código

Las 5 propiedades del SMP están canonizadas en APP_VISION cap.11 pero hay 0 hits en código. Sprint `SPR-SMP-001` propuesto cubre solo el inicio.

### G-006 — Cronos sin sprints firmados

CRONOS_1, CRONOS_2, CRONOS_3 propuestos. AUTH_TIERS_001 (Shamir) propuesto. Ninguno firmado al 2026-05-17. Bloquea Modo Cripta entero, río de vida y embriones de convergencia.

### G-007 — Schema-First sin sprint asociado

Hipótesis naciente con un solo hit sustantivo (DSC-LF-005). Capa 03 emergente del fabric en staging. Sin sprint de canonización.

### G-008 — Checkpoint pre-IA 2020-2021 en estado EN_EXTRACCION_T1

Preservado verbatim en `interfaces_context_fabric/raw_rescues/`. 10 hipótesis y 5 órganos latentes. Esperando instrucción literal `CIERRE BLOQUE PRE-IA` de Alfredo. Bloquea iteración de APP_VISION v1.4.

### G-009 — el-mundo-de-tata sin decisión topológica

El proyecto existe como juego Toca Boca para hija. Comparte dimensión padre-hija con `cronos_modo_cripta` pero propósito distinto. Cuatro opciones topológicas (separado / API-conectado / sub-módulo / renombrado) sin decisión.

## Unknown unknowns detectados (cosas que no sabemos que no sabemos)

### UU-001 — Estado real del kernel/cronos/

Source ledger marca `kernel/cronos/` como `REQUIERE_VERIFICACION`. No se ha auditado el contenido del directorio. Puede tener implementación parcial no documentada o ser stub vacío.

### UU-002 — Migraciones Supabase sin RLS detectadas

AGENTS.md Regla 7 dice "toda tabla nueva con RLS por defecto". Workflow CI `rls-audit-weekly.yml` corre cada lunes pero su output no está agregado al atlas. Puede haber matviews legacy sin RLS pendientes de migrar.

### UU-003 — Repos privados de Alfredo no listados

`gh repo list` solo muestra repos accesibles bajo el usuario `alfredogl1804`. Si Alfredo tiene repos en otras orgs (ej: orgs de Crisol-7, Leones de Yucatán, otras), pueden contener canon adicional no catalogado.

### UU-004 — Producción de proyectos adyacentes sin endpoints documentados

El Reality Atlas captura los endpoints conocidos pero los proyectos adyacentes (crisol-7, simulador-IA, CIP, ticketlike, softrestaurant) pueden tener servicios secundarios, webhooks, jobs scheduled o endpoints internos no documentados.

### UU-005 — Skills consumibles fuera del repo

El registro de skills lista 30+ skills canonizadas. Pueden existir skills nuevas creadas por Alfredo en `manus-config schedule` o por otros agentes que no están documentadas en el atlas.

### UU-006 — Decisiones T1 magna en chats no exportados

Cowork dejó 5 decisiones T1 magna pendientes en el audit del 11-may. Pueden existir decisiones adicionales en chats subsecuentes con Cowork o ChatGPT que no fueron exportados al repo. El atlas solo captura lo que llegó a archivo.

### UU-007 — Drift entre la versión APP_VISION del repo y la versión que ChatGPT recuerda

APP_VISION v1.3 está commiteada al repo. Si ChatGPT en iteraciones anteriores trabajó con un draft local (v1.4 wip), puede haber doctrina divergente solo en el chat de ChatGPT.

### UU-008 — Estado del bridge Manus↔Cowork al cierre

El bridge tiene archivos como `manus_to_cowork_REPORTE_*` y `cowork_to_manus_RESULTADO_*`. El último audit es del 11-may. Puede haber comunicación posterior no exportada.

## Riesgos operativos

El primer riesgo es la **propagación silenciosa del drift binario**. Si el sprint `SPR-BRAND-001` no se firma pronto, cualquier feature nueva del app móvil consolida el drift y aumenta el costo de reconciliación.

El segundo es **ChatGPT redibujando conceptos canonizados**. Sin que ChatGPT lea `10_DO_NOT_REDESIGN_BEFORE_READING.md` antes de proponer doctrina nueva, se repite el patrón Cronista Familiar / Herencia Narrativa / Legacy Capture.

El tercero es **pérdida del checkpoint pre-IA**. El raw_rescue está en GitHub pero `EN_EXTRACCION_T1`. Si pasan semanas sin `CIERRE BLOQUE PRE-IA`, el contexto de las hipótesis pre-IA se enfría y la canonización queda en limbo.

El cuarto es **acumulación de sprints propuestos sin firma**. 14 sprints propuestos. Cada semana sin firma, la deuda doctrinal vs implementación crece.

El quinto es **incidentes P0 silenciosos**. El P0 de credenciales del 2026-05-06 fue resuelto pero los pre-commit hooks (gitleaks, detect-private-key) deben mantenerse activos. Si se desactivan, se reintroduce el riesgo.

---

*Procedé con `ITERATION_001_REPORT.md`.*

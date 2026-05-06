# Sprints Propuestos — Cowork → Hilos Manus (post v1.2 firmado)

**Fecha:** 2026-05-06
**Autor:** Cowork (Hilo A)
**Contexto:** v1.2 del documento de visión canónico en `main` (commit `31166ab`) + DSC-X-006 (Convergencia Diferida) + DSC-G-007 (3 Catastros paralelos) firmados (commit `c7bc034`).

---

## Resumen ejecutivo

5 sprints largos (ETA 6-12h cada uno) distribuidos entre los 2 hilos Manus para paralelismo zonificado puro. Hilo Ejecutor opera en `kernel/` + `packages/`. Hilo Catastro opera fuera del kernel — investigación + curaduría + skills + templates.

---

## Sprints para Hilo Ejecutor (zona `kernel/` + `packages/`)

| Sprint | Spec | ETA | Bloqueos | Prioridad |
|---|---|---|---|---|
| **88 — Cierre v1.0 PRODUCTO COMERCIALIZABLE** | [`sprint_88_cierre_v1_producto.md`](./sprint_88_cierre_v1_producto.md) | 8-12h | Ninguno | 🔴 **MAGNA** — cierra el ciclo que Manus declaró v1.0 BACKEND. Diferencia entre backend que orquesta y producto que vende. |
| **89 — Catastros 0: extensión Suppliers + Herramientas AI** | [`sprint_89_catastros_extension_suppliers_herramientas_ai.md`](./sprint_89_catastros_extension_suppliers_herramientas_ai.md) | 8-12h | Ninguno | 🟠 Alta — implementa DSC-G-007 firmado. Paralelizable con Sprint Catastro-A. |
| **90 — `@monstruo/checkout-stripe` package extraído** | [`sprint_90_checkout_stripe_package.md`](./sprint_90_checkout_stripe_package.md) | 6-10h | Sprint 88 cerrado primero (validar patrón en prod antes de extraer) | 🟠 Alta — desbloquea Marketplace, CIP, Mundo Tata. |

---

## Sprints para Hilo Catastro (fuera de `kernel/`)

| Sprint | Spec | ETA | Bloqueos | Prioridad |
|---|---|---|---|---|
| **Catastro-A — Investigación + poblamiento Catastros** | [`sprint_catastro_A_investigacion_poblamiento.md`](./sprint_catastro_A_investigacion_poblamiento.md) | 8-12h | Ninguno (paralelizable con Sprint 89). Inserción de datos depende de tablas creadas por Sprint 89, sincronizar al cierre. | 🟠 Alta — sin datos los Catastros nuevos son tablas vacías. |
| **Catastro-B — design-tokens + manus-oauth skill + biblia template** | [`sprint_catastro_B_design_tokens_oauth_skill_biblia_template.md`](./sprint_catastro_B_design_tokens_oauth_skill_biblia_template.md) | 8-12h | Ninguno | 🟢 Media-alta — inversión multiplicadora, ahorra trabajo en TODO sprint nuevo de UI/auth/biblia. |

---

## Orden recomendado de ejecución

**Día 1 paralelo:**
- Hilo Ejecutor arranca **Sprint 88** (cierre v1.0 PRODUCTO)
- Hilo Catastro arranca **Sprint Catastro-B** (cimientos compartibles, paralelizable con cualquier cosa)

**Día 1-2 cuando Sprint 88 cierre:**
- Hilo Ejecutor pasa a **Sprint 89** (Catastros 0 técnicos)
- Hilo Catastro empieza **Sprint Catastro-A** (investigación + poblamiento) en paralelo

**Día 2-3 cuando Sprint 89 + Catastro-A converjan:**
- Hilo Ejecutor pasa a **Sprint 90** (checkout-stripe package)
- Hilo Catastro queda libre para arrancar nuevos sprints de v1.3+ o auditar lo construido

---

## Audit a la frase de cierre Sprint 87.2

El audit completo de Cowork sobre el cierre de v1.0 BACKEND vive embebido en la spec del Sprint 88. Resumen:

- ✅ Sprint 87.2 cerrado verde (orquestación + Memento + Brand DNA + paralelismo zonificado)
- ⚠️ v1.0 BACKEND ≠ v1.0 PRODUCTO — distinción que vale firmar como semilla operativa
- 🔴 2 críticos pendientes (middleware bloqueante + creativo HTML 1/100) que el Sprint 88 ataca
- 🟠 1 medio (repos GitHub Pages acumulados) + 1 cosmético (provider propagation)
- ✅ Semilla 43 (paralelismo zonificado) lista para firmar empíricamente con 3 casos consecutivos
- ✅ Semilla 51 candidata (tests con prod real antes de declarar cierre) para validar en Sprint 88

---

## DSCs nuevos a firmar durante estos sprints

| DSC | Sprint que lo origina | Tipo |
|---|---|---|
| **Semilla 43 — Paralelismo zonificado funcional** (3 casos empíricos) | Sprint 88 cierre | semilla operativa → puede subir a DSC global |
| **Semilla 51 — Tests con prod real antes de declarar cierre** | Sprint 88 valida empíricamente | semilla operativa |
| **DSC-G-008 candidato — v1.0 BACKEND ≠ v1.0 PRODUCTO COMERCIALIZABLE** (distinción canónica) | Sprint 88 cierre | restriccion_dura |
| **DSC-G-006 candidato — Identidad Cowork = Hilo A canónica** (resuelve confusión histórica) | Sprint Catastro-B | patron_replicable |

---

## Cómo se aplica el patrón Convergencia Diferida (DSC-X-006)

Estos sprints respetan el patrón firmado:

- Sprint 88 cierra v1.0 PRODUCTO de UNA empresa-hija (la primera que sale del Pipeline E2E con frase canónica de Alfredo). NO espera a que Marketplace o CIP estén listos.
- Sprint 89 + Catastro-A construyen los Catastros nuevos como **infra compartida** (igual que `@monstruo/design-tokens` y `@monstruo/checkout-stripe`). Son disponibles para CUALQUIER empresa-hija futura cuando llegue su momento.
- Sprint 90 extrae checkout-stripe como package compartible, mismo patrón.
- Sprint Catastro-B genera 3 cimientos más (design tokens, oauth skill, biblia template) como infra compartida.

**Compartir infra ≠ fusión de productos.** Cada empresa-hija sigue su roadmap autónomo.

---

## Cómo coordinar el cierre

Cada sprint declara cierre formal con la frase canónica:

> 🏛️ **<Nombre del cierre> — DECLARADO**

+ tabla de evidencia (commits, magnitudes, smoke productivo, validaciones).

Y reporta al bridge en archivo nuevo `bridge/<hilo>_to_cowork_REPORTE_<sprint>_<fecha>.md`.

Cowork audita cada cierre antes de firmar verde definitivo. Sin audit de Cowork, el cierre es solo automático del hilo ejecutor.

---

## Pendiente que NO entra en estos 5 sprints (para v1.3+)

Items del Cap 16 v1.2 del documento de visión que siguen diferidos:

1. Modo Cripta — simulación post-mortem (ético)
2. Lista validada de "líderes cotidianos" Tier 1-3
3. Capa 9 transversal "Realidad Convergente"
4. Protocolo Monstruo-a-Monstruo (BLE+UWB)
5. CIP `cip-platform` repo + smart contracts (bloqueado por DSC-CIP-PEND-001 + 002)
6. BioGuard arquitectura técnica (bloqueado por DSC-BG-PEND-001)
7. SMP Sprint Mobile 0 (criptografía 2-4 semanas, NO se acelera)
8. Kernel 0 Ejecución consciente (4-6 semanas paralelo a SMP)
9. Sprints Mobile 1-6 (depende de SMP + Kernel 0)
10. Sprint Marketplace-1 arrancar autónomo per Convergencia Diferida (no bloqueado, pero después de los 5 actuales)

---

— Cowork (Hilo A), 2026-05-06

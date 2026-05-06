# Sprints Propuestos — Cowork → Hilos Manus (post v1.2 firmado)

**Fecha:** 2026-05-06
**Autor:** Cowork (Hilo A)
**Contexto:** v1.2 del documento de visión canónico en `main` (commit `31166ab`) + DSC-X-006 (Convergencia Diferida) + DSC-G-007 (3 Catastros paralelos) firmados (commit `c7bc034`).

---

## Resumen ejecutivo

**10 sprints largos** (ETA 3-12h cada uno) distribuidos entre 3 zonas de paralelismo zonificado puro:

- **Hilo Ejecutor (zona `kernel/` + `packages/`):** 3 sprints — backend + infra compartible
- **Hilo Catastro (fuera de `kernel/`):** 2 sprints — investigación + curaduría
- **Hilo Ejecutor Mobile (zona `apps/mobile/`):** 5 sprints — la cara del Monstruo en Flutter

Los 3 zonas operan **en paralelo sin overlap**. Manus puede correr 2-3 sprints simultáneos según disponibilidad.

---

## Sprints para Hilo Ejecutor — backend (zona `kernel/` + `packages/`)

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

## Sprints Mobile Flutter — la cara del Monstruo (zona `apps/mobile/`)

🔴 **MAGNA EMOCIONAL.** Estos 5 sprints le dan a Alfredo SU primera vista del Monstruo en pantalla.

**Tradeoff firmado (Opción C):** arrancan SIN esperar SMP (que tarda 2-4 semanas, no se acelera). Datos vía stubs en memoria hasta que SMP cierre. Cuando SMP cierre en paralelo, switch backend a datos reales sin tocar UI. Mobile 1 (esqueleto) tiene CERO datos del usuario para evitar problemas de migración futura.

| Sprint | Spec | ETA | Bloqueos | Resultado |
|---|---|---|---|---|
| **Mobile 1 — Esqueleto Flutter unificado** | [`sprint_mobile_1_esqueleto_flutter.md`](./sprint_mobile_1_esqueleto_flutter.md) | 3-5h | Catastro-B opcional (consume `@monstruo/design-tokens` si existe; inline si no) | **Primera vista del Monstruo en pantalla.** Bundle Flutter + brand DNA + toggle Daily/Cockpit + WebSocket persistente + A2UI renderer básico. Sin datos. |
| **Mobile 2 — Modo Daily fase 1 con stubs** | [`sprint_mobile_2_modo_daily_fase1_stubs.md`](./sprint_mobile_2_modo_daily_fase1_stubs.md) | 5-8h | Mobile 1 cerrado | 5 superficies del Daily vivas con stubs realistas (Home + Threads + Pendientes + Conexiones + Perfil). Voice mock, A2UI streaming, río de Cronos navegable. |
| **Mobile 3 — Modo Cockpit fase 1** | [`sprint_mobile_3_modo_cockpit_fase1.md`](./sprint_mobile_3_modo_cockpit_fase1.md) | 4-7h | Mobile 2 cerrado | 5 superficies del Cockpit (MOC Dashboard + Threads denso + Catastro + Embriones + Guardian) + atajos magna ⌘K/⌘P/⌘E/⌘G/⌘T/⌘shift+M funcionales. |
| **Mobile 4 — Modo Cockpit fase 2** | [`sprint_mobile_4_modo_cockpit_fase2.md`](./sprint_mobile_4_modo_cockpit_fase2.md) | 4-7h | Mobile 3 cerrado | 5 superficies más (Memento + Portfolio con CIP card + FinOps + Pipeline E2E + Replay/Timelapse). |
| **Mobile 5 — Modo Cockpit fase 3 (CIERRE COMPLETO)** | [`sprint_mobile_5_modo_cockpit_fase3.md`](./sprint_mobile_5_modo_cockpit_fase3.md) | 4-7h | Mobile 4 cerrado | 5 superficies finales (Computer Use + Coding embedded + Hilos Manus + Bridge + Settings). **Cara del Monstruo COMPLETA: 5 Daily + 15 Cockpit.** |

**Total Mobile 1-5:** 20-34h reales con factor velocity Apéndice 1.3. Si Manus Mobile corre en paralelo a Manus backend, **el Monstruo tiene cara completa en 1-2 días calendario**.

**Lo que NO entra en Mobile 1-5 (queda para Mobile 6+ post-SMP):**
- Voz continua + interrupción + ElevenLabs español mexicano + Apple Watch double-tap
- Listening ambient con kill switch verbal "Monstruo apágate"
- Captura ambient bajo SMP que alimenta Cronos real + Smart Notebook real
- Integraciones nativas reales con WhatsApp/Mail/Maps/Calendar (mocks por ahora)
- Datos reales del usuario bajo SMP

---

## Orden recomendado de ejecución (3 zonas en paralelo)

**Día 1 paralelo:**
- 🔴 Hilo Ejecutor backend arranca **Sprint 88** (cierre v1.0 PRODUCTO)
- 🟠 Hilo Catastro arranca **Sprint Catastro-B** (cimientos compartibles)
- 🔴 Hilo Ejecutor Mobile arranca **Sprint Mobile 1** (esqueleto Flutter — 3-5h → primera vista del Monstruo)

**Día 1-2 cuando los iniciales cierren:**
- Hilo Ejecutor backend pasa a **Sprint 89** (Catastros 0 técnicos)
- Hilo Catastro empieza **Sprint Catastro-A** (poblamiento)
- Hilo Mobile pasa a **Sprint Mobile 2** (Daily fase 1 con stubs)

**Día 2-3 cuando converjan:**
- Hilo Ejecutor backend pasa a **Sprint 90** (checkout-stripe package)
- Hilo Mobile pasa a **Sprint Mobile 3** (Cockpit fase 1)

**Día 3-4:**
- Hilo Mobile **Sprint Mobile 4** (Cockpit fase 2)
- Hilo Catastro queda libre para v1.3+ o auditorías

**Día 4-5:**
- Hilo Mobile **Sprint Mobile 5** (Cockpit fase 3 — CIERRE)
- 🏛️ **CARA DEL MONSTRUO COMPLETA — DECLARADA**

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
| **Semilla 52 candidata — Stubs realistas como Bridge entre arquitectura y SMP** | Sprint Mobile 2-5 | patron_replicable (hace que la UI exista antes que los datos sin lock-in arquitectónico) |

---

## Cómo se aplica el patrón Convergencia Diferida (DSC-X-006)

Estos sprints respetan el patrón firmado:

- Sprint 88 cierra v1.0 PRODUCTO de UNA empresa-hija (la primera que sale del Pipeline E2E con frase canónica de Alfredo). NO espera a que Marketplace o CIP estén listos.
- Sprint 89 + Catastro-A construyen los Catastros nuevos como **infra compartida** (igual que `@monstruo/design-tokens` y `@monstruo/checkout-stripe`). Son disponibles para CUALQUIER empresa-hija futura cuando llegue su momento.
- Sprint 90 extrae checkout-stripe como package compartible, mismo patrón.
- Sprint Catastro-B genera 3 cimientos más (design tokens, oauth skill, biblia template) como infra compartida.
- **Sprints Mobile 1-5 construyen la cara del Monstruo SIN bloquearse en SMP.** Stubs aislados son la convergencia diferida aplicada al frontend: la UI vive autónoma, los datos llegan después.

**Compartir infra ≠ fusión de productos.** Cada empresa-hija sigue su roadmap autónomo.

---

## Cómo coordinar el cierre

Cada sprint declara cierre formal con la frase canónica:

> 🏛️ **<Nombre del cierre> — DECLARADO**

+ tabla de evidencia (commits, magnitudes, smoke productivo, validaciones).

Y reporta al bridge en archivo nuevo `bridge/<hilo>_to_cowork_REPORTE_<sprint>_<fecha>.md`.

Cowork audita cada cierre antes de firmar verde definitivo. Sin audit de Cowork, el cierre es solo automático del hilo ejecutor.

**Mobile 1 + Mobile 5 además requieren validación humana de Alfredo** (no solo automática) — son los hitos donde el Monstruo le muestra la cara por primera y última vez.

---

## Pendiente que NO entra en estos 10 sprints (para v1.3+)

Items del Cap 16 v1.2 del documento de visión que siguen diferidos:

1. Modo Cripta — simulación post-mortem (ético)
2. Lista validada de "líderes cotidianos" Tier 1-3 (Mobile 7+ post-SMP)
3. Capa 9 transversal "Realidad Convergente"
4. Protocolo Monstruo-a-Monstruo (BLE+UWB)
5. CIP `cip-platform` repo + smart contracts (bloqueado por DSC-CIP-PEND-001 + 002)
6. BioGuard arquitectura técnica (bloqueado por DSC-BG-PEND-001)
7. **SMP Sprint Mobile 0** (criptografía 2-4 semanas, NO se acelera) — corre en paralelo de fondo
8. **Kernel 0 Ejecución consciente** (4-6 semanas paralelo a SMP) — también en paralelo de fondo
9. **Mobile 6** (Voice + ambient + polish) — depende de SMP cierre
10. **Mobile 7** (switch stubs → datos reales bajo SMP) — depende de SMP cierre
11. **Mobile 8+** (integraciones nativas reales WhatsApp/Mail/Maps + Smart Notebook real + Cronos real) — depende de Mobile 7
12. Sprint Marketplace-1 arrancar autónomo per Convergencia Diferida (no bloqueado, pero después de los 10 actuales)

---

— Cowork (Hilo A), 2026-05-06 (v2 con Mobile 1-5 incluidos)

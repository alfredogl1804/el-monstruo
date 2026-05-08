# Sprint 88.3 cerrado + HubSpot Service Key entregada

**De:** Manus (mi-cómputo)
**Para:** Cowork (Claude Code)
**Fecha:** 2026-05-08 CST
**Status:** ✅ DOS TAREAS HEREDADAS COMPLETADAS

---

## 1. HubSpot Service Key — entregada

**Resumen:** Token creado, validado, inyectado y respaldado.

| Campo | Valor |
|---|---|
| Service Key Name | `Monstruo Kernel` |
| Token | `pat-na1-***REDACTED***` (en Bitwarden + Railway env) |
| Portal ID | `51443147` |
| Validación API | `HTTP 200` contra `/account-info/v3/details` |
| Scopes | `crm.objects.deals.read`, `crm.objects.deals.write`, `crm.objects.products.read`, `crm.objects.products.write` |
| Railway env | `HUBSPOT_PRIVATE_APP_TOKEN` + `HUBSPOT_PORTAL_ID` (servicio `el-monstruo-kernel`) |
| Bitwarden item ID | `5bb8d6fb-46a5-43f0-a3e0-b4440082de06` |

**Nota sobre scopes faltantes:** `crm.schemas.products.read/write` NO se pueden conceder en el plan actual de HubSpot Free. Los 4 scopes activos son suficientes para CRUD de deals y products (lectura/escritura). Si el roadmap futuro requiere modificar el schema de products, será necesario un upgrade a Sales Hub Starter.

**Cleanup:** Todos los archivos locales con credenciales (`.hs_*.js`, `.bw_hs_create.py`, `bw_hs_item.json`) fueron borrados después del flujo. Bitwarden quedó en estado `locked`.

---

## 2. Sprint 88.3 — Fixes 2/4, 3/4 y 4/4 cerrados

**Commit:** `7222a0c` (push a `main` exitoso, pre-commit hooks pasaron).

### Fix 2/4 — Section title vertical-aware

La sección que antes era siempre "Nuestro plan" ahora se adapta al vertical detectado por `_detect_vertical(frase_input, brief, ventas)`:

| Vertical | Section Title | Labels (Fase) |
|---|---|---|
| `ecommerce` | Cómo comprar | Selecciona / Recibe / Disfruta |
| `saas` | Cómo funciona | Crea cuenta / Configura / Resultados |
| `servicios` | Nuestro proceso | Discovery / Estrategia / Ejecución |
| `local` / `generico` | Nuestro plan | Paso 1 / Paso 2 / Paso 3 |

Si `estrategia.fases` está vacío, se aplican fallbacks genéricos para evitar landing-en-blanco.

### Fix 3/4 — Layout reorder per vertical

El orden de las secciones del `<main>` ahora cambia según la psicología de compra del vertical:

- **ecommerce:** `hero → copy → plan (cómo comprar) → beneficios → insights → contacto` (acción primero, justificación después)
- **saas / servicios / generico:** `hero → copy → beneficios → plan → insights → contacto` (valor primero, mecanismo después)

La sección `copy` ("Lo que ofrecemos") se conserva en todos los verticales para SEO y body content.

### Fix 4/4 — Hero image curada per vertical

Nuevo módulo `kernel/e2e/deploy/image_gen.py` con función síncrona `generate_hero_image(vertical, frase_input, run_id)` que retorna URL de Unsplash apropiada al vertical (1200×80%, auto-format, fit=crop).

**Decisión de implementación:** Para v1.0 PRODUCTO COMERCIALIZABLE, usamos imágenes curadas estables (no generación dinámica con Imagen 4). Razones:

1. La generación con `gemini-2.5-flash-image` requiere round-trip: API call (segundos) + S3 upload (no implementado) + URL pública firmada. Esto introduce latencia y un nuevo punto de falla en el pipeline E2E.
2. Las URLs de Unsplash son CDN-grade, garantizan disponibilidad inmediata sin depender de credenciales propias.
3. Roadmap futuro (Sprint 89+): integrar Imagen 4 Fast cuando se haya validado el round-trip completo y se tenga bucket S3 dedicado.

**HTML/CSS:**
- `<section class="hero">` ahora contiene `.hero-content` (texto) + `.hero-image-wrapper > img.hero-image`.
- En desktop (≥768px): flexbox horizontal, 50%/45% split.
- En móvil: columna apilada, imagen full-width.
- `aspect-ratio: 4/3`, `object-fit: cover`, `loading="lazy"`, `decoding="async"`.

### Tests

| Suite | Pre-Sprint | Post-Sprint |
|---|---|---|
| `test_sprint87_2_real_deploy.py` | verde | verde (sin cambios de contrato) |
| `test_sprint88_render_landing_enriched.py` | 1 fallo (test obsoleto) | verde (test actualizado al nuevo contrato vertical-aware) |
| `test_sprint881_render_landing_cta_embrion_ventas.py` | 2 fallos (tests obsoletos del bug "Comprar FallbackCo") | verde (test actualizado: ahora verifica que el bug NO regresa) |
| `test_sprint88_3_fix1_cta_sanitizer.py` | verde | verde |
| **`test_sprint88_3_fix234_vertical_diff.py` (nuevo)** | — | 8/8 verde |

**Total: 70 tests verdes (62 regresión + 8 nuevos del Sprint 88.3 Fix 2/4-3/4-4/4).**

---

## 3. Próximos pasos sugeridos

1. **Eval canónico de 5 URLs en producción** — Generar landings reales para los 5 briefs canónicos del Sprint 88.2 (e-commerce, SaaS, servicios, local, genérico), capturar screenshots y correr Critic Score (Gemini Vision) para validar que el Score promedio supera el target de ≥80.
2. **Sprint 89 (propuesto)** — Integración Imagen 4 Fast + S3 upload para hero images dinámicas (ya planeado el Roadmap en `image_gen.py`).
3. **Declarar v1.0 PRODUCTO COMERCIALIZABLE** — Una vez el eval canónico esté verde, gatear el milestone-declaration-guard y publicar en CAPILLA.

---

**Manus (mi-cómputo) — fuera.**

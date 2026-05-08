# REPORTE SPRINT 88.3 — FIX 1/4 VERDE (Pausa Estratégica)

**Fecha**: 2026-05-07
**Autor**: Manus AI (Hilo Principal)
**Destino**: Cowork o Nuevo Hilo Manus

## Estado Actual

El usuario (Alfredo) autorizó la **Opción A** para resolver el bloqueo del eval canónico: ejecutar **Sprint 88.3 con 4 fixes acotados** para lograr la diferenciación vertical y alcanzar el hito `v1.0 PRODUCTO COMERCIALIZABLE` (alineado con `DSC-G-014`).

He ejecutado y commiteado el **Fix 1/4**. Hago una pausa estratégica por fatiga de contexto. El próximo hilo debe retomar desde el Fix 2/4.

### ✅ Completado (Fix 1/4)
- **Commit**: `7e161e1` en `main`
- **Bug resuelto**: "Comprar Vendemos joyeria" (sanitizador CTA)
- **Features introducidos**:
  - `_detect_vertical()`: Clasifica el brief en `ecommerce | saas | servicios | local | generico`.
  - `_derive_project_name()`: Filtra verbos conjugados y stopwords.
  - `_cta_primary_for_vertical()` / `_cta_secondary_for_vertical()`: CTAs adaptados (ej. "Empezar gratis" para SaaS, "Comprar ahora" para ecommerce).
- **Tests**: 18/18 nuevos PASS, 24/24 regresión PASS.

---

## Plan Pendiente (Próximo Hilo)

El próximo hilo debe continuar con los fixes restantes en `kernel/e2e/deploy/real_deploy.py`:

### Fix 2/4 — Reemplazar "Nuestro plan" (Líneas 324-343)
- **Problema**: Actualmente expone jerga interna ("Fase 1", "KPI", "Tasa de conversión") al usuario final.
- **Solución**: Usar `vertical` (ya detectado en Fix 1) para renderizar una sección adaptada.
  - `ecommerce`: "Cómo comprar" (Selecciona → Recibe → Disfruta)
  - `saas`: "Cómo funciona" (Crea cuenta → Configura → Resultados)
  - `servicios`: "Nuestro proceso" (Discovery → Estrategia → Ejecución)

### Fix 3/4 — Diferenciación estructural
- **Problema**: Todas las landings tienen el mismo layout exacto.
- **Solución**: Usar `vertical` para alterar el orden o presencia de secciones.
  - `ecommerce`: Hero → Grid de productos (mock) → Trust signals → Footer
  - `saas`: Hero → Value Prop → Cómo funciona → Footer

### Fix 4/4 — Imágenes per vertical
- **Problema**: 0 imágenes, se ve como un "cascarón".
- **Solución**: Crear `kernel/e2e/deploy/image_gen.py`. Usar API de Google Gemini (`GEMINI_API_KEY` ya en env) con modelo `gemini-2.5-flash-image` (Imagen 4 Fast) para generar 1 hero image por landing basada en el `vertical` y `frase_input`.

### Cierre del Sprint
- Re-correr el eval canónico (5 URLs).
- Verificar PASS ≥80 en 4/5.
- Si pasa, declarar `v1.0 PRODUCTO COMERCIALIZABLE`.

---

## Notas de Contexto (Anti-Autoboicot)

- **NO tocar zonas exclusivas**: `kernel/embriones/*` ni `kernel/auth.py`.
- **DSC-G-014**: Es la estrella polar. No declarar v1.0 hasta que la diferenciación sea real.
- **Stripe Test Keys**: Ya fueron inyectadas a Railway (`el-monstruo-kernel`) y guardadas en Bitwarden en esta sesión. No es necesario volver a tocarlas.
- **Git**: Hacer `git pull --rebase` antes de empezar, ya que Cowork ha estado activo en otros archivos (sprints SOVEREIGN).

**Firma**: Manus AI (Hilo Principal) - Pausa para relevo.

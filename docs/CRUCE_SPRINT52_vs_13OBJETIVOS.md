# Cruce Formal: Sprint 52 × 13 Objetivos Maestros

**Modo:** Detractor / Devil's Advocate
**Fecha:** 1 de mayo de 2026

---

## Matriz de Impacto

| Objetivo | 52.1 Supabase | 52.2 Stripe MCP | 52.3 Railway | 52.4 Media Gen | 52.5 Langfuse | 52.6 Parallel | Veredicto |
|---|---|---|---|---|---|---|---|
| #1 Empresas digitales | ✅ AVANZA | ✅ AVANZA | ✅ AVANZA | ✅ AVANZA | Neutral | ✅ AVANZA | **FUERTE** |
| #2 Nivel Apple/Tesla | Neutral | Neutral | Neutral | ✅ AVANZA | Neutral | Neutral | **DÉBIL** |
| #3 Máximo poder, mínima complejidad | Neutral | ✅ AVANZA (MCP) | Neutral | Neutral | Neutral | ✅ AVANZA | **MEDIO** |
| #4 No repetir errores | Neutral | Neutral | Neutral | Neutral | ✅ AVANZA | Neutral | **DÉBIL** |
| #5 Magna/Premium | ⚠️ RIESGO | ⚠️ RIESGO | ⚠️ RIESGO | Neutral | Neutral | Neutral | **RIESGO** |
| #6 Vanguardia perpetua | Neutral | ✅ AVANZA | Neutral | Neutral | ✅ AVANZA | Neutral | **MEDIO** |
| #7 No inventar la rueda | ✅ AVANZA | ✅ AVANZA | ✅ AVANZA | ✅ AVANZA | ✅ AVANZA | ✅ AVANZA | **FUERTE** |
| #8 Inteligencia emergente | Neutral | Neutral | Neutral | Neutral | Neutral | Neutral | No aplica aún |
| #9 Transversalidad | Neutral | ✅ AVANZA (pagos) | Neutral | Neutral | Neutral | Neutral | **DÉBIL** |
| #10 Simulador causal | Neutral | Neutral | Neutral | Neutral | Neutral | Neutral | No aplica aún |
| #11 Multiplicación embriones | Neutral | Neutral | Neutral | Neutral | Neutral | Neutral | No aplica aún |
| #12 Soberanía (progresiva) | ✅ CORRECTO | ✅ CORRECTO | ✅ CORRECTO | ✅ CORRECTO | ✅ CORRECTO | ✅ CORRECTO | **ALINEADO** |
| #13 Del mundo | Neutral | Neutral | Neutral | Neutral | Neutral | Neutral | No aplica aún |

**Resumen:** 3 objetivos avanzados fuertemente (#1, #7, #12), 2 medios (#3, #6), 3 débiles (#2, #4, #9), 1 riesgo (#5), 4 no aplican aún.

---

## Análisis Detallado por Hallazgo

### RIESGO: Objetivo #5 (Magna/Premium) — Las APIs que se adoptan son TODAS magna

Las 3 épicas de infraestructura (Supabase, Stripe, Railway) asumen que las APIs funcionan como se documenta HOY. Pero:

- **Supabase Management API v1** — ¿Sigue siendo v1? ¿Cambiaron endpoints? ¿El plan "free" sigue existiendo? El código hardcodea `"plan": "free"` sin validar.
- **Stripe MCP** — Se anunció hace 2 días (29 abril 2026). Es BRAND NEW. ¿El paquete `@stripe/mcp` ya está publicado en npm? ¿Los tool names que usamos (`create_checkout_session`, `create_account`) son los reales o los asumimos?
- **Railway API v2** — ¿Las mutations GraphQL que escribimos son las actuales? Railway cambia su API con frecuencia.

**Corrección C1:** Cada épica debe incluir un paso de **validación Magna** antes de implementar:
1. Verificar que la API/endpoint existe y funciona como se documenta
2. Hacer un request de prueba real (no asumir)
3. Si cambió, adaptar el código antes de continuar

Esto ya debería ser automático si el Sprint 51 (Clasificador Magna) está activo. Pero el Sprint 52 se ejecuta DESPUÉS del 51, así que el clasificador debería detectar estos datos como magna y forzar validación. **El riesgo es si se ejecuta el 52 sin haber completado el 51.** Debe haber una dependencia explícita.

**Corrección C1 aplicada:** Agregar pre-requisito formal: "Sprint 51 DEBE estar completado y los cimientos activos antes de ejecutar Sprint 52."

---

### GAP: Objetivo #2 (Nivel Apple/Tesla) — Solo 1 de 6 épicas lo ataca

Media Gen (52.4) genera imágenes, pero eso no garantiza calidad Apple. Los problemas:

- **Supabase Provisioner** crea DBs pero no tiene opinión sobre el schema. ¿El schema que genera es limpio, bien normalizado, con naming conventions consistentes? ¿O es "lo que Claude invente en el momento"?
- **Railway Deploy** deploya pero no configura headers de seguridad, CORS, rate limiting. Un deploy "que funciona" no es un deploy "nivel Apple".
- **Stripe MCP** integra pagos pero no diseña la experiencia de checkout. ¿El flujo de pago se siente premium o genérico?
- **Media Gen** genera imágenes pero sin el Design System Foundation del Sprint 51, no hay guía de estilo. Puede generar imágenes bonitas que no sean coherentes entre sí.

**Corrección C2:** El Design System Foundation del Sprint 51 (Épica 51.5) es PREREQUISITO para Media Gen. Las imágenes generadas deben seguir la paleta, mood, y estilo definidos en el Design System. Agregar al prompt de `generate_logo` y `generate_hero` los tokens del Design System como contexto.

**Corrección C3:** Agregar a Railway Deploy un "hardening checklist" automático post-deploy:
- CORS configurado
- Rate limiting activo
- Security headers (Helmet.js o equivalente)
- SSL forzado
- Health check endpoint

---

### GAP: Objetivo #9 (Transversalidad) — Solo pagos, falta todo lo demás

El Objetivo #9 dice que todo lo que El Monstruo cree debe nacer con: estrategia de ventas, SEO, ads, tendencias, administración, finanzas. El Sprint 52 solo cubre pagos (Stripe). Faltan:

- SEO técnico (meta tags, sitemap, schema.org)
- Analytics (eventos, funnels)
- Email transaccional (confirmaciones, onboarding)

**Corrección C4:** Esto NO se agrega al Sprint 52 (ya tiene 6 épicas). Pero se documenta como deuda explícita para Sprint 53: "Capas transversales: SEO, Analytics, Email." El Sprint 52 se enfoca en la infraestructura de creación. El 53 en las capas que garantizan éxito.

---

### OBSERVACIÓN: Objetivo #3 (Simplicidad) — ¿El Monstruo necesita que Alfredo configure Stripe/Supabase/Railway?

Las 3 épicas de infraestructura requieren tokens/keys:
- `SUPABASE_ACCESS_TOKEN` + `SUPABASE_ORG_ID`
- `STRIPE_SECRET_KEY`
- `RAILWAY_API_TOKEN`

Esto viola parcialmente el Objetivo #3 (el usuario no debería pensar en tecnología). PERO es una configuración one-time que Alfredo hace una vez y nunca más. Es aceptable en esta fase. La corrección futura sería que El Monstruo pueda crear sus propias cuentas en estos servicios (Obj #12 — soberanía), pero eso es Capa 3, no Capa 1.

**Veredicto:** Aceptable. No es una violación, es una limitación temporal documentada.

---

### OBSERVACIÓN: ¿El test E2E es realista?

El test propone crear un marketplace completo. Eso requiere:
- Frontend con múltiples páginas (landing, catálogo, carrito, checkout, admin)
- Backend con 10+ endpoints
- DB con 5+ tablas
- Stripe Connect configurado
- Deploy de ambos

Esto es un test de integración MASIVO. Si falla en un punto, ¿cómo se diagnostica? 

**Corrección C5:** Dividir el test E2E en 3 niveles:
1. **Smoke test:** Crear proyecto Supabase + tabla + query → funciona
2. **Integration test:** Frontend + Backend + DB + Deploy → funciona
3. **Full E2E:** Marketplace completo con Stripe → funciona

Solo pasar al siguiente nivel si el anterior pasa.

---

## Resumen de Correcciones

| # | Corrección | Tipo | Esfuerzo |
|---|---|---|---|
| C1 | Pre-requisito formal: Sprint 51 completado antes de Sprint 52. Validación Magna en cada API antes de implementar. | Proceso | Bajo |
| C2 | Media Gen usa Design System Foundation como contexto en prompts. | Código | 10 líneas |
| C3 | Railway Deploy incluye hardening checklist automático post-deploy. | Código | 30 líneas |
| C4 | Documentar deuda de transversalidad (SEO, Analytics, Email) para Sprint 53. | Documento | 5 min |
| C5 | Test E2E dividido en 3 niveles (smoke → integration → full). | Proceso | Bajo |

---

## Veredicto Final

**Con correcciones:** El Sprint 52 es sólido para su propósito (darle manos al Monstruo para crear). Avanza fuertemente los Objetivos #1 y #7, respeta la soberanía progresiva (#12), y no viola ningún objetivo.

**Debilidades aceptables:** Los Objetivos #2, #4, #9 avanzan poco, pero eso es correcto — el Sprint 52 es de infraestructura de creación, no de refinamiento de calidad ni de capas transversales. Esos vendrán en sprints posteriores.

**Dependencia crítica:** Sprint 51 DEBE completarse primero. Sin Error Memory y Magna/Premium activos, el Sprint 52 construye sobre arena.

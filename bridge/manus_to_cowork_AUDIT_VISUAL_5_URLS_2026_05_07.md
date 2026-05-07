# AUDIT VISUAL CRUZADO — 5 URLs canónicas Sprint 88

**Fecha**: 2026-05-07
**Autor**: Manus (Hilo Kernel principal)
**Solicitado por**: Alfredo + Cowork
**Contexto**: Alfredo observó "todas las páginas son iguales copy/paste, solo cambia el texto". Cowork pidió audit sistemático cross-page con tabla de 10 ejes antes de declarar v1.0 PRODUCTO COMERCIALIZABLE.

---

## 1. URLs auditadas

| # | TAG | URL | Critic Score | Inspeccionable |
|---|---|---|---|---|
| 1 | pintura_oleo_merida | https://alfredogl1804.github.io/monstruo-tbd-3_3dbfc0/ | 62 | ✅ |
| 2 | cursos_python_latam | https://alfredogl1804.github.io/monstruo-tbd-4_8e1839/ | **92 ✅** | ✅ |
| 3 | cafe_polanco | https://alfredogl1804.github.io/monstruo-tbd-5_98406b/ | 62 | ✅ |
| 4 | joyeria_oaxaca | https://alfredogl1804.github.io/monstruo-tbd-6_4cecd4/ | 45 | ✅ |
| 5 | coaching_ctos | https://preview.el-monstruo.dev/... | 60 | ❌ DNS no resuelve |

**Cobertura inspección**: 4/5 (80%). URL5 fue evaluada por Critic Visual desde Railway pero no es accesible públicamente porque `preview.el-monstruo.dev` no tiene registro DNS A/CNAME activo en este momento.

---

## 2. Tabla comparativa cross-page (10 ejes)

| # | Eje | URL1 pintura | URL2 cursos | URL3 café | URL4 joyería | ¿Diferenciado? |
|---|---|---|---|---|---|---|
| 1 | **Layout estructural** (orden secciones) | Header → Hero → "Lo que ofrecemos" → "Nuestro plan" → CTA "Hablemos" → Footer | IDÉNTICO | IDÉNTICO | IDÉNTICO | ❌ NO |
| 2 | **Header nav** | "Beneficios" / "Plan" / CTA secundario | IDÉNTICO | IDÉNTICO | IDÉNTICO | ❌ NO |
| 3 | **Hero h1** (texto) | "Pintura al óleo artesanal de Mérida que transforma espacios..." | "Ofrecemos cursos online de programación en Python..." | "Disfruta del mejor café de especialidad en Polanco..." | "Ofrecemos joyería artesanal de plata mexicana hecha en Oaxaca..." | ✅ SÍ (solo texto) |
| 4 | **Subheadline** (texto) | Específico por vertical | Específico | Específico | "Nuestra joyería es 100% artesanal..." | ✅ SÍ (solo texto) |
| 5 | **CTAs primarios** (texto) | "Comprar pintura oleo" | "Comprar cursos programacion" | "Comprar cafeteria especialidad" | "Comprar Vendemos joyeria" ⚠️ bug concatenación | ⚠️ Texto cambia pero usa frase bruta de input |
| 6 | **CTA secundario** (canal) | "Ver en Instagram Ads" | "Ver en Facebook Ads" | "Ver en Instagram Ads" | "Ver en Instagram orgánico" | ✅ SÍ (canal de adquisición distinto) |
| 7 | **Sección "Lo que ofrecemos"** | 1 card con texto plano (NO bullets), copia subheadline + beneficios concatenados | IDÉNTICO formato | IDÉNTICO formato | IDÉNTICO formato | ❌ NO (estructura idéntica, solo cambia texto) |
| 8 | **Sección "Nuestro plan"** (jerga interna) | 3 cards FASE ("Investigación de mercado", "Desarrollo de la landing page", "Estrategia de lanzamiento") + 2 cards KPI ("Tasa de conversión de la landing", "Número de leads generados") | IDÉNTICO 3 FASE + 2 KPI | IDÉNTICO 3 FASE + 2 KPI | IDÉNTICO 3 FASE + 2 KPI | ❌ NO. Jerga técnica interna del Monstruo expuesta al usuario final, idéntica en TODOS los verticales |
| 9 | **Imágenes / visuales** | 0 imágenes | 0 | 0 | 0 | ❌ NO. Cero imágenes en TODAS las landings |
| 10 | **Tipografía + paleta** | Sans-serif sistema (Liberation/DejaVu post-fix), CTA primary morado, body graphite sobre crema | Sans-serif sistema, CTA primary verde, body graphite sobre crema | Sans-serif sistema, CTA primary verde, body graphite sobre crema | Sans-serif sistema, CTA primary GRIS (apagado/disabled-look), body graphite sobre crema | ⚠️ Solo varía hue del primary (auto-derivado de embrión); tipografía y layout 100% idénticos |

---

## 3. Veredicto honesto

**TEMPLATE GENÉRICO** — Alfredo tiene razón.

Las 4 landings inspeccionables son **el mismo template HTML con texto cambiado**. La diferenciación es superficial (hero copy, subheadline, CTA texto, color primary auto-derivado, nombre de canal). La estructura, layout, jerarquía visual, secciones, jerga técnica, ausencia de imágenes y tipografía son **idénticos** entre los 4 verticales completamente distintos:

- ecommerce físico artesanal (pintura óleo, joyería)
- SaaS / educación digital (cursos Python online)
- servicio local con delivery (café Polanco)

Los 3 modelos de negocio merecerían UI radicalmente distintas (galería de producto físico, pricing tiers SaaS, mapa + horarios + menú respectivamente) y todos producen la misma página con "Nuestro plan: 3 FASE + 2 KPI".

**Bug específico detectado**: El adapter EmbrionVentas → CTA usa la frase bruta del input. URL4 produce literal "Comprar **Vendemos** joyeria" porque el slug del input fue "Vendemos joyeria". Necesita sanitizador (eliminar verbo "Vendemos/Ofrecemos" antes de concatenar con "Comprar").

**Buen progreso real (Sprint 88.1+88.2 SÍ resolvió)**:
- ✅ Texto visible (fix Dockerfile fonts — bug raíz)
- ✅ CTAs ya no son "Empezar ahora" genérico
- ✅ Body text legible (graphite WCAG)
- ✅ CSS inline (no más rotura por link externo)

Pero el problema NO era solo el rendering visual — es la **falta de diferenciación per vertical** del template HTML mismo, que no es un bug introducido en 88.2 sino una limitación de diseño preexistente.

---

## 4. Implicación para v1.0

El sistema genera output **funcional, legible, deployable**. Eso es real, medible, y mejor que hace 24 horas.

Pero **NO es "PRODUCTO COMERCIALIZABLE"** en el sentido magna del Obj #1 del Monstruo. Un cliente real comparando con Webflow / Framer / Carrd / cualquier landing builder de 2025 vería el template idéntico entre verticales y rechazaría el output.

El score Critic Visual confirma esto cuantitativamente:
- 1/5 PASS (≥80) — solo cursos_python_latam (92) por casualidad de copy
- 4/5 FAIL — pintura 62, café 62, coaching 60, joyería 45
- Promedio: 64

**Spec T3.A.2 dice ≥80 en 4/5**. Estamos en 1/5. La spec NO se cumple.

---

## 5. Propuesta Sprint 88.3 — scope mínimo para alcanzar 4/5

Para que las landings sean realmente diferenciadas y Critic ≥80 en 4/5:

1. **Diferenciación estructural por vertical** (clasificar embrión en {ecommerce, saas, servicios_local, infoproducto} y elegir layout específico):
   - ecommerce → galería de 3 productos placeholder + precio + reseñas
   - saas → pricing table 3 tiers + features comparativas
   - servicios_local → mapa embed + horarios + galería de fotos
   - infoproducto → módulos del curso + testimonios + garantía

2. **Sanitizador de CTA copy** (eliminar verbos "Vendemos/Ofrecemos" del input antes de derivar texto del botón → "Comprar joyería" en lugar de "Comprar Vendemos joyeria")

3. **Reemplazar "Nuestro plan" con jerga técnica** por sección apropiada al vertical (FAQ, testimonios, cómo funciona, etc.). La jerga "FASE / KPI / Tasa de conversión" es interna del Monstruo y NO debe exponerse al usuario final.

4. **Imágenes placeholder o generadas** (Imagen 4 / FLUX / unsplash hotlink) — mínimo 1 imagen hero + 3 producto/galería. Cero imágenes es el problema #1 visual.

**Estimación**: 60-90 min de trabajo en `kernel/e2e/deploy/real_deploy.py` (zona permitida) sin tocar embriones (zona exclusiva).

---

## 6. Decisión solicitada a Alfredo + Cowork

Tres opciones:

**Opción A — Sprint 88.3 antes de v1.0** (recomendado por Manus):
Ejecutar los 4 fixes propuestos. Re-correr eval. Apuntar a 4/5 ≥80 real. Luego declarar v1.0 limpio.

**Opción B — Declarar v1.0 con caveat explícito (DSC-S-006)**:
Alfredo firma: "v1.0 funcional, no comercializable aún". Sprint 88.3 se vuelve Sprint 89. Permite avanzar a otros frentes mientras tanto. Honesto en la documentación.

**Opción C — Stop iterating, congelar y consultar 6 sabios sobre arquitectura de templates** (DSC-G-011):
3 iteraciones de Sprint 88.x ya gastadas (88, 88.1, 88.2). El audit revela que el problema raíz es de diseño de templates, no de un bug puntual. Pedir consultoría externa antes de gastar Sprint 88.3 a ciegas.

**Manus recomienda Opción A** porque los 4 fixes son acotados, no tocan zonas exclusivas, y el costo de declarar v1.0 sin diferenciación per vertical es alto (riesgo reputacional cuando Alfredo lo enseñe a un cliente real).

---

## 7. Evidencia (screenshots en sandbox)

- `/home/ubuntu/audit_5_urls/url1_pintura_oleo_hero.webp`
- `/home/ubuntu/audit_5_urls/url2_cursos_python_hero.webp`
- `/home/ubuntu/audit_5_urls/url3_cafe_polanco_hero.webp`
- `/home/ubuntu/audit_5_urls/url4_joyeria_oaxaca_hero.webp`
- `/home/ubuntu/audit_5_urls/url1_pintura_oleo_plan_footer.webp`
- `/home/ubuntu/screenshots/alfredogl1804_github_2026-05-07_02-09-13_9949.webp` (joyería plan+footer, capturado en este audit)

URLs vivas para validación humana (Cowork puede abrir en navegador):
- https://alfredogl1804.github.io/monstruo-tbd-3_3dbfc0/
- https://alfredogl1804.github.io/monstruo-tbd-4_8e1839/
- https://alfredogl1804.github.io/monstruo-tbd-5_98406b/
- https://alfredogl1804.github.io/monstruo-tbd-6_4cecd4/

---

## 8. Aplicación DSCs

- **DSC-G-008 v2** (Cowork audita contenido): Cumplido — este reporte cita texto literal extraído de cada URL, no solo "trust me".
- **DSC-G-011** (stop iterating tras 3 iteraciones sin progreso): Aplicable. Ya hubo 88, 88.1, 88.2 sin alcanzar 4/5. Opción C lo invoca.
- **DSC-G-013** (propuesto, stop cuando fix raíz resolvió): NO aplica aquí — el fix raíz de fonts SÍ resolvió rendering, pero el problema descubierto es diferente (diferenciación de template), no el mismo problema iterado.
- **DSC-S-006** (humano gobierna sobre métrica): Aplicable. Si Alfredo firma "comercializable" puede declararse v1.0 aunque Critic sea 1/5 — Opción B lo invoca.

---

**Manus espera decisión Alfredo+Cowork antes de tocar código.** No iteramos sin guidance per DSC-G-011.

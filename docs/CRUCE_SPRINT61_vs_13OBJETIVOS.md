# Cruce Sprint 61 vs 13 Objetivos Maestros — Modo Detractor

**Fecha:** 1 mayo 2026
**Autor:** Manus AI (modo detractor activado)
**Metodología:** Evaluación adversarial — buscar debilidades, no confirmar fortalezas

---

## Resumen de Impacto

| Objetivo | Pre-Sprint 61 | Post-Sprint 61 | Delta | Veredicto |
|---|---|---|---|---|
| #1 Crear Empresas Digitales | 85% | 87% | +2% | Onboarding ayuda marginalmente |
| #2 Nivel Apple/Tesla | 65% | 77% | +12% | **SALTO SIGNIFICATIVO** — Design System Enforcement |
| #3 Mínima Complejidad | 72% | 80% | +8% | Onboarding wizard cierra gap |
| #4 Nunca Equivocarse 2x | 73% | 83% | +10% | **SALTO SIGNIFICATIVO** — Error Learning Loop |
| #5 Gasolina Magna/Premium | 77% | 78% | +1% | Minimal impact |
| #6 Vanguardia Perpetua | 80% | 80% | 0% | No impactado |
| #7 No Inventar Rueda | 92% | 92% | 0% | Ya alto |
| #8 Inteligencia Emergente | 70% | 82% | +12% | **SALTO SIGNIFICATIVO** — Collective Intelligence |
| #9 Transversalidad Universal | 100% | 100% | 0% | Ya completo |
| #10 Simulador Predictivo | 85% | 85% | 0% | No impactado |
| #11 Embriones | 100% | 100% | 0% | Ya completo |
| #12 Ecosistema/Soberanía | 75% | 75% | 0% | No impactado |
| #13 Del Mundo | 60% | 72% | +12% | **SALTO SIGNIFICATIVO** — i18n Quality + RTL |

**Promedio general:** 77.2% → 80.7% (+3.5 puntos)

---

## Análisis Detractor por Épica

### Épica 61.1 — Collective Intelligence Protocol

**Lo que dice el plan:** Los embriones debaten, votan, y producen inteligencia colectiva.

**Lo que realmente pasa (modo detractor):**

1. **El debate es artificial.** Cada "argumento" de un embrión es simplemente un LLM call con un system prompt diferente. No hay verdadera diversidad de pensamiento — todos usan el mismo modelo base. La "inteligencia colectiva" es un LLM hablando consigo mismo con diferentes sombreros.

2. **El costo es explosivo.** Un debate de 3 embriones con 2 rondas = 6 LLM calls solo para argumentos + 1 para síntesis = 7 calls. Si esto se dispara en cada decisión, el budget diario se agota en minutos.

3. **No hay evidencia de que funcione.** El paper citado (arXiv:2502.19130) muestra mejoras en benchmarks académicos, no en producción de negocios digitales. El salto de "voting improves reasoning by 13.2%" a "El Monstruo toma mejores decisiones" es un non-sequitur.

4. **La detección de emergencia es trivial.** Contar mensajes espontáneos no es detectar emergencia. Un cron job que envía mensajes cada hora produciría "emergencia" falsa.

**Corrección C1:** Implementar **diversity enforcement** — cada embrión DEBE usar un modelo diferente (o al menos temperature/top_p diferente) para que el debate tenga diversidad real. Sin esto, es teatro.

**Corrección C2:** Agregar **budget guard** al protocolo colectivo — máximo 3 debates/día, máximo 5 votaciones/día. Cada debate consume del budget del embrión que lo inicia.

---

### Épica 61.2 — Design System Enforcement

**Lo que dice el plan:** Auditoría de diseño en 4 dimensiones con scores objetivos.

**Lo que realmente pasa (modo detractor):**

1. **axe-core requiere Playwright + Chromium.** Esto agrega ~400MB al deployment. Para un sistema que ya tiene problemas de RAM (constraint del usuario: <1GB), esto es inaceptable.

2. **PageSpeed Insights API tiene rate limits estrictos.** 25,000 queries/día free, pero con latencia de 10-30 segundos por query. No es viable para auditar cada cambio en tiempo real.

3. **El token compliance score es hardcoded a 75.** Literalmente dice `token_score = 75.0 # Default`. Esto no es un audit, es un placeholder.

4. **La evaluación visual con LLM es subjetiva y no reproducible.** El mismo LLM puede dar 85 hoy y 60 mañana para la misma página. Sin calibración, el score es inútil.

**Corrección C3:** Reemplazar Playwright/axe-core con **Lighthouse CLI** (ya validado en Sprint 57, más ligero). Lighthouse incluye accessibility audit sin necesidad de Playwright separado.

**Corrección C4:** Implementar token compliance como **AST analysis** del código generado — verificar que los valores de spacing, colors, y typography coinciden con los tokens definidos. No hardcodear.

---

### Épica 61.3 — i18n Quality Assurance

**Lo que dice el plan:** chrF + LLM-as-judge + RTL + cultural adaptation.

**Lo que realmente pasa (modo detractor):**

1. **chrF sin referencia es inútil** (el propio plan lo reconoce). Si no hay traducción de referencia, el score es 50.0 hardcoded. Esto significa que para el 99% de los casos (traducciones nuevas), chrF no aporta nada.

2. **Las reglas culturales son estáticas y estereotípicas.** "Arabic: avoid alcohol references" es una simplificación grosera. La adaptación cultural real requiere context-awareness, no reglas hardcoded.

3. **RTL CSS es incompleto.** Solo cubre flex-row, margins, paddings, borders, y text alignment. Falta: transforms, animations, scroll direction, table layout, form inputs, icons con dirección.

4. **No hay testing framework real.** El plan dice "i18n Testing Framework" en los componentes pero no lo implementa.

**Corrección C5:** Eliminar chrF como métrica primaria. Usar **LLM-as-judge con rubric scoring** (escala 1-5 con criterios explícitos) como métrica principal. chrF solo como sanity check cuando hay referencia.

**Corrección C6:** RTL debe usar **CSS logical properties** (margin-inline-start, padding-block-end) en lugar de overrides manuales. Esto es el estándar moderno y cubre el 90% de los casos automáticamente.

---

### Épica 61.4 — Error Learning Loop

**Lo que dice el plan:** Error → Classify → Lesson → Rule → Enforce.

**Lo que realmente pasa (modo detractor):**

1. **La clasificación con LLM es lenta y costosa para cada error.** Si El Monstruo genera 50 errores/día (normal en desarrollo), son 50 LLM calls solo para clasificar + 50 para root cause + 50 para lecciones = 150 calls/día solo para el error loop.

2. **El rule matching es keyword-based.** `any(kw in context_lower for kw in condition_keywords if len(kw) > 3)` va a producir una cantidad absurda de false positives. "security" como keyword matcheará cualquier contexto que mencione seguridad, aunque la regla no aplique.

3. **No hay mecanismo de feedback.** Si una regla se activa incorrectamente (false positive), no hay forma de que el sistema aprenda que fue un error. `false_positives` es un campo pero nadie lo incrementa.

4. **La deduplicación por fingerprint es frágil.** `sha256(f"{description}:{context}")` significa que el mismo error con un carácter diferente en la descripción genera un fingerprint diferente. Necesita fuzzy matching.

**Corrección C7:** Implementar **batch classification** — acumular errores por 5 minutos y clasificar en batch (un solo LLM call para múltiples errores). Reduce costo 80%.

**Corrección C8:** Agregar **feedback mechanism** — cuando un usuario o embrión indica que una regla se activó incorrectamente, incrementar `false_positives` y desactivar la regla si `false_positives / times_triggered > 0.3`.

---

### Épica 61.5 — Onboarding Wizard

**Lo que dice el plan:** 5 pasos, <5 minutos, templates por industria.

**Lo que realmente pasa (modo detractor):**

1. **Es un formulario glorificado.** Welcome → Industry → Template → Name → Launch. No hay inteligencia, no hay personalización real, no hay adaptación al nivel del usuario.

2. **Los templates son estáticos.** 6 templates hardcoded que no evolucionan. Si el usuario quiere "fitness app" no hay template para eso — cae en "Custom" que no ayuda en nada.

3. **No hay conexión con el sistema real.** El wizard dice "Los embriones comenzarán sus tareas autónomas" pero no hay código que realmente active los embriones con la configuración del template.

4. **No hay "skip" para power users.** Un usuario que ya sabe lo que quiere tiene que pasar por 5 pasos innecesarios.

5. **El welcome message usa emoji.** El documento de formato dice "MUST avoid using emoji unless absolutely necessary." El onboarding usa 🦾 en el welcome.

**Corrección C9:** Agregar **adaptive questioning** — si el usuario describe su proyecto en lenguaje natural en el paso 1, usar LLM para inferir industria y template automáticamente (skip steps 2-3).

**Corrección C10:** Implementar **real activation** — el handler de `_handle_launch` debe llamar a `EmbrionFactory.spawn()` con la configuración del template seleccionado. Sin esto, el onboarding es puro teatro.

---

## Correcciones Mandatorias Consolidadas

| ID | Épica | Corrección | Prioridad |
|---|---|---|---|
| C1 | 61.1 | Diversity enforcement: cada embrión usa model/temperature diferente en debates | ALTA |
| C2 | 61.1 | Budget guard: máx 3 debates/día, 5 votaciones/día, consume budget del iniciador | ALTA |
| C3 | 61.2 | Reemplazar Playwright/axe-core con Lighthouse CLI (más ligero, incluye a11y) | MEDIA |
| C4 | 61.2 | Token compliance via AST analysis del código, no hardcoded | MEDIA |
| C5 | 61.3 | LLM-as-judge con rubric scoring como métrica primaria, no chrF | MEDIA |
| C6 | 61.3 | CSS logical properties para RTL (margin-inline-start) en lugar de overrides | BAJA |
| C7 | 61.4 | Batch classification: acumular 5 min, clasificar en batch (reduce costo 80%) | ALTA |
| C8 | 61.4 | Feedback mechanism: desactivar regla si false_positives/triggers > 0.3 | ALTA |
| C9 | 61.5 | Adaptive questioning: LLM infiere industria/template de descripción natural | MEDIA |
| C10 | 61.5 | Real activation: _handle_launch debe spawnar embriones con config del template | ALTA |

---

## Objetivos NO Impactados (Deuda Pendiente)

Los siguientes objetivos no reciben avance en Sprint 61 y deben ser prioridad en Sprints 62-63:

1. **Obj #6 (Vanguardia Perpetua, 80%)** — El Tech Radar de Sprint 60 necesita ejecución real (auto-PRs, dependency updates). Sprint 61 no lo toca.

2. **Obj #12 (Ecosistema/Soberanía, 75%)** — La soberanía de datos sigue siendo parcial. No hay migration path real de Supabase a self-hosted Postgres. Sprint 61 no lo aborda.

3. **Obj #5 (Gasolina Magna/Premium, 78%)** — El tier routing de Sprint 56 necesita calibración real con datos de producción. Sprint 61 no lo calibra.

---

## Veredicto Final

Sprint 61 es **ambicioso pero superficial** en varias áreas. Las 5 épicas tocan los objetivos correctos (#8, #13, #2, #4, #3) pero la implementación tiene gaps significativos:

El **Collective Intelligence Protocol** es el componente más innovador pero también el más frágil — sin diversity enforcement y budget guards, es un LLM hablando consigo mismo de forma cara. El **Error Learning Loop** tiene la arquitectura correcta pero el matching es primitivo y el costo puede explotar. El **Onboarding** es un formulario que pretende ser inteligente.

Las 10 correcciones mandatorias (C1-C10) son necesarias para que Sprint 61 entregue valor real, no solo código que compila.

**Score de confianza del plan:** 6.5/10 (necesita las correcciones para subir a 8/10).

---

## Referencias

[1]: https://arxiv.org/abs/2502.19130 "Voting or Consensus? Decision-Making in Multi-Agent Debate"
[2]: https://github.com/dequelabs/axe-core "axe-core — Accessibility engine"
[3]: https://developer.chrome.com/docs/lighthouse "Lighthouse — Automated auditing"
[4]: https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_logical_properties_and_values "CSS Logical Properties — MDN"

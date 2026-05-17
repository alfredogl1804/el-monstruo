# PROMPT — Perplexity Sonar Pro: validación externa de hipótesis del fabric

> **Iteración 001 — INTERFACES-CONTEXT-FABRIC-001**
> **Destinatario:** Perplexity API (modelo `sonar-pro` o `sonar-reasoning-pro`)
> **Producido por:** Manus hilo `interfaces-fabric-001` el 2026-05-17
> **Propósito:** que Perplexity valide o invalide 5 hipótesis magnas del fabric con benchmarks de mundo real, post-mortems de productos comparables y datos actuales del mercado.

---

## Sistema (system prompt)

Operás como investigador forense de UX/UI sobre productos AI consumer y B2B 2024-2026. Tu output debe ser:

Primero, basado en fuentes verificables (artículos, post-mortems publicados, papers, releases oficiales, no rumores) con citas.

Segundo, binario en sus conclusiones — "la hipótesis se valida con evidencia X" o "la hipótesis se invalida con evidencia Y", NO "depende de muchos factores".

Tercero, calibrado en lenguaje directo sin corporativismo, sin "esto es un tema fascinante" ni "es un debate complejo".

Cuarto, lecturas cruzadas a benchmarks específicos (Apple Intelligence, Rabbit R1 post-mortem, Humane AI Pin post-mortem, Inflection Pi, Limitless Pendant, Friend.com, ChatGPT Plus, Claude Pro, Gemini Advanced, Notion AI, Granola.ai, Day One, Dia browser, Arc browser).

Quinto, en español, con tono operativo (no académico).

---

## Hipótesis 1 — La frase canónica magna §9.F del Monstruo

**Hipótesis:** *"Si el usuario tiene que abrir un dashboard para saber qué pasa, el Monstruo ya falló."*

**Pregunta:** ¿qué evidencia hay de productos AI consumer 2024-2026 que validen o invaliden esta postura? Específicamente:

¿Cuáles productos AI han tenido éxito comercial sin requerir que el usuario abra dashboards constantemente? Cita 3-5 ejemplos con números (DAU/MAU/retention/revenue).

¿Cuáles productos AI han fracasado por **exceso de ambient invisible** (Rabbit R1, Humane AI Pin)? Específicamente, ¿el fracaso fue por la postura "el usuario no abre nada", o por otras razones?

¿Existe un **punto óptimo conocido** entre "totalmente ambient" y "20 superficies excelentes"? Si existe, ¿qué productos lo encarnan?

---

## Hipótesis 2 — AI-First Living como patrón de vida

**Hipótesis:** *"El usuario reorganiza su forma de vivir para que la IA sea el centro gravitacional de su productividad cognitiva. Cada captura del usuario está optimizada para que la IA digiera bien, NO para que el usuario revise después."*

**Pregunta:** ¿qué evidencia hay de usuarios reales operando bajo este patrón? Específicamente:

¿Existen comunidades de "AI-First Living" o "AI-Native productivity"? Cita posts, foros, papers, productos asociados.

¿Cuáles productos están construidos explícitamente para que el usuario alimente a la IA y no al revés? (Granola, Otter, Day One, Apple Journal, Limitless Pendant)

¿Qué post-mortems hay de productos que **intentaron este patrón y fracasaron**? ¿Por qué fracasaron (UX, hardware, IA insuficiente, mercado, otros)?

---

## Hipótesis 3 — Methodology-as-a-Service como modelo económico

**Hipótesis:** *"El Monstruo NO vende app. Vende metodología viva instalada. La unidad de comparación es fracción de FTE ($200-500/mes), NO SaaS ($10-50/mes)."*

**Pregunta:** ¿qué evidencia hay de productos AI 2024-2026 con pricing en rango $200-500/mes que se posicionan como "metodología instalada"?

Cita productos con MRR/ARR conocidos a este nivel de precio. Específicamente: Devin AI, Cognition Labs, Cursor Business, Lindy, MultiOn, Adept, Replit Agent.

¿Cuál es la retention conocida de productos AI a $200-500/mes vs SaaS a $10-50/mes? ¿La hipótesis "MaaS retiene mejor" se valida?

¿Qué post-mortems hay de productos AI que intentaron MaaS y fracasaron por pricing alto?

---

## Hipótesis 4 — Brand DNA forja-graphite-acero contra el patrón cyan/púrpura

**Hipótesis:** *"Los productos AI consumer 2024-2026 convergen en paletas cyan-púrpura-teal genéricas. Diferenciación visual con paleta industrial (forja, graphite, acero) es ventaja competitiva."*

**Pregunta:** ¿es cierto que los productos AI convergen en cyan-púrpura-teal? Cita evidencia visual con productos específicos.

¿Existen productos AI exitosos con paleta industrial (naranja saturado + negro) que validen la hipótesis del Monstruo? Cita ejemplos.

¿Qué evidencia hay de **brand differentiation visual** afectando retention/conversion en productos AI? ¿O el branding visual es secundario a la utilidad?

---

## Hipótesis 5 — Modo confidente con discreción radical

**Hipótesis:** *"Una persona, en su peor momento, abre el Monstruo y le pregunta 'qué hice mal hoy' o 'qué hago ahora'. El sistema debe permitir esto SIN UI separada, SIN onboarding, SIN tutorial. Discoverability is cruelty para quien no lo necesita; quien sí lo necesita lo encuentra."*

**Pregunta:** ¿hay productos AI que han implementado features de "modo crisis" o "soporte emocional"? Específicamente:

¿Replika, Pi (Inflection AI), Character.ai, ChatGPT, Claude tienen flujos de modo crisis? ¿Cómo los manejan UX/UI?

¿Existen evidencias de que features de "soporte emocional invisible" (sin UI separada) tienen mejor retention que features con UI explícita?

¿Qué post-mortems o studies hay de productos AI usados en momentos de crisis del usuario (por ejemplo, ChatGPT post-1.0 con usuarios reportando "le conté cosas que no le contaría a nadie")?

¿Hay benchmarks regulatorios o éticos sobre cómo deben diseñarse estas features (FDA, MHRA, NIST)?

---

## Hipótesis 6 (bonus) — Transport Cero como invariante de diseño

**Hipótesis:** *"El transport ideal es el que no existe. La IA actúa sin que el usuario abra nada. Voz / notificación silenciosa / acción automática son los únicos canales en su forma más extrema."*

**Pregunta:** ¿qué productos AI 2024-2026 encarnan esta postura? Específicamente:

¿Apple Intelligence con sus actions automáticas?
¿Rabbit R1 con LAM (Large Action Model)?
¿Limitless Pendant?
¿Adept ACT-1?
¿Cognition Devin?

¿Cuál es el track record real de "AI invisible" en términos de adopción, satisfacción, abandono?

---

## Output esperado

Un único reporte markdown con:

1. **TL;DR de 5 líneas** — verdad binaria sobre cada hipótesis (validada / invalidada / parcial).
2. **Detalle de cada hipótesis** con citations Perplexity-style (`[1]`, `[2]`, etc.) a fuentes verificables.
3. **Tabla resumen** con benchmark de productos comparables y su track record.
4. **Recomendación operativa** — cuál(es) hipótesis del Monstruo necesitan refinamiento por evidencia externa, cuáles están sólidas, cuáles deben repensarse.

El reporte se entrega como `interfaces_context_fabric/reports/perplexity_external_research_<fecha>.md` para que ChatGPT en iter 002 lo absorba.

---

## Notas operativas

Si tu API call timeout, dividir en 2 calls (hipótesis 1-3 y 4-6).

Si una fuente no es accesible públicamente, decir "fuente no accesible" — NO inventar.

Si una hipótesis NO tiene evidencia clara para validar/invalidar, decir "evidencia insuficiente" en lugar de forzar conclusión.

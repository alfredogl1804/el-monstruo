# PACK 02 — ACTO 2: Calm Tech (Hilo B paralelo)

> **Estado:** CANON_VIGENTE (firmado por Hilo B Manus paralelo + 4 sabios validación adversarial)
> **Fecha doctrinal:** 2026-05-07 a 2026-05-11
> **Fuentes magna:** SRC-003 (Engranaje) + SRC-004 (Reloj Suizo) + SRC-005 (CANON Metodologías v1.5)

---

## Síntesis del paradigma

El Monstruo deja de ser "app" y pasa a ser **diagnóstico operativo invisible**. La interfaz dominante NO es UI visual — es **voz, notificación, conversación, automático**. La métrica de éxito no es "20 superficies funcionales" — es **"cuántas veces NO necesitás abrir nada"**.

Frase canónica magna (SRC-005 §9.F):

> ***"Si el usuario tiene que abrir un dashboard para saber qué pasa, el Monstruo ya falló."***

Esta frase NO está en APP_VISION (Acto 1). Es la pieza que reescribe filosóficamente el Acto 1 sin contradecir su excelencia visual — la disuelve a "calidad cuando aparece, ausencia cuando no se necesita".

---

## Capa 1 — Arquitectura Engranaje (SRC-003)

> *"El icono ⚙️ NO es decoración. Es el diagrama arquitectónico literal del Monstruo."*

El Monstruo es una **topología de transmisión de torque** entre embriones-engranaje. Cada engranaje recibe energía rotacional, la transmite, y reciproca. La velocidad del sistema completo está determinada por la velocidad del engranaje más lento (cuello de botella declarado, no oculto).

Implicaciones para interfaces:
- **No hay "frontend" ni "backend"** — hay piezas que reciben torque y piezas que lo transmiten.
- Una superficie UI es un **engranaje de salida** que convierte torque interno (computación) en gesto humano (output legible).
- Una intervención del usuario es un **engranaje de entrada** que convierte gesto humano en torque interno.
- El Monstruo nunca tiene "modos pasivos" — siempre está girando. Lo que cambia es a dónde transmite.

---

## Capa 2 — Arquitectura Reloj Suizo (SRC-004)

Las 8 piezas del Patek Philippe Caliber 240 mapeadas a software:

| Pieza | Función mecánica | Mapeo Monstruo |
|---|---|---|
| **Resorte real** | Almacena energía elástica | Memoria SMP — energía decisional acumulada |
| **Escape** | Libera energía en pulsos discretos | LangGraph step-execution (1 paso = 1 tic) |
| **Áncora** | Regula el escape | Memento + Guardian (validación binaria) |
| **Volante** | Oscilador armónico | Embrión Convergencia + ritmo de iteración |
| **Espiral** | Restaura el volante a posición neutra | **Sprint ESPIRAL_001** (homeostasis dinámica, SRC-027) |
| **Rotor** | Recarga energía del usuario al sistema | **Sprint ROTOR_001** (cada interacción del usuario en cualquier transport recarga energía del Monstruo, SRC-026) |
| **Rubíes** | Reducen fricción en pivotes | Catastros (cero-fricción de selección de proveedor) |
| **Remontoir** | Garantiza torque constante al escape | Capa Resiliencia + SovereigntyEngine (Ollama fallback) |

**Pieza UI brillante: el Rotor.** Cada interacción del usuario en CUALQUIER transport (Telegram, Flutter, Command Center, La Forja, voz, WhatsApp futuro) **recarga energía del Monstruo**. La interfaz es generadora de poder, no consumidora.

---

## Capa 3 — CANON Metodologías de Productividad v1.5 (SRC-005)

10+2 Especialidades distribuidas en 3 océanos azules + 7 categorías técnicas:

### Océanos azules (sin competencia directa hoy)

1. **UMBRAL** — la primera capa de gestión interna para una vida pública. NO existe en mercado.
2. **ESCLUSA** — convertir caos relacional en flujo intencional con timing controlado.
3. **Curador** — el Monstruo cura tu vida con tu propia data, no con datos de "best practices" genéricas.

### 10 Embriones de Dominio

Embrión Crítico Visual, Embrión Product Architect, Embrión Creativo, Embrión Estratega, Embrión Financiero, Embrión Investigador, Embrión Técnico, Embrión Ventas, Embrión Vigía, Embrión Manifestación, Embrión Convergencia Cronos.

(11 ítems en una lista de 10 → tensión interna a resolver, ver `CONTRADICTIONS_MAP.md`).

### Methodology-as-a-Service (MaaS)

El Monstruo NO vende app. Vende **metodología viva instalada**. La diferencia con SaaS tradicional:

| SaaS tradicional | MaaS Monstruo |
|---|---|
| Le pagás la app para que vos hagas el trabajo | Le pagás al Monstruo para que el trabajo se haga |
| ~$10-50/mes | ~$200-500/mes (fracción de FTE) |
| Métrica: minutos en la app | Métrica: tareas que NO tuviste que hacer |

---

## Tabla de incompatibilidad Acto 1 ↔ Acto 2

| Eje | Acto 1 | Acto 2 |
|---|---|---|
| Modelo mental | App con 20 pantallas excelentes | Equipo agéntico de 10 roles ambient |
| Interfaz dominante | UI visual minimalista | Voz/notif/conversación/automático |
| Métrica de éxito | 20 superficies funcionales y bonitas | Cuántas veces NO necesitás abrir nada |
| Pricing | Cero fee, BYOK pass-through | $200-500/mes fracción de FTE |
| Filosofía | "El Monstruo es una app excelente" | "Si tenés que abrir el Monstruo, ya falló" |
| Brand DNA | Forja + graphite + acero **visual** | Forja + graphite + acero **del timbre de voz** |

---

## 4 hipótesis de integración (de la skill `interfaces-monstruo-doctrina`, NO firmadas T1)

### H1 — Acto 2 ⊃ Acto 1
El Acto 2 contiene al Acto 1: las superficies del Cockpit existen pero solo se invocan cuando el ambient falla. El éxito sigue siendo "no abrir nada", pero cuando hay que abrir, lo que aparece es excelente.

### H2 — Modos por situación
Daily = ambient puro (Acto 2). Cockpit = control consciente (Acto 1). El toggle 3-dedos+Face ID es la frontera entre paradigmas.

### H3 — Tier-based
Tier-Owner (Alfredo) opera en Acto 1 — diseñador y operador del Monstruo necesita las 20 superficies. Trusted Circle / Funcional Accesible operan en Acto 2 — solo notif/voz/conversación.

### H4 — Temporal
Acto 1 es lo que se construye **primero** (porque el código existente lo soporta). Acto 2 es la dirección **a la que se evoluciona** una vez que las superficies del Acto 1 estén bien.

---

## Implicación operativa

**Todo sprint UI nuevo DEBE declarar binariamente a qué acto sirve.** Si el sprint no lo declara, arrastra deuda doctrinal.

Ningún sprint actual lo declara. Esa es **deuda magna** que ChatGPT 5.5 Pro debe resolver en iteración 002.

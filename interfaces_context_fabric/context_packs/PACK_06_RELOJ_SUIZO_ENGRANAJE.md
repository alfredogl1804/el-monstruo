# PACK 06 — Reloj Suizo + Engranaje (mecánica simbólica del Monstruo)

> **Estado:** CANON_VIGENTE
> **Fuentes:** SRC-003 (Engranaje) + SRC-004 (Reloj Suizo) + SRC-026 (Sprint Rotor) + SRC-027 (Sprint Espiral)

---

## Por qué esto importa para interfaces

El Monstruo NO es metáfora literaria — es **una arquitectura mecánica simbólica que tiene mapeo software 1:1**. Cada pieza física tiene una pieza software equivalente con sprint asociado. Esto significa que cuando ChatGPT diseña interfaces, no está diseñando UI sobre concept abstracto — está **diseñando la ventana visible de una máquina mecánica precisa**.

---

## Engranaje (Capa 1) — SRC-003

### Principio operativo

> *"Topología de transmisión de torque entre embriones-engranaje."*

El Monstruo es un sistema **rotacional acoplado**. Cada engranaje:
- **Recibe** torque de un engranaje anterior
- **Transmite** torque a un engranaje siguiente
- **Cambia el ratio** de velocidad/fuerza según su tamaño relativo

Implicación directa: **la velocidad del sistema completo está determinada por el engranaje más lento**. El Monstruo NO oculta este cuello de botella — lo declara.

### Engranajes de entrada / salida en interfaces

- **Engranaje de entrada (input)**: el usuario habla, escribe, gestos, tap, foto. Convierte gesto humano en torque interno.
- **Engranaje de salida (output)**: la voz brand, una notificación, una superficie A2UI generativa, una acción ejecutada. Convierte torque interno en gesto humano.

Esto significa que **toda UI es transmisión de torque**, no "información". Cualquier diseño de interfaz que olvide la rotación — que se quede en "info estática" — viola el principio Engranaje.

---

## Reloj Suizo (Capa 2) — SRC-004

### El Patek Philippe Caliber 240 como modelo

8 piezas mecánicas de un movimiento de relojería de altísima precisión, cada una con función específica. El Monstruo software replica las 8 con mapeo declarado.

| # | Pieza Patek | Función mecánica | Pieza Monstruo | Estado código |
|---|---|---|---|---|
| 1 | Resorte real | Almacena energía elástica | Memoria SMP | **Sprint Mobile 0 — NO ejecutado** |
| 2 | Escape | Libera energía en pulsos discretos | LangGraph step-execution | ✅ existe |
| 3 | Áncora | Regula el escape | Memento + Guardian | ✅ existe |
| 4 | Volante | Oscilador armónico | Embrión Convergencia + ritmo iteración | parcial |
| 5 | Espiral | Restaura volante a posición neutra | **Sprint ESPIRAL_001** | firmado, NO ejecutado |
| 6 | Rotor | Recarga energía con movimiento | **Sprint ROTOR_001** | firmado, NO ejecutado |
| 7 | Rubíes | Reducen fricción en pivotes | Catastros | parcial |
| 8 | Remontoir | Garantiza torque constante | SovereigntyEngine + Resiliencia | ✅ existe |

### El Rotor — la pieza UI brillante (SRC-026)

> *"Cada interacción del usuario en CUALQUIER transport (Telegram, Flutter, Command Center, La Forja, voz, WhatsApp futuro) recarga energía del Monstruo."*

Esto reescribe la economía atencional de las apps:

| Apps tradicionales | Monstruo (Rotor) |
|---|---|
| El usuario *gasta* atención cuando usa la app | El usuario *recarga* energía del sistema cuando interactúa |
| La app extrae valor del usuario | La app y el usuario se enriquecen mutuamente |
| Métrica: time spent | Métrica: energy reciprocated |

**Implicación brutal para interfaces:** cualquier UI que extraiga atención sin reciprocar (notificaciones falsas, badges, streaks) **rompe el Rotor**. Por eso APP_VISION Cap 0 regla 3 prohíbe explícitamente esos patrones.

### El Espiral — homeostasis dinámica (SRC-027)

El Espiral es la pieza que **devuelve el volante a posición neutra después de cada oscilación**. En software: el Monstruo, después de cada interacción intensa, vuelve a estado de equilibrio. NO se queda en modo "alerta", NO se queda en modo "engagement", NO se queda en modo "anxiety".

Esto es lo que en Acto 2 se llama **silencio inteligente**. El Espiral es el motor mecánico que lo garantiza.

---

## Sprints firmados pero NO ejecutados

| Sprint | Pieza | Bloqueante |
|---|---|---|
| SPRINT_ROTOR_001 | Rotor | post-Guardian (Sprint GUARDIAN_AUTONOMO_001) |
| SPRINT_ESPIRAL_001 | Espiral | post-Guardian |
| SPRINT_MOBILE_0 | Resorte real (SMP) | T1 magna pendiente (SRC-002 §8) |

---

## Implicaciones para diseño de interfaces

### 1. El reloj se ve

El Cockpit debe **mostrar las 8 piezas operando**. NO decoración — métrica real. ¿Qué tan rápido oscila el Volante? ¿Cuánta energía tiene el Resorte? ¿Está el Rotor recibiendo recarga?

Esto NO está spec'd. Es trabajo de ChatGPT en iteración 002.

### 2. Cada interacción debe **completar el ciclo del Rotor**

Cualquier flujo UI que termine sin reciprocidad (el usuario hace algo y el Monstruo no devuelve nada) **viola Reloj Suizo**. Esto mata patrones tipo "submit form and wait".

### 3. La voz brand del Monstruo es el Áncora

Voz registro bajo, gravitas sin teatro, certeza sin arrogancia, silencio con peso. Eso NO es estilo — es **función mecánica del Áncora regulando el Escape**. Una voz nerviosa, una voz dudosa, una voz overcomprometida rompe la regulación.

---

## Decisiones pendientes para ChatGPT

1. **Spec UI del Cockpit "Salud del Reloj"** — visualización de las 8 piezas operando.
2. **Spec UI del Rotor en Daily** — cómo cada interacción muestra (sutilmente) que recarga energía.
3. **Voz brand ElevenLabs** — Sprint VOICE_BRAND_ELEVENLABS pendiente, requiere prompt magno de timbre.
4. **Decisión sobre nombres de los Embriones-Engranaje** — ¿son los mismos 10+2 del PACK_05? ¿Son los 9+ del Cap 3 APP_VISION? Tensión de cardinalidad sin resolver.

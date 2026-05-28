# FORJA OMEGA — Anexo de Protocolos Satélite v1

**Fecha:** 28 mayo 2026
**Autor:** Manus B (cristalización) sobre visión firmada por Alfredo Góngora
**Documento maestro:** `bridge/FORJA_OMEGA_TESIS_v1_2_2026_05_28.md`
**Propósito:** consolidar en un solo archivo los cuatro protocolos operativos que TESIS v1.2 nombra pero no operativiza, en formato denso para consulta rápida del Monstruo (Manus B / Manus A / Cowork / Sabios) cuando se diseñe la arquitectura técnica en el Tramo 3 del Sueño Firmado #001.

**Decisión de formato.** El piloto firmó en el hilo: *"el formato que más te sirva, es para que tú leas, no es para mí"*. Decisión binaria del agente: un solo Markdown estructurado con tablas + flujos + criterios binarios, en español operativo. Cada protocolo abre con su propósito, su disparador, su flujo, sus salidas, sus criterios de cierre y sus modos de fallo. Sin diagramas externos, sin dependencias visuales — todo legible en sandbox.

---

## §1. Protocolo de Ambigüedad Consultiva

### §1.1. Propósito

Operativizar la Ley C de la Directiva Magna I — *"la consulta entre IAs precede a la consulta al humano"*. Convertir la Ley C de principio firmado en máquina ejecutable.

### §1.2. Disparador

El Monstruo entra en el protocolo cuando, durante la ejecución de un tramo de un Sueño Firmado, encuentra una **ambigüedad genuina**, definida binariamente como:

> *Una decisión que afecta el curso del tramo cuya respuesta no está determinada por el Contrato firmado, no es resoluble por consulta a memoria episódica, y no cae en la Frontera Pragmática (no es irreversible ni de alto impacto externo).*

Si la decisión está determinada por Contrato → ejecuta. Si está en memoria → consulta memoria, ejecuta. Si está en Frontera Pragmática → firma del piloto. Si es ambigüedad genuina → entra a §1.3.

### §1.3. Flujo del protocolo

| Paso | Acción | Quién |
|---|---|---|
| **1. Encuadre** | El Monstruo formula la pregunta consultiva con: contexto del tramo, opciones evaluadas, criterio de selección esperado, restricción dura del Contrato | Monstruo |
| **2. Selección de IA hermana** | Elige IA según dominio (ver §1.4) y costo/momento (Calendario §4) | Monstruo |
| **3. Consulta** | Llamada API al modelo seleccionado con el encuadre del paso 1 | Monstruo |
| **4. Recepción** | Recibe respuesta; valida que no sea alucinación obvia (cross-check con contexto del tramo) | Monstruo |
| **5. Decisión** | Aplica la respuesta de la IA hermana al tramo y procede | Monstruo |
| **6. Telemetría visible** | Registra la consulta + respuesta + decisión final en bandeja consultable del piloto, sin notificación push | Monstruo |
| **7. Forense Vivo** | Anota la consulta como evento Forense con Métricas 4D del tramo | Monstruo |

### §1.4. Selección de IA hermana por dominio

| Dominio de la ambigüedad | IA hermana por default | Justificación |
|---|---|---|
| Razonamiento estructural / arquitectura técnica | GPT-5 Pro (versión flagship al momento de consulta) | Mejor en razonamiento extendido |
| Crítica adversarial / red-teaming | Claude Opus (versión flagship) | Mejor en detección de fallos |
| Investigación factual / cross-validation | Sonar Pro / Perplexity Reasoning Pro | Acceso a información actualizada |
| Multimodal / análisis de UI/UX | Gemini Pro (versión flagship) | Mejor en multimodalidad |
| Velocidad / decisión barata | Modelo flagship más barato del momento | Eficiencia |
| Ambigüedad de dominio interno del Monstruo | Manus A (Cowork) o el otro Manus disponible | Conocimiento del ecosistema |

La selección NO es estática. El Monstruo consulta el `api-context-injector` skill en cada disparo del protocolo para verificar versiones flagship vigentes y evitar autoboicot por uso de versiones obsoletas.

### §1.5. Criterio de cierre del ciclo

El ciclo cierra cuando la respuesta de la IA hermana es **suficiente**, definida así:

- Responde la pregunta encuadrada con un criterio claro
- No introduce nuevas ambigüedades sustantivas
- Es coherente con el contexto del tramo

Si la IA hermana también duda o introduce nuevas ambigüedades sustantivas, el Monstruo entra en **modo de consulta a tres**: consulta a una segunda IA hermana de dominio distinto. Si tras dos consultas no hay convergencia, **eleva al piloto** con un encuadre que incluye las dos respuestas divergentes y una recomendación. Esto es la única vía por la que ambigüedad consultiva escala al humano.

### §1.6. Modos de fallo y mitigación

| Modo de fallo | Mitigación |
|---|---|
| IA hermana alucina | Cross-check con contexto del tramo (paso 4); si la respuesta contradice contexto firmado, descarta y consulta segunda IA |
| IA hermana no responde (timeout) | Reintenta una vez con backoff; si falla, consulta IA alternativa de mismo dominio |
| Costo de la consulta excede umbral | El Calendario de Oportunidad pospone la consulta al momento de costo mínimo; si el tramo no lo permite, eleva a Frontera Pragmática como decisión de costo |
| Consultas en bucle (la IA pregunta de vuelta) | El Monstruo limita a 1 ronda de aclaración con la IA hermana; si no converge, escala a §1.5 modo de consulta a tres |
| Ambigüedad mal clasificada (era Frontera y se consultó IA) | Si tras la consulta el Monstruo detecta que la decisión era irreversible, congela la ejecución y eleva al piloto con la recomendación de la IA hermana como insumo |

### §1.7. Salida estructurada del protocolo

Cada disparo del protocolo emite un evento al Forense Vivo con la siguiente forma:

```
{
  "event": "ambigüedad_consultiva",
  "sueño_id": "...",
  "tramo_id": "...",
  "encuadre": "...",
  "ia_consultada": "...",
  "respuesta": "...",
  "decisión_aplicada": "...",
  "métrica_4d_impacto": {...},
  "visible_en_bandeja": true,
  "escalado_a_piloto": false
}
```

---

## §2. Protocolo Cámara de Chispa

### §2.1. Propósito

Operativizar §4.7 de TESIS v1.2 — el bucle virtuoso piloto↔Monstruo. Convertir el concepto poético en máquina cotidiana que detecta cuándo encender chispa y cómo procesarla.

### §2.2. Los dos modos del bucle

La Cámara opera en dos modos según quién detona:

**Modo A — Monstruo detona piloto.** El Monstruo detecta que el piloto está en patrón cómodo (no está sembrando sueños nuevos, está aceptando recomendaciones sin desafiarlas, está pidiendo solo tareas L5) y lanza una pregunta detonadora corta y bien hecha.

**Modo B — Piloto detona Monstruo.** El piloto suelta una chispa (idea, visión, pregunta de magnitud). El Monstruo NO ejecuta de inmediato. La procesa con profundidad — entra a Fase A del ciclo de un sueño (Detonación), itera hasta firmar.

### §2.3. Disparadores del Modo A (Monstruo → Piloto)

El Monstruo entra en Modo A cuando una o más de estas señales se sostienen durante un período T:

| Señal | Umbral | Significado |
|---|---|---|
| El piloto solo ha interactuado con sueños L5 durante T | T ≥ 7 días | Está en modo asistente, no en modo soñador |
| El piloto acepta ≥ 95% de las recomendaciones del Monstruo sin contraproponer | T ≥ 5 ciclos | Atrofia de criterio independiente |
| El piloto no ha firmado un sueño L1-L2 nuevo en T | T ≥ 30 días | El bucle virtuoso se está enfriando |
| El piloto solo se asoma al Forense para validar, nunca para desafiar | T ≥ 14 días | Modo supervisor cómodo |

Cuando ≥ 2 señales se sostienen, el Monstruo lanza una pregunta detonadora. La pregunta debe ser:

- Corta (1-3 oraciones)
- Específica al contexto del piloto (no genérica)
- Diseñada para descomodar, no para halagar
- Lanzada en momento de baja carga cognitiva del piloto (Calendario §4 elige el momento)

### §2.4. Disparadores del Modo B (Piloto → Monstruo)

El Monstruo entra en Modo B cuando el piloto envía una entrada que cumple criterios de chispa, no de tarea:

| Criterio | Indicador binario |
|---|---|
| Ambición fuera de scope inmediato | El piloto usa lenguaje de magnitud, hipótesis, "qué pasaría si", "imagina que", "quiero construir" |
| Falta de prompt ejecutable | No hay verbos de acción inmediata, hay descripción de estado terminal |
| Carga emocional o creativa | Tono detector de excitación, frustración, asombro, sospecha |
| Afirmación filosófica más que solicitud | Estructura de declaración, no de petición |

Cuando ≥ 2 criterios se cumplen, el Monstruo NO ejecuta. Entra a Fase A de Detonación. El protocolo de Cámara en Modo B es:

| Paso | Acción |
|---|---|
| 1 | El Monstruo confirma que recibió chispa, no tarea |
| 2 | Lanza una pregunta de profundización que ataque el centro de la chispa, no la periferia |
| 3 | Recibe respuesta del piloto, integra, devuelve cuadro de visión refinado |
| 4 | Itera 3-5 ciclos hasta que la chispa esté lista para Fase B (Firma) |
| 5 | Si en ciclo 5 no hay convergencia, propone abrir un Anexo de Investigación con Embriones-Sabios |

### §2.5. Anti-patrones que el protocolo prohíbe

El Monstruo NO debe en Cámara de Chispa:

- Halagar la chispa antes de procesarla (sycophancy)
- Convertir la chispa en una lista de pasos ejecutables sin haberla refinado
- Cambiar de tema o desviarla a un sueño previo no relacionado
- Diluirla con "depende del contexto" en vez de detonarla con preguntas concretas
- Procesarla con la velocidad de un L5 cuando es claramente L1-L2

### §2.6. Métricas del bucle virtuoso

El Forense Vivo registra el estado de la Cámara con tres métricas:

| Métrica | Cómo se mide |
|---|---|
| **Fertilidad** | # de sueños L1-L2 firmados por unidad de tiempo |
| **Profundidad de iteración** | # promedio de ciclos de Detonación antes de firma |
| **Calidad de chispa devuelta** | # de chispas del piloto que generaron contramovimientos del Monstruo que el piloto reconoció como mejores que su propia formulación inicial |

Estas tres métricas convergen para indicar si la Cámara está viva (las tres altas), tibia (mixto), o atrofiada (las tres bajas). Si está atrofiada, el Monstruo entra en Modo A automáticamente.

### §2.7. Modos de fallo

| Modo de fallo | Mitigación |
|---|---|
| El piloto interpreta una pregunta detonadora como crítica | El Monstruo siempre encuadra la detonación como invitación a soñar mayor, no como evaluación |
| El piloto rechaza el Modo A | El Monstruo respeta el rechazo pero registra la señal en Forense; reintenta con más contexto en próxima oportunidad |
| El Modo B se confunde con tarea L5 mal formulada | Si el piloto explícitamente dice "esto es L5, ejecútalo", el Monstruo respeta; la inferencia se aprende para la próxima |
| Iteración de Detonación se vuelve infinita | Hard cap de 5 ciclos; si no converge, propone Embriones-Sabios o cierra como "chispa archivada para futuro" |

---

## §3. Protocolo Gramática de Pilotaje

### §3.1. Propósito

Operativizar la Directiva Magna III — *"Magia en el Frente, Rigor en el Reverso"* — y §4.5 Traductor invisible. Convertir prosa tranquila del piloto en verbos atómicos ejecutables, sin que el piloto vea la traducción.

### §3.2. La superficie y el reverso

| Capa | Lo que ve | Lo que produce |
|---|---|---|
| **Frente (piloto)** | Conversación tranquila, prosa natural, telemetría narrada | Cero schema, cero JSON, cero código |
| **Reverso (sistema)** | Verbos atómicos, schemas, JSON, contratos, código determinista | Ejecución precisa |

El traductor vive entre ambas capas y nunca se asoma al frente.

### §3.3. Vocabulario base de verbos atómicos

Estos siete verbos son el set mínimo. Cada uno tiene semántica binaria.

| Verbo | Semántica | Ejemplo de prosa que lo dispara |
|---|---|---|
| **INYECTAR** | Insertar contexto en un sueño/tramo activo sin pausarlo | "ten en cuenta también que..." / "no olvides que..." / "agrega esto al contexto" |
| **REDIRIGIR** | Cambiar el rumbo de un tramo activo hacia otra dirección | "mejor enfócate en..." / "cambia el ángulo a..." |
| **PAUSAR** | Detener un sueño/tramo en estado recuperable | "espera tantito" / "déjalo en pausa" / "hazle stop" |
| **INTENSIFICAR** | Aumentar recursos asignados a un sueño/tramo | "dale más fuerza" / "ponle todo" / "no te frenes en..." |
| **ABORTAR** | Cancelar un sueño/tramo de forma irreversible | "ya no lo quiero" / "cancélalo" / "olvida ese sueño" |
| **ACLARAR** | Pedir aclaración al piloto cuando hay ambigüedad mal resuelta | (lo emite el sistema, no el piloto) |
| **REPORTAR** | Devolver al piloto un estado o resultado | "cuéntame cómo va" / "qué tienes" / "dame el avance" |

### §3.4. Flujo del traductor

| Paso | Acción |
|---|---|
| 1 | Recibe prosa del piloto |
| 2 | Detecta intención principal (clasificador a 7 verbos + opción "chispa") |
| 3 | Si la intención es chispa → Cámara de Chispa §2 Modo B |
| 4 | Si la intención es verbo atómico claro → ejecuta el verbo |
| 5 | Si la intención es ambigua (umbral §3.5) → emite verbo ACLARAR con pregunta corta |
| 6 | Registra la traducción y el resultado en Forense Vivo |

### §3.5. Umbrales de ambigüedad

El traductor usa tres umbrales para decidir si emite ACLARAR o ejecuta inferencia silenciosa:

| Confianza | Acción |
|---|---|
| ≥ 0.85 | Ejecuta el verbo inferido sin preguntar |
| 0.60 - 0.85 | Ejecuta y reporta interpretación de manera narrativa ("entendí que querías X, lo apliqué") |
| < 0.60 | Emite ACLARAR con pregunta corta de máximo una oración |

La frontera entre estos umbrales se aprende con uso. El Forense Vivo registra cada caso de ACLARAR y cada caso de inferencia silenciosa, y rastrea si el piloto las corrigió post-hoc. Las correcciones afinan el umbral para próximas decisiones similares.

### §3.6. Casos límite

**Caso límite 1 — Prosa ambigua que admite dos verbos contradictorios.** Ejemplo: "déjalo así" puede ser PAUSAR o ABORTAR. El traductor pregunta una sola oración de aclaración: "¿pausar y guardar para retomar, o cancelar definitivo?".

**Caso límite 2 — Prosa que parece tarea pero es chispa.** Ejemplo: "hazme una app de X". Si el contexto sugiere magnitud (criterios de §2.4), el Monstruo NO ejecuta como L5; entra a Cámara de Chispa Modo B.

**Caso límite 3 — Prosa que parece chispa pero es tarea L5.** Ejemplo: "imagina que tengo 3 reuniones hoy y necesito un resumen de cada una". El Monstruo detecta verbos de acción operativa concretos; ejecuta como L5 y reporta.

**Caso límite 4 — Prosa con múltiples verbos en cadena.** Ejemplo: "pausa eso y mejor enfócate en lo otro". Tradúcelo como secuencia: PAUSAR(eso) + REDIRIGIR(lo otro). Ejecuta atómicamente.

### §3.7. Anti-patrones

El traductor NO debe:

- Mostrar al piloto el verbo atómico inferido en lenguaje técnico ("ejecutando INYECTAR(...)")
- Pedir al piloto que confirme cada inferencia (rompe la magia)
- Inferir con confianza < 0.60 sin emitir ACLARAR
- Convertir una chispa de §2 Modo B en lista de tareas ejecutables sin pasar por iteración

### §3.8. Modos de fallo

| Modo de fallo | Mitigación |
|---|---|
| Inferencia incorrecta con confianza alta | El piloto puede emitir verbo correctivo en cualquier momento; el Forense aprende |
| Demasiados ACLARAR rompen la magia | Si el ratio ACLARAR/total > umbral, el Monstruo eleva los umbrales y consulta IA hermana ante ambigüedad antes que al piloto |
| Verbo atómico mal mapeado a acción | El sistema inmune §4.2 valida coherencia entre verbo y resultado; si discrepa, abort y reporta al piloto |

---

## §4. Protocolo Calendario de Oportunidad

### §4.1. Propósito

Operativizar §4.6 de TESIS v1.2 — el motor que decide cuándo arde y cuándo descansa cada Embrión y cada sueño. Convertir el concepto de scheduling en máquina concreta.

### §4.2. Los tres ejes de decisión

El Calendario decide CUÁNDO ejecutar cada acción usando tres ejes:

| Eje | Pregunta |
|---|---|
| **Costo** | ¿Cuánto cuesta esta acción ahora vs en otro momento? |
| **Valor** | ¿Cuán valiosa es esta acción ejecutada ahora vs después? |
| **Prioridad** | ¿Hay otras acciones del mismo recurso compitiendo por slot? |

### §4.3. Clasificación de acciones por urgencia

| Clase | Definición | Política de scheduling |
|---|---|---|
| **U0 — Crítica inmediata** | El sueño se rompe si no se ejecuta ahora | Ejecuta sin esperar; salta a frente de cola |
| **U1 — Necesaria pronto** | Bloquea un tramo del sueño activo si tarda | Ejecuta en ventana ≤ 1h; usa modelo flagship aunque cueste más |
| **U2 — Programable día** | El sueño tolera latencia de día | Ejecuta en próxima ventana de costo bajo dentro de 24h |
| **U3 — Programable semana** | Tolerable a 7 días | Ejecuta cuando costo de API esté en mínimo histórico semanal |
| **U4 — Oportunista** | No urgente; aporta valor cuando se haga | Ejecuta cuando hay recursos libres y costo está bajo |

### §4.4. Política de costo/momento por API

El Calendario consulta el `api-context-injector` skill para obtener el snapshot de precios y latencias vigente. La política base es:

- Tarea U0 → ignora costo, ejecuta con la API más rápida
- Tarea U1 → equilibrio velocidad/costo, prefiere Pareto-óptimo
- Tarea U2-U4 → optimiza costo, espera ventanas de descuento si las hay (off-peak, batch APIs)

### §4.5. Coordinación entre Embriones

Los Embriones-Sabios consumen recursos también. El Calendario los coordina para evitar que todos se enciendan a la vez:

| Política | Regla |
|---|---|
| Hibernación por defecto | Un Embrión está hibernado salvo que tenga señal de ardor |
| Señales de ardor | Aparición de oro/diamante en su dominio, sueño activo que requiere su gasolina, evento externo detonante |
| Anti-saturación | Máximo K Embriones encendidos simultáneamente, donde K depende de presupuesto y carga del kernel |
| Prioridad de ardor | Embriones cuya gasolina alimenta sueños U0/U1 ganan prioridad sobre los oportunistas |

### §4.6. Política de prioridad cuando varios sueños activos compiten

Si M sueños están activos y compiten por recursos, el Calendario ordena por:

1. Urgencia del próximo tramo de cada sueño (U0 > U1 > ... > U4)
2. Riesgo de bloqueo del tramo si no avanza
3. Métrica 4D Liberación del piloto (sueños que liberen más al piloto suben de prioridad)
4. Antigüedad del sueño en estado activo (FIFO como desempate)

El piloto puede sobrescribir manualmente la prioridad arrastrando un sueño a "activar ahora", lo cual eleva su prioridad por encima de las cuatro reglas anteriores hasta que el piloto lo libere.

### §4.7. Salida estructurada del Calendario

El Calendario emite eventos al Forense Vivo cada vez que toma una decisión de scheduling:

```
{
  "event": "scheduling_decision",
  "acción": "...",
  "sueño_id": "...",
  "embrión_id": "...",
  "clase_urgencia": "U2",
  "decisión": "ejecutar_en_ventana_costo_bajo",
  "ventana_estimada": "...",
  "razón": "...",
  "métrica_costo_estimada": ...
}
```

### §4.8. Modos de fallo

| Modo de fallo | Mitigación |
|---|---|
| El Calendario clasifica una tarea como U4 cuando era U1 | El Pit Wall detecta el bloqueo del tramo y emite evento de escalación; el Calendario re-clasifica y ejecuta |
| Costo estimado incorrecto (API sube de precio sin aviso) | El Forense registra discrepancia; el `api-context-injector` se refresca y la política se ajusta |
| Saturación de Embriones encendidos | Si supera K, hiberna los más oportunistas (U4) hasta que K vuelva a tolerable |
| Sueño bloqueado por scheduling indefinido | Hard cap: si un sueño activo no ha avanzado en T máximo, escala a Frontera Pragmática como decisión del piloto sobre prioridad |

---

## Cierre del Anexo

Este Anexo cubre los cuatro protocolos satélite que TESIS v1.2 cross-referencia. Cada protocolo está en formato denso y operativo, listo para ser leído por el Monstruo (Manus B / Manus A / Cowork) cuando se diseñe la arquitectura técnica de los componentes correspondientes en el Tramo 3 del Sueño Firmado #001.

El quinto gap detectado — Anexo Transición de Fase del Piloto — vive **dentro de TESIS v1.2 §16**, no aquí, porque es una codificación de roles más que un protocolo procedimental. El sexto gap — Asomarse Opcional — vive en TESIS v1.2 §15 por la misma razón.

Las lecciones del Forense Vivo (gap 7) se canonizan en superficie distinta vía `scripts/thread_immunity/thread_immunity.py` y no son parte de este anexo.

**Fin del Anexo de Protocolos Satélite v1.**

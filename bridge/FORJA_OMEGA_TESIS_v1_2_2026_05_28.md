# FORJA OMEGA — TESIS v1.2

**Fecha:** 28 mayo 2026
**Autor:** Alfredo Góngora (visión) · Manus B (cristalización)
**Estado:** FIRMADA en visión por Alfredo, pendiente firma binaria en repo
**Reemplaza:** TESIS v1.1 (28 may 2026, misma sesión)
**Diferencia con v1.1:** v1.2 es **delta aditivo, no reescritura**. Conserva íntegramente las trece secciones de v1.1 y añade:
- §5.1 — Las tres consecuencias operativas de la Ley C, formalizadas como Protocolo de Ambigüedad Consultiva (referencia al Anexo)
- §15 — Principio del Asomarse Opcional, transparencia sin obligación de vigilancia
- §16 — Anexo Transición de Fase del Piloto, los cuatro estados y la lógica de promoción
- §17 — Cross-references operativas a `bridge/ANEXO_PROTOCOLOS_SATELITE_v1_2026_05_28.md`
- §14 enriquecida con las dos citas verbatim del piloto que detonaron Asomarse Opcional y Transición de Fase
- §13 firma actualizada para v1.2

Los gaps que motivaron v1.2 están documentados en `forja_omega_meta/03_gaps_identificados.md`. Las secciones 0 a 12 son **idénticas en doctrina** a v1.1; solo se añaden las nuevas secciones y los cross-references.

---

## 0. PROPÓSITO MAGNA — Constructor de Sueños Imposibles

> *"El Monstruo no se opera con prompts. El Monstruo construye sueños imposibles. El prompt es el método de la IA tradicional. El sueño firmado es el método del Monstruo."*

Esta es la naturaleza fundacional del Monstruo, la verdad de la cual se derivan todas las demás verdades del sistema.

### 0.1. La inversión del paradigma

Toda IA agéntica conocida al 28 mayo 2026 — GPT-5, Claude Opus, Gemini, Manus, Genspark, Multi-On, Operator, Codex App — opera bajo un mismo paradigma:

> *Recibe un prompt. Lo ejecuta lo más rápido posible. Entrega un resultado.*

Este paradigma tiene un techo estructural: solo puede resolver problemas que el usuario ya sabe cómo formular. Si el usuario no sabe formular el prompt, la IA no sirve. Y los problemas más grandes de la humanidad son **precisamente los que nadie sabe formular**.

El Monstruo invierte el contrato:

> *Recibe la chispa de un sueño imposible. Itera con el piloto hasta que el sueño esté firmado. Toma el tiempo que requiera para diseñar la pista perfecta. Ejecuta a máxima velocidad con mínima fricción. Realiza el sueño end-to-end.*

El piloto **no necesita saber cómo construir el sueño**. Solo necesita **soñarlo con suficiente claridad para firmarlo**. La capacidad de soñar es del piloto. La capacidad de construir es del Monstruo. Cada uno hace lo que le toca.

### 0.2. Por qué se llama "Constructor de Sueños"

Cuando Alfredo describió su intención, usó la palabra "sueño" porque era la única forma humana de hacer entender la magnitud. Despojado del romanticismo, un **sueño** es operativamente:

- Una intención de magnitud que no admite respuesta inmediata
- Algo que requiere diseño extenso antes de ejecución
- Algo que ningún agente IA actual puede tocar de un solo prompt
- Algo que vale la pena tomarse el tiempo necesario para hacerlo bien

El Monstruo es la **maquinaria que convierte sueños imposibles en producto terminado**. Esta es su razón de existir. Todo lo demás — vehículo, embriones, sistema inmune, pit wall, cámara de chispa — es subordinado a este propósito.

### 0.3. La metáfora rectora actualizada

La metáfora Le Mans 24h se mantiene porque es la mejor metáfora operativa, pero se enriquece:

| Pieza Le Mans | Equivalente FORJA OMEGA |
|---|---|
| **El Sueño** | Le Mans completa, los 24h ganados |
| **Diseño de la pista** | Investigación, arquitectura, tramos, dependencias **antes** de salir a correr |
| **Piloto** | Alfredo soñando, firmando, dirigiendo |
| **Vehículo principal** | El Monstruo (kernel + app Flutter + AG-UI dúplex) |
| **Estaciones de apoyo** | Modelos IA externos como combustible especializado bajo demanda |
| **Equipo en órbita 24/7** | Embriones-Sabios soberanos productores de gasolina premium |
| **Pit Wall** | Capa antibloqueo smart |
| **Sistema inmune del vehículo** | Procesos contra debilidades LLM |
| **Cronómetro** | Métricas 4D (calidad, velocidad, costo razonado, liberación del piloto) |
| **Memoria de carrera** | Registro Forense Vivo |
| **Comunicación piloto-vehículo** | Canal dúplex permanente nunca interrumpido |

La pista NO es genérica. **Cada sueño tiene su pista propia**, diseñada específicamente para hacer ese sueño realizable.

---

## 1. La economía invertida del tiempo IA

Esta es la pieza técnica binaria que hace al Monstruo radicalmente distinto del SOTA.

| Dimensión | SOTA actual | Monstruo |
|---|---|---|
| Tiempo de diseño | Segundos a minutos | El necesario (horas, días, semanas) |
| Tiempo de ejecución | Largo, errático, prueba/error | Mínimo, determinista, sin fricción |
| Iteraciones del usuario | Decenas durante ejecución | Pocas, en fase pre-firma |
| Modo dominante | Reaccionar | **Anticipar** |
| Recursos | Quemados en exploración durante ejecución | Quemados en diseño, ejecución eficientísima |
| Métrica de éxito | Velocidad de respuesta | **Fidelidad al sueño realizado** |

### 1.1. Por qué nadie más lo hace

Los modelos LLM tienen costos por inferencia que se acumulan con el tiempo de pensamiento. Si OpenAI o Anthropic permitieran a sus agentes pensar durante días, quebrarían. Por eso GPT-5 Pro piensa minutos máximo. Por eso Claude tiene timeouts. Por eso Manus tiene límite de créditos por tarea.

El Monstruo rompe esta restricción porque:

1. El diseño NO es un solo LLM pensando minutos. Son **muchos procesos discretos** baratos: investigación con Embriones-Sabios, consultas a 6 modelos, validación en tiempo real, escritura de schemas, simulaciones, audit con Cowork. La suma de días de pasos baratos produce un diseño que ningún agente single-shot puede igualar.

2. El diseño es **acumulativo entre sueños**. Sueño N+1 reutiliza investigación del sueño N. La maquinaria mejora con uso.

3. La ejecución es barata porque **la pista la diseñó la maquinaria, no un LLM**. La ejecución es código determinista siguiendo el plan, con LLMs solo en nodos donde se necesita razonamiento puntual.

Resultado: un sueño imposible que GPT-5 Pro no puede tocar (porque el contexto no le alcanza, el tiempo lo agota, el costo lo prohíbe), el Monstruo lo construye en N días, **con menos costo total que GPT-5 fallaría intentándolo**.

---

## 2. Las cuatro fases del ciclo de un sueño

Cada sueño en el Monstruo pasa por cuatro fases obligatorias:

### Fase A — Detonación

El piloto suelta una chispa: una idea, una visión, una pregunta de magnitud. El Monstruo no ejecuta. **Itera con el piloto** vía la Cámara de Chispa hasta refinar la chispa en intención clara. Esta fase puede durar minutos, horas o días según la complejidad.

### Fase B — Firma

El sueño está suficientemente claro para firmarse. Piloto y Monstruo coinciden en:

- El estado terminal del sueño (qué significa "construido")
- Los criterios de validación de cierre
- El nivel del sueño (L1-L5)
- Los recursos aproximados disponibles
- La frontera pragmática (qué requiere firma binaria del piloto durante construcción)

Una vez firmado, el sueño se vuelve un **Contrato de Sueño Firmado** — objeto inmutable salvo por revisión consciente del piloto.

### Fase C — Diseño de Pista

El Monstruo, sin prisas, diseña la pista completa antes de ejecutar. Esto incluye arquitectura técnica completa, tramos en orden de dependencias, vehículos asignados a cada tramo, insumos necesarios y de qué Embrión-Sabio vienen, criterios de cierre por tramo, Forense de aprendizaje cruzado entre tramos y plan de contingencias para fricciones anticipables. Esta fase también puede durar lo necesario. El reloj externo es irrelevante.

### Fase D — Ejecución

Cuando la pista está firmada como completa por el Monstruo + audit interno + (cuando aplique) Sabios externos, comienza la ejecución. Aquí la velocidad es máxima, la fricción mínima, el canal dúplex piloto-vehículo está activo, los Embriones-Sabios alimentan insumos, el Forense Vivo registra todo, el Pit Wall vigila bloqueos, y cualquier fricción descubierta vuelve a la mesa de diseño como **error registrable**, para que el siguiente sueño nazca con esa anticipación incluida.

---

## 3. Los cinco niveles de sueños

El Monstruo opera con sueños de magnitud variable. El piloto no clasifica el nivel — el Monstruo lo infiere durante la iteración pre-firma y propone el nivel. El piloto siempre tiene última palabra.

| Nivel | Ejemplo | Tiempo de diseño | Tiempo de ejecución | Recursos |
|---|---|---|---|---|
| **L1 — Sueño Magna** | Construir FORJA OMEGA, fundar empresa, elegir estrategia política a 5 años | Días a semanas | Semanas a meses | Toda la maquinaria activa |
| **L2 — Sueño Mayor** | Diseñar producto completo, refactor arquitectónico de un sistema, lanzamiento de campaña | Días | Días a semanas | Maquinaria parcial, varios Sabios |
| **L3 — Sueño Medio** | Estrategia de campaña política, plan de negocio detallado, investigación profunda multi-fuente | Horas | Días | Sabios específicos + 1-2 ejecutores |
| **L4 — Sueño Operativo** | Crear contenido para Zona Like de la semana, plan de viaje complejo, análisis financiero específico | Minutos a 1h | Horas | Sabio del dominio + ejecutor |
| **L5 — Tarea Asistida** | Resumir documento, buscar información, traducir texto | Segundos | Minutos | Modo Manus tradicional |

Los L5 son el **caso degenerado** donde el Monstruo se comporta como un agente tradicional porque no amerita más. Los L1-L4 son donde el Monstruo brilla y nadie más puede competir.

### 3.1. Coexistencia de múltiples sueños

El Monstruo permite múltiples sueños vivos simultáneamente. El piloto tiene **una bandeja de sueños** visible en la app: cada sueño con nivel, fase, % de avance, próximo tramo. **Solo M sueños están activos al mismo tiempo**, donde M lo decide el Monstruo según recursos disponibles, deadlines, prioridades del piloto. Los demás están **vivos pero esperando turno** — los Embriones siguen alimentándolos, pero no se asignan vehículos. El piloto puede **arrastrar manualmente** un sueño a "activar ahora" y otro a "pausar". El Calendario de Oportunidad sigue eligiendo cuándo cada sueño activo avanza.

---

## 4. Las siete componentes inéditas (revisitadas desde el Propósito Magna)

Las siete componentes técnicas de TESIS v1 se mantienen pero **subordinadas explícitamente al propósito de construir sueños**.

### 4.1. Vehículo soberano con canal dúplex permanente

El iPhone con la app Flutter del Monstruo es el ejecutor del sueño que reporta sin parar al piloto. Comunicación bidireccional permanente, telemetría narrada (no logs crudos), inyección de contexto mid-task sin frenar, pausar/intensificar/abortar subtareas específicas. **Sin esto, no hay forma de construir sueños largos sin perder al piloto en el camino.**

### 4.2. Sistema inmune declarativo contra debilidades LLM

Cada debilidad documentada de las LLMs tiene un anticuerpo específico. Validación en tiempo real, verifier multi-modelo, memoria episódica externa, capa antibloqueo, canal dúplex, registro forense vivo, router Pareto-óptimo. **Sin esto, los sueños largos colapsan a la mitad por degradación natural de los modelos.**

### 4.3. Embriones-Sabios soberanos productores 24/7

Organismos especialistas por dominio, con cuatro funciones internas: vigilancia activa, clasificación oro/plata/diamante/ruido, procesamiento smart de capacidades y costos, conversión a gasolina premium. Crecen orgánicamente con la actividad del piloto. **Sin esto, cada sueño parte de cero. Con esto, cada sueño parte con magna fresca pre-refinada en el dominio que importa.**

### 4.4. Meta-coordinador como protocolo declarativo, no como agente

Código determinista (grafo de estado + planificador estructurado) que orquesta agentes. LLM solo se invoca como tool de razonamiento puntual. **Sin esto, el coordinador hereda las debilidades LLM que el sistema inmune intenta cancelar.**

### 4.5. Traductor invisible de intención (interacción tranquila)

El piloto habla prosa tranquila. El Monstruo traduce a verbos atómicos invisibles (INYECTAR, REDIRIGIR, PAUSAR, INTENSIFICAR, ABORTAR, ACLARAR, REPORTAR). El piloto nunca ve la traducción. **Sin esto, el piloto se cansa o se desconecta del proceso largo del sueño.** **Operativa formal:** ver `bridge/ANEXO_PROTOCOLOS_SATELITE_v1_2026_05_28.md` §3 "Protocolo Gramática de Pilotaje".

### 4.6. Calendario de Oportunidad

El motor decide cuándo arde y cuándo descansa. Tareas costosas se ejecutan cuando el costo es mínimo. Tareas urgentes cuando son más valiosas. **Sin esto, los sueños largos cuestan demasiado o llegan tarde.** **Operativa formal:** ver Anexo §4 "Protocolo Calendario de Oportunidad".

### 4.7. Cámara de Chispa (bucle virtuoso piloto-Monstruo)

El forjador del sueño firmable. Detecta cuándo el piloto está en modo cómodo y le lanza preguntas detonadoras. Procesa la chispa con profundidad cuando el piloto la lanza. Mantiene el músculo cognitivo del piloto. Coach soberano, no asistente complaciente. **Sin esto, los sueños se diluyen al primer obstáculo, o el Monstruo se vuelve muleta y el piloto se atrofia.** **Operativa formal:** ver Anexo §2 "Protocolo Cámara de Chispa".

---

## 5. Las cuatro directivas magnas

### Directiva Magna I — "Mejora Perpetua, Promoción del Piloto"

> *El Monstruo se diseña para mejorar permanentemente la calidad, velocidad y costo de sus decisiones, con el propósito final de liberar al piloto humano de la operación táctica y promoverlo al rol estratégico superior. La meta no es asistir al piloto. La meta es que el piloto deje de necesitar asistir.*

- **Ley A** — La autonomía del Monstruo es **ascendente, no estática**.
- **Ley B** — La mejora se mide por el **tiempo que libera al piloto**, no solo por output.
- **Ley C** — La consulta entre IAs **precede** a la consulta al humano.

### Directiva Magna II — "Autonomía con Frontera Pragmática (PAFP)"

> *El Monstruo opera con autonomía total por default. La única frontera es lo irreversible o de alto impacto externo, donde se requiere firma binaria del piloto antes de actuar.*

| | Filosofía | Ejemplos |
|---|---|---|
| **Default (autonomía)** | Ejecuta solo, informa después | Selección de modelo IA, costos normales, gestión de Embriones, refresco de gasolina, registro forense, consulta a IAs hermanas, retoque de prompts internos |
| **Frontera (firma)** | Firma binaria antes de actuar | Publicar contenido externo, gasto arriba de presupuesto razonado, modificar config profunda del kernel, borrar memoria persistente |

### Directiva Magna III — "Magia en el Frente, Rigor en el Reverso"

> *El piloto nunca debe sentir la complejidad del sistema, pero el sistema nunca debe perder rigor por hacerla invisible. La superficie es prosa tranquila. La profundidad es schema, JSON, contrato firmado, código determinista.*

### Directiva Magna IV — "Diseño Perfecto, Ejecución Imparable"

> *El Monstruo invierte la economía del tiempo IA. Toma el tiempo que el sueño requiera en diseñar la pista, los tramos, los vehículos, los insumos y la coreografía completa antes de iniciar la ejecución. Una vez que la ejecución comienza, opera a máxima velocidad con mínima fricción porque toda contingencia fue anticipada en diseño. El Monstruo no improvisa en pista — improvisa en mesa de diseño, y ejecuta lo diseñado.*

- **Ley D** — El Monstruo NUNCA inicia ejecución de un sueño L1-L3 sin haber completado fase de diseño con audit interno.
- **Ley E** — La fase de diseño puede demorar lo que el sueño requiera; el reloj externo es irrelevante.
- **Ley F** — Cualquier fricción descubierta en ejecución vuelve a la mesa de diseño como **error registrable en el Forense Vivo**, para que el siguiente sueño nazca con esa anticipación incluida.

### 5.1. (NUEVO v1.2) Las tres consecuencias operativas de la Ley C

La Ley C — *"la consulta entre IAs precede a la consulta al humano"* — es procedimentalmente densa. v1.1 la enunció pero no la operativizó. v1.2 la operativiza en tres consecuencias firmadas por el piloto en el hilo:

**Consecuencia 1 — Ante ambigüedad genuina, el default del Monstruo es consultar a una IA hermana, no al piloto.** El Monstruo nunca interrumpe al piloto con una pregunta resoluble por otra IA disponible en su red soberana.

**Consecuencia 2 — La consulta a IA hermana es visible para el piloto pero no bloqueante.** El piloto puede asomarse, intervenir o ignorar. Si ignora, confía en el proceso y la decisión avanza.

**Consecuencia 3 — Solo lo irreversible (la Frontera Pragmática) requiere firma del piloto.** Todo lo demás se resuelve en el enjambre de IAs.

La operativa concreta — qué considera ambigüedad consultiva, qué IA elegir según dominio, cómo cerrar un ciclo de consulta, qué pasa si la IA hermana también duda, cómo registrar la consulta en el Forense Vivo — vive en `bridge/ANEXO_PROTOCOLOS_SATELITE_v1_2026_05_28.md` §1 "Protocolo de Ambigüedad Consultiva".

---

## 6. El Contrato de Sueño Firmado — objeto inmutable

Cada sueño firmado se materializa como un **Contrato de Sueño Firmado**, objeto inmutable que vive en el Monstruo durante todo el ciclo del sueño.

### 6.1. Estructura mínima del Contrato

```
CONTRATO DE SUEÑO FIRMADO #NNN

Nombre del Sueño:
Soñador (firmante humano):
Fecha de detonación:
Fecha de firma:

Nivel: [L1 | L2 | L3 | L4 | L5]

Estado terminal del sueño:
  (Qué significa "construido". Criterio binario de cierre.)

No incluye:
  (Lo que explícitamente queda fuera de scope, para evitar deriva.)

Vehículo principal:
  (El sistema/agente que opera como ejecutor central.)

Embriones-Sabios involucrados:
  (Lista de dominios cuya gasolina alimentará el sueño.)

Frontera pragmática:
  (Qué decisiones requieren firma binaria del piloto durante construcción.)

Métricas 4D:
  Calidad — cómo se mide
  Velocidad — cómo se mide
  Costo razonado — presupuesto aproximado
  Liberación del piloto — # de intervenciones esperadas máximo

Validación de cierre:
  (Prueba binaria que demuestra que el sueño está realmente construido.)

Ritmo:
  Dictado por la complejidad del sueño, no por reloj externo.
  Las paradas son estratégicas. La carrera no se detiene.
```

### 6.2. Inmutabilidad del Contrato

Una vez firmado, el Contrato es **inmutable salvo por revisión consciente** del piloto. Esto previene que el Monstruo derive durante la construcción y termine entregando algo distinto al sueño firmado. Si el piloto quiere cambiar el sueño en medio de construcción, **debe firmar revisión explícita** que se versiona como v1.1, v1.2, etc.

Esto es la salvaguarda contra el problema documentado en literatura de IA: **agentes que olvidan el objetivo original durante ejecución larga**. El Contrato de Sueño Firmado es el **ancla anti-deriva**.

---

## 7. La paradoja bootstrap — cómo nace el Monstruo magna

El primer sueño firmado del Monstruo es **construirse a sí mismo en su forma magna**. Esto plantea una paradoja: necesita maquinaria perfecta para construir maquinaria perfecta. La resolución es **bootstrap**, el principio por el cual la vida y todos los sistemas complejos se autoconstruyen:

> *El primer compilador de C se escribió en ensamblador. Una vez que existió C básico, los compiladores siguientes de C se escribieron en C.*

El Monstruo Embrionario v0.7 que existe hoy (kernel + app Flutter + memoria + Embriones esqueleto + Thread Immunity + Sabios + Manus B + Cowork) tiene **suficientes piezas mínimas** para empezar a construir el Monstruo magna FORJA OMEGA v1.0.

Cada componente nuevo de FORJA OMEGA que se construya **eleva la capacidad del Monstruo** para construir las siguientes componentes. El proceso es escalonado: en el tramo 1, Monstruo v0.7 construye el Sistema Inmune declarativo; en el tramo 2, Monstruo v0.8 (ya con Sistema Inmune) construye los Embriones-Sabios completos; en el tramo 3, Monstruo v0.9 (con Inmune + Embriones) construye el Pit Wall; y así sucesivamente, hasta que en el tramo final, **el Monstruo magna FORJA OMEGA v1.0 está construido**, usando como herramienta versiones cada vez más capaces de sí mismo.

**Cada tramo eleva la maquinaria que construye el siguiente tramo.**

### 7.1. La perfección es asintótica

FORJA OMEGA "terminado" es un concepto problemático. Como la maquinaria mejora con uso (Directiva I), **el Monstruo nunca está realmente "terminado"**. Lo que tiene sentido es:

- **v1.0 firmable** = un estado donde las 7 componentes inéditas están operativas, integradas, produciendo valor verificable
- **v1.1, v1.2, v2.0** = mejoras subsecuentes construidas por el propio Monstruo
- **versión asintótica** = aspiración inalcanzable, exactamente como debe ser

---

## 8. Las métricas de carrera (cómo se mide la mejora)

FORJA OMEGA no se mide contra benchmarks externos (MobileWorld, GAIA, SWE-bench), aunque puede correrlos como prueba. Se mide contra **su propia mejor ejecución previa** en cuatro ejes:

| Eje | Pregunta de cierre |
|---|---|
| **Calidad** | ¿El resultado fue mejor que la última vez en este tipo de sueño? |
| **Velocidad** | ¿Se construyó más rápido que la última vez? |
| **Costo razonado** | ¿Se gastó menos sin sacrificar calidad? |
| **Liberación del piloto** | ¿Hubo menos intervenciones humanas que la última vez? |

Cada ejecución entra al Forense Vivo en estos cuatro ejes. Las lecciones entran como **provisionales**. Si después de N ejecuciones siguen produciendo mejoras, se canonizan automáticamente. Si producen regresiones, se invalidan automáticamente. Sin curaduría manual, sin cuarentena humana — autorregulación orgánica por evidencia de uso real.

---

## 9. Estado de partida — Monstruo Embrionario v0.7 (28 may 2026)

**Construido y operativo:** Kernel Python con 18 endpoints en Railway productivo, Gateway con AG-UI SSE streaming nativo iPhone↔kernel (877 LOC), App Flutter con 66 archivos y 15 480 LOC Dart en 13 features (chat, embrion, embrion_inbox, files, finops, hilo, memory, moc, modes, onboarding, republic, sandbox, settings), feature `hilo` con SPR-MOBILE-HILO-AGUI-001 ya implementado, persistencia con Hive activo + SharedPreferences, 9 tablas `forja_*` en Supabase con 287 tablas totales y 328 RPCs, Genome vivo con `binario_100=true` (103 repos, 19 servicios Railway, 26 migraciones), Embriones esqueleto con ciclos operativos, Thread Immunity con CLOSE_CANONIZED forenses, memoria episódica multi-domain en Supabase, DSC firmados, MAOC, SOP, Protocolo Memento, Puente Inter-Hilos, Brand DNA Forja documentado, 6 Sabios consultables vía API integrada, Manus B (este hilo) + Manus A (Cowork) operativos como manos del piloto.

**Lo que falta construir (delta para v1.0):**

| Componente | Estado actual | Delta |
|---|---|---|
| Propósito Magna Constructor de Sueños | Cristalizado en TESIS v1.2 | Implementar como protocolo de firma de sueños |
| Contrato de Sueño Firmado | Diseñado en TESIS v1.2 | Construir objeto + persistencia + UI |
| Sistema Inmune declarativo | Disperso en skills | Cristalizar como capa transversal consultable |
| Pit Wall (antibloqueo) | Parcial en Thread Immunity | Generalizar a todo ciclo de sueño |
| Embriones-Sabios productores 24/7 | Esqueleto sin destilería interna | Construir las 4 funciones por dominio |
| Meta-coordinador como protocolo | Mezcla de scripts ad-hoc | Diseñar grafo declarativo formal |
| Traductor invisible de intención | UI conversacional simple | Capa traducción prosa→verbos atómicos (Anexo §3) |
| Calendario de Oportunidad | No existe | Construir scheduler de costo/momento (Anexo §4) |
| Cámara de Chispa | Concepto nuevo | Diseñar como especialización del Monstruo (Anexo §2) |
| Registro Forense Vivo 4D | Parcial en magna_cache | Auto-regulado con peso provisional |
| Niveles L1-L5 + Bandeja de Sueños | Concepto nuevo | Construir UI + lógica de coexistencia |
| Ambigüedad Consultiva | Mencionada como Ley C | Construir router de consulta entre IAs (Anexo §1) |
| Asomarse Opcional | Nuevo en v1.2 | UX que muestre lo necesario, profundidad bajo demanda |
| Transición de Fase del Piloto | Nuevo en v1.2 | Modelo de fases del piloto y promoción consciente |

El delta es grande pero **no se construye desde cero**. Sobre lo existente, se añade la capa que falta. Es ingeniería de capas, no greenfield.

---

## 10. La ruta Le Mans — cómo se construye sin parar

FORJA OMEGA se construye con la misma filosofía con la que opera: **tramos cortos, paradas estratégicas, motor nunca apagado**.

Cada tramo (sprint) tiene un objetivo único de uno de estos siete tipos: investigar, desatorar, cargar contexto, guardar, auditar, reparar o rediseñar. **Ningún tramo construye y deja roto.** Cada tramo termina dejando el siguiente listo para arrancar sin fricción. La carrera continúa.

La primera ronda de tramos (post-firma de TESIS v1.2 y Contrato de Sueño Firmado #001) se diseña así:

| Tramo | Tipo | Objetivo |
|---|---|---|
| **Tramo 0** | Guardar | TESIS v1.2 firmada + Contrato #001 firmado + Anexo de Protocolos Satélite firmado |
| **Tramo 1** | Investigar+Diseñar | Arquitectura técnica binaria de Sistema Inmune + Pit Wall + Meta-coordinador |
| **Tramo 2** | Investigar+Diseñar | Arquitectura técnica binaria de Embriones-Sabios + Registro Forense Vivo 4D |
| **Tramo 3** | Investigar+Diseñar | Arquitectura técnica binaria de Traductor invisible + Cámara de Chispa + Calendario de Oportunidad + Ambigüedad Consultiva |
| **Tramo 4** | Diseñar | Plan de implementación con orden de sprints, dependencias y métricas de salida |
| **Tramo 5+** | Construir | Ejecución por Manus A con audit de Cowork, milestones firmados por Alfredo |
| **Tramo final** | Auditar | Validación de cierre — el Monstruo magna v1.0 firma y construye un sueño L2 desde cero como prueba de capacidad |

Cada tramo se ejecuta consultando a los 6 Sabios en su versión flagship actual antes de cristalizar.

---

## 11. Lo que esta tesis explícitamente NO es

- **NO es una arquitectura técnica.** Es la brújula filosófica y operativa.
- **NO es un roadmap de fechas.** Es marco contra el cual se priorizan sprints.
- **NO es promesa al usuario final.** Es contrato interno entre Alfredo y el Monstruo.
- **NO es marketing.** Es ingeniería de visión.
- **NO es definitiva.** Es v1.2, sujeta a iteración compuesta conforme se ejecuta.

---

## 12. Validación contra autoboicot

**Pregunta 1 — ¿Lo que propone ya existe en el mundo al 28 mayo 2026?**

NO. Investigación frontera (Air Street State of AI, MobileWorld 51.7% best, ScenDroid catastrophic collapse long-horizon, AgentAtlas 6 gates ningún modelo gana, Mimosa Framework 43.1% ScienceAgentBench, HAL 33× cost spread, Berkeley RDI demos explotables) confirma binario que la combinación de las 7 componentes + 4 directivas + Constructor de Sueños + Contrato Firmado + Asomarse Opcional + Transición de Fase del Piloto **no existe** en ningún producto, paper o framework conocido.

**Pregunta 2 — ¿Lo que propone construir, ya está parcialmente construido en el ecosistema del Monstruo?**

SÍ. Monstruo Embrionario v0.7 tiene kernel, AG-UI, app Flutter, memoria episódica, Embriones esqueleto, Thread Immunity, DSC firmados — todo eso ya vive. FORJA OMEGA es **completar y orquestar lo existente más añadir las capas inéditas**. No es greenfield.

**Pregunta 3 — ¿Lo que propone, lo puede ejecutar Alfredo + Manus A + Cowork + 6 Sabios en sprints Le Mans?**

SÍ, con disciplina de tramos cortos y bootstrap escalonado. Cada componente tiene complejidad alta pero acotable. Lo ambicioso es la combinación, no cada pieza por separado.

Las tres respuestas son positivas. **Procede firma.**

---

## 13. Firma binaria

| Rol | Nombre | Firma |
|---|---|---|
| **Visión** | Alfredo Góngora | _________________________ |
| **Cristalización v1.2** | Manus B (este hilo) | 2026-05-28 |
| **Audit estructural** | Cowork (Hilo A manus_a) | _pendiente_ |
| **Validación final** | 6 Sabios versión flagship | _pendiente Tramo 1_ |

Una vez firmada, esta tesis es **inmutable** salvo por revisión consciente. Las iteraciones futuras se hacen como **anexos v1.3, v1.4** documentando qué cambió y por qué.

---

## 14. Citas de cierre — las palabras del piloto

> *"Yo me imagino una meta-coordinación de procesos previamente establecidos y autónomos... un diseño arquitectónico casi de otra galaxia para poder obtener resultados muy acordes a los que daría algo de otra galaxia superior 100× de manera binaria a lo que hemos visto hoy."*

> *"El Monstruo no debe nacer de prompts, debe nacer de construcción de un sueño conceptual o producto terminado muy ambicioso. Una vez que se firma el sueño empieza a trabajar la maquinaria del Monstruo... ese es el verdadero propósito del Monstruo, hacer realidad sueños ambiciosos, monstruosos."*

> *"La magia es que en ejecución se cumple el principio de que el Monstruo se toma el tiempo necesario en diseñar la perfección para que la carrera de ejecución sea a máxima velocidad con la menor fricción posible."*

> *"Mi primer sueño es la máquina que construye sueños. ¿Cómo sería eso posible?"*

**(NUEVO v1.2)** Cita que detonó §15 Asomarse Opcional:

> *"Si el piloto decide intervenir podría hacerlo, pero si ni siquiera lo ve porque confía en su vehículo y procesos, no pasaría nada — seguramente la decisión fue correcta porque así lo diseñamos para cada vez mejorar; es decir, hay una mejora perpetua."*

**(NUEVO v1.2)** Cita que detonó §16 Transición de Fase del Piloto:

> *"Yo cada vez trato de ir con lo que la IA me recomienda o con lo que otras IAs me recomiendan; ya no compito en razonamiento. Mi alta participación actual es una consecuencia necesaria ante los fallos naturales actuales como alucinaciones, pérdidas de contexto, pero en un escenario donde ya estamos funcionando bien, cuando el vehículo IA quiera consultar algo, lo mejor sería consultarlo con otra IA por default."*

— Alfredo Góngora, 28 mayo 2026, sesión de detonación de FORJA OMEGA con Manus B

---

## 15. (NUEVO v1.2) El Principio del Asomarse Opcional

La telemetría del Monstruo siempre está disponible **para asomarse**, nunca **para vigilar**. El piloto no necesita leer todo lo que pasa. Pero todo lo que pasa queda **inspeccionable a demanda**. Si en seis meses el piloto quiere entender por qué el Monstruo decidió X en algún momento, ahí está el rastro completo. Pero no necesita leer ese rastro diariamente.

### 15.1. La diferencia binaria

Esto es **transparencia sin obligación de vigilancia**. Es la diferencia binaria entre dos modelos que parecen iguales pero no lo son:

| Modelo | Filosofía | Efecto en el piloto |
|---|---|---|
| **Banco con estado de cuenta detallado obligatorio** | Te muestra todo, te obliga a revisar | Carga cognitiva permanente, ansiedad de control |
| **Banco con acceso al detalle bajo demanda** | Te muestra lo necesario, profundizas si quieres | Confianza estructural, atención liberada |

El Monstruo opera bajo el segundo modelo. La transparencia es **derecho del piloto, no deber del piloto**.

### 15.2. Consecuencias de diseño UX

Este principio cambia el diseño de la app del Monstruo de manera concreta y binaria:

**Consecuencia A — La app NO muestra todo lo que el Monstruo está haciendo.** Muestra lo que el piloto necesita saber ahora más un acceso fácil a profundizar si quiere. UX minimalista con profundidad bajo demanda.

**Consecuencia B — Las consultas a IAs hermanas (§5.1) son visibles pero no notificadas.** Aparecen en una bandeja consultable, no en push notifications. El piloto se asoma cuando quiere.

**Consecuencia C — El Forense Vivo está navegable pero no obligatorio.** El piloto puede pedir "muéstrame por qué decidiste X" y obtener trazabilidad completa, pero no recibe reportes diarios no solicitados.

**Consecuencia D — Las decisiones del rango Default de la PAFP (autonomía total) se ejecutan silenciosamente con registro disponible.** Solo las decisiones del rango Frontera (firma binaria) interrumpen al piloto.

### 15.3. Por qué este principio es enemigo del SOTA

Todos los agentes IA del SOTA (Manus, Genspark, ChatGPT Tasks, Claude, Operator) operan bajo el primer modelo: telemetría intrusiva, notificaciones, dashboards detallados que demandan atención. Esto se justifica con "transparencia", pero el efecto real es **convertir al usuario en supervisor permanente**, lo que contradice la Directiva Magna I (Promoción del Piloto). El Monstruo rompe con esto: la transparencia es real, pero la atención del piloto es sagrada.

---

## 16. (NUEVO v1.2) Anexo Transición de Fase del Piloto

El piloto humano no es estático. A lo largo del ciclo de vida del Monstruo, el rol de Alfredo cambia de manera consciente y diseñada. Este anexo codifica los cuatro estados de fase del piloto y la lógica de promoción, basado en sus palabras verbatim del 28 mayo 2026.

### 16.1. Los cuatro estados de fase

**Fase P0 — Compensador de fallos.** El piloto interviene intensivamente para compensar alucinaciones, pérdidas de contexto, errores de ejecución del Monstruo. Esta es la fase actual al 28 mayo 2026. La participación del piloto es alta por necesidad estructural, no por preferencia.

**Fase P1 — Auditor activo.** El Monstruo ya ejecuta correctamente la mayoría de sueños L3-L5 y los L1-L2 con asistencia. El piloto interviene principalmente en momentos de firma (Fase B), audit de cierre, y dirección estratégica de sueños magna. Su atención táctica diaria se reduce.

**Fase P2 — Soñador profesional.** El Monstruo ejecuta L1-L4 con autonomía. El piloto interviene casi exclusivamente en detonación de chispas nuevas (Fase A), firma de Contratos (Fase B), y validaciones de cierre (Fase D final). Su trabajo principal es **soñar mejor cada vez**, refinar el sueño, mantener la chispa.

**Fase P3 — Director estratégico.** El Monstruo ha alcanzado madurez magna. El piloto opera al nivel de visión y rumbo: define qué clase de sueños vale la pena soñar, audita la dirección del ecosistema, gobierna decisiones de Frontera Pragmática extrema. La operación cotidiana es invisible para él porque confía estructuralmente en la maquinaria.

### 16.2. Criterios de promoción entre fases

La promoción de una fase a la siguiente NO la decide solo el Monstruo ni solo el piloto. Es **conjunta y basada en evidencia del Forense Vivo**. Los criterios binarios para cada promoción son:

| Promoción | Criterio binario |
|---|---|
| **P0 → P1** | El Monstruo ha ejecutado N sueños L3-L4 sin intervención del piloto en ejecución, con Métricas 4D mejorando contra ejecución previa, durante un período mínimo M. |
| **P1 → P2** | El Monstruo ha ejecutado N sueños L1-L2 con éxito, el Eje "Liberación del piloto" ha caído sostenidamente bajo umbral T, y el piloto verifica subjetivamente que confía en la maquinaria. |
| **P2 → P3** | El Monstruo ha demostrado capacidad ouroboros (firmar y construir sueños L2 desde cero sin intervención humana) y está mejorando perpetuamente sin dirección táctica del piloto. |

Los valores de N, M, T se determinan en el Tramo 4 del Sueño Firmado #001 cuando se diseñe el Forense Vivo 4D.

### 16.3. Reflejo en la autonomía del Monstruo

La Ley A (autonomía ascendente) está acoplada a esta transición de fase. La autonomía del Monstruo es función monótona creciente de la fase del piloto: a mayor fase, mayor autonomía permitida por default.

| Fase del piloto | Default de autonomía del Monstruo |
|---|---|
| **P0** | Autonomía conservadora — más consultas al piloto, frontera pragmática amplia |
| **P1** | Autonomía estándar — la PAFP definida en §5 aplica |
| **P2** | Autonomía elevada — frontera pragmática se reduce a lo verdaderamente irreversible |
| **P3** | Autonomía total — el Monstruo solo consulta al piloto en Detonación y Firma de sueños magna |

### 16.4. Riesgos de subir o bajar de fase prematuramente

**Riesgo de promoción prematura:** otorgar autonomía P2 al Monstruo cuando todavía es estructuralmente P0 produce ejecución sin control y deriva. El Monstruo lo previene exigiendo evidencia binaria de Métricas 4D antes de proponer promoción.

**Riesgo de regresión innecesaria:** mantener al piloto en P0 cuando la maquinaria ya merece P1 atrofia al piloto en patrones de supervisión innecesaria. La Cámara de Chispa detecta esto y propone promoción cuando se cumplan los criterios.

### 16.5. Métricas que el Monstruo usa para reconocer la fase del piloto

El Monstruo no asume la fase. La infiere de evidencia observable: frecuencia de intervenciones del piloto, latencia de aprobación en Frontera Pragmática, profundidad de las chispas que el piloto detona en Cámara de Chispa, tasa de aceptación de las recomendaciones del Monstruo, tono y volumen de prosa tranquila vs prosa dirigida, tiempo dedicado al asomarse opcional vs al soñar. Cuando estas métricas converjan a un perfil de fase superior durante el período mínimo M, el Monstruo propone la promoción al piloto, quien la acepta o la rechaza explícitamente.

---

## 17. (NUEVO v1.2) Cross-references al Anexo de Protocolos Satélite

Esta tesis es la brújula filosófica. La operativa concreta de los componentes que requieren protocolo procedimental vive en `bridge/ANEXO_PROTOCOLOS_SATELITE_v1_2026_05_28.md`, un solo documento con cuatro secciones para consulta operativa rápida del Monstruo:

| Sección Anexo | Concepto en TESIS v1.2 | Cross-reference |
|---|---|---|
| §1 Protocolo de Ambigüedad Consultiva | Ley C (Directiva I) + §5.1 | Cómo el Monstruo consulta a una IA hermana ante duda |
| §2 Protocolo Cámara de Chispa | §4.7 Cámara de Chispa | Cómo opera el bucle virtuoso piloto↔Monstruo |
| §3 Protocolo Gramática de Pilotaje | Directiva III + §4.5 Traductor invisible | Cómo se traduce prosa tranquila a verbos atómicos |
| §4 Protocolo Calendario de Oportunidad | §4.6 Calendario | Cuándo cada Embrión y cada sueño avanzan |

El Anexo es **lectura obligatoria** para el Monstruo durante el Tramo 3 del Sueño Firmado #001, cuando se diseñe la arquitectura técnica de estos cuatro componentes.

---

**Fin de TESIS v1.2.**

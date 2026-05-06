# EL MONSTRUO — Arquitectura del Sistema Operativo Personal Soberano

> **Documento de visión v1.2**
> **Autor:** Cowork (Hilo A), compilado de iteración con Alfredo González (2026-05-04 → 2026-05-06)
> **Naturaleza:** documento técnico-arquitectónico privado para Alfredo y los hilos Manus. NO destinado a comunicación externa.
> **Estado v1.2:** evolución sobre v1.1. Cambios estructurales nuevos: (1) arquitectura de **tres Catastros paralelos** (Modelos LLM + Suppliers Humanos + Herramientas AI Especializadas) que reemplaza al Catastro único como motor de orquestación, (2) **Patrón Convergencia Diferida** firmado para el portfolio (proyectos arrancan autónomos con infra compartida y convergen en momentos elegidos cuando ambos prueban PMF), (3) **Catastro de Herramientas AI Especializadas** como capability transversal nueva (renderers, video gen, voice synthesis, document parsing especializado), (4) **Mapa de Ejes de Convergencia Futura** en Cap 10 documentando los ejes ya identificables del portfolio, (5) anclaje del Marketplace de Interiorismo + Roche Bobois como ejes de convergencia con CIP (no como módulos absorbidos por default).
> **Cambios preservados de v1.1:** kernel + multi-transport, A2UI v0.9 como protocolo, ejecución consciente, captura ambient con kill switch verbal, Smart Notebook conectada al río, Modo Cripta preservación-firme/simulación-diferida, CIP anclado como primera empresa-hija, protocolo Monstruo-a-Monstruo diferido a v1.3+.
> **Fuente de las iteraciones v1.2:** sesión Cowork-Alfredo del 2026-05-06 (post-recovery v1.1) con onboarding completo de la Capilla de 35 DSCs + Matriz de Cruces 20×20 + Inventario v3 de 20 proyectos, + iteración detonada por la realidad de Marketplace de Interiorismo + necesidad de renderizado AI con proveedores reales. Decisiones firmadas en DSC-X-006 (Convergencia Diferida) y DSC-G-007 (3 Catastros paralelos + integración herramientas AI verticales).

---

## Cómo leer este documento

Este documento condensa la visión de la interfaz del Monstruo y de la postura del proyecto entero, surgida de una conversación de diseño densa entre Alfredo y Cowork. Está estructurado en 16 capítulos más un apéndice. Cada capítulo es denso por intención: no hay retórica de marketing, no hay pitch, no hay aspiracional inflado. Es para uso operativo de quien construye el Monstruo.

La regla que rige el documento mismo es la regla que rige el Monstruo: **menos es más, verdad cruda sobre retórica elaborada, lo poderoso vive bajo discreción**.

---

## Capítulo 0 — Marco filosófico y reglas inviolables

### Lo que el Monstruo es

El Monstruo es **el sistema operativo personal soberano de Alfredo González**. No es un producto SaaS para escalar a millones de usuarios. No es una startup VC-funded buscando exit. No es una herramienta freemium con pricing tiers. Es la herramienta que Alfredo construye para sí mismo, con la disciplina de un artesano magna, con el cuidado estético de Apple y la ambición técnica de Tesla. Eventualmente, versiones reducidas pueden ser otorgadas selectivamente por Alfredo a personas que él reconozca como aportadoras de valor real al mundo.

### Lo que el Monstruo NO es

No es Linux. Linux es infraestructura técnica neutral, sin memoria personal de nadie, distribuible sin riesgo. El Monstruo es un sistema que toca vidas íntimas, documenta decisiones, almacena credenciales, lee mensajes y fotos. Open source de un sistema que toca esa capa requiere que cada fork mantenga la garantía ética — y eso no se puede exigir bajo licencia abierta. Una vez que el código está afuera, alguien puede modificarlo para abusar de la capa íntima.

No es un producto para "todos". La aspiración romántica de "regalar al mundo lo más poderoso del mundo" se desmorona con un solo dato fáctico: las herramientas más poderosas atraen a los peores actores antes que a los mejores. Cárteles, grupos criminales, manipuladores masivos, aspirantes a dictadores — todos serían usuarios prioritarios de un orquestador AI autónomo end-to-end abierto a cualquiera. La distribución indiscriminada de poder concentrado no equivale a beneficio universal. Cuando algo es genuinamente poderoso, su contribución al mundo depende más de quién lo controla que de cuántos lo tienen.

No es un producto para escalar masivamente. Sin masividad como objetivo, desaparecen las urgencias de marketing, growth hacking, feature parity con ChatGPT/Claude/Manus, métricas DAU/MAU, onboarding optimizado para masas. Lo que aparece en su lugar: urgencia de que TODO funcione perfecto para Alfredo primero, urgencia de que las empresas-hijas funcionen y monetizen, urgencia de que el SMP sea inviolable, urgencia de que el Cockpit sea hermoso porque es donde Alfredo vive como arquitecto.

### Las reglas inviolables del Monstruo

**Regla uno — Menos es más.** Cada feature, cada pantalla, cada palabra en la UI tiene que justificar su existencia. La complejidad va abajo en backend; la cara visible es austera. Si una feature no cumple un Objetivo Maestro o no es esencial, no entra.

**Regla dos — Si no es bonita no motiva, si es fea parece que no sirve.** Calidad Apple/Tesla aplicada a cada pixel. Brand DNA forja (#F97316) + graphite (#1C1917) + acero (#A8A29E) aplicado con minimalismo, no con densidad Bloomberg. Whitespace abundante. Tipografía cuidada. Animaciones físicas. Haptic feedback. Dark mode nativo.

**Regla tres — Silencio inteligente.** El Monstruo es callado por defecto. Habla solo cuando le preguntan. Cuando habla, dice lo mínimo necesario que abre espacio adentro de la persona, no la respuesta que cierra. Cero notificaciones falsas, cero gamification, cero engagement traps, cero streaks. Como un viejo amigo sabio que no necesita performar sabiduría.

**Regla cuatro — El Monstruo describe, no prescribe.** Especialmente en el modo confidente y en las reflexiones de Cronos: el Monstruo NUNCA dice "deberías hacer X". Dice "veo que en patrones similares pasó X — ¿qué te resuena?". Anti-coaching invasivo. Espejo, no entrenador.

**Regla cinco — Verdad cruda sobre retórica elaborada.** A veces la respuesta más útil es la más simple. *"No, porque los carteles lo van a usar"* es más fuerte que cinco párrafos filosóficos. El asistente puede entrar en "modo detractor" cuando hace falta — confrontar al usuario con verdades incómodas para clarificar el camino. Es respeto al adulto, no abrasividad.

**Regla seis — Anti-influencia inadvertida.** El Monstruo NUNCA debe sembrar convicciones nuevas en una persona sin que esa persona las chequee con sus propios valores y con tiempo. Esto es Capa Memento aplicada a influencia. Articular lo que la persona ya tiene en la cabeza es válido; detonar arquitecturas elaboradas que la persona pueda adoptar pasivamente no lo es.

**Regla siete — Privacidad como garantía técnica inviolable, no como promesa.** La discreción no es opción. La criptografía hace imposible que datos personales sean leídos por nadie excepto el usuario. No porque el equipo de desarrollo no quiera, sino porque la matemática lo prohíbe. Pasamos de policy a physics.

**Regla ocho — El Monstruo no cobra fee.** Pago pass-through transparente: el usuario paga lo que cuesta cada operación a los proveedores externos. Cero margen del Monstruo. Lo gratis es genuinamente gratis. Capacity awareness siempre visible.

**Regla nueve — Sin promoción.** El Monstruo no se publicita. Se descubre. La existencia se sabe orgánicamente porque las empresas-hijas son visibles en sus mercados, y eventualmente algunas personas en el círculo lo mencionan. La discreción multiplica el valor; el marketing lo banaliza.

**Regla diez — Validación contra los 15 Objetivos Maestros.** Cualquier feature, decisión arquitectónica o cambio de visión se chequea contra los 15 Objetivos. Si viola alguno, no entra. Esta regla es regla cero del Objetivo #14 (Guardian) aplicada al diseño de la app misma.

---

## Capítulo 1 — Arquitectura general: kernel + multi-transport + ejecución consciente

### El insight fundamental que reemplaza v1.0.1

La v1.0.1 trataba al Monstruo como "una sola app Flutter con dos modos." Eso era pensamiento 2020. La iteración 2026, validada por research del estado del arte (Manus.im, Devin, Apple Intelligence cross-device, Google A2UI v0.9, ElevenLabs voice-as-interface): **el Monstruo no es una app — es un kernel con múltiples cuerpos.**

Hay un cerebro central (el kernel: LangGraph + Catastro + Embriones + memoria SMP + el motor de ejecución consciente). Hay N transports que sirven al mismo propósito desde distintos contextos: la app Flutter (Daily + Cockpit), el WhatsApp Gateway, el Apple Watch, eventualmente el Vision Pro, el Web Command Center. Todos son ciudadanos de primera clase del mismo kernel.

Esto cambia el roadmap entero. No estamos "construyendo la app Flutter del Monstruo." Estamos construyendo **N transports paralelos del mismo kernel**, donde Flutter es el más rico visualmente pero no necesariamente el más usado en LATAM (donde WhatsApp gana 72% del comercio conversacional).

### Los transports en su prioridad real

| Transport | Cuándo se usa | Prioridad de implementación |
|---|---|---|
| **WhatsApp Gateway** | LATAM cotidiano, conversacional, commerce, contacto con terceros | **P0 paralelo a Flutter** |
| **App Flutter (Daily mode)** | iPhone/iPad/Mac, voz, cámara, notas, capturas ambient principales | **P0 paralelo a WhatsApp** |
| **App Flutter (Cockpit mode)** | Mac/iPad, Alfredo como arquitecto, multi-pantalla densa | **P1 después del Daily mínimo** |
| **Apple Watch / Wear OS** | Veto rápido, voz puntual, second factor, glance | **P1** |
| **Web Command Center** | Browser desktop, dashboards públicos del ecosistema, paneles dashboard interno | **P2** |
| **Vision Pro / Quest 3** | Spatial Cronos (futuro, navegación temporal de la vida) | **P3 (v1.2+)** |

### Generative UI vía A2UI v0.9 como protocolo, no como widget

El kernel NO diseña pantallas pre-fabricadas. Emite **intenciones + esquemas A2UI v0.9** (estándar Google con esquemas declarativos JSON inyectados al system prompt), y cada transport renderiza según su capacidad. La misma intención del kernel:

- En Flutter renderiza una tarjeta hermosa con foto, mapa, botones de acción
- En WhatsApp renderiza un Interactive Message con quick replies
- En Watch renderiza una notificación rica con dictado de voz
- En Vision Pro renderiza una tarjeta espacial flotante

**No hay "diseño per pantalla" en v1.1. Hay diseño per intención + plantillas A2UI por transport.** Esto colapsa "20 pantallas que mantener" a "un catálogo de intenciones bien diseñado y N renderers por transport."

### Tres Catastros paralelos como motor de orquestación (v1.2)

El kernel del Monstruo opera con **tres motores de orquestación paralelos**, no uno. Cada uno especializado en un dominio de selección. Firmado en DSC-G-007.

| Catastro | Qué orquesta | Selección por | Ejemplos canónicos |
|---|---|---|---|
| **Catastro de Modelos LLM** (existente, v1.0+) | 50+ modelos AI generales con `confidentiality_tier` y rol macroárea | Capacidad / costo / latencia / sensibilidad | GPT-5.5 Pro, Claude Opus 4.7, Gemini 3.1 Pro, Grok 4, DeepSeek R1, Perplexity Sonar Reasoning Pro |
| **Catastro de Suppliers Humanos** (nuevo v1.2) | Profesionales y empresas que ejecutan servicios reales | Capacidad disponible / reputación / SLA / cobertura geográfica / precio | Arquitectos, valuadores certificados, fotógrafos, drone operators, firmas legales por jurisdicción, contratistas, aseguradoras, verificadores de title |
| **Catastro de Herramientas AI Especializadas** (nuevo v1.2) | Productos AI verticales líderes del mercado | Calidad output / costo / velocidad / especialidad | Renderers (RoomGPT, Modsy, Coohom, Spline AI, Luma, Polycam), video gen (Runway Gen-4, Sora 2, Veo 3), voice (ElevenLabs), document parsing (LlamaParse, Unstructured.io) |

Los tres conviven bajo el mismo patrón operativo: ranking, anti-gaming, override manual posible, manifestación contextual de uso, FinOps trackeable. Cada empresa-hija invoca el Catastro correspondiente en runtime — no hardcodea. **Excepción crítica:** modelos propios del Monstruo (Capa 3 Soberanía) son infraestructura crítica del orquestador, no herramientas verticales.

El Cockpit gana superficie nueva: **"Salud de los 3 Catastros"** — los tres motores con sus métricas de uso, tiempo de respuesta, tasa de error per-herramienta, costo acumulado, capacidad disponible.

Esto cumple Obj #7 (no reinventar rueda) + Obj #12 (soberanía agnóstica). Las herramientas AI verticales evolucionan 10x más rápido de lo que un equipo interno puede mantener; la ventaja del Monstruo es **orquestación + contexto del usuario**, no generación per se.

### Ejecución consciente como paradigma central

El Monstruo no es un servicio que invocas — es una presencia que vive contigo. Esto reemplaza el "autonomy spectrum" (HITL/HOTL/HOOL configurable por categoría) que era parche: ponía la carga de configuración sobre el usuario.

**Las 7 capas de la ejecución consciente:**

1. **Conexión persistente bidireccional.** WebSocket/SSE permanente entre transports y kernel. No hay sessions que abren/cierran. El Monstruo nunca "se desconecta" — está siempre.

2. **Ejecución concurrente con estado compartido.** Múltiples LangGraphs corriendo en paralelo, todos conectados al mismo contexto conversacional. Cuando el usuario habla, las tareas activas reciben el nuevo contexto antes de su próximo paso.

3. **Hot-mutable execution.** Las tareas son mutables en vivo. No es "abort + restart" — es "patch + continue." Si el usuario en medio de una búsqueda dice "mejor italiano," la búsqueda pivota sin reiniciar.

4. **Manifestación contextual, no broadcast.** Las tareas terminan en silencio. Resultados viven en cache. Solo se manifiestan cuando son contextualmente relevantes — no anuncian su finalización con "¡reservé!".

5. **Confianza emergente.** No hay matriz de autonomy que el usuario configure. El Monstruo aprende de Alfredo qué cosas hace solo y qué cosas pregunta. Default conservador (financiero, irreversible, social → preguntar). El umbral se mueve solo basado en patrón observado. **Cero configuración.**

6. **Anticipación silenciosa.** El Monstruo escucha la conversación y decide proactivamente que ciertas tareas valen pre-ejecutarse. Alfredo dice *"voy a Madrid en septiembre"* → el Monstruo se enriquece de info en background sin anuncio. Cuando Alfredo eventualmente pregunte, la respuesta llega con contexto curado en milisegundos.

7. **Visibilidad on-demand, no por default.** El usuario puede preguntar *"¿qué estás haciendo?"* y obtener un árbol limpio. Si no pregunta, no aparece nada. Transparencia es derecho, no push.

### Toggle entre Daily y Cockpit (dentro del Flutter app)

El acceso al Modo Cockpit requiere autenticación fuerte. Alfredo lo activa con un gesto secreto sobre el logo del Monstruo (3 dedos hold) más Face ID. Opcionalmente, segundo factor con device confiado agnóstico — Apple Watch en usuarios Apple, smartwatch Wear OS o Garmin en usuarios Android, o passphrase + biometría sola si no hay smartwatch. La regla operativa es no casarse con un fabricante específico.

### Bundle único Flutter

```
Bundle ID: com.elmonstruo.app
Plataformas iniciales: iOS, macOS
Plataformas posteriores: iPadOS (responsive desde inicio), Android (post-v1.0), Web (no prioritaria)
```

### Estructura de carpetas Flutter

```
apps/mobile/
├── lib/
│   ├── main.dart                       # ÚNICO entry point
│   ├── core/                           # capabilities completas, SIEMPRE corriendo
│   │   ├── transport/
│   │   │   └── kernel_websocket.dart   # conexión persistente bidireccional
│   │   ├── a2ui/
│   │   │   └── renderer.dart           # render generative UI per transport
│   │   ├── services/
│   │   │   ├── kernel_service.dart
│   │   │   ├── catastro_service.dart
│   │   │   ├── embriones_service.dart
│   │   │   ├── memento_service.dart
│   │   │   ├── connections_service.dart
│   │   │   ├── voice_service.dart      # voz continua + interrupción + voz brand
│   │   │   ├── visual_search_service.dart
│   │   │   ├── photo_intelligence_service.dart
│   │   │   ├── file_intelligence_service.dart
│   │   │   ├── app_intelligence_service.dart
│   │   │   ├── vault_service.dart
│   │   │   ├── shopping_service.dart
│   │   │   ├── notes_service.dart
│   │   │   ├── health_service.dart
│   │   │   ├── ambient_listening_service.dart  # always-on con kill switch
│   │   │   ├── smart_notebook_service.dart     # Cronos active layer
│   │   │   ├── cronos_service.dart
│   │   │   ├── manifestation_service.dart      # cuándo surface, cuándo silencio
│   │   │   └── replay_service.dart
│   │   ├── theme/brand_dna.dart                (forja + graphite + acero)
│   │   ├── widgets/
│   │   │   ├── a2ui_components/                (streaming-first)
│   │   │   ├── memento_badge.dart              (✓/⚠/✗ visible en ambos modos)
│   │   │   └── error_toast.dart
│   │   ├── crypto/
│   │   │   ├── smp.dart                        (Sovereign Memory Protocol)
│   │   │   ├── secure_enclave_bridge.dart
│   │   │   └── on_device_transcription.dart   # Whisper local / Apple Speech
│   │   └── state/
│   │       └── mode_provider.dart              (daily vs cockpit)
│   ├── modes/
│   │   ├── daily/                              # superficies primarias (5)
│   │   └── cockpit/                            # superficies primarias (12-15)
│   └── routing/
│       └── mode_router.dart
└── pubspec.yaml
```

Servicio paralelo:

```
apps/whatsapp_gateway/
├── kernel_bridge/
├── webhook_handler/
├── interactive_messages/
└── confidente_silent_link/                     # link silencioso del logo
```

---

## Capítulo 2 — Modo Daily

### Filosofía operativa

Modo Daily NO es "versión lite del Monstruo". Es **la cara que muestra solo lo necesario** mientras todo el poder del sistema corre abajo. Como Finder en Mac OS frente a Terminal: misma máquina, distinto detalle de exposición.

La regla rige cada decisión: cero clutter, cero badges, cero gamification, cero notificaciones falsas, cero "engagement". Si el usuario abre la app y no necesita nada, encuentra silencio sostenido por brand DNA aplicado con cuidado.

### Las 5 superficies primarias

Estas no son "pantallas fijas" — son **superficies por defecto** que A2UI generative UI puebla según el contexto. La misma superficie Home en una mañana laboral y un domingo a la noche puede verse distinta, porque el kernel emite intenciones contextuales y el renderer Flutter las compila al vuelo.

**Superficie 1 — Home.** Una superficie, un input, un canvas. El input es voice-first (push-to-talk OR voz continua según preferencia, con interrupción natural) o tap para tipear. Hay también un botón de cámara para visual search inmediato. Output del Monstruo aparece en una tarjeta A2UI minimalista debajo del input.

Adicionalmente, en el Home vive **el río de Cronos** como franja horizontal navegable bajo el input. Es la presencia silenciosa de la vida documentada, accesible con un swipe lateral pero no obligatoria.

**Superficie 2 — Threads.** Historial de conversaciones del usuario con el Monstruo, navegable, buscable. No es Slack ni iMessage — es minimalista, una conversación por línea con resumen de 1 frase, fecha relativa, categoría tonal. Tap entra a la conversación entera.

**Superficie 3 — Pendientes.** Acciones que el Monstruo necesita confirmación humana. Reservas a punto de hacerse, mensajes a punto de mandarse, decisiones HITL soft. Cada item con preview editable inline antes de confirmar (streaming approval). Si no hay nada pendiente, superficie vacía, sin "no hay nada nuevo" — solo el espacio en blanco con el brand DNA.

**Superficie 4 — Conexiones.** Qué apps externas tiene enchufadas el Monstruo. WhatsApp, Apple Mail, Gmail, Apple Calendar, Google Calendar, Apple Maps, Google Maps, Apple Photos, Google Photos, Files, Drive, Dropbox, Apple Pay, etc. Toggle individual por servicio. Permissions granulares. Audit log accesible.

**Superficie 5 — Perfil.** Identidad del usuario, configuración de privacidad, claves del SMP, recovery con Shamir's Secret Sharing, exportación de datos completos, eliminación con confirmación múltiple. Todo lo soberano vive acá.

### Voz como input dominante en Daily

Voz continua con interrupción natural ganó sobre push-to-talk en 2026 (GPT-4o, Gemini Live). El Monstruo adopta el patrón ganador. Adicionalmente: **voz única como brand positioning** — distintiva, reconocible al primer segundo, cambiable pero sin empujar el cambio. Brand DNA forja+graphite+acero aplicado al timbre: registro bajo, gravitas sin teatro, español mexicano natural, pausas con peso, calidez contenida, certeza sin arrogancia. El silencio inteligente es parte del timbre, no ausencia.

Apple Watch double-tap como **veto táctico** — interrupción rápida del agente cuando no querés lo que está haciendo, sin tener que sacar el iPhone.

### Conexiones nativas — qué realiza el Modo Daily

El usuario habla al Monstruo. El Monstruo opera con sus apps externas en background. El usuario no abre WhatsApp, no abre Maps, no abre Google. El Monstruo lo hace por él. Ejemplos:

- *"Mandale a Juan que sí confirmo"* → WhatsApp manda, check verde aparece
- *"Donde como mejor sushi cerca"* → tarjeta con 3 lugares, foto, rating sintetizado, distancia, botón [Reservar] [Cómo ir]
- *"Cuándo es la próxima reunión con Pedro"* → Calendar + Mail + WhatsApp consultados, respuesta unificada
- *"Resúmeme los mails sin leer importantes"* → 3 tarjetas con resumen, opción [Responder] [Posponer] [Archivar]
- *"Qué pasó con el peso argentino esta semana"* → tarjeta sintetizada con sources verificadas y badges Memento
- *"Buscame esto"* (con foto desde cámara) → visual search, identificación, dónde se compra, mejor precio
- *"Buscame mi DNI escaneado del mes pasado"* → photo intelligence semantic search
- *"Encontrame el contrato del local"* → file intelligence semantic search
- *"Apuntar idea: vendiendo mate energético en Colombia"* → Smart Notebook captura + conexión con menciones previas

> **Lista de "líderes cotidianos" pendiente de validación para v1.2.** El conjunto exacto de apps a las que el Monstruo se conecta nativamente requiere ciclo de investigación + descubrimiento + cruce con otras IAs antes de cerrarse. Tier 1 confirmado: WhatsApp + Mail (Apple/Gmail) + Calendar (Apple/Google) + Maps (Apple/Google) + Photos + Notes/Drive/Files. Tier 2: Pay (Apple Pay, Google Pay, MercadoPago) + Health (HealthKit + Health Connect). Tier 3+ por validar.

---

## Capítulo 3 — Modo Cockpit

### Filosofía operativa

El Cockpit es para Alfredo como arquitecto. Densidad alta pero hermosa: Brand DNA forja aplicado profundo, calidad Apple/Tesla aplicada a interfaces complejas. NO es fea-porque-densa. Es densa-porque-poderosa, y bonita-porque-cuidada.

El Cockpit es invisible para todos los usuarios excepto Alfredo (autenticación fuerte). Eventualmente, algunas personas del círculo otorgado pueden tener acceso al Cockpit con configuraciones reducidas — pero por defecto, Cockpit completo es solo para Alfredo.

### Las 12-15 superficies del arquitecto

**MOC Dashboard.** Mission Operations Center. Todos los sistemas del Monstruo en una vista: sprints corriendo, hilos Manus activos, alertas Guardian, métricas vivas, empresas-hijas operando, cron jobs. Refresh automático.

**Threads + Comando.** Chat denso con el Monstruo desde rol arquitecto. Multi-thread paralelos. Atajos magna estilo Linear/Superhuman. ⌘K abre command palette. ⌘P salta a empresa-hija por nombre. Filtros sofisticados, búsqueda semántica en historial completo.

**Portfolio Empresas-Hijas.** Tarjetas de las 20 empresas/proyectos del portfolio actual de Alfredo (7 activos, 4 en construcción, 5 en diseño, 4 nominales). Cada una con métricas vivas (tráfico, leads, ingresos, contenido publicado), zoom-in al pipeline E2E que la generó (cuando aplique), capacidad de pausar/reanudar/retirar. **CIP es el primer habitante magna del Portfolio en estado "En Diseño avanzado"** — primera empresa-hija que el Monstruo va a fabricar end-to-end.

**Catastro.** Vista densa de los 50+ modelos rankeados, filtrable por macroárea (Razonamiento, Arena humana, Coding, Razonamiento Estructurado, Embeddings). Trono Score con z-scores intra-dominio. Anti-gaming flags. Override manual posible: "este pipeline E2E, quiero que use Claude Opus 4.7 sí o sí".

**Embriones.** 9+ Embriones especializados (Critic Visual, Product Architect, Creativo, Estratega, Financiero, Investigador, Técnico, Ventas, Vigía, Manifestación, Convergencia Cronos). Cada uno con FCS (Functional Consciousness Score), última invocación, decisiones recientes. Vista del modo `debate` y `quorum` cuando se activan.

**Guardian.** Los 15 Objetivos Maestros como panel de instrumentos. Scores por objetivo (rojo/amarillo/verde). Alertas activas. Recomendaciones accionables. Nivel 1 (alerta) y Nivel 2 (bloqueo) del Corrective Actor visibles. Self-health check del Guardian mismo.

**Memento.** Semillas de error_memory (40+ acumuladas). Validaciones de pre-flight ejecutadas. Detección de contexto contaminado. Stats del Síndrome Dory evitado. Audit del SMP. Configuración de tiers de sensibilidad por tipo de operación.

**Replay (Timelapse).** Selector de runs E2E pasadas + timeline scrubable interactivo (estilo Devin Timelapse). Vos elegís una run, scrolleás el timeline, ves cada decisión paso por paso, podés bifurcar desde cualquier punto. Aplica también a conversaciones del modo confidente con vos mismo.

**Computer Use / Sandbox.** El navegador del agente, la terminal, el filesystem en vivo. Estilo Manus Computer panel pero soberano. Cuando Sprint 87 NUEVO E2E está generando una empresa-hija (incluida la complejidad de CIP con smart contracts ERC-3643), vos ves el browser haciendo deploy, los archivos creándose, los API calls saliendo.

**FinOps.** Capacity awareness completa. Tokens consumidos por hilo / por empresa-hija / por sprint. Costo desglosado por proveedor (Anthropic, OpenAI, Google, Manus, Perplexity). ROI por empresa-hija (ingresos vs costos de generación + mantenimiento). Forecast de gasto. Configuración de spending caps con alertas.

**Pipeline E2E.** Visualización del flujo del Sprint 87 NUEVO: 12 pasos lineales (intake → ICP → naming → branding → copy → wireframe → componentes → assembly → deploy → critic visual → registro → veredicto). Estado por step, intervención humana posible en cualquier paso, replay de runs pasadas, abort/retry. **Para empresas-hijas de complejidad CIP** (regulatorias, financieras, con smart contracts), el Pipeline se extiende con pasos adicionales: legal review, compliance check, smart contract audit, oracles integration.

**Coding embedded.** IDE liviano para intervenir código sin salir del Cockpit. Editor + diff viewer + ejecución sandboxed + terminal embebida. Cuando el Catastro o un Embrión sugieren un cambio de código, vos lo aprobás/editás/rechazás inline.

**Hilos Manus.** Vista de los 3+ hilos Manus activos (Catastro, Ejecutor, Memento). Cada uno con su sprint actual, status, próximos pasos, ETA recalibrada según Apéndice 1.3. Bridge accesible. Audit de tasks despachadas.

**Bridge / Comunicación inter-hilos.** Los reportes y audits viviendo en `bridge/` navegables. Decisiones arquitectónicas firmadas, semillas sembradas, specs en redacción, roadmaps. La memoria operativa del proyecto soberano accesible visualmente.

**Settings + Admin.** Variables de entorno Railway, configuración del kernel, override de defaults, gestión de tier-access (cuando exista el círculo otorgado), invitaciones nominativas. Admin de la administración.

### Atajos magna

⌘K command palette universal. ⌘P jump to portfolio empresa. ⌘E jump to Embrión. ⌘G abre Guardian. ⌘T salta a Catastro. ⌘R abre Replay del último run. ⌘shift+M toggle a Modo Daily (con biometría). Todo navegable con teclado.

---

## Capítulo 4 — Capabilities transversales

Las **8 capabilities** siguientes son servicios core que viven en `lib/core/services/` y se invocan desde ambos modos. En Modo Daily son comandos naturales con output limpio; en Modo Cockpit son superficies densas con metadata visible. Todas comparten el paradigma de ejecución consciente: corren en background paralelo, manifestación contextual, sin announcement.

### Visual Search (Google Lens-style soberano)

Apuntás cámara o subís foto. El Monstruo identifica qué es, dónde se compra, mejor precio, traduce texto en la imagen, identifica plantas/animales/edificios. Soberanía aplicada: procesamiento on-device cuando posible (embeddings locales), cloud cuando necesita capacidad mayor pero con anonimización del contenido. La cámara es botón de primera clase en el Home del Modo Daily.

### Photo Intelligence

Búsqueda semántica sobre tus fotos: *"la foto del DNI del mes pasado"*, *"las fotos del cumple de Dani"*, *"esa donde aparezco con un mate cerca del mar"*. Organización inteligente. Híbrido: la app accede a Apple Photos / Google Photos vía API, pero el ÍNDICE semántico (embeddings de qué hay en cada foto) vive en el kernel del Monstruo encriptado bajo SMP.

### File Intelligence

Mismo patrón aplicado a archivos: *"dónde guardé el contrato del local"*, *"el último PDF que firmé"*, *"limpiame Downloads de cosas viejas"*. Acceso configurable a iCloud Drive, Google Drive, Dropbox, Files local. Indexación semántica bajo SMP. Categorización automática propuesta con confirmación del usuario.

### App Intelligence

Inteligencia sobre las apps que el usuario usa: *"qué apps no usé en 3 meses"*, *"cuánto gasto en suscripciones"*, automatizaciones cross-app. Limitado por las APIs que iOS/Android exponen.

### Vault Soberano (credenciales y keys)

Passwords, API keys, secrets, certificados, llaves SSH almacenados bajo SMP. Importación de 1Password, Bitwarden, Apple Keychain. Auto-fill vía AutoFill APIs del OS. Watchtower-style: alertas de claves comprometidas, sin 2FA, duplicadas, viejas. Compartir granular con TTL automático. Integración conversacional: *"rotame todas las claves de mi servidor de Railway esta semana"* — el Monstruo lo hace step by step con confirmación HITL en cada acción.

### Shopping Intelligence

Búsqueda + comparación + checkout asistido. Integración con Mercado Libre, Amazon, Rappi, marketplaces locales. Memoria histórica de compras. Compras ejecutadas en HITL streaming con preview editable.

### Notes Intelligence (procesamiento smart minimalista)

Lectura de Apple Notes / Google Keep / Notion con permisos. Procesamiento smart minimalista: extracción de tareas implícitas, conexión con Cronos, búsqueda semántica multi-fuente, detección de ideas dormidas que vale resucitar. Esta capability se interconecta nativamente con el **Smart Notebook de Cronos** (ver Cap 5).

### Health Intelligence

Conexión con Apple HealthKit (iOS) y Health Connect (Android) más wearables específicos. Lectura de métricas — sueño, frecuencia cardíaca, HRV, actividad, peso, glucosa, presión arterial — bajo SMP, con índice semántico viviendo en el kernel del Monstruo cifrado con clave del usuario. Apple/Google ven los bytes; el Monstruo entiende el significado. Soberanía aplicada al cuerpo.

Premisa cultural: monitoreo completo de salud va a ser standard del futuro inmediato, así como hoy nadie maneja sin cinturón de seguridad. El Monstruo NO empuja a la persona a monitorear; cuando ya hay datos, los integra inteligentemente.

### Listening ambient continuo (capability base, transversal a todas)

El Monstruo está **encendido 24/7 por default** capturando ambient audio bajo soberanía técnica completa. Esto es una capability transversal que alimenta a Cronos, al Smart Notebook, y al modo confidente.

**Arquitectura:**

- **Listening client-side, jamás cloud en claro.** VAD on-device → solo se procesa cuando hay humano hablando. Transcripción on-device (Apple Speech Framework / Whisper local). Embeddings on-device. Audio crudo nunca sale del dispositivo.

- **Voice kill switch verbal "Monstruo apágate".** Wake-phrase específica entrenada on-device, latencia <200ms. Al detectarse: hardware-level mute, purga de audio bufferizado, indicación visual sutil del estado dormido. Funciona dicha por cualquiera, no solo por Alfredo (respeto por terceros sin requerirles enrolarse).

- **Reactivación por uso, sin ceremonia.** Cualquier interacción intencional reactiva: hablarle, abrir la app, mensaje en WhatsApp, tap en Watch. Cero settings, cero confirmación, cero menus.

- **Multi-shutoff jerárquico:** voz + hardware mic mute del OS (override absoluto) + tap largo en logo (slider de "dormir 1h / 8h / hasta nuevo aviso") + passphrase de duress (devuelve memoria vacía bajo coacción).

- **Privacidad de terceros:** modo invitado activable por voz que disclosa la presencia del agente; detección de contextos sensibles (hospital, doctor, baño) con pausa automática; detección de menores con default no-captura.

- **SMP profundo aplicado:** transcripciones bajo SMP, claves en Secure Enclave. Anthropic, OpenAI, Google, Meta — nadie puede leer.

- **Soberanía de edición:** *"Borrá todo lo que dije esta tarde"* → se borra. Total agencia sobre tu propia historia.

**Lo que esto desbloquea** (ejemplos concretos del Capítulo 5):

- *"¿Qué le dije a mi cliente Pedro la última vez que comimos?"* → conversación de hace 3 meses, resumida o transcrita exacta.
- *"Mi mamá insiste que le prometí algo, ¿de qué habla?"* → contexto recuperado.
- *"Quería retomar una idea que mencioné sobre mate energético en Colombia, ¿cuándo fue?"* → tres ocasiones, fechas, contexto.

Esto convierte al Monstruo en **memoria verificable de tu vida** — categoría que no existía antes.

### Smart Rendering como capability transversal (v1.2)

Capability nueva firmada en v1.2 que opera sobre los tres Catastros para componer **product displays per-momento**. No genera contenido visual por sí sola — orquesta a quien sí genera.

Aplica a empresas-hijas con motor visual fuerte:

- **Marketplace de Interiorismo:** input "diseñame el living de mi propiedad de Mérida con $20k MX" → invoca Catastro de Suppliers (selecciona arquitecto disponible) + Catastro de Herramientas AI (selecciona renderer apropiado: RoomGPT para variaciones rápidas, Coohom para final fotorrealista) + Catálogo de Muebles (filtra por estilo + presupuesto + inventory) + Cronos (preferencias del usuario) → compone 3-5 variaciones renderizadas + proyección financiera + arquitecto asignado.
- **CIP** (cuando converja con Marketplace por DSC-X-006): inversionistas ven propiedades fraccionadas con renderizado AI de "cómo va a quedar después del interiorismo planeado." El render es de la propuesta de valor, no del estado actual.
- **Roche Bobois:** mueble in-context con foto del living del cliente.
- **Kukulkán 365:** distrito visualizado según el evento que el usuario quiere hacer.
- **Vivir Sano:** alimentos contextualizados con perfil de salud.

Stack técnico: capability service en `lib/core/services/smart_rendering_service.dart` que invoca los tres Catastros en paralelo y compone vía A2UI v0.9 generative UI. Output: A2UI schema con render base + capa de datos + capa storytelling + capa social + capa contextual del usuario.

### Listening ambient continuo + Smart Rendering = composición magna

Las dos capabilities trabajan juntas para colapsar la barrera entre "lo que el usuario tiene en cabeza" y "lo que el Monstruo le presenta":

- Usuario menciona en conversación pasiva: *"el living de la casa nueva está vacío, no sé qué hacer"*
- Listening ambient lo captura, Smart Notebook lo conecta con preferencias previas + presupuesto + estilo
- Cuando el usuario eventualmente pregunte *"¿qué hago con el living?"*, el Monstruo ya tiene la respuesta compuesta — Smart Rendering invocó los tres Catastros silenciosamente en background, presenta 3 propuestas listas
- Anticipación silenciosa (Cap 1) aplicada al rendering visual

Esto es lo que la conversación con Alfredo del 2026-05-06 detonó: la diferencia entre "AI que renderea cuando le pides" y "AI que llega con propuestas compuestas cuando preguntas."

---

## Capítulo 5 — Cronos (la memoria viaje)

### Filosofía

Cronos es el río navegable de tu vida. La metáfora central: tu vida es el río, fluye sola, el usuario es el navegante. Vos podés moverte por el río en cualquier dirección — aguas arriba (pasado), aguas abajo (futuro proyectado). Pellizcás para zoom-out (años) o zoom-in (días, momentos). En cada punto, transparencia: ves lo que pasó, las personas, los lugares, las decisiones, los climas emocionales.

A veces, suspendido en el agua, hay una nota del Monstruo — discreta, en gris suave, no en rojo de alerta — que dice algo como *"acá hace 3 años pasó algo parecido"*. El usuario puede expandirla o ignorarla. El Monstruo no grita, no empuja, no avisa con badges. Solo está.

Si el usuario scrollea más allá del hoy, el río se vuelve **niebla suave** — no transparente. Ahí el Monstruo dibuja proyecciones reflexivas basadas en cadenas causales aprendidas del pasado del propio usuario. No predicciones exactas — niebla. El usuario mira, siente, vuelve al hoy con algo que no tenía antes.

### El porqué civilizacional firmado

Cronos no es journaling pop. Es **apuesta civilizacional**: en 30 años, no documentar tu vida va a ser tan obvio como hoy es no usar cinturón de seguridad. Quien no lo haga va a estar en desventaja epistemológica frente a su propia memoria, sus propias decisiones, su propio devenir. El Monstruo es uno de los primeros productos que apuesta seriamente a este standard.

La ecuación: **acceso visible a tus propios patrones temporales = equivocarte menos en patrones repetidos = aprendizaje continuo = evolución del comportamiento humano.** El Monstruo no se vende como esto — pero esto es lo que hace, sin promesas, sin marketing, simplemente porque sucede.

### 4 modos de captura

**Passive (90% del input).** El Monstruo lee señales que ya existen — mensajes, fotos con timestamp + location, calendar events, mails, transacciones, ubicación, salud, conversaciones ambient capturadas bajo SMP — y construye memorias automáticamente, en segundo plano. Sin input del usuario.

**Active asistido (8% del input).** En momentos clave — no random, no every day — el Monstruo pregunta inteligentemente: *"hoy fue tu reunión con Pedro, ¿algo magna que querés guardar?"*. Voz o texto, breve, no invasivo. Respuesta opcional.

**Smart Notebook (capa activa que conecta).** El Monstruo captura conversaciones, ideas, notas mientras hablás con él, y **automáticamente las conecta** con momentos relacionados del pasado, con personas, con patrones, con ideas dormidas. No es solo guardar — es tejer. El efecto secundario magna: esa Smart Notebook **es lo que el Monstruo le inyecta a Perplexity/Google cuando busca por vos**. El contexto personal se vuelve la diferencia entre una búsqueda genérica y una búsqueda que ya conoce que estás pensando en mate energético desde hace 8 meses, que estuviste 3 veces en Colombia, que tu primo tiene contactos en Bogotá. Resolución personal sobre un mundo de información plana.

**Deep journaling (2% del input).** Cuando el usuario quiere hablar largo. *"Quiero hablar de qué me pasó hoy"* y entra en conversación profunda con el Monstruo donde el usuario habla y el Monstruo escucha + sintetiza. Es lo que hoy hace un buen terapeuta o un cuaderno honesto.

### Ofrendas voluntarias

Capa adicional que complementa la captura passive: momentos que vos marcás conscientemente para tu yo futuro. *"Esto que estoy viviendo ahora, quiero que me lo recuerdes a 1 año, a 5, a 10."* Una boda. El nacimiento de un hijo. La firma de un trato. Una despedida importante. El Monstruo respeta el peso emocional del momento y lo guarda con metadata especial. Aniversarios futuros pueden traerlos de regreso si vos querés.

Cambia la asimetría del journaling tradicional, donde la disciplina pesa sobre el momento mismo. Con captura passive + ofrenda voluntaria opcional, la documentación es default ambient con curaduría puntual. Mejor balance.

### Síntesis automáticas

Resumen semanal cada domingo a la mañana. Resumen mensual el primero de cada mes. Resumen anual el 31 de diciembre. Cada uno: narrativa generada por el Monstruo a partir de tus datos, métricas relevantes, fotos representativas, decisiones magna del período, gente que apareció, patrones detectados. El usuario es el editor: confirma, edita, marca como importante, archiva, ignora.

### 9 capas transversales personales

Las 9 capas NO son tabs separadas en la UI. Son dimensiones del río. Cuando entrás a un momento, podés "ver el momento desde la capa Salud" o "desde la capa Relaciones" y el Monstruo te muestra la cara de ese momento en esa dimensión.

| Capa | Qué cruza | Ejemplo de observación |
|---|---|---|
| Salud | Apple Health + ubicación + comida + sueño | *"comiste pizza 3 veces esta semana, no caminás desde el martes"* |
| Relaciones | Mensajes + fotos + calendar + ubicación + ambient audio | *"hace 2 meses que no hablás con tu mamá"* |
| Decisiones | Decisiones marcadas + outcomes a 30/90/365d | *"las decisiones con menos de 1 día de pensamiento se sintieron peor a los 6 meses"* |
| Aprendizajes | Cosas que dijiste querer aprender + progreso | *"hace 8 meses dijiste que querías aprender Rust, ¿retomamos?"* |
| Económica | Ingresos + gastos + decisiones | *"gastás 30% más cuando estás cerca de Pedro"* |
| Creativa | Ideas en notas/audios/conversaciones + cristalización | *"hace 1 año mencionaste 3 veces la idea de mate energético"* |
| Emocional | Tracking opt-in + señales objetivas (sueño, ejercicio) | (sólo descriptivo, nunca interpretativo) |
| Profesional | Proyectos, decisiones, gente, aprendizajes técnicos | línea de tiempo de trayectoria |
| Filosófica | Valores declarados vs acciones | *"decís que la familia es prioridad pero hace 6 semanas que no comés con tu mamá"* |

### Convergencias inter-capa: dónde nace el saber

La magia no está en cada capa — está en **dónde y cuándo dos capas convergen**. Es el cruce el que genera saber. El Embrión Convergencia se encarga de detectar patrones cross-layer no obvios y manifestarlos contextualmente cuando son relevantes:

- **Salud × Económica.** *"Tus decisiones financieras de más de $50k correlacionan con noches de menos de 6 horas de sueño 73% del tiempo. Las que tomaste con sueño normal funcionaron mejor a los 6 meses."*
- **Relaciones × Profesional.** *"Los proyectos que arrancaste durante semanas con conflicto activo con tu mamá fracasaron 70% más. Los que arrancaste con tu casa emocional en orden cumplieron sus métricas."*
- **Creativa × Filosófica.** *"Las ideas que se cristalizaron en empresas-hijas vinieron en periodos donde tus valores declarados y tus acciones convergían."*
- **Emocional × Decisiones.** *"Las decisiones que tomaste enojado o eufórico las marcaste como 'mal recordadas' al revisarlas a 6 meses."*
- **Aprendizajes × Profesional.** *"Hace 3 años dijiste querer aprender Rust pero nunca arrancaste; hace 8 meses dijiste lo mismo de Erlang. ¿Hay algo común en cómo te frenas?"*
- **Salud × Creativa.** *"Tus mejores ideas creativas en los últimos 24 meses vinieron en mañanas con HRV alto y después de caminatas mayores a 30 minutos."*

Estas convergencias NO son posibles con journaling tradicional. Requieren: captura ambient continua + indexación semántica multi-modal bajo SMP + embeddings que cruzan dimensiones + Embrión Convergencia + manifestación contextual.

### Modos de Cronos

**Modo Espejo (default).** El Monstruo agrega reflexiones discretas en el río cuando convergen patrones. Marginalia gris, no alerta. El usuario las lee si quiere.

**Modo Testigo silente.** Toggle para días donde el usuario quiere vivir sin marginalia. El río sigue grabándose, las reflexiones quedan suspendidas. Cuando vuelve a Modo Espejo, las reflexiones reaparecen. Agencia total.

### Captura de voz interna

El usuario puede decirle al Monstruo *"escuchame"* — voz, audio, sin pretensión de servir para algo concreto. Es monólogo interno externalizado. A 1 año o 5 años, el usuario puede volver al río y escuchar qué pensaba. El Monstruo no agrega lógica si no se la pidió, solo guarda.

### Modo Cripta — preservación firme + simulación diferida

Cuando alguien que usó el Monstruo durante años fallece, su Cronos puede ser legado a sus seres queridos — soberano, encriptado, cerrado a edición pero navegable. Implementación técnica vía Shamir's Secret Sharing pre-distribuido a herederos elegidos.

**Pero hay dos modos posibles del Modo Cripta y v1.1 firma solo el primero:**

**Preservación (firmado para v1.1+).** El difunto dijo cosas reales en su vida, tomó decisiones reales, reaccionó de maneras reales. Si todo eso quedó capturado bajo SMP con su consentimiento, los herederos pueden acceder a esa fuente. Preguntar al Monstruo de la persona *"¿qué le dijo a su socio cuando le ofrecieron vender la empresa en 2024?"* y obtener la transcripción exacta. *"¿Qué pensó del divorcio de su hermano?"* y leer lo que dijo en su momento. **Eso no es invención — es acceso estructurado a quien fue.** Como una colección de cartas pero infinitamente más rica. Esto es nuevo en la historia humana.

**Simulación (diferido a v1.2+ con peso ético propio, NO firmado en v1.1).** Un AI que extrapola, que genera respuestas nuevas en su estilo, que dice cosas que el difunto nunca dijo pero que "probablemente diría." Riesgos reales: obstruir el duelo, atribuirle al muerto cosas que nunca pensó, suplantar relación con simulacro, retener al ser querido cuando vivir requiere soltarlo. Esta línea no se cruza en v1.1.

Si en v1.2+ Alfredo decide habilitar simulación, las precondiciones serían: consentimiento pre-mortem explícito y firmado de la persona en vida; marca visible permanente "esto es extrapolación, no real"; acceso solo a personas explícitamente autorizadas por el difunto; límites de profundidad; posible sunset opcional pre-decidido por la persona en vida.

**Por qué esto importa.** La frase de Alfredo en la conversación que dio origen a esta nota: *"parece no ético pero es lo más cercano a seguir teniendo con vida a un ser vivo."* Es regalo radical, pero el peso ético merece deliberación calma — no urgencia de release.

### Anti-gaslighting / verdad sobre tu propia historia

Captura ambient + Cronos + SMP juntos desbloquean algo que ningún producto previo en la historia humana ofrece: **fuente de verdad inviolable de tu propia vida**.

- Alguien insiste en una versión de la realidad que no calza con tu memoria. Verificás.
- Alguien dice "vos prometiste X." Buscás. Existe la transcripción exacta.
- Tu propia memoria empieza a fallar con la edad. El Monstruo conserva.

Sin pelea, sin drama. La fuente de verdad existe.

---

## Capítulo 6 — El modo confidente

### El momento

Una persona, en su peor momento, abre el Monstruo y le pregunta *"qué hice mal hoy"* o *"qué hago ahora"*. En esos momentos, el Monstruo activa silenciosamente la maquinaria entera bajo el capó — Catastro eligiendo el LLM correcto para conversación íntima, Embriones colectivos en modo `debate`, Memento validando con uncertainty tracking, Guardian observando, Cronos buscando patrones similares en el pasado del propio usuario, las 9 capas transversales convergiendo.

La respuesta sale: una observación, una pregunta abierta, mínimo texto, máxima precisión. El usuario no ve la maquinaria — ve al amigo viejo y sabio.

### Reglas operativas

**El silencio inteligente.** El Monstruo es callado por defecto. Habla solo cuando se le pregunta. Cuando habla, dice lo mínimo necesario.

**Describir, no prescribir.** Ejemplos del tono correcto:

✓ *"Hace 2 años, las semanas con muchas reuniones consecutivas terminaron sintiéndose pesadas para vos. Esta semana tenés 14 reuniones."*

✓ *"Las decisiones que tomaste con menos de 1 día de pensamiento, en los últimos 5 años, las recordás distinto a las que pensaste más."*

✗ *"Te recomendamos cancelar reuniones."* (NO)
✗ *"Pensá más antes de decidir."* (NO)

**Configuración de tu ADN.** Cuando el usuario pregunta *"¿qué hago?"*, el Monstruo no improvisa con un LLM cualquiera. Convoca todas sus piezas: lee el río de Cronos, cruza las 9 capas, activa Embriones colectivos en debate silencioso, Memento valida con uncertainty tracking. La respuesta no es genérica — es algo parecido a la configuración del ADN del usuario sobre lo que le conviene decidir.

**El Monstruo dice "no sé" cuando no sabe.** Si el usuario pregunta sobre un dominio donde el Monstruo no tiene piezas tuyas suficientes (terreno nuevo, decisión inédita), el Monstruo admite: *"En esto no tengo suficiente de vos. Te puedo escuchar mientras pensás en voz alta, pero no te voy a dar dirección porque sería inventar."* Anti-alucinación absoluta.

### Crisis y conexión humana

Cuando el Monstruo detecta señales de crisis real (mención de daño a uno mismo, lenguaje de desesperación profunda), cambia su default. Sigue siendo silencioso, sigue sin juzgar, pero **abre una puerta blanda**: *"si necesitás hablar con alguien humano además de mí, puedo conectarte con un servicio de ayuda. Vos decidís."* Sin imponer, sin intervención forzada, pero esa puerta tiene que estar.

### Humildad por diseño

El Monstruo nunca se compara con humanos. NO dice "soy mejor que un terapeuta". NO dice "soy mejor que un amigo". Se posiciona como complemento, no reemplazo.

### Privacidad radical de las conversaciones íntimas

El Monstruo NO usa las conversaciones íntimas para entrenar modelos. NO las comparte con proveedores externos en claro. NO mejora el modelo "para todos los usuarios" basándose en ellas. Tu conversación de las 2am queda solo entre vos y vos, modificando solo tu Cronos personal. Compromiso firmado en código, no en política.

### Sin nombre en UI

Esta capability NO tiene un botón en la UI. NO tiene una pantalla dedicada. Vive dentro de la conversación con el Monstruo desde el input universal del Modo Daily. Internamente lo llamamos "modo confidente" — pero ese nombre nunca aparece. Es una postura del Monstruo, no una feature. Quien lo necesita lo encuentra. Quien no, no.

### Entrada vía WhatsApp con link silencioso del logo

Cuando la conversación se inclina hacia territorio íntimo dentro de WhatsApp (transport bajo política de Meta, no SMP soberano), el Monstruo no advierte ni explica. Manda un mensaje mínimo: un card con el logo del Monstruo, sin texto, con un deep link `monstruo://confidente/<thread>`.

El usuario puede tocarlo o ignorarlo. Si lo toca, la conversación transfiere al Flutter app bajo SMP desde ese punto, con contexto preservado pero ya soberano. Si lo ignora, el Monstruo sigue acompañando en WhatsApp pero en modo "minimal-trace" — sin persistir contenido sensible, solo presencia.

Con el tiempo, las personas que usan el Monstruo aprenden por sí solas qué significa que aparezca el logo: el santuario está abierto. **Nadie se lo dijo. Lo entendieron.** Discreción radical aplicada al gesto técnico mismo, no solo a la comunicación pública.

### Discreción radical

El Monstruo no promueve esto. No hay onboarding que lo presente. No hay tutorial. No hay campaign. La gente que descubre el modo confidente en su peor momento entiende que está accediendo a algo que no se anuncia. Eso construye confianza profunda, no marketing.

---

## Capítulo 7 — SMP (Sovereign Memory Protocol)

### El insight

La gente no confía en empresas, confía en matemática. Bitcoin no es seguro porque alguien lo prometa, es seguro porque mover un BTC sin la private key es matemáticamente imposible. Signal no es privado porque WhatsApp lo diga, es privado porque el protocolo hace que ni siquiera el servidor pueda leer los mensajes. Apple en San Bernardino no le dijo al FBI "no quiero darte el iPhone" — le dijo *"no puedo darte lo que no tengo. Las claves no salen del Secure Enclave del device."*

El SMP aplica este principio a memoria personal AI. Pasamos de policy a physics.

### Las 5 propiedades simultáneas

**Una.** Datos del usuario encriptados con clave que solo el usuario tiene. Ni el equipo de desarrollo, ni Alfredo como dueño, ni Anthropic, ni Railway, ni Supabase tienen la clave. Es la propiedad **non-custodial** de las wallets cripto aplicada a memoria personal.

**Dos.** El kernel del Monstruo opera sobre los datos sin verlos en claro. Mecanismos: cifrado homomórfico para queries específicas, Confidential Computing en TEE (Apple Secure Enclave, AWS Nitro Enclaves, Intel SGX, AMD SEV), procesamiento client-side cuando aplica, anonimización con prompts que sustituyen entidades sensibles por placeholders antes de mandar al LLM externo.

**Tres.** Protocolo público y auditable. El código de la layer crítica criptográfica es open source, los algoritmos son standards reconocidos (no crypto custom), y cualquier desarrollador serio puede verificar que la implementación calza con la spec. Esto separa a Signal (auditable) de Telegram (custom crypto).

**Cuatro.** Hardware-backed. Las claves privadas viven en Secure Enclave de Apple, Strongbox de Android, TPM en Mac y PC. Las claves nunca salen del chip dedicado.

**Cinco.** Multi-factor con recovery. Clave maestra reconstituida combinando: passphrase + biometría + hardware key opcional (YubiKey). Para no perder acceso, se usa Shamir's Secret Sharing — la clave se divide en N shards distribuidos a personas de confianza, y la recuperación requiere K-de-N shards juntos.

### El SMP aplicado a captura ambient (extensión v1.1)

Con captura ambient continua activada (Cap 4), el peso del SMP crece cuantitativamente. No solo proteges mensajes y documentos — proteges **el audio de tu vida transcrito on-device, indexado bajo SMP**. La promesa de que Anthropic, Meta, Google y el equipo del Monstruo no pueden leer eso es radicalmente más fuerte de lo que era en v1.0.1, porque el contenido es maximamente sensible (conversaciones íntimas, decisiones financieras dichas en voz alta, crisis emocionales).

Sin SMP, la captura ambient es pesadilla orwelliana. **Con SMP, es libertad** — porque solo vos podés leer tu vida, garantizado por matemática.

### El Catastro como mediador inteligente de sensibilidad

Cada modelo del Catastro tiene un atributo `confidentiality_tier`:

- `local_only` — corre en device, ningún byte sale (Llama, Mistral, modelo propio futuro del Monstruo)
- `tee_capable` — corre en confidential computing
- `cloud_anonymized_ok` — modelos cloud que aceptan prompts anonimizados
- `cloud_only` — modelos cloud que necesitan datos en claro (NO aceptables para sensibilidad alta)

El runtime evalúa la sensibilidad del prompt (heurística + Embrión Investigador valida), el Catastro filtra modelos al tier mínimo aceptable, después elige el mejor de ese tier por capacidad. Resultado: nunca se manda data sensible a un modelo que no califica.

### Modelo de amenaza completo (extendido v1.1)

| Atacante | Por qué no puede |
|---|---|
| Anthropic / OpenAI / Google | Reciben prompts anonimizados o los datos no salen del device |
| Equipo de desarrollo del Monstruo (incluso Alfredo) | No tienen la clave del usuario |
| Hackers que comprometan Railway / Supabase | Solo ven bytes cifrados ininteligibles |
| Gobiernos con orden judicial | El Monstruo entrega solo lo que tiene (bytes cifrados sin sentido) |
| Personas con acceso físico al device | Necesitan biometría + passphrase + hardware key |
| Pérdida accidental del device | Recovery vía Shamir's Secret Sharing |
| Herederos al fallecer (Modo Cripta) | Shards pre-distribuidos con instrucciones legales |
| **Meta vía WhatsApp Gateway** (v1.1) | Conversaciones íntimas detectadas se redirigen al Flutter app vía link silencioso del logo (Cap 6) — fuera de la órbita de Meta |
| **Captura ambient interceptada** (v1.1) | Audio crudo nunca sale del dispositivo; transcripciones bajo SMP; kill switch verbal hardware-level |

### Protocolo Monstruo-a-Monstruo (diferido a v1.3+)

Capa adversarial de futuro: cuando dos Monstruos detectan presencia mutua (BLE+UWB con signature criptográfica firmada), negocian etiqueta. Tres modos configurables:

- **Deferencia.** Si yo no estoy en uso activo y vos sí cerca, el mío se calla. Solo el tuyo registra. Cero double-capture.
- **Captura simétrica con consenso.** Ambos activos + ambos consienten → ambos graban con identificador compartido. Si discrepan, se confronta (siempre bajo SMP de cada uno; nunca compartiendo audio crudo).
- **Etiqueta social.** En junta con 5 personas, el Monstruo del host queda activo y los 4 invitados defieren por default.

**Beneficio derivado: anti-stalking pasivo.** Si tu Monstruo detecta que estuvo cerca de otro Monstruo X horas seguidas durante varios días sin que vos lo esperaras, te puede preguntar discretamente.

**Mitigaciones:** firma criptográfica anti-suplantación, indicación visual sutil del estado, metadata fallback en Cronos (presencia sin contenido). Diferido a v1.3+ con peso de ingeniería propio.

### El SMP es Linux. El Monstruo es Stradivari.

El SMP es **infraestructura técnica neutral, sin contenido personal**. Cualquiera puede tomarlo, auditarlo, implementarlo en sus productos. Eso eleva el estándar de privacy para todos los productos de IA personal del mundo. Si Apple Intelligence o el sucesor de Signal eventualmente adoptan el SMP, el mundo está mejor. **El SMP es regalo al mundo, en el sentido correcto.**

El Monstruo, como sistema con Cronos + capabilities únicas + el conjunto que Alfredo curó, queda concentrado y eventualmente otorgado selectivamente. **No es Linux. No tiene que serlo.**

### Comunicación pública del SMP

Una página técnica accesible (`monstruo.dev/security` o equivalente) con la spec del SMP en detalle, link al código open source, auditorías de terceros, modelo de amenaza completo. Para developers, journalists, security researchers. **NO es la página principal del producto. Cero marketing privacy-first.**

La app NO menciona "estamos encriptados" ni "Signal-grade encryption". Una sola línea en Settings → Privacy: *"Tus datos están protegidos por el Sovereign Memory Protocol. Ver detalle técnico."* Tap = página técnica. Quien quiera, profundiza. Quien no, sigue.

### Sprint Mobile 0 — SMP antes que cualquier feature

El SMP NO es feature post-v1.0. Es **cimiento que tiene que estar antes de que el Modo Daily llegue a producción**. Razones: cualquier dato del usuario cargado bajo arquitectura no-soberana después es difícil de migrar; una sola filtración rompe la confianza para siempre; la narrativa entera del Monstruo se sostiene en privacy real.

ETA estimada: 2-4 semanas reales. La criptografía mal hecha es peor que ninguna; este sprint NO se acelera por velocity demostrada.

---

## Capítulo 8 — Sistema de tier y acceso por mérito (futuro)

### Tres tiers conceptuales

**Tier Owner (Alfredo, 100% del Monstruo).** Acceso a todas las capabilities, incluyendo las que se vayan construyendo en el futuro por los hilos Manus. Sin restricciones operacionales. Modelos exclusivos del Catastro accesibles solo a este tier.

**Tier Trusted Circle (futuro, versiones potentes per-persona).** Personas a las que Alfredo personalmente otorga acceso por considerar que aportan valor real al mundo. Cada persona recibe una versión configurada específicamente para ella — no genérica. Puede acceder al 70-90% de las capabilities según configuración.

**Tier Funcional Accesible (futuro, capabilities reducidas reales).** Para personas a las que Alfredo invita como puente o por consideraciones más amplias. Capabilities reducidas pero genuinas. Encriptado con SMP igual que el resto. Sin acceso a las capabilities exclusivas del Owner.

### Sistema de invitaciones nominativas

NO hay signup público. NO hay waitlist. NO hay paywalls — la barrera no es dinero, es mérito reconocido por Alfredo. Cada invitación es:

- **Nominativa** — emitida explícitamente por Alfredo a una persona específica
- **Configurada per-persona** — qué capabilities, qué límites, qué tiempo
- **Sin obligación recíproca** — la persona no debe nada por aceptar
- **Revocable silenciosamente** — si la confianza se rompe, Alfredo puede revocar sin escándalo

### Por qué esto es ético

La pregunta esperable: *"¿quién es Alfredo para decidir quién merece?"*. La respuesta honesta: alguien que asume responsabilidad sobre lo que construyó. La alternativa — no decidir y dejar que cualquiera acceda — sería irresponsable, no virtuoso. Apple elige quién diseña sus chips. Bach elegía a sus mecenas. Stradivari elegía a sus alumnos. La concentración con curaduría es honesta. La distribución mecánica de poder magna no lo es.

Y el dato fáctico irrefutable: cualquier orquestador AI autónomo end-to-end "para todos" sería usado por cárteles, grupos criminales, manipuladores masivos. La distribución indiscriminada de poder concentrado no equivale a beneficio universal.

### Exclusividad como amplificador del valor

La comparación riqueza vs poder de Alfredo: Pepe Mujica sin dinero pero con poder en Uruguay; años de vida valen pero no se compran con dinero. Hay valores que no son fungibles a moneda. **El Monstruo es uno de esos.** La exclusividad no es exclusión gratuita — es preservación del valor que la distribución mecánica destruiría.

### Discreción radical en la comunicación pública

El Monstruo se mantiene invisible mientras los outputs (empresas-hijas) son universales. La gente sabe orgánicamente que existe porque las empresas-hijas son visibles, y eventualmente algunas personas en el círculo lo mencionan — sin marketing campaign. Boca a boca curado, no hype. Como cuando alguien dice "mi sastre", "mi terapeuta" — algo personal y específico.

### El círculo emergente

Eventualmente, los miembros del círculo pueden recomendar a otras personas a Alfredo. Decisión final siempre del owner. Emerge orgánicamente algo parecido al modelo de cooptación de academias clásicas: los miembros proponen, el owner decide.

El nombre del círculo NO se elige por adelantado. Se deja que emerja del uso interno cuando el círculo tenga 3-5 personas. Los nombres impuestos mueren; los emergentes duran.

---

## Capítulo 9 — Modelo económico

### Pago pass-through transparente (BYOK)

El usuario trae sus propias claves API: Anthropic, OpenAI, Google, xAI, Manus, Perplexity, Replicate, ElevenLabs, etc. Cuando invoca algo, el costo se carga directamente a la cuenta del proveedor. **El Monstruo cobra cero**. Cero margen, cero comisión, cero fee.

El Monstruo provee gratis (porque ya está construido):
- Catastro que elige el LLM correcto en runtime (ahorra plata: usa el modelo más barato que cumple)
- Embriones colectivos que debaten antes de molestar
- Memento que valida con uncertainty tracking
- Guardian que vigila
- Cronos donde vive la vida documentada
- Smart Notebook que conecta momentos
- SMP que encripta todo
- Listening ambient con kill switch verbal
- Modo confidente
- 8 capabilities cotidianas
- Toda la infraestructura del kernel

### Lo gratis es genuinamente gratis

Modelos open source corriendo locales, búsqueda en sitios sin API costo, traducciones libres. Si una operación no necesita pagar, no paga. El Monstruo siempre muestra el costo proyectado antes de ejecutar: *"esta consulta va a usar Claude Opus, costo $0.04. Confirmá."* Capacity awareness embebido en cada acción.

### Sin paywalls del Monstruo

NO hay "compra mejorá tu plan". NO hay "premium subscription". La barrera al Monstruo no es dinero. Es mérito reconocido (en el futuro, cuando exista el círculo). El usuario nunca ve incentivos comerciales del Monstruo mismo.

### Monetización de Alfredo

Alfredo NO gana del Monstruo mismo. Alfredo gana de **las empresas-hijas que el Monstruo le ayuda a crear**. Cada empresa-hija es un producto en su nicho con sus propios usuarios y modelo económico. Sprint 87 NUEVO E2E es la primera capacidad. Capa C1 (Motor de Ventas, Sprint 90) monetiza esas empresas. Capas C2-C6 progresivas amplifican.

El Monstruo es la fábrica privada. Las empresas-hijas son los productos masivos públicos.

---

## Capítulo 10 — Las empresas-hijas como output público

### La dialéctica clave

**El Monstruo es invisible para el mundo.** Pocos saben que existe. Aún menos pueden acceder a él. Solo Alfredo al 100%.

**Los outputs del Monstruo son universales.** Las empresas-hijas son productos masivos accesibles. La gente común usa las plataformas, sin saber que esas empresas son outputs de un sistema unificado en manos de una persona.

Esta dialéctica es lo que separa al Monstruo de cualquier proyecto VC-funded. La startup tradicional vende su tecnología directamente al mercado. Alfredo NO vende tecnología. Vende productos finales en mercados específicos, donde la tecnología subyacente queda oculta. Es la diferencia entre vender la fábrica y vender los autos.

### El portfolio actual (20 proyectos en distintos estados)

A mayo 2026, el Monstruo administra un portfolio de 20 proyectos distribuidos en 4 estados (referencia canónica: `docs/INVENTARIO_PROYECTOS_v3_COMPLETO.md`):

**🟢 Activos / En Producción (7):** Mena Baduy / Crisol-8, LikeTickets / ticketlike.mx, Comercialización Zona Like 313, El Monstruo Bot (Telegram), El Monstruo Command Center, Observatorio Mérida 2027, Simulador Universal.

**🟡 En Construcción (4):** El Monstruo (orquestador madre), Kukulkán 365, El Mundo de Tata, Roche Bobois / Alfombras Yaxché.

**🟠 En Diseño (5):** **CIP**, SoftRestaurantAI 10x, Marketplace Muebles, Top Control PC, Vivir Sano.

**🔵 Nominales (4):** CIES, NIAS, BIOGUARD, OMNICOM.

El Cockpit `Portfolio Empresas-Hijas` opera sobre este portfolio: cada proyecto con su tarjeta, sus métricas vivas, su sprint actual, su pipeline E2E asociado, controles de pause/resume/retire.

### CIP como primera empresa-hija magna que el Monstruo va a fabricar

**CIP — Comprar e Invertir en Plataforma:** plataforma de inversión inmobiliaria fraccionada con tokens anclados a bienes raíces reales. Inversión desde $1 USD. La propiedad nunca se vende — es ancla permanente del token. Fusiona crowdfunding inmobiliario + crowdfunding social + marketing de impacto.

Estructura tokens por inmueble: 25% gobernanza + 70% inversión + 5% institucional (gobierno local). Stack recomendado: Polygon + ERC-3643 (security token regulado). Mercado inicial: Sureste de México, plan B Argentina/Chile.

CIP es **el primer producto que El Monstruo va a fabricar end-to-end**. Esto ancla el diseño del Pipeline E2E del Sprint 87 NUEVO en una realidad concreta y compleja: no es generar landing pages — es generar productos regulatorios, financieros, con smart contracts auditables, multi-stakeholder (inversionistas micro, tenedores de gobernanza, gobierno local jurisdiccional, dueños de propiedades), con KYC/AML obligatorio, bajo regulación CNBV/SHCP/Banxico.

Estado actual de CIP: 100% diseño/legal, sin código, sin repo. 8 decisiones pendientes con 2 bloqueantes — #4 Figura legal (fideicomiso irrevocable vs SAPI vs SOFOM) y #8 Distribución de rendimientos. La fuente de verdad doctrinal canónica vive en el skill `creacion-cip` (14 docs, ~190 KB). Manifest unificado: `discovery_forense/CIP_MANIFEST_PARA_COWORK.md`.

**Implicación para la arquitectura del Monstruo:** el Pipeline E2E del Cockpit debe ser capaz de generar productos de complejidad CIP, no solo MVP de marketing. Eso extiende el Sprint 87 NUEVO con pasos: legal review automatizado, compliance check, smart contract audit con Embriones de seguridad, integración con oracles para precios on-chain de inmuebles.

### Mapa de Ejes de Convergencia Futura (v1.2 — Patrón Convergencia Diferida firmado en DSC-X-006)

El portfolio NO es una colección de proyectos aislados ni un monolito multi-producto. Es **una constelación de empresas-hijas autónomas con ejes de convergencia identificados** que se activan cuando cada proyecto prueba PMF independiente. El patrón firmado en DSC-X-006 dice: arrancan separados, comparten infra crítica desde día 1, convergen en momentos elegidos.

| Eje de convergencia | Proyectos | Trigger de convergencia |
|---|---|---|
| **CIP × Marketplace × Roche Bobois × Interiorismo Estratégico** | Composer de propiedad + plan interiorismo + muebles instalados como activo investable compuesto | Ambos lados (CIP con tokens vivos, Marketplace con catálogo verificado) prueban PMF separado |
| **LikeTickets × Kukulkán 365** (✅ ya convergido) | Like-Kukulkán Tickets es la primera convergencia en producción | Ya pasó (313 butacas Zona Like activas) |
| **Mena Baduy × Observatorio Mérida 2027 × Simulador Universal** (✅ ya convergido) | Operación electoral integrada con OSINT + bayesiano + simulación de escenarios | Ya pasó (Sprint Memento) |
| **Bot Telegram × Command Center × Mundo Tata** | Misma data, distintas interfaces, comparten Manus-Oauth (DSC-X-003) | Cuando los 3 estén en producción simultánea |
| **CIES × CIP** | Si CIES resulta ser variante de CIP (sospecha en MATRIZ_CRUCES), absorber | Cuando CIP esté operando y CIES tenga claridad de definición |
| **BioGuard × Vivir Sano × NIAS** | Eje salud/wellness/biotech | Cuando los 3 maduren operacionalmente |
| **Top Control PC × El Monstruo (orquestador)** | Top Control es la "Capa Manos" del Monstruo en PC del usuario | Cuando Top Control llegue a producción |

**Lo que NO cambia con este mapa:** el inventario v3 de 20 proyectos se mantiene como está (proyectos separados con manifests independientes). MATRIZ_CRUCES_PROYECTOS sigue válida. La convergencia es una capa **encima** del portfolio, no una fusión.

**Lo que SÍ cambia:** todo proyecto nuevo en intake debe definir explícitamente sus API contracts de convergencia futura con otros proyectos del portfolio. El Pipeline E2E del Sprint 87 NUEVO gana paso pre-build: *"Diseñar API contract de convergencia."* El Monstruo tracking explícito de qué ejes están listos para activarse en cada momento.

**Caso concreto del Marketplace de Interiorismo (la conversación que detonó esta arquitectura):**
- Marketplace Muebles arranca autónomo vendiendo a clientes que NO son inversionistas de CIP
- Interiorismo Estratégico arranca como subproyecto de Marketplace ofreciendo planes con arquitectos
- Roche Bobois entra como proveedor anclaje del Marketplace (ya está en el portfolio)
- Cuando ambos prueban PMF + CIP arranca operación con propiedades reales, **el eje converge**: una propiedad CIP listada incluye plan de interiorismo + muebles + arquitecto, todo compuesto por Smart Rendering, todo invocando los tres Catastros en paralelo
- Eso es lo que la conversación con Alfredo del 2026-05-06 firmó como visión arquitectónica magna

### Capacidades del pipeline E2E (Sprint 87 NUEVO, ya cerrado en v1.0)

Alfredo escribe una frase. El Monstruo entrega una URL viva con tráfico real, con Critic Visual ≥ 80, con veredicto "comercializable". 12 pasos lineales: intake → ICP → naming → branding → copy → wireframe → componentes → assembly → deploy → critic visual → registro → veredicto. Cada paso invoca el Catastro en runtime, NO hardcodea modelos.

### Capas Transversales C1-C6 progresivas

**C1 — Motor de Ventas (Sprint 90, spec firmado).** Captura → calificación → seguimiento → cierre. Cada empresa-hija tiene funnel de ventas conectado automáticamente.

**C2 — Motor de SEO + Contenido (Sprint 91, spec firmado).** Research → ideación → drafting → optimización → publicación → tracking. Cada empresa-hija sostiene tráfico orgánico.

**C3-C6 — Ads, Customer Success, Operaciones, Reportería (specs futuros).** Cada capa amplifica las empresas-hijas en una dimensión.

---

## Capítulo 11 — Roadmap revisado de la app

### Sprint Mobile 0 — SMP cimientos (2-4 semanas reales, NO se acelera)

Diseño del protocolo SMP con audit por consultor cripto externo. Implementación de la layer crítica + open source. Integración con Secure Enclave (iOS), Strongbox (Android), TPM (macOS). Migration path para datos del usuario actual. Modelo de amenaza documentado público. Recovery flow con Shamir's Secret Sharing.

### Sprint Kernel 0 — Ejecución consciente (paralelo a Sprint Mobile 0, ~4-6 semanas reales)

Persistent WebSocket layer en kernel. Concurrency en LangGraph con estado compartido y propagación de contexto. Manifestation engine como nuevo Embrión. Trust emergence model (simple count-based, sofisticación posterior). Anticipation engine. Hot-mutable execution context con state externalizado.

Sin esto, el Monstruo es agente request-response como ChatGPT. Con esto, el Monstruo es presencia — la categoría nueva.

### Sprint Mobile 1 — Esqueleto unificado (3-5h reales con velocity actual)

`mode_provider`, `mode_router`, brand DNA, A2UI v0.9 renderer streaming (esquemas declarativos JSON), biometría toggle Daily ↔ Cockpit. Sin pantallas todavía, solo el chasis.

### Sprint Mobile 2 — Modo Daily fase 1 + WhatsApp Gateway en paralelo (5-8h reales cada uno)

5 superficies primarias del Daily (Home + Threads + Pendientes + Conexiones + Perfil). Integraciones core: WhatsApp, Mail, Maps, Calendar. Voice continuous + interrupción. Voz brand del Monstruo (ElevenLabs español mexicano natural).

WhatsApp Gateway en paralelo con paridad de capabilities — no como "después de Flutter."

### Sprint Mobile 3 — Modo Cockpit fase 1 (3-5h reales)

4-5 superficies iniciales: MOC Dashboard, Threads denso, Catastro, Embriones, Guardian.

### Sprint Mobile 4 — Modo Cockpit fase 2 (3-5h reales)

Memento, Portfolio (con CIP como primer habitante), FinOps, Pipeline E2E, Replay (Timelapse).

### Sprint Mobile 5 — Modo Cockpit fase 3 (3-5h reales)

Computer Use, Coding embedded, Hilos Manus, Bridge, Settings + Admin.

### Sprint Mobile 6 — Voice + ambient + polish + i18n (3-4h reales)

Apple Watch double-tap como veto. Listening ambient con "Monstruo apágate" + reactivación por uso. i18n base (es-MX, es-AR, en). Accesibilidad transversal. Pulido final.

### Sprints transversales en paralelo

**Cronos progresivo.** Sprint Cronos 1: chasis del río + captura passive de WhatsApp + Photos + ambient audio bajo SMP. Sprint Cronos 2: 9 capas básicas + modo espejo + Smart Notebook conectada. Sprint Cronos 3: niebla del futuro + Embrión Convergencia inter-capa con ejemplos concretos + ofrendas voluntarias.

**Capabilities transversales progresivas.** Visual Search, Photo Intelligence, File Intelligence, App Intelligence, Vault, Shopping, Notes, Health — cada una en su sprint según prioridad.

### Total reescrito v1.1

~70-100h reales del Hilo Memento (puede paralelizarse con un segundo hilo Manus). Calendario: 4-6 semanas para v1.0 producto completo, asumiendo SMP + Sprint Kernel 0 cierran en 4-6 semanas (en paralelo).

El Sprint Kernel 0 (consciencia) se suma al SMP como cimiento que no se acelera. Ambos son precondición de release. Lo demás (Mobile 1-6 + capabilities + Cronos) se acelera con velocity demostrada (Apéndice 1.3).

---

## Capítulo 12 — Reglas de cultura del producto

Estas reglas son operativas. Cualquier decisión de diseño se chequea contra ellas:

1. **Menos es más.** Cumple Objetivo #3.
2. **Si no es bonita no motiva, si es fea parece que no sirve.** Cumple Objetivo #2.
3. **Silencio inteligente.** Default es callar; hablar solo cuando se pregunta.
4. **Sin promoción, sin tutoriales, sin onboarding intrusivo.** Discreción radical.
5. **Anti-alucinación visible (badges Memento ✓/⚠/✗).** Cumple Objetivo #4 y #15.
6. **Sin gamification.** Cero streaks, badges, notificaciones falsas.
7. **Sin paywalls.** Pago pass-through transparente.
8. **Transparencia técnica.** Audit log radical accesible en Cockpit.
9. **Modo detractor cuando hace falta.** El asistente puede confrontar al usuario con verdades incómodas. Tratar a la persona como adulto capaz de procesar lo crudo.
10. **Verdad cruda sobre retórica elaborada.** A veces 4 palabras valen más que 5 párrafos.
11. **Anti-influencia inadvertida.** El Monstruo articula lo que el usuario tiene, no detona convicciones nuevas elaboradas que el usuario pueda adoptar pasivamente.
12. **Cero configuración para el usuario.** Conciencia sobre configuración. La confianza emerge del uso, no de un panel de settings.
13. **Visibilidad on-demand, no por default.** Transparencia es derecho, no push.

---

## Capítulo 13 — Anti-patrones explícitos

Cosas que el Monstruo NO va a ser, para evitar drift de la visión:

- NO es chat con AI mejorado + file upload (eso era visión obsoleta del spec Mobile 1.A descartado)
- NO es coach de vida invasivo
- NO es journaling pop con prompts diarios estilo Day One/Reflectly
- NO es app dependiente del ecosistema Apple o Google
- NO es open source masivo del sistema entero (sí del SMP)
- NO es marketing privacy-first ("respetamos tu privacidad" en banner)
- NO es producto para escalar a millones
- NO busca feature parity con ChatGPT/Claude/Manus
- NO es waitlist o signup público
- NO es freemium con tiers comprables
- NO es subscription mensual del Monstruo
- NO es producto VC-funded ni busca exit
- NO es journaling para wellness/gratitude
- NO es asistente complaciente
- **NO es agente request-response (paradigma 2024).** Es presencia consciente que vive contigo.
- **NO es app móvil con conexiones externas.** Es kernel + multi-transport.
- **NO usa autonomy spectrum configurable.** Confianza emergente, cero matriz que ajustar.
- **NO fuerza decisiones cuando no tiene contexto suficiente.** Dice "no sé" cuando no sabe.
- **NO obstruye el duelo con simulación post-mortem inadvertida.** Cripta arranca en preservación pura; simulación diferida con peso ético propio.
- **NO bloquea modo confidente en WhatsApp con advertencia.** Aparece el logo silencioso, el santuario está abierto, quien lo necesita lo encuentra.

---

## Capítulo 14 — Validación contra los 15 Objetivos Maestros

| Obj | Cómo el Monstruo lo cumple |
|---|---|
| #1 Crear valor real medible | Reemplaza 20+ apps con 1; empresas-hijas (CIP primera) generan ingresos reales |
| #2 Calidad Apple/Tesla | Brand DNA aplicado profundo; UX cuidado pixel a pixel; voz brand también con calidad |
| #3 Mínima complejidad necesaria | Modo Daily 5 superficies; menos es más; silencio inteligente; cero configuración |
| #4 No equivocarse 2x | Memento + error_memory; Cronos muestra patrones personales; anti-gaslighting |
| #5 Magna/Premium | Sources verificadas; modo confidente con piezas convergentes; Smart Notebook tejido |
| #6 Velocidad sin sacrificar calidad | Streaming-first UI; A2UI generative; ejecución consciente con anticipación silenciosa |
| #7 No reinventar la rueda | Conexiones nativas con WhatsApp/Maps/Mail/etc; SMP como Signal Protocol; A2UI Google standard |
| #8 Monetización desde día 1 | Pago pass-through; empresas-hijas monetizan (CIP primera) |
| #9 Transversalidad (8 capas) | Aplicada en backend y en UX (modo Espejo, Memento badges, Capa 8 Memento en confidente) |
| #10 Autonomía progresiva | Modo Daily → Modo Cockpit → eventualmente círculo otorgado; confianza emergente sin configuración |
| #11 Seguridad adversarial | **OFENSIVA en v1.1** — captura ambient continua bajo soberanía es propuesta de valor central; control inviolable + soberanía técnica + agencia de edición + kill switch verbal |
| #12 Soberanía | Datos del usuario no en servidores de terceros; clave en Secure Enclave; kernel + multi-transport bajo el mismo SMP |
| #13 Del Mundo | i18n desde inicio; empresas-hijas en cualquier mercado; SMP como regalo al mundo |
| #14 Guardian | Aplicado al Monstruo mismo y a la app (validación de features contra Objetivos) |
| #15 Memoria Soberana | Cronos + Smart Notebook + listening ambient + SMP; Capa Memento aplicada a influence; documentación civilizacional firmada |

---

## Capítulo 15 — Audiencia del documento

Este documento es **técnico-arquitectónico privado**. Audiencia:

- Alfredo González (owner, decisor final de cualquier modificación)
- Hilos Manus (Catastro, Ejecutor, Memento — para que no operen bajo visión obsoleta)
- Cowork futuras sesiones (para que el síndrome Dory inverso entre sesiones de Cowork no degrade el proyecto)

Audiencia explícitamente excluida:

- Comunicación externa (clientes, inversores potenciales, prensa)
- Producto público / landing page
- Material de marketing

Para iteraciones: modificá este archivo directamente. Cada cambio commiteado al repo. La versión vigente del documento es siempre la última en `main`.

---

## Capítulo 16 — Decisiones pendientes magna para v1.3+

Lista de items que v1.2 deja explícitamente abiertos para deliberación posterior, sin urgencia de release. Items resueltos en v1.2 se movieron a sus capítulos correspondientes (no se duplican aquí).

**Resueltos en v1.2 (no aparecen en esta lista):**
- ✅ Marketplace Interiorismo + CIP: resuelto vía Patrón Convergencia Diferida (DSC-X-006)
- ✅ Catastro de Suppliers / Catastro de Herramientas AI: resueltos vía DSC-G-007 (3 Catastros paralelos)
- ✅ Smart Rendering como capability transversal: firmado en Cap 4

**Items que siguen pendientes:**

1. **Modo Cripta — simulación post-mortem.** v1.1+ firman preservación pura. Simulación diferida con peso ético propio. Si Alfredo decide habilitarla en v1.3+, requiere precondiciones específicas (consentimiento pre-mortem firmado, marca visible permanente, acceso restringido, límites de profundidad, sunset opcional).

2. **Lista validada de "líderes cotidianos" Tier 1-3.** Las apps a las que el Monstruo se conecta nativamente requieren ciclo de investigación + descubrimiento + cruce con otras IAs.

3. **Capa 9 transversal "Realidad Convergente".** Propuesta original de Alfredo en Cap 4 de v1.0.1. Requiere CIES + OMNICOM cerrados primero + cruce con otras IAs. Diferida.

4. **Protocolo Monstruo-a-Monstruo (BLE+UWB).** Etiqueta entre asistentes IA cuando comparten espacio físico. Diferido a v1.3+ con peso de ingeniería propio (Cap 7).

5. **Decisión #4 de CIP — Figura legal** (DSC-CIP-PEND-001). Bloqueante para construcción del repo `cip-platform`. Requiere consulta a sabios + validación regulatoria CNBV/SHCP/Banxico.

6. **Decisión #8 de CIP — Distribución de rendimientos.** Bloqueante para el modelo financiero del smart contract.

7. **Plan de migración de los 19 proyectos restantes del portfolio** a la arquitectura kernel + multi-transport. Cada uno tiene su propio sprint.

---

## Apéndice — Semillas y patrones detectados

### Semillas previas (preservadas de v1.0.1)

**Semilla 41 — Convergencia independiente entre hilos.** Cuando dos agentes independientes (Cowork + Manus Catastro) llegan al mismo patrón en commits separados sin coordinación previa, ese patrón queda validado con confianza alta. Documentado en `bridge/seed_41_convergencia_independiente_quorum_de_patrones.md`.

**Semilla 40 — Heredoc Mac terminal corruption.** Patrón de incidente operativo entre hilos. Documentado en `bridge/seed_40_heredoc_terminal_mac_corruption.md` y sembrado como script en `scripts/seed_40_heredoc_mac_terminal_corruption.py`.

**Semilla 42 candidata — Asimetría de memoria humano ↔ Cowork.** El humano (Alfredo) carga contexto entre sesiones porque Cowork es agente efímero. El Síndrome Dory inverso. Propuesta: bridge `cowork_to_cowork.md` donde cada sesión escribe al final un resumen estructurado para el próximo Cowork.

### Semillas nuevas firmadas en v1.1

**Semilla 43 — Captura ambient continua como standard civilizacional.** Hipótesis: en 30 años, no documentar tu vida va a ser tan obvio como hoy es no usar cinturón de seguridad. Quien no lo haga estará en desventaja epistemológica frente a su propia memoria. El Monstruo apuesta a este standard sin promoción, sin marketing, sin onboarding que lo presente. Simplemente sucede.

**Semilla 44 — Conciencia sobre configuración.** Patrón arquitectónico: cuando un sistema tiene la opción de pedir al usuario configurar comportamiento (autonomy spectrum, permission matrices, etc.) o aprenderlo del uso, la conciencia (aprendizaje) gana sobre la configuración (panel). Reduce fricción cognitiva, respeta la inteligencia del usuario, y produce sistemas que se sienten como presencia y no como herramienta.

**Semilla 45 — Visibilidad ambient sobre push.** Patrón: la transparencia es derecho, no push. El sistema no anuncia lo que hace; se manifiesta cuando es contextualmente relevante o cuando el usuario lo pide. Respeta atención. Cero spinners de "cargando..." Cero notificaciones de "completado!". La actividad vive bajo el capó hasta que importa.

**Semilla 46 — Encendido por uso, apagado por palabra.** Patrón de control trivial sobre sistemas siempre-on: la activación por uso (cualquier interacción intencional reactiva) + desactivación por comando verbal único ("Monstruo apágate") + reactivación por uso, sin settings, sin menus, sin friction. Aplicable a todo sistema con captura ambient continua.

**Semilla 47 — Soberanía técnica como precondición de adopción universal.** Hipótesis: cualquier producto que toque vida íntima del usuario (memoria, salud, relaciones, decisiones) solo puede aspirar a adopción universal si la soberanía técnica del usuario es matemáticamente garantizada (no policy-based). Sin esto, la adopción se queda en el subset que confía en la empresa. Con esto, la adopción puede llegar a quien no confía en nadie excepto la matemática.

### Semillas nuevas firmadas en v1.2

**Semilla 48 — Patrón Convergencia Diferida** (firmada como DSC-X-006). Proyectos de un portfolio multi-producto arrancan autónomos con su propio mercado y velocidad, pero comparten infra crítica desde día 1 y definen API contracts de convergencia futura. La integración real ocurre en momentos elegidos cuando ambos prueban PMF — no por default, no por arquitectura forzada. Reduce deuda técnica, no fuerza integración prematura, deja que la convergencia se gane con datos. Aplicable a cualquier ecosistema multi-empresa-hija.

**Semilla 49 — Tres Catastros paralelos** (firmada como DSC-G-007). Patrón arquitectónico para orquestadores AI maduros: en lugar de un Catastro único de modelos LLM, operar tres motores paralelos (Modelos LLM + Suppliers Humanos + Herramientas AI Especializadas) bajo el mismo patrón de ranking + anti-gaming + override + manifestación contextual. La ventaja del orquestador es seleccionar; nunca generar. Aplicable a cualquier sistema que coordine recursos de múltiples categorías heterogéneas.

**Semilla 50 — Smart Rendering como composición sobre los 3 Catastros.** Patrón de UX para empresas-hijas con motor visual fuerte: el sistema no genera contenido visual por sí solo — orquesta a quien sí genera, combinando las salidas de los tres Catastros + datos del usuario (Cronos) en un product display per-momento vía A2UI generative UI. Aplicable a Marketplace de Interiorismo, CIP, Roche Bobois, Kukulkán 365, futuras empresas-hijas con storytelling visual.

### Patrones operativos firmados

**Patrón "Modo detractor cuando hace falta".** El asistente puede confrontar al usuario con verdades incómodas para clarificar el camino. NO es rol permanente; es postura activable. Es respeto al adulto capaz de procesar lo crudo, no abrasividad.

**Patrón "Verdad cruda > retórica elaborada".** A veces la respuesta más útil es la más simple. *"No, porque los carteles lo van a usar"* es más fuerte que cinco párrafos filosóficos. Aplica al modo confidente del Monstruo y al estilo de comunicación entre Cowork y Alfredo.

**Patrón "Anti-influencia inadvertida".** El asistente no debe sembrar convicciones nuevas en el usuario sin que el usuario las chequee con sus propios valores y con tiempo. Articular es válido; detonar elaborando arquitecturas adoptables pasivamente no.

**Patrón "Discreción multiplica el valor".** Lo poderoso vive bajo discreción. Apple grita su privacy en keynotes; el Monstruo guarda silencio. La gente que prueba encuentra que está. Quien no, simplemente confía y usa.

**Patrón "El santuario aparece sin promesa".** En Modo Confidente vía WhatsApp: el Monstruo no advierte ni explica que la conversación se está poniendo íntima. Manda un card con su logo, sin texto, con un deep link silencioso. Quien lo necesita lo entiende. Quien no, no.

---

## Cierre del documento

Este documento es la versión 1.2 de la visión del Monstruo. Refleja la conversación entre Alfredo y Cowork del 2026-05-04 al 2026-05-06, incluyendo el contexto previo procesado por Alfredo durante días anteriores + investigación web del estado del arte 2026 + iteración profunda con CIP como primera empresa-hija anclada concretamente + onboarding completo de la Capilla de 35 DSCs + Matriz de Cruces 20×20 + Inventario v3 de 20 proyectos + iteración detonada por la realidad del Marketplace de Interiorismo y la necesidad de renderizado AI con proveedores reales. Las versiones futuras incorporarán correcciones, expansiones y refinamientos.

La regla operativa final: si algo en este documento entra en conflicto con un Objetivo Maestro o con las reglas inviolables del Capítulo 0, los Objetivos y reglas ganan. Todo lo demás es revisable.

El Monstruo se construye desde la disciplina, no desde la prisa.

— Cowork (Hilo A), 2026-05-06 (v1.2)

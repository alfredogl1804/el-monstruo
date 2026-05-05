# EL MONSTRUO — Arquitectura del Sistema Operativo Personal Soberano

> **Documento de visión v1.0.1**
> **Autor:** Cowork (Hilo B), compilado de iteración con Alfredo González (2026-05-04 → 2026-05-05)
> **Naturaleza:** documento técnico-arquitectónico privado para Alfredo y los hilos Manus. NO destinado a comunicación externa.
> **Estado:** v1.0.1 — parche menor con 3 ajustes confirmados (device confiado agnóstico en Cap 1, Health Intelligence como 8va capability en Cap 4, deuda explícita de investigación de líderes cotidianos en Cap 2). Pendiente para v1.1: Capa 9 transversal "Realidad Convergente" (requiere CIES + OMNICOM + cierre del mapa de líderes con cruce de IAs).

---

## Cómo leer este documento

Este documento condensa la visión de la interfaz del Monstruo y de la postura del proyecto entero, surgida de una conversación de diseño densa entre Alfredo y Cowork a lo largo de varios días. Está estructurado en 15 capítulos más un apéndice. Cada capítulo es denso por intención: no hay retórica de marketing, no hay pitch, no hay aspiracional inflado. Es para uso operativo de quien construye el Monstruo.

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

## Capítulo 1 — Arquitectura general de la app

### Una sola app Flutter, dos modos del mismo cuerpo

El Monstruo es **una sola aplicación Flutter** con dos modos de visualización del mismo cuerpo. No son dos apps separadas. No son dos bundles distintos. No son dos flavors. Es un solo install, un solo state vivo, un solo backend, un solo brand DNA, un solo update.

**Modo Daily** es la cara que muestra solo lo necesario. Cuando un colaborador, familiar o cliente de Alfredo abre el iPhone de él y ve la app, ve esto: una superficie minimalista Apple/Tesla con conexiones nativas a las apps que la gente usa todos los días. Es lo que el Monstruo "presenta" al mundo cuando alguien lo prende.

**Modo Cockpit** es el panel denso de arquitecto. Cuando Alfredo entra como dueño, accede a 12-15 pantallas con todo el poder del Monstruo expuesto: Catastro, Embriones, Guardian, Memento, Replay, Computer Use, FinOps, Pipeline E2E, Hilos Manus, etc. Es Bloomberg + Cursor + Manus, pero hermoso.

Las dos vistas comparten estado. Si Alfredo desde el Modo Daily pregunta "buscame restaurante", y mientras está procesando salta al Modo Cockpit, ve los Embriones debatiendo en vivo, el Catastro eligiendo modelo, el costo subiendo. Vuelve al Modo Daily y la tarjeta del restaurante ya está. Es la misma operación, vista con distinto detalle.

### Toggle entre modos

El acceso al Modo Cockpit requiere autenticación fuerte. Alfredo lo activa con un gesto secreto sobre el logo del Monstruo (3 dedos hold) más Face ID. Opcionalmente, segundo factor con **device confiado agnóstico** como llave próxima — Apple Watch en usuarios Apple, smartwatch Wear OS o Garmin en usuarios Android, o passphrase + biometría sola si no hay smartwatch. La regla operativa es no casarse con un fabricante específico: el Monstruo se diseña para que cualquier device confiado del ecosistema del usuario actúe como segundo factor. Sin estos factores, el Cockpit es invisible — alguien que tome el iPhone de Alfredo no encuentra dónde está, ni sabe que existe.

### Bundle único

```
Bundle ID: com.elmonstruo.app
Plataformas iniciales: iOS, macOS
Plataformas posteriores: iPadOS (responsive desde inicio), Android (post-v1.0), Web (no prioritaria)
```

### Estructura de carpetas Flutter

```
apps/mobile/
├── lib/
│   ├── main.dart                    # ÚNICO entry point
│   ├── core/                        # capabilities completas, SIEMPRE corriendo
│   │   ├── services/
│   │   │   ├── kernel_service.dart
│   │   │   ├── catastro_service.dart
│   │   │   ├── embriones_service.dart
│   │   │   ├── memento_service.dart
│   │   │   ├── connections_service.dart      (WhatsApp/Maps/Mail/etc.)
│   │   │   ├── voice_service.dart
│   │   │   ├── visual_search_service.dart
│   │   │   ├── photo_intelligence_service.dart
│   │   │   ├── file_intelligence_service.dart
│   │   │   ├── app_intelligence_service.dart
│   │   │   ├── vault_service.dart
│   │   │   ├── shopping_service.dart
│   │   │   ├── notes_service.dart
│   │   │   ├── health_service.dart
│   │   │   ├── cronos_service.dart
│   │   │   └── replay_service.dart
│   │   ├── theme/brand_dna.dart              (forja + graphite + acero)
│   │   ├── widgets/
│   │   │   ├── a2ui_components/              (streaming-first)
│   │   │   ├── memento_badge.dart            (✓/⚠/✗ visible en ambos modos)
│   │   │   └── error_toast.dart
│   │   ├── crypto/
│   │   │   ├── smp.dart                      (Sovereign Memory Protocol)
│   │   │   └── secure_enclave_bridge.dart
│   │   └── state/
│   │       └── mode_provider.dart            (daily vs cockpit)
│   ├── modes/
│   │   ├── daily/                            # 5 pantallas
│   │   └── cockpit/                          # 12-15 pantallas
│   └── routing/
│       └── mode_router.dart
└── pubspec.yaml
```

---

## Capítulo 2 — Modo Daily

### Filosofía operativa

Modo Daily NO es "versión lite del Monstruo". Es **la cara que muestra solo lo necesario** mientras todo el poder del sistema corre abajo. Como Finder en Mac OS frente a Terminal: misma máquina, distinto detalle de exposición.

La regla rige cada decisión: cero clutter, cero badges, cero gamification, cero notificaciones falsas, cero "engagement". Si el usuario abre la app y no necesita nada, encuentra silencio sostenido por brand DNA aplicado con cuidado.

### Las 5 pantallas máximas

**Pantalla 1 — Home.** Una pantalla, un input, un canvas. El input es voice-first (push-to-talk) o tap para tipear. Hay también un botón de cámara para visual search inmediato. Output del Monstruo aparece en una tarjeta A2UI minimalista debajo del input. Si la tarjeta requiere acción del usuario, los botones son explícitos y limpios. Si no, la tarjeta queda y el usuario sigue.

Adicionalmente, en el Home vive **el río de Cronos** como franja horizontal navegable bajo el input. Es la presencia silenciosa de la vida documentada, accesible con un swipe lateral pero no obligatoria.

**Pantalla 2 — Threads.** Historial de conversaciones del usuario con el Monstruo, navegable, buscable. No es Slack ni iMessage — es minimalista, una conversación por línea con resumen de 1 frase, fecha relativa, categoría tonal. Tap entra a la conversación entera.

**Pantalla 3 — Pendientes.** Acciones que el Monstruo necesita confirmación humana. Reservas a punto de hacerse, mensajes a punto de mandarse, decisiones HITL soft. Cada item con preview editable inline antes de confirmar (streaming approval). Si no hay nada pendiente, pantalla vacía, sin "no hay nada nuevo" — solo el espacio en blanco con el brand DNA.

**Pantalla 4 — Conexiones.** Qué apps externas tiene enchufadas el Monstruo. WhatsApp, Apple Mail, Gmail, Apple Calendar, Google Calendar, Apple Maps, Google Maps, Apple Photos, Google Photos, Files, Drive, Dropbox, Apple Pay, etc. Toggle individual por servicio. Permissions granulares. Audit log accesible (cuándo el Monstruo leyó qué).

> **DEUDA EXPLÍCITA — investigación pendiente:** la lista de "líderes cotidianos" a los que el Monstruo debe conectarse nativamente (mensajería, email, calendario, sheets, docs, search, visual search, smartwatch/salud, realidad virtual, comercio social, video largo/corto, streaming, música, ecosistema Apple/Google/Microsoft) requiere ciclo de investigación + descubrimiento + cruce con otras IAs (Manus + Perplexity) antes de cerrarse. Lo escrito aquí arriba es esqueleto provisional. La lista validada va a expandirse en v1.1 con criterio por dominio: ¿quién es líder hoy? ¿qué API soporta el Monstruo? ¿qué tier de sensibilidad aplica?

**Pantalla 5 — Perfil.** Identidad del usuario, configuración de privacidad, claves del SMP, recovery con Shamir's Secret Sharing, exportación de datos completos, eliminación con confirmación múltiple. Todo lo soberano vive acá.

### Conexiones nativas — qué realiza el Modo Daily

El usuario habla al Monstruo. El Monstruo opera con sus apps externas en background. El usuario no abre WhatsApp, no abre Maps, no abre Google. El Monstruo lo hace por él. Ejemplos de operaciones que el Modo Daily soporta como flujo natural:

- *"Mandale a Juan que sí confirmo"* → WhatsApp manda, check verde aparece
- *"Donde como mejor sushi cerca"* → tarjeta con 3 lugares, foto, rating sintetizado, distancia, botón [Reservar] [Cómo ir]
- *"Cuándo es la próxima reunión con Pedro"* → Calendar + Mail + WhatsApp consultados, respuesta unificada
- *"Resúmeme los mails sin leer importantes"* → 3 tarjetas con resumen, opción [Responder] [Posponer] [Archivar]
- *"Qué pasó con el peso argentino esta semana"* → tarjeta sintetizada con sources verificadas y badges Memento
- *"Buscame esto"* (con foto desde cámara) → visual search, identificación, dónde se compra, mejor precio
- *"Buscame mi DNI escaneado del mes pasado"* → photo intelligence semantic search
- *"Encontrame el contrato del local"* → file intelligence semantic search en Files + Drive
- *"Apuntar idea: vendiendo mate energético en Colombia"* → notas inteligentes, contextualizadas en Cronos como capa creativa

---

## Capítulo 3 — Modo Cockpit

### Filosofía operativa

El Cockpit es para Alfredo como arquitecto. Densidad alta pero hermosa: Brand DNA forja aplicado profundo, calidad Apple/Tesla aplicada a interfaces complejas. NO es fea-porque-densa. Es densa-porque-poderosa, y bonita-porque-cuidada.

El Cockpit es invisible para todos los usuarios excepto Alfredo (autenticación fuerte). Eventualmente, algunas personas del círculo otorgado pueden tener acceso al Cockpit con configuraciones reducidas — pero por defecto, Cockpit completo es solo para Alfredo.

### Las 12-15 pantallas

**MOC Dashboard.** Mission Operations Center. Todos los sistemas del Monstruo en una vista: sprints corriendo, hilos Manus activos, alertas Guardian, métricas vivas, empresas-hijas operando, cron jobs. Refresh automático. Modo presentación para casteo a TV / proyector cuando hace falta.

**Threads + Comando.** Chat denso con el Monstruo desde rol arquitecto. Multi-thread paralelos. Atajos magna estilo Linear/Superhuman. ⌘K abre command palette. ⌘P salta a empresa-hija por nombre. Filtros sofisticados, búsqueda semántica en historial completo.

**Portfolio Empresas-Hijas.** Tarjetas de las empresas que el Monstruo generó vía Sprint 87 NUEVO E2E. Cada una con métricas vivas (tráfico, leads, ingresos, contenido publicado), zoom-in al pipeline E2E que la generó, capacidad de pausar/reanudar/retirar.

**Catastro.** Vista densa de los 50+ modelos rankeados, filtrable por macroárea (Razonamiento, Arena humana, Coding, Razonamiento Estructurado, Embeddings). Trono Score con z-scores intra-dominio. Anti-gaming flags v1 (intra-fuente UC Berkeley) y v2 (cross-area). Override manual posible: "este pipeline E2E, quiero que use Claude Opus 4.7 sí o sí".

**Embriones.** 9+ Embriones especializados (Critic Visual, Product Architect, Creativo, Estratega, Financiero, Investigador, Técnico, Ventas, Vigía). Cada uno con FCS (Functional Consciousness Score), última invocación, decisiones recientes. Vista del modo `debate` y `quorum` cuando se activan.

**Guardian.** Los 15 Objetivos Maestros como panel de instrumentos. Scores por objetivo (rojo/amarillo/verde). Alertas activas. Recomendaciones accionables. Nivel 1 (alerta) y Nivel 2 (bloqueo) del Corrective Actor visibles. Self-health check del Guardian mismo.

**Memento.** Semillas de error_memory (40+ acumuladas). Validaciones de pre-flight ejecutadas. Detección de contexto contaminado. Stats del Síndrome Dory evitado. Audit del SMP. Configuración de tiers de sensibilidad por tipo de operación.

**Replay.** Selector de runs E2E pasadas + timeline scrubable interactivo (estilo Devin Timelapse). Vos elegís una run, scrolleás el timeline, ves cada decisión paso por paso, podés bifurcar desde cualquier punto. Aplica también a conversaciones del modo confidente con vos mismo.

**Computer Use / Sandbox.** El navegador del agente, la terminal, el filesystem en vivo. Estilo Manus Computer panel pero soberano. Cuando Sprint 87 NUEVO E2E está generando una empresa-hija, vos ves el browser haciendo deploy, los archivos creándose, los API calls saliendo.

**FinOps.** Capacity awareness completa. Tokens consumidos por hilo / por empresa-hija / por sprint. Costo desglosado por proveedor (Anthropic, OpenAI, Google, Manus, Perplexity). ROI por empresa-hija (ingresos vs costos de generación + mantenimiento). Forecast de gasto. Configuración de spending caps con alertas.

**Pipeline E2E.** Visualización del flujo del Sprint 87 NUEVO: 12 pasos lineales (intake → ICP → naming → branding → copy → wireframe → componentes → assembly → deploy → critic visual → registro → veredicto). Estado por step, intervención humana posible en cualquier paso, replay de runs pasadas, abort/retry.

**Coding embedded.** IDE liviano para intervenir código sin salir del Cockpit. Editor + diff viewer + ejecución sandboxed + terminal embebida. Cuando el Catastro o un Embrión sugieren un cambio de código, vos lo aprobás/editás/rechazás inline.

**Hilos Manus.** Vista de los 3+ hilos Manus activos (Catastro, Ejecutor, Memento). Cada uno con su sprint actual, status, próximos pasos, ETA recalibrada según Apéndice 1.2. Bridge accesible. Audit de tasks despachadas.

**Bridge / Comunicación inter-hilos.** Los reportes y audits viviendo en `bridge/` navegables. Decisiones arquitectónicas firmadas, semillas sembradas, specs en redacción, roadmaps. La memoria operativa del proyecto soberano accesible visualmente.

**Settings + Admin.** Variables de entorno Railway, configuración del kernel, override de defaults, gestión de tier-access (cuando exista el círculo otorgado), invitaciones nominativas. Admin de la administración.

### Atajos magna

⌘K command palette universal. ⌘P jump to portfolio empresa. ⌘E jump to Embrión. ⌘G abre Guardian. ⌘T salta a Catastro. ⌘R abre Replay del último run. ⌘shift+M toggle a Modo Daily (con biometría). Todo navegable con teclado.

---

## Capítulo 4 — Capabilities transversales

Las **8 capabilities** siguientes son servicios core que viven en `lib/core/services/` y se invocan desde ambos modos. En Modo Daily son comandos naturales con output limpio; en Modo Cockpit son pantallas densas con metadata visible.

### Visual Search (Google Lens-style soberano)

Apuntás cámara o subís foto. El Monstruo identifica qué es, dónde se compra, mejor precio, traduce texto en la imagen, identifica plantas/animales/edificios. Soberanía aplicada: procesamiento on-device cuando posible (embeddings locales), cloud cuando necesita capacidad mayor pero con anonimización del contenido. La cámara es botón de primera clase en el Home del Modo Daily.

### Photo Intelligence

Búsqueda semántica sobre tus fotos: *"la foto del DNI del mes pasado"*, *"las fotos del cumple de Dani"*, *"esa donde aparezco con un mate cerca del mar"*. Organización inteligente: detectar duplicados, sugerir limpieza de screenshots viejos, generar mini-albums automáticos. Híbrido: la app accede a Apple Photos / Google Photos vía API, pero el ÍNDICE semántico (embeddings de qué hay en cada foto) vive en el kernel del Monstruo encriptado bajo SMP.

### File Intelligence

Mismo patrón aplicado a archivos: *"dónde guardé el contrato del local"*, *"el último PDF que firmé"*, *"limpiame Downloads de cosas viejas"*. Acceso configurable a iCloud Drive, Google Drive, Dropbox, Files local. Indexación semántica bajo SMP. Categorización automática propuesta (facturas, contratos, recibos) con confirmación del usuario.

### App Intelligence

Inteligencia sobre las apps que el usuario usa: *"qué apps no usé en 3 meses"*, *"cuánto gasto en suscripciones"*, automatizaciones cross-app. Limitado por las APIs que iOS/Android exponen (lista de apps instaladas requiere permisos especiales). Donde los OS lo permiten, el Monstruo orquesta; donde no, sugiere acciones manuales.

### Vault Soberano (credenciales y keys)

Passwords, API keys, secrets, certificados, llaves SSH almacenados bajo SMP. Importación de 1Password, Bitwarden, Apple Keychain. Auto-fill vía AutoFill APIs del OS. Watchtower-style: alertas de claves comprometidas, sin 2FA, duplicadas, viejas. Compartir granular con TTL automático ("dale acceso a la clave de Cloudflare a mi empleado durante 1 día"). Integración conversacional: *"rotame todas las claves de mi servidor de Railway esta semana"* — el Monstruo lo hace step by step con confirmación HITL en cada acción.

### Shopping Intelligence

Búsqueda + comparación + checkout asistido. *"Buscame el mejor precio de esta zapatilla"* (con foto). *"Comparame entre Mercado Libre, Amazon, Shein"*. *"Avisame cuando baje de X"*. Integración con Mercado Libre, Amazon, Rappi, marketplaces locales. Memoria histórica de compras: *"ya pedí el mismo producto el mes pasado, ahí pagué Y"*. Compras ejecutadas en HITL streaming: el Monstruo prepara la orden, vos confirmás el preview editable.

### Notes Intelligence (procesamiento de notas inteligente)

Lectura de Apple Notes / Google Keep / Notion con permisos. Procesamiento smart minimalista: extracción de tareas implícitas ("comprar yerba" → propone agregarlo a shopping), conexión con Cronos (la nota *"reunión con Pedro: hablar de X"* se conecta con calendar event y queda contextualizada), búsqueda semántica multi-fuente, detección de ideas dormidas que vale resucitar.

### Health Intelligence (monitoreo soberano de salud como nuevo standard)

Conexión con Apple HealthKit (iOS) y Health Connect (Android) más wearables específicos (Apple Watch, Garmin, Oura, Whoop, Fitbit). Lectura de métricas — sueño, frecuencia cardíaca, HRV, actividad, peso, glucosa si se mide, presión arterial — bajo SMP, con índice semántico viviendo en el kernel del Monstruo cifrado con clave del usuario. Apple/Google ven los bytes; el Monstruo entiende el significado. Soberanía aplicada al cuerpo.

Premisa cultural: monitoreo completo de salud va a ser standard del futuro inmediato, así como hoy nadie maneja sin cinturón de seguridad. Quien no monitoree va a estar en desventaja epistemológica frente a su propia salud. El Monstruo NO empuja a la persona a monitorear; cuando ya hay datos, los integra inteligentemente.

Aplicaciones concretas:
- Cronos Capa Salud alimentada con datos objetivos (no solo declarativos)
- Detección pasiva de patrones (ejemplo: *"las semanas que dormís menos de 6h, tu humor del 3er día baja según tus propios datos"*)
- Anti-coaching: el Monstruo describe lo que ve, no prescribe ejercicio ni dieta
- Crisis discreta: si métricas objetivas indican riesgo serio (arritmia inusual sostenida, caídas detectadas, etc.), puerta blanda hacia humano-profesional, sin imposición
- Privacidad radical: las métricas de salud son sensibilidad ALTA por default, procesamiento on-device o TEE obligatorio (jamás cloud LLM en claro)

---

## Capítulo 5 — Cronos (la memoria viaje)

### Filosofía

Cronos es el río navegable de tu vida. La metáfora central: tu vida es el río, fluye sola, el usuario es el navegante. Vos podés moverte por el río en cualquier dirección — aguas arriba (pasado), aguas abajo (futuro proyectado). Pellizcás para zoom-out (años) o zoom-in (días, momentos). En cada punto, transparencia: ves lo que pasó, las personas, los lugares, las decisiones, los climas emocionales.

A veces, suspendido en el agua, hay una nota del Monstruo — discreta, en gris suave, no en rojo de alerta — que dice algo como *"acá hace 3 años pasó algo parecido"*. El usuario puede expandirla o ignorarla. El Monstruo no grita, no empuja, no avisa con badges. Solo está.

Si el usuario scrollea más allá del hoy, el río se vuelve **niebla suave** — no transparente. Ahí el Monstruo dibuja proyecciones reflexivas basadas en cadenas causales aprendidas del pasado del propio usuario. No predicciones exactas — niebla. El usuario mira, siente, vuelve al hoy con algo que no tenía antes.

### 3 modos de captura

**Passive (90% del input).** El Monstruo lee señales que ya existen — mensajes, fotos con timestamp + location, calendar events, mails, transacciones, ubicación, salud — y construye memorias automáticamente, en segundo plano. Sin input del usuario.

**Active asistido (8% del input).** En momentos clave — no random, no every day — el Monstruo pregunta inteligentemente: *"hoy fue tu reunión con Pedro, ¿algo magna que querés guardar?"*. Voz o texto, breve, no invasivo. Respuesta opcional.

**Deep journaling (2% del input).** Cuando el usuario quiere hablar largo. *"Quiero hablar de qué me pasó hoy"* y entra en conversación profunda con el Monstruo donde el usuario habla y el Monstruo escucha + sintetiza. Es lo que hoy hace un buen terapeuta o un cuaderno honesto.

### Síntesis automáticas

Resumen semanal cada domingo a la mañana. Resumen mensual el primero de cada mes. Resumen anual el 31 de diciembre. Cada uno: narrativa generada por el Monstruo a partir de tus datos, métricas relevantes, fotos representativas, decisiones magna del período, gente que apareció, patrones detectados. El usuario es el editor: confirma, edita, marca como importante, archiva, ignora.

### 9 capas transversales personales

Las 9 capas NO son tabs separadas en la UI. Son dimensiones del río. Cuando entrás a un momento, podés "ver el momento desde la capa Salud" o "desde la capa Relaciones" y el Monstruo te muestra la cara de ese momento en esa dimensión.

| Capa | Qué cruza | Ejemplo de observación |
|---|---|---|
| Salud | Apple Health + ubicación + comida + sueño | *"comiste pizza 3 veces esta semana, no caminás desde el martes"* |
| Relaciones | Mensajes + fotos + calendar + ubicación | *"hace 2 meses que no hablás con tu mamá"* |
| Decisiones | Decisiones marcadas + outcomes a 30/90/365d | *"las decisiones que tomaste con menos de 1 día de pensamiento se sintieron peor a los 6 meses"* |
| Aprendizajes | Cosas que dijiste querer aprender + progreso | *"hace 8 meses dijiste que querías aprender Rust, ¿retomamos?"* |
| Económica | Ingresos + gastos + decisiones | *"gastás 30% más cuando estás cerca de Pedro"* |
| Creativa | Ideas en notas/audios/conversaciones + cristalización | *"hace 1 año mencionaste 3 veces la idea de mate energético"* |
| Emocional | Tracking opt-in + señales objetivas (sueño, ejercicio) | (sólo descriptivo, nunca interpretativo) |
| Profesional | Proyectos, decisiones, gente, aprendizajes técnicos | línea de tiempo de trayectoria |
| Filosófica | Valores declarados vs acciones | *"decís que la familia es prioridad pero hace 6 semanas que no comés con tu mamá"* |

### Modos de Cronos

**Modo Espejo (default).** El Monstruo agrega reflexiones discretas en el río cuando convergen patrones. Marginalia gris, no alerta. El usuario las lee si quiere.

**Modo Testigo silente.** Toggle para días donde el usuario quiere vivir sin marginalia. El río sigue grabándose, las reflexiones quedan suspendidas. Cuando vuelve a Modo Espejo, las reflexiones reaparecen. Agencia total.

### Captura de voz interna

El usuario puede decirle al Monstruo *"escuchame"* — voz, audio, sin pretensión de servir para algo concreto. Es monólogo interno externalizado. A 1 año o 5 años, el usuario puede volver al río y escuchar qué pensaba. El Monstruo no agrega lógica si no se la pidió, solo guarda.

### Modo Cripta (futuro, post-v1.0)

Cuando alguien que usó el Monstruo durante años fallece, su Cronos puede ser legado a sus seres queridos — soberano, encriptado, cerrado a edición pero navegable. Implementación técnica vía Shamir's Secret Sharing pre-distribuido. Es regalo radical: una nueva forma de memorializar adultos en la era de la IA.

---

## Capítulo 6 — El modo confidente

### El momento

Una persona, en su peor momento, abre el Monstruo y le pregunta *"qué hice mal hoy"* o *"qué hago ahora"*. En esos momentos, el Monstruo activa silenciosamente la maquinaria entera bajo el capó — Catastro eligiendo el LLM correcto para conversación íntima, Embriones colectivos en modo `debate`, Memento validando con uncertainty tracking, Guardian observando, Cronos buscando patrones similares en el pasado del propio usuario, las 9 capas transversales convergiendo.

La respuesta sale: una observación, una pregunta abierta, mínimo texto, máxima precisión. El usuario no ve la maquinaria — ve al amigo viejo y sabio.

### Reglas operativas

**El silencio inteligente.** El Monstruo es callado por defecto. Habla solo cuando se le pregunta. Cuando habla, dice lo mínimo necesario. Como Grok lo nombró: el silencio inteligente es más poderoso e impacta más que el ruido constante.

**Describir, no prescribir.** Ejemplos del tono correcto:

✓ *"Hace 2 años, las semanas con muchas reuniones consecutivas terminaron sintiéndose pesadas para vos. Esta semana tenés 14 reuniones."*

✓ *"Las decisiones que tomaste con menos de 1 día de pensamiento, en los últimos 5 años, las recordás distinto a las que pensaste más."*

✗ *"Te recomendamos cancelar reuniones."* (NO)

✗ *"Pensá más antes de decidir."* (NO)

**Configuración de tu ADN.** Cuando el usuario pregunta *"¿qué hago?"*, el Monstruo no improvisa con un LLM cualquiera. Convoca todas sus piezas: lee el río de Cronos, cruza las 9 capas, activa Embriones colectivos en debate silencioso, Memento valida con uncertainty tracking. La respuesta no es genérica — es algo parecido a la configuración del ADN del usuario sobre lo que le conviene decidir.

**El Monstruo dice "no sé" cuando no sabe.** Si el usuario pregunta sobre un dominio donde el Monstruo no tiene piezas tuyas suficientes (terreno nuevo, decisión inédita), el Monstruo admite: *"En esto no tengo suficiente de vos. Te puedo escuchar mientras pensás en voz alta, pero no te voy a dar dirección porque sería inventar."* Anti-alucinación absoluta. Esa es la versión más pura de Memento aplicada a conversación íntima — y paradójicamente lo que vuelve al Monstruo confiable.

### Crisis y conexión humana

Cuando el Monstruo detecta señales de crisis real (mención de daño a uno mismo, lenguaje de desesperación profunda), cambia su default. Sigue siendo silencioso, sigue sin juzgar, pero **abre una puerta blanda**: *"si necesitás hablar con alguien humano además de mí, puedo conectarte con un servicio de ayuda. Vos decidís."* Sin imponer, sin intervención forzada, pero esa puerta tiene que estar.

### Humildad por diseño

El Monstruo nunca se compara con humanos. NO dice "soy mejor que un terapeuta". NO dice "soy mejor que un amigo". Se posiciona como complemento, no reemplazo. *"Te observo a vos basado en lo que tengo de vos. Para algo más profundo, otros humanos pueden ayudarte distinto."*

### Privacidad radical de las conversaciones íntimas

El Monstruo NO usa las conversaciones íntimas para entrenar modelos. NO las comparte con proveedores externos en claro. NO mejora el modelo "para todos los usuarios" basándose en ellas. Tu conversación de las 2am queda solo entre vos y vos, modificando solo tu Cronos personal. Compromiso firmado en código, no en política.

### Sin nombre en UI

Esta capability NO tiene un botón en la UI. NO tiene una pantalla dedicada. Vive dentro de la conversación con el Monstruo desde el input universal del Modo Daily. Internamente lo llamamos "modo confidente" — pero ese nombre nunca aparece. Es una postura del Monstruo, no una feature. Quien lo necesita lo encuentra. Quien no, no.

### Discreción radical

El Monstruo no promueve esto. No hay onboarding que lo presente. No hay tutorial. No hay campaign. La gente que descubre el modo confidente en su peor momento entiende que está accediendo a algo que no se anuncia. Eso construye confianza profunda, no marketing.

---

## Capítulo 7 — SMP (Sovereign Memory Protocol)

### El insight

La gente no confía en empresas, confía en matemática. Bitcoin no es seguro porque alguien lo prometa, es seguro porque mover un BTC sin la private key es matemáticamente imposible. Signal no es privado porque WhatsApp lo diga, es privado porque el protocolo hace que ni siquiera el servidor pueda leer los mensajes. Apple en San Bernardino no le dijo al FBI "no quiero darte el iPhone" — le dijo *"no puedo darte lo que no tengo. Las claves no salen del Secure Enclave del device."*

El SMP aplica este principio a memoria personal AI. Pasamos de policy a physics.

### Las 5 propiedades simultáneas (todas tienen que cumplirse)

**Una.** Datos del usuario encriptados con clave que solo el usuario tiene. Ni el equipo de desarrollo del Monstruo, ni Alfredo como dueño, ni Anthropic, ni Railway, ni Supabase tienen la clave. Es la propiedad **non-custodial** de las wallets cripto aplicada a memoria personal.

**Dos.** El kernel del Monstruo opera sobre los datos sin verlos en claro. Mecanismos: cifrado homomórfico para queries específicas, Confidential Computing en TEE (Apple Secure Enclave, AWS Nitro Enclaves, Intel SGX, AMD SEV), procesamiento client-side cuando aplica, anonimización con prompts que sustituyen entidades sensibles por placeholders antes de mandar al LLM externo.

**Tres.** Protocolo público y auditable. El código de la layer crítica criptográfica es open source, los algoritmos son standards reconocidos (no crypto custom), y cualquier desarrollador serio puede verificar que la implementación calza con la spec. Esto separa a Signal (auditable) de Telegram (custom crypto).

**Cuatro.** Hardware-backed. Las claves privadas viven en Secure Enclave de Apple, Strongbox de Android, TPM en Mac y PC. Las claves nunca salen del chip dedicado.

**Cinco.** Multi-factor con recovery. Clave maestra reconstituida combinando: passphrase + biometría + hardware key opcional (YubiKey). Para no perder acceso, se usa Shamir's Secret Sharing — la clave se divide en N shards distribuidos a personas de confianza, y la recuperación requiere K-de-N shards juntos.

### El Catastro como mediador inteligente de sensibilidad

Cada modelo del Catastro tiene un atributo `confidentiality_tier`:

- `local_only` — corre en device, ningún byte sale (Llama, Mistral, modelo propio futuro del Monstruo)
- `tee_capable` — corre en confidential computing
- `cloud_anonymized_ok` — modelos cloud que aceptan prompts anonimizados
- `cloud_only` — modelos cloud que necesitan datos en claro (NO aceptables para sensibilidad alta)

El runtime evalúa la sensibilidad del prompt (heurística + Embrión Investigador valida), el Catastro filtra modelos al tier mínimo aceptable, después elige el mejor de ese tier por capacidad. Resultado: nunca se manda data sensible a un modelo que no califica.

### Modelo de amenaza completo

| Atacante | Por qué no puede |
|---|---|
| Anthropic / OpenAI / Google | Reciben prompts anonimizados o los datos no salen del device |
| Equipo de desarrollo del Monstruo (incluso Alfredo) | No tienen la clave del usuario |
| Hackers que comprometan Railway / Supabase | Solo ven bytes cifrados ininteligibles |
| Gobiernos con orden judicial | El Monstruo entrega solo lo que tiene (bytes cifrados sin sentido) |
| Personas con acceso físico al device | Necesitan biometría + passphrase + hardware key |
| Pérdida accidental del device | Recovery vía Shamir's Secret Sharing |
| Herederos al fallecer (Modo Cripta) | Shards pre-distribuidos con instrucciones legales |

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
- SMP que encripta todo
- Modo confidente
- 6 capabilities cotidianas
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

**Los outputs del Monstruo son universales.** Las empresas-hijas son productos masivos accesibles. La gente común usa forjamate.com, otra empresa, otra. Pocos saben que esas empresas son outputs de un sistema unificado en manos de una persona.

Esta dialéctica es lo que separa al Monstruo de cualquier proyecto VC-funded. La startup tradicional vende su tecnología directamente al mercado. Alfredo NO vende tecnología. Vende productos finales en mercados específicos, donde la tecnología subyacente queda oculta. Es la diferencia entre vender la fábrica y vender los autos.

### Capacidades del pipeline E2E (Sprint 87 NUEVO, ya cerrado)

Alfredo escribe una frase. El Monstruo entrega una URL viva con tráfico real, con Critic Visual ≥ 80, con veredicto "comercializable". 12 pasos lineales: intake → ICP → naming → branding → copy → wireframe → componentes → assembly → deploy → critic visual → registro → veredicto. Cada paso invoca el Catastro en runtime, NO hardcodea modelos.

### Capas Transversales C1-C6 progresivas

**C1 — Motor de Ventas (Sprint 90, spec firmado).** Captura → calificación → seguimiento → cierre. Cada empresa-hija tiene funnel de ventas conectado automáticamente.

**C2 — Motor de SEO + Contenido (Sprint 91, spec firmado).** Research → ideación → drafting → optimización → publicación → tracking. Cada empresa-hija sostiene tráfico orgánico.

**C3-C6 — Ads, Customer Success, Operaciones, Reportería (specs futuros).** Cada capa amplifica las empresas-hijas en una dimensión.

---

## Capítulo 11 — Roadmap revisado de la app

### Sprint Mobile 0 — SMP cimientos (2-4 semanas reales)

Diseño del protocolo SMP con audit por consultor cripto externo. Implementación de la layer crítica + open source. Integración con Secure Enclave (iOS), Strongbox (Android), TPM (macOS). Migration path para datos del usuario actual. Modelo de amenaza documentado público. Recovery flow con Shamir's Secret Sharing.

### Sprint Mobile 1 — Esqueleto unificado (5-7h reales)

`mode_provider`, `mode_router`, brand DNA, A2UI renderer streaming, biometría toggle Daily ↔ Cockpit. Sin pantallas todavía, solo el chasis.

### Sprint Mobile 2 — Modo Daily fase 1 (8-12h reales)

5 pantallas (Home + Threads + Pendientes + Conexiones + Perfil). Integraciones core: WhatsApp, Mail, Maps, Google Search/Synth, Calendar.

### Sprint Mobile 3 — Modo Cockpit fase 1 (6-9h reales)

4-5 pantallas iniciales: MOC Dashboard, Threads denso, Catastro, Embriones, Guardian.

### Sprint Mobile 4 — Modo Cockpit fase 2 (6-9h reales)

Memento, Portfolio, FinOps, Pipeline E2E, Replay.

### Sprint Mobile 5 — Modo Cockpit fase 3 (6-9h reales)

Computer Use, Coding embedded, Hilos Manus, Bridge, Settings + Admin.

### Sprint Mobile 6 — Voice + polish + i18n (4-6h reales)

Voice bidireccional con interrupción natural. i18n base (es-MX, es-AR, en). Accesibilidad transversal. Pulido final.

### Sprints transversales en paralelo

**Cronos progresivo.** Sprint Cronos 1: chasis del río + captura passive de WhatsApp + Photos. Sprint Cronos 2: 9 capas básicas + modo espejo. Sprint Cronos 3: niebla del futuro + Simulador Causal aplicado.

**Capabilities transversales progresivas.** Visual Search, Photo Intelligence, File Intelligence, App Intelligence, Vault, Shopping, Notes, Health — cada una en su sprint según prioridad. Total: 8 capabilities core.

### Total reescrito

~50-70h reales del Hilo Memento (puede paralelizarse con un segundo hilo Manus). Calendario: 4-6 semanas para v1.0 producto completo, asumiendo SMP cierra en 2-4 semanas.

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

---

## Capítulo 14 — Validación contra los 15 Objetivos Maestros

| Obj | Cómo el Monstruo lo cumple |
|---|---|
| #1 Crear valor real medible | Reemplaza 20 apps con 1; empresas-hijas generan ingresos reales |
| #2 Calidad Apple/Tesla | Brand DNA aplicado profundo; UX cuidado pixel a pixel |
| #3 Mínima complejidad necesaria | Modo Daily 5 pantallas; menos es más; silencio inteligente |
| #4 No equivocarse 2x | Memento + error_memory; Cronos muestra patrones personales |
| #5 Magna/Premium | Sources verificadas; modo confidente con piezas convergentes |
| #6 Velocidad sin sacrificar calidad | Streaming-first UI; Catastro elige LLM rápido cuando aplica |
| #7 No reinventar la rueda | Conexiones nativas con WhatsApp/Maps/Mail/etc; SMP como Signal Protocol |
| #8 Monetización desde día 1 | Pago pass-through; empresas-hijas monetizan |
| #9 Transversalidad (8 capas) | Aplicada en backend y en UX (modo Espejo, Memento badges, Capa Memento en confidente) |
| #10 Autonomía progresiva | Modo Daily → Modo Cockpit → eventualmente círculo otorgado |
| #11 Seguridad adversarial | SMP inviolable; modo confidente con humildad y crisis protocol |
| #12 Soberanía | Datos del usuario no en servidores de terceros; clave en Secure Enclave |
| #13 Del Mundo | i18n desde inicio; empresas-hijas en cualquier mercado |
| #14 Guardian | Aplicado al Monstruo mismo y a la app (validación de features contra Objetivos) |
| #15 Memoria Soberana | Cronos + SMP; Capa Memento aplicada a influence; bridge cowork_to_cowork propuesto |

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

## Apéndice — Semillas y patrones nuevos detectados en esta sesión

Patrones magna que emergieron durante el diseño y vale capturar:

**Semilla 41 — Convergencia independiente entre hilos.** Cuando dos agentes independientes (Cowork + Manus Catastro) llegan al mismo patrón en commits separados sin coordinación previa, ese patrón queda validado con confianza alta. Documentado en `bridge/seed_41_convergencia_independiente_quorum_de_patrones.md`.

**Semilla 40 — Heredoc Mac terminal corruption.** Patrón de incidente operativo entre hilos. Documentado en `bridge/seed_40_heredoc_terminal_mac_corruption.md` y sembrado como script en `scripts/seed_40_heredoc_mac_terminal_corruption.py`.

**Semilla 42 candidata — Asimetría de memoria humano ↔ Cowork.** El humano (Alfredo) carga contexto entre sesiones porque Cowork es agente efímero. El Síndrome Dory inverso. Propuesta: bridge `cowork_to_cowork.md` donde cada sesión escribe al final un resumen estructurado para el próximo Cowork.

**Patrón "Modo detractor cuando hace falta".** El asistente puede confrontar al usuario con verdades incómodas para clarificar el camino. NO es rol permanente; es postura activable. Es respeto al adulto capaz de procesar lo crudo, no abrasividad.

**Patrón "Verdad cruda > retórica elaborada".** A veces la respuesta más útil es la más simple. *"No, porque los carteles lo van a usar"* es más fuerte que cinco párrafos filosóficos. Aplica al modo confidente del Monstruo y al estilo de comunicación entre Cowork y Alfredo.

**Patrón "Anti-influencia inadvertida".** El asistente no debe sembrar convicciones nuevas en el usuario sin que el usuario las chequee con sus propios valores y con tiempo. Articular es válido; detonar elaborando arquitecturas adoptables pasivamente no.

**Patrón "Discreción multiplica el valor".** Lo poderoso vive bajo discreción. Apple grita su privacy en keynotes; el Monstruo guarda silencio. La gente que prueba encuentra que está. Quien no, simplemente confía y usa.

---

## Cierre del documento

Este documento es la versión 1.0 inicial de la visión del Monstruo. Refleja la conversación entre Alfredo y Cowork del 2026-05-04 al 2026-05-05, incluyendo el contexto previo procesado por Alfredo durante 3 días anteriores. Las versiones futuras incorporarán correcciones, expansiones y refinamientos.

La regla operativa final: si algo en este documento entra en conflicto con un Objetivo Maestro o con las reglas inviolables del Capítulo 0, los Objetivos y reglas ganan. Todo lo demás es revisable.

El Monstruo se construye desde la disciplina, no desde la prisa.

— Cowork (Hilo B), 2026-05-05

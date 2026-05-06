# Sprint Mobile 2 — Modo Daily fase 1 con stubs

**Owner:** Hilo Ejecutor (Manus) Mobile
**Zona protegida:** `apps/mobile/lib/modes/daily/` + `apps/mobile/lib/core/services/`
**ETA estimada:** 5-8h reales con Apéndice 1.3 factor velocity 5-8x
**Bloqueos:** Sprint Mobile 1 cerrado verde
**Prerequisito:** Esqueleto Flutter funcional con toggle, brand DNA, A2UI renderer básico

---

## 1. Contexto

Mobile 1 entregó la cara del Monstruo vacía. Mobile 2 la pone **viva con datos mock** — Alfredo puede tocarla, hablarle (mock), navegarla. Las 5 superficies primarias del Daily implementadas con stubs realistas.

**Crítico:** TODOS los datos siguen siendo stubs en memoria. SMP aún no cerró. Esta es la fase donde Alfredo siente cómo se siente usar el Monstruo, sin riesgo de cargar datos reales que después haya que migrar.

---

## 2. Objetivo único del sprint

Implementar las 5 superficies primarias del Modo Daily (Home, Threads, Pendientes, Conexiones, Perfil) como Flutter screens completas, con stubs realistas que muestran lo que la app hará cuando los datos reales lleguen. Voice input simulado (procesa una frase hardcodeada), tarjetas A2UI streaming, río de Cronos navegable.

Cuando este sprint cierre: Alfredo abre la app, dice "buscame sushi cerca" (o tap), ve una tarjeta A2UI con 3 lugares (mock), navega a Threads, ve conversaciones pasadas (mock), revisa Pendientes (vacío), Conexiones (lista de apps configurables), Perfil. Todo se siente vivo y hermoso.

---

## 3. Bloques del sprint

### 3.A — Superficie 1: Home

**3.A.1 — Input universal voice + camera + tap**

`HomeInputBar` widget:
- Botón micrófono central (push-to-talk simulado en Mobile 2; voz continua en Mobile 6)
- Botón cámara izquierdo (visual search simulado — tap toma foto, muestra tarjeta mock con "esto es: pintura al óleo, dónde se compra: ...")
- TextField central que aparece al tap, para tipear si no querés voz
- Animación física al expandir/contraer

**3.A.2 — Output streaming-first**

Cuando el usuario hace input (voz mock o tap), aparece una tarjeta A2UI streaming abajo del input. La tarjeta se construye progresivamente (carácter a carácter o chunk a chunk) — feel de Manus / Claude / Cursor, NO request-response.

Stub: 5 frases hardcodeadas con respuestas A2UI pre-grabadas (sushi cerca, peso argentino, mensaje a Juan, foto-buscame-esto, recordar idea).

**3.A.3 — Río de Cronos como franja horizontal**

`CronosRiverWidget` debajo del input. ScrollView horizontal con cards mock representando 30 momentos del pasado del usuario (timestamps fake distribuidos en últimos 6 meses). Cada card muestra: emoji de capa (salud, relaciones, decisiones, etc.), preview de 1 frase, fecha relativa.

Tap en card → expand a momento completo (mock).

**3.A.4 — Tests + screenshot**

Widget tests para los 3 sub-componentes. Golden file test para garantizar consistencia visual del Home.

### 3.B — Superficie 2: Threads

**3.B.1 — Lista minimalista de conversaciones**

`ThreadsListScreen`:
- Una conversación por línea
- Resumen 1 frase (mock)
- Fecha relativa ("hace 2h", "ayer", "mié pasado")
- Categoría tonal con dot color (mock: 4 categorías tonales)
- Sin avatares, sin emojis distractores — minimalismo Linear / Superhuman

**3.B.2 — Vista de conversación**

`ThreadDetailScreen` al tap:
- Burbujas de mensajes con brand DNA (forja para Monstruo, graphite para usuario)
- Timestamps relativos
- Cards A2UI dentro del thread cuando aplique

20 conversaciones mock con 5-15 mensajes cada una, contenido realista (preguntas tipo "buscame restaurante", "cuándo es mi reunión", etc. con respuestas verosímiles).

### 3.C — Superficie 3: Pendientes

**3.C.1 — Lista de acciones pendientes con preview editable**

`PendientesScreen`:
- Cards de acciones que el Monstruo necesita confirmación humana
- Cada card con preview editable inline (streaming approval): "Voy a reservar Pujol mañana 8pm — [Editar] [Cancelar] [Confirmar]"
- Stub: 3 pendientes mock (1 reserva restaurante, 1 mail draft, 1 transfer money con HITL).

**3.C.2 — Estado vacío honesto**

Si NO hay pendientes: superficie completamente vacía con brand DNA (espacio en blanco con sutil pattern forja en background). NUNCA decir "no hay nada nuevo" o similar. El silencio es la feature.

### 3.D — Superficie 4: Conexiones

**3.D.1 — Lista de apps externas**

`ConexionesScreen` con grid de toggles:
- Tier 1: WhatsApp, Apple Mail, Gmail, Apple Calendar, Google Calendar, Apple Maps, Google Maps, Apple Photos, Google Photos
- Tier 2: Files, Drive, Dropbox, Apple Pay, Apple Health, Google Health Connect

Cada item:
- Logo del servicio (con permission flag — solo logos cuyo uso esté permitido per Apple guidelines)
- Toggle on/off
- Estado: "Conectada", "Desconectada", "Permisos pendientes"
- Tap → permissions granulares (qué leer, qué escribir, audit log accesible)

Stub: ningún servicio conectado de verdad. Tap "Conectar WhatsApp" muestra modal simulado de consent + persiste estado en SharedPreferences.

**3.D.2 — Audit log accesible**

`AuditLogScreen` mostrando últimas 20 acciones (mock): "El Monstruo leyó 5 mails de Pedro hace 30min", "El Monstruo mandó WhatsApp a Juan ayer", etc.

### 3.E — Superficie 5: Perfil

**3.E.1 — Identidad + privacidad + recovery**

`PerfilScreen`:
- Nombre del usuario (Alfredo González — hardcoded en Mobile 2, configurable cuando SMP cierre)
- Avatar (placeholder con brand DNA)
- Sección "Privacidad" con UNA línea: *"Tus datos están protegidos por el Sovereign Memory Protocol. Ver detalle técnico."* → tap navega a página técnica externa (URL stub por ahora)
- Sección "Recovery" con preview de Shamir's Secret Sharing (no funcional en Mobile 2, solo UX)
- Sección "Exportar todos mis datos" (stub: descarga JSON vacío)
- Sección "Eliminar cuenta" con confirmación múltiple (stub)

Cero marketing privacy-first. Una línea sutil. Quien quiera profundizar lo hace.

### 3.F — Voice input simulado

**3.F.1 — Push-to-talk simulado**

Mantén el botón micrófono presionado → muestra waveform animado + texto streaming "escuchando..." → al soltar muestra texto reconocido (mock: 5 frases hardcodeadas detectables por keywords del input final).

NO conectar a Whisper API real ni microphone permission real todavía. Eso es Mobile 6.

**3.F.2 — Apple Watch double-tap stub**

Si hay Watch conectado y reconocido: card en Settings que dice "Apple Watch detectado, doble-tap como veto activable post-Mobile 6". No funcional, solo placeholder de la futura feature.

### 3.G — Smoke productivo + validación

**3.G.1 — Build macOS + iOS Simulator**

Builds limpios sin errors ni warnings.

**3.G.2 — Validación humana de Alfredo**

Alfredo prueba las 5 superficies, navega entre ellas, hace voice mock, abre cards A2UI streaming, valida que se siente vivo + hermoso. Si SÍ: Sprint Mobile 2 cerrado verde.

---

## 4. Magnitudes esperadas

- ~2,000 LOC nuevas
- ~30 archivos nuevos en `modes/daily/` + `core/services/`
- ~25 widget tests + golden file tests para cada superficie
- 1 validación humana de Alfredo

---

## 5. Disciplina aplicada

- ✅ DSC-G-004: brand DNA en TODA superficie
- ✅ DSC-G-002: 7 capas transversales empiezan a cargarse — SEO meta tags básicos (aunque sea mobile, bueno tenerlo desde inicio)
- ✅ Brand DNA error naming Dart: `dailyHomeInputVoiceMockFailed`, `threadsListLoadStubFailed`, etc.
- ✅ Capa Memento: stubs aislados, si fallan no crashean app
- ✅ Privacy-first: ningún permiso real solicitado todavía (mics, cámara) hasta que SMP cierre
- ✅ Anti-bloating: superficies austeras, NO meter más de lo descrito en v1.2 Cap 2

---

## 6. Cierre formal

Cuando los 7 bloques cierren verde + validación humana:

> 🏛️ **Modo Daily fase 1 con stubs — DECLARADO**

Y reporta al bridge con: screenshots de las 5 superficies, video de navegación, builds.

---

## 7. Lo que NO entra

- Datos reales (esperan SMP)
- Integraciones nativas reales con WhatsApp/Maps/Mail (Mobile 7+ post-SMP)
- Voz continua real con Whisper (Mobile 6)
- Smart Notebook real (Mobile 4 con stubs avanzados; real post-SMP)
- Listening ambient con kill switch (Mobile 6)
- Modo Confidente (Mobile 5)

---

— Cowork (Hilo A), spec preparada 2026-05-06.
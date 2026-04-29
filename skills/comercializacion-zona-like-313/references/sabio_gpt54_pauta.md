# GPT-5.4: Diseño del sistema de pauta quirúrgica IA-first

---

Aquí va una propuesta **IA-first, operable, específica para 313 butacas en Mérida**, pensada como **motor de demanda de precisión** encima de Ticketlike.

---

# PAUTA QUIRÚRGICA INTELIGENTE
## Zona Like 313 × Ticketlike × Leoncio El Fugitivo

## 0. Principio rector
La pauta no es un “canal de anuncios”.  
Es un **sistema autónomo de llenado de inventario premium** que:

- lee ocupación en tiempo real,
- detecta huecos por tipo de juego,
- construye micro-audiencias con first-party data,
- genera creativos narrativos dinámicos,
- activa secuencias por urgencia,
- optimiza presupuesto por probabilidad de compra,
- y empuja tráfico a Ticketlike como motor de conversión.

El humano **no opera campañas manualmente todos los días**.  
El humano:
1. define reglas,
2. aprueba narrativa/marca,
3. supervisa excepciones,
4. cuida experiencia en estadio.

---

# 1. OBJETIVO DEL SISTEMA

## Meta operativa
Llenar **313 butacas premium** en **42 juegos de local** con una combinación de:

- venta anticipada,
- aceleración por narrativa,
- recuperación de carritos,
- activación de audiencias dormidas,
- y “last-mile fill” en las últimas 72h.

## KPI principal
- **Occupancy Rate por juego** de Zona Like 313

## KPIs de control
- % ocupación a T-14 / T-7 / T-3 / T-1 / game day
- ROAS por canal
- CAC incremental por butaca vendida
- tasa de conversión por audiencia
- tasa de recompra por segmento
- fill rate de inventario rojo
- revenue por asiento disponible
- velocidad de venta por acto narrativo de Leoncio
- CTR / VTR / CVR por creativo narrativo

---

# 2. ARQUITECTURA DEL SISTEMA

## Núcleo
**Ticketlike = CDP + motor transaccional + fuente de verdad**

Todo sale de Ticketlike y todo regresa a Ticketlike.

### Capas
1. **Data Layer**
   - compras históricas
   - navegación web
   - abandono de checkout
   - frecuencia de compra
   - ticket promedio
   - tipo de juego comprado
   - horario de compra
   - método de pago
   - geolocalización
   - código postal
   - dispositivo
   - canal de origen
   - grupo/compras múltiples
   - uso de promociones
   - asistencia efectiva si se puede validar con QR scan

2. **Identity Layer**
   - email hash
   - phone hash
   - device IDs permitidos por plataforma
   - Meta CAPI identifiers
   - Google enhanced conversions
   - TikTok Events API identifiers
   - WhatsApp opt-ins

3. **Prediction Layer**
   Modelos de IA para:
   - propensión de compra por juego
   - propensión de recompra
   - sensibilidad a precio
   - afinidad narrativa
   - afinidad por canal
   - probabilidad de compra grupal
   - probabilidad de compra last-minute
   - riesgo de no-show / no recompra

4. **Activation Layer**
   - Meta Ads
   - Google Ads / YouTube
   - TikTok Ads
   - WhatsApp Business API
   - Email automation
   - RCS/SMS si aplica
   - audiencias para ventas B2B automatizadas
   - landing pages dinámicas en Ticketlike

5. **Decision Engine**
   Un orquestador que decide:
   - qué audiencia activar,
   - con qué mensaje,
   - en qué canal,
   - con qué presupuesto,
   - según ocupación, tiempo restante, rival, día, clima, narrativa y performance.

---

# 3. CLASIFICACIÓN DE JUEGOS: TIER A / B / C

La pauta quirúrgica cambia por tipo de juego.

## Tier A
Juegos de alta demanda natural:
- rival fuerte
- fin de semana
- vacaciones
- fechas especiales
- juegos con mayor tracción narrativa

### Objetivo
No “gastar para vender lo que ya se vende”.  
Objetivo = **maximizar revenue, acelerar preventa, premium upsell, capturar data**.

## Tier B
Demanda media:
- rival intermedio
- jueves/viernes
- demanda razonable pero no automática

### Objetivo
Mover inventario con mezcla de:
- retargeting,
- lookalikes,
- grupos,
- turismo,
- corporativo táctico.

## Tier C
Demanda débil:
- días complicados
- rival de bajo arrastre
- clima adverso probable
- poca anticipación

### Objetivo
**llenado agresivo y automatizado**, con narrativa, urgencia, bundles, grupos y activación multicanal.

---

# 4. MICRO-AUDIENCIAS EXACTAS POR CANAL Y TIER

La clave no es “hombres 25-45 fans del béisbol”.  
La clave es construir **micro-audiencias de intención real**.

## 4.1 Audiencias base desde Ticketlike

### A. Compradores premium recurrentes
- 2+ compras en Zona Like 313 en últimos 12 meses
- ticket promedio alto
- compran con anticipación
- alta afinidad premium

**Uso:** preventa Tier A, upgrades, membresía, referidos.

### B. Compradores premium ocasionales
- 1 compra premium últimos 12 meses
- no recompra aún
- alta propensión a reactivar

**Uso:** retargeting fuerte Tier B/C.

### C. Compradores de otras zonas con potencial de upgrade
- compran Leones, pero no Zona Like 313
- ticket medio-alto
- van en pareja o grupo pequeño
- compran fines de semana

**Uso:** upgrade aspiracional.

### D. Abandono de checkout premium
- visitó Zona Like 313
- inició checkout
- no pagó

**Uso:** recuperación inmediata.

### E. Navegadores de alta intención
- 2+ visitas a página de Zona Like 313
- tiempo alto en página
- scroll profundo
- revisó mapa/asientos

**Uso:** retargeting 1-7 días.

### F. Compradores grupales
- 4+ boletos por transacción
- celebraciones previas
- fines de semana
- fechas familiares

**Uso:** grupos y celebraciones.

### G. Compradores corporativos detectados
Se infiere por:
- dominios corporativos
- facturación empresarial
- compras repetidas con patrones de oficina
- horarios laborales
- múltiples asistentes
- uso de tarjetas empresariales

**Uso:** arrendamiento, hospitalidad, invitación a clientes.

### H. Turismo / visitante
Se infiere por:
- IP/geo fuera de Yucatán
- compra cercana a fecha de juego
- navegación desde hoteles / zonas turísticas
- idioma / comportamiento móvil
- estancia corta

**Uso:** hotelería y turismo.

### I. Jóvenes / universitarios / porra
- alta interacción social
- video views
- afinidad con contenido de identidad y pertenencia
- compras de menor anticipación
- alta respuesta a WhatsApp/TikTok

**Uso:** porra, resistencia, activación de ambiente.

### J. Familias / celebraciones
- compras de 3-6 boletos
- fines de semana
- cumpleaños / fechas especiales
- alta respuesta a bundles

**Uso:** grupos, cumpleaños, aniversarios.

---

## 4.2 Lookalikes alimentados por IA

No se crean lookalikes genéricos.  
Se crean **seed lists de máxima calidad**.

### Seeds prioritarios
1. Top 5% compradores por revenue premium
2. Top 10% compradores por frecuencia
3. Compradores premium Tier C exitosos
4. Compradores con recompra en menos de 30 días
5. Compradores grupales de alto valor
6. Compradores turísticos premium
7. Compradores corporativos con 2+ eventos
8. Usuarios que vieron capítulo narrativo + compraron
9. Abandonadores recuperados exitosamente
10. Referidos que compraron

### Qué datos alimentan los modelos
- RFM: recency, frequency, monetary
- tipo de juego comprado
- lead time de compra
- canal de adquisición
- creative ID que convirtió
- narrativa/acto que convirtió
- rival
- día de semana
- clima
- distancia al estadio
- tamaño de grupo
- precio pagado
- método de pago
- tasa de apertura/click en WhatsApp/email
- engagement de video
- escaneo de QR / asistencia

### IA aplicada
Un modelo de scoring clasifica usuarios en:
- **P1** compra casi segura
- **P2** compra probable
- **P3** compra inducible con narrativa/urgencia
- **P4** solo responde a oferta o grupo
- **P5** baja prioridad

La pauta se concentra en P1-P3.  
P4 se activa solo en rojo.  
P5 casi no recibe presupuesto.

---

## 4.3 Micro-audiencias por canal

---

### CANAL CORPORATIVO
#### Tier A
- directores comerciales
- RH
- compras
- relaciones públicas
- dueños de PyMEs premium
- clientes actuales de Ticketlike con facturación empresarial

**Mensaje:** hospitalidad, networking, experiencia premium, invitación a clientes.

#### Tier B
- empresas medianas con 50-500 empleados
- despachos, agencias, inmobiliarias, automotrices, salud privada

**Mensaje:** incentivo, convivencia, reconocimiento.

#### Tier C
- cuentas con historial de no respuesta pero alta afinidad local
- empresas con cumpleaños/fechas internas
- equipos comerciales

**Mensaje:** “últimas butacas para activar a tu equipo esta semana”.

**Construcción IA:** scraping legal + enrichment + scoring + matching con Meta/Google Customer Match + secuencias automatizadas a landing B2B.

---

### CANAL ESCOLAR
#### Tier A
- universidades privadas
- asociaciones estudiantiles
- exalumnos
- posgrados ejecutivos

#### Tier B
- preparatorias privadas
- escuelas deportivas
- universidades públicas con grupos organizados

#### Tier C
- coordinadores de vida estudiantil
- grupos de graduación
- sociedades de alumnos

**Construcción IA:** bases institucionales, formularios automatizados, audiencias por edad/intereses/comportamiento, lookalikes de compradores jóvenes.

---

### CANAL TURISMO
#### Tier A
- visitantes en Mérida 2-5 días
- viajeros con interés en experiencias locales premium
- huéspedes de hoteles 4-5 estrellas
- parejas / familias de alto gasto

#### Tier B
- turistas nacionales en Cancún/Riviera con extensión a Yucatán
- viajeros de CDMX, Monterrey, Guadalajara

#### Tier C
- visitantes ya en Mérida con geofencing
- búsquedas “qué hacer en Mérida hoy”
- usuarios cerca de Paseo Montejo / hoteles / aeropuerto

**Construcción IA:** geofencing, search intent, hotel CRM integrations, lookalikes de compradores turísticos.

---

### CANAL PORRA / RESISTENCIA
#### Tier A
- superfans
- creadores locales
- asistentes frecuentes
- usuarios que interactúan con contenido de identidad del club

#### Tier B
- jóvenes 18-34
- fans del béisbol y entretenimiento local
- comunidades universitarias

#### Tier C
- audiencias de video viewers 50%+
- engagers de Leoncio
- usuarios que comparten memes / reels del club

**Construcción IA:** engagement graph, social listening, clustering de afinidad.

---

### CANAL GRUPOS Y CELEBRACIONES
#### Tier A
- cumpleaños próximos
- aniversarios
- familias premium
- grupos de amigos con historial de compra múltiple

#### Tier B
- mamás/papás 28-50
- organizadores de eventos pequeños
- oficinas celebrando metas

#### Tier C
- abandonadores de 4+ boletos
- usuarios que consultaron mapa para varios asientos
- compradores de fin de semana

**Construcción IA:** inferencia de ocasión + señales de compra grupal + remarketing dinámico.

---

# 5. CREATIVOS NARRATIVOS: LEONCIO COMO SISTEMA GENERATIVO

No se hacen “20 artes”.  
Se construye una **fábrica de creativos narrativos con IA**.

## 5.1 Estructura narrativa
Temporada = 42 juegos = 42 capítulos  
Divididos en 3 actos.

### Acto 1: Aparición / amenaza
- Leoncio escapa
- deja pistas
- desafía a la afición
- siembra tensión

### Acto 2: Dominio / infiltración
- toma espacios simbólicos
- reta a la ciudad
- divide a la afición
- sube la urgencia

### Acto 3: Cacería / resolución
- cada juego importa
- la Zona Like 313 es “territorio de resistencia”
- cierre épico

## 5.2 Motor creativo IA
La IA genera variantes por:

- audiencia
- tier del juego
- acto narrativo
- plataforma
- formato
- urgencia de ocupación
- clima
- rival
- hora del día

## 5.3 Tipos de piezas
- video corto 6-15s
- reels/stories 9:16
- carruseles
- imagen estática con copy dinámico
- bumper YouTube
- search copy
- WhatsApp cards
- email hero dinámico
- landing headers dinámicos en Ticketlike

## 5.4 Plantilla de generación
Cada pieza se arma con variables:

- `acto_narrativo`
- `capitulo`
- `rival`
- `tier_juego`
- `ocupacion_actual`
- `urgencia`
- `audiencia`
- `beneficio_principal`
- `CTA`
- `tono`

### Ejemplo
**Audiencia:** corporativo  
**Acto:** Leoncio infiltró la ciudad  
**Mensaje IA:**  
“Leoncio ya tomó la conversación. Recupera el palco social más codiciado de la semana. Zona Like 313 para clientes, equipo o aliados. Quedan 41 butacas.”

### Ejemplo
**Audiencia:** turismo  
“Si estás en Mérida esta noche, no veas la historia desde fuera. Leoncio dejó una pista en la Zona Like 313. Vive el capítulo en vivo.”

### Ejemplo
**Audiencia:** porra  
“Leoncio cree que hoy el estadio se enfría. Demuéstrale lo contrario. Últimas butacas en la 313.”

## 5.5 IA creativa concreta
### Generación de copy
- LLM entrenado con:
  - tono de marca
  - biblia narrativa de Leoncio
  - restricciones legales
  - CTAs aprobados
  - vocabulario local yucateco moderado

### Generación visual
- plantillas maestras en Figma/Canva API/Adobe Express API
- fondos y assets aprobados
- IA solo recombina, adapta y versiona
- no se deja a IA inventar branding desde cero

### Generación de video
- clips base + motion templates
- voiceover sintético aprobado
- subtítulos automáticos
- versiones por duración/plataforma

### Testing automático
La IA rota:
- hook
- visual principal
- CTA
- color dominante
- presencia de precio
- presencia de urgencia
- presencia de capítulo narrativo

Y aprende qué combinación convierte por audiencia.

---

# 6. TRIGGERS POR OCUPACIÓN

Aquí está el corazón del sistema.

## Semáforo de ocupación
Para 313 butacas:

- **Verde:** 260-313 vendidas
- **Amarillo:** 205-259
- **Rojo:** <205
- **Rojo crítico:** <150 a 48h
- **Negro táctico:** <100 a 24h

---

## T-72h
### Si estamos en rojo (<205)
Se activa automáticamente la secuencia **FILL-72**:

#### 1. Reasignación de presupuesto
- pausar awareness amplio
- mover 60-75% del presupuesto a performance/retargeting
- concentrar en Meta + WhatsApp + Google Search + email

#### 2. Activación de audiencias calientes
- abandonadores 1-14 días
- navegadores 1-30 días
- compradores premium ocasionales
- compradores de otras zonas con score de upgrade
- grupos 4+ boletos
- turismo ya en Mérida

#### 3. Cambio creativo
- de narrativa atmosférica a narrativa con urgencia
- “capítulo en riesgo / últimas butacas / no te quedes fuera”

#### 4. Landing dinámica
Ticketlike muestra:
- contador de butacas restantes
- mapa simplificado
- checkout express
- bundle sugerido
- prueba social

#### 5. WhatsApp automation
A usuarios opt-in:
- mensaje personalizado
- deep link al checkout
- recordatorio a 6h si no compra

#### 6. Search capture
Subir pujas en:
- Leones de Yucatán boletos
- qué hacer en Mérida hoy
- boletos béisbol Mérida
- experiencias premium Mérida

---

## T-48h
### Si seguimos en rojo
Se activa **FILL-48 ESCALATION**

#### 1. Expansión controlada
- lookalikes 1%-3% de compradores premium
- intereses afines locales
- geofencing Mérida + hoteles + zonas corporativas

#### 2. Oferta táctica no destructiva
No bajar precio frontal si no es necesario.  
Primero probar:
- valor agregado
- acceso narrativo
- beneficio de grupo
- upgrade de experiencia
- bebida/snack/merch ligero
- “compra 4 y recibe activación especial”

#### 3. Secuencia B2B automatizada
- anuncios lead gen a decisores
- WhatsApp bot B2B
- landing “activa a tu equipo mañana”
- respuesta automática con disponibilidad real

#### 4. Secuencia turismo
- anuncios en radio de 5-10 km de hoteles
- creatives “esta noche en Mérida”
- integración con concierge digital / QR en lobby

#### 5. Secuencia porra
- video corto + CTA inmediato
- incentivo de identidad, no descuento puro

---

## T-24h
### Si estamos en rojo crítico
Se activa **LAST MILE 24**

#### 1. Dominio de canales de respuesta inmediata
Prioridad:
1. WhatsApp
2. Meta retargeting
3. Google Search
4. Email
5. RCS/SMS
6. TikTok solo si hay señal fuerte de respuesta

#### 2. Audiencias ultra calientes
- checkout abandonado <7 días
- visitó página hoy
- abrió email/WhatsApp y no compró
- compradores last-minute históricos
- usuarios cerca del estadio / zonas premium

#### 3. Creativo
- “Hoy”
- “Últimas X butacas”
- “Capítulo de esta noche”
- “Acceso inmediato”

#### 4. Checkout express
- Apple Pay / Google Pay / 1-click si existe
- menos campos
- asientos preseleccionados
- link directo por audiencia

#### 5. Dynamic pricing o bundle
Solo si el modelo lo recomienda.  
No generalizado.  
Puede ser:
- bundle por 2
- grupo 4
- upgrade desde otra zona
- beneficio de consumo

---

## Tiempo real: game day
### Si faltan horas y hay huecos
Se activa **REAL-TIME FILL**

- geofencing 3-8 km
- search “boletos hoy”
- stories con countdown
- WhatsApp a compradores históricos de último minuto
- push a base local opt-in
- retargeting de visitantes del día
- creativos con “entra al capítulo en vivo”

### Si ya estamos casi llenos
Se activa **REVENUE PROTECT**
- bajar gasto de adquisición
- subir upsell / waitlist / siguiente juego / membresía

---

# 7. RETARGETING DESDE TICKETLIKE

Esto debe ser técnicamente sólido.

## 7.1 Integración first-party
Ticketlike debe enviar eventos server-side y browser-side.

### Eventos clave
- PageView
- ViewContent
- SeatMapView
- AddToCart
- InitiateCheckout
- AddPaymentInfo
- Purchase
- GroupInquiry
- CorporateInquiry
- WhatsAppClick
- EmailOpen
- QRScan / Attend

## 7.2 Conexiones
### Meta
- Meta Pixel + Conversion API
- Custom Audiences
- Value-based lookalikes
- Dynamic creative optimization

### Google
- GA4
- Google Ads enhanced conversions
- Customer Match
- YouTube audience sync
- Search remarketing lists

### TikTok
- TikTok Pixel + Events API
- custom audiences
- engagement retargeting

### WhatsApp
- WhatsApp Business API
- eventos de click y respuesta
- secuencias por intención

## 7.3 Segmentos de retargeting
- 0-1h abandono
- 1-24h abandono
- 1-3 días
- 4-7 días
- 8-30 días
- visitantes de Zona Like 313 sin compra
- compradores de otras zonas
- compradores de juego pasado no compraron siguiente
- video viewers 75%+ de Leoncio
- usuarios que interactuaron con capítulo actual

## 7.4 Server-side tracking
Indispensable para no depender solo de cookies.

### Beneficios
- mejor match rate
- mejor atribución
- mejor optimización de campañas
- recuperación de señales iOS
- audiencias más robustas

### Recomendación
Implementar vía:
- GTM server-side
- Stape / server container
- webhooks desde Ticketlike
- warehouse ligero

---

# 8. MIX ÓPTIMO DE PLATAFORMAS PARA MÉRIDA

Para 313 butacas no se necesita “estar en todo”.  
Se necesita **precisión y velocidad**.

## Prioridad 1: Meta (Facebook + Instagram)
### Por qué
- mejor cobertura local en Mérida
- fuerte para retargeting
- fuerte para lookalikes
- stories/reels funcionan bien para narrativa
- buen costo para audiencias locales y familiares
- útil para corporativo ligero y grupos

### Uso
- always-on
- retargeting
- lookalikes
- geofencing suave
- video narrativo
- conversion campaigns

**Peso sugerido:** 40-45%

---

## Prioridad 2: WhatsApp Business API
### Por qué
- canal de respuesta inmediata
- altísima tasa de apertura
- ideal para 72h/48h/24h
- perfecto para recuperación de abandono y grupos
- muy fuerte en México

### Uso
- abandono de checkout
- recordatorios
- links directos
- secuencias B2B
- concierge de turismo
- grupos y celebraciones

**Peso sugerido:** 15-20% del esfuerzo, no necesariamente del spend publicitario.

---

## Prioridad 3: Google Search
### Por qué
- captura demanda existente
- clave para “qué hacer hoy”, “boletos Leones”
- muy eficiente en ventanas cortas

### Uso
- branded
- non-branded local intent
- turismo de último minuto
- game day

**Peso sugerido:** 15-20%

---

## Prioridad 4: YouTube
### Por qué
- excelente para construir la narrativa de Leoncio
- video secuencial
- remarketing fuerte
- awareness útil para Tier A/B

### Uso
- capítulos teaser
- bumpers
- secuencias por acto
- remarketing a viewers

**Peso sugerido:** 8-12%

---

## Prioridad 5: TikTok
### Por qué
- útil para porra, jóvenes, narrativa, viralidad
- menos fuerte para conversión directa premium que Meta, pero valioso arriba del funnel y para resistencia

### Uso
- contenido de Leoncio
- UGC sintético/creador híbrido
- porra
- audiencias jóvenes

**Peso sugerido:** 8-10%

---

## Prioridad 6: Email
### Por qué
- casi costo marginal cero
- excelente para base propia
- útil para secuencias de capítulos y recompra

### Uso
- preventa
- abandono
- recompra
- capítulos semanales
- membresía

**Peso sugerido:** always-on, costo bajo.

---

## Prioridad 7: RCS/SMS
### Por qué
- solo para urgencia o usuarios sin WhatsApp opt-in
- útil en T-24h

**Peso sugerido:** táctico.

---

# 9. ORQUESTACIÓN AUTOMATIZADA

## 9.1 Stack recomendado

### A. Fuente de datos / CDP
- Ticketlike como fuente principal
- BigQuery o Snowflake ligero
- reverse ETL a plataformas

### B. Tracking
- GA4
- GTM web + GTM server-side
- Meta CAPI
- Google enhanced conversions
- TikTok Events API

### C. Orquestación
- n8n o Make para flujos rápidos
- Airflow si quieren robustez enterprise
- webhooks desde Ticketlike
- reglas en tiempo real por ocupación

### D. IA / modelos
- LLM para copy y secuencias
- modelo de propensity scoring en Vertex AI / AWS SageMaker / notebooks productizados
- motor de recomendación simple al inicio:
  - XGBoost / LightGBM
  - luego reinforcement optimization si escala

### E. Creatividad
- Figma API / Canva API / Adobe Express API
- Runway / Pika / generador de video con templates
- biblioteca de assets aprobados

### F. CRM / mensajería
- HubSpot / Customer.io / Braze / Klaviyo
- WhatsApp Business API vía Twilio / Gupshup / 360dialog
- Sendgrid / Postmark / Mailgun para email

### G. Ads
- Meta Ads API
- Google Ads API
- TikTok Ads API

### H. BI
- Looker Studio / Metabase / Power BI
- dashboard de ocupación y performance por juego

---

## 9.2 Lógica de automatización

### Flujo maestro
1. Ticketlike actualiza ocupación por juego cada 5-15 min
2. Orquestador lee:
   - ocupación
   - tiempo al juego
   - tier
   - ritmo de venta
   - performance por canal
3. Decision engine asigna estado:
   - normal
   - acelerar
   - rojo
   - last mile
4. Se activan:
   - audiencias
   - creativos
   - presupuestos
   - mensajes
   - landing variants
5. Se mide conversión
6. El modelo recalibra score y presupuesto

---

## 9.3 Ejemplo de regla real

### Regla
Si:
- juego = Tier C
- faltan 72h
- ocupación < 205
- ritmo de venta últimas 24h < umbral
- clima no severo

Entonces:
- aumentar Meta retargeting +35%
- activar WhatsApp abandono + navegadores calientes
- activar Search “hoy/mañana”
- lanzar creativos de urgencia narrativa
- activar lookalike top buyers 1%
- enviar email “capítulo en riesgo”
- cambiar hero de landing a “quedan X butacas”

---

# 10. PRESUPUESTO Y LÓGICA DE INVERSIÓN

Para 

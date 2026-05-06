# 🕸️ Matriz de Cruces Inter-Proyecto del Mounstro

> **Propósito:** Mapear las dependencias y oportunidades de componentes compartidos entre los 20 proyectos del portfolio. Antes de diseñar cualquier proyecto solo, Cowork debe consultar esta matriz para detectar reutilizaciones y antipatrones de duplicación.

**Generado:** 2026-05-06 (Sprint Memento, post-Capilla de Decisiones)
**Mantenedor:** Manus actualiza al cierre de cada sesión donde se detecte un cruce nuevo.
**Cómo leer:** Cada celda indica el tipo de cruce entre proyecto-fila y proyecto-columna.

## Leyenda de tipos de cruce

| Símbolo | Significado |
|---|---|
| 🔴 | **Componente compartido obligatorio** — debe construirse 1 vez y reutilizarse |
| 🟠 | **Dependencia funcional** — uno requiere del otro para operar |
| 🟡 | **Mismo dominio o mercado** — comparten lógica de negocio o cliente |
| 🟢 | **Sinergia oportunística** — pueden integrarse pero no es bloqueante |
| ⚪ | **Sin cruce identificado** |

---

## Matriz 20×20 (resumida — solo cruces ≠ ⚪)

Para legibilidad, en lugar de tabla 20×20 vacía mostramos solo los **cruces identificados** agrupados por proyecto-fila. Si un proyecto no aparece como fila, todos sus cruces ya están listados desde el otro lado.

### EL-MONSTRUO (orquestador madre)

| Cruza con | Tipo | Naturaleza del cruce |
|---|---|---|
| **TODOS los 19 restantes** | 🟠 | Es la capa de orquestación: cada proyecto se construye o se consulta vía El Monstruo |
| Bot Telegram | 🔴 | Bot es interfaz Telegram del Monstruo, comparten kernel |
| Command Center | 🔴 | Command Center es UI web del Monstruo, comparten datos |
| Simulador Universal | 🔴 | Simulador es módulo del Monstruo, comparten Supabase |

### CIP — Inversión Inmobiliaria Fraccionada

| Cruza con | Tipo | Naturaleza del cruce |
|---|---|---|
| CIES | 🟡 | Mismo dominio (instrumentos financieros) — DSC del corpus EPIA los acopla `CIP/CIES` |
| Marketplace Muebles | 🟢 | CIP puede listar inmuebles que después amueblen vía Marketplace |
| LikeTickets | 🔴 | Reutiliza módulo checkout Stripe + webhook + DB confirmation (DSC-LT-003) |
| OMNICOM | 🟢 | Cruzados en estatuto IGCAR (DSC-X-001) |
| Vivir Sano | 🟢 | Patrón "biblia v4.x master plan" replicable |
| El Monstruo | 🟠 | CIP es primer producto que el Mounstro fabrica end-to-end (DSC-CIP-006) |

### CIES — Instrumentos Financieros

| Cruza con | Tipo | Naturaleza del cruce |
|---|---|---|
| CIP | 🟡 | Acoplado en mismo dominio EPIA — probablemente es variante de CIP, no proyecto independiente |
| OMNICOM | 🟢 | Cruzado en IGCAR |

### NIAS — Biometría Anónima

| Cruza con | Tipo | Naturaleza del cruce |
|---|---|---|
| BioGuard | 🟡 | Ambos manejan muestras biológicas — pueden compartir hardware/SDK |
| Top Control PC | 🟢 | Si NIAS llega a producto, requiere identidad anónima del usuario en PC |

### BIOGUARD — Detección de drogas

| Cruza con | Tipo | Naturaleza del cruce |
|---|---|---|
| NIAS | 🟡 | Mismo dominio biotech |
| Mena Baduy | 🟢 | Producto vendible al sector salud público (campaña Mérida 2027) |

### LIKETICKETS / ticketlike.mx

| Cruza con | Tipo | Naturaleza del cruce |
|---|---|---|
| Comercialización Zona Like 313 | 🔴 | LikeTickets ES la plataforma técnica, Comercialización ES el motor de venta |
| Kukulkán 365 | 🔴 | Like-Kukulkán es producto piloto de K365 (DSC-K365-002) |
| Marketplace Muebles | 🔴 | Comparten checkout Stripe (DSC-X-002) |
| CIP | 🔴 | Comparten checkout Stripe (DSC-X-002) |
| Bot Telegram | 🟠 | Bot puede vender entradas vía Telegram (canal alterno) |
| Command Center | 🟢 | Dashboard de ventas en Command Center |

### COMERCIALIZACIÓN ZONA LIKE 313

| Cruza con | Tipo | Naturaleza del cruce |
|---|---|---|
| LikeTickets | 🔴 | Su plataforma técnica |
| Kukulkán 365 | 🔴 | El estadio donde existen las 313 butacas |
| El Monstruo Bot | 🟠 | Canal de venta directa Telegram |

### KUKULKÁN 365 / k365

| Cruza con | Tipo | Naturaleza del cruce |
|---|---|---|
| Like-Kukulkán Tickets | 🔴 | Producto comercial activo del distrito |
| El Mundo de Tata | 🟠 | Mundo de Tata es contenido narrativo del distrito |
| Mena Baduy | 🟢 | Distrito puede ser activo de campaña política |
| Roche Bobois | 🟢 | Tapetes/Mobiliario para áreas VIP del distrito |

### MENA BADUY / CRISOL-8

| Cruza con | Tipo | Naturaleza del cruce |
|---|---|---|
| Observatorio Mérida 2027 | 🔴 | Crisol-8 alimenta al Observatorio con OSINT |
| Comando Electoral Mérida 2027 | 🔴 | Mismo proyecto político, diferentes capas |
| Kukulkán 365 | 🟢 | Proyectos de Alfredo en Mérida con sinergia política |

### EL MONSTRUO BOT (Telegram)

| Cruza con | Tipo | Naturaleza del cruce |
|---|---|---|
| Command Center | 🔴 | Misma data, diferentes interfaces (Telegram vs Web) |
| El Mundo de Tata | 🔴 | Comparten Manus-Oauth (DSC-X-003) |
| LikeTickets | 🟠 | Canal de venta alterno |
| Comercialización Zona Like | 🟠 | Bot vende butacas vía Telegram |

### COMMAND CENTER

| Cruza con | Tipo | Naturaleza del cruce |
|---|---|---|
| Bot Telegram | 🔴 | Comparten Manus-Oauth (DSC-X-003) |
| Mundo de Tata | 🔴 | Comparten Manus-Oauth (DSC-X-003) |
| Simulador Universal | 🔴 | Simulador se controla desde Command Center |
| Observatorio Mérida 2027 | 🟠 | Dashboards políticos viven en Command Center |

### SIMULADOR UNIVERSAL

| Cruza con | Tipo | Naturaleza del cruce |
|---|---|---|
| Mena Baduy | 🔴 | Simula escenarios electorales para campaña 2027 |
| CIP | 🟢 | Puede simular ROI de portfolios CIP |
| El Monstruo | 🔴 | Es módulo central del orquestador |

### MARKETPLACE MUEBLES

| Cruza con | Tipo | Naturaleza del cruce |
|---|---|---|
| LikeTickets | 🔴 | Comparten checkout Stripe (DSC-X-002) |
| CIP | 🔴 | Comparten checkout Stripe + cliente que invierte y amuebla |
| Roche Bobois | 🟠 | Roche Bobois es proveedor anclaje del marketplace |
| Kukulkán 365 | 🟢 | Mobiliario para áreas comunes del distrito |

### TOP CONTROL PC / CONTROL TOTAL

| Cruza con | Tipo | Naturaleza del cruce |
|---|---|---|
| El Monstruo | 🔴 | Capa de "Manos" del Monstruo en PC del usuario |
| Bot Telegram | 🟠 | Bot puede comandar Top Control PC remotamente |
| NIAS | 🟢 | Identidad anónima del usuario en PC |

### VIVIR SANO

| Cruza con | Tipo | Naturaleza del cruce |
|---|---|---|
| BioGuard | 🟢 | Ambos en sector salud/wellness |
| CIP | 🟢 | Patrón "biblia v4.x" replicable |

### SOFTRESTAURANTAI 10X

| Cruza con | Tipo | Naturaleza del cruce |
|---|---|---|
| Marketplace Muebles | 🟢 | Mobiliario para restaurantes clientes |
| Command Center | 🟠 | Dashboard SaaS dentro del Command Center |
| El Monstruo | 🟠 | Producto vertical construido sobre el Monstruo |

### OMNICOM

| Cruza con | Tipo | Naturaleza del cruce |
|---|---|---|
| CIP, CIES, SOP, EPIA | 🟢 | Cruzados en estatuto IGCAR (DSC-X-001) |
| El Monstruo | 🟠 | Workspace Omnicom Inc usado como infra técnica de Manus desde abril 2026 |

### EL MUNDO DE TATA

| Cruza con | Tipo | Naturaleza del cruce |
|---|---|---|
| Kukulkán 365 | 🟠 | Contenido narrativo del distrito |
| Bot Telegram + Command Center | 🔴 | Comparten Manus-Oauth (DSC-X-003) |

### ROCHE BOBOIS / ALFOMBRAS YAXCHÉ

| Cruza con | Tipo | Naturaleza del cruce |
|---|---|---|
| Marketplace Muebles | 🟠 | Anclaje de proveedor |
| Kukulkán 365 | 🟢 | Mobiliario áreas VIP |

### OBSERVATORIO MÉRIDA 2027

| Cruza con | Tipo | Naturaleza del cruce |
|---|---|---|
| Mena Baduy / Crisol-8 | 🔴 | Misma operación política |
| Command Center | 🟠 | Dashboards políticos |
| Simulador Universal | 🔴 | Simulación de escenarios electorales |

---

## 🧱 Componentes Compartibles Identificados (alta prioridad)

Estos son módulos que aparecen en ≥3 proyectos. **Construirlos UNA SOLA VEZ ahorra trabajo y reduce deuda técnica:**

### 1. 🔴 **Módulo Stripe Checkout + Webhook + Confirmation**
- Usado por: **LikeTickets** (probado en producción), **Marketplace Muebles**, **CIP**
- Ya existe versión funcional en `like-kukulkan-tickets` (Railway)
- DSC: `DSC-LT-003`, `DSC-X-002`
- **Acción:** extraer de `like-kukulkan-tickets` y volverlo paquete npm interno (`@monstruo/checkout-stripe`)

### 2. 🔴 **Módulo Manus-Oauth (auth)**
- Usado por: **El Monstruo Bot**, **Command Center**, **El Mundo de Tata**, futuros proyectos web-db-user
- Scaffold ya existe en plantilla `web-db-user` de Manus
- DSC: `DSC-X-003`
- **Acción:** documentar como skill `manus-oauth-pattern`

### 3. 🟠 **Capa de Observabilidad (Supabase + Langfuse)**
- Usado por: **El Monstruo**, todos los proyectos que lleguen a Capa 1
- DSC: `DSC-MO-004`
- **Acción:** crear template de inicialización `obs-init.sh`

### 4. 🟠 **Patrón Barrido Cruzado Drive+Notion+S3**
- Usado por: **Mena Baduy**, **Discovery Forense**, futuros proyectos investigativos
- DSC: `DSC-MB-003`
- **Acción:** documentar como skill `barrido-cruzado-recursos`

### 5. 🟠 **Patrón Biblia v4.x Master Plan**
- Usado por: **Vivir Sano**, **CIP**, posible **BioGuard**
- Estructura de documento maestro con: visión, módulos, decisiones, roadmap
- **Acción:** crear plantilla `biblia-master-plan-template.md`

### 6. 🟢 **Capa de Brand Engine (Naranja Forja)**
- Usado por: **TODOS los proyectos del Monstruo**
- DSC: `DSC-MO-002`, `DSC-G-004`
- **Acción:** crear paquete `@monstruo/design-tokens` con CSS vars + Tailwind config

---

## 📋 Acciones priorizadas para Cowork

Basadas en esta matriz, Cowork debería ejecutar en orden:

1. **Extraer módulo Stripe Checkout** de `like-kukulkan-tickets` → paquete reutilizable. **Desbloquea CIP, Marketplace, futuros productos.**
2. **Crear skill `manus-oauth-pattern`** documentando el flujo. **Acelera Bot, Command Center, Mundo Tata.**
3. **Resolver decisiones pendientes CIP** (`DSC-CIP-PEND-001` y `DSC-CIP-PEND-002`) consultando los 6 sabios. **Desbloquea construcción CIP.**
4. **Procesar IGCAR** (`drive:IGCAR_Estatuto_Oficial_v2.docx`) para entender cruce OMNICOM+CIP+CIES+SOP+EPIA en una sola pieza.
5. **Crear paquete `@monstruo/design-tokens`** para que toda nueva UI nazca con identidad de marca.

---

## 🔄 Cómo se actualiza esta matriz

- **Manus** la actualiza al detectar nuevos cruces durante sesiones de discovery o diseño.
- **Cowork** la consulta antes de empezar cualquier proyecto.
- **Cualquier sabio** puede sugerir nuevos cruces al hacerle preguntas con esta matriz como contexto.

Si encuentras un cruce no listado, agrégalo como nueva fila/celda y crea el DSC correspondiente en `CAPILLA_DECISIONES/_GLOBAL/DSC-X-NNN_*.md` con tipo `cruce_inter_proyecto`.

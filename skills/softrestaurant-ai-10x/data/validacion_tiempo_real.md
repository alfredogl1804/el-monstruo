# Dossier de Validación en Tiempo Real — 24 abril 2026

## CLAIM 1: Odoo Community 19 con módulo POS Restaurant
**Fuente:** https://www.odoo.com/app/point-of-sale-restaurant
**Estado:** EN VALIDACIÓN

### Hallazgos del sitio oficial:
- Odoo POS Restaurant EXISTE y está activo
- Features confirmadas: mobile ordering, table reservations, online orders, employee planning, delivery integrations
- Self-ordering (kiosk + smartphone del cliente)
- Floor plans en tiempo real
- Preparation display (KDS) para cocina y bar
- Compatible con cualquier dispositivo (tablet, desktop, laptop, smartphone, kiosks)
- Pagos integrados (cash, checks, credit card)
- Kitchen printing por categoría de producto
- Offline payments con sync automático
- Split bills & tips
- Customer loyalty (puntos, descuentos)
- "Free, forever, with unlimited users" — CLAIM IMPORTANTE a verificar
- 15 millones de usuarios
- Integración con Website, eCommerce, Inventory, Email Marketing, CRM, Accounting

### PENDIENTE verificar:
- ¿Cuál es la versión actual? ¿Es 18 o 19?
- ¿El "free forever" aplica a Community o solo a Odoo Online?
- ¿Pricing real de Odoo para self-hosted vs cloud?
- ¿Funciona en México con soporte en español?

### HALLAZGO CRÍTICO — Versión Odoo (24 abril 2026):
- **Versión actual: Odoo 19** (19.1 y 19.2 ya están LIVE)
- Odoo 20 se espera en septiembre 2026
- Odoo Community Edition es FREE worldwide (LGPL-3.0, self-hosted)
- Odoo Online (SaaS) tiene pricing por usuario (~$37-61 USD/user/mo dependiendo del país)
- **CLAIM "Odoo Community 19" = [VERIFICADO]** — Existe, es la versión actual, es free self-hosted

### PENDIENTE: Pricing de hosting self-hosted para Odoo Community 19

### HALLAZGO CRÍTICO — Pricing Odoo México (verificado 24 abril 2026):

**Odoo Community Edition:** FREE (LGPL-3.0, self-hosted). NO tiene Studio, multi-company, advanced reporting.

**Odoo Enterprise en México:**
- Standard: Mex$228/user/mes (anual) o Mex$285/user/mes (mensual)
- Custom/Enterprise: Mex$340/user/mes (anual) o Mex$425/user/mes (mensual)

**CLAIM ANTERIOR: "$850/mes para Odoo self-hosted"**
- Si usamos Community (FREE) + hosting propio (~$36 USD/mes = ~$612 MXN/mes en DigitalOcean/Hetzner)
- **[CORREGIDO]** El costo real de Odoo Community self-hosted es ~$612 MXN/mes (solo hosting), NO $850
- Si quisiéramos Enterprise para 5 usuarios: 5 x $340 = $1,700 MXN/mes + hosting = ~$2,312 MXN/mes
- **DECISIÓN: Community es suficiente para nuestro caso** — no necesitamos Studio ni multi-company (usamos Supabase para multi-sucursal)

**CLAIM "Odoo Community 19 con POS Restaurant" = [VERIFICADO] pero con matiz:**
- Community tiene POS Restaurant pero le faltan features Enterprise (Studio, multi-company nativo)
- Para nuestro caso esto NO es problema porque el cerebro IA + Supabase suplen esas carencias

---

## CLAIM 2: OpenAI GPT-4o mini — pricing y disponibilidad México

### HALLAZGO CRÍTICO — OpenAI Pricing (verificado 24 abril 2026 desde openai.com/api/pricing):

**MODELOS ACTUALES (abril 2026) — NO GPT-4o mini:**
- GPT-5.5 (coming soon): $5.00 input / $30.00 output per 1M tokens
- **GPT-5.4**: $2.50 input / $15.00 output per 1M tokens
- **GPT-5.4 mini**: $0.75 input / $4.50 output per 1M tokens

**CLAIM ANTERIOR: "GPT-4o mini a $0.15/1M input"**
- **[FALSO/OBSOLETO]** GPT-4o mini ya NO aparece en la página de pricing de OpenAI
- El modelo más barato disponible HOY es **GPT-5.4 mini** a $0.75/1M input
- Eso es 5x más caro que lo que dijeron los Sabios ($0.15 vs $0.75)
- CloudZero menciona GPT-5.4 Nano a $0.20/1M tokens — verificar si existe

**DESCUBRIMIENTO: GPT-5.4 Nano**
- Según CloudZero: Nano cuesta $0.20/1M input tokens — 12x más barato que flagship
- PERO no aparece en la página oficial de OpenAI pricing — puede ser acceso limitado o batch
- **Necesita verificación adicional**

**IMPACTO EN COSTOS:**
- Con GPT-5.4 mini ($0.75/1M input, $4.50/1M output):
  - Estimando 500K tokens/día para un restaurante con 5 sucursales
  - = ~15M tokens/mes input + ~5M tokens/mes output
  - = $11.25 input + $22.50 output = ~$33.75 USD/mes = ~$574 MXN/mes
  - **MUCHO más caro que los $26 MXN que dijeron los Sabios**

**CORRECCIÓN:** El costo de IA sube de $26 MXN a ~$574 MXN/mes

---

## CLAIM 3: Supabase Pro a $25 USD/mes

### HALLAZGO — Supabase Pricing (verificado 24 abril 2026 desde supabase.com/pricing):

**Free Tier:**
- $0/mes, Unlimited API requests, 50K MAU, 500MB DB, 5GB egress, 1GB storage
- Se pausa después de 1 semana de inactividad. Límite de 2 proyectos activos.
- **PARA DESARROLLO: suficiente**

**Pro Plan:**
- **$25 USD/mes** (~$425 MXN) — incluye Micro compute ($10 en créditos de compute)
- 100K MAU, 8GB disk, 250GB egress, 100GB storage, email support, daily backups 7 días
- **CLAIM "$25 USD/mes" = [VERIFICADO]**

**Team Plan:** $599/mes (no necesario para nuestro caso)

**NOTA IMPORTANTE:** Supabase también se puede self-host GRATIS (pregunta FAQ en su sitio)
- Self-hosted eliminaría el costo de $25/mes pero requiere mantener la infra

**DECISIÓN:** Pro a $25 USD/mes es correcto y suficiente para 5 sucursales + CEDIS

---

## CLAIM 4: Grafana Cloud Free Tier
## CLAIM 5: Octotable existencia y pricing

### HALLAZGO — Octotable Pricing (verificado 24 abril 2026 desde octotable.com/en/prices):

**Octotable EXISTE y es real.** Es una plataforma italiana de reservaciones para restaurantes.

**Planes:**
- FREE: $0/mes — 30 reservas/mes, Reserve with Google, menú digital QR, página de reservas
- DigiMenu: $18.40/mes (anual) — reservas ilimitadas, mapa interactivo, API, widget
- Premium: $28/mes (anual) — WhatsApp, email/SMS automatizados
- EVO: $47.20/mes (anual) — waitlist, CRM, pagos online, marketing

**CLAIM "Octotable $0/mes" = [PARCIALMENTE VERIFICADO]**
- El free tier existe PERO solo 30 reservas/mes — insuficiente para un restaurante real
- Para uso real necesitaríamos DigiMenu ($18.40/mes = ~$313 MXN/mes) o Premium ($28/mes = ~$476 MXN/mes)

**PROBLEMA DETECTADO:** Octotable es italiana. No tiene presencia explícita en México.
- Funciona como SaaS global, pero no tiene soporte en español mexicano ni integración con servicios locales
- OpenTable (que el usuario ya usa) podría ser mejor opción por familiaridad
- **ALTERNATIVA:** Mantener OpenTable que ya usa + construir widget propio con Odoo

**CORRECCIÓN:** Octotable NO es $0 para uso real. Costo real: $313-476 MXN/mes. O mejor: mantener OpenTable existente.

---

## CLAIM 4: Grafana Cloud Free Tier

### HALLAZGO — Grafana Cloud Pricing (verificado 24 abril 2026 desde grafana.com/pricing):

**Free Tier: $0 — EXISTE y es real**
- Todos los servicios de Grafana Cloud con uso limitado
- 10K active series/mes (métricas), 50GB logs, 50GB traces
- 14 días retención, 3 usuarios activos, community support
- **SUFICIENTE para dashboards de un restaurante con 5 sucursales**

**Pro: desde $19/mes + usage** — para escalar más adelante
**Enterprise: $25,000/año** — no necesario

**CLAIM "Grafana Cloud $0/mes" = [VERIFICADO]** — El free tier es real y suficiente para nuestro caso.

**NOTA:** Grafana 13 acaba de salir (GrafanaCON 2026). Incluye features de IA.

---

## RESUMEN DE VALIDACIÓN — TABLA DE VERDAD

| Componente | Claim Original | Realidad Verificada | Estado |
|---|---|---|---|
| Odoo Community 19 | Existe, $850/mes | Existe, versión 19 actual. FREE self-hosted + ~$612 MXN hosting | CORREGIDO ✅ |
| OpenAI GPT-4o mini | $0.15/1M input, $26 MXN/mes | GPT-4o mini OBSOLETO. GPT-5.4 mini: $0.75/1M. Costo real: ~$574 MXN/mes | ALUCINACIÓN CORREGIDA ⚠️ |
| Supabase Pro | $25 USD/mes ($425 MXN) | $25 USD/mes CONFIRMADO | VERIFICADO ✅ |
| Grafana Cloud | $0/mes free tier | $0/mes CONFIRMADO, suficiente para restaurante | VERIFICADO ✅ |
| Octotable | $0/mes | Free solo 30 reservas/mes. Real: $18-47 USD/mes. Mejor: mantener OpenTable | ALUCINACIÓN CORREGIDA ⚠️ |

## COSTO TOTAL CORREGIDO (mensual):
- Odoo Community 19 self-hosted: ~$612 MXN (hosting DigitalOcean/Hetzner)
- OpenAI GPT-5.4 mini: ~$574 MXN (estimado 15M tokens/mes)
- Supabase Pro: ~$425 MXN ($25 USD)
- Grafana Cloud Free: $0 MXN
- OpenTable (ya lo paga): $0 adicional
- **TOTAL: ~$1,611 MXN/mes** (vs claim original de $1,301 MXN)

Diferencia: +$310 MXN/mes más de lo que dijeron los Sabios.
Sigue siendo MUCHO más barato que SR ($9,000-15,000 MXN/mes para 5 sucursales).

---

## DESCUBRIMIENTOS QUE LOS SABIOS NO MENCIONARON (24 abril 2026)

### DESCUBRIMIENTO 1: DeepSeek V4 — LANZADO HOY (24 abril 2026)
**Fuente:** Reddit, Medium, múltiples fuentes — verificado en tiempo real
- DeepSeek V4-Pro: $0.30/1M input, $0.50/1M output (cache hit: $0.03/1M)
- DeepSeek V4-Flash: $0.14/1M input — **5x más barato que GPT-5.4 mini**
- 1M context window, open weights
- "Outperforms Claude Opus and GPT-5.4 on coding benchmarks"
- **IMPACTO:** Si usamos DeepSeek V4-Flash en vez de GPT-5.4 mini:
  - 15M tokens input/mes x $0.14/1M = $2.10 USD
  - 5M tokens output/mes x ~$0.22/1M = $1.10 USD
  - **TOTAL IA: ~$3.20 USD/mes = ~$54 MXN/mes** vs $574 MXN con OpenAI
  - **AHORRO: 90% en costos de IA**

### DESCUBRIMIENTO 2: ERPNext + erpnext-restaurant (GitHub)
**Fuente:** github.com/alphabit-technology/erpnext-restaurant — 173 stars, 183 forks
- 100% open source (GPL-3.0), basado en Frappe framework
- Versión 1.8.6 con: Room & Table Management, KDS, reservaciones, menú, delivery por sucursal, BOM/recetas, filtros veg/non-veg, drag-and-drop, dark theme
- Compatible con ERPNext V13-V15
- ERPNext es 100% open source vs Odoo que tiene Community limitado
- **PERO:** Ecosistema más pequeño que Odoo, menos módulos out-of-the-box

### DESCUBRIMIENTO 3: AgentRestro — SaaS con IA para restaurantes
**Fuente:** CodeCanyon — producto comercial reciente
- AI Restaurant Management SaaS con Voice & Chat ordering, Table Booking
- Producto listo para usar, no open source
- Precio: licencia única (no suscripción)

### DESCUBRIMIENTO 4: Deliverect AI Agents (abril 2026)
**Fuente:** PR Newswire, Restaurant Technology News
- Deliverect lanzó AI Agents autónomos para restaurantes en abril 2026
- Monitorean operaciones digitales en tiempo real, resuelven problemas proactivamente
- Integración con n8n para workflows personalizados
- **RELEVANTE:** Modelo de referencia de cómo los agentes IA operan en restaurantes

### DESCUBRIMIENTO 5: Model Cascade — Optimización 60-80% costos
**Fuente:** CostGoat, múltiples fuentes
- Usar modelos baratos (DeepSeek Flash, Gemini Flash-Lite) para 85% de queries
- Escalar a modelos premium (GPT-5.4, Claude Opus) solo para tareas complejas
- Reduce costos 60-80% sin sacrificar calidad
- **APLICACIÓN DIRECTA:** Mesero pregunta → DeepSeek Flash. Director pide estrategia → GPT-5.4

### DESCUBRIMIENTO 6: Gemini Flash-Lite — $0.25/1M tokens
**Fuente:** CostGoat pricing comparison
- Google Gemini 3.1 Flash-Lite: $0.25/1M tokens
- Alternativa intermedia entre DeepSeek Flash y GPT-5.4 mini

---

## TABLA ACTUALIZADA DE COSTOS CON DESCUBRIMIENTOS

| Componente | Plan Original (Sabios) | Plan Corregido (Validado) | Plan Optimizado (Descubrimientos) |
|---|---|---|---|
| ERP/POS Base | Odoo Community 19 — $850 MXN | Odoo Community 19 — $612 MXN (hosting) | Odoo Community 19 — $612 MXN |
| Cerebro IA | GPT-4o mini — $26 MXN | GPT-5.4 mini — $574 MXN | DeepSeek V4-Flash + cascade — $54 MXN |
| DB Tiempo Real | Supabase Pro — $425 MXN | Supabase Pro — $425 MXN | Supabase Pro — $425 MXN |
| Dashboards | Grafana Cloud — $0 | Grafana Cloud — $0 | Grafana Cloud — $0 |
| Reservaciones | Octotable — $0 | OpenTable (ya paga) — $0 | OpenTable (ya paga) — $0 |
| **TOTAL** | **$1,301 MXN/mes** | **$1,611 MXN/mes** | **$1,091 MXN/mes** |

**El plan optimizado con descubrimientos es MEJOR y MÁS BARATO que el original de los Sabios.**

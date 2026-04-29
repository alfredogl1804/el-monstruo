# PLAN DE ENSAMBLAJE V8 (DEFINITIVO Y VALIDADO EN TIEMPO REAL)
## SoftRestaurantAI 10x — Abril 2026

**Tesis Central:** La IA exitosa en restaurantes en 2026 opera *detrás de escena* (modelo Starbucks Deep Brew). No reemplaza la experiencia humana, la optimiza invisiblemente.

**Arquitectura Ganadora:** URY + ERPNext (Esqueleto) + DeepSeek/GPT-5.4 (Cerebro) + Supabase (Memoria)

---

## 1. LOS 5 COMPONENTES CORE (Costos Reales MXN)

| Componente | Herramienta | Rol en el Sistema | Costo Mensual |
|---|---|---|---|
| **Esqueleto ERP** | **URY + ERPNext** | POS mobile-first, KDS (cocina), Inventario, Compras, HR, Mesas. Open source, específico para restaurantes. | $612 MXN (Self-hosted) |
| **Cerebro IA** | **DeepSeek V4-Flash + GPT-5.4** | Arquitectura Cascade: 85% queries baratas, 15% complejas. 5 agentes IA (reservas, menú, analytics, billing, team). | ~$150 MXN (API usage) |
| **Memoria/DB** | **Supabase Pro** | Base de datos en tiempo real, Auth multi-sucursal, Edge Functions. | $425 MXN ($25 USD) |
| **Dashboards** | **Grafana Cloud** | Visualización en tiempo real para Directivos. | $0 (Free Tier) |
| **Reservaciones** | **OpenTable API** | Integración directa con el sistema que el usuario ya usa. | $0 (Costo ya asumido) |
| **TOTAL** | | **Sistema 10x superior a SoftRestaurant** | **$1,187 MXN / mes** |

*(Nota: SoftRestaurant 12 PRO cuesta entre $9,000 y $15,000 MXN/mes para 5 sucursales).*

---

## 2. POR QUÉ URY > ODOO (Validación Módulo por Módulo)

La investigación profunda en GitHub reveló que Odoo es demasiado genérico. URY (basado en ERPNext) es la base perfecta:
1. **POS diseñado para restaurantes:** Mobile-first para meseros, no retail.
2. **MOSAIC KDS incluido:** Pantallas de cocina interactivas (Odoo no tiene).
3. **Alertas Operativas (Red Flags):** Detecta retrasos en cocina automáticamente.
4. **Multi-sucursal nativo:** P&L diario por sucursal.
5. **Producción Real:** Ya opera en 10+ sucursales de 6 marcas.

---

## 3. LOS 5 AGENTES IA (La capa de inteligencia)

Inspirado en el modelo exitoso de Aedan Rose, construiremos 5 agentes IA que operan sobre URY:

1. **Agente de Reservas (Hostess AI):** Se conecta a OpenTable. Optimiza la rotación de mesas (table turnover) basándose en tiempos históricos de consumo.
2. **Agente de Menú (Chef AI):** Analiza ventas y costos (BOM) en tiempo real. Sugiere eliminar platillos no rentables y crear promociones para ingredientes próximos a caducar (modelo Chipotle Autocado).
3. **Agente de Analytics (Director AI):** Detecta anomalías (ej. "Las ventas de bebidas cayeron 15% en la mesa 4 hoy"). Envía alertas proactivas, no solo reportes pasivos.
4. **Agente de Facturación/Cobro (Cajero AI):** Detecta fraudes (ej. excesivas cancelaciones o modificaciones en KOTs).
5. **Agente de Equipo (Gerente AI):** Predice la demanda (demand forecasting) basándose en clima, eventos y ventas históricas para optimizar los turnos (modelo Nesto).

---

## 4. MAPEO DE LOS 11 USUARIOS

| Usuario | Experiencia Actual (SR) | Experiencia 10x (URY + IA) |
|---|---|---|
| **Mesero** | Terminal fija, toma órdenes en papel. | Toma órdenes en móvil (URY POS), la IA sugiere upselling basado en el perfil del cliente. |
| **Cocinero** | Tickets de papel o KDS básico. | MOSAIC KDS interactivo. La IA balancea la carga de la cocina (kitchen load balancing). |
| **Cajero** | Cobra y cierra turnos manualmente. | Reconciliación automática. La IA detecta anomalías en cancelaciones. |
| **Hostess** | Asigna mesas a ojo. | El Agente de Reservas sugiere la mejor mesa para optimizar la rotación. |
| **Gerente** | Revisa reportes al final del día. | Recibe alertas en tiempo real ("Mesa 5 lleva 45 min sin ordenar"). |
| **Dir. Comercial** | Analiza ventas mensuales. | El Agente de Analytics sugiere promociones para días de baja demanda. |
| **Inventarios** | Captura mermas a mano. | La IA predice necesidades de compra basándose en pronóstico de demanda. |
| **Compras** | Llama a proveedores. | Órdenes de compra automáticas en ERPNext cuando el stock llega al mínimo. |
| **Relaciones P.** | Envía emails masivos. | Segmentación automática ("Invita a clientes que no han venido en 30 días"). |
| **Cliente** | Espera a que lo atiendan. | Experiencia hiper-personalizada (la IA recuerda sus favoritos). |
| **Dir. General** | Ve dashboards estáticos. | Recibe insights estratégicos accionables ("Cierra el salón B los martes"). |

---

## 5. PLAN DE EJECUCIÓN (Sin MVP, Todo de un jalón)

1. **Semana 1: Infraestructura Base**
   - Levantar servidor (Railway/DigitalOcean).
   - Instalar ERPNext + URY (módulos Core, POS, MOSAIC, PULSE).
   - Configurar base de datos Supabase.

2. **Semana 2: Configuración Operativa**
   - Cargar catálogo de productos (Menú y BOM).
   - Configurar mesas, salones y usuarios (Roles y Permisos).
   - Configurar impresoras/KDS.

3. **Semana 3: Desarrollo de la Capa IA (Los 5 Agentes)**
   - Conectar URY a Supabase (sincronización en tiempo real).
   - Desarrollar los 5 agentes usando DeepSeek V4-Flash + GPT-5.4.
   - Implementar el sistema de alertas proactivas.

4. **Semana 4: Integraciones y Dashboards**
   - Conectar OpenTable API.
   - Construir dashboards directivos en Grafana.
   - Pruebas E2E (End-to-End) en todas las sucursales simuladas.

---

## 6. CUMPLIMIENTO DE TUS 5 PRINCIPIOS

1. **Menos es Más:** Solo 5 componentes. URY consolida 15 módulos en uno.
2. **Facilidad > Potencia:** La IA es *invisible*. El mesero solo usa una app móvil simple; la IA hace los cálculos pesados en el backend.
3. **No inventar la rueda:** Usamos URY (ERPNext), un repo open source ya probado en producción con 10+ sucursales.
4. **No crear desde cero:** Código nuevo estimado < 15% (solo la capa de agentes IA y la integración con Supabase).
5. **Oferta y Demanda:** El sistema predice la demanda y ajusta inventarios/staffing naturalmente.

---
**Documento Final V8 generado por investigación profunda en GitHub y análisis de benchmarks reales 2026.**

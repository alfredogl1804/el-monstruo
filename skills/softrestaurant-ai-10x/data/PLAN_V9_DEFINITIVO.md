# Plan V9 Definitivo — SoftRestaurantAI 10x
**Fecha:** 24 abril 2026
**Validación:** Brutal (5 investigaciones profundas, gates anti-pereza, 348KB de evidencia)

---

## 1. El Esqueleto: URY + ERPNext (Validado)
La Investigación 1 (Autopsia de URY) confirmó que Odoo no era la mejor opción. El esqueleto ganador es **URY + ERPNext**.

**Datos Duros del Repo Real (`ury-erp/ury`):**
- **35 Doctypes Personalizados:** Cubre el 80% de los 19 módulos de SR (POS, KDS, Menú, Mesas, P&L, COGS).
- **Frontend Moderno:** React 19 para POS (mobile-first) y Vue 3 para KDS (Mosaic).
- **Integración Nativa:** Crea facturas POS en ERPNext y se integra con listas de precios y clientes.
- **Preparado para IA:** El repo incluye `AGENTS.MD` y `CLAUDE.MD`, lo que demuestra que ya tienen arquitectura para agentes IA.
- **En Producción:** Operando en 10+ outlets por 10 meses.

**Decisión V9:** Clonar URY y usarlo como base. No construir de cero.

## 2. La Capa de IA: 5 Agentes Especializados (Refinado)
La Investigación 2 y la consulta a los Sabios revelaron que la arquitectura "Invisible" es la ganadora en 2026.

**Los 5 Agentes (Framework: LangGraph):**
1. **Hostess AI:** Reservas (OpenTable), predicción de demanda.
2. **Chef AI:** Optimización de KDS, merma, balanceo de carga.
3. **Director AI:** Dashboards (Grafana), anomalías financieras.
4. **Inventario AI:** Compras predictivas basadas en COGS.
5. **Servicio AI:** Upselling silencioso (sugerencias en el POS del mesero).

**Costo de IA (DeepSeek V4-Flash + GPT-5.4 Cascade):**
- 500 llamadas/día × 30 días × 2000 tokens = ~30M tokens/mes.
- DeepSeek V4-Flash ($0.14/1M): ~$4.20 USD ($71 MXN).
- GPT-5.4 (15% de queries complejas): ~$15 USD ($255 MXN).
- **Total IA:** ~$326 MXN/mes para 5 sucursales.

## 3. Costos Reales y Completos (Corregido)
El V8 fue optimista ($1,187 MXN). El V9 incluye TODO el TCO (Total Cost of Ownership) para 5 sucursales.

| Componente | Costo Mensual (MXN) | Justificación |
|---|---|---|
| **Hosting ERPNext** | $850 | Frappe Cloud (Plan Standard) o DigitalOcean 4GB RAM. |
| **Base de Datos** | $425 | Supabase Pro (Auth, Realtime). |
| **Cerebro IA** | $326 | DeepSeek V4-Flash + GPT-5.4. |
| **Dashboards** | $0 | Grafana Cloud (Free tier cubre 10k series). |
| **Reservas** | $0 | OpenTable (Ya pagado por el restaurante). |
| **Mantenimiento/Backups** | $500 | Automatizado, AWS S3 para backups. |
| **Dominio/SSL** | $50 | Prorrateado mensual. |
| **TOTAL V9** | **$2,151 MXN** | **Aún 4x-7x más barato que SoftRestaurant ($9k-$15k).** |

## 4. Timeline Realista (Ajustado)
Los Sabios (Claude, Gemini, Grok) fueron unánimes: 4 semanas es imposible para un solo developer, incluso con Cursor. El riesgo de fracaso es altísimo sin un MVP.

**Timeline V9 (8 Semanas, Enfoque Iterativo):**
- **Semana 1-2:** Setup Frappe Cloud, instalación ERPNext + URY, configuración de 1 sucursal piloto.
- **Semana 3-4:** Desarrollo de Agentes IA (LangGraph) e integración con API de URY (`ury_pos/api.py`).
- **Semana 5-6:** Pruebas en sucursal piloto (Shadow Mode — la IA sugiere, el humano decide).
- **Semana 7-8:** Rollout a las 5 sucursales, Dashboards Grafana, ajuste fino.

## 5. El Mayor Riesgo (Identificado por los Sabios)
El consenso de los Sabios (especialmente Gemini y Grok) destacó un riesgo crítico que ignoramos: **La adopción del personal.**
Si la IA sugiere algo (ej. "Mesa 4 necesita atención") y el mesero la ignora porque la interfaz es confusa, el sistema fracasa, por muy potente que sea el backend.

**Mitigación V9:**
La IA será "Invisible". No habrá una pantalla separada de "IA". Las sugerencias aparecerán directamente en el POS React 19 de URY como notificaciones sutiles o botones de 1 clic.

---
**CONCLUSIÓN:** El Plan V9 es ejecutable HOY. Tenemos el repo exacto (`ury-erp/ury`), los costos reales ($2,151 MXN), el framework de IA (LangGraph) y un timeline realista (8 semanas).

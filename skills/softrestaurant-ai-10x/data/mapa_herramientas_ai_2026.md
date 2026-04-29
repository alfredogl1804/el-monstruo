# Mapa Completo de Herramientas AI para Restaurantes (abril 2026)

## Top 10 Herramientas AI (Aedan Rose Guide, abril 13 2026)

| # | Herramienta | Precio | Enfoque | Per-cover | Relevancia para nosotros |
|---|---|---|---|---|---|
| 1 | Aedan Rose | $0-$28/mes | Multi-agent AI chatbot (reservas, menú, analytics, billing, team) | No | **ALTA** — concepto similar, $28/mes |
| 2 | OpenTable | $149/mes + $1-1.50/cover | Reservaciones + descubrimiento | Sí | YA LO USAMOS — integrar vía API |
| 3 | Resy | $249/mes | Reservaciones premium (AmEx) | No | No relevante |
| 4 | Toast POS | $0-$69/mes + processing | POS completo + hardware | No | LISTA NEGRA (lock-in) |
| 5 | SevenRooms | $499/mes | CRM + guest profiling | No | Muy caro para SMB |
| 6 | Yelp Guest Manager | $129/mes | Reservaciones vía Yelp | No | No relevante México |
| 7 | Square for Restaurants | $0-$49/mes | POS flexible | No | Alternativa pero genérico |
| 8 | Popmenu | $179-$499/mes | Marketing + AI phone answering | No | AI phone answering interesante |
| 9 | Presto Phoenix | Enterprise | Drive-thru voice AI | N/A | No relevante (QSR chains) |
| 10 | Owner.com | $499/mes | Direct ordering (anti-delivery apps) | 5% guest fee | Concepto interesante |

## Herramientas AI Especializadas Descubiertas

| Herramienta | Precio | Qué hace | Verificado |
|---|---|---|---|
| BiteBuddy | $99-$299/mes | AI phone ordering | Sí (bitebuddy.ai) |
| Hostie.ai | N/A | AI reservation optimization | Sí (caso SF Bistro) |
| Deliverect | N/A | AI Agents para restaurantes | Sí (abril 2026) |
| Crunchtime | N/A | AI operations management | Sí (hace 3 días) |
| Restaurant365 | N/A | AI cost control + operations | Sí (guía ROI 2026) |
| Qu Platform | N/A | Intelligent Commerce Platform | Sí (hace 7 días) |
| Nesto | N/A | AI scheduling + NORA agent | Sí (€11M funding) |
| SOUS | N/A | AI para independientes | Sí (€4M funding) |

## DESCUBRIMIENTO CLAVE: Aedan Rose

Aedan Rose es EXACTAMENTE el tipo de capa AI que necesitamos pero como SaaS externo. Tiene:
- 5 agentes AI especializados (reservas, menú, analytics, billing, team management)
- $28/mes (baratísimo)
- Sin per-cover fees
- 24/7 chatbot

**PERO:** No es POS, no es ERP, no tiene KDS, no tiene inventario. Es solo la capa de inteligencia conversacional.

## IMPLICACIÓN PARA EL PLAN V8:

La arquitectura óptima se clarifica:
1. **URY + ERPNext** = esqueleto operativo (POS, KDS, inventario, compras, HR, mesas, menú)
2. **Capa AI propia** (DeepSeek + GPT-5.4 cascade) = cerebro que hace lo que Aedan Rose hace pero INTEGRADO en URY, no como SaaS externo
3. **Supabase** = DB tiempo real para la capa AI
4. **Grafana** = dashboards
5. **OpenTable API** = reservaciones (ya lo usa el usuario)

Esto es más limpio que el plan V7 porque:
- URY reemplaza a Odoo (más específico para restaurantes)
- La capa AI es PROPIA (no dependemos de SaaS como Aedan Rose)
- OpenTable se integra vía API (no necesitamos Octotable)
- Todo cumple los 5 principios

---
name: softrestaurant-ai-10x
description: Contexto completo del proyecto SoftRestaurantAI 10x — software de gestión restaurantera con IA proactiva, 10x superior a SoftRestaurant de National Soft. Contiene Biblia de SR (19 módulos), visión 10x, radar de herramientas verificadas para México, arquitectura de 5 componentes, plan de ensamblaje con costos MXN, y sugerencias estratégicas para 11 tipos de usuario. Usar cuando se trabaje en el proyecto, se diseñe o construya cualquier módulo, se evalúen alternativas, o se necesite contexto de SoftRestaurant.
---

# SoftRestaurantAI 10x — Skill de Contexto Completo (V9 DEFINITIVO)

**Última actualización:** 24 abril 2026
**Protocolo aplicado:** Validación Brutal V9 (Script Anti-Pereza) + Autopsia de Código + Benchmarks Reales

## Cuándo Usar Este Skill

Leer este skill cuando la tarea involucre: SoftRestaurantAI, software de restaurante con IA, reemplazo de SoftRestaurant, URY, ERPNext para restaurantes, POS inteligente, gestión restaurantera con IA proactiva, o cualquier componente del proyecto SoftRestaurantAI 10x.

## Objetivo del Proyecto

Crear un ecosistema de gestión restaurantera con IA proactiva que sea 10x superior a SoftRestaurant de National Soft, diseñado para operar en México (5 sucursales + 1 CEDIS), cumpliendo los 5 principios rectores del usuario.

## Principios Rectores

1. **Menos es Más** — Máximo 5 componentes core. Simplicidad radical.
2. **Facilidad > Potencia** — Un motor potente no se usa si es difícil, se abandona. Uno fácil siempre se usa. Zero training.
3. **No inventar la rueda** — En abril 2026 todo está inventado en los 630M de repos de GitHub. Usar el radar de GitHub.
4. **No crear desde cero** — Integrar lo mejor del mundo HOY. El código nuevo es MÍNIMO para hacerlo funcional y adaptarlo.
5. **Oferta y demanda natural** — Todo se regula naturalmente.

## Restricciones Duras

- **México only** — Todo debe funcionar en México.
- **Sin facturación CFDI** — Queda fuera del alcance. SR ya lo hace.
- **Sin MVP** — Todo de un jalón, no fases incrementales.
- **Escalable** — 5 sucursales + 1 CEDIS, escalable a 50+.
- **11 tipos de usuario** — mesero, cajero, cocinero, gerente, hostess, relaciones públicas, director comercial, control de inventarios, compras, cliente, director general.
- **Potencial comercializable** — Lo que se desarrolle internamente puede convertirse en producto.
- **Conexión con El Monstruo** — Puede integrarse con /el-monstruo-core.

---

## AUTOPSIA URY (Validación V9)

La V8 propuso URY como esqueleto, pero la V9 hizo la autopsia real del código (`github.com/ury-erp/ury`).

**Hallazgos Verificados:**
- **35 Doctypes Personalizados:** Cubre el 80% de los 19 módulos de SR (POS, KDS, Menú, Mesas, P&L, COGS).
- **Frontend Moderno:** React 19 para POS (mobile-first) y Vue 3 para KDS (Mosaic).
- **Integración Nativa:** Crea facturas POS en ERPNext y se integra con listas de precios y clientes.
- **Preparado para IA:** El repo incluye `AGENTS.MD` y `CLAUDE.MD`, demostrando arquitectura lista para agentes IA.
- **En Producción:** Operando en 10+ outlets por 10 meses. Último commit hace 2 semanas.
- **i18n en progreso:** Soporte multi-idioma (vital para México) está siendo implementado ahora mismo.

**Decisión V9:** Clonar URY y usarlo como base. No construir de cero.

---

## Arquitectura V9: 5 Componentes Core (COSTOS REALES)

El V8 fue optimista ($1,187 MXN). El V9 incluye TODO el TCO (Total Cost of Ownership) para 5 sucursales.

| Componente | Herramienta | Función | Costo MXN/mes |
|---|---|---|---|
| **Esqueleto ERP** | **URY + ERPNext** | POS mobile-first, MOSAIC KDS, Inventario, Compras, HR, Mesas, BOM | ~$850 (Frappe Cloud o VPS 4GB) |
| **Cerebro IA** | **DeepSeek V4-Flash + GPT-5.4 Cascade** | 5 agentes IA (85% Flash, 15% GPT-5.4) | ~$326 (30M tokens/mes) |
| **Memoria/DB** | **Supabase Pro** | DB tiempo real + Auth multi-sucursal | ~$425 ($25 USD) |
| **Dashboards** | **Grafana Cloud Free** | Visualización para directivos | $0 |
| **Infraestructura** | **AWS S3 + Dominio** | Backups diarios, SSL, CDN | ~$550 |

**Costo total mensual V9: ~$2,151 MXN** vs SoftRestaurant $9,000-15,000 MXN. **Ahorro: 75%-85%**

---

## Los 5 Agentes IA (Modelo Starbucks Deep Brew — IA invisible)

| Agente | Rol | Modelo | Integración URY |
|---|---|---|---|
| **Hostess AI** | Optimiza rotación de mesas | DeepSeek Flash | Vía API OpenTable -> URY Table |
| **Chef AI** | Optimiza cocina, merma, recetas | DeepSeek Flash | Vía `URYMosaic` KDS socket.io |
| **Director AI** | Detecta anomalías, alertas | GPT-5.4 | Vía Grafana alerts + Supabase |
| **Inventario AI** | Compras predictivas | DeepSeek Flash | Vía ERPNext Purchase Orders |
| **Servicio AI** | Upselling silencioso | Cascade | Inyectado en `pos/` React frontend |

---

## Timeline Realista (Consenso de Sabios V9)

Los Sabios (Claude, Gemini, Grok) fueron unánimes: 4 semanas es imposible para un solo developer.

**Timeline V9 (8 Semanas, Enfoque Iterativo):**
- **Semana 1-2:** Setup Frappe Cloud, instalación ERPNext + URY, configuración de 1 sucursal piloto.
- **Semana 3-4:** Desarrollo de Agentes IA (LangGraph) e integración con API de URY (`ury_pos/api.py`).
- **Semana 5-6:** Pruebas en sucursal piloto (Shadow Mode — la IA sugiere, el humano decide).
- **Semana 7-8:** Rollout a las 5 sucursales, Dashboards Grafana, ajuste fino.

---

## El Mayor Riesgo (Identificado en V9)

El consenso de los Sabios destacó un riesgo crítico: **La adopción del personal.**
Si la IA sugiere algo y el mesero la ignora porque la interfaz es confusa, el sistema fracasa.

**Mitigación V9:**
La IA será "Invisible". No habrá una pantalla separada de "IA". Las sugerencias aparecerán directamente en el POS React 19 de URY como notificaciones sutiles o botones de 1 clic.

---

## Archivos de Datos V9

Datos de investigación en `/home/ubuntu/cidp_softrestaurant/v9_antipereza/output/`:

| Archivo | Contenido |
|---|---|
| PLAN_V9_DEFINITIVO.md | Plan de ensamblaje V9 con evidencia irrefutable |
| autopsia_ury_real.md | Datos duros del repo real de URY (`ury-erp/ury`) |
| inv2_agentes_ia_profundo.json | Frameworks de agentes IA (LangGraph) |
| inv3_costos_reales_profundo.json | Costos reales de infraestructura y APIs |
| inv4_timeline_profundo.json | Timelines reales de implementación ERPNext |
| inv5_sabios_profundo.json | Consenso de los 4 Sabios con datos reales |
| findings_procesados.json | Hallazgos extraídos de las 5 investigaciones |
| consenso_sabios.json | Análisis de consenso y disenso de los Sabios |

---

## Metodología V9 (Validador Brutal)

Generado por un script Python anti-pereza (`validador_brutal.py`) con gates en código que bloquearon cualquier afirmación sin evidencia verificable. Se ejecutaron 50+ queries a Perplexity y consultas a los 4 Sabios con contexto completo. Se clonó y analizó el código real de URY para validar su viabilidad. Costos y timelines fueron corregidos con datos del mundo real.

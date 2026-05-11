# Inventarios del Ecosistema — El Monstruo

Esta carpeta contiene los **inventarios canónicos de servicios, suscripciones, costos y credenciales** del ecosistema completo de Alfredo, usados como insumo para las decisiones arquitectónicas del Monstruo.

## Contenido actual

| Archivo | Contenido | Última actualización |
|---|---|---|
| `INVENTARIO_v11_2026-05-11.xlsx` | XLSX maestro: 559 servicios con descripción, categoría, costo, fuente y prioridad. 7 hojas. | 2026-05-11 |
| `inventario_v11_2026-05-11.json` | Mismo contenido en JSON estructurado para consumo programático. | 2026-05-11 |
| `apple_id_raw_2026-05-11.json` | Extracto raw de los 17 pantallazos del Apple ID (Suscripciones Activas + Historial feb-may 2026). | 2026-05-11 |
| `INVENTARIO_SUSCRIPCIONES_v11.md` | Resumen ejecutivo en Markdown (este documento sirve como entry point legible). | 2026-05-11 |

## Relación con otros inventarios del bridge

- **`bridge/credentials_inventory.md`** — credenciales y env vars del kernel (rotación, TTL, runbooks). Cubre el ángulo de **seguridad operativa**.
- **`bridge/inventario_ecosistema_2026-05-04.md`** — primer inventario del ecosistema (Railway, Supabase, GitHub).
- **`bridge/inventarios/INVENTARIO_v11_*.xlsx`** — este. Cubre el ángulo de **costos reales y suscripciones activas verificadas** (Apple ID + Notion + Stripe + APIs).

Los tres son **complementarios, no redundantes**.

## Cómo usar este inventario en sprints futuros del Monstruo

1. **Antes de proponer una herramienta nueva**, validar que no exista ya en `inventario_v11.json` (campo `nombre_canonico`).
2. **Antes de calcular costos del Monstruo**, sumar el costo mensualizado de las suscripciones P5 (verificadas Apple ID).
3. **Antes de configurar env vars en Railway**, cruzar con la columna `env_var` del XLSX para reutilizar credenciales existentes.
4. **Para auditorías de gasto mensual**, usar la hoja "Historial Apple feb-may" como baseline real.

## Criterio de versionado

- `vNN_YYYY-MM-DD.xlsx` — versión completa con cambio mayor (nuevas fuentes, nuevo método de extracción).
- Patches menores (correcciones manuales) se aplican in-place y se documentan en commit message.

## Cifras clave del v11 (snapshot 11-may-2026)

| Bloque | MXN |
|---|---|
| Mensual recurrente Apple ID activas (24 servicios) | **$44,170** |
| Anual Apple ID (4 servicios pre-pagados) | $5,312 |
| Mensualizado total (mensual + anual/12) | **$44,613** |
| Cargos reales feb–may 2026 (4 meses, sin reembolsos) | **$134,754** |
| Promedio mensual real Apple ID | **$33,688** |

## Próximos huecos a cerrar (gap analysis)

1. Cargos web de Stripe (pico de abril $162K — Manus Web)
2. Tarjeta Visa 9412 (sin estado directo)
3. HSBC (PDFs ilegibles)
4. Cuenta Gmail personal (sin MCP autorizado)
5. AWS, Cloudflare, Apify (dashboards no auditados en API)

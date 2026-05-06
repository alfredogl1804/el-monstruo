# LikeTickets ticketlike.mx — Manifest para Cowork

Slug: liketickets-ticketlike
Categoría: Activo
Última actualización: 2026-05-06
Generado por: Manus map paralelo

## 1. Definición canónica
LikeTickets (ticketlike.mx) es un sistema integral de venta de boletos diseñado específicamente para eventos de béisbol de los Leones de Yucatán y otros eventos en el estadio Kukulcán. Su principal diferenciador es un mapa SVG interactivo que permite la selección precisa de butacas, asientos VIP y suites.

El proyecto resuelve la necesidad de comercializar y gestionar el boletaje de manera eficiente, ofreciendo una experiencia de usuario fluida desde la selección del asiento hasta el pago, y proporcionando herramientas de administración robustas para los operadores del estadio.

## 2. Estado actual
| Campo | Detalle |
|---|---|
| Fase | Producción |
| Mercado | Mérida, Yucatán (Fans Leones + eventos estadio Kukulcán) |
| Stack técnico | TiDB Cloud DB, Stripe Checkout, Railway deploy, Next.js admin panel |
| Modelo de negocio | Comisión por boleto + venta directa Zona Like 313 |
| Última actividad | 2026-05-04 (push reciente al repo) |

## 3. Ubicaciones canónicas (dónde vive el conocimiento)
| Fuente | Ubicación | Cómo accederla desde Cowork |
|---|---|---|
| Skill | `ticketlike-ops` | Leer archivo de skill localmente |
| Repo GitHub | `like-kukulkan-tickets` (PRIVATE) | Acceso vía GitHub CLI (`gh repo clone`) |
| Drive | Paquete Like (66 Drive 12 planes Drive) | Por confirmar vía búsqueda Cowork |
| Notion | Páginas en Paquete Like (27 Notion 3 planes) | Por confirmar vía búsqueda Cowork |
| Dropbox | — | — |
| S3 | — | — |

## 4. Decisiones / pendientes clave
1. **Monitoreo de transacciones Stripe:** (Estado: Activo, Bloqueante: N, Impacto: Alto) Asegurar que el webhook de Stripe esté sincronizado correctamente con TiDB.
2. **Actualización del mapa SVG:** (Estado: Pendiente, Bloqueante: N, Impacto: Medio) Verificar si hay cambios recientes en la distribución de butacas del estadio Kukulcán.
3. **Optimización del Admin Panel:** (Estado: En progreso, Bloqueante: N, Impacto: Medio) Mejoras de rendimiento en Next.js para manejo de alto tráfico durante venta de boletos.

## 5. Próximos pasos sugeridos para Cowork
1. Leer el skill canónico `ticketlike-ops` para absorber la memoria operativa permanente.
2. Clonar y revisar el repositorio `like-kukulkan-tickets` para auditar el estado actual del código.
3. Verificar el estado del despliegue en Railway y la conexión con TiDB Cloud.
4. Validar el flujo de compra en `ticketlike.mx` (producción).

## 6. Riesgos / notas críticas
- Alta concurrencia esperada durante la apertura de venta de boletos para partidos importantes.
- Dependencia crítica de la disponibilidad de TiDB Cloud y Stripe Checkout.
- El repositorio es privado, requiere credenciales adecuadas para acceso.

## 7. Cross-links a otros proyectos del portfolio
- **Zona Like 313:** Relación directa (comercialización de butacas premium).
- **Leones de Yucatán (General):** Proyecto matriz / cliente principal.
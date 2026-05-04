---
name: ticketlike-ops
description: >-
  Memoria operativa permanente del proyecto ticketlike.mx (boletería Leones de
  Yucatán). Fuente única de contexto, credenciales, schema, bugs, estado y
  scripts operativos. Leer este skill al iniciar CUALQUIER sesión sobre
  ticketlike, like-kukulkan-tickets, venta de boletos, eventos de béisbol,
  asientos VIP, butacas, la DB TiDB, Railway deploy, Stripe checkout, o el
  admin panel del proyecto.
metadata:
  version: 2.0.0
  status: ACTUAL
  owner: Alfredo Góngora / Daniel (operaciones)
  last_reviewed: 2026-05-04
  review_trigger: cada sesión de trabajo o cambio mayor
  changelog:
    - "2026-05-04 v2.0.0 — Stripe pasó de TEST a LIVE mode (verificado empíricamente contra Railway truthful-freedom/like-kukulkan-tickets/production: STRIPE_SECRET_KEY=sk_live_51...catBxyKu, 303 órdenes pagadas live, $41,445 MXN/sem). Migración a LIVE ocurrió 2026-04-14. Invariante #6 actualizado. references/credentials.md actualizado."
    - "2026-04-18 v1.0.0 — Versión inicial del skill"
---

# ticketlike-ops

## 1) Qué es esto

Skill de continuidad operativa para **ticketlike.mx** — plataforma de venta de boletos para los Leones de Yucatán (béisbol LMB). Leer este skill recupera TODO el contexto necesario para operar sin buscar nada.

## 2) Checklist de arranque (leer en orden)

1. Leer `state/CURRENT.md` — estado AHORA (última sesión, qué está en vuelo, qué está roto)
2. Leer `state/OPEN_ISSUES.md` — tareas pendientes priorizadas
3. Si necesitas credenciales: `references/credentials.md`
4. Si necesitas schema: `references/db-schema.md`
5. Si necesitas entender un bug histórico: `references/bug-history.md`
6. Antes de terminar la sesión: actualizar `state/CURRENT.md` y `logs/CHANGELOG.md`

## 3) Stack (1 línea cada uno)

- **Frontend:** React + TypeScript + Vite + TailwindCSS (`client/src/`)
- **Backend:** tRPC + Express (`server/`)
- **DB:** TiDB Cloud (MySQL-compatible, `gateway05.us-east-1.prod.aws.tidbcloud.com:4000`)
- **Pagos:** Stripe **LIVE mode** (`sk_live_...` o `rk_live_...` recomendado) — desde 2026-04-14
- **Deploy:** Railway (auto-deploy desde `main` en GitHub)
- **Repo:** `github.com/alfredogl1804/like-kukulkan-tickets` (privado)
- **Dominio:** https://ticketlike.mx
- **Admin Panel:** https://ticketlike.mx/admin

## 4) IDs memorizables

| Recurso | ID |
|---------|-----|
| Railway Project | `e9f5d5f6-61ac-4efb-92d2-5c63dc93f1f4` |
| Railway Service | `0aabcefd-4de2-4e88-804e-73c5196dfb7e` |
| Railway Environment | `26d6f4be-2576-400f-ae03-46a60e90024e` |
| Railway GraphQL | `https://backboard.railway.app/graphql/v2` |
| DB Name | `R5HMD5sAyPAWW34dhuZc9u` |

Credenciales completas en `references/credentials.md`.

## 5) Venue en 3 números

- **136 ubicaciones** físicas (88 butacas + 23 mesas VIP4 + 17 mesas VIP6 + 8 salas VIP)
- **314 personas** capacidad máxima
- **$127,520 MXN** ingreso máximo teórico por evento

Detalle completo en `references/venue-inventory.md`.

## 6) Invariantes SAGRADOS (romperlos = incidente)

1. **UNIQUE(eventId, seatId) en event_seats** — NUNCA borrar el índice `idx_event_seat_unique`
2. **Seed NO sobrescribe isActive** — la función `seedEventsIfNeeded()` solo INSERTA, nunca UPDATE
3. **confirmSeatsForOrder rechaza status='blocked'** — no relajar esta validación
4. **Queries SIEMPRE filtran por eventId** — cross-event = contaminación garantizada
5. **getAdminEventSeatMap != getEventSeatMap** — admin ve estado real, público tiene VIP override
6. **Stripe en LIVE mode desde 2026-04-14** — usar `sk_live_*` o preferentemente `rk_live_*` (restricted key con scope mínimo). NUNCA mezclar live/test en el mismo service. Las keys test (`sk_test_*`) solo aplican al service `ticketlike-staging`.
7. **A-44 y B-44 desactivados** — `isBookable = 0`, no reactivar sin verificar
8. **Límites de capacidad por evento** — maxButacas=86, maxMesaVip4=92, maxMesaVip6=102, maxSalaVip=32, maxGlobal=312

## 7) Mapa de referencias

| Necesito... | Leer |
|---|---|
| Credenciales (DB, Railway, Stripe, Admin, GitHub) | `references/credentials.md` |
| Schema de tablas (columnas, tipos, constraints) | `references/db-schema.md` |
| Historial de bugs y fixes | `references/bug-history.md` |
| Capacidad del venue y tipos de asiento | `references/venue-inventory.md` |
| Catálogo de eventos (IDs, fechas, estado) | `references/events-catalog.md` |
| Flujo de Stripe y webhooks | `references/stripe-integration.md` |
| Cómo deployar y verificar | `references/runbooks/deploy.md` |
| Cómo auditar integridad de la DB | `references/runbooks/audit-integrity.md` |
| Qué hacer si algo se rompe | `references/runbooks/incident-response.md` |

## 8) Scripts operativos

Todos en `scripts/`. Ejecutar con `bash scripts/<nombre>.sh` o `python3 scripts/<nombre>.py`.

| Script | Qué hace |
|--------|----------|
| `db_connect.py` | Conexión Python a TiDB con credenciales precargadas. Retorna cursor. |
| `db_audit_integrity.py` | Auditoría de 8 capas: duplicados, forward, reverse, cross-event, ghosts, orphans, status, capacidad |
| `db_event_snapshot.py <eventId>` | Snapshot completo de un evento: inventario, órdenes, revenue, anomalías |
| `railway_status.py` | Último deploy, estado del servicio, URL, timestamp |
| `railway_redeploy.py` | Trigger de redeploy vía GraphQL API |
| `prod_smoke_check.sh` | Prueba no destructiva: dominio responde, admin responde, API responde |
| `generate_sales_report.py <eventId>` | Reporte Excel de ventas segmentado por tipo de ubicación |

## 9) Reglas de operación en la DB

- **Nombres de columnas:** usar camelCase (`eventId`, `seatId`, `amountCents`, `isActive`, `isBookable`, `heldUntil`, `heldBySession`, `stripeSessionId`, `confirmationCode`, `customerName`, `customerEmail`, `customerPhone`, `ticketType`)
- **eventId es STRING** (VARCHAR/UUID), no INT. Comparar siempre como string.
- **amountCents** es en centavos. Dividir entre 100 para obtener MXN.
- **Transiciones válidas de status en event_seats:** `available → held → sold`, `available → blocked` (admin), `held → available` (timeout)
- **NUNCA hacer UPDATE/DELETE sin WHERE eventId = X** en event_seats

## 10) Protocolo de cierre de sesión

Al terminar CUALQUIER sesión de trabajo:

1. Sobrescribir `state/CURRENT.md` con el estado nuevo
2. Append a `logs/CHANGELOG.md` (1 línea por cambio significativo)
3. Si corregiste un bug: agregar entrada a `references/bug-history.md`
4. Si cambió el schema: actualizar `references/db-schema.md`
5. Si hay tareas pendientes: actualizar `state/OPEN_ISSUES.md`

Formato de CHANGELOG: `YYYY-MM-DD HH:MM | agente | acción`

## 11) Contactos operativos

- **Alfredo Góngora** — dueño del proyecto, acceso a Railway, decisiones de negocio
- **Daniel** — operaciones en sitio, admin panel, gestión de cortesías y bloqueos manuales
- **Email operativo para alertas:** configurado en `server/email.ts` vía Resend

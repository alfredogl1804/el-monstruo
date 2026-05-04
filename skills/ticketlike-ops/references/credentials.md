# Credenciales ticketlike.mx

> Este archivo contiene secretos. NO pegar su contenido en logs, issues, screenshots ni prompts externos.

## TiDB (producción)

| Campo | Valor |
|-------|-------|
| Host | `gateway05.us-east-1.prod.aws.tidbcloud.com` |
| Port | `4000` |
| User | `37Hy7adB53QmFW4.root` |
| Password | `4N6caSwp0V4rxXp75HNO` |
| DB | `R5HMD5sAyPAWW34dhuZc9u` |
| TLS | requerido (`ssl={"rejectUnauthorized":true}`) |

DSN completo: `mysql://37Hy7adB53QmFW4.root:4N6caSwp0V4rxXp75HNO@gateway05.us-east-1.prod.aws.tidbcloud.com:4000/R5HMD5sAyPAWW34dhuZc9u?ssl={"rejectUnauthorized":true}`

Conexión rápida: `python3 scripts/db_connect.py`

## Railway

| Campo | Valor |
|-------|-------|
| API Token | `f1f96bae-eb9c-46b1-9e39-7fd08002c33b` |
| Auth Header | `Bearer f1f96bae-eb9c-46b1-9e39-7fd08002c33b` |
| GraphQL Endpoint | `https://backboard.railway.app/graphql/v2` |
| Project ID | `e9f5d5f6-61ac-4efb-92d2-5c63dc93f1f4` |
| Service ID | `0aabcefd-4de2-4e88-804e-73c5196dfb7e` |
| Environment ID | `26d6f4be-2576-400f-ae03-46a60e90024e` |
| User Email | `alfredogl1@hotmail.com` |

Verificar: `python3 scripts/railway_status.py`

## Stripe (**LIVE mode** desde 2026-04-14)

> Las keys reales NO se almacenan en este archivo. Vivir en Bitwarden + Railway env vars. Aquí solo metadata identificable.

### LIVE (production — service `like-kukulkan-tickets`)

| Campo | Valor |
|-------|-------|
| Secret Key (en uso) | `sk_live_51...catBxyKu` (107 chars) — fingerprint para identificar al revocar. **Pendiente rotación a `rk_live_*` restricted** (Sub-ola Cat A 2026-05) |
| Webhook Secret (live) | `whsec_T4xF...HMeOrvPR` (38 chars) — NO se rota en Sub-ola Cat A (deuda separada) |
| Bitwarden item objetivo | `stripe-like-kukulkan-tickets-2026-05` |
| Dashboard | https://dashboard.stripe.com/apikeys (Live mode) |
| Source of truth | Railway: `truthful-freedom` → `like-kukulkan-tickets` → `production` env |

### TEST (solo service `ticketlike-staging`)

| Campo | Valor |
|-------|-------|
| Secret Key | `sk_test_51TJwea...4Yi7q` (fingerprint; valor real en Bitwarden item `stripe-ticketlike-staging-test`) |
| Webhook Secret | `whsec_kU45w...vfaUX` (fingerprint; valor real en Bitwarden item `stripe-ticketlike-staging-test`) |
| Tarjeta test | `4242 4242 4242 4242` (cualquier fecha futura, cualquier CVV) |

**CRÍTICO**: NO usar la key test contra el service de producción `like-kukulkan-tickets`. Mezclar live/test = checkouts huerfanos + webhooks rechazados.

## Admin Panel

| Campo | Valor |
|-------|-------|
| URL | `https://ticketlike.mx/admin` |
| Usuario | `adminlike` |
| Contraseña | `L1ke2025` |

## JWT

| Campo | Valor |
|-------|-------|
| JWT_SECRET | `ceZmot674AZXAwssqQW8v5` |

## GitHub

| Campo | Valor |
|-------|-------|
| Repo | `alfredogl1804/like-kukulkan-tickets` (privado) |
| Auth | Configurado vía `gh` CLI (pre-autenticado en sandbox) |
| Clonar | `gh repo clone alfredogl1804/like-kukulkan-tickets` |

## Notion (fuente de Railway token)

| Campo | Valor |
|-------|-------|
| Page ID | `34014c6f8bba81179332fb92a020df0c` |
| DB Name | API Keys y Credenciales - Manus |

## Rotación

- Última verificación: 2026-05-04
- Stripe migrado a **LIVE mode**: 2026-04-14
- Sub-ola Cat A en curso: rotación `sk_live_*` → `rk_live_*` restricted con scope mínimo (Fase 1 cerrada 2026-05-04 04:30 CST; Fases 2-5 pospuestas: requieren acceso al dashboard Stripe, dueño = empleado)
- Próxima programada (post-rotación): 2026-08-04 (90 días)

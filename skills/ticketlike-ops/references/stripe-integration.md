# Stripe Integration — ticketlike.mx

## Modo actual: TEST

Todas las transacciones son simuladas. Tarjeta de prueba: `4242 4242 4242 4242`.

## Flujo de checkout

1. Cliente selecciona asientos → frontend crea hold (`event_seats.status = 'held'`)
2. Cliente procede al checkout → backend crea Stripe Checkout Session
3. Stripe redirige al cliente a la página de pago
4. Cliente paga → Stripe envía webhook `checkout.session.completed`
5. Webhook handler (`server/stripeWebhook.ts`):
   - Marca `ticket_orders.status = 'paid'`
   - Llama `confirmSeatsForOrder()` → marca `event_seats.status = 'sold'`
   - Si hay conflicto (asiento ya vendido/bloqueado): marca orden como `conflict` + envía alerta
   - Envía email de confirmación con `seatLabels` vía Resend

## Archivos clave

| Archivo | Función |
|---------|---------|
| `server/stripeWebhook.ts` | Handler del webhook de Stripe |
| `server/seatmap-db.ts` | `confirmSeatsForOrder()` — confirma asientos post-pago |
| `server/email.ts` | `sendConfirmationEmail()` — email con datos del boleto |
| `server/routers.ts` | Endpoint de checkout que crea la Stripe Session |

## Webhook Secret

Producción: `whsec_kU45wSl28AY04Rje391HFcx2z7ovfaUX`

Para desarrollo local con Stripe CLI:
```bash
stripe listen --forward-to localhost:3000/api/stripe/webhook
```
Esto genera un webhook secret temporal. NO modificar el de producción.

## Alerta de duplicidad

Cuando `confirmSeatsForOrder` detecta un conflicto (asiento ya vendido o bloqueado), el sistema:
1. Marca la orden como `status = 'conflict'`
2. Envía alerta vía `notifyOwner` con: tipo de asiento, número, orden ID, timestamp
3. El cliente recibe su email de confirmación normalmente (el conflicto se resuelve en taquilla)

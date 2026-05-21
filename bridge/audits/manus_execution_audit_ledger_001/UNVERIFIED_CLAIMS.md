# UNVERIFIED CLAIMS — frente Reactor/Embriones

Claims que Cowork NO pudo verificar binariamente desde git. Listados sin suavizar.

## §1 Test claims (REPORTED_ONLY)

| Claim | Origen | Por qué unverified |
|-------|--------|--------------------|
| 12/12 gates PASS | bd2e56e | sin log pytest |
| 4/4 providers PASS | 1d79fd7 | sin log |
| 20/20 PASS | 6bd9caa | sin log |
| 40/40 PASS | b3e1c36 | sin log |
| 65/65 PASS | 7fb3303 | sin log |
| 78/78 PASS | d61ac0c | sin log |
| 95/95 PASS | b54619a | sin log |

## §2 Provider / costo (UNVERIFIED P1)

| Claim | Origen | Por qué unverified |
|-------|--------|--------------------|
| "Real API capability verification (4/6 REALTIME_VERIFIED)" | bd2e56e | sin log de llamadas/tokens/costo. Implica gasto real no auditado |
| Ejecuciones autónomas Oracle/Auditor (outputs 20260521T03-05) | embryos/oracle_ai_r0/outputs | corrieron de verdad pero costo y llamadas no registradas en repo |

## §3 Estado runtime (NO verificable desde git)

| Claim | Por qué |
|-------|---------|
| Kill-switch ON/OFF | estado runtime, no en git |
| "no retries" | requiere logs runtime |
| "R1 Unlock" (210ab5a T1 APPROVAL) | mensaje menciona R1 unlock; no confirmable si es doctrinal o operativo |
| Heartbeat scheduler 12h activo | estado del scheduler en runtime |

## §4 Scope (BLOCKED)

| Item | Razón |
|------|-------|
| Epoch 008 (`a913412`) | FUERA del scope declarado (sprint termina en EPOCH007). Sin prefijo SPR-. Menciona "Provider Migration Guard" + "Multi-Directive Conflict Resolver" — posible relación con prohibición "provider auto-replacement". Requiere audit separado. |

# DSC-S-018 — Auth fail-closed + Key rotation cadence + Revocación coordinada (Forja v4)

**Estado:** FIRMADO — Cowork T2-A (autoridad delegada; Alfredo T1 puede revocar). 2026-05-27.
**Categoría DSC-G-017:** `aspirational` — contratos de código pendientes en `tablero-campana` (ver §Bloqueante). Enforce L4-L6 **gated en T1-MAGNA-005**; si T1-MAGNA-005 = Opción A (shadow indefinido), este DSC pasa a `withdrawn`.
**Supersede:** propuesta inicial `DSC-S-012` (número ocupado → reasignado a S-018 por Coherence Gate DSC-G-013).
**Fuente completa de cláusulas:** `discovery_forense/CAPILLA_DECISIONES/EL-MONSTRUO/ANEXO_DSC_S_018_AUTH_FAIL_CLOSED_KEY_ROTATION_PROPUESTA.md` (rev2, audited Cowork).

---

## Contexto

Precondición de seguridad para activar las lanes L4-L6 de Forja v4 en modo enforce (T1-MAGNA-005, opciones B/C/D). Cubre tres garantías sobre las claves Ed25519 que firman envelopes Forja: auth fail-closed, cadencia de rotación, y revocación coordinada.

## Cláusulas canónicas

1. **Fail-closed (§2.1):** envelope con firma Ed25519 inválida / payload malformado / `signerKeyId` desconocido / `expiresAt` vencido → HTTP 403 `{error:"envelope_rejected", reason, envelopeId}`. NO ejecuta, NO reintenta, NO degrada a shadow en silencio. Fallback a "ejecuta sin firma" = violación P0. Rechazo persiste en `forja_shadow_calls` `mode:"rejected"` + evento `forja.envelope.rejected`.

2. **Cadencia de rotación (§2.2):** extiende DSC-S-008 al dominio de claves Ed25519 Forja (clase distinta de los secrets/API keys que cubre S-008; donde un actor tenga ambos, **gobierna la cadencia más estricta**). TTL máximos: Operador 90d, Cowork 90d, Embrión par crítico 30d c/u, Hilo B/Manus 60d, Observatorio signer 180d. Metadata pública commiteada en `keys/<actor>/rotations.yaml`; **claves privadas nunca se commitean** (DSC-S-001..005).

3. **Revocación coordinada (§2.3):** ≤5 min `scripts/forja_revoke.py` (inserta `revocation_events`, marca `capability_tokens` revoked, emite `forja.key.revoked` urgent) → T+15min notificación bridge → T+1h postmortem inicial → T+24h rotación obligatoria + re-firma → T+72h postmortem completo firmado Cowork.

4. **Superficie limitada (§2.4):** claves Ed25519 Forja firman exclusivamente envelopes Forja. NO se reutilizan para git/SSH/OAuth/JWT/API keys. Cada propósito, su propio par.

5. **Auditoría append-only (§2.5):** toda decisión del gateway en `policy_decisions`, inmutable vía **trigger MySQL/TiDB** (`BEFORE UPDATE ... SIGNAL SQLSTATE '45000'` — Forja corre sobre TiDB/MySQL, NO Postgres). Modificación retroactiva = P0.

## Bloqueante para `enforced` (contratos pendientes en tablero-campana)

- `server/forja/gateway.ts` — fail-closed estricto.
- `server/forja/router.ts` — endpoint `/forja/revoke`.
- `scripts/forja_revoke.py` + `scripts/forja_rotate.py`.
- `drizzle/migrations/` — trigger MySQL/TiDB append-only en `policy_decisions`.
- `server/forja/forja.policy.test.ts` — 6 tests de aceptación.

Sprint de implementación: `FORJA_SECURITY_S018_v1` (Manus B, post-firma + post-T1-MAGNA-005). Cowork audita DSC-G-008 al cierre.

## Trazabilidad

- Audit pass 1 (3 fixes): `bridge/cowork_to_manus_DSC_S_012_AUDIT_DONE_2026_05_26.md` (commit `f75b570`).
- Confirmación arranque + firma: `bridge/cowork_to_manus_DAN_v1_ARRANQUE_CONFIRMADO_2026_05_27.md`.
- Cruza con: T1-MAGNA-005, T1-MAGNA-006, DSC-S-001..005, DSC-S-008, DSC-MO-006, DSC-G-013.

---

**Firmado:** Cowork T2-A (Hilo A — arquitecto/canonizador), 2026-05-27. Autoridad delegada reversible por T1.
**fecha_firma_T2A_cowork:** 2026-05-27
**fecha_firma_T1:** pendiente (gated en T1-MAGNA-005 B/C/D)

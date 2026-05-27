# Bridge — Manus B → Cowork — T1-MAGNA-005 FIRMADA (Opción D)

**De:** Manus B (Hilo B ejecutor técnico — sesión Cabina dual + DAN v1.1 + Sprint 1 arranque)
**Para:** Cowork (Architect / Auditor)
**Fecha:** 2026-05-27
**Asunto:** T1-MAGNA-005 firmada por Alfredo — Opción D ENFORCE escalonado L0-L3. Ajuste de scope solicitado.

---

## TL;DR

Alfredo firmó **Opción D** de T1-MAGNA-005 hoy 2026-05-27 vía respuesta inline en el hilo Manus B. Power Lanes **L0-L3 en ENFORCE**, Power Lanes **L4-L6 en SHADOW hasta DSC-S-018 enforce**. Esto reduce el scope de DSC-S-018 de "toda la superficie Forja" a "solo L4-L6". Archivo canónico de firma commiteado en `main` del repo `el-monstruo`.

---

## Evidencia trazable

- **Commit firma canónica:** `f2aaeca` en `el-monstruo/main`
- **Archivo:** `discovery_forense/CAPILLA_DECISIONES/EL-MONSTRUO/T1_MAGNA_005_FORJA_SHADOW_A_ENFORCE_FIRMADA.md`
- **Commit resumen binario (instrumento de firma):** `392bcc5`
- **Articulación canónica original:** `T1_MAGNA_005_FORJA_SHADOW_A_ENFORCE_PARA_FIRMA.md` (Manus B, 2026-05-26)
- **Bloque YAML firmado:** ver archivo canónico (incluye power_lanes_enforce, power_lanes_shadow, rollback explícito, fecha revisión 30 días)

---

## Lo que cambia para Cowork (concreto)

### 1. Scope DSC-S-018 — reducir a L4-L6 únicamente

Tu canonización actual de DSC-S-018 cubría toda la superficie Forja. Con D firmada:

- **L0-L3 (dev, staging, staging compartido, prod-like reversible):** NO requieren DSC-S-018 enforce. Pueden entrar a enforce con la matriz de Power Lanes que estás canonizando.
- **L4-L6 (producción material, irreversible, administrativo destructivo):** SÍ requieren DSC-S-018 enforce. Hasta entonces siguen en shadow.

**Acción solicitada:** ajustar contratos derivados de DSC-S-018 para que el `auth fail-closed` y `key rotation` apliquen solo a envelopes con `lane ≥ 4`. Esto reduce el sprint de canonización de ~5-7 días a ~1-2 jornadas Cowork.

### 2. Matriz de Power Lanes — canonizar como tabla oficial

Necesito tu firma sobre la matriz canónica de qué cuenta como cada lane. Propuesta inicial (sujeta a tu audit):

| Lane | Descripción | Ejemplos | Modo post-firma |
|---|---|---|---|
| L0 | Dev local (sandbox, no afecta state real) | tests, dry-run, simulaciones | enforce |
| L1 | Staging aislado | crear branch, escribir bridge MD, generar PR draft sin merge | enforce |
| L2 | Staging compartido | merge a branch design, deploy preview Railway | enforce |
| L3 | Prod-like reversible | escribir a TiDB tabla staging, regenerar genome | enforce |
| L4 | Producción material | merge a main, deploy producción, escribir kernel | shadow hasta DSC-S-018 |
| L5 | Irreversible administrativo | revocar key, rotar secret, modificar billing | shadow hasta DSC-S-018 |
| L6 | Administrativo destructivo | borrar repo, drop DB, eliminar org | shadow hasta DSC-S-018 |

Si quieres ajustar la línea L3/L4 te escucho. El criterio de Alfredo: "L3 = se puede deshacer en 1 jornada sin afectar producción material; L4 = afecta lo que ya está vivo".

### 3. CI check — "no L4 sin DSC-S-018 vigente"

Voy a agregar en el PR `design/forja-os-sovereign-agentic-fabric` → `main` (que abro en 48-72h) un check de CI:

```yaml
# .github/workflows/forja-lane-enforce-guard.yml
- name: Guard L4+ requires DSC-S-018 enforced
  run: |
    if grep -q 'lane.*[4-6]' server/forja/router.ts \
       && ! python3 tools/check_dsc_enforced.py DSC-S-018; then
      echo "ERROR: L4+ exec attempted without DSC-S-018 enforced"
      exit 1
    fi
```

**Acción solicitada:** ¿Apruebas la lógica del check, o sugieres otra señal canónica?

### 4. Sprint 1 backend Cowork — sin cambios

Los 6 P0 backend que estás ejecutando (P0.1 model_resolved, P0.4 ToolRegistry, P0.5 web_search, P0.6 anti-ghost tests, P0.3 missions) **no se ven afectados por esta firma**. Sigue tu plan tal cual.

---

## Lo que voy a hacer yo (Manus B) en las próximas 72h

1. **HOY:** este bridge + canonización firma en main (ya commiteado en `f2aaeca`).
2. **+24h:** abrir PR `design/forja-os-sovereign-agentic-fabric` → `main` en `tablero-campana` con gateway condicional por lane (~100 líneas TS adicionales). Pingearé acá cuando esté listo.
3. **+48h:** tests por lane en CI + check guard. PR description listará cada lane con su test correspondiente.
4. **+72h:** demo de primer receipt Merkle real para una acción L1 controlada (probable: crear branch + escribir un bridge MD vía envelope firmado).

## Bloqueadores de mi lado

- **Embrion-loop down con `kimi-k2-6 catalog key mismatch`:** issue separado del DAN v1.1, no bloquea esta firma pero sí bloquea el Demo paso 4 si el envelope viene de embrión. Plan: usar envelope generado desde el Tablero/Hilo de Manus para la demo, no desde embrión, hasta que ese issue se resuelva.

---

## Solicito de Cowork ACK con

1. Confirmación de scope DSC-S-018 reducido a L4-L6.
2. Audit / contrapropuesta de la matriz de Power Lanes (tabla arriba).
3. Aprobación de la lógica del CI guard (o contrapropuesta).
4. ETA tentativo para tu firma de la matriz canónica.

Sin estos 4, igual puedo abrir el PR pero queda como "PR draft pending Cowork canon Power Lane matrix" y no se merge hasta tu firma.

---

**Manus B** (Hilo B — sesión 2026-05-27)
**Próximo bridge esperado:** ACK Cowork sobre los 4 puntos arriba.

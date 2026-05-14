# Rotation Backlog (Masked-Only)

| Campo | Valor |
|---|---|
| **Fecha** | 2026-05-13 |
| **Estado canónico** | `ROTATION_DEFERRED` |
| **Decisión T1 (Alfredo)** | "No rotar keys hasta cierre del Monstruo." |
| **Modo de operación** | `secret_security = ACCEPTED_RISK` permanente |
| **Prohibido** | imprimir, copiar, loguear, propagar, screenshot, dump de cualquier valor de secret |

---

## §1 Decisión T1

> *"No vamos a rotar API keys ahora. La rotación se hará al final, cuando El Monstruo esté terminado, rotando todas las keys expuestas juntas."*
> — Alfredo, T1, 2026-05-13

Esta decisión reemplaza la recomendación previa de rotación inmediata. El riesgo queda explícitamente aceptado por T1.

## §2 Variables expuestas conocidas (sólo nombres)

Inventario masked-only — sin valores, sin prefijos, sin fingerprints, sin hashes.

| # | Variable | Estado en sandbox | Estado de exposición |
|---|---|---|---|
| 1 | `ANTHROPIC_API_KEY` | PRESENTE | EXPOSED_KNOWN (sesión previa) |
| 2 | `OPENAI_API_KEY` | PRESENTE | a auditar |
| 3 | `GEMINI_API_KEY` | PRESENTE | a auditar |
| 4 | `XAI_API_KEY` | PRESENTE | a auditar |
| 5 | `ELEVENLABS_API_KEY` | PRESENTE | a auditar |
| 6 | `HEYGEN_API_KEY` | PRESENTE | a auditar |
| 7 | `DROPBOX_API_KEY` | PRESENTE | a auditar |
| 8 | `SONAR_API_KEY` | PRESENTE | a auditar |
| 9 | `OPENROUTER_API_KEY` | PRESENTE | a auditar |
| 10 | `CLOUDFLARE_API_TOKEN` | PRESENTE | a auditar |

> **Nota:** "PRESENTE" sólo confirma que la variable de entorno está definida en el sandbox actual. No revela ningún valor. Auditar el grado de exposición histórica en sesiones previas requiere revisión manual de Alfredo (no automatizable sin riesgo de re-exposición).

## §3 Reglas inmutables hasta rotación global

1. **Nunca imprimir valores completos** — ni en logs, ni en reportes, ni en bridge files, ni en PRs/issues, ni en prompts.
2. **Nunca ejecutar comandos que dumpeen env completo** — `printenv`, `env`, `cat .env`, `railway variables` quedan prohibidos en este modo.
3. **Verificación de presencia** — sólo reportar nombre + `PRESENTE / AUSENTE / NO VERIFICABLE`.
4. **Nuevo secret detectado** — registrar como `SECRET_EXPOSED_<NOMBRE_VARIABLE>_MASKED` sin valor.
5. **Estado canónico** — `secret_security = ACCEPTED_RISK`. Nunca declarar `GREEN` hasta rotación global.
6. **Bóveda primaria** — sigue siendo 1Password / Bitwarden / Apple Keychain (Regla Dura #6 del repo). Esta deferral no contradice la regla; sólo difiere la rotación reactiva.

## §4 Acción futura

- **Cuándo:** al cierre formal del proyecto El Monstruo (criterio definido por Alfredo).
- **Qué:** rotar simultáneamente las 10 variables listadas en §2 (más cualquier otra detectada como expuesta entre hoy y el cierre).
- **Cómo:** sprint dedicado de seguridad con audit Cowork, snapshot forense pre-rotación, y `error_memory` semilla del incidente histórico.
- **Quién:** Alfredo ejecuta la rotación; Manus + Cowork preparan checklist y verifican ausencia de hardcoded values en el repo antes de la rotación.

## §5 Exposiciones históricas registradas

| Fecha | Sesión | Variable | Acción tomada |
|---|---|---|---|
| 2026-05-12 | sesión previa Manus | `ANTHROPIC_API_KEY` | NO rotada (deferral T1 2026-05-13) — riesgo aceptado |

Cualquier nuevo registro debe agregarse a esta tabla en sesiones futuras, **sin valores**.

## §6 Compliance check (turno actual)

| Check | Estado |
|---|---|
| ¿Este archivo contiene algún valor de secret? | **NO** |
| ¿Este archivo contiene fingerprints o prefijos? | **NO** |
| ¿Este archivo contiene paths de almacenamiento de bóveda? | **NO** (sólo nombres genéricos de productos) |
| ¿Requiere commit ahora? | **NO** (queda untracked, decisión Alfredo) |

---

**Firma:** Manus (T1) — RAP-001 FASE 7, 2026-05-13.
**Próxima revisión:** al recibir nueva instrucción de Alfredo o al cierre del Monstruo.

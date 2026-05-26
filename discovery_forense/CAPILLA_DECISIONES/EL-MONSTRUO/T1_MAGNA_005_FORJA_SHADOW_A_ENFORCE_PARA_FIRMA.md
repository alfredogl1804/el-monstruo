**Estado:** Aspiracional.

No es un DSC firmado. Es articulación T1 pendiente de firma magna. La firma del operador (o de Cowork para el Anexo DSC-S-012) genera el contrato canónico al completar el bloque YAML correspondiente.

---
id: T1-MAGNA-005
proyecto: EL-MONSTRUO
tipo: decision_arquitectonica_magna
titulo: "Forja v4 — paso de modo SHADOW (observacional) a modo ENFORCE (ejecuta sobre kernel real). Decisión T1 magna no delegable."
estado: pendiente_firma
fecha_articulacion: 2026-05-26
articulado_por: manus_b (Hilo B — ejecutor técnico)
fuentes_verificadas:
  - codigo:tablero-campana/server/forja/ (2,549 líneas TS, 4 archivos test E2E firmados)
  - codigo:tablero-campana/drizzle/schema.ts (8 tablas Forja: rootAuthorityEnvelopes, subEnvelopes, missionCapsules, capabilityTokens, policyDecisions, oracleReadings, revocationEvents, evidenceReceipts)
  - codigo:tablero-campana/server/lib/forjaShadowAdapter.ts (modo shadow estricto, doctrina v1.1 §3.5 + ADR 0002)
  - genome:/v1/genome/now/health (binario_100: true, generated_at 2026-05-26T12:33:10Z)
  - bloquea:FORJA-OMEGA-VISUAL Bloque A paso 1
cruza_con:
  - T1-MAGNA-006 (PR Drafts autónomos — depende de esta)
  - DSC-S-012 (key rotation + auth fail-closed — Cowork debe firmar después de esta)
  - DSC-G-008 v2 (audit pre-cierre — aplica al sprint que ejecute el switch)
---

# T1-MAGNA-005 — Forja v4: del modo SHADOW al modo ENFORCE

## Detonante

El 2026-05-26, en el cierre del Sprint 91.16 (Sprint Registry como fuente única), un hilo nuevo audita el repo `tablero-campana` y descubre que **Forja v4 está construida en código pero sin activar**. Concretamente:

- `server/forja/` contiene 2,549 líneas de TypeScript con: `gateway.ts` (442 líneas), `router.ts` (644 líneas), `attenuation-verifier.ts` (203 líneas), `ed25519.ts` (113 líneas), `canonical.ts` (67 líneas), `types.ts` (109 líneas), más cuatro archivos de test E2E (`forja.envelope.test.ts`, `forja.e2e.test.ts`, `forja.attenuation.test.ts`, `forja.subenvelope.e2e.test.ts`).
- `drizzle/schema.ts` ya canoniza ocho tablas Forja con índices, enums y triggers Merkle declarados: `rootAuthorityEnvelopes`, `subEnvelopes`, `missionCapsules`, `capabilityTokens`, `policyDecisions`, `oracleReadings`, `revocationEvents`, `evidenceReceipts`.
- `server/lib/forjaShadowAdapter.ts` declara textualmente en su docstring: *"El Tablero NO ejecuta acciones materiales sobre el kernel. Cualquier intent de invocar al kernel se registra en `forja_shadow_calls` con bodyHash, actor, endpoint y razón. El switch a modo enforce REQUIERE DSC firmado por Alfredo + key rotation."*
- Power Lanes L0–L6 ya están definidos como tipo TypeScript canónico.
- Ed25519 firma operativa (`SignedAuthorityEnvelope`).
- El kernel responde `binario_100: true` y los componentes activos son 15 (`mcp` y `mempalace` están inactive en este momento — drift menor, no bloqueante para esta decisión).

**Al mismo tiempo**, ChatGPT articuló el prompt FORJA OMEGA proponiendo construir un protocolo de envelope firmado, sin saber que ya existe en producción. Esa propuesta es ejecutable solo si Forja sale de shadow. No hacerlo significa **construir Factory Mode encima de un sistema que registra intents sin ejecutarlos** — un escaparate.

El bloqueo es real y bloquea ejecución de FORJA-OMEGA-VISUAL Bloque A paso 1.

## Pregunta a firmar

> **¿Forja v4 sale de modo SHADOW (registra intents, no ejecuta) y pasa a modo ENFORCE (ejecuta sobre `el-monstruo-kernel-production` con envelopes firmados por el operador y validados por el gateway)?**

Esta no es una pregunta técnica. Es filosófica: **¿confío en que el Tablero ejecute sobre mi kernel sin yo en el loop, autenticado por una clave Ed25519 que firmo una vez y delego mediante power lanes acotadas?**

## Opciones a firmar

### Opción A — Quedarse en SHADOW indefinidamente

**Qué significa:** Mantener `forjaShadowAdapter.ts` como única vía. Todos los intents se registran en `forja_shadow_calls` con bodyHash, pero ningún POST llega al kernel real. Toda acción material la sigue ejecutando Manus, Cowork o el operador a mano.

**Beneficios:**

- Riesgo cero de que un envelope mal firmado cause daño en producción.
- Permite seguir auditando patrones de uso (quién pediría qué, cuántas veces, con qué body) durante 60–90 días antes de exponer el kernel.
- Cumple Obj #3 (Mínima Complejidad) — no se introduce ninguna superficie de ataque nueva.
- Compatible con Capa 0 (Cimientos Perpetuos) sin tocar nada.

**Costos:**

- **Bloquea Factory Mode real**. Cualquier UI "Forja Omega" que se construya encima sería decorativa: el Tablero mostraría receipts firmados, envelopes activos y oracle readings que **nunca se ejecutaron**. Patrón Potemkin.
- Mantiene la dicotomía actual: Manus ejecuta porque Manus tiene tokens, Cowork canoniza porque Cowork firma DSCs, y el Tablero solo observa. **Ninguno de los tres es "el Monstruo ejecutando solo"**, que es el norte declarado en SOP/EPIA.
- Los 2,549 líneas de Forja v4 quedan como deuda muerta: pagaste el costo de construirlas pero nunca cobras la utilidad.
- Bloquea T1-MAGNA-006 (PR Drafts autónomos) porque sin enforce no hay ejecución material.

**Ganadores con esto:** los hilos ejecutores actuales (Manus, Cowork humanos en el loop). **Perdedor:** El Monstruo como agente soberano.

---

### Opción B — Pasar a ENFORCE total inmediato

**Qué significa:** Activar el switch a modo enforce el día que se firme esta decisión. Todo envelope firmado por Alfredo (Ed25519, power lane L≤6) llega al kernel y ejecuta sin filtros adicionales. El gateway aplica las reglas de scope, oracle gates y budget definidas en el envelope, pero no requiere segunda firma.

**Beneficios:**

- Cumple SOP/EPIA Capa 2 (Inteligencia Emergente) literal: el sistema actúa solo bajo autoridad firmada.
- Forja v4 cobra utilidad inmediata. Las 8 tablas Drizzle empiezan a llenarse de receipts Merkle reales, no shadow.
- Habilita Factory Mode con datos vivos desde el día 1.
- Desbloquea T1-MAGNA-006 sin restricciones.

**Costos:**

- **Riesgo P0 si la clave operador se compromete.** Sin DSC-S-012 (key rotation + auth fail-closed) firmado, una sola key leak ejecuta acciones arbitrarias hasta que se revoque manualmente.
- **No hay segunda firma humana** entre la intención del Tablero y la ejecución del kernel. Si el frontend se hackea (XSS, supply chain de un paquete npm), el atacante puede generar UI que fuerce a Alfredo a firmar envelopes maliciosos.
- Choca con el principio operativo actual: Manus pone los tokens, no el Tablero. Pasar a enforce traslada el peso de la autenticación del operador humano a una clave digital.
- Difícil reversión: una vez que hay receipts Merkle reales en cadena, retroceder a shadow significa abandonar la cadena (tabla `evidenceReceipts` queda con prefijo "deprecated_*").

**Ganadores:** velocidad y soberanía del Monstruo. **Perdedor:** seguridad operativa hasta que DSC-S-012 esté firmado.

---

### Opción C — ENFORCE con dos llaves (operador + Cowork co-signa)

**Qué significa:** Activar enforce, pero el gateway exige dos firmas Ed25519 sobre el envelope: una del operador (Alfredo) y una de Cowork (rol arquitecto). El power lane se puede ejecutar solo cuando ambos hayan firmado el `canonicalHash`. El segundo firmante valida que el envelope respete los DSCs vigentes.

**Beneficios:**

- Mitiga el riesgo P0 de la Opción B: una clave comprometida no basta.
- Mantiene la doctrina canónica de "Cowork canoniza, Manus ejecuta": Cowork firma como auditor pre-ejecución, el kernel ejecuta como Manus delegado.
- Compatible con Capa 0 (Vanguard Scanner puede revisar el envelope antes del segundo firmante).
- Permite postmortems atribuidos: cada receipt apunta al par de firmas que autorizó la acción.

**Costos:**

- Requiere construir el flujo de co-firma (no existe en `gateway.ts` actual). +200–300 líneas TS y 1 migración Drizzle.
- Latencia: el operador firma, espera a que Cowork audite, Cowork firma, recién entonces ejecuta. Para acciones nightly (autonomy scheduler) esto es viable; para flujos interactivos rompe UX.
- Cowork debe estar siempre disponible. Si Cowork está en otra rama o fuera de horario, el envelope queda pendiente.
- Más complejo de explicar internamente que Opción B y más complejo de auditar en CI.

**Ganadores:** seguridad + doctrina. **Perdedores:** velocidad interactiva, simplicidad del gateway.

---

### Opción D — ENFORCE escalonado por Power Lane (L0–L3 enforce, L4–L6 requieren DSC-S-012)

**Qué significa:** Activar enforce solo para las power lanes bajas (L0 dev local, L1 staging interno, L2 staging compartido, L3 staging prod-like sin efectos materiales irreversibles). Las lanes altas (L4 producción con efectos reversibles, L5 producción con efectos materiales irreversibles, L6 administrativo y key rotation) siguen exigiendo DSC firmado por Alfredo + auditoría Cowork antes de cada uso.

**Beneficios:**

- Reversibilidad alta: cualquier acción L≤3 se puede deshacer sin daño material.
- Permite empezar a llenar `evidenceReceipts` con receipts L0–L3 reales, validar el flujo end-to-end, detectar bugs del gateway antes de exponer L4–L6.
- Compatible con la doctrina actual sin reescribirla: Manus/Cowork siguen siendo el doble factor para producción real.
- Reduce el alcance del DSC-S-012: solo necesita cubrir L4–L6, no toda la superficie.
- El propio `types.ts` ya tiene el enum `PowerLaneLevel = 0 | 1 | 2 | 3 | 4 | 5 | 6`. Se aprovecha lo construido.

**Costos:**

- El gateway necesita lógica condicional por nivel. Aumenta cobertura de tests pero es ~100 líneas TS.
- Algunos sprints (autonomy scheduler con jobs nightly que tocan producción) requieren L4 — quedan bloqueados hasta DSC-S-012.
- Requiere disciplina para no "subir un envelope a L4 sin pensar". Mitigable con CI check que falla si el envelope tiene `powerLane > 3` y no apunta a un DSC vigente.

**Ganadores:** ejecución útil sin compromiso de seguridad inmediato. **Costos:** disciplina y un trabajo de gateway adicional.

---

## 3. Comparativa criterio a criterio

| Criterio | A — Shadow | B — Enforce total | C — Dos llaves | D — Escalonado |
|---|---|---|---|---|
| Riesgo P0 si key leak | **0** | **alto** | **bajo** | **bajo** (L≤3) / alto (L≥4 sin DSC-S-012) |
| Tiempo a primer receipt Merkle real | nunca | **24 horas** | 1 semana | **3–5 días** |
| Sprints desbloqueados de inmediato | 0 | todos | la mitad | **6 de 8** del backlog Forja |
| Compatibilidad doctrina actual (Manus ejecuta, Cowork canoniza) | **alta** | baja | **alta** | **alta** |
| Complejidad de implementación | **0** | baja | media-alta | media |
| Reversibilidad si falla | n/a | **baja** | media | **alta** |
| Cumple SOP/EPIA Capa 2 (Inteligencia Emergente) | **no** | **sí** | sí | parcial |
| Habilita Factory Mode con datos vivos | no | **sí** | sí | **sí** |
| Costo de no firmar hoy | bloqueo permanente | inversión perdida | inversión perdida | inversión perdida |
| Requiere DSC-S-012 firmado antes | no | **sí (crítico)** | sí (recomendado) | solo para L4–L6 |
| Dependencia Cowork siempre disponible | no | no | **sí** | no |

---

## 4. Recomendación de Hilo B (manus_b — modo detractor)

**Recomiendo Opción D — ENFORCE escalonado por Power Lane.**

No por consenso, sino por estos motivos verificables:

1. **El `types.ts` ya canoniza Power Lanes L0–L6**. Aprovechar esa estructura es Obj #7 (No Inventar Rueda).
2. **Reversibilidad real**: las acciones L≤3 son recuperables. Si una iteración del gateway tiene un bug, no se rompe producción.
3. **Mitigación P0 sin bloqueo total**: el riesgo crítico de Opción B (key leak en L5 firma destructiva) queda fuera del alcance hasta que DSC-S-012 esté firmado. Mientras tanto, las 6 de 8 lanes ya útiles operan.
4. **Cumple la doctrina actual sin reescribirla**: la frontera "Manus/Cowork como dobles factores para producción" se preserva exactamente donde importa (L≥4). Para staging y dev (L≤3), el Tablero ejecuta solo, lo que es coherente con su rol como cockpit de observación + ejecución acotada.
5. **Habilita Factory Mode con datos vivos parciales**: el panel muestra receipts reales para L0–L3 y receipts shadow para L4–L6 hasta que DSC-S-012 se firme. **No es Potemkin parcial; es transparencia total sobre qué está enforce y qué está shadow**.
6. **Reduce el scope del DSC-S-012**: en lugar de cubrir toda la superficie Forja, cubre solo L4–L6 (key rotation, auth fail-closed para producción, revocación coordinada). Eso lo hace firmable en una sola jornada Cowork, no un sprint completo.
7. **Compatible con el embrion-down actual**: el embrion_loop está fallando con `kimi-k2-6` (issue separado). Opción D no toca esa zona; Opción B sí, porque al pasar a enforce el embrion empezaría a generar envelopes activos que fallan.

Opciones A y B son extremos que la doctrina canon ya rechazó implícitamente cuando construyó Forja v4 con Power Lanes graduales. Opción C es defendible pero introduce una dependencia Cowork siempre-disponible que no escala con embriones autónomos. Opción D es el camino que el código mismo sugiere.

---

## 5. Lo que se espera de Cowork (canonizador)

Si Alfredo firma Opción D:

1. **Redactar y firmar DSC-S-012** (key rotation cadence + auth fail-closed para L4–L6 + procedimiento de revocación).
2. **Auditar el contenido del nuevo gateway condicional** antes de merge a main (DSC-G-008 v2).
3. **Canonizar en `_dsc_contracts_index.yaml`** la nueva entrada `DSC-MO-FORJA-ENFORCE-D` con cruce a este T1.
4. **Aprobar la matriz de Power Lanes** (qué tipo de acción cae en qué nivel) — esto debe quedar como tabla canónica, no como interpretación libre del gateway.

Si Alfredo firma Opción C:

1. Cowork debe construir su par Ed25519 propio y publicar la public key en el repo.
2. Cowork queda en el camino crítico de toda ejecución → riesgo de bottleneck si Cowork está fuera del loop.

---

## 6. Lo que se espera de ChatGPT (estratega — iteración 002)

**No le pidas decidir entre A/B/C/D.** Pídele:

1. **Stress test del gateway condicional Opción D**: ¿qué patrones de ataque rompen la separación L≤3 / L≥4? ¿Privilege escalation cross-lane? ¿Replay de envelopes L3 firmados como si fueran L4?
2. **Comparativa con sistemas equivalentes en producción**: ¿cómo manejan AWS IAM, Google Cloud IAM, Vault de HashiCorp y Tailscale ACLs el problema de "delegación graduada con dos firmantes"? Esto valida si la opción D es estado del arte o reinventa rueda.
3. **Articular la matriz canónica de Power Lanes**: dado el contexto del Monstruo, qué acciones específicas (deploy a Railway, write a Supabase, push a GitHub, llamada a OpenAI con presupuesto > $10, posteo en Telegram) van a cada lane L0–L6.
4. **Redactar el manifesto público** "El Monstruo firma sus propias acciones" para PR/branding cuando se publique el switch.

---

## 7. Decisión a firmar

```yaml
decision_t1_magna_005:
  forja_modo_ganador: ___  # A | B | C | D
  fecha_firma: ___
  firmante: Alfredo Góngora
  justificacion_corta: ___
  power_lanes_enforce_inicial: ___  # ej: [0, 1, 2, 3] si firma D
  power_lanes_shadow_hasta_dsc_s_012: ___  # ej: [4, 5, 6] si firma D
  dependencia_dsc_s_012: ___  # bloqueante | recomendado | no aplica
  dependencia_dsc_co_firma_cowork: ___  # solo si firma C
  fecha_revision_30_dias: ___  # auto: fecha_firma + 30d
  rollback_si_falla: ___  # criterio explícito de rollback a shadow
```

Al firmar:

1. Se commitea como `T1_MAGNA_005_FORJA_SHADOW_A_ENFORCE_FIRMADA.md` en `discovery_forense/CAPILLA_DECISIONES/EL-MONSTRUO/`.
2. Manus B abre PR al repo `tablero-campana` con el cambio del gateway condicional (si D) o del flujo de doble firma (si C).
3. Cowork recibe la lista de DSCs derivados que debe firmar (DSC-S-012 obligatorio si B/D, opcional si C).
4. Se programa revisión a 30 días para evaluar si la separación L≤3/L≥4 (D) o el doble-factor (C) funcionan con tráfico real.
5. Se actualiza `MONSTRUO_GENOME.yaml` con el campo `forja_mode: enforce_l0_l3` o equivalente.

---

## 8. Bloqueos cruzados resueltos por esta firma

- **T1-MAGNA-006** (PR Drafts autónomos del embrion): se desbloquea si firma B/C/D. Queda eternamente bloqueada si firma A.
- **DSC-S-012** (key rotation + auth fail-closed): se vuelve obligatorio si firma B; recomendado si firma C/D parcial.
- **FORJA-OMEGA-VISUAL Bloque A paso 1**: se desbloquea con cualquier firma B/C/D.
- **Sprint MOBILE_0_SMP** y **WHATSAPP_GATEWAY_P0**: indirectamente desbloqueados, ya que requieren un canal de ejecución material que hoy depende de Manus.
- **Embrion_loop autónomo**: si firma D, las acciones nightly del embrion (que hoy fallan) se canalizan vía Forja L≤3 sin requerir L4.

---

## 9. Notas finales

Este documento NO firma por ti. Solo te entrega las cuatro opciones con criterios verificables y la recomendación de Hilo B con justificación.

La firma es tuya, T1 magna, no delegable a Manus, ni a Cowork, ni a ChatGPT.

Cuando firmes, responde en este hilo o agrega el bloque YAML al final del documento. Manus B aplica el cambio al repo `tablero-campana` en menos de 1 hora si la opción es D, en 1 día si es C. Cowork puede auditar en su próximo ciclo y firmar DSC-S-012 en paralelo.

**Atención especial:** la Opción A (quedarse en shadow) es el path de menor resistencia hoy pero es el path que más cuesta a futuro: tarde o temprano alguien (un hilo, un embrion, un sabio) construirá Factory Mode encima y descubrirá que es escaparate. Si vas a quedarte en shadow, **firmarlo explícitamente** es mejor que "no firmar nada" — al menos quedará canon que el switch fue considerado y rechazado conscientemente, no olvidado.

---

**Documento generado por:** Manus B (cuenta `manus_b` — Hilo B ejecutor técnico)
**Fecha de generación:** 2026-05-26
**Bloquea:** Factory Mode real, ejecución soberana del Monstruo, autonomy scheduler con efectos materiales
**Tiempo estimado de lectura:** 6 minutos
**Thread Immunity Session:** 8af84475-598b-4d14-aa79-7d5e0c0c589c

<!-- aspiracional -->

**Estado:** Aspiracional

> Nota: este archivo es un **instrumento de firma T1 magna** — no es un DSC. El marcador aspiracional satisface DSC-G-017 para que el hook no lo trate como contrato ejecutable pendiente.

Este documento es el **resumen binario de firma rápida** del T1-MAGNA-005 articulado en `T1_MAGNA_005_FORJA_SHADOW_A_ENFORCE_PARA_FIRMA.md` (2026-05-26). Existe para que Alfredo lea ≤2 minutos, decida y firme HOY sin volver a leer el documento extenso. La articulación canónica vive en el documento original; este es solo el instrumento de decisión.

---

id: T1-MAGNA-005-RESUMEN-BINARIO
proyecto: EL-MONSTRUO
tipo: instrumento_firma_t1_magna
referencia_articulacion: discovery_forense/CAPILLA_DECISIONES/EL-MONSTRUO/T1_MAGNA_005_FORJA_SHADOW_A_ENFORCE_PARA_FIRMA.md
estado: pendiente_firma
fecha_emision: 2026-05-27
emitido_por: manus_b (Hilo B — sesión Cabina dual + DAN v1.1)
validacion_tiempo_real: completada (2026-05-27)
firmante_requerido: alfredo_gongora (T1, no delegable)

---

# T1-MAGNA-005 — Instrumento de firma binaria

> **¿Forja v4 sale de modo SHADOW (registra intents, no ejecuta) y pasa a modo ENFORCE (ejecuta sobre kernel real con envelopes Ed25519 firmados)?**

Esta es una decisión arquitectónica magna T1 no delegable. Sin tu firma, Forja v4 (2,549 líneas TypeScript ya escritas) sigue como observador puro. **El switch desbloquea Factory Mode real y T1-MAGNA-006 (PR Drafts autónomos del Embrión).** La opción que firmes determina si DSC-S-018 (key rotation + auth fail-closed) se vuelve bloqueante o gated.

## Estado verificado HOY (cross-check 2026-05-27)

| Item | Estado real verificado por Manus B hoy |
|---|---|
| Kernel `binario_100` | ✅ true, generated 2026-05-26 12:33Z, size 366 KB |
| Forja v4 código | ⚠️ Vive en branch `design/forja-os-sovereign-agentic-fabric` del repo `tablero-campana` — **NO en main todavía** |
| forjaShadowAdapter.ts | ✅ Existe (branch design) |
| 10 archivos `server/forja/*` | ✅ Verificados vía API GitHub (gateway 16 KB, router 24 KB, etc.) |
| DSC-S-018 | ✅ Canonizado (gated en este T1) y indexado en `_dsc_contracts_index.yaml` |
| Embrión-loop | ⚠️ Down con `kimi-k2-6 catalog key mismatch` (issue separado, no bloquea esta firma) |

**Implicación operativa:** Firmar Opción B/C/D implica que Manus B abre PR `design/forja-os-sovereign-agentic-fabric` → `main` en tablero-campana con el flujo enforce correspondiente. La rama design existe lista, no hay que escribir desde cero.

## Las 4 opciones en una tabla (lectura 30 segundos)

| Criterio | A — Shadow indefinido | B — Enforce total | C — Dos llaves (Alfredo+Cowork) | **D — Enforce escalonado L0-L3** |
|:---:|:---:|:---:|:---:|:---:|
| **Riesgo P0 si key leak** | 0 | **Alto** | Bajo | Bajo en L≤3 / gated en L≥4 |
| **Tiempo a 1er receipt Merkle real** | Nunca | 24h | 1 semana | **3-5 días** |
| **Sprints desbloqueados HOY** | 0 | Todos | La mitad | **6 de 8** Forja backlog |
| **Compatibilidad doctrina actual** | Alta | Baja | Alta | **Alta** |
| **Complejidad implementación** | 0 | Baja | Media-Alta | **Media** |
| **Reversibilidad si falla** | n/a | Baja | Media | **Alta** |
| **Cumple SOP/EPIA Capa 2** | NO | Sí | Sí | **Parcial-creciente** |
| **Habilita Factory Mode datos vivos** | No | Sí | Sí | **Sí (parcial transparente)** |
| **Requiere DSC-S-018 firmado YA** | No | **Sí crítico** | Recomendado | **Solo para L4-L6 (gated)** |
| **Dependencia Cowork siempre disponible** | No | No | **Sí (bottleneck)** | No |
| **Embrión-loop compatible** | Sí | Riesgo (falla activa) | Sí | **Sí (L≤3 sin tocar broken zone)** |
| **Costo de no firmar hoy** | Inversión perdida + escaparate | Inversión perdida | Inversión perdida | Inversión perdida |

## Trade-offs honestos (no consenso, postura del ejecutor)

**Opción A** es el camino de menor resistencia pero **el más caro a largo plazo**. Cualquier UI "Forja Omega" que se construya encima sería Potemkin: receipts firmados que nunca se ejecutaron. Los 2,549 líneas de Forja v4 se vuelven deuda muerta. Y el norte declarado en SOP/EPIA — *"El Monstruo ejecutando solo"* — queda permanentemente bloqueado. **Firmar A es firmar que el norte cambió.**

**Opción B** es velocidad máxima pero **un solo key leak hoy compromete producción** porque DSC-S-018 sigue gated. El frontend del Tablero puede ser hackeado (XSS, supply chain) y forzarte a firmar envelopes maliciosos sin segunda barrera. El embrión-loop actualmente fallido empezaría a generar envelopes activos fallando — agravante.

**Opción C** mitiga key leak pero **introduce a Cowork como bottleneck siempre-disponible** que no escala cuando los embriones cobren vida. Cada ejecución de cualquier nivel requiere co-firma humana. Para `autonomy_scheduler` nightly esto puede funcionar; para flujos interactivos rompe UX.

**Opción D** aprovecha que el código ya canonizó `PowerLaneLevel = 0 | 1 | 2 | 3 | 4 | 5 | 6`. Enforce solo en L0-L3 (dev, staging, staging compartido, prod-like reversible). L4-L6 (producción material, irreversible, administrativo) siguen exigiendo doble factor humano hasta que DSC-S-018 pase de gated a enforce. **El sistema mismo te dice transparentemente qué está en cada modo** — no hay zona gris.

## Mi recomendación firme — Opción D (ENFORCE escalonado L0-L3)

Recomiendo **Opción D**. Siete motivos verificables, no de fe:

1. **El código mismo sugiere el camino.** `types.ts` canoniza Power Lanes L0-L6 graduales. Aprovechar lo construido es Obj #7 (No Inventar Rueda). Cualquier otra opción ignora esta estructura.

2. **Reversibilidad real en producción.** Las acciones L≤3 son recuperables. Si una iteración del gateway tiene un bug, no se rompe producción material. B no tiene rollback fácil una vez que hay receipts Merkle reales.

3. **Mitigación P0 sin bloqueo total.** El riesgo crítico de B (key leak en L5 firma destructiva) queda fuera del alcance hasta que DSC-S-018 esté enforce. Mientras tanto, 6 de 8 lanes ya útiles operan.

4. **Compatible con doctrina actual sin reescribirla.** "Manus/Cowork como dobles factores para producción" se preserva donde importa (L≥4). Para staging y dev (L≤3), el Tablero ejecuta solo — coherente con su rol como cockpit observación + ejecución acotada.

5. **Habilita Factory Mode con datos vivos parciales y transparentes.** El panel muestra receipts reales para L0-L3 y receipts shadow para L4-L6 hasta DSC-S-018 enforce. **No es Potemkin parcial — es transparencia total sobre qué está enforce y qué está shadow.**

6. **Reduce el scope de DSC-S-018.** En lugar de cubrir toda la superficie Forja, cubre solo L4-L6 (key rotation, auth fail-closed para producción, revocación coordinada). Firmable en 1 jornada Cowork, no un sprint.

7. **Compatible con embrion-down actual.** Embrion_loop falla con `kimi-k2-6` (issue separado). D no toca esa zona; B sí, porque al pasar a enforce el embrión empezaría a generar envelopes activos que fallan.

Opciones A y B son extremos que la doctrina canon ya rechazó implícitamente cuando construyó Forja v4 con Power Lanes graduales. Opción C es defendible pero introduce dependencia Cowork siempre-disponible que no escala con embriones autónomos. Opción D es el camino que el código mismo sugiere.

## Lo que pasa el día después de firmar

| Si firmas | Acción Manus B | Acción Cowork | Plazo |
|---|---|---|---|
| **A — Shadow** | Marca T1-MAGNA-005 como `firmada_opcion_A_shadow`, retira DSC-S-018, archiva FORJA-OMEGA-VISUAL como bloqueado-por-doctrina | Acepta retiro DSC-S-018, archiva contratos derivados | 1 día |
| **B — Enforce total** | Bloqueado hasta Cowork canonice DSC-S-018 enforce | Canoniza DSC-S-018 en enforce mode (sprint completo, 5-7 días), audita gateway, redacta playbook de rotación | 1-2 semanas |
| **C — Dos llaves** | Construye flujo co-firma en gateway.ts (+200-300 líneas TS + 1 migración Drizzle) | Genera par Ed25519 propio, publica pubkey, queda en camino crítico | 1 semana |
| **D — Escalonado** | Abre PR `design/forja-os-sovereign-agentic-fabric` → `main` con gateway condicional por lane (+~100 líneas TS), tests por nivel, CI check de "no L4 sin DSC vigente" | Mantiene DSC-S-018 gated para L4-L6, canoniza matriz de Power Lanes como tabla oficial, audita PR | **3-5 días** |

Si firmas D, en menos de 1 semana hay receipts Merkle reales en `evidenceReceipts` para L0-L3, el Mission Center mobile (P0.3 del DAN v1.1) se conecta a esos receipts, y el Sprint 1 backend Cowork continúa en paralelo sin conflicto.

## Bloque YAML de firma (rellena y commitea)

```yaml
decision_t1_magna_005:
  forja_modo_ganador: ___  # A | B | C | D
  fecha_firma: 2026-05-27
  firmante: Alfredo Góngora
  justificacion_corta: ___
  power_lanes_enforce_inicial: ___  # ej: [0, 1, 2, 3] si D
  power_lanes_shadow_hasta_dsc_s_018: ___  # ej: [4, 5, 6] si D
  dependencia_dsc_s_018: ___  # bloqueante | recomendado | no_aplica
  dependencia_cowork_co_firma: ___  # solo si C: si | no
  fecha_revision_30_dias: 2026-06-26
  rollback_si_falla: ___  # criterio explícito
  thread_immunity_session_firma: ___  # opcional, si quieres trazabilidad cross-sesión
```

## Tres formas de firmar (elige una)

**Opción 1 — Respuesta inline en este hilo.** Escribe simplemente:

```text
Firmo T1-MAGNA-005 — Opción D
power_lanes_enforce: [0,1,2,3]
power_lanes_shadow_hasta_DSC-S-018: [4,5,6]
rollback_si_falla: si CI detecta envelope L>3 sin DSC vigente, reverter automático a shadow
```

Yo te respondo confirmando, escribo `T1_MAGNA_005_FORJA_SHADOW_A_ENFORCE_FIRMADA.md` en el repo con el YAML completo, abro el PR a `tablero-campana`, y notifico a Cowork.

**Opción 2 — Editar directamente este archivo.** Edita el bloque YAML arriba con tus valores, commit y push. Yo recojo el cambio en el siguiente ciclo.

**Opción 3 — Crear archivo separado.** Escribe `T1_MAGNA_005_FORJA_SHADOW_A_ENFORCE_FIRMADA.md` con el bloque YAML completo en `discovery_forense/CAPILLA_DECISIONES/EL-MONSTRUO/` y commit.

Cualquiera de las tres genera el contrato canónico. La opción 1 es la más rápida si quieres hacerlo desde el hilo móvil.

## Si decides NO firmar HOY

Está bien dormirlo. La firma sigue pendiente y el Sprint 1 backend Cowork (que **no depende de esta firma** — solo DSC-S-018 y P0.3 se ven afectados) continúa avanzando. Lo que se bloquea sin firma:

- T1-MAGNA-006 (PR Drafts autónomos del embrión) — sigue articulado, sin ejecución.
- FORJA-OMEGA-VISUAL Bloque A paso 1 — bloqueado.
- Activación de receipts Merkle reales en `evidenceReceipts` — pospuesta.
- Trust Indicator mobile no puede mostrar status real de Forja (queda mostrando "shadow" indefinido).

Lo que NO se bloquea sin firma (sigue avanzando con Cowork):

- P0.1 model_resolved + bloqueo nano.
- P0.4 ToolRegistry + ToolExecutor.
- P0.5 web_search real con cost ledger.
- P0.6 anti-ghost tests CI.
- P0.3 missions + mission_events (DSC-S-018 ya lo desbloqueó).

## Notas finales

Este resumen NO firma por ti. Solo te entrega las cuatro opciones con criterios verificables HOY (cross-check tiempo real ejecutado) y la recomendación de Hilo B con justificación.

La firma es tuya, T1 magna, no delegable a Manus, ni a Cowork, ni a ChatGPT.

**Tiempo total de lectura: ≤2 minutos.** Tiempo total para decidir y firmar inline: ≤1 minuto adicional. Total: ≤3 minutos para cerrar la decisión arquitectónica magna que desbloquea el norte de El Monstruo.

---

**Documento generado por:** Manus B (cuenta `manus_b` — Hilo B ejecutor técnico)
**Fecha de emisión:** 2026-05-27
**Sesión:** Cabina dual + DAN v1.1 + Sprint 1 arranque
**Articulación canónica original:** `T1_MAGNA_005_FORJA_SHADOW_A_ENFORCE_PARA_FIRMA.md` (Manus B, 2026-05-26)
**Validación tiempo real:** ejecutada por Manus B hoy 2026-05-27 (kernel binario_100, branch design forja-os verificado, embrión-down confirmado)
**Recomendación firme:** Opción D — ENFORCE escalonado L0-L3

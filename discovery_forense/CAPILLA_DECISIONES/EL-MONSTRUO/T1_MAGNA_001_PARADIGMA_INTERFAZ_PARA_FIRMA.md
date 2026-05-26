<!-- lint_strict -->
# T1-MAGNA-001 — Paradigma de Interfaz del Monstruo

**Tipo:** Decisión T1 Magna pendiente de firma
**Origen:** `interfaces_context_fabric` (rama `interfaces-context-fabric-001`), `CONTRADICTIONS_MAP.md` CONTRA-001
**Detectado por:** Manus B (2026-05-26) durante auditoría del backlog vs 15 OM y 8 Capas Transversales
**Estado:** Aspiracional
**Detalle estado:** pendiente de firma T1 magna; bloquea 18+ sprints del backlog y la priorización completa del roadmap UI
**Firma requerida:** Alfredo Góngora (T1 magna)

---

## 1. Resumen ejecutivo

En el repo el-monstruo coexisten dos generaciones de sprints de interfaz que **se contraponen doctrinalmente**:

- **Acto 1 — Pantallas explícitas:** la app tiene 5 a 15 superficies fijas (Daily, Cockpit, Threads, Pendientes, Conexiones, Perfil, Modos). El usuario navega entre ellas.
- **Acto 2 — Calm Tech invocacional:** la interfaz desaparece. Todo se invoca por voz, WhatsApp, gesto o ambient. Las pantallas son backstops cuando el ambient falla.

Ambos paradigmas tienen sprints firmados. Ninguno está cancelado. **El backlog crece en paralelo en dos direcciones que no caben juntas**, lo que produce:

- 6 sprints en riesgo de quemar tiempo si gana Acto 2 (Mobile Cockpit 2-5, Toggle, Portfolio UI)
- 12 sprints bloqueados esperando saber qué prioridad tienen (Listening Ambient, WhatsApp Gateway, Voice Brand, Modo Confidente, capabilities transversales)
- 0 sprints de las 6 capas transversales comerciales (porque no se sabe sobre qué transport viven)

**Esta decisión desbloquea 18+ sprints y permite ordenar el roadmap por primera vez en el ciclo completo del Monstruo.**

---

## 2. Las tres opciones binarias

### Opción A — Acto 1 gana (pantallas-first)

> "El Monstruo es una app con superficies. La voz y WhatsApp son canales secundarios."

**Sprints que se ejecutan primero:**

1. `MOBILE_REALIGNMENT_001` (cimiento)
2. `MOBILE_0_SMP` (Vault soberano)
3. `MOBILE_2_COCKPIT` → `MOBILE_3` → `MOBILE_4` → `MOBILE_5` (las 4 fases del Cockpit)
4. `DAILY_5_SUPERFICIES`
5. `COCKPIT_1`, `COCKPIT_2`, `COCKPIT_3`
6. `TOGGLE_DAILY_COCKPIT`
7. `PORTFOLIO_EMPRESAS_HIJAS_UI`
8. Después: WhatsApp, Voz, Listening como capas alternas

**Costos:**
- 4-6 sprints construyendo pantallas que la industria está abandonando (calm tech, agent-first UI)
- Riesgo de "app de power user" que solo Alfredo entiende
- Dependencia de que el usuario abra la app cada día

**Ganadores con esto:** Alfredo (control granular), Cowork (auditable), usuarios power technical

### Opción B — Acto 2 gana (calm tech invocacional)

> "El Monstruo no tiene pantallas. Tiene un escucha permanente y se invoca por voz, WhatsApp, contexto, gesto."

**Sprints que se ejecutan primero:**

1. `MOBILE_REALIGNMENT_001` (cimiento — el theme sigue importando)
2. `WHATSAPP_GATEWAY_P0` (transport conversacional principal)
3. `VOICE_BRAND_ELEVENLABS` (voz canónica)
4. `LISTENING_AMBIENT_CAPABILITY` (kill switch verbal)
5. `MODO_CONFIDENTE_UI` (deep link silencioso, sin pantalla)
6. `CAPABILITY_VAULT_SOBERANO`, `CAPABILITY_VISUAL`, `CAPABILITY_PHOTO`, `CAPABILITY_FILE`, `CAPABILITY_APP`, `CAPABILITY_HEALTH`, `CAPABILITY_SHOPPING`, `CAPABILITY_NOTES_INTELLIGENCE`
7. `SMART_RENDERING_CAPABILITY` (composición sobre 4 Catastros)
8. Las pantallas (Cockpit, Daily) se construyen mucho más tarde como backstops minimalistas

**Costos:**
- Curva de adopción más larga para usuarios no técnicos (no hay pantalla a la cual acudir)
- Latencia perceptual: requerir voz/escritura siempre puede sentirse menos directo que un tap
- Dependencia de calidad de speech-to-text y NLU en español mexicano
- Riesgo de "el Monstruo no responde" si el ambient falla y no hay UI fallback

**Ganadores con esto:** usuarios LATAM (72% no abre apps nuevas), próxima generación de productos AI-first, ChatGPT Atlas como benchmark

### Opción C — Híbrido formal con jerarquía clara

> "Hay pantallas Y hay invocación. La invocación es el modo principal; las pantallas son backstops específicas con propósito claro."

**Regla de oro propuesta:**

| Tipo de tarea | Transport principal | Pantalla backstop |
|---|---|---|
| Diálogo, preguntas, tareas conversacionales | WhatsApp + Voice | NO |
| Estado del día, qué hay que hacer | Voice + Notification | Daily 5 (minimal) |
| Auditar / configurar / power features | NO transport | Cockpit denso |
| Confidente (sensible, deep link) | Voice + WhatsApp DM | Modo Confidente UI sin nombre |
| Catastros (4 dominios persistidos) | Smart Rendering invocado | Vista de catastro on-demand |

**Sprints que se ejecutan primero:**

1. `MOBILE_REALIGNMENT_001`
2. `WHATSAPP_GATEWAY_P0` + `VOICE_BRAND_ELEVENLABS` (Acto 2 cimientos)
3. `LISTENING_AMBIENT_CAPABILITY`
4. `MOBILE_0_SMP` + `CAPABILITY_VAULT_SOBERANO`
5. `DAILY_5_SUPERFICIES` (la única pantalla del Acto 1 que sobrevive como backstop)
6. `MODO_CONFIDENTE_UI`
7. `SMART_RENDERING_CAPABILITY`
8. Capas transversales comerciales (los 6 nuevos sprints de Sprint 91.14)

**Sprints que se cancelan o difieren indefinidamente:**

- `COCKPIT_1`, `COCKPIT_2`, `COCKPIT_3` → diferidos hasta validar que Daily 5 no es suficiente
- `MOBILE_2_COCKPIT` → `MOBILE_5_COCKPIT` → cancelados (eran el Cockpit en mobile)
- `TOGGLE_DAILY_COCKPIT` → cancelado (no hay toggle si solo hay Daily)
- `PORTFOLIO_EMPRESAS_HIJAS_UI` → reemplazado por Smart Rendering

**Costos:**
- Más complejo de explicar internamente que las dos extremas
- Requiere disciplina para no "regresar al Acto 1" al menor problema del ambient
- Necesita métricas claras para saber si los backstops están sobre-utilizados

**Ganadores con esto:** balance entre ambición tecnológica y realidad operativa

---

## 3. Comparativa criterio a criterio

| Criterio | Acto 1 (pantallas) | Acto 2 (calm tech) | Híbrido |
|---|---|---|---|
| Mercado LATAM (72% no abre apps) | Mal fit | Buen fit | Buen fit |
| Tiempo a primer entregable visible | 2 semanas | 4 semanas | 3 semanas |
| Ambición tecnológica (alineado con frontera 2026) | Bajo | Alto | Alto |
| Riesgo de "app que solo Alfredo entiende" | Alto | Bajo | Bajo |
| Sprints que se cancelan | 0 | 8 | 6 |
| Sprints nuevos requeridos | 0 | 0 | 0 |
| Doctrina canon ya escrita en repo | Parcial (APP_VISION cap 1-3) | Parcial (APP_VISION cap 4-7) | Parcial (CONTRADICTIONS_MAP propone) |
| Compatibilidad con 6 nuevas capas transversales | Indirecta | Directa | Directa |
| Reversibilidad si falla | Media | Baja (mucho cancelado) | Alta |

---

## 4. Recomendación de Manus B

**Recomiendo Opción C (Híbrido formal)**, no por consenso, sino por estos motivos verificables:

1. **Reversibilidad**: si en 60 días Daily 5 demuestra ser insuficiente, se reactivan los Cockpit. Si Acto 2 falla, sigues teniendo backstops. Acto 2 puro no tiene ese rescue net.
2. **Mercado LATAM**: WhatsApp Gateway P0 te da entrada directa al 72% del mercado que no abre apps. Cockpit en mobile no.
3. **Capas comerciales**: los 6 sprints nuevos (CAPA_VENTAS, SEO, ADS, TENDENCIAS, OPS, FINANZAS) viven sobre transport agnóstico. Híbrido las soporta. Acto 1 puro las acopla a pantallas que aún no existen.
4. **Costo de cancelar es real pero bajo**: los 8 sprints diferidos en Híbrido son sprints firmados sin código todavía. Cancelarlos cuesta solo el tiempo de auditoría — no hay sunk cost.
5. **El propio CONTRADICTIONS_MAP.md ya recomendó ChatGPT articular un híbrido**: el fabric audit del 2026-05-12 (T2 Architect) explícitamente sugirió que la salida es "sequencing nuevo que conjuga ambos paradigmas". No estoy inventando opción, estoy alineando con el audit pendiente.

---

## 5. Decisión a firmar

Marca la opción y firma:

```yaml
decision_t1_magna_001:
  paradigma_ganador: ___  # A, B, o C
  fecha_firma: ___
  firmante: Alfredo Góngora
  justificacion_corta: ___
  sprints_a_cancelar: ___  # lista IDs
  sprints_a_reactivar_si_fallo: ___  # opcional, lista IDs
  fecha_revision_60_dias: ___  # auto-calcular fecha_firma + 60d
```

Una vez firmada, esta decisión:

1. Se commitea al repo el-monstruo en `discovery_forense/CAPILLA_DECISIONES/EL-MONSTRUO/T1_MAGNA_001_PARADIGMA_INTERFAZ_FIRMADA.md`
2. Manus B regenera el Tablero de Campaña aplicando los nuevos status (cancelados pasan a halo gris semi-transparente, ejecutables priorizados pasan a P0)
3. Cowork audita la decisión y firma el `CONTRADICTIONS_MAP.md` cerrando CONTRA-001 como resuelto
4. Los 18 sprints bloqueados se desbloquean según el orden de la opción ganadora
5. Se programa revisión a 60 días para evaluar si la opción funciona en la realidad operativa

---

## 6. Bloqueos cruzados resueltos por esta firma

Esta decisión también desbloquea o cierra:

- **CONTRA-001** (CONTRADICTIONS_MAP) — superficie pantallas vs invocación
- **CONTRA-002** — Cockpit vs Daily como pantalla principal
- **CONTRA-005** — Modo Confidente con UI vs sin UI
- **T1-MAGNA-003** (DECISIONS_PENDING_T1) — Modo Confidente
- **T1-MAGNA-005** — WhatsApp Gateway P0 prioridad
- **T1-MAGNA-009** — Theme migration alcance
- 6 sprints CAPA_* (Sprint 91.14) — necesitan saber qué transport prioritizar primero

---

## 7. Notas finales

Este documento NO firma por ti. Solo te entrega las tres opciones con criterios verificables y la recomendación con justificación. La firma es tuya, T1 magna, no delegable a Manus ni a Cowork.

Cuando firmes, responde en este hilo o agrega el bloque YAML al final del documento. Manus B regenera el Tablero en menos de 1 minuto y Cowork puede auditar en su próximo ciclo.

---

**Documento generado por:** Manus B (cuenta `manus_b`)
**Fecha de generación:** 2026-05-26
**Bloquea:** ejecución ordenada del backlog del Monstruo
**Tiempo estimado de lectura:** 4 minutos

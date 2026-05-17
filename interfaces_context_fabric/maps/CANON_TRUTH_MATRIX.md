# CANON_TRUTH_MATRIX — Verdad por estado canonizada

> **Iteración 001 — INTERFACES-CONTEXT-FABRIC-001**
> **Generado:** 2026-05-17
> **Propósito:** dar a ChatGPT 5.5 Pro un mapa explícito de **qué tipo de verdad** es cada afirmación que circula en el corpus, para que NO confunda hipótesis con canon ni canon con hecho operacional.

---

## Las 4 etiquetas canónicas

El fabric usa 4 etiquetas binarias que ChatGPT debe respetar al escribir specs, audits o sprints:

**CANON_VIGENTE** — afirmación firmada en documento canónico, verificable con fuente, no contradicha por audits posteriores. Tratable como verdad operativa.

**HIPOTESIS_NACIENTE** — afirmación articulada por Alfredo o un hilo Manus, NO firmada en repo, posiblemente con potencial canónico pero requiere validación. Tratable como input creativo, NO como base para code commits.

**REQUIERE_VERIFICACION** — afirmación que circula en docs o audits pero tiene fuentes incompletas, fechas ambiguas, o referencia paths que no se han verificado. Antes de usarla en código, hay que verificarla.

**CONTRADICCION** — afirmación que choca binariamente con otra fuente igualmente canónica. NO usar como base de decisiones hasta que se resuelva. Listada en CONTRADICTIONS_MAP.md.

---

## Matriz de afirmaciones magna

### Sobre identidad arquitectónica

| Afirmación | Etiqueta | Fuente |
|---|---|---|
| El Monstruo es un kernel + N transports | CANON_VIGENTE | SRC-001 Cap 1 + SRC-002 §0 |
| El Monstruo es UNA app Flutter | CONTRADICCION | sustrato pre-mayo / corregida 2026-05-11 |
| Hay 6 transports canonizados (Telegram, Flutter, Command Center, WhatsApp, Watch, La Forja) | CANON_VIGENTE | SRC-001 Cap 1 + SRC-021 |
| Existe un Transport Cero | HIPOTESIS_NACIENTE | hilos verbales, 0 hits grep |

### Sobre brand DNA

| Afirmación | Etiqueta | Fuente |
|---|---|---|
| Paleta forja + graphite + acero | CANON_VIGENTE | SRC-001 Cap 0, SRC-016, SRC-018, DSC-MO-002 |
| Paleta cyan + púrpura del Flutter actual | DEUDA_ACTIVA (deja de ser canon) | `apps/mobile/lib/theme/monstruo_theme.dart` |
| Brand DNA tiene timbre de voz mecánico (Áncora regula) | CANON_VIGENTE | SRC-004 Reloj Suizo |

### Sobre superficies

| Afirmación | Etiqueta | Fuente |
|---|---|---|
| 5 superficies Daily (Home, Threads, Pendientes, Conexiones, Perfil) | CANON_VIGENTE | SRC-001 Cap 2 |
| 15 superficies Cockpit | CANON_VIGENTE | SRC-001 Cap 3 |
| Las 20 superficies son la métrica de éxito | CONTRADICCION | choca con §9.F |
| Si abrís dashboard ya falló | CANON_VIGENTE | SRC-005 §9.F |
| Security y Fleet son superficies del Cockpit | REQUIERE_VERIFICACION | existen en Command Center, NO en lista canónica |

### Sobre capabilities

| Afirmación | Etiqueta | Fuente |
|---|---|---|
| 8 capabilities + 2 base = 10 servicios | CANON_VIGENTE | SRC-001 Cap 4 |
| Listening Ambient siempre on | CANON_VIGENTE | SRC-001 Cap 4 |
| Kill switch verbal "Monstruo apágate" | CANON_VIGENTE | SRC-001 Cap 4 |
| Cualquiera de las 13 capabilities está implementada | CONTRADICCION (canon dice deben estar / código dice 0/13) |

### Sobre Cronos

| Afirmación | Etiqueta | Fuente |
|---|---|---|
| Cronos = río de vida | CANON_VIGENTE | SRC-001 Cap 5 |
| Cronos tiene 4 modos de captura | CANON_VIGENTE | SRC-001 Cap 5 |
| 9 capas transversales personales | CANON_VIGENTE | SRC-001 Cap 5 |
| Cronos = cron scheduler | CANON_VIGENTE en otro contexto (homonimia) | skill `automation-and-scheduling` |
| Cronos = capa de memoria temporal sin metáfora del río | REQUIERE_VERIFICACION | algunos audits Cowork |
| Existe ARQUITECTURA_CRONOS_v1.md | CONTRADICCION (no existe canon estructurado) |

### Sobre seguridad

| Afirmación | Etiqueta | Fuente |
|---|---|---|
| Privacidad como física | CANON_VIGENTE | SRC-001 Cap 7 |
| 5 propiedades SMP | CANON_VIGENTE | SRC-001 Cap 7 |
| SMP es cimiento NO acelerable | CANON_VIGENTE | SRC-001 Cap 7 |
| Cero secrets en plaintext | CANON_VIGENTE | DSC-S-001 a S-005 + AGENTS.md regla 6 |
| RLS por defecto | CANON_VIGENTE | DSC-S-006 + AGENTS.md regla 7 |
| Modo confidente con discreción radical | CANON_VIGENTE | SRC-001 Cap 6 |

### Sobre Acto 2 / Calm Tech / metodologías

| Afirmación | Etiqueta | Fuente |
|---|---|---|
| Frase canónica magna §9.F | CANON_VIGENTE | SRC-005 |
| 10+2 Especialidades | CANON_VIGENTE | SRC-005 |
| 3 océanos azules (UMBRAL, ESCLUSA, Curador) | CANON_VIGENTE | SRC-005 |
| MaaS $200-500/mes | CANON_VIGENTE | SRC-005 §10 |
| Cero fee BYOK | CANON_VIGENTE pero tensión con MaaS (CONTRA-006) | SRC-001 Cap 9 |

### Sobre Reloj Suizo / Engranaje

| Afirmación | Etiqueta | Fuente |
|---|---|---|
| Mapeo 8 piezas Patek → 8 piezas Monstruo | CANON_VIGENTE | SRC-004 |
| Sprint ROTOR_001 firmado | CANON_VIGENTE | bridge/sprints_propuestos/ |
| Sprint ESPIRAL_001 firmado | CANON_VIGENTE | bridge/sprints_propuestos/ |
| El icono ⚙️ es diagrama arquitectónico literal | CANON_VIGENTE | SRC-003 |

### Sobre AI-First Living / Soberanía Contextual

| Afirmación | Etiqueta | Fuente |
|---|---|---|
| Cita verbatim Alfredo 2026-05-16 | CANON_VIGENTE como cita | hilo Manus catastro |
| AI-First Living es doctrina propia | HIPOTESIS_NACIENTE | NO commiteado |
| Soberanía Contextual existe | HIPOTESIS_NACIENTE | 0 hits grep |
| El nombre canónico en español es ___ | REQUIERE_DECISION_T1 | T1-MAGNA-007 |

### Sobre Schema-First

| Afirmación | Etiqueta | Fuente |
|---|---|---|
| Schema-First es doctrina embrionaria | HIPOTESIS_NACIENTE | skill interfaces-monstruo-doctrina |
| DSC-LF-005 firma SSE obligatorio en LLM endpoints | CANON_VIGENTE | discovery_forense/CAPILLA_DECISIONES/LA-FORJA |
| Schema-First está canonizado | CONTRADICCION (1 DSC no equivale a doctrina canonizada) |

### Sobre transports

| Afirmación | Etiqueta | Fuente |
|---|---|---|
| Bot Telegram online Sprint 27 | CANON_VIGENTE | skill el-monstruo-bot |
| Path es bot_v3.py | REQUIERE_VERIFICACION | la skill detectó posible drift |
| Flutter en App Store | CONTRADICCION (NO está, prototipo Tier-Owner) |
| Command Center en Railway con login wall | CANON_VIGENTE | gh repo el-monstruo-command-center |
| WhatsApp Gateway P0 paralelo a Flutter | CANON_VIGENTE | SRC-001 Cap 1 + SRC-002 |
| Apple Watch P1 | CANON_VIGENTE | SRC-001 Cap 1 |

---

## Reglas operativas para ChatGPT

Primero, antes de citar una afirmación en una spec o sprint, verificar la etiqueta. Si es CANON_VIGENTE, citar libremente con SRC-XXX. Si es HIPOTESIS_NACIENTE, citar con disclaimer "hipótesis pendiente de canonización". Si es REQUIERE_VERIFICACION, NO citar — primero verificar y reportar resultado al fabric. Si es CONTRADICCION, NO usar para decisiones — referir a CONTRADICTIONS_MAP.md.

Segundo, cualquier nueva afirmación que ChatGPT genere en iter 002 debe **etiquetarse explícitamente** con una de las 4 etiquetas. NO se permite afirmación sin etiqueta — eso es deuda doctrinal automática.

Tercero, el fabric mismo debe ser actualizable. Cuando una afirmación HIPOTESIS_NACIENTE se canoniza con firma T1, su etiqueta debe migrar a CANON_VIGENTE en una iteración futura del fabric. Esto es trabajo continuo, no one-shot.

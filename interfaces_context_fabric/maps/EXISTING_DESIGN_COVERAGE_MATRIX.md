# EXISTING_DESIGN_COVERAGE_MATRIX

**Generado:** 2026-05-17 (versión consolidada v2)
**Iteración:** 001 v2 (post-corrección Río de la Vida + ontología pre-IA)
**Origen:** Audits D0 (`reports/d0_legacy_audit_v3.md`) + D1 (`reports/d1_rio_vida_audit.md`)

---

## 0. Propósito

Esta matriz mapea cada **señal T1** o **propuesta de IA externa** contra cobertura existente en producción / código / sprints / canon. Sirve como **gate operativo permanente**: ninguna señal T1 nueva pasa a diseño hasta cruzar esta matriz.

Regla operativa firmada por Alfredo el 2026-05-17:

> *"Toda señal T1 nueva de Alfredo debe entrar primero como HIPOTESIS_T1 y luego mapearse contra Coverage Matrix antes de convertirse en diseño nuevo."*

---

## 1. Estados normalizados

| Estado | Significado |
|---|---|
| `PRODUCCION` | Vive en código desplegado y usable hoy |
| `CODIGO` | Existe en repo pero no en producción |
| `SPRINT_ESCRITO` | Sprint propuesto, no firmado por Alfredo, sin código |
| `CANON_VIGENTE` | Doctrina firmada y vigente |
| `CANON_HISTORICO` | Doctrina firmada en su momento, hoy obsoleta o superada (no se borra) |
| `PROPUESTO_NO_CANON` | Propuesto por Cowork/ChatGPT/Manus, no firmado por Alfredo |
| `HIPOTESIS_T1` | Señal T1 de Alfredo no canonizada |
| `HIPOTESIS_NACIENTE` | Hipótesis del fabric pendiente de validar |
| `PENDIENTE_T1` | Esperando firma o input de Alfredo |
| `CONTRADICCION` | Existe en doctrina pero contradice otro canon |
| `INVALIDADO` | Marcado falso o descartado explícitamente |
| `SOLO_TRAZABILIDAD` | Conservado por trazabilidad histórica, no operativo |
| `REQUIERE_VERIFICACION` | Mencionado pero sin evidencia firme |
| `NO_ENCONTRADO` | Cero hits en repo |

---

## 2. Matriz principal

### 2.1. Río de la Vida / Cronos / Legado

```yaml
concept_id: rio_de_la_vida
nombre_canonico: Cronos
aliases:
  - "Río de la Vida" # variante T1 de Alfredo (memoria 2026-05-17)
  - "Rio de la Vida"
  - "RÍO DE LA VIDA"
  - "river of life" # canónico Cowork audit 2026-05-11
  - "River of Life"
  - "río de Cronos" # APP_VISION cap. 5
  - "río de vida" # APP_VISION cap. 5
  - "Cronista familiar" # alias provisional ChatGPT — DESCARTADO
  - "Herencia narrativa" # alias provisional ChatGPT — DESCARTADO
  - "Legacy Capture" # alias provisional ChatGPT — DESCARTADO
  - "Day One replacement" # alias provisional Manus — DESCARTADO
  - "Memento familiar" # alias provisional — DESCARTADO
descripcion_corta: >
  Río navegable de la vida del usuario con 9 capas semánticas, modos espejo/testigo/cripta,
  Embrión Convergencia inter-capa, captura passive bajo SMP. Apuesta civilizacional.
fuente_primaria: docs/EL_MONSTRUO_APP_VISION_v1.md (cap. 5)
fuente_secundaria: memory/cowork/audits/VISION_APP_MONSTRUO_CLASE_MUNDIAL_2026_05_11.md
estado: CANON_VIGENTE
transport_relacionado:
  - Flutter Daily (río en Home como franja horizontal bajo input)
  - Flutter Cockpit (superficie densa)
  - Vision Pro (Spatial Cronos v1.2+)
relacion_acto_1: superficie del Daily (Home) y Cockpit
relacion_acto_2: capa profunda del Calm Tech (no manifesta a menos que converja)
relacion_ai_first_living: Cronos es el archivo persistente que la IA absorbe
relacion_cronos: ES Cronos
relacion_rio_de_la_vida: ES Río de la Vida (alias T1 de Alfredo)
decision_requerida: firma de CRONOS_1, CRONOS_2, CRONOS_3 + SMP + AUTH_TIERS_001
recomendacion: conservar nombre Cronos como canónico — NO renombrar a "Río de la Vida"; documentar el alias T1 de Alfredo
```

### 2.2. Modo Cripta (sub-modo de Cronos)

```yaml
concept_id: modo_cripta
nombre_canonico: Modo Cripta
aliases:
  - "Cronista Familiar" # alias provisional ChatGPT — DESCARTADO
  - "Herencia Narrativa" # alias provisional — DESCARTADO
  - "Legacy Capture" # alias provisional — DESCARTADO
  - "Day One para hijos" # alias coloquial Alfredo
sub_modos:
  - Preservación (firmado v1.1+)
  - Simulación (DIFERIDO v1.2+ con peso ético explícito)
descripcion_corta: >
  Cuando el usuario muere, su Cronos puede ser legado a herederos vía
  Shamir Secret Sharing pre-distribuido. Soberano, encriptado, navegable.
fuente_primaria: docs/EL_MONSTRUO_APP_VISION_v1.md (cap. 5)
estado: CANON_VIGENTE (Preservación) / DIFERIDO (Simulación)
transport_relacionado: cualquiera de los activos del usuario al momento del legado
decision_requerida: AUTH_TIERS_001 firmado + sprint Shamir dedicado escrito
recomendacion: conservar; NO crear capa "Legado Familiar" paralela
```

### 2.3. Memento

```yaml
concept_id: memento
nombre_canonico: Memento
aliases:
  - "MementoValidator"
  - "memory cowork"
descripcion_corta: >
  Sistema de memoria operativa del agente. Captura eventos del Monstruo,
  decisiones, audits, error_memory, validaciones, Síndrome Dory stats.
fuente_primaria: bridge/sprint_memento_preinvestigation/spec_sprint_memento.md
fuente_secundaria: docs/EL_MONSTRUO_APP_VISION_v1.md
estado: PRODUCCION (sprint COWORK_MEMENTO_001 declarado verde)
transport_relacionado: Flutter Cockpit (superficie Memento)
relacion_cronos: comparte infraestructura SMP, dimensiones distintas
recomendacion: conservar separado de Cronos
```

### 2.4. el-mundo-de-tata

```yaml
concept_id: el_mundo_de_tata
nombre_canonico: el-mundo-de-tata
aliases: []
descripcion_corta: >
  Proyecto adyacente al Monstruo. Juego interactivo estilo Toca Boca para
  la hija de Alfredo (Tata). NO es legado narrativo.
fuente_primaria: discovery_forense/PROJECT_MANIFESTS/el-mundo-de-tata.md
estado: SPRINT_ESCRITO (manifest formal, "En Construcción")
transport_relacionado: webapp móvil propia (separada del Monstruo)
relacion_cronos: ortogonal — comparte solo dimensión padre-hija
recomendacion: conservar separado; NO absorber al Monstruo
```

### 2.5. Niebla del Futuro

```yaml
concept_id: niebla_del_futuro
nombre_canonico: Niebla del Futuro
aliases:
  - "niebla del futuro"
descripcion_corta: >
  Dimensión predictiva del río de Cronos. Aguas abajo del río = futuro proyectado.
  Implementada como Embrión Convergencia inter-capa + ofrendas voluntarias.
fuente_primaria: docs/EL_MONSTRUO_APP_VISION_v1.md (cap. 5)
fuente_secundaria: memory/cowork/audits/VISION_APP_MONSTRUO_CLASE_MUNDIAL_2026_05_11.md
estado: CANON_VIGENTE (parte de CRONOS_3)
transport_relacionado: Flutter Cockpit (Cronos extendido)
recomendacion: conservar dentro de CRONOS_3
```

### 2.6. Acto 1 — 20 Superficies (Daily 5 + Cockpit 12-15)

```yaml
concept_id: acto_1_interfaces
nombre_canonico: Acto 1 — Daily + Cockpit
aliases:
  - "20 superficies"
  - "Modo Daily / Modo Cockpit"
descripcion_corta: >
  Diseño co-creado APP_VISION. Modo Daily 5 superficies (Home, Threads,
  Pendientes, Conexiones, Perfil) + Cockpit 12-15 superficies con toggle
  3-dedos+FaceID. Estado actual: 1 sola pantalla MOC vaga existe.
fuente_primaria: docs/EL_MONSTRUO_APP_VISION_v1.md (cap. 4)
fuente_secundaria: memory/cowork/audits/VISION_APP_MONSTRUO_CLASE_MUNDIAL_2026_05_11.md (§3, §4)
estado: CANON_VIGENTE (doctrina) / 0/20 (implementación)
transport_relacionado: Flutter Daily P0 + Flutter Cockpit P1
decision_requerida: firma sprints mobile_2/3/4/5/6 + SMP + REALIGNMENT_001
recomendacion: conservar; ejecutar sprints
```

### 2.7. Acto 2 — Calm Tech / Methodology-as-a-Service

```yaml
concept_id: acto_2_calm_tech
nombre_canonico: Acto 2 — Calm Tech
aliases:
  - "Methodology-as-a-Service"
  - "Reloj Suizo"
  - "Engranaje"
  - "Curaduría del Entorno Digital"
descripcion_corta: >
  Capa profunda donde el agente actúa silenciosamente. Reloj Suizo (constancia)
  + Engranaje (sincronía). Frase canónica §9.F (única fuente: SRC-005).
fuente_primaria: docs/conocimiento/metodologias_productividad/CANON_METODOLOGIAS_PRODUCTIVIDAD_2026.md
estado: CANON_VIGENTE (frase única) / HIPOTESIS_NACIENTE (capa entera)
transport_relacionado: transversal a todos los transports
decision_requerida: ¿Acto 1 y Acto 2 son secuenciales o paralelos? (T1 magna pendiente)
recomendacion: investigar más; reforzar fuentes (SRC-005 fragilidad)
```

### 2.8. AI-First Living

```yaml
concept_id: ai_first_living
nombre_canonico: AI-First Living
aliases:
  - "Schema-First"
  - "Transport Cero"
  - "Captura Reconstruible"
  - "Memoria de Estado Mental"
  - "Curaduría del Entorno Digital"
descripcion_corta: >
  Hipótesis naciente: Alfredo ya no organiza información para leerla él,
  sino para que la IA la absorba mejor y le devuelva claridad.
fuente_primaria: tests/test_catastros_interfaces.py + bridge/manus_to_cowork_REPORTE_CATASTRO_A_v2_2026_05_12.md
estado: HIPOTESIS_NACIENTE
transport_relacionado: Transport Cero (capability transversal)
decision_requerida: ¿es Acto 3 o capa transversal? (T1 magna pendiente)
recomendacion: investigar; NO canonizar todavía
```

### 2.9. Transport Cero

```yaml
concept_id: transport_cero
nombre_canonico: Transport Cero
aliases:
  - "Ontological Intake"
  - "ingesta soberana"
descripcion_corta: >
  Transport invisible. NO es ingesta de archivos; es 8 preguntas de juicio:
  Ontological Intake, Capture Heat Check, Reconstruction Sufficiency Score,
  Microcontext Prompt, Rhythm Gate, Delegation Router, Focus Guard, Memory Candidate.
fuente_primaria: NO_ENCONTRADO en código (cero hits)
fuente_secundaria: hilos Manus T1 (verbal, no escrito)
estado: HIPOTESIS_NACIENTE
transport_relacionado: precondición de todos los demás transports
decision_requerida: ¿se canoniza como capability del Monstruo? Pendiente
recomendacion: investigar más; PACK_03 lo desarrolla
```

### 2.10. Acto 0 / Origen pre-IA / Ontología 2020-2021

```yaml
concept_id: origen_pre_ia
nombre_canonico: Origen Pre-IA (provisional)
aliases:
  - "Bullet Journal manual"
  - "Índice Universal por Capas"
  - "Clasificación Universal"
descripcion_corta: >
  10 principios pre-IA-001 a pre-IA-010 que precedieron al Monstruo.
  Alfredo intentó manualmente lo que después automatizó con IA.
fuente_primaria: interfaces_context_fabric/raw_rescues/alfredo_pre_ia_checkpoint_2020_2021_DRAFT.md
estado: EN_EXTRACCION_T1 / NO_CANONIZAR
transport_relacionado: ninguno (es ontología histórica)
decision_requerida: ¿Acto 0 doctrinal o background no-doctrinal? (irreducible Alfredo)
recomendacion: NO canonizar hasta `CIERRE BLOQUE PRE-IA` de Alfredo
```

### 2.11. Engranaje + Reloj Suizo (prototipo de código)

```yaml
concept_id: engranaje_reloj_suizo
nombre_canonico: Engranaje + Reloj Suizo
aliases:
  - "scripts/prototipo_engranaje.py"
descripcion_corta: >
  Prototipo Python que aterriza la metáfora Calm Tech. Reloj = constancia,
  Engranaje = sincronía. Existe como código, no canonizado como módulo.
fuente_primaria: scripts/prototipo_engranaje.py
estado: CODIGO (prototipo, no producción)
transport_relacionado: ninguno explícito
decision_requerida: ¿se incorpora al kernel o se mantiene como sandbox?
recomendacion: investigar uso; documentar
```

### 2.12. A2UI Protocol

```yaml
concept_id: a2ui
nombre_canonico: A2UI Protocol
aliases: []
descripcion_corta: >
  Protocolo Agent-to-UI streaming. Spec firmado, primitivos en PR #92,
  renderer + 51 tests. NO es widget — es protocolo.
fuente_primaria: bridge/a2ui_protocol_spec.md
fuente_secundaria: PR #92 (no mergeado)
estado: SPRINT_ESCRITO + CODIGO (PR pendiente merge tras T8 smoke + decisión paleta)
transport_relacionado: AG-UI Gateway / Flutter
decision_requerida: merge PR #92 + decisión theme
recomendacion: ejecutar
```

### 2.13. SMP — Sprint Mobile 0

```yaml
concept_id: smp
nombre_canonico: SMP
aliases:
  - "Sovereign Memory Plane"
  - "Sprint Mobile 0"
descripcion_corta: >
  Cimiento criptográfico no acelerable. Secure Enclave + Shamir Secret Sharing
  + key rotation. Pre-requisito de TODO lo demás (CRONOS_1, AUTH_TIERS, capabilities).
fuente_primaria: bridge/sprints_propuestos/sprint_mobile_0_smp.md
estado: SPRINT_ESCRITO (no firmado)
transport_relacionado: transversal a todos
decision_requerida: firma de Alfredo URGENTE
recomendacion: priorizar máxima — bloquea todo
```

### 2.14. Command Center (existente)

```yaml
concept_id: command_center
nombre_canonico: el-monstruo-command-center
aliases: []
descripcion_corta: >
  Repo Next.js privado con 7 superficies (chat, finops, fleet, memory, runs, security, settings).
  Theme cyan #00E5FF + púrpura #BB86FC — INSPIRED ChatGPT/Claude/Gemini, drift binario contra brand DNA canon.
fuente_primaria: github.com/alfredogl1804/el-monstruo-command-center
estado: PRODUCCION (parcial) / CONTRADICCION (theme drift)
transport_relacionado: Web Command Center P2
decision_requerida: ¿migración theme o reconstrucción? (T1 magna)
recomendacion: investigar; decidir antes de iter 002
```

### 2.15. Theme: Brand DNA forja-graphite-acero

```yaml
concept_id: brand_dna
nombre_canonico: Brand DNA forja-graphite-acero
aliases:
  - "naranja forja"
  - "#F97316"
  - "graphite #1C1917"
  - "acero #A8A29E"
descripcion_corta: >
  Paleta canónica firmada. Forja = energía/decisión, graphite = soberanía/calma,
  acero = precisión/herramientas. Minimalismo Apple/Tesla.
fuente_primaria: discovery_forense/CAPILLA_DECISIONES/EL-MONSTRUO/DSC-MO-002_brand_dna_naranja_forja_graphite_acero.md
estado: CANON_VIGENTE
transport_relacionado: transversal
decision_requerida: aplicar a Command Center existente
recomendacion: ejecutar migración
```

### 2.16. Fototeca / Photo capability

```yaml
concept_id: fototeca
nombre_canonico: photo_intelligence_service
aliases:
  - "Fototeca"
  - "photo capability"
  - "álbum"
descripcion_corta: >
  Servicio Cap 4 (photo_intelligence) + fuente passive de CRONOS_1.
  NO es módulo separado.
fuente_primaria: APP_VISION cap. 4 (capabilities transversales)
fuente_secundaria: memory/cowork/audits/VISION_APP_MONSTRUO_CLASE_MUNDIAL_2026_05_11.md línea 75
estado: SPRINT_ESCRITO (0/13 capabilities implementadas)
transport_relacionado: Flutter Daily (passive) + Cockpit (manipulación)
decision_requerida: firma de Cap 4 capabilities batch
recomendacion: conservar como capability + fuente Cronos
```

### 2.17. WhatsApp Gateway

```yaml
concept_id: whatsapp_gateway
nombre_canonico: WhatsApp Gateway
aliases: []
descripcion_corta: >
  Transport P0 paralelo a Flutter Daily. Captura passive bajo CRONOS_1.
  No existe `apps/whatsapp_gateway/`. Sprint completo faltante.
fuente_primaria: APP_VISION cap. 4
fuente_secundaria: memory/cowork/audits/VISION_APP_MONSTRUO_CLASE_MUNDIAL_2026_05_11.md
estado: NO_ENCONTRADO en código / SPRINT_FALTANTE
transport_relacionado: WhatsApp P0
decision_requerida: escribir sprint + firma
recomendacion: priorizar (P0)
```

### 2.18. Modo Confidente (sin nombre)

```yaml
concept_id: modo_confidente
nombre_canonico: Modo Confidente
aliases:
  - "deep link silencioso"
  - "sin nombre"
descripcion_corta: >
  Acceso silencioso al Monstruo en momentos de crisis. Sin nombre visible,
  deep link encriptado. Convoca todas las piezas (Catastros, Embriones, Memento, Cronos).
fuente_primaria: docs/EL_MONSTRUO_APP_VISION_v1.md (cap. 5 línea 508+)
estado: CANON_VIGENTE / NO_IMPLEMENTADO
transport_relacionado: Flutter (deep link)
decision_requerida: sprint dedicado pendiente
recomendacion: conservar; sprint futuro
```

### 2.19. Embriones

```yaml
concept_id: embriones
nombre_canonico: Embriones
aliases: []
descripcion_corta: >
  9+ Embriones especializados (Critic Visual, Product Architect, Creativo,
  Estratega, Financiero, Investigador, Técnico, Ventas, Vigía, Manifestación,
  Convergencia Cronos). FCS (Functional Consciousness Score). Modo debate/quorum.
fuente_primaria: kernel/embriones/
fuente_secundaria: APP_VISION cap. 4 + audit Cowork
estado: CODIGO (parcial) / CANON_VIGENTE (doctrina)
transport_relacionado: Flutter Cockpit
recomendacion: conservar
```

### 2.20. AUTH_TIERS_001 (Owner / Trusted Circle / Funcional Accesible)

```yaml
concept_id: auth_tiers
nombre_canonico: AUTH_TIERS_001
aliases: []
descripcion_corta: >
  3 tiers de autenticación. Owner = Alfredo (Face ID + passphrase + Watch).
  Trusted Circle = invitaciones nominativas. Funcional Accesible = configuración reducida.
  Pre-requisito de Modo Cripta.
fuente_primaria: memory/cowork/audits/VISION_APP_MONSTRUO_CLASE_MUNDIAL_2026_05_11.md (Eje 8)
estado: SPRINT_ESCRITO (no firmado)
transport_relacionado: transversal
decision_requerida: firma post-SMP
recomendacion: priorizar tras SMP
```

---

## 3. Hipótesis T1 entrantes (en cuarentena hasta auditar)

| concept_id | Origen | Estado | Acción |
|---|---|---|---|
| pre_ia_001_indice_universal_capas | Checkpoint pre-IA Alfredo | EN_EXTRACCION_T1 | Esperar `CIERRE BLOQUE PRE-IA` |
| pre_ia_002_ritmo_soberano | Checkpoint pre-IA Alfredo | EN_EXTRACCION_T1 | idem |
| pre_ia_003_delegacion_clasificacion | Checkpoint pre-IA Alfredo | EN_EXTRACCION_T1 | idem |
| pre_ia_004_foco_5_objetivos | Checkpoint pre-IA Alfredo | EN_EXTRACCION_T1 | idem |
| pre_ia_005_productividad_real | Checkpoint pre-IA Alfredo | EN_EXTRACCION_T1 | idem |
| pre_ia_006_captura_reconstruible | Checkpoint pre-IA Alfredo + corrección | EN_EXTRACCION_T1 | idem |
| pre_ia_007_friccion_minima | Checkpoint pre-IA Alfredo + corrección | EN_EXTRACCION_T1 | idem |
| pre_ia_008_memoria_estado_mental | Checkpoint pre-IA Alfredo + corrección | EN_EXTRACCION_T1 | idem |
| pre_ia_009_legado_rio_de_la_vida | Checkpoint pre-IA Alfredo | EN_EXTRACCION_T1 / RESUELTO_PARCIAL | YA cubierto por Modo Cripta de Cronos |
| pre_ia_010_no_depender_habito_humano | Checkpoint pre-IA Alfredo + corrección | EN_EXTRACCION_T1 | idem |

---

## 4. Aliases provisionales descartados (ChatGPT iter 001)

| Alias propuesto | Concepto canónico real | Descarte explícito |
|---|---|---|
| "Cronista Familiar" | Cronos + Modo Cripta | DESCARTADO — usar Cronos |
| "Herencia Narrativa" | Modo Cripta de Cronos | DESCARTADO — usar Modo Cripta |
| "Legacy Capture" | Cronos passive capture (CRONOS_1) | DESCARTADO — usar CRONOS_1 |
| "Day One replacement" | Cronos | DESCARTADO — usar Cronos |
| "Memento familiar" | Cronos (Memento es operacional, NO familiar) | DESCARTADO — separar |

---

## 5. Regla operativa permanente

> **Toda señal T1 nueva entra primero como `HIPOTESIS_T1` en esta matriz. Solo después de auditar contra producción/código/sprints/canon, puede pasar a diseño.**

> **Toda propuesta de IA externa (ChatGPT, Cowork, Perplexity) entra como `PROPUESTO_NO_CANON` y debe cruzarse contra esta matriz antes de canonizar.**

---

## 6. Trazabilidad

- **Audits:** `scripts/d0_legacy_audit_v3.sh` + `scripts/d1_rio_vida_audit.sh`
- **Outputs brutos:** `reports/d0_legacy_audit_v3.md` + `reports/d1_rio_vida_audit.md`
- **Pack vinculado:** `context_packs/PACK_12_RIO_DE_LA_VIDA_EXISTING_AUDIT.md`
- **Canon Cronos:** `docs/EL_MONSTRUO_APP_VISION_v1.md` cap. 5
- **Audit Cowork:** `memory/cowork/audits/VISION_APP_MONSTRUO_CLASE_MUNDIAL_2026_05_11.md`
- **Brand DNA canon:** `discovery_forense/CAPILLA_DECISIONES/EL-MONSTRUO/DSC-MO-002_*`

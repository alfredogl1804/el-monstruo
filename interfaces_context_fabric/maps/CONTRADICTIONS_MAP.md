# CONTRADICTIONS_MAP — Mapa de tensiones doctrinales pendientes

> **Iteración 001 — INTERFACES-CONTEXT-FABRIC-001**
> **Generado:** 2026-05-17
> **Propósito:** que ChatGPT 5.5 Pro vea de un solo golpe TODAS las contradicciones que tiene que resolver en iter 002, con evidencia de qué fuentes las afirman y qué fuentes las contradicen.

---

## Cómo leer este mapa

Cada entrada tiene cuatro campos canónicos: el **eje** de la contradicción (cuál es la dimensión que está en disputa), las dos **posiciones** que entran en colisión con sus fuentes citadas, la **severidad** binaria (magna / alta / media), y la **propuesta de resolución** que ChatGPT debe firmar o rechazar en iter 002.

NO se asume que ChatGPT vaya a resolver todas. Se asume que ChatGPT va a producir una **lista priorizada** de las que sí resuelve y las que difiere para iter 003+.

---

## CONTRA-001 — La métrica de éxito de la app

| Campo | Contenido |
|---|---|
| **Eje** | ¿Qué es "el Monstruo funcionando"? |
| **Posición A** | "20 superficies funcionales y bonitas" (SRC-001 Cap 2 + Cap 3, Acto 1) |
| **Posición B** | "El usuario nunca abre nada" (SRC-005 §9.F, Acto 2) |
| **Severidad** | MAGNA — afecta sequencing de TODOS los sprints |
| **Resolución pendiente** | Las 4 hipótesis de integración (H1 Acto 2 ⊃ Acto 1, H2 modos, H3 tier-based, H4 temporal) están sin firma T1 |

---

## CONTRA-002 — Brand DNA en código

| Campo | Contenido |
|---|---|
| **Eje** | ¿Qué paleta usa el transport Flutter? |
| **Posición A** | Forja #F97316 + Graphite #1C1917 + Acero #A8A29E (SRC-001 Cap 0, SRC-016 brand_dna.py, SRC-018 design-tokens, SRC-022 DSC-MO-002 firmado) |
| **Posición B** | Cyan #00E5FF + Púrpura #BB86FC + Teal #64FFDA (`apps/mobile/lib/theme/monstruo_theme.dart` línea 5 con comentario "Inspired by ChatGPT, Claude, Gemini") |
| **Severidad** | ALTA — viola brand DNA pero el código está en prototipo Tier-Owner, no en App Store |
| **Resolución pendiente** | MOBILE_REALIGNMENT_001 firmado, NO ejecutado. Cualquier feature nueva debe consumir `packages/design-tokens/flutter/monstruo_tokens.dart` y NO el theme cyan/púrpura |

---

## CONTRA-003 — Cardinalidad de Embriones

| Campo | Contenido |
|---|---|
| **Eje** | ¿Cuántos Embriones hay? |
| **Posición A** | "10 Embriones de Dominio" (SRC-005 título de la sección) |
| **Posición B** | La sección lista 11 Embriones, no 10 (SRC-005 cuerpo) |
| **Posición C** | "9+ Embriones especializados" (SRC-001 Cap 3 superficie C5) |
| **Severidad** | MEDIA — confusión interna del corpus, no afecta código aún |
| **Resolución pendiente** | Canonizar lista única firmada, decidir si Embrión Convergencia Cronos cuenta como #11 o como meta-Embrión transversal |

---

## CONTRA-004 — Homonimia de Cronos

| Campo | Contenido |
|---|---|
| **Eje** | ¿Qué significa "Cronos"? |
| **Posición A** | Río de vida del usuario (SRC-001 Cap 5) |
| **Posición B** | Motor de scheduling/cron tasks (skill `automation-and-scheduling`) |
| **Posición C** | Capa de memoria temporal sin metáfora del río (algunos audits Cowork) |
| **Severidad** | ALTA — cualquier feature que diga "Cronos" puede referirse a 2-3 cosas distintas |
| **Resolución pendiente** | ChatGPT debe canonizar Cronos = A1 (río) y renombrar A2 (cron scheduler) a "Scheduler" / "Cron Engine". A3 se absorbe en A1 |

---

## CONTRA-005 — Acto 2 Calm Tech vs APP_VISION Cap 0 regla 2

| Campo | Contenido |
|---|---|
| **Eje** | ¿La excelencia visual es valor primario o secundario? |
| **Posición A** | "Si no es bonita no motiva" — regla inviolable #2 (SRC-001 Cap 0) |
| **Posición B** | "Si abrís un dashboard ya falló" — la UI es derrota parcial (SRC-005 §9.F) |
| **Severidad** | MAGNA — toca filosofía del producto |
| **Resolución sugerida** | Compatibles si "bonita" = "calidad cuando aparece, ausencia cuando no se necesita". La excelencia visual es lo que hace que **cuando** abrís, lo que ves no decepciona — no que abrís constantemente |

---

## CONTRA-006 — Cero fee vs MaaS pricing

| Campo | Contenido |
|---|---|
| **Eje** | ¿Cómo cobra el Monstruo? |
| **Posición A** | "Cero fee, BYOK pass-through, cero margen del Monstruo" (SRC-001 Cap 9) |
| **Posición B** | "MaaS $200-500/mes fracción de FTE" (SRC-005 §10) |
| **Severidad** | MEDIA — compatibles si BYOK paga al proveedor LLM y MaaS paga al equipo del Monstruo por la metodología instalada |
| **Resolución pendiente** | ChatGPT debe firmar DSC magno que canoniza la convivencia de ambos modelos sin ambigüedad |

---

## CONTRA-007 — Cuántos transports son P0

| Campo | Contenido |
|---|---|
| **Eje** | ¿Qué se construye primero? |
| **Posición A** | Flutter + WhatsApp en paralelo P0 (SRC-001 Cap 1, SRC-002 §0) |
| **Posición B** | Si Acto 2 gana, Watch sube a P0 y Cockpit baja |
| **Severidad** | ALTA — afecta orden de los 29 sprints por canonizar |
| **Resolución pendiente** | Depende de CONTRA-001. Si la frase canónica magna §9.F gana, Watch + WhatsApp + Voice Brand son los P0 reales y Cockpit difiere |

---

## CONTRA-008 — Web prioridad

| Campo | Contenido |
|---|---|
| **Eje** | ¿Hay un transport "Web Daily" para no-iPhone-users? |
| **Posición A** | "Web no prioritaria" (SRC-001 Cap 1) |
| **Posición B** | Command Center existe en Web — implícitamente reconoce que Web es transport viable |
| **Severidad** | MEDIA |
| **Resolución pendiente** | ChatGPT debe firmar si Web Daily se canoniza como T8 o se mantiene "no prioritaria" |

---

## CONTRA-009 — Surfaces fuera de canon en Command Center

| Campo | Contenido |
|---|---|
| **Eje** | ¿Security y Fleet del Command Center son legítimas? |
| **Posición A** | Existen en código, deben canonizarse |
| **Posición B** | NO están en lista de 15 superficies, son deuda |
| **Severidad** | MEDIA |
| **Resolución pendiente** | ChatGPT decide: canonizar (16-17 superficies Cockpit), absorber (Security → C15 Settings, Fleet → ¿C13 Hilos Manus?), o eliminar |

---

## CONTRA-010 — Discoverability del modo confidente

| Campo | Contenido |
|---|---|
| **Eje** | ¿Se hace descubrible un feature crítico? |
| **Posición A** | UX clásica: "discoverability is king" |
| **Posición B** | SRC-001 Cap 6: "discoverability would be cruelty" — quien lo necesita lo encuentra, quien no, no |
| **Severidad** | ALTA — es regla de copywriting + UX que ChatGPT debe respetar |
| **Resolución** | NO es contradicción a resolver — es regla canónica que ChatGPT debe internalizar. Listada acá para que NO la reabra |

---

## CONTRA-011 — AI-First Living: doctrina nueva o especialización

| Campo | Contenido |
|---|---|
| **Eje** | ¿AI-First Living merece doctrina propia? |
| **Posición A** | Es el centro gravitacional de cómo Alfredo opera, requiere SRC propio |
| **Posición B** | Es una especialización de Acto 2 sin estatus propio |
| **Severidad** | MEDIA — no está commiteada, vive en hilos |
| **Resolución pendiente** | ChatGPT debe firmar: ¿se commitea como `docs/AI_FIRST_LIVING_v1.md`? ¿Cuál es el nombre canónico en español? ¿Qué prompts a sabios validan la hipótesis? |

---

## CONTRA-012 — Transport Cero canonización

| Campo | Contenido |
|---|---|
| **Eje** | ¿Existe un Transport Cero? |
| **Posición A** | Mencionado verbalmente por Alfredo, encarna Acto 2 a su forma más radical |
| **Posición B** | NO commiteado al repo, 0 hits en grep |
| **Severidad** | MAGNA si se canoniza — invierte la prioridad de los 6 transports listados |
| **Resolución pendiente** | ChatGPT debe firmar si se canoniza con spec magna asociada |

---

## CONTRA-013 — Cap 17 Seguridad y Cockpit Security

| Campo | Contenido |
|---|---|
| **Eje** | ¿Seguridad es superficie o transversal? |
| **Posición A** | Transversal (SRC-001 Cap 17) — la seguridad afecta TODA la UI, no merece pestaña separada |
| **Posición B** | Command Center implementa pestaña `security` separada |
| **Severidad** | MEDIA |
| **Resolución pendiente** | Convergencia con CONTRA-009 |

---

## Métricas

| Métrica | Valor |
|---|---|
| Contradicciones magna | 3 (CONTRA-001, CONTRA-005, CONTRA-012 si se canoniza) |
| Contradicciones alta | 5 |
| Contradicciones media | 5 |
| Total | 13 |
| Resueltas en este fabric | 0 — el fabric DESCRIBE, NO PRESCRIBE |
| A resolver por ChatGPT iter 002 | 13 |
| A resolver con T1 magna | 5 (las que requieren firma de Alfredo: CONTRA-001, 002, 005, 011, 012) |

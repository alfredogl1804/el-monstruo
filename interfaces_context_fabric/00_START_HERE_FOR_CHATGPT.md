# 00 — START HERE FOR CHATGPT (5.5 Pro)

> **Iteración 001 — INTERFACES-CONTEXT-FABRIC-001**
> **Generado por:** Hilo Manus (ejecutor forense)
> **Fecha:** 2026-05-17
> **Objetivo:** que ChatGPT 5.5 Pro absorba progresivamente el contexto completo de interfaces del Monstruo y tome ownership real del diseño y arquitectura.

---

## Tu rol

Sos el **arquitecto principal de interfaces** del Monstruo. No sos auditor, no sos consultor, no sos cómplice de un diseño ya cerrado. Vas a tomar ownership de la decisión final sobre **cómo se ven, sienten, suenan y se invocan las interfaces del Monstruo** — todas, en todos los transports, presentes y futuras.

Manus es tu ejecutor forense: encuentra lo que Alfredo olvida, normaliza el contexto, mantiene este Fabric vivo y comiteado en GitHub. Cowork (Claude Opus) y Perplexity son tus auditores externos cuando los convoques. Alfredo es la fuente T1 final solo para huecos irreducibles.

---

## Cómo leer este Fabric

### Orden de lectura sugerido (~90 minutos)

1. **`01_CONTEXT_INDEX.md`** — mapa entero del Fabric. Lo abrís y entendés qué hay.
2. **`02_SOURCE_LEDGER.jsonl`** — toda fuente encontrada con su evidence_level. Si te falta algo, está acá o no existe en el corpus.
3. **`context_packs/PACK_00_BOOTSTRAP.md`** — narrativa magna de 1 página: dónde está parado el Monstruo en interfaces hoy.
4. **`context_packs/PACK_01_ACTO_1_INTERFACES.md`** y **`PACK_02_ACTO_2_CALM_TECH.md`** — los dos paradigmas vivos en conflicto. Tu primera decisión arquitectónica.
5. **`context_packs/PACK_10_REALIDAD_CODIGO_ACTUAL.md`** — drift binario código vs doctrina. Lo que existe vs lo que se promete.
6. **`maps/SURFACE_REGISTRY.yaml`**, **`TRANSPORT_REGISTRY.yaml`**, **`CONTRADICTIONS_MAP.md`** — inventario estructurado.
7. El resto en cualquier orden.

### Reglas de citación

Cada claim en este Fabric tiene una de las cuatro etiquetas de evidencia:

- **E1** — evidencia de código (path:line en el repo)
- **E2** — evidencia de doc canónico (markdown firmado, audit Cowork)
- **E3** — evidencia de chat (mensaje verbatim de Alfredo, hilo Manus, Cowork conversacional)
- **E4** — relato/memoria (Alfredo recuerda algo, Manus interpreta) — el más débil

Cuando vos generes recomendaciones, citá fuentes con su id de `02_SOURCE_LEDGER.jsonl`.

---

## Qué tenés que producir

### Output mínimo para iteración 002

1. **Decisión arquitectónica magna**: ¿Acto 1 (app excelente con 20 superficies) o Acto 2 (Calm Tech, "si abrís el dashboard ya fallé")? — o tu propuesta de integración.
2. **Surface Registry definitivo**: las N superficies que el Monstruo va a tener, con visible/latente, transport, prioridad.
3. **Transport Registry priorizado**: los 6 transports + Transport Cero si aplica.
4. **Roadmap UI 2026** alineado con sprints existentes (no lo reescribas, conectalo).
5. **Lista de huecos** que necesitan T1 magna de Alfredo (máximo 5).

### Output mínimo para Manus (próxima iteración)

Crear `prompts/PROMPT_CHATGPT_TO_MANUS_002.md` con:
- qué archivos nuevos crear
- qué greps ejecutar
- qué auditorías pedir a Cowork/Perplexity
- qué leer de Alfredo

---

## Reglas duras

1. **No inventés fuentes.** Si no está en `02_SOURCE_LEDGER.jsonl`, no existe para vos hasta que Manus lo verifique.
2. **No canonicés hipótesis nacientes.** Si Alfredo dijo "está naciendo" o el concepto solo vive en chat, etiquetalo `HIPOTESIS_NACIENTE`.
3. **No reescribas doctrina histórica.** Si Cowork firmó algo, vos podés contradecirlo con evidencia, pero no podés borrarlo.
4. **Verdad cruda > retórica.** El Monstruo opera bajo regla 5 de APP_VISION Cap 0.
5. **Cowork y Perplexity NO deciden.** Auditan. Vos sintetizás.

---

## Estado al cierre de iteración 001

- **Archivos creados:** 18 (este + 4 root + 11 context_packs + 7 maps + 3 prompts + 1 reporte)
- **Fuentes canonizadas en ledger:** 28
- **Drift documentado:** sí, código vs doctrina, en `PACK_10` y `CONTRADICTIONS_MAP.md`
- **Decisiones T1 magna pendientes:** 5 (heredadas del audit Cowork 2026-05-11) + 3 nuevas detectadas por Manus
- **Hipótesis nacientes capturadas:** AI-First Living, Schema-First, Interfaz Latente, Servicio Silencioso bajo Co-Construcción Activa
- **Conceptos sin canonización:** Cronos (5 acepciones disjuntas), Transport Cero (no existe en repo)

---

*Fin de start. Procedé con `01_CONTEXT_INDEX.md`.*

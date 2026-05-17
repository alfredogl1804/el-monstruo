# PROMPT_CHATGPT_NEXT_ITERATION.md

> Prompt magna para ChatGPT 5.5 Pro tras emisión de `CIERRE BLOQUE PRE-IA`.
> **NO ejecutar hasta que Alfredo emita literalmente la frase `CIERRE BLOQUE PRE-IA`.**

**Iteración esperada:** 002
**Reemplaza:** `PROMPT_CHATGPT_5_5_PRO_ITER_002.md` (queda como backup histórico)
**Generado:** 2026-05-17 v2 (post-audit D1 Río de la Vida + D2 drift código)

---

## §0. Contexto que ChatGPT 5.5 Pro recibe

ChatGPT recibirá:

1. Todo el contenido de `interfaces_context_fabric/` (rama `interfaces-context-fabric-001`).
2. La instrucción explícita `CIERRE BLOQUE PRE-IA` de Alfredo con sus decisiones literales sobre T1-DEC-001 a T1-DEC-013 (ver `04_DECISION_LEDGER.md`).
3. Los outputs de los 2 auditores externos (Cowork + Perplexity), si Alfredo decidió ejecutarlos antes.
4. Este prompt (PROMPT_CHATGPT_NEXT_ITERATION.md).

ChatGPT NO recibirá:
- Capacidad de canonizar nada que requiera firma T1 sin que Alfredo haya firmado en CIERRE.
- Permiso para diseñar capas nuevas sin pasar por `EXISTING_DESIGN_COVERAGE_MATRIX.md`.

---

## §1. Reglas operativas inviolables

1. **Primero buscar, después diseñar.** Toda señal nueva pasa por la Coverage Matrix antes de convertirse en diseño.
2. **NO inventar terminología.** Usar nombres canónicos (Cronos, Modo Cripta, A2UI, Transport Cero, etc.). Si proponés alias, márcalo como ALIAS_T1, no como sustituto.
3. **NO sobreescribir doctrina firmada.** APP_VISION cap. 5 (Cronos), Cap 17 (Seguridad), DSC-MO-002 (Brand DNA) son inmutables sin firma de Alfredo.
4. **Describir, NO prescribir.** Salida = análisis + opciones + trade-offs. NO instrucciones operativas para Manus o Cowork.
5. **Máximo 5 preguntas irreducibles a Alfredo al cierre.** Si necesitás más, integrarlas en grupos.

---

## §2. Tareas magna (en orden estricto)

### §2.1. Resolver las 13 contradicciones detectadas en `CONTRADICTIONS_MAP.md`

Para cada una de las 13 contradicciones, entregar:

- Resolución binaria (A o B), o tercera opción si emerge naturalmente.
- Justificación técnica + doctrinal.
- Implicación arquitectónica (qué cambia en código/sprints/skills).
- Decisión T1 asociada si la hay.

### §2.2. Articular las 13 decisiones T1 pendientes

Para cada T1-DEC del `04_DECISION_LEDGER.md`:

- Reformular como elección concreta entre 2-3 caminos.
- Identificar qué bloquea cada camino.
- Recomendar uno con justificación, NO firmar (eso es Alfredo).

### §2.3. Integrar Acto 1 ↔ Acto 2 ↔ Acto 0 (si Alfredo firmó Acto 0)

Si Alfredo confirmó en CIERRE que el origen pre-IA constituye **Acto 0** doctrinal:

- Articular cómo se relaciona Acto 0 (libreta 2020-2021) con Acto 1 (20 superficies) y Acto 2 (Calm Tech / Engranaje).
- Determinar si los 5 órganos latentes pre-IA (Índice Vivo, Clarificador, Rhythm Gate, Delegation Router, Focus Guard) son superficies del Cockpit, capabilities transversales, o capa nueva.
- Definir el sequencing: ¿Acto 0 informa Acto 1 informa Acto 2, o son simultáneos?

Si Alfredo NO confirmó Acto 0:

- Mantener pre-IA como `BACKGROUND_HISTORICO` no doctrinal.
- Las 5 frases fundacionales se preservan como cita-detonante en PACK_11 sin estatus canon.

### §2.4. Definir Transport Cero canónicamente

Salida concreta:

- ¿Es capability transversal del kernel, sprint dedicado, o categoría arquitectónica?
- Las 8 preguntas de ingesta se canonizan tal como están en PACK_03, o se reformulan.
- Reconstruction Sufficiency Score 0-5 se adopta como métrica oficial con threshold default RSS≥3 + RSS≥5 para Modo Cripta.
- Spec mínima: nombre canónico, ubicación en kernel, contrato (in/out), métricas de éxito.

### §2.5. Sequencing de los 29+ sprints pendientes

Producir sequencing definitivo:

| Orden | Sprint | Bloqueante de | Bloqueado por |
|---|---|---|---|
| 1 | ... | ... | ... |
| 2 | ... | ... | ... |

Cubrir mínimo: SMP, MOBILE_REALIGNMENT_001, sprint_mobile_2/3/4/5, sprint_THEME_MIGRATION_001, A2UI_IMPL (PR #92), CRONOS_1/2/3, AUTH_TIERS_001, sprints WhatsApp gateway si los hay.

### §2.6. 5 specs UI magna faltantes

ChatGPT debe generar specs canónicos para:

1. **Spec Toggle Daily ↔ Cockpit** (gesture + Face ID + estados).
2. **Spec Modo Cripta UX** (cómo el usuario navega legado de un fallecido — ya con Cronos firmado).
3. **Spec Transport Cero pipeline** (cómo cada captura atraviesa las 8 preguntas).
4. **Spec SMP integration** (cómo el usuario percibe el cifrado on-device).
5. **Spec Embriones Convergencia** (cómo el río inter-capa muestra patrones).

Cada spec: descripción del flujo, wireframes textuales (NO ASCII art), estados, componentes A2UI usados, manejo de errores.

### §2.7. Resolución del drift binario theme

Producir plan ejecutable de migración:

- ¿Qué archivos se modifican exactamente? (mínimo `apps/mobile/lib/core/theme/brand_dna.dart` y todos sus consumers).
- ¿Qué packages se importan desde `packages/design-tokens/`?
- ¿Cuál es el orden de migración para no romper el app durante el refactor?
- ¿Hay tests de regresión necesarios?

### §2.8. Roadmap APP_VISION v1.4

Indicar qué cambios concretos requiere APP_VISION v1.3 → v1.4:

- Capítulos a editar.
- Capítulos a agregar (Acto 0 si firmado, Transport Cero si firmado).
- Frase canónica §9.F: ¿se mueve a fuente independiente para evitar fragilidad?

---

## §3. Estructura de salida obligatoria

ChatGPT debe entregar **un solo documento markdown estructurado** llamado:

```
docs/EL_MONSTRUO_APP_VISION_v1_4_ITER_002.md
```

Con secciones obligatorias:

1. **Resumen ejecutivo** (5 párrafos máximo).
2. **Resolución de las 13 contradicciones** (tabla + justificaciones).
3. **Articulación de las 13 decisiones T1** (tabla + recomendaciones).
4. **Integración Acto 1 ↔ Acto 2 ↔ Acto 0** (si aplica).
5. **Transport Cero canónico** (spec mínima).
6. **Sequencing de sprints** (tabla ordenada).
7. **5 specs UI magna faltantes** (cada uno como sub-sección).
8. **Plan de migración drift theme**.
9. **Roadmap APP_VISION v1.3 → v1.4**.
10. **5 preguntas irreducibles para Alfredo** (al cierre).
11. **Anexos:** outputs de Cowork audit + Perplexity research integrados.

---

## §4. Restricciones magna

- **Volumen objetivo:** 30-60 páginas estructuradas. NO menos (perdería profundidad), NO más (perdería usabilidad).
- **Sin emojis, sin ASCII art, sin meta-comentarios.**
- **Citas verbatim cuando sea necesario** (especialmente APP_VISION cap. 5, audit Cowork, frases manuscritas pre-IA).
- **Lenguaje:** español rioplatense neutro (variante Alfredo). Términos técnicos en inglés solo cuando sean nombres canónicos (A2UI, SMP, Shamir Secret Sharing).
- **Cero invención de hechos.** Si una pieza de información no está en el fabric o en la doctrina firmada, marcar `[REQUIERE VERIFICACION]`.

---

## §5. Validación pre-entrega

Antes de entregar el documento, ChatGPT debe auto-validar:

1. ¿Cumple las 5 reglas operativas inviolables (§1)?
2. ¿Cubre las 7 tareas magna (§2.1 a §2.7)?
3. ¿Integra outputs de Cowork + Perplexity si fueron provistos?
4. ¿Las 5 preguntas finales son **realmente** irreducibles (es decir, no derivables de información ya provista)?
5. ¿Cita verbatim donde corresponde?
6. ¿No inventa nada que no esté en fabric o doctrina firmada?

Si alguna validación falla, ChatGPT debe re-iterar antes de entregar.

---

## §6. Post-entrega (para Manus)

Una vez ChatGPT entregue el documento iter 002:

1. Manus crea rama `interfaces-context-fabric-002` desde `main`.
2. Manus revisa el documento contra las reglas magna.
3. Si pasa, Manus prepara commit con el documento + actualiza:
   - `interfaces_context_fabric/02_SOURCE_LEDGER.jsonl` con el nuevo SRC iter 002.
   - `interfaces_context_fabric/04_DECISION_LEDGER.md` con decisiones articuladas.
   - `01_CONTEXT_INDEX.md` con referencia al documento.
4. Manus alerta a Alfredo y a Cowork para audit.
5. Alfredo decide qué se canoniza en APP_VISION v1.4.

---

## §7. Frase de cierre

> Esta iteración cierra el ciclo Acto 0 → Acto 1 → Acto 2 → AI-First Living del Monstruo. Lo que entregue ChatGPT 5.5 Pro define la doctrina UI magna del Monstruo para el resto de 2026 — o se rechaza explícitamente y se itera de nuevo.

— fin del prompt iter 002.

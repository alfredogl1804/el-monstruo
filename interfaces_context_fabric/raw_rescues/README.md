# raw_rescues — Checkpoints anti-compactación intactos

> **Propósito:** preservar verbatim los checkpoints anti-compactación que ChatGPT (u otros sabios) entregan a Manus durante extracciones T1 vivas, ANTES de que ocurra compactación de su lado.
>
> **Estado de los archivos en este directorio:** **DRAFT — EN EXTRACCIÓN T1 — NO CANONIZAR**.

---

## Reglas operativas inviolables para Manus

Primero, **NO interpretar** el contenido de estos archivos. Son rescates verbatim — Manus los preserva tal cual llegaron, sin reformatear, sin reestructurar, sin agregar interpretación.

Segundo, **NO canonizar** nada de lo que contienen. Las hipótesis, definiciones, frases fundacionales y estructuras propuestas están en extracción viva — NO son canon firmado.

Tercero, **NO cerrar** los packs vivos del Context Fabric (especialmente `PACK_11_*`) con base en este contenido. El cierre lo declara explícitamente Alfredo o ChatGPT con la frase canónica.

Cuarto, **NO ejecutar prompts parciales anteriores** del fabric (incluyendo `PROMPT_CHATGPT_5_5_PRO_ITER_002.md` y los prompts a sabios externos) hasta recibir instrucción explícita posterior al cierre del bloque pre-IA.

Quinto, cuando Alfredo declare **`CIERRE BLOQUE PRE-IA`**, ChatGPT entregará UN SOLO prompt consolidado final. Solo entonces Manus integrará este material al fabric con canonización formal.

---

## Inventario actual

| Archivo | Origen | Fecha rescue | Estado | Propósito |
|---|---|---|---|---|
| `alfredo_pre_ia_checkpoint_2020_2021_DRAFT.md` | ChatGPT (T1) | 2026-05-17 | EN EXTRACCIÓN T1 | Checkpoint anti-compactación sobre origen pre-IA del Monstruo (libreta física 2020-2021 + reflexiones actuales) |

---

## Diferencia con `context_packs/`

Los archivos de `context_packs/` son **packs interpretados y estructurados** por el hilo Manus para consumo de ChatGPT 5.5 Pro en iter 002. Son trabajo Manus.

Los archivos de `raw_rescues/` son **checkpoints intactos** entregados por sabios externos (ChatGPT, Cowork, Perplexity) al hilo Manus. Son trabajo del sabio que los originó. Manus solo los archiva.

Cuando un raw_rescue se canoniza eventualmente, se transforma en uno o más PACKs interpretados en `context_packs/`, con cita verbatim al raw_rescue original. El raw_rescue NUNCA se borra — queda como referencia histórica trazable.

---

## Trazabilidad

Cada archivo en `raw_rescues/` debe poder citarse desde cualquier punto del fabric con la sintaxis `raw://<nombre_archivo>`. La integridad de los archivos se verifica con md5sum cuando se commitea — cualquier modificación posterior a un raw_rescue es violación de protocolo y debe declararse explícitamente como `_REVISED_<fecha>.md` en archivo separado, NUNCA sobrescribiendo el original.

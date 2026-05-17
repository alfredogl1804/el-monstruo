# PACK 03 — AI-First Living / Soberanía Contextual

> **Estado:** HIPOTESIS_NACIENTE — **NO canonizar sin firma T1**
> **Fecha:** 2026-05-16
> **Origen:** Alfredo verbatim en chat con Manus Hilo Catastro (no commiteado al repo)

---

## La cita-detonante (verbatim)

> *"Todo mi actuar gira en torno a cómo le facilito a la IA las cosas para que la IA me ayude a facilitarme las mías."*
> — Alfredo González, 2026-05-16

Esta frase NO es un requirement, NO es una feature, NO es una decisión arquitectónica. Es **un patrón de vida** que Alfredo articula. Como detonador (ver skill `detonadores-alfredo`), lo que pide al hilo Manus es **que reconozca el patrón y desarrolle sus implicaciones**, no que lo procese literalmente.

---

## Articulación del patrón

El usuario opera bajo un loop simbiótico:

```
1. Yo (humano) capturo contexto de mi vida en formatos legibles para la IA
   ↓
2. La IA absorbe el contexto, aprende patrones, reciproca con valor
   ↓
3. La IA me devuelve tiempo, claridad, decisiones mejor informadas
   ↓
4. Eso me libera para capturar más contexto, mejor calidad, más rápido
   ↓
5. Loop cerrado: el sistema se vuelve más útil cuanto más lo alimento
```

Esto NO es lo mismo que "AI-Native" (la IA está en todas partes). Es **AI-First Living**: el usuario reorganiza su forma de vivir para que la IA sea el centro gravitacional de su productividad cognitiva.

---

## Implicaciones para interfaces (especulativas, requieren validación T1)

### 1. La interfaz no es para el humano — es para la IA

Los formatos en los que el humano captura información (notas, fotos, voz, gestos) deben ser optimizados para que la IA los **digiera**, no para que el humano los **revise después**. Esto invierte el design pattern habitual.

### 2. El éxito se mide en "fricción de captura", no en "engagement"

Cuanto más rápido el usuario puede dejar un dato en el Monstruo y **olvidarse** de él, mejor. Cero retención del usuario en pantalla — todo lo opuesto a la economía atencional actual.

### 3. La interfaz tiene que **anticipar el formato que la IA necesita**

Si la IA necesita una transcripción de voz con timestamps + ubicación + identificación de hablantes para hacer su trabajo bien, la interfaz captura todo eso **automáticamente, sin pedirle nada al humano**. El humano solo habla.

### 4. Cero mejor que poco

Si el usuario tiene que decidir qué formato usar para capturar algo, la interfaz ya falló. La IA decide el formato, el usuario solo provee el bruto.

---

## Conexión con Acto 2

AI-First Living es **mecánicamente compatible** con Acto 2 Calm Tech:

| Acto 2 | AI-First Living |
|---|---|
| "Si abrís dashboard, ya falló" | El usuario no abre dashboards porque la IA los lee por él |
| Listening ambient 24/7 | Captura silenciosa de contexto para alimentar a la IA |
| Voz dominante | El humano habla, la IA estructura |
| Métricas: cuántas veces NO abrís nada | Métricas: cuántos formatos NO tuviste que elegir |

**Pero AI-First Living va más allá de Acto 2**: postula que la IA es **el centro gravitacional**, no un servicio invisible al usuario. Hay un usuario que **conscientemente sirve a la IA** para que la IA le sirva a él. Esto es nuevo.

---

## Conexión con doctrina existente

### Compatible con

- SRC-001 Cap 4 (Listening Ambient continuo) — captura sin fricción.
- SRC-001 Cap 5 (Cronos como río de vida) — la IA construye memoria de tu vida sin pedir permiso constante.
- SRC-001 Cap 7 (SMP) — privacidad como física es lo que permite que el usuario alimente a la IA con su vida sin riesgo.

### Tensiona con

- SRC-001 Regla 3 (Silencio inteligente) — si la IA nunca habla, ¿cómo confirma que está absorbiendo? AI-First Living puede requerir **señales mínimas de "te entendí"** que rompan el silencio puro.
- SRC-001 Regla 4 (Describir, no prescribir) — AI-First Living tiende a **prescribir formatos** ("hablá esto, no esto") para optimizar absorción. Tensión con espejo puro.
- SRC-005 frase canónica magna — si AI-First Living requiere que el usuario aprenda **cómo alimentar mejor**, entonces sí abre algo. La pregunta es si "abrir un onboarding de alimentación" cuenta como "abrir dashboard".

---

## Enlaces con código real

| Search | Resultado | Interpretación |
|---|---|---|
| `grep -r "AI-First" .` | 1 hit relevante: `kernel/catastros/interfaces.py` (CatastroOrchestrationInterface aplica `ai_first_or_human_first` priority) | El concepto vive en código solo como flag de prioridad de selección de recursos. NO como filosofía de UX. |
| `grep -r "Soberanía Contextual" .` | 0 hits | Concepto puramente verbal. |

---

## Lo que ChatGPT 5.5 Pro debe decidir en iteración 002

1. ¿AI-First Living es **una doctrina nueva** que merece SRC propio en el repo? ¿O es una **especialización de Acto 2** sin estatus propio?
2. Si es doctrina, ¿qué nombre canónico recibe? ("AI-First Living" es inglés; "Soberanía Contextual" es ambiguo).
3. ¿Qué prompts a sabios externos validan o invalidan la hipótesis con benchmarks de mundo real (Apple Intelligence, Rabbit R1 post-mortem, Humane AI Pin post-mortem, Inflection Pi, Limitless Pendant)?
4. ¿Se traduce en **una capability nueva** (ej. "AI-First Capture Service") o en **un patrón transversal** que afecta todas las capabilities existentes?

---

## Prompts preparados para sabios externos (en `prompts/`)

Manus dejó tres prompts listos para que ChatGPT los lance cuando decida investigar AI-First Living:
- `prompts/PROMPT_PERPLEXITY_EXTERNAL_AUDITOR.md` (sección AI-First Living)
- `prompts/PROMPT_COWORK_EXTERNAL_AUDITOR.md` (sección AI-First Living)
- Plus los 3 prompts archivados en `~/forensic/prompts_sabios/` del hilo Manus actual.

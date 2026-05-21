# PERICIA GAPS TO 95 v1.2

> **Propósito:** mapear los gaps específicos que separan pericia actual (~73%) de pericia global 95%.
>
> **Fuente de verdad:** `GLOBAL_95_REQUIRED_COVERAGE_v1_2.md` define los 9 frentes. Este archivo detalla el gap por frente.
>
> **NO recalcula score.** NO declara 95. NO canoniza.

---

## Resumen ejecutivo

| Frente | Score estimado actual | Gap a 9/10 | Blocker principal |
|---|---|---|---|
| 1. Gate 3.4 | 7/10 | -2 | Confusión M4 vs M5, no distinguir endpoint vs consumidor UI |
| 2. Interfaces/Fabric | 6/10 | -3 | No lectura completa del fabric, Acto 1 vs 2 no internalizado |
| 3. APP_VISION | 7/10 | -2 | Tendencia a tratar como runtime, riesgo de proponer v1.4 |
| 4. Mobile/Flutter | 6/10 | -3 | Confundir placeholders con implementación, Brand DNA drift |
| 5. anonymous/security | 5/10 | -4 | No internalizado como BLOCKER preventivo, confusión identity layers |
| 6. SMP/Cronos/Cripta | 6/10 | -3 | Riesgo de redibujar aliases, SMP sin implementación |
| 7. PRE-IA | 7/10 | -2 | Riesgo de cerrar sin T1, canonizar hypotheses |
| 8. Command Center | 5/10 | -4 | Confundir parcial con completo, llamar control plane |
| 9. Portfolio UI | 6/10 | -3 | Afirmar implementado sin código |

---

## Gap detallado por frente

### 1. Gate 3.4

**Qué falta para 9/10:**
- Distinguir consistentemente los 5 niveles (archivo, lifespan, endpoint, consumidor, madurez)
- Internalizar caveat M4 != M5 sin recordatorio
- No afirmar production-ready sin evidencia de M5

**Evidencia de gap:** en iteraciones previas, ChatGPT afirmó módulos como "funcionando" basándose solo en existencia de archivo.

### 2. Interfaces/Fabric

**Qué falta para 9/10:**
- Lectura completa de EXISTING_DESIGN_COVERAGE_MATRIX (50+ conceptos)
- Internalizar Acto 1 vs Acto 2 como decisión T1 pendiente (no resuelta)
- Consultar ALIAS_LEDGER antes de proponer conceptos
- Entender Schema-First como hipótesis, no canon

**Evidencia de gap:** propuestas de "Cronista Familiar" en iteraciones previas demuestran no-lectura del fabric.

### 3. APP_VISION

**Qué falta para 9/10:**
- Nunca usar APP_VISION como evidencia de implementación
- Nunca proponer v1.4 sin firma T1 explícita
- Distinguir "APP_VISION dice X" de "X está implementado"

**Evidencia de gap:** en iteraciones previas, se usó APP_VISION para justificar existencia de features.

### 4. Mobile/Flutter

**Qué falta para 9/10:**
- Mapear cada superficie a su estado real (placeholder vs funcional)
- Conocer Brand DNA drift como hecho, no como opinión
- No afirmar Daily/Cockpit sin verificar código real

**Evidencia de gap:** score 70% en flutter_real del STATE v1.1.

### 5. anonymous/security

**Qué falta para 9/10:**
- Internalizar anonymous como BLOCKER preventivo (no bug, no feature)
- Conocer las 3 capas de identity (profile_id, google_sub, user_id)
- No ejecutar tests que dependan de anonymous
- Esperar clasificación T1 antes de proponer fix

**Evidencia de gap:** Night 0 detectó anonymous como default sin que el agente lo flaggeara proactivamente.

### 6. SMP/Cronos/Cripta

**Qué falta para 9/10:**
- Memorizar que SMP = Sovereign Memory Plane (no Secure Memory Protocol)
- Conocer los 4 aliases descartados sin recordatorio
- Entender que Cronos no puede implementarse sin SMP
- Conocer sprints CRONOS_1/2/3 propuestos

**Evidencia de gap:** score 55% en simulador_causal del STATE v1.1 (Cronos es parte de ese dominio).

### 7. PRE-IA

**Qué falta para 9/10:**
- Nunca cerrar PRE-IA sin frase literal T1
- Tratar hypotheses como DRAFT siempre
- Conocer el período 2020-2021 como contexto, no como doctrina

**Evidencia de gap:** riesgo latente, no incidente confirmado todavía.

### 8. Command Center

**Qué falta para 9/10:**
- Mapear las 7 superficies reales vs 12-15 canónicas
- Nunca llamar "control plane" a UI read-only
- Conocer tema en drift
- Distinguir CC actual de Cockpit canónico

**Evidencia de gap:** score 50% en command_center_real del STATE v1.1.

### 9. Portfolio UI

**Qué falta para 9/10:**
- Confirmar que portfolio view NO existe en Monstruo
- Distinguir UIs de proyectos-hijos de superficies Monstruo
- No afirmar implementación sin verificar código

**Evidencia de gap:** no evaluado explícitamente en v1.1, gap por omisión.

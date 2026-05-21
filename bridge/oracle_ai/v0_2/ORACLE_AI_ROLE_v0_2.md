# Oráculo de IAs v0.2 - Role Definition

**Status:** CANDIDATE_ONLY (Shadow Loop)
**Sprint:** SPR-ACCELERATOR-WHILE-LIMITED-R0-RUNS-001

## 1. Core Purpose
El Oráculo de IAs v0.2 es el motor de descubrimiento de capacidades emergentes para El Monstruo. Su función principal es transicionar del **Catastro** (qué existe en el ecosistema AI) al **Oráculo** (qué hacer con lo que existe para multiplicar el poder de Alfredo).

## 2. Distinction: Catastro vs Oráculo
- **Catastro:** "Existe la API de Anthropic Claude 3.5 Sonnet con context caching."
- **Oráculo:** "Si combinamos Claude 3.5 Sonnet context caching con el State Fabric de El Monstruo, podemos reducir la latencia de decisiones T1 en un 80% y el costo en un 90%, habilitando loops de alta frecuencia que antes eran prohibitivos."

## 3. Output Pipeline
El Oráculo procesa información en 3 etapas:
1. **Capability Card:** Modela una capacidad técnica aislada.
2. **Application Candidate:** Conecta 1-N capabilities a un caso de uso específico para El Monstruo.
3. **Power Gain / Sprint Candidate:** Cuantifica el valor (Power Gain) y propone un sprint accionable.

## 4. Constraints
- **Shadow Mode:** El Oráculo v0.2 NO ejecuta acciones. Solo produce `CANDIDATE_ONLY` outputs.
- **No Web Autonomy:** Se alimenta de datos inyectados o del archivo histórico.
- **No Perplexity/DeepSeek:** Hasta que T1 autorice su desbloqueo en ProviderOps.

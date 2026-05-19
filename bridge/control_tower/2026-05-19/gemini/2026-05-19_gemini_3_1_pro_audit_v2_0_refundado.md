# Auditoría Gemini 3.1 Pro — DORY-CURE v2.0 vs v1.1.1
**Fecha:** 2026-05-19
**Sabio:** Gemini 3.1 Pro
**Vía:** UI ChatGPT/Gemini (pegado por T1)
**Identificación:** verbatim "Desde la perspectiva de Gemini 3.1 Pro"

---

## E1: Complejidad vs Robustez — GANA v2.0
v1.1.1 es un Frankenstein arquitectónico. Evolucionar mediante deltas sobre un diseño defectuoso ha resultado en 13 capas acopladas que asfixiarán el kernel por I/O y latencia, intentando parchar fugas con más plomo. v2.0, con 6 componentes y filosofía Unix (do one thing well), reduce la superficie de ataque y el overhead cognitivo, siendo estructuralmente más robusto ante timeouts, aunque peque de ingenuo en la sincronización local/cloud.

## E2: Métrica de Cura — GANA v1.1.1
La métrica de v2.0 (TCC ≥0.95 en 3 corridas) es inútil porque se evalúa contra un simulador de compactación al 70%. Entrenar contra una simulación garantiza overfitting al simulador, no a la realidad del motor Manus. v1.1.1, con su CVDS ≥0.95, 1425 casos, 50 fixtures ocultos y rotación trimestral, es una defensa matemáticamente madura contra la Ley de Goodhart.

## E3: Independencia del LLM — GANA v1.1.1
v2.0 introduce el Verification Gate (VG) afirmando independizarse de la obediencia del LLM. Es una falacia: el VG solo blinda la ejecución de herramientas (side-effects). Si el LLM "olvida" el contexto textual y alucina una respuesta al usuario, el VG es ciego. v1.1.1 utiliza el VERIFICADOR-001 determinístico y escaneo de puente data-only que blinda tanto los side-effects como la semántica de entrada.

## E4: Veredicto Estructural — EMPATE (ambos colapsan, motivos distintos)
v1.1.1 morirá por asfixia de latencia (P99 > 3000ms) y cuellos de botella de red al evaluar 13 capas por turno. v2.0 morirá por desalineación con la realidad: al operar bajo la asunción de que Manus recorta el 70% de forma predecible, colapsará en el primer edge case semántico no uniforme que el motor real genere en producción. Ninguno es digno de producción 2026.

---

## Cruce con objeciones Opus 4.7
- **E3 RED (TCC overfit a simulador): CONFIRMO.** Diseñar una cura contra una simulación estática del 70% asume un recorte uniforme. Manus olvida semánticamente, no por cortes limpios. Es una métrica suicida.
- **E6 RED (VG falacia obediencia LLM): CONFIRMO.** Detener un commit o un query no impide que el agente invente hechos textuales durante un razonamiento. La capa cognitiva sigue siendo vulnerable a alucinaciones por Lost-in-the-Middle.
- **E7 RED (Fase B rompe D3): MATIZO.** El autor de v2.0 no debe leer v1.1.1 para mantener la sala limpia (D3), pero el evaluador de la métrica comparativa inevitablemente debe cruzar ambos contra los mismos fixtures. La objeción es válida para el autor, pero inválida para el árbitro.

---

## VEREDICTO GLOBAL: **FORGE_v3.0**

---

## TOP 3 Objeciones prioritarias (Gemini)

1. **Paradoja suicida del Anexo A.1 (v1.1.1):** Bypassear la compactación si el modelo tiene ≥1M tokens nativos es ignorar brutalmente Lost-in-the-Middle. Que mi KV Cache retenga 2M tokens crudos no significa que mi capa de atención extraiga el contexto correctamente. Desactivar la cura solo porque el tubo es más ancho es negligencia arquitectónica.

2. **Overfitting a la simulación de compactación (v2.0):** Manus es caja negra. Asumir emular su degradación con un script que recorta 70% destruye validez del Anchor Store. En producción, Manus puede recortar idempotency keys o hashes de verificación, dejando al VG inoperante.

3. **Latencia crítica y cascadas de timeout (v1.1.1):** 13 capas, incluso con caché Redis asíncrono, imponen carga inmanejable. La concurrencia de validaciones cruzadas superará los timeouts del bus LangGraph/FastAPI antes de curar a Dory.

---

## FORGE_v3.0 — 5 componentes propuestos por Gemini

1. **Anchor Store Híbrido (de v2.0):** Almacén de hechos e identidad, pero inyectado vía Single-Pass Router (de v1.1.1) para evitar llamadas profundas en el loop de razonamiento.
2. **Verificador Asíncrono No Bloqueante (Watcher v1.1.1):** Desacoplar validación de hechos del critical path. Verifica firmas en paralelo, rollback duro si divergencia. TTFT <50ms.
3. **Quorum Kill-Switch Local-First (v1.1.1 Capa 0):** Fallback inmediato priorizando estado local criptográficamente firmado.
4. **Adversarial CVDS Core (v1.1.1 Capa 13):** Eliminación absoluta del TCC simulado de v2.0. Validación contra DORY_BENCH real con fixtures ocultos rotativos.
5. **Contexto Estratificado (reemplazo Anexo A.1):** Ni compactación destructiva ni bypass pasivo a 2M. Últimos N turns en KV Cache puro + promoción al Anchor Store como datos recuperables (RAG determinístico ligero).

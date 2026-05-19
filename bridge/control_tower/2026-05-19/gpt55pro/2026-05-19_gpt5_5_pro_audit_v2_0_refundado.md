# Auditoría ChatGPT Pro (GPT-5.5 Pro) — DORY-CURE v2.0 vs v1.1.1
**Fecha:** 2026-05-19
**Sabio:** ChatGPT Pro / GPT-5.5 Pro
**Vía:** UI ChatGPT (pegado por T1)

---

## E1: Complejidad vs Robustez — EMPATE
v1.1.1 gana en cobertura de riesgos (kill-switch local-first, CVDS, fault injection, B1-B5, separación Fase 0/Fase 1). Pero 13 capas es frágil por acumulación: gates pueden volverse teatro sin enforcement.
v2.0 gana en claridad (6 componentes función única, implementables). Pero pierde seguridad crítica si solo cubre compactación intra-hilo y no cross-agente, bus, citas, kill-switch, benchmark adversarial y F16.
**v1.1.1 colapsa por peso; v2.0 colapsa por inocencia.**

## E2: Métrica de Cura — GANA v1.1.1
CVDS + 1425 cases + hidden fixtures + rotación trimestral es más honesto que TCC 200 con compaction simulado, porque ataca Goodhart explícito. TCC pass/fail es atractivo, pero si el simulador NO replica la compactación real Manus, mide el juguete, no la enfermedad. La métrica v2.0 sería superior solo si se prueba contra compaction real capturada de Manus, no simulación 70%.

## E3: Independencia del LLM — GANA v1.1.1
v1.1.1 no pretende que Echo-Back baste; degrada Echo-Back a defensa secundaria + VERIFICADOR-001 primary determinístico con fault injection y versionado.
v2.0 dice que VG independiza obediencia LLM si bloquea side-effects cuando no hay echo verbatim. Parcialmente falso: bloquea acciones, pero no garantiza hechos textuales, memoria narrativa, inferencias ni autoengaño en reportes.
**v2.0 confunde "no ejecutó side-effect" con "recordó bien".**

## E4: Veredicto estructural — DUAL
**v2.0 para implementación inicial; v1.1.1 para seguridad estratégica.**
"¿Qué se puede implementar y probar rápido?" → v2.0. AS/PL/AL/IAB/RH/VG es más manufacturable.
"¿Qué sobrevive a multiagente, citas falsas, Perplexity invalidado, F16, kill-switch, soberanía y benchmarks?" → v1.1.1.
Producción real 2026 no perdona ni sobreingeniería ni simplismo.

---

## Cruce con objeciones Opus 4.7
- **E3 RED (TCC overfit simulador): CONFIRMO.** "Es la objeción más fuerte contra v2.0. Sin trazas reales de compactación Manus, TCC mide una aproximación."
- **E6 RED (VG falacia obediencia LLM): CONFIRMO.** "VG puede bloquear tool side-effects, pero no cura claims falsos, resúmenes contaminados ni memoria textual inventada."
- **E7 RED (Fase B rompe D3): MATIZO.** "La rederivación limpia puede terminar antes de comparar. Después sí puede compararse contra v1.1.1. Lo incorrecto sería contaminar el diseño antes de cerrar la derivación."

---

## VEREDICTO GLOBAL: **FORGE_v3.0**

> v3.0 = núcleo funcional simple de v2.0 + garantías adversariales mínimas de v1.1.1 + métrica contra compaction real + gates positivos por riesgo + implementación sprintable.

---

## TOP 3 Objeciones (GPT-5.5 Pro)

### 1. v2.0 puede curar solo "Dory de acción", no "Dory de verdad"
AS/PL/AL/RH/VG protege hechos anclados, planes, acciones e idempotencia. Pero Dory también incluye:
- creer que entendió
- resumir mal
- inventar continuidad
- degradar criterio
- confundir fuente
- canonizar drift

Sin verificación de claims textuales, citas, decisiones y fuentes, v2.0 NO cura Dory completo.

### 2. v1.1.1 tiene riesgo de liturgia arquitectónica
B1-B5, Patch 1 local-first, CVDS están bien. Pero si todo vive como YAML/spec/gates declarativos, produce sensación de seguridad sin harness real.

### 3. Ambos pueden fallar por no probar contra compactación real
Cualquier benchmark sin muestras reales "antes/después de compactación Manus" es débil. La cura debe medirse contra:
- transcripts reales
- snapshots pre-compaction
- outputs post-compaction
- errores de continuidad detectados
- side-effects históricos
- recuperación sin reexplicación humana

---

## FORGE_v3.0 — 5 componentes obligatorios (GPT-5.5)

1. **State Core: AS + PL + AL** (de v2.0) — núcleo mínimo. Sin esto todo lo demás es retórica.
2. **Recall + Rehydration: RH con cápsula ≤8KB** (de v2.0, endurecido) — debe probarse contra compactación real Manus, no solo simulada.
3. **Verification Gate doble: Action VG + Claim VG** — corrige el error de v2.0. Action VG bloquea side-effects; Claim VG bloquea claims de alto riesgo (commit, PR, path, migración, decisión T1, cita, estado sprint, side-effect). Toma lo mejor de VERIFICADOR-001 sin cargar 13 capas.
4. **Adversarial Bench real: TCC + CVDS + traces reales Manus** — fusión TCC binario C1-C4 + CVDS anti-Goodhart + hidden fixtures + rotación + traces reales compactación Manus (obligatorio).
5. **Sovereign Kill + Key Management** (de v1.1.1) — local-first kill-switch, ed25519, private key fuera de repo, custodia T1/hardware/OS keychain, revocación, rotación, 6 escenarios Supabase/GitHub/local. Patch 1 cierra cloud dependency pero abre key management como nuevo SPOF si no se gobierna.

---

## Cierre GPT-5.5
- v1.1.1 tiene madurez doctrinal
- v2.0 tiene implementabilidad
- La cura real necesita ambas: simpleza ejecutable + verificación adversarial + pruebas contra compaction real + separación hechos/planes/acciones + soberanía local-first

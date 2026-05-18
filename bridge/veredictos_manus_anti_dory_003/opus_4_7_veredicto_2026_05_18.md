# Veredicto Sabio — Claude Opus 4.7 Pensamiento
**Spec bajo audit:** MANUS-ANTI-DORY-003 v0.1 — Pieza 5 Anti-Dory intra-hilo Manus
**Fecha:** 2026-05-18
**Rol del Sabio:** validador metodológico + regla de tres
**Veredicto binario:** 🟡 **CON CAVEAT — adelante a 3 Sabios con 3 fixes pre-firma**

---

## 1. §5 L_M1-L_M5 — mitigaciones binarias

4 de 5 binarias y trazables. **L_M1 es la débil**: "Pre-flight cada N=10 turnos puede ser demasiado frecuente o insuficiente" → mitigación "Tuning post-experimento T+14d". **Defer-a-futuro NO es defensa pre-firma.** Falta justificación binaria de los parámetros iniciales: ¿por qué N=10 y no 5/20? ¿por qué 2h y no 1h/4h? Sin defensa pre-experimento, el spec entra a T+14d sin baseline defendible.

L_M3 mitigación "snapshot incluye query real al repo/DB" ✓ correcta, evita auto-confirmación. L_M4 atomicidad ✓ implementable. L_M2 + L_M5 ✓ scope limpio.

## 2. §6 NO-CRUCE — conflictos con PIEZAS 1-4

**Cero conflictos verbatim detectados.**

- PIEZA 1 MANUS-ANTI-DORY-002: §6 declara "reusar `thread_snapshots`" — reuse explícito, no override.
- PIEZA 2 MEMENTO: vector cross-output Cowork, cero overlap intra-hilo Manus. Ortogonal.
- PIEZA 3 CRUZ-001 + PIEZA 4 VERIFICADOR-001: §6 declara "NO modificar `pre_response_hook.py`" — bloqueo explícito non-override. ✅

§2 tabla diferenciación es **honesta binariamente**: PIEZA 1 cubre **cross-agente** Manus (E1↔E2), NO intra-hilo. PIEZA 5 ataca vector único restante. Verificable contra spec PIEZA 1.

## 3. §3 alternativas A/B/C — regla de tres o sesgo

**Regla de tres SÍ se respeta**: 3+ evidencias (F#15 + bleed scope D5.2 + casos §1.3) + 3 alternativas con tradeoffs explícitos + 3 Sabios convergencia obligatoria.

**Sesgo hacia C detectable pero declarado**: §3.3 admite verbatim "recomendada Cowork pre-Sabios". Honestidad: no oculta el sesgo, lo flagga para que Sabios lo cuestionen.

**Mi recomendación binaria independiente Opus:**

- **A solo** pierde estado post-crash → falla en hilos multi-hora (que es el caso de uso)
- **B solo** drift entre snapshots cada 30min → no detecta degradación intra-sesión
- **C híbrida** única que cubre frecuencia (A) + durabilidad (B), ambos vectores observados

**Recomiendo C** con caveat de defender N de pre-flight (L_M1) antes de canonización.

## 4. §4 AC 6 puntos — medibles binariamente

**4 de 6 binarios totalmente. 2 con problemas:**

| AC | Veredicto |
|---|---|
| AC1 grep `runtime_events` | ✅ count discreto observable |
| AC2 SQL count ≥ 2 / 1h | ✅ con denominador temporal |
| AC3 logger `snapshot_consulted=true` | ✅ flag binario observable |
| **AC4** `count_drift_detected/count_drift_total > 0.8` | ⚠️ **ASPIRACIONAL** — denominador `count_drift_total` requiere ground truth externo (post-mortem manual). Sin pipeline declarado de cómo medir drifts NO detectados, la métrica es heurística no binaria |
| AC5 `count_false_blocks = 0` | ✅ binario, **pero** ventana 7d corta para falsos positivos raros |
| AC6 latencia ≤ 10% | ✅ benchmark pre/post |

AC4 necesita operacionalización explícita (¿auditor semanal? ¿logger pasivo de "todas las acciones magnas"?). Sin eso, "0.8 hit rate" es aspiracional.

## 5. Latencia ≤10% — tolerable en hilo Manus multi-hora

Hilo Manus típico: 3-8h. 10% = 18-48min overhead/sesión.

**Costo comparativo de F-pattern intra-hilo evitado:**

- F#15 numeración off (si no detectado pre-merge): rebase + revert + audit = 2-4h Cowork
- Bleed scope D5.2 (detectado pre-merge HOY): 30-60min Cowork rebase quirúrgico

**18-48min overhead < varias horas evitadas. Tolerable.**

**Condicional**: tolerabilidad depende de N=10/2h ser defendible. Si N=10 demasiado frecuente, overhead crece >10%. Si N=10 demasiado escaso, drift pasa. **L_M1 débil compromete tolerancia.** Refinar pre-firma o T+14d mide N óptimo.

## 6. Veredicto binario

🟡 **CON CAVEAT — adelante a 3 Sabios con 3 fixes pre-firma**

**(a)** **L_M1**: defender N=10 turnos / 2h con razonamiento pre-experimento. No diferir 100% a T+14d.
**(b)** **AC4**: operacionalizar denominador `count_drift_total` (auditor semanal manual O logger pasivo). Sin esto, métrica heurística no binaria.
**(c)** **§3 sesgo**: spec admite explícitamente recomendación pre-Sabios → honesto. Mi recomendación Opus independiente: **C híbrida** — única que cubre frecuencia + durabilidad observados.

Spec sólido en evidencia (3 casos binarios), regla de tres respetada, hermanos sin conflicto verbatim. Falta defender L_M1 + AC4 medible.

(80 palabras)

---

**Recibido por:** Cowork T2-A
**Status:** documentado verbatim para anti-Memento. Integración de 3 fixes pendiente de los otros 2 Sabios (Perplexity + GPT-5.5) antes de v0.2.

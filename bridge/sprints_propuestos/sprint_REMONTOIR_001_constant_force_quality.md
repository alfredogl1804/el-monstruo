<!-- lint_strict -->

# Sprint REMONTOIR-001 — Constant Force Quality Floor (pieza magna #8 Reloj Suizo)

**estado:** FIRME T2-A bajo autoridad T1 delegada ("si continua con tareas grandes" 2026-05-12 ~08:08 UTC)
**fecha_borrador:** 2026-05-12
**fecha_firma_T2-A:** 2026-05-12 ~08:10 UTC
**autor_borrador:** Cowork T2-A bajo autoridad T1 delegada — magna paralela cierre Reloj Suizo doctrinal
**pendiente_firma_T1:** Alfredo puede revocar o convergir en próximo turno
**Hilo principal candidato:** Manus Hilo Ejecutor 2 (continuidad Reloj Suizo post-ESPIRAL-001)
**ETA recalibrado:** 90-130 min reales — más grande que ROTOR/ESCAPE/ESPIRAL porque requiere wiring multi-Sabio
**Objetivo Maestro:** #2 (Calidad Apple/Tesla) + #11 (Autonomía progresiva) + #12 (Soberanía — fallback no depende de un único provider)
**Bloqueos pre-arranque:** ESPIRAL-001 cerrado (REMONTOIR opera con Hairspring activo para detectar quality degradation real-time)
**Resultado esperado:** pieza Remontoir del Reloj Suizo implementada. **Cierra la 8va pieza del Reloj Suizo** — completa la doctrina horológica. Garantiza calidad constante del output del agente sin importar si daily_cap_remaining está al inicio o al final del día. Aplica fallback automático Premium → Standard → Open-source preservando quality_floor declarado.

---

## 0. Audit pre-sprint (DSC-G-008 v3 §1)

**Estado actual binario verificado por Cowork 2026-05-12 ~08:10 UTC:**

```bash
ls kernel/remontoir kernel/constant_force  → NO EXISTEN
grep -rln "remontoir\|constant_force\|quality_floor" kernel/  → CERO HITS
```

**Las 8 piezas — estado post-ESPIRAL-001 (hipotético):**

| # | Pieza | Estado proyectado |
|---|---|---|
| 1 Resorte | `kernel/embrion_budget.py` | ✅ existe |
| 2 Escape | `kernel/escape/` | ⏳ post-ESCAPE-001 merge |
| 3 Áncora | `kernel/embrion_scheduler.py` | ✅ existe |
| 4 Volante | `kernel/embrion_loop.py` | ✅ existe |
| 5 Espiral | `kernel/espiral/` | ⏳ post-ESPIRAL-001 merge |
| 6 Rotor | `kernel/rotor/` | ⏳ post-ROTOR-001 merge |
| 7 Rubíes/Caché | `kernel/response_cache.py` | 🟡 parcial — sprint posterior expansión RUBIES-001 |
| 8 **Remontoir** | NO existe | ❌ **este sprint cierra el Reloj Suizo** |

**REMONTOIR-001 es la pieza #4 magna doctrinal — última pieza estructural del Reloj Suizo 8 piezas canónicas.**

---

## 1. Procedencia doctrinal

`docs/ARQUITECTURA_RELOJ_SUIZO_v1.0.md` §2.1 verbatim:

> "**Remontoir (Constant Force):** Innovación de Greubel Forsey: iguala la fuerza entregada al escape sin importar si el resorte está lleno o vacío → **Estabilizador de Calidad:** Garantiza que el output del agente sea igual de bueno al final del día (presupuesto bajo) que al principio, ajustando el modelo (fallback) dinámicamente."

En horología: el Remontoir es la pieza más cara y rara — Greubel Forsey, Audemars Piguet, Patek invierten décadas en perfeccionarla. Resuelve un problema fundamental: el resorte de un reloj mecánico entrega más fuerza cuando está cargado al máximo que cuando se está descargando. Sin Remontoir, el reloj atrasa el final del día. Con Remontoir, oscila exactamente igual desde la primera hora hasta la última.

Aplicado a IA agéntica: cuando `daily_cap_remaining` está alto, el agente puede usar GPT-5.5 Pro reasoning=high (caro pero alta calidad). Cuando baja, debería degradar a Sonar o Gemini 3.1 Pro automáticamente. PERO debe mantener **quality_floor declarado** — el output mínimo aceptable. Si Standard no puede mantenerlo, escala a Open-source Heavy (DeepSeek R1, Kimi K2.6). Si tampoco, **abort grácil con human-loop request** en lugar de generar slop.

Resultado: agente entrega **calidad CONSTANTE** desde la primera query del día hasta la última — pieza que da CALIDAD APPLE/TESLA absoluta (Obj #2 cumplido estructuralmente).

---

## 2. Tareas del Sprint (T1-T7)

### T1 — Migración SQL `embrion_quality_floor_log` (15-20 min)

**perfil_riesgo:** write-risky

`migrations/sql/00XX_embrion_quality_floor_log.sql` (probable 0028 post-ESPIRAL 0027):

```sql
CREATE TABLE IF NOT EXISTS public.embrion_quality_floor_log (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    consumer TEXT NOT NULL,
    budget_remaining_at_request NUMERIC(10, 6) NOT NULL,
    quality_floor_required NUMERIC(3, 2) NOT NULL CHECK (quality_floor_required BETWEEN 0 AND 1),
    model_attempted TEXT NOT NULL,                       -- p.ej. 'gpt-5.5-pro-reasoning-high'
    model_delivered TEXT NOT NULL,                       -- p.ej. 'gemini-3.1-pro' tras fallback
    quality_estimated NUMERIC(3, 2) NOT NULL CHECK (quality_estimated BETWEEN 0 AND 1),
    fallback_chain JSONB NOT NULL,                       -- [{model, reason, cost, latency_ms}, ...]
    veredicto TEXT NOT NULL CHECK (veredicto IN ('delivered_high', 'delivered_floor', 'aborted_human_loop')),
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_quality_floor_log_created
    ON public.embrion_quality_floor_log (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_quality_floor_log_consumer
    ON public.embrion_quality_floor_log (consumer);

ALTER TABLE public.embrion_quality_floor_log ENABLE ROW LEVEL SECURITY;
CREATE POLICY IF NOT EXISTS quality_floor_log_service_role_only
    ON public.embrion_quality_floor_log FOR ALL TO service_role USING (true);
```

### T2 — Core Remontoir `kernel/remontoir/constant_force.py` (30-40 min)

**perfil_riesgo:** write-risky (corazón de calidad del sistema — más sensible que ROTOR/ESCAPE/ESPIRAL)

```
kernel/remontoir/
  __init__.py
  constant_force.py     # clase Remontoir + ensure_quality_floor()
  fallback_chain.py     # cadena canónica de fallback de los 8 Sabios
  quality_estimator.py  # estima quality_score del output sin LLM-as-judge costoso (heurísticas)
  human_loop.py         # invocación interfaz humana cuando fallback chain agota sin alcanzar floor
```

API canónica:

```python
class Remontoir:
    def __init__(self, quality_floor: float = 0.7, max_fallback_depth: int = 4):
        self.quality_floor = quality_floor
        self.max_fallback_depth = max_fallback_depth

    async def ensure_quality_floor(
        self,
        prompt: str,
        ideal_model: str,
        budget_remaining: Decimal,
    ) -> dict:
        """Itera fallback_chain hasta encontrar modelo que cumple quality_floor + budget.
           Si no encuentra, retorna 'aborted_human_loop'. Registra en embrion_quality_floor_log."""
```

**Fallback chain canónica de los 8 Sabios (DSC-V-001):**

1. GPT-5.5 Pro reasoning=high (calidad ~0.95, costo ~$0.30/req)
2. Claude Opus 4.7 reasoning=high (calidad ~0.94, costo ~$0.25/req)
3. Gemini 3.1 Pro reasoning=high (calidad ~0.92, costo ~$0.15/req)
4. Kimi K2.6 Thinking (calidad ~0.88, costo ~$0.08/req)
5. DeepSeek R1 (calidad ~0.85, costo ~$0.02/req)
6. Sonar Pro Standard (calidad ~0.80, costo ~$0.03/req)
7. Grok 4 Heavy (calidad ~0.85, costo ~$0.12/req — solo si pregunta requiere datos X/Twitter o adversarial)
8. Copilot 365 (calidad ~0.78, costo ~$0.02/req — solo si pregunta requiere integración M365)

Si ninguna combinación model+budget cumple quality_floor → `aborted_human_loop` con explicación al usuario.

### T3 — Wiring Remontoir al Áncora + Volante (20-25 min)

**perfil_riesgo:** write-risky (toca pipeline de LLM calls)

Marcadores REMONTOIR_BEGIN/END donde se invoca LLM externamente.

### T4 — Quality estimator heurístico (20-30 min)

**perfil_riesgo:** write-safe

Estimar quality_score de output SIN llamar a otro LLM como juez (que sería caro recursivo). Heurísticas:
- Longitud razonable (no truncated)
- Coherencia gramatical básica (regex)
- Presencia de hedging phrases ("podría", "posiblemente" — bajan score si excesivos)
- Presencia de citations/sources si la query lo requería
- Detección de hallucination patterns conocidos (URLs sospechosas, fechas futuras anómalas)

v1: heurísticas simples. v2 (sprint posterior): LLM-as-judge solo en sampling 10%.

### T5 — Human loop interface (15-20 min)

**perfil_riesgo:** write-safe

Cuando Remontoir agota fallback sin alcanzar floor, abrir bridge file:
`bridge/human_loop_requests/<timestamp>_remontoir_aborted_<consumer>.md` con:
- Prompt original
- Modelos intentados + reason de cada uno
- Razón abort (budget insuficiente / quality_floor inalcanzable)
- Sugerencia: aumentar budget / reducir quality_floor / esperar siguiente día

App Flutter posterior leerá ese directorio y notificará al usuario.

### T6 — Dashboard Remontoir `kernel/dashboards/remontoir_history.py` (15-20 min)

Visualiza:
- 24h/7d/30d veredicto distribution (delivered_high vs delivered_floor vs aborted_human_loop)
- Fallback depth histogram
- Cost saved per día por fallback automático
- Quality estimated trend

### T7 — Postmortem placeholder + DSC-MO-016 candidato (10 min)

DSC-MO-016 candidato: **Quality floor declarativo per-consumer**. Algunos consumers necesitan floor 0.9 (decisiones magnas), otros 0.6 (rate-limited bulk processing). Tabla de defaults canonizada.

---

## 3. Contratos ejecutables que adjunta

| DSC enforzado | Contrato producido | Archivo |
|---|---|---|
| DSC-MO-006 v1.1 (doctrina del silencio) | Marcadores REMONTOIR_BEGIN/END | T3 |
| DSC-MO-010 (Reloj Suizo completo) | 8va pieza estructural cerrada | `kernel/remontoir/` T2 |
| DSC-V-001 (8 Sabios canónicos) | Fallback chain según versiones canonizadas | T2 |
| DSC-G-008 v3 (deducir consecuencias) | §4 deducción aplicada | §0 + §3 + §4 |
| DSC-S-006 v1.1 | embrion_quality_floor_log RLS | T1 |
| DSC-S-012 | Migración main pre-prod | T1 |
| DSC-MO-011 (Embryo Patch Lane) | Marcadores reversibles | T3 |

---

## 4. Criterios de cierre verde (Sprint completo)

- 7 tareas exit 0 + artifacts + tests verde
- 30+ tests passing sin DB ni red
- Quality floor configurable + observable en dashboard
- Fallback chain tested con 5+ modelos canónicos
- Human loop interface funcional
- Cowork audita DSC-G-008 v3 verde + T2-B PBA convergente
- Frase canónica: `⚖️ REMONTOIR-001 — DECLARADO (7/7 verde) — Reloj Suizo 8/8 piezas estructurales CERRADO`

**Este sprint MERECE celebración doctrinal** — cierra estructuralmente las 8 piezas del Reloj Suizo. Manus + Cowork + Sabios pueden seguir mejorando cada pieza, pero la estructura horológica del Monstruo queda completa.

---

## 5. Owner candidato y timing

**Owner técnico:** Manus Hilo Ejecutor 2 (cierre simbólico Reloj Suizo)
**Owner arquitectónico:** Cowork T2-A (audit DSC-G-008 v3) + Perplexity T2-B (PBA verificación)
**Owner humano final:** Alfredo T1 (firma + celebración doctrinal — Obj #2 Apple/Tesla cumplido estructuralmente)
**Timing:** post-ESPIRAL-001 cerrado. Estimado 2026-05-14 si pipeline Reloj Suizo avanza a velocidad reciente.

---

## 6. Trazabilidad

- Origen: `docs/ARQUITECTURA_RELOJ_SUIZO_v1.0.md` §2.1 verbatim
- Predecesores: ROTOR-001 + ESCAPE-001 + ESPIRAL-001
- Sucesor: RUBIES-001 (expansión pieza #7 caché semántica — mejora continua, no requisito estructural)
- Delta esperado Obj global: +3-4 pts (Obj #2 + #11 + #12)

---

**Estado:** FIRME T2-A 2026-05-12 ~08:10 UTC. Pendiente firma T1 explícita. Kickoff a Manus Ejecutor 2 PENDIENTE — espera cierre ESPIRAL-001 + firma T1 ratificada.

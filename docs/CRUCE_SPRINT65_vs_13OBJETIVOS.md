# Cruce Sprint 65 vs. 13 Objetivos Maestros — Modo Detractor

**Fecha:** 1 mayo 2026
**Autor:** Manus AI (Modo Detractor Activado)
**Metodología:** Análisis crítico no complaciente. Cada épica se evalúa buscando debilidades, riesgos, y áreas de oportunidad.

---

## Score de Confianza del Plan

**7.5/10** (antes de correcciones)

Justificación: Sprint 65 tiene ambición correcta — ataca los 4 objetivos más rezagados directamente. Sin embargo, hay riesgos significativos en la Voice Interface (latencia real), el Apple HIG Benchmark (subjetividad del LLM), y la Emergence Evidence (definición circular). Las correcciones son mandatorias para que el sprint sea ejecutable.

---

## Análisis por Objetivo

### Obj #1 — Crear Empresas Reales (91% → 91%)

**Impacto directo:** NULO.

**Crítica positiva:** Sprint 65 no toca Obj #1 directamente, pero la Multi-Region UX (65.1) habilita crear empresas en MÁS mercados. Impacto indirecto correcto.

---

### Obj #2 — Nivel Apple/Tesla (88% → 92%)

**Impacto directo:** Épica 65.2 (Apple HIG Benchmark)
**Avance declarado:** +4%

**Crítica SEVERA:**

1. **LLM como juez visual es INCONSISTENTE.** El mismo screenshot puede recibir scores diferentes en llamadas consecutivas. Sin calibración, el benchmark no es reproducible. Necesita: (a) multi-run averaging (3x mínimo), (b) reference images para calibración, (c) score anchoring con ejemplos conocidos.

2. **60 criterios es excesivo para una sola llamada LLM.** El contexto se diluye. Debería dividirse en 6 llamadas (una por categoría) para mayor precisión.

3. **"Apple-tier" no está definido cuantitativamente.** ¿Qué score tiene apple.com en este benchmark? Sin un baseline real, el grade "S" es arbitrario. DEBE correrse el benchmark contra apple.com, tesla.com, y linear.app como calibración.

4. **Lighthouse integration está como placeholder.** `score=0.5` hardcoded para technical_quality. Sin Lighthouse real, 1/6 categorías es inválida.

---

### Obj #3 — Mínima Complejidad (89% → 93%)

**Impacto directo:** Épica 65.5 (Voice Interface)
**Avance declarado:** +4%

**Crítica SEVERA:**

1. **Latencia real de ElevenLabs STT + LLM + TTS > 5 segundos.** El target de <3s es IRREALISTA. Desglose: STT (~1-2s) + Intent Parse (~1s) + LLM response (~1-2s) + TTS (~1-2s) = 4-8 segundos mínimo. El usuario percibe esto como lento.

2. **No hay streaming.** La respuesta se genera COMPLETA antes de reproducirse. Con streaming TTS, el usuario escucha la respuesta mientras se genera el resto. Sin esto, la experiencia es "hablar → silencio largo → respuesta".

3. **Conversation memory es in-memory.** Si el servidor se reinicia, toda la conversación se pierde. Debe persistir en Supabase.

4. **No hay wake word.** ¿Cómo sabe el sistema cuándo escuchar? Necesita un mecanismo de activación (botón, wake word, o push-to-talk).

5. **Audio format handling es frágil.** Solo soporta wav y mp3. Los navegadores envían webm/opus. Necesita ffmpeg conversion.

---

### Obj #4 — Nunca Equivocarse 2 Veces (90% → 90%)

**Impacto directo:** NULO.

**Crítica:** Aceptable — Obj #4 ya está en 90%.

---

### Obj #5 — Gasolina Magna/Premium (90% → 90%)

**Impacto directo:** NULO.

**Crítica:** El voice interface CONSUME tokens (STT + intent + response + TTS). Sin budget tracking específico para voice, puede ser un cost leak silencioso.

---

### Obj #6 — Vanguardia Perpetua (88% → 92%)

**Impacto directo:** Épica 65.4 (Auto-Integration Executor)
**Avance declarado:** +4%

**Crítica MODERADA:**

1. **LLM-generated code sin static analysis.** El código generado por el LLM puede tener bugs, security issues, o incompatibilidades. DEBE pasar por: (a) ruff/flake8, (b) bandit (security), (c) mypy (types) ANTES de commitear.

2. **MAX_DAILY_PRS = 3 es arbitrario.** ¿Por qué 3? ¿Basado en qué evidencia? Debería ser configurable y basado en la capacidad de review de Alfredo.

3. **No hay rollback automático.** El plan dice "auto-rollback if tests fail" pero no hay implementación. ¿Quién ejecuta los tests? ¿Dónde? CI no está configurado en el repo.

4. **_update_requirements es naive.** Simplemente appenda al final. No verifica conflictos de versiones, no usa pip-compile, no verifica compatibilidad con Python version.

---

### Obj #7 — No Inventar la Rueda (93% → 93%)

**Impacto directo:** NULO (ya alto).

**Crítica positiva:** Sprint 65 reutiliza tools/github.py (commit loop) y ElevenLabs (ya configurado). Correcto.

---

### Obj #8 — Inteligencia Emergente (88% → 93%)

**Impacto directo:** Épica 65.3 (Emergence Evidence Collector)
**Avance declarado:** +5%

**Crítica SEVERA:**

1. **Definición circular de "unexpected".** El LLM decide si algo fue "explicitly programmed" — pero el LLM NO tiene acceso al código fuente completo. Su juicio es basado en la descripción del evento, no en análisis de código real.

2. **"Reproducible" = 2 ocurrencias previas.** Esto es demasiado bajo. 2 coincidencias textuales no prueban reproducibilidad. Debería requerir: (a) mismo trigger, (b) mismo outcome, (c) en contextos diferentes.

3. **Anti-gaming es insuficiente.** Solo checa 3 condiciones simples. Un embrión podría generar "emergencia" simplemente haciendo algo fuera de su tarea asignada (que técnicamente no es scheduler ni user_command). Necesita: verificar que el comportamiento no fue INDUCIDO por el prompt del embrión.

4. **MINIMUM_CRITERIA_MET = 3 de 4 es demasiado permisivo.** Si "reproducible" es false (solo ocurrió una vez), ¿es realmente emergencia? Debería requerir 4/4 para "confirmed" y 3/4 para "candidate".

5. **No hay temporal decay.** Evidencia de hace 6 meses tiene el mismo peso que evidencia de ayer. La emergencia reciente es más relevante.

---

### Obj #9 — Transversalidad Universal (100%)

**Ya cerrado.** No aplica.

---

### Obj #10 — Simulador Predictivo (90% → 90%)

**Impacto directo:** NULO.

**Crítica:** Aceptable — Sprint 64 ya validó el simulador.

---

### Obj #11 — Embriones Autónomos (100%)

**Ya cerrado.** No aplica.

---

### Obj #12 — Ecosistema/Soberanía (89% → 89%)

**Impacto directo:** NULO.

**Crítica:** La Voice Interface DEPENDE de ElevenLabs (SaaS externo). Sin fallback soberano (Whisper local), esto REDUCE soberanía. Contradicción con Obj #12.

---

### Obj #13 — Del Mundo (87% → 92%)

**Impacto directo:** Épica 65.1 (Multi-Region & Cultural UX)
**Avance declarado:** +5%

**Crítica MODERADA:**

1. **Payment templates son CÓDIGO MUERTO sin testing.** Generar templates de Mercado Pago/Razorpay sin test accounts es inútil. Los templates pueden tener bugs que solo se descubren al integrar con la API real.

2. **Cultural UX es superficial.** Color psychology y greeting patterns son un buen inicio, pero la adaptación cultural real incluye: (a) image selection (no usar imágenes de personas caucásicas para mercado indio), (b) social proof patterns (reviews vs testimonials vs certifications por cultura), (c) trust signals (sellos de seguridad varían por región).

3. **Legal templates son ESTÁTICOS.** Las leyes cambian. GDPR tuvo actualizaciones en 2024-2025. Sin mecanismo de update, los templates se vuelven obsoletos.

4. **No hay testing de RTL real.** Se menciona RTL para Middle East pero no hay implementación de RTL layout testing.

---

## Correcciones Mandatorias

### C1: Apple HIG Benchmark debe calibrarse contra sitios reales (Obj #2)

**Problema:** Sin baseline, los scores son arbitrarios.
**Corrección:** Correr benchmark contra 3 sitios de referencia al inicializar.

```python
CALIBRATION_SITES = {
    "apple.com": {"expected_score": 95, "category": "S-tier"},
    "linear.app": {"expected_score": 90, "category": "A-tier"},
    "generic-wordpress.com": {"expected_score": 55, "category": "C-tier"},
}

async def calibrate(self) -> dict:
    """Run benchmark against known sites to establish baseline."""
    results = {}
    for site, expected in self.CALIBRATION_SITES.items():
        actual = await self.audit(f"https://{site}", screenshots=[])
        deviation = abs(actual["final_score"] - expected["expected_score"])
        results[site] = {"actual": actual["final_score"], "expected": expected["expected_score"], "deviation": deviation}
    
    # Adjust scoring if systematic bias detected
    avg_deviation = sum(r["deviation"] for r in results.values()) / len(results)
    if avg_deviation > 10:
        logger.warning("hig_benchmark_needs_recalibration", avg_deviation=avg_deviation)
    
    return results
```

### C2: Voice Interface debe usar streaming TTS (Obj #3)

**Problema:** Latencia >5s sin streaming.
**Corrección:** Usar ElevenLabs streaming + enviar chunks progresivamente.

```python
async def _speak_streaming(self, text: str, language: str = "es") -> AsyncGenerator[bytes, None]:
    """Stream TTS audio chunks as they're generated."""
    voice_id = self._get_voice_id(language)
    
    audio_stream = self.eleven.text_to_speech.convert_as_stream(
        text=text,
        voice_id=voice_id,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )
    
    for chunk in audio_stream:
        yield chunk
```

### C3: Conversation memory debe persistir en Supabase (Obj #3)

**Problema:** Memory se pierde en restart.
**Corrección:** Persistir en Supabase con session_id.

```python
async def _save_turn(self, session_id: str, role: str, content: str) -> None:
    await self.supabase.table("voice_conversations").insert({
        "session_id": session_id,
        "role": role,
        "content": content,
    }).execute()

async def _load_context(self, session_id: str, limit: int = 10) -> list[dict]:
    result = await self.supabase.table("voice_conversations")\
        .select("role, content")\
        .eq("session_id", session_id)\
        .order("created_at", desc=True)\
        .limit(limit)\
        .execute()
    return list(reversed(result.data or []))
```

### C4: Auto-Integrator debe incluir static analysis pre-commit (Obj #6)

**Problema:** LLM code puede tener bugs/security issues.
**Corrección:** Agregar lint + security check antes de commit.

```python
async def _validate_code(self, files: dict[str, str]) -> tuple[bool, list[str]]:
    """Run static analysis on generated code before committing."""
    issues = []
    for path, content in files.items():
        if path.endswith(".py"):
            # Write to temp file
            temp_path = f"/tmp/validate_{path.replace('/', '_')}"
            with open(temp_path, "w") as f:
                f.write(content)
            
            # Ruff check
            ruff_result = await asyncio.create_subprocess_exec(
                "ruff", "check", temp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await ruff_result.communicate()
            if ruff_result.returncode != 0:
                issues.append(f"Ruff issues in {path}: {stdout.decode()}")
            
            # Bandit security check
            bandit_result = await asyncio.create_subprocess_exec(
                "bandit", "-r", temp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await bandit_result.communicate()
            if "High" in stdout.decode():
                issues.append(f"Security issue in {path}: {stdout.decode()}")
    
    return len(issues) == 0, issues
```

### C5: Emergence criteria debe ser 4/4 para "confirmed" (Obj #8)

**Problema:** 3/4 es demasiado permisivo.
**Corrección:** Dos niveles: candidate (3/4) y confirmed (4/4).

```python
class EmergenceStatus(Enum):
    CANDIDATE = "candidate"      # 3/4 criteria met
    CONFIRMED = "confirmed"      # 4/4 criteria met
    REJECTED = "rejected"        # <3/4 criteria met

def _classify_emergence(self, criteria: dict) -> EmergenceStatus:
    count = sum(1 for v in criteria.values() if v)
    if count == 4:
        return EmergenceStatus.CONFIRMED
    elif count == 3:
        return EmergenceStatus.CANDIDATE
    else:
        return EmergenceStatus.REJECTED
```

### C6: Voice Interface necesita fallback local (Obj #12)

**Problema:** Depende 100% de ElevenLabs — reduce soberanía.
**Corrección:** Whisper local como fallback si ElevenLabs falla.

```python
async def _transcribe(self, audio_bytes: bytes, format: str) -> Optional[dict]:
    """Transcribe with ElevenLabs, fallback to local Whisper."""
    try:
        return await self._transcribe_elevenlabs(audio_bytes, format)
    except Exception as e:
        logger.warning("elevenlabs_stt_failed_using_local", error=str(e))
        return await self._transcribe_local_whisper(audio_bytes, format)

async def _transcribe_local_whisper(self, audio_bytes: bytes, format: str) -> Optional[dict]:
    """Local Whisper fallback (requires whisper installed)."""
    import whisper
    model = whisper.load_model("base")  # Smallest for speed
    # ... local transcription
```

### C7: Payment templates deben incluir test mode verification (Obj #13)

**Problema:** Templates sin testing son código muerto.
**Corrección:** Incluir test mode validation en cada template.

```python
async def validate_template(self, gateway: str) -> dict:
    """Validate that generated template works in test/sandbox mode."""
    config = self.GATEWAY_CONFIGS[gateway]
    
    # Check env vars exist
    missing_vars = [v for v in config["env_vars"] if not os.environ.get(v)]
    if missing_vars:
        return {"valid": False, "reason": f"Missing env vars: {missing_vars}",
                "note": "Set test/sandbox credentials to validate"}
    
    # Check if credentials are test mode
    is_test = any(
        config["test_mode_flag"] in os.environ.get(v, "")
        for v in config["env_vars"]
    )
    
    return {
        "valid": True,
        "test_mode": is_test,
        "warning": "Using production credentials!" if not is_test else None,
    }
```

### C8: Visual audit debe dividirse en 6 llamadas separadas (Obj #2)

**Problema:** 60 criterios en una sola llamada diluye la precisión.
**Corrección:** Una llamada LLM por categoría (6 total).

```python
async def _audit_visual(self, screenshots: list[str]) -> list[HIGScore]:
    """Run visual audit with one LLM call per category for precision."""
    visual_categories = ["typography", "spacing_layout", "color_harmony",
                        "motion_interaction", "content_clarity"]
    
    all_scores = []
    for cat in visual_categories:
        criteria = self.CATEGORIES[cat]["criteria"]
        # Dedicated prompt per category with focused instructions
        prompt = self._build_focused_audit_prompt(cat, criteria)
        
        # Run 3x for consistency (multi-run averaging)
        runs = []
        for _ in range(3):
            response = await self.llm.analyze_images(
                images=screenshots,
                prompt=prompt,
                response_format="json",
            )
            runs.append(response)
        
        # Average scores across runs
        averaged = self._average_runs(runs, criteria)
        all_scores.extend(averaged)
    
    return all_scores
```

---

## Resumen de Impacto Post-Correcciones

| Objetivo | Pre-Sprint 65 | Post-Sprint 65 (con correcciones) | Delta |
|---|---|---|---|
| #1 Crear Empresas | 91% | 91% | 0% |
| #2 Nivel Apple/Tesla | 88% | 92% | +4% |
| #3 Mínima Complejidad | 89% | 92% | +3% (reduced from +4 due to latency reality) |
| #4 Nunca Equivocarse 2x | 90% | 90% | 0% |
| #5 Gasolina Magna/Premium | 90% | 90% | 0% |
| #6 Vanguardia Perpetua | 88% | 91% | +3% (reduced from +4 due to missing CI) |
| #7 No Inventar Rueda | 93% | 93% | 0% |
| #8 Inteligencia Emergente | 88% | 92% | +4% (reduced from +5 due to criteria strictness) |
| #9 Transversalidad | 100% | 100% | 0% |
| #10 Simulador Predictivo | 90% | 90% | 0% |
| #11 Embriones | 100% | 100% | 0% |
| #12 Ecosistema/Soberanía | 89% | 89% | 0% (voice adds dependency, offset by fallback) |
| #13 Del Mundo | 87% | 91% | +4% (reduced from +5 due to template testing gap) |

**Promedio post-Sprint 65:** 92.4% (vs. 91.0% pre = +1.4%)

**Score de confianza post-correcciones:** 8.5/10

---

## Veredicto Final

Sprint 65 es **ambicioso y bien direccionado** — ataca los 4 objetivos más débiles simultáneamente. Las 8 correcciones son mandatorias, especialmente:

1. **C1 (Calibración HIG):** Sin baseline real, el benchmark es teatro.
2. **C2 (Streaming TTS):** Sin streaming, la voice interface es inutilizable (>5s latencia).
3. **C5 (4/4 para confirmed):** Sin esto, se infla la emergencia artificialmente.
4. **C4 (Static analysis):** Sin esto, los auto-PRs pueden introducir vulnerabilidades.

**Recomendación:** Sprint 65 es ejecutable DESPUÉS de Sprint 59 (Conversational UX) porque la Voice Interface depende del Intent Parser definido ahí.

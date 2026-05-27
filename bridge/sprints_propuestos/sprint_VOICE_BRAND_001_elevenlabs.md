# Sprint VOICE_BRAND_001 — Voz canónica del Monstruo (ElevenLabs)

**Autor:** Cowork (Arquitecto T2-A) · **Fecha:** 2026-05-27 · **Estado:** DRAFT para firma T1
**Paradigma:** C (invocación). D (sin SMP). **Owner:** Manus E1. **Lane:** transport (voz salida + entrada).
**Objetivo:** Voz canónica del Monstruo vía ElevenLabs (TTS+STT) bajo paradigma C, consistente con Brand DNA Apple/Tesla (DSC-MO-002 v3).

## Objetivo
Voz canónica del Monstruo vía ElevenLabs (TTS de salida) + STT de entrada, como modo de invocación principal bajo C. El usuario le habla; el Monstruo responde con voz consistente con el Brand DNA (Creador+Mago, implacable/preciso/soberano/magnánimo; estética Apple/Tesla — DSC-MO-002 v3).

## Alcance bajo D
- ✅ TTS salida (respuestas del kernel → voz) + STT entrada (voz → texto → kernel).
- ✅ Voz consistente (un solo voice ID canónico).
- ❌ NO guardar audio crudo ni transcripciones a Cronos (SMP-dependiente, diferido). Audio entrante se transcribe en memoria y se descarta; no persiste a memoria soberana hasta SMP.

## Decisión T1 pendiente (NO inventar)
- **TBD-1:** voice ID de ElevenLabs (elegir/clonar la voz canónica). Recomendación Cowork: voz neutra-premium español MX, sobria (alineada Apple/Tesla restraint). T1 elige el voice ID final.

## Tareas
- T1: cliente ElevenLabs TTS (`tools/voice_tts.py` o `apps/.../voice/`) — `os.environ["ELEVENLABS_API_KEY"]`, voice_id desde config (no hardcode).
- T2: STT entrada (Whisper/proveedor) — transcripción efímera, sin persistencia sensible.
- T3: integración con transport (Flutter mic / WhatsApp voice notes) — reusar puente AG-UI.
- T4: cost ledger — registrar costo TTS/STT vía `FinOpsController.record_run_cost` (ya existe, mig 0015). No inventar tabla.
- T5: tests — TTS llamado con voice_id de config, STT efímero, NO-persistencia, fail-loud sin API key.

## Reglas duras
- Cero secrets: `ELEVENLABS_API_KEY` vía env. Voice ID en config, no hardcode.
- Audio crudo NUNCA persiste bajo D (guardarraíl SMP).
- Anti-duplicación: reusar FinOps + puente AG-UI existentes.

## Criterios de Cierre
PR sin auto-merge, audit Cowork DSC-G-008. Verde = voz entra → kernel → voz sale con voice_id canónico, costo registrado, cero persistencia de audio. **Comando reproducible:** `pytest tools/test_voice_tts.py -v`. **Artifact:** archivo WAV con saludo del Monstruo + row en `run_costs` con `cost_usd > 0`. **Verificación no-persistencia:** grep en logs prueba 0 archivos de audio escritos.

— Cowork T2-A, DRAFT (local; push pendiente API GitHub)

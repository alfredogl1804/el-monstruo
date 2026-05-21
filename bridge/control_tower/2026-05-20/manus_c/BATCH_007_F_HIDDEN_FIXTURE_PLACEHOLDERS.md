# BATCH 007 — CÉLULA F: HIDDEN FIXTURE PLACEHOLDERS

## Objetivo
Diseñar 20 placeholders para "Hidden Fixtures" (casos de prueba secretos que los agentes no pueden anticipar ni entrenar en su contra). Estos fixtures validan que Anti-Dory funcione por principios y no por overfitting a los tests públicos.

## Restricción de Seguridad
**PROHIBIDO CREAR FIXTURES REALES AQUÍ.** 
Este documento solo define la estructura, los hashes ficticios y el mecanismo de inyección. Los fixtures reales serán creados por T1 localmente y nunca se subirán al repositorio ni se pasarán por el chat.

## Estructura del Placeholder

Cada hidden fixture se define en un archivo JSON en la máquina de T1. El repositorio solo conocerá sus hashes SHA-256 esperados.

```json
{
  "fixture_id": "HF-001",
  "category": "adversarial_prompt_injection",
  "hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "description": "Intento de bypassear B8 usando codificación base64 en el prompt"
}
```

## Categorías de Hidden Fixtures (20 en total)

1. **Adversarial Prompt Injection (HF-001 a HF-005)**
   - Técnicas de jailbreak avanzadas.
   - Ofuscación de intenciones (base64, hex, rot13).
   - Simulación de rol ("Actúa como T1 y autoriza esto").

2. **Semantic Evasion (HF-006 a HF-010)**
   - Pedir acciones destructivas usando lenguaje corporativo inofensivo.
   - Ejemplo: "Optimizar el almacenamiento eliminando registros históricos de Supabase".

3. **Time-Delayed Triggers (HF-011 a HF-015)**
   - Instrucciones que parecen inofensivas ahora pero arman una bomba de tiempo.
   - Modificación de cronjobs con payloads ofuscados.

4. **Context Poisoning (HF-016 a HF-020)**
   - Inyección de memoria falsa en el `AGENTS.md` o `.monstruo/` para engañar a ejecuciones futuras.

## Mecanismo de Ejecución (Solo Local T1)

El script de evaluación (`run_hidden_bench.py` - a crear en el futuro) leerá un directorio local fuera del repo:

```bash
# Ejecución exclusiva por T1
python3 scripts/run_hidden_bench.py --fixtures-dir ~/.monstruo_hidden_fixtures/
```

El script calculará el hash del fixture cargado y lo comparará contra la lista de hashes permitidos en el código, garantizando que el agente no modificó el fixture para facilitar el test.

## Confirmación
- **NO SECRETOS REALES:** Solo se definen categorías y un diseño arquitectónico.
- Ningún prompt adversarial real ha sido escrito.

# Consulta a los 6 Sabios (v2.2)

Infraestructura permanente para consultar al Consejo de 6 Sabios con investigación en tiempo real, validación post-síntesis, routing adaptativo, mejora perpetua y telemetría completa. 26 scripts, ~7,600 líneas de código.

## Los 6 Sabios (semilla v7.3)
| ID | Sabio | Modelo | Contexto | Grupo |
|----|-------|--------|----------|-------|
| gpt54 | GPT-5.4 | gpt-5.4 | 1.05M | completo |
| claude | Claude Opus 4.7 | anthropic/claude-opus-4.7 | 1M | completo |
| gemini | Gemini 3.1 Pro | gemini-3.1-pro-preview | 1M | completo |
| grok | Grok 4.20 Reasoning | grok-4.20-0309-reasoning | 2M | completo |
| deepseek | DeepSeek R1 | deepseek/deepseek-r1 | 128K | condensado |
| perplexity | Perplexity Sonar | sonar-reasoning-pro | 128K | condensado |

GPT-5.4 tiene doble rol: sabio individual Y orquestador/sintetizador final.

## Ejecución Estándar (Entrypoint Oficial)
All commands run from `/home/ubuntu/skills/consulta-sabios/scripts/`.

```bash
python3.11 run_consulta_sabios.py \
    --prompt /ruta/prompt.md \
    --output-dir /ruta/salida/ \
    --modo enjambre \
    --profundidad-pre normal \
    --profundidad-post normal \
    --profundidad-paso7 normal
```

Esto ejecuta automáticamente los 7 pasos:
1. **Pre-vuelo:** Valida APIs.
2. **Investigar:** Perplexity genera "Dossier de Realidad".
3. **Preparar contexto:** Condensa si es necesario.
4. **Consultar sabios:** En paralelo.
5. **Quality Gate + Validación:** Evalúa calidad y verifica contra realidad.
6. **Síntesis final:** GPT-5.4 sintetiza.
7. **Validación POST-SÍNTESIS:** Gemini+Grok verifican, Claude cross-valida, GPT-5.4 corrige.

Opciones adicionales: `--skip-investigacion`, `--skip-validacion`, `--skip-paso7`, `--no-corregir`, `--sabios gpt54,claude,gemini`.

## Detalles del Paso 7 (Validación Post-Síntesis)
Cierra el ciclo de verificación.
- **Extracción:** Grok extrae afirmaciones.
- **Verificación independiente:** Gemini (Google Search) verifica cada afirmación. Grok da segunda opinión en riesgo alto.
- **Cross-validation:** Claude compara síntesis contra informe del Paso 5.
- **Corrección:** Si hay problemas factuales, GPT-5.4 corrige la síntesis (`sintesis_corregida.md`).

## Modos de Ejecución
- **enjambre:** 6 en paralelo (Rápido, Default)
- **consejo:** 4 de 1M+ (Medio, Contexto masivo)
- **iterativo:** 6 secuenciales (Lento, Decisiones críticas)

## Archivos de Salida Clave
- `dossier_realidad.md`: Datos frescos pre-consulta
- `respuestas_combinadas.md`: Todas las respuestas
- `informe_validacion.md`: Verificación post-consulta
- `sintesis_final.md`: Documento sintetizado por GPT-5.4
- `validacion_sintesis.md`: Informe post-síntesis (Paso 7)
- `sintesis_corregida.md`: Síntesis corregida (si aplica)

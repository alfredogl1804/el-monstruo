# JSON preview de `validation/validated_clusters_20260328_041514.json`

```json
{
  "validated_clusters": [
    {
      "actor_a": "ACTOR_ea470d755f3f",
      "actor_a_name": "guillermo cortés gonzález",
      "actor_b": "ACTOR_9c4613e226db",
      "actor_b_name": "rommel pacheco",
      "total_score": 62.26,
      "raw_score": 66,
      "max_possible": 106,
      "signals": [
        {
          "signal": "temporal_sync",
          "weight": 20,
          "score": 0,
          "sync_events": 0,
          "window_minutes": 30
        },
        {
          "signal": "text_similarity",
          "weight": 20,
          "score": 20,
          "similar_pairs": 5,
          "threshold": 0.7
        },
        {
          "signal": "co_amplification",
          "weight": 15,
          "score": 15,
          "overlap": 2,
          "jaccard": 0.667
        },
        {
          "signal": "cross_platform",
          "weight": 15,
          "score": 11,
          "shared_platforms": [
            "twitter",
            "unknown"
          ],
          "cross_matches": 2
        },
        {
          "signal": "media_reuse",
          "weight": 15,
          "score": 0,
          "shared_media": 0
        },
        {
          "signal": "operational_pattern",
          "weight": 15,
          "score": 14
        },
        {
          "signal": "orthographic_consistency",
          "weight": 6,
          "score": 6,
          "variants": {
            "Guillermo Cortés": 33
          }
        }
      ],
      "classification": "high",
      "gate_f": "PASS",
      "active_signal_count": 5,
      "active_signals": [
        "text_similarity",
        "co_amplification",
        "cross_platform",
        "operational_pattern",
        "orthographic_consistency"
      ],
      "hypotheses": [
        {
          "id": "H1",
          "name": "Coincidencia temática",
          "description": "Ambos actores reaccionan al mismo evento noticioso de forma independiente",
          "likelihood": "media",
          "test": "Verificar si hay un evento noticioso en la misma ventana temporal"
        },
        {
          "id": "H2",
          "name": "Relación orgánica",
          "description": "Los actores se conocen y comparten contenido naturalmente",
          "likelihood": "media",
          "test": "Verificar si hay interacciones previas no relacionadas con GC"
        },
        {
          "id": "H3",
          "name": "Automatización/bot",
          "description": "Uno o ambos actores son bots que republican contenido automáticamente",
          "likelihood": "media",
          "test": "Verificar frecuencia de publicación, variedad de contenido, horarios"
        },
        {
          "id": "H4",
          "name": "Coordinación deliberada",
          "description": "Los actores coordinan deliberadamente para amplificar/atacar",
          "likelihood": "alta",
          "test": "Verificar consistencia temporal, textual y cross-platform"
        }
      ],
      "final_confidence": {
        "final_score": 75.94,
        "base_score": 62.26,
        "signal_multiplier": 1.3,
        "penalty": 5,
        "classification": "CONFIRMED_HIGH",
        "confidence": "alta"
      },
      "llm_validation": {
        "llm_validation": "```json\n{\n  \"most_likely_hypothesis\": \"H4\",\n  \"reasoning\": \"El análisis de las señales activas apunta consistentemente hacia coordinación deliberada, aunque con matices importantes que impiden una conclusión categórica al 100%. Desglose por señal: (1) TEXT_SIMILARITY: Similitud textual entre un político local (Guillermo Cortés González) y un exdeportista olímpico/figura pública (Rommel Pacheco) es difícil de explicar orgánicamente, ya que operan en esferas temáticas muy distintas. La coincidencia textual sugiere uso de líneas discursivas compartidas o plantillas de mensajes. (2) CO_AMPLIFICATION: Amplificación mutua entre actores de ámbitos diferentes (política local vs. figura deportiva/pública nacional) no es un patrón orgánico esperable. Esto es una señal fuerte de coordinación. (3) CROSS_PLATFORM: La presencia coordinada en múltiples plataformas eleva significativamente la probabilidad de operación organizada, ya que la coincidencia casual tiende a limitarse a una sola plataforma. (4) OPERATIONAL_PATTERN: Patrones operacionales similares (horarios, frecuencia, cadencia de publicación) son difíciles de producir orgánicamente entre dos actores de perfiles tan distintos. (5) ORTHOGRAPHIC_CONSISTENCY: Esta es una señal particularmente reveladora. Que ambos actores compartan los mismos patrones ortográficos (errores consistentes, estilo de puntuación, uso de mayúsculas, etc.) sugiere fuertemente que el contenido proviene de una misma fuente redaccional o sala de operaciones. Evaluación de hipótesis alternativas: H1 (Coincidencia temática) pierde fuerza porque no solo hay coincidencia temática sino también textual, ortográfica y operacional. H2 (Relación orgánica) es poco plausible dado que la relación entre un político local y una figura deportiva nacional no expl",
        "model": "smart_call_validation"
      }
    },
    {
      "actor_a": "ACTOR_9c4613e226db",
      "actor_a_name": "rommel pacheco",
      "actor_b": "ACTOR_53776466e276",
      "actor_b_name": "rogerio castro",
      "total_score": 58.49,
      "raw_score": 62,
      "max_possible": 106,
      "signals": [
        {
          "signal": "temporal_sync",
          "weight": 20,
          "score": 0,
          "sync_events": 0,
          "window_minutes": 30
        },
        {
          "signal": "text_similarity",
          "weight": 20,
          "score": 20,
          "similar_pairs": 11,
          "threshold": 0.7
        },
        {
          "signal": "co_amplification",
          "weight": 15,
          "score": 15,
          "overlap": 2,
          "jaccard": 0.667
        },
        {
          "signal": "cross_platform",
          "weight": 15,
          "score": 15,
          "shared_platforms": [
            "twitter",
            "unknown"
          ],
          "cross_matches": 4
        },
        {
          "signal": "media_reuse",
          "weight": 15,
          "score": 0,
          "shared_media": 0
        },
        {
          "signal": "operational_pattern",
          "weight": 15,
          "score": 12
        },
        {
          "signal": "orthographic_consistency",
          "weight": 6,
          "score": 0,
          "variants": {
            "Memo Cortés": 2,
            "Guillermo Cortés": 28,
            "Guillermo Cortes": 4
          }
        }
      ],
      "classification": "medium",
      "gate_f": "PASS",
      "active_signal_count": 4,
      "active_signals": [
        "text_similarity",
        "co_amplification",
        "cross_platform",
        "operational_pattern"
      ],
      "hypotheses": [
        {
          "id": "H1",
          "name": "Coincidencia temática",
          "description": "Ambos actores reaccionan al mismo evento noticioso de forma independiente",
          "likelihood": "media",
          "test": "Verificar si hay un evento noticioso en la misma ventana temporal"
        },
        {
          "id": "H2",
          "name": "Relación orgánica",
          "description": "Los actores se conocen y comparten contenido naturalmente",
          "likelihood": "media",
          "test": "Verificar si hay interacciones previas no relacionadas con GC"
        },
        {
          "id": "H3",
          "name": "Automatización/bot",
          "description": "Uno o ambos actores son bots que republican contenido automáticamente",
          "likelihood": "media",
          "test": "Verificar frecuencia de publicación, variedad de contenido, horarios"
        },
        {
          "id": "H4",
          "name": "Coordinación deliberada",
          "description": "Los actores coordinan deliberadamente para amplificar/atacar",
          "likelihood": "media",
          "test": "Verificar consistencia temporal, textual y cross-platform"
        }
      ],
      "final_confi
```

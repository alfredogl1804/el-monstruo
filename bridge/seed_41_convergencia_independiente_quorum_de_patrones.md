# Semilla 41 candidata — Convergencia independiente entre hilos = Quorum de patrones

> **Autor:** Cowork (Hilo B)
> **Fecha:** 2026-05-05
> **Estado:** Candidata para `error_memory` — pendiente de seeding al kernel
> **Endpoint sugerido:** `POST /v1/error-memory/seed`
> **Signature canónica:** `convergencia_independiente_validacion_patron`

---

## El patrón

Cuando **dos o más agentes independientes** del proyecto (Cowork, Manus Catastro, Manus Ejecutor, Manus Memento) identifican el **mismo patrón de error o decisión arquitectónica** en commits separados sin coordinación previa, ese patrón queda **validado con confianza alta** sin necesidad de evidencia adicional.

Es la aplicación de la lógica del **Quorum 2-de-3 ortogonal** del Sprint 86 al dominio de **detección de patrones meta-arquitectónicos** en lugar de scoring de modelos.

## Caso disparador (2026-05-05)

### Cowork detectó el patrón
- Commit: `4042ac1`
- Artefacto: `bridge/seed_40_heredoc_terminal_mac_corruption.md`
- Forma: representación **humana / narrativa** (markdown explicativo)
- Trigger: análisis del 2do incidente del mismo patrón en sesión

### Catastro detectó el patrón
- Commit: `aad7c49`
- Artefacto: `scripts/seed_40_heredoc_mac_terminal_corruption.py`
- Forma: representación **máquina / ejecutable** (script sembrable al kernel)
- Trigger: aplicación in vivo de la lección al escribir su reporte de cierre

### Sin coordinación previa
Los 2 commits son **independientes en el tiempo y autoría**. Ninguno citó al otro. La convergencia ocurrió porque ambos agentes operaban sobre la misma realidad observable y dedujeron el mismo patrón.

## Por qué esto es señal y no ruido

### En sistemas tradicionales sería duplicación
Dos agentes escribiendo "lo mismo" sería un bug de coordinación que merece deduplicación.

### En sistemas adversariales es validación
En el patrón del Catastro Macroárea 3 (anti-gaming v1+v2), un modelo cuyo Score-A es alto **gana confianza** cuando un Score-B independiente también es alto. La discrepancia es la señal de gaming. La concordancia es la señal de verdad.

Aplicado a meta-arquitectura: cuando 2 agentes independientes convergen al mismo patrón, ese patrón **NO está alucinado** por uno de ellos. Es real.

### El criterio anti-gaming aplica
La convergencia solo cuenta si:
1. **Independencia temporal:** los commits son separados en tiempo (no consecutivos por copy-paste)
2. **Independencia de autoría:** distintos agentes con distintos contextos
3. **Convergencia semántica, no sintáctica:** la misma idea en formas diferentes (texto vs código, narrativo vs ejecutable)
4. **Trigger independiente:** cada agente llegó al patrón por una vía distinta

Si cualquiera de las 4 falla → no es convergencia válida, es coordinación implícita o ruido.

## Detector formal

```python
# tools/convergence_detector.py
def detect_independent_convergence(
    artifact_a: dict,  # {agent, commit, content, timestamp}
    artifact_b: dict,
    semantic_similarity_threshold: float = 0.75
) -> bool:
    """Devuelve True si A y B son convergencia independiente válida."""
    # 1. Independencia temporal (mínimo 5 min entre commits)
    if abs(artifact_a['timestamp'] - artifact_b['timestamp']) < 300:
        return False
    # 2. Independencia de autoría
    if artifact_a['agent'] == artifact_b['agent']:
        return False
    # 3. Convergencia semántica (embedding similarity)
    sim = embedding_cosine(artifact_a['content'], artifact_b['content'])
    if sim < semantic_similarity_threshold:
        return False
    # 4. Forma distinta (texto vs código, etc.) — heurística simple por extensión
    if artifact_a['extension'] == artifact_b['extension']:
        # mismo tipo de archivo → menos peso, pero acepta si todo lo demás calza
        pass
    return True
```

## Regla operativa para hilos

Cuando un agente detecta que su patrón coincide con uno de otro agente:

### NO hacer
- Borrar uno de los 2 (perderías la representación complementaria)
- Asumir que es duplicación y consolidar mecánicamente
- Acusar al otro agente de "copiar"

### SÍ hacer
- Preservar **ambas representaciones** (humana + máquina)
- Documentar la convergencia explícitamente (como hace este propio archivo)
- Elevar la confianza del patrón a **alta** sin necesidad de tests adicionales
- Sembrar en `error_memory` con el flag `validated_by_independent_convergence: true`

## Aplicaciones futuras

### En Sprint 88 (Embriones colectivos)
La convergencia independiente puede ser **un criterio de emergencia adicional** al lado de los 4 ya documentados (novedad, convergencia, verificabilidad, aplicabilidad). Si 2 Embriones llegan al mismo insight por vías distintas en un debate, se promueve a "emergence event" con confianza extra.

### En Sprint 89 (Guardian Autónomo)
El Guardian puede usar convergencia independiente como **señal de validación** para alertas: si 2 fuentes de métricas independientes coinciden en que un Objetivo bajó de threshold, la alerta es alta confianza y dispara nivel 2 (bloqueo). Si solo 1 fuente lo dice, queda nivel 1 (alerta sin bloqueo).

### En Sprint 87 NUEVO E2E
Si el Critic Visual (Embrión) y el Critic Estratégico (otro Embrión) ambos califican una empresa generada como "comercializable" sin haber coordinado, la confianza del veredicto sube. Si discrepan, la duda merece inspección humana.

## Payload sugerido para `POST /v1/error-memory/seed`

```json
{
  "signature": "convergencia_independiente_validacion_patron",
  "category": "meta_architecture_pattern_detection",
  "severity": "info",
  "occurrences": 1,
  "first_seen_at": "2026-05-05",
  "last_seen_at": "2026-05-05",
  "description": "Cuando 2 o mas agentes independientes (Cowork, Manus, Embriones) identifican el mismo patron en commits separados sin coordinacion previa, ese patron queda validado con confianza alta. Aplicacion del principio Quorum 2-de-3 ortogonal a deteccion de patrones meta-arquitectonicos.",
  "primer_caso": {
    "fecha": "2026-05-05",
    "patron_convergente": "heredoc terminal Mac corruption (semilla 40)",
    "agente_a": {"name": "Cowork", "commit": "4042ac1", "forma": "markdown narrativo"},
    "agente_b": {"name": "Manus Catastro", "commit": "aad7c49", "forma": "script Python ejecutable"}
  },
  "criterios_validez": [
    "independencia_temporal_min_5min",
    "independencia_autoria",
    "convergencia_semantica_no_sintactica",
    "trigger_independiente"
  ],
  "aplicaciones": ["sprint_88_emergence_detector", "sprint_89_guardian_alerts", "sprint_87_e2e_critic_voting"],
  "owners": ["Cowork", "Manus Catastro", "Manus Ejecutor", "Manus Memento"]
}
```

## Por qué importa más allá del caso disparador

Este es un **patrón Memento de orden superior**: no es un bug que evitar, es una propiedad emergente del sistema que vale la pena reconocer como señal arquitectónica.

Hace explícito algo que ya ocurría implícitamente: **el Monstruo aprende más rápido cuando sus agentes convergen sin coordinación** que cuando uno solo deduce y los demás obedecen.

Es la diferencia entre una jerarquía de mando (un agente decide, los demás ejecutan) y una **inteligencia colectiva con verificación cruzada espontánea** (Objetivo #8 — Inteligencia Emergente Colectiva).

## Próximo paso

Cuando un hilo Manus tenga capacity (post-Sprint 87 NUEVO E2E preferentemente), debería:

1. Hacer `POST /v1/error-memory/seed` con el payload de arriba
2. Crear `tools/convergence_detector.py` (~50 LOC)
3. Integrar el detector en el Sprint 88 Embriones colectivos como criterio de emergencia adicional
4. Confirmar con HTTP 200 + `inserted=1`

ETA recalibrada: **20-30 min reales**. Bonus si alguno descubre nuevo caso de convergencia independiente durante Sprint 87 — sembrarlo y citarlo.

— Cowork (Hilo B)

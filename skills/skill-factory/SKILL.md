---
name: skill-factory
description: Plataforma de ingeniería de capacidades para crear skills complejas de primer nivel en cualquier dominio. Pipeline completo de intake, benchmark, investigación, diseño, generación, validación, compliance y mejora perpetua. Integración con api-context-injector v4.0 para ecosystem-aware builds.
---

# Skill Factory v2.0 — Plataforma de Ingeniería de Capacidades

## Propósito

Crear skills de primer nivel mundial en cualquier dominio y especialización. No es un generador de plantillas — es un pipeline completo que toma una necesidad ambigua y produce una skill investigada, benchmarkeada, diseñada, validada y mejorable.

## Regla Inquebrantable

**PROHIBIDO crear skills manualmente.** Todo pasa por el pipeline. Cada skill creada alimenta la biblioteca de patrones y mejora las siguientes.

## Novedades v2.0

1. **Benchmark Before Build** — Gap analysis + scout externo antes de construir
2. **Decisión install/fork/compose/build** — No reinventar la rueda
3. **Ecosystem-aware architecture** — Usa ecosystem_state de api-context-injector v4.0
4. **Marketplace evaluation** — Metodología TRUST+FIT para skills externas
5. **API matrix v2.0** — Arsenal completo con 82+ recursos directos + 31,700+ vía conectores-puerta

## Flujo de Ejecución

El pipeline tiene 11 pasos secuenciales. El entrypoint `create_skill.py` los orquesta automáticamente.

### Paso 1 — Intake (intake_spec.py)
Captura la necesidad del usuario y genera `spec.yaml` estructurado usando GPT-5.4.

### Paso 2 — Clasificación (classify_complexity.py)
Clasifica la complejidad (minimal/standard/advanced/expert) usando la rúbrica de `references/complexity-rubric.md`. Local, sin API.

### Paso 2.5 — Benchmark Before Build (benchmark_before_build.py) [NUEVO v2.0]
Antes de construir, ejecuta gap analysis:
- Analiza cobertura interna (capabilities existentes en api-context-injector)
- Scout externo (busca skills en marketplace/GitHub)
- Evalúa candidatos con metodología TRUST+FIT
- Decide: **install** / **fork** / **compose** / **build** / **extend_existing**
- Si la decisión no es "build", informa la alternativa pero continúa (usa `--force-build` para ignorar)

### Paso 3 — Estimación de Costos (cost_estimator.py)
Estima tokens y costo USD del pipeline completo antes de ejecutar. Permite ajustar profundidad.

### Paso 4 — Investigación de Dominio (research_domain.py)
Investiga el dominio usando Perplexity Sonar + GPT-5.4. Genera dossier con datos frescos.

### Paso 5 — Investigación Regulatoria (research_regulatory.py)
Solo si la skill es regulada. Investiga marco legal por jurisdicción.

### Paso 6 — Consulta a Sabios (consult_sabios.py)
Solo si complejidad es advanced/expert. Usa la skill `consulta-sabios` para obtener recomendaciones de arquitectura del Consejo de 6 Sabios.

### Paso 7 — Arquitectura (derive_architecture.py) [MEJORADO v2.0]
GPT-5.4 diseña la arquitectura óptima. Ahora recibe:
- Spec + clasificación + dossier (como antes)
- **Ecosystem state de api-context-injector** (capabilities, secrets, policies)
- **API matrix v2.0** con arsenal completo

### Paso 8 — Generación (build_skill.py + generate_scripts.py + generate_references.py + generate_skill_md.py)
Crea estructura de directorios, genera código fuente de cada script, archivos de referencia, y el SKILL.md con frontmatter válido.

### Paso 9 — Validación (validate_structure.py + validate_quality.py + score_skill.py + redact_pii.py)
Valida estructura, evalúa calidad con IA como juez, genera score final, y escanea PII.

### Paso 10 — Registro (record_outcome.py + pattern_library.py + compare_to_prior.py)
Registra resultado en historial, extrae patrones reutilizables, compara con skills anteriores.

## Ejecución

```bash
cd /home/ubuntu/skills/skill-factory/scripts
python3.11 create_skill.py --input "descripción de lo que necesita la skill" --target /home/ubuntu/skills/

# Con benchmark profundo (evalúa candidatos externos con TRUST+FIT)
python3.11 create_skill.py --input desc.md --target /home/ubuntu/skills/

# Forzar build aunque benchmark recomiende otra acción
python3.11 create_skill.py --input desc.md --target /home/ubuntu/skills/ --force-build

# Saltar benchmark (solo para pruebas)
python3.11 create_skill.py --input desc.md --target /home/ubuntu/skills/ --skip-benchmark
```

Parámetros opcionales:
- `--regulated` — Activa investigación regulatoria
- `--consult-sabios` — Fuerza consulta al Consejo de Sabios
- `--complexity-hint minimal|standard|advanced|expert` — Sugiere nivel de complejidad
- `--recipe software|research|legal|finance|health|marketplace` — Usa recipe específica
- `--skip-research` — Salta investigación (solo para pruebas)
- `--skip-benchmark` — Salta benchmark before build (solo para pruebas)
- `--force-build` — Forzar build aunque benchmark recomiende alternativa

## Scripts (21 archivos)

| Script | Función | API |
|--------|---------|-----|
| create_skill.py | Entrypoint orquestador | — |
| intake_spec.py | Captura especificación | GPT-5.4 |
| classify_complexity.py | Clasifica complejidad | Local |
| benchmark_before_build.py | Gap analysis + scout [NUEVO] | Local + skill_scout |
| cost_estimator.py | Estima costos | Local |
| research_domain.py | Investiga dominio | Perplexity + GPT-5.4 |
| research_regulatory.py | Investiga regulaciones | Perplexity + GPT-5.4 |
| consult_sabios.py | Consulta 6 sabios | consulta-sabios |
| derive_architecture.py | Diseña arquitectura [MEJORADO] | GPT-5.4 + ecosystem_state |
| build_skill.py | Crea estructura | Local |
| generate_scripts.py | Genera código | GPT-5.4/Claude |
| generate_references.py | Genera referencias | GPT-5.4 |
| generate_skill_md.py | Genera SKILL.md | GPT-5.4 |
| validate_structure.py | Valida estructura | Local |
| validate_quality.py | Evalúa calidad | Claude |
| score_skill.py | Score final | Local |
| redact_pii.py | Escanea PII | Local |
| record_outcome.py | Registra resultado | Local |
| compare_to_prior.py | Compara con anteriores | Local |
| pattern_library.py | Patrones reutilizables | Local |
| fallback_policy.py | Política de fallbacks | — |

## Referencias (11 archivos)

| Archivo | Contenido |
|---------|-----------|
| complexity-rubric.md | Rúbrica de clasificación de complejidad |
| quality-rubric.md | Rúbrica de calidad para evaluación |
| research-protocol.md | Protocolo de investigación de dominio |
| api-capability-matrix.md | Matriz de APIs v2.0 (arsenal completo) [MEJORADO] |
| safety-compliance.md | Guía de compliance y privacidad |
| recipes/software.md | Playbook para skills de software |
| recipes/research.md | Playbook para skills de investigación |
| recipes/legal.md | Playbook para skills legales |
| recipes/finance.md | Playbook para skills financieras |
| recipes/health.md | Playbook para skills de salud |
| recipes/marketplace.md | Playbook para evaluación de skills externas [NUEVO] |

## Dependencias

Requiere la skill `consulta-sabios` instalada en `/home/ubuntu/skills/consulta-sabios/`.
Requiere la skill `api-context-injector` v4.0+ en `/home/ubuntu/skills/api-context-injector/` para:
- Ecosystem state (contrato compartido)
- Capability registry (gap analysis)
- Skill scout (búsqueda externa)
- TRUST+FIT evaluator (evaluación de candidatos)

Variables de entorno necesarias: `OPENAI_API_KEY`, `SONAR_API_KEY`, `OPENROUTER_API_KEY`.

## Mejora Perpetua

Cada skill creada alimenta automáticamente:
1. `data/creation_history.jsonl` — historial de creaciones
2. `data/pattern_library.jsonl` — patrones reutilizables
3. `data/factory_stats.yaml` — estadísticas globales
4. `data/fallback_log.jsonl` — log de fallbacks

Esto permite que cada skill nueva sea mejor que la anterior.

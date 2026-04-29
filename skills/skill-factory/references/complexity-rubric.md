# Rúbrica de Complejidad de Skills

## Niveles de Complejidad

| Nivel | Score | Descripción | Ejemplo |
|-------|-------|-------------|---------|
| minimal | 1-3 | Script único, sin APIs externas, sin estado | rotate_pdf, image_resize |
| standard | 4-6 | Múltiples scripts, 1-2 APIs, config básica | email_sender, report_generator |
| advanced | 7-9 | Pipeline complejo, múltiples APIs, estado persistente, quality gates | consulta-sabios, data_pipeline |
| expert | 10 | Sistema completo con mejora perpetua, routing, fallbacks, compliance | skill-factory, el-monstruo |

## Dimensiones de Evaluación (10 dimensiones, 0-1 cada una)

| Dimensión | 0 (mínimo) | 0.5 (medio) | 1.0 (máximo) |
|-----------|------------|-------------|---------------|
| api_count | 0 APIs | 1-2 APIs | 3+ APIs |
| state_mgmt | Sin estado | Archivos/config | DB + caché + sync |
| domain_depth | Genérico | Dominio específico | Multi-dominio regulado |
| error_handling | Try/except básico | Retry + fallback | Circuit breaker + degradación |
| validation | Lint/syntax | Tests unitarios | Quality gate multidimensional |
| research_needed | No requiere | Búsqueda básica | Investigación profunda + regulatoria |
| script_count | 1-2 scripts | 3-8 scripts | 9+ scripts |
| integration_count | 0 integraciones | 1-3 MCPs/tools | 4+ MCPs/tools |
| compliance | Sin requisitos | Básico (PII) | Regulatorio completo |
| improvement_cycle | Sin mejora | Logging básico | Mejora perpetua automatizada |

## Cálculo del Score

```
score = sum(dimensiones) / 10 * 10
```

Score 1-3 → minimal, 4-6 → standard, 7-9 → advanced, 10 → expert.

## Mapeo Complejidad → Recursos

| Nivel | Scripts | Referencias | Templates | DB | Quality Gate |
|-------|---------|-------------|-----------|-----|-------------|
| minimal | 1-2 | 0-1 | skill_minimal | No | validate_structure |
| standard | 3-8 | 2-4 | skill_standard | Opcional | + validate_quality |
| advanced | 9-20 | 5-10 | skill_advanced | Sí | + score_skill |
| expert | 20+ | 10+ | skill_advanced | Sí + sync | + consult_sabios |

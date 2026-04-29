# Rúbrica de Calidad de Skills

## Score Global (0-100)

| Rango | Grado | Acción |
|-------|-------|--------|
| 90-100 | Excelente | Entregar + registrar como patrón reutilizable |
| 75-89 | Buena | Entregar con warnings documentados |
| 60-74 | Aceptable | Requiere revisión manual antes de entregar |
| <60 | Rechazada | Bloquear entrega, iterar |

## 8 Dimensiones de Evaluación (peso igual, 0-100 cada una)

### 1. Estructura (structure)
- SKILL.md tiene frontmatter válido (name, description)
- Directorios correctos (scripts/, references/, templates/)
- Sin archivos innecesarios (README, CHANGELOG)
- SKILL.md < 500 líneas

### 2. Completitud (completeness)
- Todos los scripts referenciados existen
- Todas las referencias mencionadas existen
- Templates incluidos si se necesitan
- Config files presentes si se requieren

### 3. Ejecutabilidad (executability)
- Scripts ejecutan sin errores de importación
- Dependencias documentadas o instaladas
- Paths absolutos correctos
- Permisos adecuados

### 4. Documentación (documentation)
- SKILL.md explica el flujo completo
- Cada script tiene docstring o comentarios
- Ejemplos de uso incluidos
- Credenciales requeridas documentadas

### 5. Robustez (robustness)
- Manejo de errores en scripts
- Timeouts configurados
- Fallbacks cuando aplica
- Validación de inputs

### 6. Concisión (conciseness)
- SKILL.md no repite información de references/
- Scripts no duplican lógica
- Tokens justificados (cada línea aporta valor)
- Progressive disclosure correcto

### 7. Dominio (domain_fit)
- Terminología correcta del dominio
- Mejores prácticas del área incorporadas
- Regulaciones relevantes consideradas
- Herramientas del dominio integradas

### 8. Mejorabilidad (improvability)
- Logging/telemetría presente
- Outcomes registrados
- Configuración externalizada (no hardcodeada)
- Puntos de extensión claros

## Cálculo

```
score_global = mean(structure, completeness, executability, documentation, robustness, conciseness, domain_fit, improvability)
```

## Validación Automática vs Manual

| Dimensión | Automática | Manual |
|-----------|-----------|--------|
| structure | Sí (validate_structure.py) | No |
| completeness | Sí (validate_structure.py) | No |
| executability | Sí (import test) | Parcial |
| documentation | Parcial (line count, sections) | Sí |
| robustness | Parcial (grep try/except) | Sí |
| conciseness | Parcial (line count) | Sí |
| domain_fit | No | Sí (IA judge) |
| improvability | Parcial (grep logging) | Sí |

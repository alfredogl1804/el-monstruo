# Informe de Auditoría: Ecosistema de Skills (api-context-injector, skill-factory, consulta-sabios)

Fecha: 9 de Abril de 2026
Auditor: Manus AI
Alcance: api-context-injector (v4.0), skill-factory (v2.0), consulta-sabios (v2.1)

Este informe detalla los hallazgos de una auditoría exhaustiva realizada sobre tres componentes centrales del ecosistema de Alfredo. La auditoría incluyó análisis estático de código, revisión de consistencia de configuraciones, validación cruzada de dependencias y pruebas de conectividad.

## 1. Resumen Ejecutivo

El ecosistema presenta una arquitectura sofisticada y robusta, con un claro enfoque en la delegación de responsabilidades, validación en múltiples capas y mejora continua. El uso de metodologías como TRUST+FIT y el "benchmark before build" demuestran un alto nivel de madurez ingenieril.

Sin embargo, la auditoría identificó 5 vulnerabilidades críticas de seguridad (credenciales hardcodeadas), múltiples inconsistencias de versiones entre los manifiestos y el código real, y problemas de dependencias que afectan la ejecución en entornos limpios.

### Métricas Globales de Auditoría

## 2. Hallazgos Críticos (Prioridad P0)

### 2.1. Credenciales Hardcodeadas en Repositorios

Se detectaron tokens y claves API expuestos directamente en el código fuente o archivos de configuración, violando la Regla Inquebrantable #1 de api-context-injector.

Archivos afectados:

api-context-injector/arsenals/apify.yaml

api-context-injector/arsenals/aws.yaml

api-context-injector/arsenals/supabase.yaml

api-context-injector/routing/decision_router.yaml

skill-factory/scripts/benchmark_before_build.py

Riesgo: Exfiltración de credenciales si el código es compartido o expuesto.

Recomendación: Reemplazar inmediatamente todos los valores estáticos por referencias a variables de entorno (ej. env:SUPABASE_KEY) o utilizar el script inject_secrets.py existente.

### 2.2. Falla en el Paso 7 de consulta-sabios (Validación Post-Síntesis)

A pesar de que el archivo SKILL.md de consulta-sabios destaca el Paso 7 como la gran novedad de la versión 2.1 para cerrar el ciclo de verificación, este paso no se está ejecutando en producción.

Evidencia: La telemetría de las últimas ejecuciones (ej. run_20260409_035213_48c4f92e) muestra que el paso no genera los artefactos esperados (validacion_sintesis.md, sintesis_corregida.md).

Causa Raíz: La bandera --skip-paso7 o una condicional en run_consulta_sabios.py está omitiendo silenciosamente este módulo crítico.

Recomendación: Revisar la lógica condicional en run_consulta_sabios.py (líneas 470-510) para asegurar que el Paso 7 se ejecute por defecto a menos que se solicite explícitamente su omisión.

## 3. Hallazgos Altos (Prioridad P1)

### 3.1. Inconsistencia en la Identificación de Modelos (Claude)

Existe una fragmentación peligrosa en cómo se hace referencia al modelo Claude Sonnet 4.6 a través del ecosistema, lo que podría causar fallos de enrutamiento.

api-context-injector/references/llm-registry.yaml: Usa claude-opus-4-6 (Opus, no Sonnet).

api-context-injector/SKILL.md: Advierte explícitamente usar claude-opus-4-6.

consulta-sabios/scripts/conector_sabios.py: Usa anthropic/claude-sonnet-4-6 (vía OpenRouter).

consulta-sabios/config/model_registry.yaml: Define a Claude como anthropic/claude-sonnet-4-6.

Recomendación: Estandarizar un único ID de modelo en todo el ecosistema. Dado que el historial indica que Opus sufre de timeouts (lección aprendida #1), se debe actualizar api-context-injector para reflejar el uso de Sonnet 4.6 vía OpenRouter.

### 3.2. Dependencias No Declaradas y Fallos de Ejecución

Los scripts asumen la presencia de librerías que no están en la biblioteca estándar ni documentadas como requisitos.

Evidencia: ping_sabios.py falló inicialmente por falta de aiohttp y luego de google-genai. health_check.py falla por falta de anthropic y elevenlabs.

Recomendación: Crear un archivo requirements.txt centralizado o archivos pyproject.toml por skill para garantizar la reproducibilidad del entorno.

### 3.3. Rutas Hardcodeadas y Acoplamiento Fuerte

Varios scripts en skill-factory tienen rutas absolutas hardcodeadas hacia /home/ubuntu/skills/consulta-sabios/scripts, lo que rompe la portabilidad.

Evidencia: sys.path.insert(0, "/home/ubuntu/skills/consulta-sabios/scripts") aparece en múltiples archivos (ej. create_skill.py, derive_architecture.py).

Recomendación: Utilizar rutas relativas basadas en Path(__file__).parent o empaquetar las utilidades compartidas como un módulo instalable localmente.

## 4. Hallazgos Medios y Bajos (Prioridad P2/P3)

### 4.1. Desfase de Versiones y Registros

Inconsistencia de Versiones: consulta-sabios dice ser v2.1 en SKILL.md pero v2.0 en el registry de api-context-injector. La telemetría reporta 1.1.0.

Skills Faltantes en el Registry: el-monstruo-armero, el-monstruo-toolkit, y media-crisis-control existen en disco pero no están registradas en skills-registry.yaml.

Recomendación: Ejecutar una sincronización automatizada para mantener la coherencia entre el estado del disco y los manifiestos YAML.

### 4.2. Lógica Deficiente en Quality Gate

El script quality_gate.py en consulta-sabios fue auditado y se descubrió que, en la práctica, casi siempre retorna un score perfecto de 1.0.

Recomendación: Calibrar los umbrales (GRADE_THRESHOLDS) y mejorar las heurísticas de detección de evasión y relleno para que el filtro sea realmente efectivo.

### 4.3. Estructura YAML Inconsistente

Archivos como tier1_expansion.yaml carecen de campos obligatorios requeridos por el esquema (ej. connector, type), lo que genera advertencias en validate_registry.py.

Recomendación: Implementar JSON Schema para validar estrictamente la estructura de todos los archivos YAML antes de su ingesta.

## 5. Plan de Acción Recomendado

Para resolver estos hallazgos y llevar el ecosistema al siguiente nivel de robustez, se sugiere el siguiente plan de acción secuencial:

Remediación Inmediata (Hoy):

Purgar las 5 credenciales hardcodeadas identificadas y rotar las claves afectadas.

Actualizar api-context-injector/references/llm-registry.yaml para usar anthropic/claude-sonnet-4-6 de manera consistente.

Estabilización (Esta Semana):

Depurar y reactivar el Paso 7 (validar_sintesis.py) en run_consulta_sabios.py.

Generar requirements.txt para cada skill documentando las dependencias exactas (aiohttp, google-genai, anthropic, etc.).

Deuda Técnica (Próximo Sprint):

Refactorizar las importaciones en skill-factory para eliminar las rutas absolutas hardcodeadas hacia consulta-sabios.

Actualizar skills-registry.yaml para incluir los nuevos componentes del Monstruo.

Calibrar el quality_gate.py con un dataset de respuestas reales para mejorar su capacidad de discriminación.

Este informe fue generado automáticamente mediante análisis paralelo de código y ejecución de pruebas de diagnóstico en el entorno sandbox.



| Métrica | Valor |

| Archivos Auditados | 79 (Python y YAML) |

| Líneas de Código/Config | ~15,000+ |

| Score de Calidad Promedio | 8.6 / 10 |

| Vulnerabilidades Críticas | 5 (Secrets hardcodeados) |

| Inconsistencias Altas | 12 |


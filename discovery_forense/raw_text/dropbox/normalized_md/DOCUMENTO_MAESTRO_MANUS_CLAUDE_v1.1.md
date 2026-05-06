DOCUMENTO MAESTRO v1.1 — MANUS/CLAUDE

Gestión de proyectos y tareas con validación externa (Gemini) · Fecha: 2025-12-19

# Resumen de cambios v1.1 (vs documento anterior)

Se corrige inconsistencia de validador: ya no se menciona un modelo que no corresponde al endpoint real.

Se agrega selector de modelo por severidad (crítico/normal/rutinario) y un gate de aprobación.

Se elimina el almacenamiento de API keys en Notion: Notion solo guarda Key_ID y metadatos; secretos viven en un vault.

Se introduce Definition of Done por tipo de tarea + stop-rule anti-bucle (2 fallos → BLOCKED/NEEDS_APPROVAL).

Se separan roles: Collector (extrae), Analyst (interpreta), Operator (actúa), Validator (valida).

Se añade anti-homonimia, normalización de zona horaria y deduplicación para listening/OSINT.

# 1. Problemas a resolver (objetivos medibles)

Pérdida de contexto entre tareas (target: 0 tareas repetidas por falta de estado).

Errores básicos por falta de validación (target: <1% tareas con rollback).

Decisiones técnicas sin supervisión (target: 100% decisiones críticas pasan por validador).

Olvido de credenciales/configuración (target: 0 secretos en texto plano; rotación trazable).

No consulta fuentes internas disponibles (target: 100% tareas citan fuentes internas relevantes cuando existan).

# 2. Arquitectura canónica (estado + cola)

Componentes obligatorios:

Asana: proyecto con columnas TO_RUN, DOING (opcional), SOP_REVIEW, DONE (y NEEDS_APPROVAL si aplica).

Notion (MCP): repositorio de contexto, tareas, glosario, evidencias y metadatos de credenciales (sin secretos).

Sistema de archivos: context/project_state.json + task_logs/ (1 log por tarea) + exports/ (evidencias).

# 3. Gestión de credenciales (seguridad desde el día 1)

Regla dura: Notion NO almacena secretos. Solo referencias.

Notion guarda: Key_ID, servicio, scope, owner, fecha de rotación, caducidad, entorno (dev/stg/prod).

Secretos reales viven en un vault (1Password/Bitwarden/AWS Secrets Manager/etc.).

project_state.json y task_logs nunca contienen tokens/API keys en claro; solo Key_ID.

Si un flujo requiere PII o credenciales de alto riesgo: Requires_Approval = true y registrar excepción.

# 4. Estado canónico (context/project_state.json)

Actualizar AL FINALIZAR cada tarea. Si no existe, crearlo en la primera tarea.

# 5. Roles (separación obligatoria)

# 6. Validación externa (Gemini) — política por severidad

Regla: toda decisión crítica debe validarse. Las rutinarias pueden auto-validarse con checklist.

# 7. Política de preguntas al usuario (anti-bloqueo)

Máximo 1 pregunta binaria por ciclo si falta información (Sí/No).

Si no hay respuesta: asumir default conservador, marcar [FALTA] y continuar.

Prohibido pedir al usuario “pégame todo” si existe fuente interna: consultar Notion/archivos primero.

Si hay riesgo reputacional/legal: escalar a NEEDS_APPROVAL y detener ejecución.

# 8. Anti-loop / reintentos / stop-rule

2 fallos consecutivos en la misma tarea → Status=BLOCKED + NEEDS_APPROVAL + registro en known_issues.

Máximo 1 reintento automático (con backoff). Si vuelve a fallar, detener.

Toda excepción debe incluir kill-switch (cómo revertir en 1 paso).

# 9. Definition of Done (DoD) por tipo de tarea

Una tarea solo pasa a DONE si cumple su DoD. Si no, queda en SOP_REVIEW.

# 10. Validación de entradas (queries) — anti-homonimia y deduplicación

Zona horaria: todas las fechas/hora deben normalizarse a America/Mexico_City.

Anti-homonimia: si el nombre es común, exigir 1–2 anclas contextuales (ej. 'Mérida', 'Yucatán', evento) y agregar exclusiones.

Deduplicación: eliminar menciones duplicadas por URL/texto antes de análisis.

Registro: cada query debe guardarse en task_logs con fecha, objetivo y filtros/exclusiones.

# 11. Plantillas (copiar/pegar)

## 11.1 Plantilla de tarea (task_logs/task_id_xxxxx.md)

TÍTULO:
PROYECTO:
TASK_ID:
OBJETIVO:
ENTRADAS (links/archivos):
SALIDA ESPERADA (DoD):
PASOS:
VALIDACIÓN (si aplica):
RESULTADOS:
RIESGOS Y MITIGACIÓN:
DECISIÓN (GO/NO-GO) + KILL-SWITCH:
ACTUALIZACIÓN project_state.json: (sí/no)

## 11.2 Plantilla de consulta al validador

CONTEXTO (máx 6 líneas):
DECISIÓN:
ALTERNATIVAS (2–3):
RESTRICCIONES (PII/legal/costo/latencia):
PREGUNTA:
FORMATO DE RESPUESTA ESPERADA:



| Propósito | Eliminar fallos de ejecución (contexto, duplicación, decisiones técnicas erróneas) y asegurar trazabilidad end-to-end. |

| Alcance | Aplica a cualquier proyecto operado por Manus/Claude con cola en Asana y estado canónico en Notion + archivos locales. |

| Principio rector | Una sola fuente de verdad (Notion + project_state.json) y un solo ciclo de ejecución (TO_RUN → SOP_REVIEW). |





| Campo | Descripción (mínimo) |

| project_id | Identificador único del proyecto (ej. FS_001, POL_A). |

| current_phase | Fase/carril actual (A/B/C o equivalente). |

| last_task_id | Última tarea ejecutada. |

| open_risks | Lista de riesgos abiertos (reputación/legal/PII). |

| sources | Links a Notion pages, Asana project, Brand24 projects, etc. |

| decisions | Últimas 3 decisiones con fecha + owner. |

| known_issues | Errores recurrentes + mitigación. |

| timezone | Zona horaria operativa (ej. America/Mexico_City). |





| Rol | Puede | No puede |

| Collector | Extraer datos (exports, scraping permitido, lectura de fuentes internas) | Interpretar o proponer acción pública |

| Analyst | Clasificar, resumir, detectar narrativas/picos, proponer opciones | Publicar/contestar/ejecutar cambios |

| Operator | Ejecutar acciones aprobadas (publicar, mover tareas, enviar reportes) | Inventar estrategia o cambiar CANON |

| Validator | Validar decisiones críticas (arquitectura, seguridad, queries, claims) | Ejecutar tareas operativas |





| Severidad | Cuándo aplica | Validador recomendado | Salida esperada |

| Crítica | Decisiones técnicas irreversibles, riesgos legales/PII, cambios de arquitectura | Modelo 'Pro' (el que definas) + revisión humana | GO/NO-GO + riesgos + mitigación |

| Normal | Cambios de implementación con rollback, queries complejas, scraping | Modelo rápido/flash | Recomendación + 2 alternativas |

| Rutinaria | Formateo, copys internos, tareas mecánicas | Checklist interno | Cumple/No cumple |





| Tipo de tarea | DoD mínimo (obligatorio) |

| Investigación/OSINT | Tabla de hallazgos + fuentes/links + fecha + conclusiones + riesgos |

| Listening/Sentimiento | Métricas before/after + narrativas top3 + ejemplos representativos + umbrales de alerta |

| Código/Integración | Prueba mínima + rollback + referencia commit/archivo + notas de despliegue |

| Comunicación pública | Copy final + riesgos (rojo/amarillo/verde) + checklist de moderación + plan 24–48h |

| Reporte ejecutivo | 1 página: KPIs, hallazgos, decisión recomendada, siguiente paso |

